"""Recheck all committed raw records without the native simulator or old absolute paths.

This validates archive bytes and replays the independent macro/value auditor.
It is not a substitute for rerunning the physical simulator or retraining.
"""
from pathlib import Path, PurePosixPath
from tempfile import TemporaryDirectory
import hashlib
import importlib.util
import json
import shutil
import sys
import tarfile

P = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    manifest = json.loads((P / 'RAW_ARCHIVE_MANIFEST.json').read_text())
    reference = json.loads((P / 'ROOT_MACRO_AUDIT.json').read_text())
    assert manifest['passed'] and manifest['raw_archived_once']
    assert reference['passed'] and not reference['partial'] and reference['observed_runs'] == 152
    assert sha(P / 'root_macro_audit.py') == reference['auditor_sha256']
    with TemporaryDirectory(prefix='r12-offline-evidence-') as temporary:
        root = Path(temporary)
        seen = set()
        for archive in manifest['archives']:
            source = P / archive['path']
            assert source.stat().st_size == archive['bytes'] and sha(source) == archive['sha256']
            expected = {m['path']: m for m in archive['members']}
            found = set()
            with tarfile.open(source, 'r:gz') as package:
                for member in package:
                    name = PurePosixPath(member.name)
                    assert member.isfile() and len(name.parts) == 2 and name.parts[0] == 'runs'
                    assert not name.is_absolute() and '..' not in name.parts
                    assert member.name in expected and member.name not in seen
                    record = expected[member.name]
                    data = package.extractfile(member).read()
                    assert len(data) == member.size == record['bytes']
                    assert hashlib.sha256(data).hexdigest() == record['sha256']
                    target = root / member.name
                    target.parent.mkdir(exist_ok=True)
                    target.write_bytes(data)
                    seen.add(member.name); found.add(member.name)
            assert found == set(expected)
        assert len(seen) == manifest['raw_member_count']
        for name in ['REGISTRATION.json', 'root_macro_audit.py']:
            shutil.copyfile(P / name, root / name)
        receipts = sorted((root / 'runs').glob('*.receipt.json'))
        assert len(receipts) == 152
        for receipt in receipts:
            data = json.loads(receipt.read_text())
            stem = data['world'] + '__' + data['policy']
            for field, suffix in [('raw', '.jsonl'), ('input', '.input.txt'), ('planner', '.planner.jsonl')]:
                assert Path(data[field]).name == stem + suffix
                target = root / 'runs' / (stem + suffix)
                assert sha(target) == data[field + '_sha256']
                data[field] = str(target)
            # Only sandbox-local path metadata changes, after all original bytes
            # and original receipt members have been checked against the archive.
            receipt.write_text(json.dumps(data))
        spec = importlib.util.spec_from_file_location('r12_offline_independent_auditor', root / 'root_macro_audit.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        previous = sys.argv
        try:
            sys.argv = ['root_macro_audit.py']
            module.main()
        finally:
            sys.argv = previous
        replay = json.loads((root / 'ROOT_MACRO_AUDIT.json').read_text())
        assert replay == reference, 'Offline audit differs from the original complete independent audit.'
        print(json.dumps({'passed': True, 'archives': len(manifest['archives']), 'original_members': len(seen),
                          'runs': len(receipts), 'original_artifacts_modified': False,
                          'native_simulator_used': False, 'all_root_audit_results_exactly_reproduced': True}))


if __name__ == '__main__':
    main()
