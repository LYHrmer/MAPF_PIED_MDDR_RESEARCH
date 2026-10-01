"""Archive all native raw files, with deterministic map/team partition and full verification."""
from collections import defaultdict
from pathlib import Path
import gzip
import hashlib
import json
import tarfile

HERE = Path(__file__).resolve().parent
RAW = Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence') / HERE.name / 'runs'
ARCHIVES = HERE / 'raw_archives'
LIMIT = 95_000_000


def digest(stream):
    value = hashlib.sha256()
    for block in iter(lambda: stream.read(1 << 20), b''):
        value.update(block)
    return value.hexdigest()


def sha(path):
    with path.open('rb') as stream:
        return digest(stream)


def pack(name, files):
    path = ARCHIVES / name
    with path.open('wb') as raw_stream:
        with gzip.GzipFile(filename='', mode='wb', compresslevel=6, fileobj=raw_stream, mtime=0) as compressed:
            with tarfile.open(fileobj=compressed, mode='w|', format=tarfile.PAX_FORMAT) as archive:
                for source in files:
                    member = archive.gettarinfo(str(source), arcname='runs/' + source.relative_to(RAW).as_posix())
                    member.mtime = member.uid = member.gid = 0
                    member.uname = member.gname = ''
                    member.mode = 0o644
                    with source.open('rb') as stream:
                        archive.addfile(member, stream)
    assert path.stat().st_size < LIMIT, f'{path.name} exceeds fixed 95 MB cap; do not publish'
    expected = {'runs/' + p.relative_to(RAW).as_posix(): {'sha256': sha(p), 'bytes': p.stat().st_size} for p in files}
    found = {}
    with tarfile.open(path, mode='r|gz') as archive:
        for member in archive:
            assert member.isfile(), member.name
            stream = archive.extractfile(member)
            found[member.name] = {'sha256': digest(stream), 'bytes': member.size}
    assert found == expected, f'archive round-trip mismatch: {path.name}'
    return {'path': str(path.relative_to(HERE)), 'sha256': sha(path), 'bytes': path.stat().st_size, 'raw_bytes': sum(p.stat().st_size for p in files), 'file_count': len(files), 'round_trip_all_file_hashes_verified': True, 'files': expected}


def main():
    specs = json.loads((HERE / 'runs.json').read_text())['runs']
    groups = defaultdict(list)
    for spec in specs:
        run = RAW / spec['id']
        assert (run / 'receipt.json').is_file(), f'missing retained receipt: {spec["id"]}'
        receipt = json.loads((run / 'receipt.json').read_text())
        for relative, expected in receipt['files'].items():
            assert sha(run / relative) == expected, f'raw file changed since receipt: {spec["id"]}/{relative}'
        groups[(spec['map'], spec['N'])].append(run)
    unexpected = sorted(p.name for p in RAW.iterdir() if p.is_dir() and p.name not in {s['id'] for s in specs})
    assert not unexpected, f'unregistered raw directories: {unexpected}'
    ARCHIVES.mkdir(exist_ok=True)
    archives = []
    for (map_name, team), directories in sorted(groups.items()):
        files = sorted((p for directory in directories for p in directory.rglob('*') if p.is_file()), key=lambda p: p.relative_to(RAW).as_posix())
        record = pack(f'{map_name}_n{team}_all_six_runs.tar.gz', files)
        record.update(map=map_name, N=team, run_ids=sorted(p.name for p in directories))
        archives.append(record)
        print(json.dumps({k: v for k, v in record.items() if k != 'files'}), flush=True)
    manifest = {
        'partition': 'Exactly four predetermined (map,N) groups, each containing both policies and all three error conditions, including every failure and complete raw file.',
        'byte_limit_exclusive': LIMIT,
        'freeze_sha256': sha(HERE / 'freeze.json'),
        'archive_script_sha256': sha(Path(__file__).resolve()),
        'native_build_directories_included': False,
        'archive_count': len(archives),
        'file_count': sum(a['file_count'] for a in archives),
        'compressed_bytes': sum(a['bytes'] for a in archives),
        'raw_bytes': sum(a['raw_bytes'] for a in archives),
        'archives': archives,
    }
    (HERE / 'archive_manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')


if __name__ == '__main__':
    main()
