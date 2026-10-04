"""Independent R13 raw-label/model/calibration audit.

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
OPTIONS = ('C', 'LD')
MASKS = {'full': (), 'no_history_prob': (0, 9)}
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
    assert all(len(x) == 10 for x in features)
    x = [[F(0) if j in masked else F(value) for j, value in enumerate(row)] for row in features]
    y = [[F(value) for value in row] for row in labels]
    width = len(y[0])
    weights = [F(1, 2)] * len(x)
    mass = sum(weights)
    means = [sum(w * row[j] for w, row in zip(weights, x)) / mass for j in range(10)]
    variances = [sum(w * (row[j] - means[j])**2 for w, row in zip(weights, x)) / mass for j in range(10)]
    # The pre-frozen candidate uses scale=1 for std<1e-12.
    scale_squared = [v if v >= F(1, 10**24) else F(1) for v in variances]
    target_means = [sum(w * row[k] for w, row in zip(weights, y)) / mass for k in range(width)]
    centered = [[row[j] - means[j] for j in range(10)] for row in x]
    matrix = [[sum(w * row[i] * row[j] for w, row in zip(weights, centered)) +
               (scale_squared[i] if i == j else 0) for j in range(10)] for i in range(10)]
    rhs = [[sum(w * row[j] * (target[k] - target_means[k])
                for w, row, target in zip(weights, centered, y)) for k in range(width)] for j in range(10)]
    beta = gauss_solve(matrix, rhs)
    raw = [[target_means[k] - sum(means[j] * beta[j][k] for j in range(10))] +
           [beta[j][k] for j in range(10)] for k in range(width)]
    return {'means': means, 'variances': variances, 'scale_squared': scale_squared,
            'unquantized': raw, 'coefficients': [[quantize9(v) for v in row] for row in raw],
            'row_weights': weights, 'lambda': F(1)}


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
    assert tc_done['native_episodes'] == 64 and tc_done['failed'] == 0
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


def read_episode(path):
    receipt = json.loads(path.read_text())
    assert receipt['error'] is None
    for key in ('raw', 'input', 'planner'):
        assert sha(receipt[key]) == receipt[key + '_sha256'], (path, key)
    fifo, parameters = {}, {}
    for line in Path(receipt['input']).read_text().splitlines():
        fields = line.split()
        if fields[0] == 'D': horizon = F(fields[3])
        elif fields[0] in ('R', 'F'): fifo.setdefault(int(fields[1]), []).append(int(fields[2]))
        elif fields[0] == 'M': parameters.setdefault(fields[1], []).append(F(int(fields[2]), int(fields[3])))
    assert len(fifo) == 16 and horizon == 128
    wanted = {(a, t) for a, tasks in fifo.items() for t in tasks[:4]}
    assert len(wanted) == 64
    services, choice, gate_actor, first_eligible = {}, None, None, None
    queries = 0
    summary = None
    with Path(receipt['raw']).open() as stream:
        for line in stream:
            event = json.loads(line)
            kind = event['event']
            if kind == 'task_service':
                key = event['agent'], event['task']
                assert key not in services
                lo, hi = bounds(event['at']); assert 0 <= lo <= hi <= horizon
                services[key] = lo, hi
            elif kind == 'certified_POSITION_committed': queries += 1
            elif kind == 'macro_choice':
                assert choice is None
                choice = event
                assert choice['feature_schema'] == 'late_target10_v1'
            elif kind == 'actor_decision':
                capacity = event['remaining_capacity']
                eligible = capacity > 0 and receipt['capacity'] - capacity >= receipt['capacity'] // 2 and event['candidates']
                if eligible and first_eligible is None: first_eligible = event['opportunity']
                if choice is not None and choice['opportunity'] == event['opportunity']:
                    assert gate_actor is None
                    gate_actor = event
            elif kind == 'joint_summary': summary = event
    assert summary and summary['served'] == len(services) and summary['queries'] == queries
    assert 0 <= queries <= receipt['capacity']
    features = None
    if choice:
        assert gate_actor and choice['at'] == gate_actor['at']
        assert receipt['policy'] != 'WAIT' and first_eligible == choice['opportunity']
        assert choice['initial_capacity'] == receipt['capacity']
        assert choice['remaining_capacity'] == gate_actor['remaining_capacity'] > 0
        assert choice['spent'] == receipt['capacity'] - choice['remaining_capacity'] >= receipt['capacity'] // 2
        candidates = gate_actor['candidates']
        def score(c):
            return F(c['probability']) * sum(F(1, claim['remaining_route_items'] * claim['owners']) for claim in c['claims'])
        target = min(candidates, key=lambda c: (-score(c), c['agent'], c['move']))
        assert (target['agent'], target['move']) == (choice['target_agent'], choice['target_move'])
        f = list(map(F, target['features'])); assert len(f) == 24
        inverse = sum(F(1, c['remaining_route_items'] * c['owners']) for c in target['claims'])
        minimum = min(c['remaining_route_items'] for c in target['claims'])
        assert F(target['probability']) == f[10]
        features = [f[10], f[0], f[18], inverse, F(minimum, 64), F(len(target['claims']), 15),
                    F(len(candidates) - 1, 15), F(choice['remaining_capacity'], 16), 1 - f[21], f[10] * inverse]
        assert list(map(F, choice['features'])) == features, ('late target features', path)
    elif receipt['policy'] != 'WAIT':
        assert first_eligible is None, ('missed eligible late gate', path)
    return {'world': receipt['world'], 'policy': receipt['policy'], 'budget': receipt['capacity'],
            'tasks': len(services), 'time_lower': sum(services.get(k, (horizon, horizon))[0] for k in wanted),
            'time_upper': sum(services.get(k, (horizon, horizon))[1] for k in wanted),
            'queries': queries, 'features': features, 'choice': choice, 'fifo': fifo,
            'input_parameters': parameters, 'receipt': receipt, 'receipt_sha256': sha(path)}


def predict(coefficients, features, variant):
    if features is None: return {'C': (F(0), F(0), F(0)), 'LD': (F(0), F(0), F(0))}
    heads = []
    for head in ('tasks', 'time'):
        c = coefficients[variant + '_LD_' + head]
        heads.append(c[0] + sum(c[j + 1] * features[j] for j in range(10) if j not in MASKS[variant]))
    return {'C': (F(0), F(0), F(0)), 'LD': (heads[0], heads[1], sum(heads))}


def choose(values, margin):
    return 'LD' if margin is not None and values['LD'][2] > margin else 'C'


def mechanics():
    xs = [[F(-1)] + [F(0)] * 9, [F(1)] + [F(0)] * 9]
    exact = ridge_heads(xs, [[F(-1)], [F(1)]])
    assert exact['coefficients'][0][:2] == [0, F(1, 2)]
    assert ridge_heads(xs, [[F(-1)], [F(1)]], (0, 9))['coefficients'][0] == [F(0)] * 11
    assert quantize9(F(1, 2 * 10**9)) == 0 and quantize9(F(3, 2 * 10**9)) == F(2, 10**9)
    coefficients = {v + '_LD_' + h: [F(0)] * 11 for v in MASKS for h in ('tasks', 'time')}
    coefficients['no_history_prob_LD_time'][1] = F(1)
    coefficients['no_history_prob_LD_time'][10] = F(2)
    assert predict(coefficients, [F(9)] * 10, 'no_history_prob')['LD'][2] == 0
    assert choose({'LD': (0, 0, F(1))}, F(1)) == 'C'
    assert choose({'LD': (0, 0, F(1))}, F(0)) == 'LD'
    assert choose({'LD': (0, 0, F(1))}, None) == 'C'
    rows = [{'key': 0, 'tasks': 1, 'time_lower': F(1), 'time_upper': F(3), 'queries': 2},
            {'key': 1, 'tasks': 1, 'time_lower': F(2), 'time_upper': F(4), 'queries': 1},
            {'key': 2, 'tasks': 1, 'time_lower': F(5), 'time_upper': F(6), 'queries': 0}]
    winner, detail = rank_complete(rows, lambda x: x)
    assert winner['key'] == 1 and detail['time_undominated'] == [0, 1]
    return {'passed': True, 'checks': ['exact_weighted_ridge', 'history_probability_mask_0_9',
             'nine_decimal_half_even', 'strict_margin_including_infinity', 'interval_undominated_query_order']}


def scientific_audit():
    required = ['REGISTRATION.json', 'TRAIN_CAL_LABELS.json', 'MODELS_FROZEN_BEFORE_TEST.json',
                'MODEL_FREEZE_RECEIPT.json', 'FIT_START.json', 'TC_START.json', 'TC_RECEIPT.json']
    missing = [n for n in required if not (HERE / n).exists()]
    if missing: return {'passed': False, 'status': 'awaiting_frozen_model', 'missing': missing}
    reg = load('REGISTRATION.json'); worlds = {w['name']: w for w in reg['worlds']}
    family_split = {}
    for w in worlds.values(): family_split.setdefault(w['family_key'], set()).add(w['split'])
    assert len(worlds) == 48 and len(family_split) == 24 and all(len(s) == 1 for s in family_split.values())
    for split, count in [('train', 12), ('calibration', 4), ('test', 8)]:
        assert sum(s == {split} for s in family_split.values()) == count
    for family in family_split:
        pair = [w for w in worlds.values() if w['family_key'] == family]
        assert len(pair) == 2 and {w['budget'] for w in pair} == {8, 16}
        assert pair[0]['robots'] == pair[1]['robots'] and pair[0]['seed'] == pair[1]['seed']
    episodes = {}
    for w in worlds.values():
        if w['split'] == 'test': continue
        for option in OPTIONS:
            path = HERE / 'runs' / (w['name'] + '__macro_' + option + '.receipt.json')
            if not path.exists(): return {'passed': False, 'status': 'missing_TC_receipt', 'missing': str(path)}
            e = read_episode(path)
            assert e['world'] == w['name'] and e['policy'] == 'macro_' + option and e['budget'] == w['budget']
            assert e['fifo'] == {r['agent']: [t['task'] for t in r['tasks']] for r in w['robots']}
            if e['choice']: assert e['choice']['selected_option'] == option and not e['choice']['learned']
            episodes[w['name'], option] = e
    rows = []
    for w in worlds.values():
        if w['split'] == 'test': continue
        base = episodes[w['name'], 'C']
        for option in OPTIONS:
            e = episodes[w['name'], option]; assert e['features'] == base['features']
            task = F(e['tasks'] - base['tasks'])
            time_gain = (base['time_lower'] + base['time_upper'] - e['time_lower'] - e['time_upper']) / (2 * DENOMINATOR)
            if e['features'] is None: assert task == time_gain == 0 and e['queries'] == base['queries']
            rows.append({'world': w['name'], 'family_key': w['family_key'], 'split': w['split'], 'budget': w['budget'],
                         'option': option, 'features': e['features'], 'weight': F(1, 2), 'task_target': task, 'time_target': time_gain,
                         'tasks': e['tasks'], 'queries': e['queries'], 'T_lower': e['time_lower'], 'T_upper': e['time_upper'],
                         'T_gain_lower': base['time_lower'] - e['time_upper'], 'T_gain_upper': base['time_upper'] - e['time_lower'],
                         'raw_sha256': e['receipt']['raw_sha256']})
    supplied = load('TRAIN_CAL_LABELS.json'); assert len(supplied) == len(rows) == 64
    for expected, observed in zip(rows, supplied):
        for k, value in expected.items():
            if isinstance(value, F): assert F(observed[k]) == value, ('label', expected['world'], k)
            elif k == 'features' and value is not None: assert list(map(F, observed[k])) == value
            else: assert observed[k] == value, ('label binding', k)
    model = load('MODELS_FROZEN_BEFORE_TEST.json')
    for key, name in [('labels_sha256', 'TRAIN_CAL_LABELS.json'), ('prefix_audit_sha256', 'PREFIX_BEFORE_FIT.json'), ('registration_sha256', 'REGISTRATION.json')]:
        assert model[key] == sha(HERE / name)
    train = [r for r in rows if r['split'] == 'train' and r['option'] == 'LD' and r['features'] is not None]
    coefficients, refits, differences = {}, [], []
    for variant, mask in MASKS.items():
        if not train:
            for head in ('tasks', 'time'):
                name = variant + '_LD_' + head; pub = model['models'][name]
                assert pub['train_rows'] == 0 and pub['bindings'] == [] and 'fallback' in pub
                assert pub['lambda_value'] == 1 and pub['masked_slots'] == list(mask)
                assert list(map(F, pub['coefficients'])) == [F(0)] * 11
                assert pub['unrounded_raw'] == pub['standardized_coefficients'] == [0.] * 11
                assert pub['train_mean'] == [0.] * 10 and pub['train_scale'] == [1.] * 10
                coefficients[name] = [F(0)] * 11
                refits.append({'head': name, 'TRAIN_context_rows': 0, 'preregistered_zero_fallback': True})
            continue
        targets = [[r['task_target'], r['time_target']] for r in train]
        exact = ridge_heads([r['features'] for r in train], targets, mask)
        bindings = [{'world': r['world'], 'family_key': r['family_key'], 'budget': r['budget'], 'option': 'LD', 'weight': '1/2'} for r in train]
        for h, head in enumerate(('tasks', 'time')):
            name = variant + '_LD_' + head; pub = model['models'][name]
            assert pub['lambda_value'] == 1 and pub['unpenalized_intercept'] is True
            assert pub['masked_slots'] == list(mask) and pub['train_rows'] == len(train) and pub['bindings'] == bindings
            for j in range(10):
                assert abs(F(str(pub['train_mean'][j])) - exact['means'][j]) < F(1, 10**11)
                assert abs(float(pub['train_scale'][j]) - math.sqrt(float(exact['scale_squared'][j]))) < 1e-11
            raw = list(map(lambda v: F(str(v)), pub['unrounded_raw'])); deployed = list(map(F, pub['coefficients']))
            assert len(raw) == len(deployed) == 11
            errors = [abs(a - b) for a, b in zip(raw, exact['unquantized'][h])]
            assert max(errors) < F(1, 10**10), ('unrounded coefficient', name, float(max(errors)))
            assert deployed == [F(str(round(float(v), 9))) for v in pub['unrounded_raw']]
            for j, (a, b) in enumerate(zip(deployed, exact['coefficients'][h])):
                if a != b:
                    differences.append({'head': name, 'coordinate': j, 'deployed': a, 'exact_quantized': b, 'unrounded_absolute_error': errors[j]})
                    assert abs(a - b) <= F(1, 10**9)
            residuals = [targets[i][h] - raw[0] - sum(raw[j + 1] * r['features'][j] for j in range(10) if j not in mask) for i, r in enumerate(train)]
            normal = [sum(residuals) / 2] + [sum((F(0) if j in mask else r['features'][j]) * v / 2 for r, v in zip(train, residuals)) - exact['scale_squared'][j] * raw[j + 1] for j in range(10)]
            assert max(map(abs, normal)) < F(1, 10**9), ('normal equation residual', name)
            standard = list(map(float, pub['standardized_coefficients']))
            assert abs(standard[0] - float(sum(row[h] for row in targets) / len(targets))) < 1e-10
            assert all(abs(standard[j + 1] - float(raw[j + 1]) * pub['train_scale'][j]) < 1e-10 for j in range(10))
            assert all(deployed[j + 1] == 0 for j in mask)
            coefficients[name] = deployed
            refits.append({'head': name, 'TRAIN_context_rows': len(train), 'max_unrounded_error': float(max(errors)), 'max_normal_equation_residual': float(max(map(abs, normal)))})
    assert set(coefficients) == set(model['models']) and len(coefficients) == 4
    cal = model['calibration']; candidates = []
    for index, margin in enumerate(MARGINS):
        chosen, details = [], []
        for world in sorted(w['name'] for w in worlds.values() if w['split'] == 'calibration'):
            scores = predict(coefficients, episodes[world, 'C']['features'], 'full'); option = choose(scores, margin)
            e = episodes[world, option]; chosen.append(e)
            details.append({'world': world, 'selected_option': option, 'scores': [str(scores[o][2]) for o in OPTIONS], 'raw_sha256': e['receipt']['raw_sha256']})
        row = aggregate(chosen, index); candidates.append(row); published = cal['grid'][index]
        assert published['index'] == index and (None if published['margin'] is None else F(published['margin'])) == margin
        assert published['selections'] == details; compare_total(published, row)
    best, ranking = rank_complete(candidates, lambda index: -index); margin = MARGINS[best['key']]
    assert cal['selected_grid_index'] == best['key'] and (None if cal['shared_margin'] is None else F(cal['shared_margin'])) == margin
    assert cal['used_variant'] == 'full' and cal['shared_by'] == ['full', 'no_history_prob']
    lookup, lookup_rank = {}, {}
    for budget in (8, 16):
        choices = []
        for index, option in enumerate(OPTIONS):
            row = aggregate([episodes[w['name'], option] for w in worlds.values() if w['split'] == 'train' and w['budget'] == budget], option)
            published = cal['lookup_candidates'][str(budget)][index]
            assert published['option'] == option and published['index'] == index; compare_total(published, row); choices.append(row)
        winner, detail = rank_complete(choices, OPTIONS.index); lookup[str(budget)] = winner['key']; lookup_rank[str(budget)] = detail
    assert cal['lookup_split'] == 'train' and lookup == cal['budget_lookup']
    parameters = {name: list(map(F, value['coefficients'])) for name, value in model['parameters'].items()}
    expected = dict(coefficients); expected['shared_margin'] = [F(margin is None), margin or F(0)]
    for budget, option in lookup.items(): expected['budget_lookup_' + budget] = [F(OPTIONS.index(option))]
    assert parameters == expected
    result = {'passed': False, 'TRAIN_CAL_passed': True, 'status': 'TRAIN_CAL_PASS_TEST_pending', 'raw_labels_rebuilt': 64,
              'TRAIN_gate_contexts': len(train), 'TRAIN_no_gate_contexts': 24 - len(train), 'exact_ridge_heads': refits,
              'coefficient_value_count': 44, 'quantization_differences': differences, 'exact_quantized_coefficients_equal': not differences,
              'numerical_limits': {'coefficient_absolute': '1e-10', 'normal_equation_residual': '1e-9', 'rounding_difference_reported': True},
              'calibration': ranking, 'shared_margin': margin, 'budget_lookup': lookup, 'lookup_ranking': lookup_rank,
              'bindings': {n: sha(HERE/n) for n in required + ['PREFIX_BEFORE_FIT.json']},
              'chronology': chronology(reg, list(episodes.values())), 'reconstructed_label_rows': rows,
              'TEST_checks': [], 'scope': 'Independent raw-label/Fraction fit/CAL/deployed score audit; complete physics/tail audit is separate. No cross-budget feature invariance asserted for R13 late gates.'}
    tests, missing = [], []
    for w in worlds.values():
        if w['split'] != 'test': continue
        for policy in reg['test_policies']:
            path = HERE/'runs'/(w['name']+'__'+policy+'.receipt.json')
            if not path.exists(): missing.append(path.name)
            else: tests.append(read_episode(path))
    result['TEST_completed_receipts'] = len(tests)
    if missing:
        result['missing_TEST_receipts'] = missing; return result
    assert len(tests) == 96
    for e in tests:
        w = worlds[e['world']]; assert w['split'] == 'test' and w['budget'] == e['budget']
        assert e['input_parameters'] == parameters, ('native parameters', e['world'], e['policy'])
        assert e['fifo'] == {r['agent']: [t['task'] for t in r['tasks']] for r in w['robots']}
        choice = e['choice']; policy = e['policy']; learned = policy in MASKS
        if choice:
            if learned:
                values = predict(coefficients, e['features'], policy)
                assert choice['learned'] and choice['inference_calls'] == 1 and choice['inference_ns'] >= 0
                assert choice['margin_infinite'] == (margin is None) and F(choice['margin']) == (margin or F(0))
                assert len(choice['scores']) == 2
                for option, score in zip(OPTIONS, choice['scores']):
                    assert score['option'] == option and tuple(F(score[h]) for h in ('tasks','time','total')) == values[option]
                selected = choose(values, margin)
            else:
                selected = 'C' if policy == 'condition' else 'LD' if policy == 'alwaysLD' else lookup[str(e['budget'])]
                assert not choice['learned'] and choice['inference_calls'] == 0
            assert choice['selected_option'] == selected
        else: selected = 'W' if policy == 'WAIT' else 'C_no_gate'
        result['TEST_checks'].append({'world': e['world'], 'family_key': w['family_key'], 'budget': e['budget'], 'policy': policy,
           'selected': selected, 'gate_available': choice is not None, 'learned_inference': learned and choice is not None,
           'tasks': e['tasks'], 'T_lower': e['time_lower'], 'T_upper': e['time_upper'], 'queries': e['queries'],
           'raw_sha256': e['receipt']['raw_sha256'], 'receipt_sha256': e['receipt_sha256']})
    result['chronology'] = chronology(reg, list(episodes.values()), tests)
    result['passed'] = True; result['status'] = 'PASS_64_raw_labels_4_heads_CAL_lookup_and_96_TEST'
    return result


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--mechanics-only', action='store_true'); args = parser.parse_args()
    result = {'passed': False, 'created_UTC': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'auditor_sha256': sha(__file__), 'candidate_fit_imports': False, 'mechanics': mechanics()}
    prior_path = HERE/'MENTOR_MODEL_AUDIT.json'
    if prior_path.exists():
        prior = load('MENTOR_MODEL_AUDIT.json'); history = prior.get('audit_history', [])
        history.append({k: prior.get(k) for k in ('created_UTC','status','passed','auditor_sha256','error')})
        result['audit_history'] = history; result['previous_audit_sha256'] = sha(prior_path)
    try:
        result.update({'status': 'mechanics_only_scientific_pending'} if args.mechanics_only else scientific_audit())
    except Exception as exc:
        result.update(passed=False,status='audit_failed',error=repr(exc))
        prior_path.write_text(json.dumps(result,indent=2,default=str)+'\n'); raise
    prior_path.write_text(json.dumps(result,indent=2,default=str)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('reconstructed_label_rows','TEST_checks','missing_TEST_receipts')},default=str))


if __name__ == '__main__': main()

