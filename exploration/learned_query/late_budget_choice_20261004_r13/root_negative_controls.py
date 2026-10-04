"""Mutate actual completed raw observations in temporary files; no extra native runs."""
import copy, hashlib, json, tempfile
from pathlib import Path
from root_macro_audit import audit, P

def main():
    reg = json.loads((P / 'REGISTRATION.json').read_text())
    worlds = {w['name']: w for w in reg['worlds']}
    source = None
    for path in sorted((P / 'runs').glob('*macro_LD*.receipt.json')):
        receipt = json.loads(path.read_text())
        events = [json.loads(line) for line in Path(receipt['raw']).read_text().splitlines()]
        if any(e['event'] == 'macro_choice' for e in events):
            source = path, receipt, events
            break
    assert source is not None
    path, receipt, events = source
    results = []
    for mutation in ['gate_wrong_spent', 'gate_false_history_probability', 'gate_wrong_target',
                     'pregate_wrong_action', 'late_wrong_mode', 'service_without_rest']:
        altered = copy.deepcopy(events)
        gate = next(e for e in altered if e['event'] == 'macro_choice')
        if mutation == 'gate_wrong_spent': gate['spent'] += 1
        elif mutation == 'gate_false_history_probability': gate['features'][0] = '7/3'
        elif mutation == 'gate_wrong_target': gate['target_move'] += '_stale'
        elif mutation == 'pregate_wrong_action':
            e = next(e for e in altered if e['event'] == 'actor_decision'); e['selected_kind'] = 'SKIP'
        elif mutation == 'late_wrong_mode':
            e = next(e for e in altered if e['event'] == 'actor_decision' and e['opportunity'] == gate['opportunity'])
            e['decision_mode'] = 'condition'
        else:
            e = next(e for e in altered if e['event'] == 'task_service'); e['original_endpoint_at_rest'] = False
        raw = ''.join(json.dumps(e, separators=(',', ':')) + '\n' for e in altered).encode()
        with tempfile.TemporaryDirectory(prefix='r13-root-negative-') as tmp:
            raw_path, receipt_path = Path(tmp) / 'raw.jsonl', Path(tmp) / 'receipt.json'
            raw_path.write_bytes(raw); changed = copy.deepcopy(receipt)
            changed['raw'], changed['raw_sha256'] = str(raw_path), hashlib.sha256(raw).hexdigest()
            receipt_path.write_text(json.dumps(changed))
            try: audit(worlds[receipt['world']], receipt_path)
            except AssertionError as exc: results.append({'mutation': mutation, 'rejected': True, 'reason': str(exc)})
            else: raise AssertionError('Accepted broken raw ' + mutation)
    report = {'passed': True, 'source_receipt': path.name, 'source_raw_sha256': receipt['raw_sha256'],
              'extra_native_runs': 0, 'checks': results}
    (P / 'ROOT_NEGATIVE_CONTROLS.json').write_text(json.dumps(report, indent=2) + '\n')
    print('ROOT_NEGATIVE_CONTROLS PASS', len(results))

if __name__ == '__main__': main()
