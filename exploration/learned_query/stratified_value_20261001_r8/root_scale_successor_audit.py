"""Independently bind the N32 guard-only successor and preserve original failures."""
from pathlib import Path
import json

import root_heldout_audit as audit

HERE = Path(__file__).resolve().parent


def main():
    successor = HERE / 'scale_guard_successor'
    original = audit.read(HERE / 'REGISTRATION.json')
    registration = audit.read(successor / 'REGISTRATION.json')
    model_path = HERE / 'MODELS_FROZEN_BEFORE_TEST.json'
    assert registration['parent_registration_sha256'] == audit.sha(HERE / 'REGISTRATION.json')
    assert registration['parent_model_sha256'] == audit.sha(model_path)
    assert registration['parent_native_source_sha256'] == audit.sha(HERE / 'joint_history_native.cpp')
    assert registration['post_outcome_compatibility_correction']
    assert not registration['new_independent_test_worlds']
    old_source = (HERE / 'joint_history_native.cpp').read_bytes()
    assert old_source.count(b'robots.size()<=16') == 1
    assert (successor / 'joint_history_native.cpp').read_bytes() == old_source.replace(
        b'robots.size()<=16', b'robots.size()<=32')
    assert registration['policies'] == original['policies']
    assert registration['worlds'] == [w for w in original['worlds'] if w['split'] == 'scale']
    assert registration['bridge_sha256'] == original['bridge_sha256']
    assert registration['config_sha256'] == original['config_sha256']
    assert len(registration['original_guard_failures']) == 12
    for item in registration['original_guard_failures']:
        name = item['world'] + '__' + item['policy'] + '.receipt.json'
        old_path, new_path = HERE / 'runs' / name, successor / 'runs' / name
        old, new = audit.read(old_path), audit.read(new_path)
        assert audit.sha(old_path) == item['parent_receipt_sha256']
        assert old['error'] is not None and old['summary'] is None
        assert 'fixed joint support/training identity differs' in old['native_stderr']
        assert old['input_sha256'] == item['input_sha256'] == new['input_sha256']
        assert new['error'] is None and new['summary'] is not None
    output_path = HERE / 'ROOT_SCALE_SUCCESSOR_AUDIT.json'
    audit.main(here=successor, model_path=model_path, expected_episodes=12, output_path=output_path)
    scale = audit.read(output_path)
    scale['uncertainty'] = 'Two N32 worlds; post-outcome guard-only compatibility correction, not new independent test worlds.'
    scale['original_guard_failures_preserved'] = 12
    scale['exact_native_change'] = 'One constructor guard: robots.size()<=16 to robots.size()<=32.'
    output_path.write_text(json.dumps(scale, indent=2) + '\n')
    parent = audit.read(HERE / 'ROOT_HELDOUT_AUDIT.json')
    assert parent['passed'] and scale['passed']
    assert parent['files']['registration'] == registration['parent_registration_sha256']
    assert parent['files']['model'] == registration['parent_model_sha256']
    for row in parent['rows']:
        path = HERE / 'runs' / (row['world'] + '__' + row['policy'] + '.receipt.json')
        assert audit.sha(path) == row['receipt_sha256']
    rows = [r for r in parent['rows'] if r['split'] == 'test'] + scale['rows']
    assert len(rows) == 60 and all(r['error'] is None for r in rows)
    result = dict(passed=True, implementation_imported=False,
                  rows=rows,
                  totals=[r for r in parent['totals'] if r['split'] == 'test'] +
                         [r for r in scale['totals'] if r['split'] == 'scale'],
                  paired_differences=parent['paired_differences'] + scale['paired_differences'],
                  family_effects=parent['family_effects'],
                  original_guard_failures=[r for r in parent['rows'] if r['split'] == 'scale'],
                  original_audit_sha256=audit.sha(HERE / 'ROOT_HELDOUT_AUDIT.json'),
                  scale_audit_sha256=audit.sha(output_path),
                  post_outcome_compatibility_correction=True,
                  uncertainty='Four N16 map/task families, each IID/SHIFT; two N32 transfer worlds. No 60-arm independent-sample inference.')
    (HERE / 'ROOT_COMPLETE_AUDIT.json').write_text(json.dumps(result, indent=2) + '\n')
    print('PASS: 60 completed arms plus 12 preserved input-guard failures; source change and all paired inputs verified.')


if __name__ == '__main__':
    main()
