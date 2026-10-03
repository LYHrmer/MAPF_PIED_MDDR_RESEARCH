"""Semantic corruption checks for the independent root auditor, no native runs."""
from pathlib import Path
from tempfile import TemporaryDirectory
import hashlib
import json
import root_macro_audit as audit

P = Path(__file__).resolve().parent


def main():
    reg = json.loads((P / 'REGISTRATION.json').read_text())
    worlds = {w['name']: w for w in reg['worlds']}
    receipts = sorted((P / 'runs').glob('*.receipt.json'))
    required = {'macro_C', 'macro_L', 'macro_ED'}
    examples = {}
    for path in receipts:
        receipt = json.loads(path.read_text())
        if receipt['policy'] not in required or receipt['policy'] in examples:
            continue
        events = [json.loads(line) for line in Path(receipt['raw']).read_bytes().splitlines()]
        if receipt['policy'] == 'macro_ED' and not any(e.get('intervention_index') == 2 for e in events):
            continue
        audit.audit(worlds[receipt['world']], path)
        examples[receipt['policy']] = receipt, events
        if set(examples) == required:
            break
    assert set(examples) == required, 'Need completed TRAIN controls; do not generate new scientific samples.'
    outcomes = []
    for name, policy in [('false_gate_feature', 'macro_C'), ('false_gate_option', 'macro_C'),
                         ('unspent_budget_overstated', 'macro_C'), ('late_trigger_before_half_budget', 'macro_L'),
                         ('second_SKIP_reuses_first_occurrence', 'macro_ED')]:
        original, old_events = examples[policy]
        events = json.loads(json.dumps(old_events))
        if name == 'false_gate_feature':
            target = next(e for e in events if e['event'] == 'macro_choice')
            target['features'][0] = str(audit.F(target['features'][0]) + audit.F(1, 7))
        elif name == 'false_gate_option':
            next(e for e in events if e['event'] == 'macro_choice')['selected_option'] = 'W'
        elif name == 'unspent_budget_overstated':
            target = next(e for e in events if e['event'] == 'actor_decision' and e['opportunity'] > 1)
            target['remaining_capacity'] += 1
        elif name == 'late_trigger_before_half_budget':
            target = next(e for e in events if e['event'] == 'actor_decision')
            assert target['pair_stage'] == 0
            target['pair_stage'] = 1
        else:
            target = next(e for e in events if e['event'] == 'actor_decision' and e['intervention_index'] == 2)
            assert target['selected'] != target['anchor_move']
            target['selected'] = target['anchor_move']
        with TemporaryDirectory(prefix='r12-root-negative-') as temp:
            folder = Path(temp)
            raw = b''.join(json.dumps(e).encode() + b'\n' for e in events)
            (folder / 'mutated.jsonl').write_bytes(raw)
            receipt = dict(original, raw=str(folder / 'mutated.jsonl'), raw_sha256=hashlib.sha256(raw).hexdigest())
            receipt_path = folder / 'receipt.json'
            receipt_path.write_text(json.dumps(receipt))
            try:
                audit.audit(worlds[receipt['world']], receipt_path)
            except AssertionError:
                rejected = True
            else:
                rejected = False
            assert rejected, name
            outcomes.append({'name': name, 'rejected': True, 'source_raw_sha256': original['raw_sha256'],
                             'mutated_raw_sha256': receipt['raw_sha256'], 'hash_binding_updated_before_check': True})
    result = {'passed': True, 'native_runs_added': 0, 'controls': outcomes,
              'auditor_sha256': hashlib.sha256((P / 'root_macro_audit.py').read_bytes()).hexdigest(),
              'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (P / 'ROOT_AUDIT_NEGATIVE_CONTROLS.json').write_text(json.dumps(result, indent=2) + '\n')
    print('Independent auditor rejects all', len(outcomes), 'semantic corruptions with valid recomputed hashes')


if __name__ == '__main__':
    main()
