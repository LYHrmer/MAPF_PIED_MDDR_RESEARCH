"""Inventory explicit source/evidence publication and independently replay archive hashes."""
from pathlib import Path
import hashlib
import json
import tarfile

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
VERSIONS = [BASE / f'published_continuous_execution_20261001_r6{s}' for s in ('', 'b', 'c')]


def digest(stream):
    value = hashlib.sha256()
    for block in iter(lambda: stream.read(1 << 20), b''):
        value.update(block)
    return value.hexdigest()


def record(path):
    with path.open('rb') as stream:
        return {'sha256': digest(stream), 'bytes': path.stat().st_size}


def main():
    archives = []
    for directory in VERSIONS:
        manifest = directory / 'archive_manifest.json'
        if directory.name.endswith('r6b'):
            assert not manifest.exists(), 'R6b has no native runs'
            continue
        data = json.loads(manifest.read_text())
        assert data['archive_count'] == 4
        expected_ids = {row['id'] for row in json.loads((directory / 'runs.json').read_text())['runs']}
        archived_ids = [run for archive in data['archives'] for run in archive['run_ids']]
        assert len(archived_ids) == 24 and set(archived_ids) == expected_ids
        assert data['file_count'] == sum(a['file_count'] for a in data['archives'])
        for archive in data['archives']:
            path = directory / archive['path']
            assert record(path) == {k: archive[k] for k in ('sha256', 'bytes')}
            assert path.stat().st_size < 95_000_000
            actual = {}
            with tarfile.open(path, 'r|gz') as stream:
                for member in stream:
                    assert member.isfile() and member.name not in actual
                    actual[member.name] = {'sha256': digest(stream.extractfile(member)), 'bytes': member.size}
            assert actual == archive['files']
            archives.append({'path': str(path.relative_to(BASE)), 'members': len(actual), **record(path)})
    files = {}
    for directory in VERSIONS + [HERE]:
        for path in sorted(directory.rglob('*')):
            if not path.is_file() or '__pycache__' in path.parts or path.name == 'PUBLICATION_MEMBERS.json':
                continue
            assert path.stat().st_size < 95_000_000, str(path)
            files[str(path.relative_to(BASE))] = record(path)
    output = {'publication_role': 'Complete R6/R6c raw evidence and source; R6b preflight without native run; no native build/cache directories.',
              'directories': [str(p.relative_to(BASE)) for p in VERSIONS + [HERE]],
              'file_count': len(files), 'bytes': sum(r['bytes'] for r in files.values()),
              'verified_archives': archives, 'files': files,
              'reproduction_scope': 'Source and raw evidence plus fixed external author sources, earlier branch artifacts and native toolchain; absolute local paths remain in original frozen receipts.'}
    (HERE / 'PUBLICATION_MEMBERS.json').write_text(json.dumps(output, indent=2) + '\n')
    print(json.dumps({'file_count': len(files), 'bytes': output['bytes'], 'archives': len(archives),
                      'archive_members': sum(a['members'] for a in archives)}), flush=True)


if __name__ == '__main__':
    main()
