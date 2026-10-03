"""Independent R12 raw-label/model/calibration audit.

No candidate fitting, summarization, or native implementation is imported.
Weighted standardized ridge is solved in raw coordinates with exact Fractions:
 (Xc' W Xc + lambda diag(training variance)) beta = Xc' W yc.
Constant or masked coordinates use scale=1. This avoids sharing the candidate's
floating-point standardization/linear-algebra implementation.
"""
from fractions import Fraction as F
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import math

HERE = Path(__file__).resolve().parent
OPTIONS = ('C', 'W', 'E', 'L', 'ED', 'LD')
MASKS = {'full': (), 'nohistory': tuple(range(10, 18)), 'nobudget': (20, 22, 23)}
MARGINS = (F(0), F(1, 10000), F(1, 1000), F(1, 100), F(1, 10), None)
DENOMINATOR = 16385


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def bounds(value):
    if isinstance(value, dict):
        return F(value['lower'], value['denominator']), F(value['upper'], value['denominator'])
    value = F(value)
    return value, value


def gauss_solve(matrix, rhs):
    """Exact elimination, including several RHS columns in one solve."""
    size = len(matrix)
    width = len(rhs[0])
    rows = [list(matrix[i]) + list(rhs[i]) for i in range(size)]
    for j in range(size):
        pivot = next((i for i in range(j, size) if rows[i][j]), None)
        assert pivot is not None, ('singular exact ridge system', j)
        rows[j], rows[pivot] = rows[pivot], rows[j]
        p = rows[j][j]
        rows[j] = [x / p for x in rows[j]]
        for i in range(j + 1, size):
            factor = rows[i][j]
            if factor:
                rows[i] = [a - factor * b for a, b in zip(rows[i], rows[j])]
    output = [[F(0) for _ in range(width)] for _ in range(size)]
    for i in range(size - 1, -1, -1):
        for k in range(width):
            output[i][k] = rows[i][size + k] - sum(rows[i][j] * output[j][k] for j in range(i + 1, size))
    return output


def quantize9(value):
    """Exact round-to-nearest/ties-even; output the deployed rational."""
    return F(round(value * 10**9), 10**9)


def ridge_heads(features, labels, masked=()):
    assert features and len(features) == len(labels)
    assert all(len(x) == 25 for x in features)
    x = [[F(0) if j in masked else F(value) for j, value in enumerate(row)] for row in features]
    y = [[F(value) for value in row] for row in labels]
    width = len(y[0])
    weights = [F(1, 2)] * len(x)
    mass = sum(weights)
    means = [sum(w * row[j] for w, row in zip(weights, x)) / mass for j in range(25)]
    variances = [sum(w * (row[j] - means[j])**2 for w, row in zip(weights, x)) / mass for j in range(25)]
    # The pre-frozen candidate uses scale=1 for std<1e-12.
    scale_squared = [v if v >= F(1, 10**24) else F(1) for v in variances]
    target_means = [sum(w * row[k] for w, row in zip(weights, y)) / mass for k in range(width)]
    centered = [[row[j] - means[j] for j in range(25)] for row in x]
    matrix = [[sum(w * row[i] * row[j] for w, row in zip(weights, centered)) +
               (scale_squared[i] if i == j else 0) for j in range(25)] for i in range(25)]
    rhs = [[sum(w * row[j] * (target[k] - target_means[k])
                for w, row, target in zip(weights, centered, y)) for k in range(width)] for j in range(25)]
    beta = gauss_solve(matrix, rhs)
    raw = [[target_means[k] - sum(means[j] * beta[j][k] for j in range(25))] +
           [beta[j][k] for j in range(25)] for k in range(width)]
    return {'means': means, 'variances': variances, 'scale_squared': scale_squared,
            'unquantized': raw, 'coefficients': [[quantize9(v) for v in row] for row in raw],
            'row_weights': weights, 'lambda': F(1)}


def read_episode(receipt_path):
    receipt_path = Path(receipt_path)
    receipt = json.loads(receipt_path.read_text())
    assert receipt['error'] is None, (receipt_path, receipt['error'])
    for name in ('raw', 'input', 'planner'):
        assert sha(receipt[name]) == receipt[name + '_sha256'], (receipt_path, name)
    fifo = {}
    input_parameters = {}
    for line in Path(receipt['input']).read_text().splitlines():
        fields = line.split()
        if fields[0] == 'D':
            horizon = F(fields[3])
        elif fields[0] in ('R', 'F'):
            fifo.setdefault(int(fields[1]), []).append(int(fields[2]))
        elif fields[0] == 'M':
            input_parameters.setdefault(fields[1], []).append(F(int(fields[2]), int(fields[3])))
    assert len(fifo) == 16 and horizon == 128
    wanted = {(a, task) for a, tasks in fifo.items() for task in tasks[:4]}
    assert len(wanted) == 64
    services = {}
    choice = None
    first_actor = None
    queries = 0
    summary = None
    choices = 0
    with Path(receipt['raw']).open() as stream:
        for line in stream:
            event = json.loads(line)
            if event['event'] == 'task_service':
                key = event['agent'], event['task']
                assert key not in services, ('duplicate service', key)
                lo, hi = bounds(event['at'])
                assert 0 <= lo <= hi <= horizon
                services[key] = lo, hi
            elif event['event'] == 'certified_POSITION_committed':
                queries += 1
            elif event['event'] == 'macro_choice':
                choice = event
                choices += 1
            elif event['event'] == 'actor_decision' and first_actor is None:
                first_actor = event
            elif event['event'] == 'joint_summary':
                summary = event
    assert summary and summary['served'] == len(services) and summary['queries'] == queries
    assert 0 <= queries <= receipt['capacity']
    if choice is not None:
        assert choices == 1 and first_actor is not None
        assert choice['at'] == first_actor['at'] and choice['opportunity'] == first_actor['opportunity']
        candidates = first_actor['candidates']
        assert candidates and all(len(c['features']) == 24 for c in candidates)
        features = [sum(F(c['features'][j]) for c in candidates) / len(candidates) for j in range(24)]
        features.append(F(len(candidates), 16))
        assert features == list(map(F, choice['features'])), 'gate is not the exact candidate mean'
        assert choice['initial_capacity'] == receipt['capacity']
        assert first_actor['remaining_capacity'] == receipt['capacity'], 'not a no-query prefix'
    else:
        assert first_actor is None and choices == 0
        features = None
    time_lo = sum(services.get(key, (horizon, horizon))[0] for key in wanted)
    time_hi = sum(services.get(key, (horizon, horizon))[1] for key in wanted)
    return {'world': receipt['world'], 'policy': receipt['policy'], 'budget': receipt['capacity'],
            'tasks': len(services), 'time_lower': time_lo, 'time_upper': time_hi,
            'queries': queries, 'features': features, 'choice': choice,
            'input_parameters': input_parameters, 'receipt': receipt,
            'receipt_path': str(receipt_path), 'receipt_sha256': sha(receipt_path)}


def scores(coefficients, features, variant):
    if features is None:
        return {k: (F(0), F(0), F(0)) for k in OPTIONS}
    fit_variant = 'full' if variant == 'tasks_only' else variant
    masked = MASKS[fit_variant]
    result = {'C': (F(0), F(0), F(0))}
    for option in OPTIONS[1:]:
        heads = []
        for head in ('tasks', 'time'):
            if variant == 'tasks_only' and head == 'time':
                heads.append(F(0))
                continue
            c = coefficients[fit_variant + '_' + option + '_' + head]
            heads.append(c[0] + sum(c[j + 1] * features[j] for j in range(25) if j not in masked))
        result[option] = heads[0], heads[1], sum(heads)
    return result


def choose(predictions, margin):
    selected = 'C'
    if margin is not None:
        for option in OPTIONS[1:]:
            if predictions[option][2] > margin and (selected == 'C' or predictions[option][2] > predictions[selected][2]):
                selected = option
    return selected


def rank_complete(candidates, final_order):
    """Max tasks; interval-undominated time set; queries; registered tie order."""
    top = max(row['tasks'] for row in candidates)
    same_tasks = [row for row in candidates if row['tasks'] == top]
    undominated = [a for a in same_tasks if not any(a['time_lower'] > b['time_upper'] for b in same_tasks)]
    fewest = min(row['queries'] for row in undominated)
    tied = [row for row in undominated if row['queries'] == fewest]
    winner = min(tied, key=lambda row: final_order(row['key']))
    return winner, {'max_tasks': top, 'task_ties': [r['key'] for r in same_tasks],
                    'time_undominated': [r['key'] for r in undominated],
                    'fewest_queries': fewest, 'query_ties': [r['key'] for r in tied]}


def mechanics():
    xs = [[F(-1)] + [F(0)] * 24, [F(1)] + [F(0)] * 24]
    fitted = ridge_heads(xs, [[F(-1)], [F(1)]])
    assert fitted['coefficients'][0][:2] == [0, F(1, 2)]
    assert ridge_heads(xs, [[F(-1)], [F(1)]], (0,))['coefficients'][0] == [F(0)] * 26
    assert quantize9(F(1, 2 * 10**9)) == 0
    assert quantize9(F(3, 2 * 10**9)) == F(2, 10**9)
    overlap = [{'key': 'a', 'tasks': 2, 'time_lower': F(1), 'time_upper': F(3), 'queries': 2},
               {'key': 'b', 'tasks': 2, 'time_lower': F(2), 'time_upper': F(4), 'queries': 1},
               {'key': 'c', 'tasks': 2, 'time_lower': F(5), 'time_upper': F(6), 'queries': 0}]
    winner, detail = rank_complete(overlap, lambda k: k)
    assert winner['key'] == 'b' and detail['time_undominated'] == ['a', 'b']
    coefficients = {v + '_' + k + '_' + h: [F(0)] * 26
                    for v in MASKS for k in OPTIONS[1:] for h in ('tasks', 'time')}
    coefficients['full_W_tasks'][0] = F(1)
    coefficients['full_E_tasks'][0] = F(1)
    coefficients['full_E_time'][0] = F(1, 2)
    zero = [F(0)] * 25
    assert choose(scores(coefficients, zero, 'full'), F(0)) == 'E'
    assert choose(scores(coefficients, zero, 'tasks_only'), F(0)) == 'W'
    assert choose(scores(coefficients, zero, 'tasks_only'), F(1)) == 'C'
    coefficients['nobudget_W_tasks'][21] = F(9)
    a, b = zero.copy(), zero.copy()
    a[20], b[20] = F(1, 2), F(1)
    assert scores(coefficients, a, 'nobudget') == scores(coefficients, b, 'nobudget')
    return {'passed': True, 'checks': ['weighted_exact_ridge', 'masked_intercept', 'half_even_9_decimals',
            'interval_undominated_then_queries', 'task_only_shared_head', 'strict_margin_and_fixed_tie', 'budget_input_mask']}


def load(name):
    return json.loads((HERE / name).read_text())


def aggregate(episodes, key):
    return {'key': key, 'tasks': sum(e['tasks'] for e in episodes),
            'time_lower': sum(e['time_lower'] for e in episodes),
            'time_upper': sum(e['time_upper'] for e in episodes),
            'queries': sum(e['queries'] for e in episodes)}


def compare_total(reference, actual):
    assert reference['tasks'] == actual['tasks'] and reference['queries'] == actual['queries']
    assert F(reference['T_lower']) == actual['time_lower'] and F(reference['T_upper']) == actual['time_upper']


def chronology(registration, episodes, test_episodes=None):
    reg_hash = sha(HERE / 'REGISTRATION.json')
    for name, digest in registration['frozen'].items():
        assert sha(HERE / name) == digest, ('source changed', name)
    assert sha(HERE / 'build/joint_history_native') == registration['binary_sha256']
    tc_start = load('TC_START.json')
    tc_done = load('TC_RECEIPT.json')
    fit_start = load('FIT_START.json')
    freeze = load('MODEL_FREEZE_RECEIPT.json')
    assert registration['frozen_unix_ns'] <= tc_start['unix_time_ns']
    assert tc_start['registration_sha256'] == reg_hash
    assert fit_start['registration_sha256'] == reg_hash
    assert fit_start['TC_receipt_sha256'] == sha(HERE / 'TC_RECEIPT.json')
    assert freeze['fit_start_sha256'] == sha(HERE / 'FIT_START.json')
    assert freeze['model_sha256'] == sha(HERE / 'MODELS_FROZEN_BEFORE_TEST.json')
    assert freeze['labels_sha256'] == sha(HERE / 'TRAIN_CAL_LABELS.json')
    assert tc_done['native_episodes'] == 96 and tc_done['failed'] == 0
    starts, finishes = [], []
    for e in episodes:
        receipt = e['receipt']
        assert receipt['registration_sha256'] == reg_hash
        assert receipt['source_frozen_unix_ns'] == registration['frozen_unix_ns']
        assert receipt['stage_start_receipt_sha256'] == sha(HERE / 'TC_START.json')
        assert receipt['model_artifact_sha256'] is None and receipt['model_freeze_receipt_sha256'] is None
        assert tc_start['unix_time_ns'] <= receipt['started_unix_ns'] <= receipt['finished_unix_ns'] <= fit_start['unix_time_ns']
        assert receipt['binary_sha256'] == registration['binary_sha256']
        assert receipt['native_source_sha256'] == registration['frozen']['joint_history_native.cpp']
        assert receipt['bridge_sha256'] == registration['bridge_sha256'] and receipt['config_sha256'] == registration['config_sha256']
        starts.append(receipt['started_unix_ns'])
        finishes.append(receipt['finished_unix_ns'])
    assert max(finishes) <= tc_done['finished_unix_ns'] <= fit_start['unix_time_ns'] < freeze['unix_time_ns']
    assert fit_start['TC_latest_finish_ns'] == max(finishes)
    result = {'passed': True, 'source_freeze_ns': registration['frozen_unix_ns'],
              'TC_first_start_ns': min(starts), 'TC_last_finish_ns': max(finishes),
              'fit_start_ns': fit_start['unix_time_ns'], 'model_freeze_ns': freeze['unix_time_ns'],
              'scope': 'Hash-linked local recorded chronology, not an external trusted timestamp.'}
    if test_episodes is not None:
        test_start = load('TEST_START.json')
        assert freeze['unix_time_ns'] < test_start['unix_time_ns']
        assert test_start['registration_sha256'] == reg_hash
        assert test_start['model_sha256'] == freeze['model_sha256']
        assert test_start['model_freeze_sha256'] == sha(HERE / 'MODEL_FREEZE_RECEIPT.json')
        for e in test_episodes:
            receipt = e['receipt']
            assert receipt['registration_sha256'] == reg_hash
            assert receipt['source_frozen_unix_ns'] == registration['frozen_unix_ns']
            assert receipt['stage_start_receipt_sha256'] == sha(HERE / 'TEST_START.json')
            assert receipt['model_artifact_sha256'] == freeze['model_sha256']
            assert receipt['model_freeze_receipt_sha256'] == sha(HERE / 'MODEL_FREEZE_RECEIPT.json')
            assert test_start['unix_time_ns'] <= receipt['started_unix_ns'] <= receipt['finished_unix_ns']
            assert receipt['binary_sha256'] == registration['binary_sha256']
            assert receipt['native_source_sha256'] == registration['frozen']['joint_history_native.cpp']
            assert receipt['bridge_sha256'] == registration['bridge_sha256'] and receipt['config_sha256'] == registration['config_sha256']
        result['TEST_first_start_ns'] = min(e['receipt']['started_unix_ns'] for e in test_episodes)
        result['TEST_last_finish_ns'] = max(e['receipt']['finished_unix_ns'] for e in test_episodes)
    return result


def scientific_audit():
    required = ['REGISTRATION.json', 'TRAIN_CAL_LABELS.json', 'MODELS_FROZEN_BEFORE_TEST.json',
                'MODEL_FREEZE_RECEIPT.json', 'FIT_START.json', 'TC_START.json', 'TC_RECEIPT.json']
    missing = [name for name in required if not (HERE / name).exists()]
    if missing:
        return {'passed': False, 'status': 'awaiting_raw_data_and_frozen_model', 'missing': missing}
    registration = load('REGISTRATION.json')
    world_list = registration['worlds']
    worlds = {w['name']: w for w in world_list}
    family_splits = {}
    for w in world_list:
        family_splits.setdefault(w['family_key'], set()).add(w['split'])
    assert len(world_list) == 24 and len(family_splits) == 12 and all(len(s) == 1 for s in family_splits.values())
    for split, count in [('train', 6), ('calibration', 2), ('test', 4)]:
        assert sum(s == {split} for s in family_splits.values()) == count
    for family in family_splits:
        pair = [w for w in world_list if w['family_key'] == family]
        assert {w['budget'] for w in pair} == {8, 16}
        assert pair[0]['robots'] == pair[1]['robots'] and pair[0]['seed'] == pair[1]['seed']
    episodes = {}
    for w in world_list:
        if w['split'] == 'test':
            continue
        for option in OPTIONS:
            receipt_path = HERE / 'runs' / (w['name'] + '__macro_' + option + '.receipt.json')
            if not receipt_path.exists():
                return {'passed': False, 'status': 'awaiting_all_96_TC_receipts', 'missing': str(receipt_path)}
            e = read_episode(receipt_path)
            assert e['world'] == w['name'] and e['budget'] == w['budget'] and e['policy'] == 'macro_' + option
            if e['choice'] is not None:
                assert e['choice']['selected_option'] == option and not e['choice']['learned']
            expected_fifo = {int(r['agent']): [int(t['task']) for t in r['tasks']] for r in w['robots']}
            actual_fifo = {}
            for line in Path(e['receipt']['input']).read_text().splitlines():
                fields = line.split()
                if fields[0] in ('R', 'F'):
                    actual_fifo.setdefault(int(fields[1]), []).append(int(fields[2]))
            assert actual_fifo == expected_fifo
            episodes[w['name'], option] = e
    assert len(episodes) == 96
    reconstructed = []
    for w in world_list:
        if w['split'] == 'test':
            continue
        base = episodes[w['name'], 'C']
        for option in OPTIONS:
            e = episodes[w['name'], option]
            assert e['features'] == base['features'], ('common gate mismatch', w['name'], option)
            reconstructed.append({'world': w['name'], 'family_key': w['family_key'], 'split': w['split'],
                'budget': w['budget'], 'option': option, 'features': e['features'], 'weight': F(1, 2),
                'task_target': F(e['tasks'] - base['tasks']),
                'time_target': (base['time_lower'] + base['time_upper'] - e['time_lower'] - e['time_upper']) / (2 * DENOMINATOR),
                'tasks': e['tasks'], 'T_lower': e['time_lower'], 'T_upper': e['time_upper'], 'queries': e['queries'],
                'T_gain_lower': base['time_lower'] - e['time_upper'], 'T_gain_upper': base['time_upper'] - e['time_lower'],
                'raw_sha256': e['receipt']['raw_sha256']})
    supplied_labels = load('TRAIN_CAL_LABELS.json')
    assert len(supplied_labels) == 96
    for expected, supplied in zip(reconstructed, supplied_labels):
        for key, value in expected.items():
            observed = supplied[key]
            if isinstance(value, F):
                assert F(observed) == value, ('label mismatch', expected['world'], expected['option'], key)
            elif key == 'features' and value is not None:
                assert list(map(F, observed)) == value
            else:
                assert observed == value, ('label binding mismatch', key)
    model = load('MODELS_FROZEN_BEFORE_TEST.json')
    assert model['labels_sha256'] == sha(HERE / 'TRAIN_CAL_LABELS.json')
    assert model['registration_sha256'] == sha(HERE / 'REGISTRATION.json')
    assert model['prefix_audit_sha256'] == sha(HERE / 'PREFIX_BEFORE_FIT.json')
    coefficients = {}
    refits = []
    exact_quantization_differences = []
    for variant, masked in MASKS.items():
        rs = [r for r in reconstructed if r['split'] == 'train' and r['option'] == 'W' and r['features'] is not None]
        if not rs:
            for option in OPTIONS[1:]:
                for head in ('tasks', 'time'):
                    name = variant + '_' + option + '_' + head
                    published = model['models'][name]
                    assert published['train_rows'] == 0 and published['bindings'] == [] and 'fallback' in published
                    assert published['masked_slots'] == list(masked) and published['lambda_value'] == 1
                    assert list(map(F, published['coefficients'])) == [F(0)] * 26
                    assert published['unrounded_raw'] == published['standardized_coefficients'] == [0.] * 26
                    assert published['train_mean'] == [0.] * 25 and published['train_scale'] == [1.] * 25
                    coefficients[name] = [F(0)] * 26
                    refits.append({'head': name, 'TRAIN_context_rows': 0, 'preregistered_zero_fallback': True})
            continue
        by_label = {(r['world'], r['option']): r for r in reconstructed}
        targets = [[by_label[r['world'], option][head] for option in OPTIONS[1:] for head in ('task_target', 'time_target')] for r in rs]
        exact = ridge_heads([r['features'] for r in rs], targets, masked)
        for k, option in enumerate(OPTIONS[1:]):
            for h, head in enumerate(('tasks', 'time')):
                name = variant + '_' + option + '_' + head
                published = model['models'][name]
                assert published['lambda_value'] == 1 and published['unpenalized_intercept'] is True
                assert published['masked_slots'] == list(masked) and published['train_rows'] == len(rs)
                expected_bindings = [{'world': r['world'], 'family_key': r['family_key'], 'budget': r['budget'], 'option': option, 'weight': '1/2'} for r in rs]
                assert published['bindings'] == expected_bindings
                for j in range(25):
                    assert abs(F(str(published['train_mean'][j])) - exact['means'][j]) < F(1, 10**11)
                    assert abs(float(published['train_scale'][j]) - math.sqrt(float(exact['scale_squared'][j]))) < 1e-11
                column = 2 * k + h
                raw = list(map(lambda v: F(str(v)), published['unrounded_raw']))
                deployed = list(map(F, published['coefficients']))
                assert len(raw) == 26 and len(deployed) == 26
                errors = [abs(a - b) for a, b in zip(raw, exact['unquantized'][column])]
                assert max(errors) < F(1, 10**10), ('unrounded fit mismatch', name, float(max(errors)))
                assert deployed == [F(str(round(float(v), 9))) for v in published['unrounded_raw']], ('candidate quantization mismatch', name)
                for j, (actual, expected) in enumerate(zip(deployed, exact['coefficients'][column])):
                    if actual != expected:
                        record = {'head': name, 'coordinate': j, 'deployed': actual, 'exact_quantized': expected,
                                  'unrounded_absolute_error': errors[j], 'exact_solution_float': float(exact['unquantized'][column][j])}
                        exact_quantization_differences.append(record)
                        assert abs(actual - expected) <= F(1, 10**9), ('more than one quantization unit mismatch', record)
                coefficients[name] = deployed
                residuals = []
                for i, row in enumerate(rs):
                    values = [F(0) if j in masked else v for j, v in enumerate(row['features'])]
                    residuals.append(targets[i][column] - raw[0] - sum(raw[j + 1] * values[j] for j in range(25)))
                normal_residual = [sum(residuals) / 2]
                for j in range(25):
                    moment = sum((F(0) if j in masked else r['features'][j]) * e / 2 for r, e in zip(rs, residuals))
                    normal_residual.append(moment - exact['scale_squared'][j] * raw[j + 1])
                assert max(map(abs, normal_residual)) < F(1, 10**9), ('ridge normal-equation residual', name)
                standardized = list(map(float, published['standardized_coefficients']))
                target_mean = sum(targets[i][column] for i in range(len(rs))) / len(rs)
                assert abs(standardized[0] - float(target_mean)) < 1e-10
                for j in range(25):
                    assert abs(standardized[j + 1] - float(raw[j + 1]) * published['train_scale'][j]) < 1e-10
                assert all(deployed[j + 1] == 0 for j in masked)
                refits.append({'head': name, 'TRAIN_context_rows': len(rs),
                    'max_unrounded_error': float(max(errors)), 'max_normal_equation_residual': float(max(map(abs, normal_residual)))})
    assert set(model['models']) == set(coefficients) and len(coefficients) == 30
    cal_worlds = sorted(w['name'] for w in world_list if w['split'] == 'calibration')
    candidates = []
    cal = model['calibration']
    for index, margin in enumerate(MARGINS):
        selected = []
        details = []
        for world in cal_worlds:
            predicted = scores(coefficients, episodes[world, 'C']['features'], 'full')
            option = choose(predicted, margin)
            e = episodes[world, option]
            selected.append(e)
            details.append({'world': world, 'selected_option': option,
                            'scores': [str(predicted[k][2]) for k in OPTIONS], 'raw_sha256': e['receipt']['raw_sha256']})
        row = aggregate(selected, index)
        candidates.append(row)
        provided = cal['grid'][index]
        assert provided['index'] == index and (None if provided['margin'] is None else F(provided['margin'])) == margin
        assert provided['selections'] == details
        compare_total(provided, row)
    best, calibration_detail = rank_complete(candidates, lambda index: -index)
    margin = MARGINS[best['key']]
    assert cal['selected_grid_index'] == best['key']
    assert (None if cal['shared_margin'] is None else F(cal['shared_margin'])) == margin
    assert cal['used_variant'] == 'full' and cal['shared_by'] == ['full', 'nohistory', 'nobudget', 'tasks_only']
    lookup = {}
    lookup_details = {}
    for budget in (8, 16):
        candidates = []
        for index, option in enumerate(OPTIONS):
            observed = [episodes[w['name'], option] for w in world_list if w['split'] == 'train' and w['budget'] == budget]
            row = aggregate(observed, option)
            candidates.append(row)
            provided = cal['lookup_candidates'][str(budget)][index]
            assert provided['option'] == option and provided['index'] == index
            compare_total(provided, row)
        winner, details = rank_complete(candidates, OPTIONS.index)
        lookup[str(budget)] = winner['key']
        lookup_details[str(budget)] = details
    assert lookup == cal['budget_lookup'] and cal['lookup_split'] == 'train'
    parameters = {k: list(map(F, value['coefficients'])) for k, value in model['parameters'].items()}
    expected_parameters = dict(coefficients)
    expected_parameters['shared_margin'] = [F(margin is None), margin or F(0)]
    for budget, option in lookup.items():
        expected_parameters['budget_lookup_' + budget] = [F(OPTIONS.index(option))]
    assert parameters == expected_parameters
    result = {'passed': False, 'status': 'TRAIN_CAL_model_calibration_pass_TEST_pending',
        'TRAIN_CAL_passed': True, 'raw_labels_rebuilt': len(reconstructed), 'exact_ridge_heads': refits,
        'quantization_differences': exact_quantization_differences, 'calibration': calibration_detail,
        'coefficient_value_count': 30 * 26,
        'exact_quantized_coefficients_equal': not exact_quantization_differences,
        'numerical_checks': {'max_unrounded_coefficient_absolute_error_limit': '1/10000000000',
                             'max_normal_equation_residual_limit': '1/1000000000',
                             'possible_one_quantization_unit_differences_reported_separately': True},
        'bindings': {name: sha(HERE / name) for name in ('REGISTRATION.json', 'TRAIN_CAL_LABELS.json',
            'MODELS_FROZEN_BEFORE_TEST.json', 'MODEL_FREEZE_RECEIPT.json', 'FIT_START.json', 'TC_RECEIPT.json',
            'TC_START.json', 'PREFIX_BEFORE_FIT.json')},
        'scope': 'Raw outcomes, model fitting, calibration and deployed selector; physical/macro-tail audits are separate.',
        'shared_margin': margin, 'budget_lookup': lookup, 'lookup_ranking': lookup_details,
        'chronology': chronology(registration, list(episodes.values())),
        'reconstructed_label_rows': reconstructed, 'TEST_checks': [], 'nobudget_pairs': []}
    test_missing = []
    test_episodes = []
    for w in world_list:
        if w['split'] != 'test':
            continue
        for policy in registration['test_policies']:
            path = HERE / 'runs' / (w['name'] + '__' + policy + '.receipt.json')
            if not path.exists():
                test_missing.append(str(path.name))
            else:
                test_episodes.append(read_episode(path))
    result['TEST_completed_receipts'] = len(test_episodes)
    if test_missing:
        result['missing_TEST_receipts'] = test_missing
        return result
    assert len(test_episodes) == 56
    no_budget = {}
    for e in test_episodes:
        assert e['input_parameters'] == parameters, ('deployed M parameters mismatch', e['world'], e['policy'])
        w = worlds[e['world']]
        assert w['split'] == 'test' and w['budget'] == e['budget']
        policy = e['policy']
        choice = e['choice']
        learned = policy in ('full', 'nohistory', 'nobudget', 'tasks_only')
        if choice is None:
            assert e['features'] is None
            result['TEST_checks'].append({'world': e['world'], 'policy': policy, 'gate_unavailable': True})
            continue
        if learned:
            predicted = scores(coefficients, e['features'], policy)
            assert choice['learned'] and choice['inference_calls'] == 1 and choice['inference_ns'] >= 0
            assert choice['margin_infinite'] == (margin is None) and F(choice['margin']) == (margin or F(0))
            for option, actual in zip(OPTIONS, choice['scores']):
                assert actual['option'] == option
                assert tuple(F(actual[head]) for head in ('tasks', 'time', 'total')) == predicted[option], ('deployed score', e['world'], policy, option)
            selected = choose(predicted, margin)
        else:
            selected = 'W' if policy == 'WAIT' else 'C' if policy == 'condition' else lookup[str(e['budget'])]
            assert not choice['learned'] and choice['inference_calls'] == 0
        assert choice['selected_option'] == selected, ('deployed macro', e['world'], policy)
        result['TEST_checks'].append({'world': e['world'], 'family_key': w['family_key'], 'budget': e['budget'],
             'policy': policy, 'selected': selected, 'learned': learned, 'tasks': e['tasks'],
             'T_lower': e['time_lower'], 'T_upper': e['time_upper'], 'queries': e['queries'],
             'receipt_sha256': e['receipt_sha256'], 'raw_sha256': e['receipt']['raw_sha256']})
        if policy == 'nobudget':
            no_budget.setdefault(w['family_key'], []).append((e, predicted, selected))
    for family, pair in no_budget.items():
        assert len(pair) == 2
        a, b = pair
        assert [v for j, v in enumerate(a[0]['features']) if j not in MASKS['nobudget']] == [v for j, v in enumerate(b[0]['features']) if j not in MASKS['nobudget']]
        assert a[1] == b[1] and a[2] == b[2], ('nobudget changed across budgets', family)
        result['nobudget_pairs'].append({'family': family, 'passed': True, 'selected': a[2]})
    result['chronology'] = chronology(registration, list(episodes.values()), test_episodes)
    result['passed'] = True
    result['status'] = 'complete_96_raw_labels_30_heads_CAL_and_56_TEST_deployments'
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mechanics-only', action='store_true')
    args = parser.parse_args()
    result = {'passed': False, 'status': 'awaiting_candidate_schema_and_raw_data',
              'created_UTC': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'candidate_fit_imports': False, 'auditor_sha256': sha(__file__),
              'mechanics': mechanics()}
    prior_path = HERE / 'MENTOR_MODEL_AUDIT.json'
    if prior_path.exists():
        prior = json.loads(prior_path.read_text())
        history = prior.get('audit_history', [])
        history.append({key: prior.get(key) for key in ('created_UTC', 'status', 'passed', 'auditor_sha256', 'error')})
        result['audit_history'] = history
        result['previous_audit_sha256'] = sha(prior_path)
    if args.mechanics_only:
        result['status'] = 'auditor_mechanics_only_scientific_audit_pending'
    else:
        try:
            result.update(scientific_audit())
        except Exception as exc:
            result.update(passed=False, status='audit_failed', error=repr(exc))
            (HERE / 'MENTOR_MODEL_AUDIT.json').write_text(json.dumps(result, indent=2, default=str) + '\n')
            raise
    (HERE / 'MENTOR_MODEL_AUDIT.json').write_text(json.dumps(result, indent=2, default=str) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k not in ('reconstructed_label_rows', 'TEST_checks', 'exact_ridge_heads', 'missing_TEST_receipts')}, default=str))


if __name__ == '__main__':
    main()
