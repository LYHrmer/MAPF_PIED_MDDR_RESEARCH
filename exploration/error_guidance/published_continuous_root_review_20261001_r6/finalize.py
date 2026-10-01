"""Publish completed evidence; never launches a native experiment or changes a freeze."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
MAIN = Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence')
NAMES = [f'published_continuous_execution_20261001_r6{s}' for s in ('', 'b', 'c')]


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for data in iter(lambda: stream.read(1 << 20), b''):
            digest.update(data)
    return digest.hexdigest()


def dump(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')


def main():
    final = BASE / NAMES[-1]
    source = MAIN / 'CONTINUOUS_EXECUTION_ROOT_20261001_R6.json'
    evidence = json.loads(source.read_text())
    ids = {r['id'] for r in json.loads((final / 'runs.json').read_text())['runs']}
    assert set(evidence['runs']) == ids
    assert set(evidence['clearance']) == ids
    assert all(r['passed'] for r in evidence['runs'].values())
    assert all(r['ticks'] == 8000 for r in evidence['clearance'].values())
    for name in ['CONTINUOUS_EXECUTION_ROOT_20261001_R6.json',
                 'verify_physical_clearance_20261001_r6.py',
                 'collect_continuous_audits_20261001_r6.py']:
        shutil.copyfile(MAIN / name, HERE / name)
    previous = final / 'audit.json'
    if previous.exists() and json.loads(previous.read_text()).get('orchestration') != 'root parallel finalized-receipt auditor':
        saved = final / 'audit_monitor_partial.json'
        assert not saved.exists()
        shutil.copyfile(previous, saved)
    dump(previous, {
        'all_available_passed': True,
        'runs': evidence['runs'],
        'auditor_sha256': sha(final / 'audit.py'),
        'mapping_replay_sha256': sha(final / 'mapping_replay.py'),
        'orchestration_sha256': sha(HERE / 'collect_continuous_audits_20261001_r6.py'),
        'orchestration': 'root parallel finalized-receipt auditor',
        'independent_sampled_geometry': '../' + HERE.name + '/' + source.name,
    })
    subprocess.run(['rtk', 'proxy', 'python3', str(final / 'summarize_results.py')], check=True)
    pins = {}
    for name in NAMES:
        path = BASE / name
        freeze = json.loads((path / 'freeze.json').read_text())
        for raw_path, expected in freeze['pins'].items():
            assert sha(raw_path) == expected, raw_path
        pins[name] = {'freeze_sha256': sha(path / 'freeze.json'),
                      'frozen_pins_verified': len(freeze['pins'])}
    dump(HERE / 'FROZEN_IDENTITIES_ROOT.json', pins)
    print(json.dumps({'finalized_runs': len(ids), 'all_audits_passed': True,
                      'sampled_envelopes_separated': all(r['all_sampled_circular_envelopes_separated'] for r in evidence['clearance'].values()),
                      'minimum_pair_gap_m': min(r['closest_pair']['circular_footprint_gap_m'] for r in evidence['clearance'].values()),
                      'minimum_box_gap_m': min(r['closest_obstacle']['circular_footprint_gap_m'] for r in evidence['clearance'].values()),
                      'freeze_checks': pins}), flush=True)


if __name__ == '__main__':
    main()
