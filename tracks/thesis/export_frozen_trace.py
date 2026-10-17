"""Re-export frozen DEV evidence; never construct or execute a scientific model."""
import argparse
import csv
from fractions import Fraction
import hashlib
import io
import json
import math
from pathlib import Path
import re
import subprocess
import types


BASE = '4a89183cf0827dcae2fa20a7d816c760e4150457'
EVIDENCE_COMMIT = 'ae058c5025eaaa61a424ef7627515d40c2e83997'
EVIDENCE_ROOT = 'exploration/spatial_constraints_s1_20261016/preexecution_dev_once_20261018/'
CASES = {'ids13_initial': 57, 'ids13_enumerate': 57,
         'ids013_initial': 74, 'ids013_enumerate': 74}
HERE = Path(__file__).resolve().parent
MODE = 'OFFLINE_REEXPORT'
POSE_SERIALIZATION_TOLERANCE = 1e-9
ZERO_COMMAND_TOLERANCE = 1e-12


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def _git(repo, *args):
    return subprocess.check_output(['git', '--no-replace-objects', '--literal-pathspecs',
                                    '-C', str(repo), *args], stderr=subprocess.PIPE)


def load_reader(repo, lock):
    """Bootstrap only the locked reader, checking its bytes BEFORE exec/import."""
    require(set(lock) == {'schema', 'reader', 'manifest'}
            and lock['schema'] == 'thesis_shared_lock_v1', 'invalid shared lock')
    for name, path in [('reader', 'shared/pinned.py'), ('manifest', 'shared/manifest.json')]:
        pin = lock[name]
        require(set(pin) == {'commit', 'path', 'blob_oid', 'sha256'}
                and pin['commit'] == BASE and pin['path'] == path
                and re.fullmatch('[0-9a-f]{40}', pin['blob_oid'])
                and re.fullmatch('[0-9a-f]{64}', pin['sha256']), 'invalid fixed shared pin')
    pin = lock['reader']
    require(_git(repo, 'cat-file', '-t', BASE).strip() == b'commit', 'base is not a commit')
    tree = _git(repo, 'ls-tree', '-z', '--full-tree', BASE, '--', pin['path'])
    expected = [f'{mode} blob {pin["blob_oid"]}\t{pin["path"]}\0'.encode()
                for mode in ('100644', '100755')]
    require(tree in expected, 'reader is not the pinned regular blob')
    raw = _git(repo, 'cat-file', 'blob', pin['blob_oid'])
    require(sha(raw) == pin['sha256'], 'reader content SHA-256 mismatch before execution')
    reader = types.ModuleType('_thesis_locked_git_reader')
    exec(compile(raw, BASE + ':' + pin['path'], 'exec'), reader.__dict__)
    return reader


def load_evidence(repo, lock):
    reader = load_reader(repo, lock)
    manifest = json.loads(reader.read_blob(repo, lock['manifest']))
    require(manifest['schema'] == reader.SCHEMA and manifest['scope'] == reader.SCOPE
            and set(manifest['modules']) == reader.MODULES, 'shared module manifest changed')
    entries = manifest['evidence']['entries']
    require(manifest['evidence']['status'] == 'PINNED' and len(entries) == 25,
            'expected 25 pinned DEV evidence entries')
    paths = {'run_receipt': EVIDENCE_ROOT + 'RUN_RECEIPT.json'}
    for case in CASES:
        paths.update({case + '_events': EVIDENCE_ROOT + case + '/events.ndjson',
                      case + '_result': EVIDENCE_ROOT + case + '/result.json'})
    pins, evidence = {}, {}
    for name, path in paths.items():
        pin = entries[name]
        require(pin['commit'] == EVIDENCE_COMMIT and pin['path'] == path,
                'unexpected frozen evidence identity: ' + name)
        evidence[name] = reader.read_blob(repo, pin)
        pins[name] = pin
    # The 12 science module bytes are deliberately never loaded or executed here.
    return evidence, pins


def number(value):
    require(not isinstance(value, bool), 'boolean is not a time or numeric measurement')
    return Fraction(str(value))


def unique(items, key, name):
    result = {}
    for item in items:
        k = key(item)
        require(k not in result, 'duplicate ' + name + ': ' + str(k))
        result[k] = item
    return result


def vector(value, length, name):
    require(isinstance(value, list) and len(value) == length, 'invalid ' + name)
    require(all(isinstance(x, (int, float)) and not isinstance(x, bool)
                and math.isfinite(x) for x in value), 'nonfinite/non-numeric ' + name)
    return value


def close_vector(a, b, name):
    require(len(a) == len(b) and all(math.isclose(x, y, rel_tol=0,
            abs_tol=POSE_SERIALIZATION_TOLERANCE) for x, y in zip(a, b)), name + ' mismatch')


def command_phase(state, v, omega):
    """Describe public state plus logged commands, not acceleration or motor ACK."""
    if state in ('STOPPED', 'DONE'):
        require(abs(v) <= ZERO_COMMAND_TOLERANCE and abs(omega) <= ZERO_COMMAND_TOLERANCE,
                'stopped/done public state has nonzero logged command')
        return state
    require(state == 'RUNNING', 'unsupported public state')
    moving, turning = abs(v) > ZERO_COMMAND_TOLERANCE, abs(omega) > ZERO_COMMAND_TOLERANCE
    return { (False, False): 'ZERO_INPUT_AT_RUNNING_CAPTURE',
             (True, False): 'TRANSLATION_COMMAND', (False, True): 'ROTATION_COMMAND',
             (True, True): 'TRANSLATION_AND_ROTATION_COMMAND'}[moving, turning]


def join_records(case, records, result):
    """Join by exact capture/sequence and bind each delivery to its acceptance receipt."""
    session, source = result['session_receipt'], result['source']
    evaluations = [r['data'] for r in records if r['event'] == 'evaluation_only']
    evals = unique(evaluations, lambda r: (r['robot'], number(r['capture'])), 'evaluation capture')
    packets = unique([r['packet'] for r in records if r['event'] == 'capture'],
                     lambda p: (p['binding']['robot'], p['seq']), 'packet sequence')
    captures = unique(packets.values(), lambda p: (p['binding']['robot'], number(p['capture'])),
                      'packet capture')
    deliveries = unique([r for r in records if r['event'] == 'delivery'],
                        lambda d: (d['robot'], d['seq']), 'delivery sequence')
    attempts = unique(session['receive_attempts'],
                      lambda a: (a['sha256'], a['bytes'], number(a['now'])), 'receive attempt')
    require(set(evals) == set(captures), 'evaluation/capture coverage mismatch')
    require(set(packets) == set(deliveries), 'capture/delivery sequence coverage mismatch')
    require(len(evals) == session['evaluation_records_count'], 'evaluation count mismatch')
    require(sha(canonical(evaluations)) == session['evaluation_records_sha256'],
            'evaluation records digest mismatch')
    require(len(packets) == session['feedback_generated']['count']
            == session['incoming_feedback_attempts']['count'] == len(attempts),
            'feedback/receive attempt count mismatch')
    robots = set(source['selected_ids'])
    require({key[0] for key in packets} == robots, 'source robot IDs mismatch')
    require(set(session['completion']) == set(result['completion']) == robots,
            'completion robot IDs mismatch')
    used_attempts, completions, rows = set(), {}, []
    for robot in sorted(robots):
        robot_packets = sorted((p for p in packets.values() if p['binding']['robot'] == robot),
                               key=lambda p: p['seq'])
        require([p['seq'] for p in robot_packets] == list(range(len(robot_packets)))
                and all(type(p['seq']) is int for p in robot_packets), 'noncontiguous sequence')
        times = [number(p['capture']) for p in robot_packets]
        require(times == sorted(set(times)), 'capture time/sequence order mismatch')
    for (robot, seq), packet in sorted(packets.items()):
        binding, capture = packet['binding'], number(packet['capture'])
        require(binding['task'] == session['task'] and binding['commitment'] == session['commitment']
                and binding['condition'] == source['source_condition'], 'task binding mismatch')
        delivery = deliveries[robot, seq]
        received = number(delivery['now'])
        require(delivery['kind'] == packet['kind'] and received == number(packet['delivery'])
                and received >= capture, 'delivery kind/time mismatch')
        wire = canonical(packet)
        attempt_key = (sha(wire), len(wire), received)
        require(attempt_key in attempts and attempt_key not in used_attempts,
                'delivery lacks unique matching packet acceptance receipt')
        used_attempts.add(attempt_key)
        accepted = attempts[attempt_key]['accepted']
        require(type(accepted) is bool, 'non-boolean receive acceptance')
        data = evals[robot, capture]['data']
        evaluation = data['evaluation']
        require(number(evaluation['physical_time']) == capture
                and evaluation['shared_clock'] == packet['clock'], 'evaluation capture/clock mismatch')
        phase = number(evaluation['controller_phase'])
        require(number(packet['phase_lo']) <= phase <= number(packet['phase_hi']),
                'controller phase outside public interval')
        ref = vector(evaluation['pose_ref'], 3, 'reference pose')
        truth = evaluation.get('pose_true')
        if truth is not None:
            truth = vector(truth, 3, 'truth pose')
        observed = vector(data['observation'], 2, 'localization observation')
        public_observed = [float(number(packet['observed_x'])), float(number(packet['observed_y']))]
        close_vector(observed, public_observed, 'public/evaluation observation')
        tracking = [a - b for a, b in zip(truth, ref)] if truth is not None else [None] * 3
        localization = [observed[i] - truth[i] for i in range(2)] if truth is not None else [None] * 2
        reported = [observed[i] - ref[i] for i in range(2)]
        if truth is not None:
            for name, computed in [('tracking_error', tracking), ('localization_error', localization)]:
                if name in evaluation:
                    close_vector(vector(evaluation[name], len(computed), name), computed, name)
        control = evaluation['control']
        v, omega = vector([control['v_cmd'], control['omega_cmd']], 2, 'logged control')
        actual_phase = command_phase(packet['state'], v, omega)
        require(packet['kind'] in ('STATE', 'END'), 'unsupported feedback kind')
        is_end = packet['kind'] == 'END'
        if is_end:
            require(packet['state'] == 'DONE' and packet['completion_time'] is not None,
                    'END lacks DONE/actual completion time')
            completed = number(packet['completion_time'])
            require(completed <= capture, 'END completion is after capture')
            if accepted:
                require(robot not in completions and robot in session['completion'],
                        'duplicate or unreported accepted END')
                require(completed == number(session['completion'][robot])
                        == number(result['completion'][robot]), 'accepted END completion mismatch')
                completions[robot] = {
                    'case': case, 'arm': result['arm'], 'task': session['task'], 'robot': robot,
                    'end_seq': seq, 'completion_exact': str(completed), 'completion_s': float(completed),
                    'end_capture_s': float(capture), 'end_received_s': float(received),
                    'completion_from_epoch_s': float(completed - number(session['common_epoch'])),
                    'completion_support': 'ACCEPTED_END_PACKET_AND_MATCHING_RECEIVE_RECEIPT',
                    'packet_sha256': sha(wire)}
        else:
            require(packet['completion_time'] is None and packet['state'] != 'DONE',
                    'completion must be supported by END')
        row = {'case': case, 'arm': result['arm'], 'task': session['task'], 'robot': robot,
               'source_input_sha256': source['staged_input']['sha256'], 'seq': seq,
               'action': binding['action'], 'source_action_index': evaluation['action_index'],
               'data_scope': 'evaluation_only', 'capture_exact': str(capture), 'capture_s': float(capture),
               'feedback_receive_exact': str(received), 'feedback_receive_s': float(received),
               'transmission_delay_s': float(received - capture), 'trajectory_time_offset_s': None,
               'trajectory_time_offset_status': 'NOT_IDENTIFIED', 'feedback_accepted': accepted,
               'feedback_kind': packet['kind'], 'public_state_at_capture': packet['state'],
               'public_phase_lo_s': float(number(packet['phase_lo'])),
               'public_phase_hi_s': float(number(packet['phase_hi'])),
               'controller_phase_exact': str(phase), 'source_primitive_mode': evaluation['mode'],
               'actual_control_phase': actual_phase, 'v_cmd': v, 'omega_cmd': omega,
               'truth_status': 'SIMULATED_EVALUATION_TRUTH' if truth is not None else 'MISSING',
               'public_observed_x': public_observed[0], 'public_observed_y': public_observed[1],
               'localization_bound_declared': packet['localization_bound'],
               'accepted_end_completion_s': float(number(packet['completion_time'])) if is_end and accepted else None,
               'packet_sha256': sha(wire)}
        for prefix, values in [('ref', ref), ('true', truth or [None] * 3), ('observed', observed),
                               ('tracking', tracking), ('localization', localization), ('reported', reported)]:
            row.update({prefix + '_' + axis: value for axis, value in zip(('x', 'y', 'theta'), values)})
        for prefix, error in [('tracking', tracking), ('localization', localization), ('reported', reported)]:
            row[prefix + '_xy_norm'] = math.hypot(*error[:2]) if error[0] is not None else None
        rows.append(row)
    require(used_attempts == set(attempts), 'unmatched receive receipt')
    require(set(completions) == set(session['completion']), 'completion lacks accepted delivered END')
    return rows, list(completions.values())


def parse_case(case, raw_events, raw_result):
    records = [json.loads(line) for line in raw_events.splitlines()]
    result = json.loads(raw_result)
    require(result['case'] == case and result['arm'] == case.split('_', 1)[1], 'case/arm mismatch')
    require(result['journal']['sha256'] == sha(raw_events)
            and result['journal']['bytes'] == len(raw_events), 'journal identity mismatch')
    inputs = [r for r in records if r['event'] == 'input']
    require(len(inputs) == 1 and inputs[0]['source'] == result['source'], 'input/result source mismatch')
    require(set(inputs[0]['grid_paths']) == set(result['source']['selected_ids']), 'grid/source IDs mismatch')
    require(result['selected_ids'] == [int(r.removeprefix('agent')) for r in result['source']['selected_ids']],
            'result/source projection IDs mismatch')
    require(result['status'] == 'SUCCESS' and result['success'] is True
            and result['session_receipt']['status'] == 'SUCCESS'
            and result['session_receipt']['success'] is True, 'frozen case is not successful')
    rows, completions = join_records(case, records, result)
    require(len(rows) == CASES[case], 'unexpected frozen evaluation coverage')
    return rows, completions, result


def csv_bytes(rows):
    buffer = io.StringIO(newline='')
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0]), lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode()


def export(repo, lock_path, output):
    lock_raw = lock_path.read_bytes()
    lock = json.loads(lock_raw)
    evidence, pins = load_evidence(repo, lock)
    receipt = json.loads(evidence['run_receipt'])
    receipts = unique(receipt['rows'], lambda r: r['case'], 'run receipt case')
    require(set(receipts) == set(CASES) and receipt['planned_count'] == 4
            and receipt['success'] is True and receipt['failed_or_unrun_cases_excluded'] == 0,
            'incomplete frozen run receipt')
    traces, completions, cases, sources = [], [], {}, {}
    for case in CASES:
        rows, ends, result = parse_case(case, evidence[case + '_events'], evidence[case + '_result'])
        run = receipts[case]
        require(run['result'] == result and run['success'] is True and run['status'] == 'SUCCESS'
                and run['exit_code'] == 0, 'run receipt/result mismatch')
        traces.extend(rows)
        completions.extend(ends)
        sources[case] = result['source']
        cases[case] = {'rows': len(rows), 'accepted_end_count': len(ends),
                       'data_status': result['data_status'], 'evaluation_scope': result['session_receipt']['evaluation_scope'],
                       'collision_observations': result['collision_observations'],
                       'coverage_observations': result['coverage_observations'],
                       'evaluation_records_sha256': result['session_receipt']['evaluation_records_sha256']}
    payloads = {'trace.csv': csv_bytes(traces), 'completion.csv': csv_bytes(completions)}
    index = {
        'schema': 'thesis_frozen_trace_v1', 'mode': MODE, 'new_experiment': False,
        'shared_lock': lock, 'shared_lock_sha256': sha(lock_raw),
        'exporter_sha256': sha(Path(__file__).read_bytes()), 'consumed_evidence_pins': pins,
        'scientific_modules_loaded': [], 'manifest_registered_modules': 12,
        'manifest_registered_evidence': 25, 'consumed_evidence_count': len(pins),
        'rows': len(traces), 'accepted_end_count': len(completions), 'cases': cases, 'sources': sources,
        'files': {name: {'sha256': sha(raw), 'bytes': len(raw),
                          'rows': len(traces) if name == 'trace.csv' else len(completions)}
                  for name, raw in payloads.items()},
        'semantics': {
            'join': 'robot+exact_rational_capture -> robot+seq -> canonical_packet_sha256+bytes+exact_receive_time',
            'tracking': 'pose_true - pose_ref at same capture; theta is raw logged-coordinate difference',
            'localization': 'evaluation observation - pose_true at same capture; no observed heading exists',
            'reported': 'evaluation observation - pose_ref; never relabeled true tracking error',
            'missing_truth': 'true pose, tracking and localization error columns remain empty',
            'actual_control_phase': 'derived public state and logged v_cmd/omega_cmd; not hardware actuation ACK or acceleration',
            'source_primitive_mode': 'source label retained, including ACCEL while STOPPED with zero commands',
            'public_state_at_capture': 'state in captured packet; available to recipient only at accepted receive time',
            'transmission_delay': 'receive_time - capture_time; not a trajectory time offset',
            'trajectory_time_offset': 'NOT_IDENTIFIED; no independent timing fit or ground truth alignment claimed',
            'completion': 'accepted delivered END and receipt completion; completion time and receive time are separate',
            'numeric_units': 'poses x/y metres, theta radians; times seconds on declared source clock; commands m/s and rad/s',
            'public_observation_tolerance': POSE_SERIALIZATION_TOLERANCE,
            'command_zero_label_tolerance': ZERO_COMMAND_TOLERANCE,
        },
        'limits': [
            'One original R16 four-agent input projected to two/three robots and two correlated arms; not independent tasks.',
            'Same-projection arms share identical evaluation digests; 262 exported rows are not 262 independent observations.',
            'Evaluation-only reference/truth/control labels are offline diagnostic labels, not assumed online guard inputs.',
            'No model, solver, world, training or new science experiment executed.',
            'No empirical collision count, tube coverage rate, continuous safety or hard error bound inferred from sampled frames.',
            'Declared localization bound is source metadata; not an independently calibrated or validated bound.',
            'No SCI discrete-path to continuous-primitive adapter implemented by this exporter.',
        ],
    }
    output.mkdir(parents=True, exist_ok=True)
    for name, raw in payloads.items():
        (output / name).write_bytes(raw)
    (output / 'index.json').write_text(json.dumps(index, indent=2, sort_keys=True, ensure_ascii=False) + '\n')
    return {'mode': MODE, 'rows': len(traces), 'accepted_end_count': len(completions),
            'cases': {case: item['rows'] for case, item in cases.items()},
            'csv_bytes': sum(map(len, payloads.values())), 'output': str(output)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=HERE.parents[1])
    parser.add_argument('--lock', type=Path, default=HERE / 'shared.lock.json')
    parser.add_argument('--output', type=Path, default=HERE / 'derived')
    args = parser.parse_args()
    print(json.dumps(export(args.repo, args.lock, args.output), sort_keys=True))


if __name__ == '__main__':
    main()
