"""Read-only publication verification; optional deterministic graph-only replay."""
from pathlib import Path
import argparse, gzip, hashlib, json

H = Path(__file__).resolve().parent
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--replay', help='Exact registered run ID; no result files are modified')
    args = parser.parse_args()
    manifest = json.loads((H / 'PUBLICATION_MEMBERS.json').read_text())
    for name, item in manifest['files'].items():
        assert sha(H / name) == item['sha256'], name
        assert (H / name).stat().st_size == item['bytes'], name
    for name in ('FREEZE_01.json', 'MECHANICS_FREEZE.json'):
        for path, expected in json.loads((H / name).read_text())['pins'].items():
            assert sha(path) == expected, path
    results = json.loads((H / 'RESULTS.json').read_text())
    for row in results['runs']:
        packed = H / row['raw']
        assert sha(packed) == row['raw_sha256']
        raw = gzip.decompress(packed.read_bytes())
        assert hashlib.sha256(raw).hexdigest() == row['uncompressed_sha256']
    binding = json.loads((H / 'ROOT_AUDIT_BINDING.json').read_text())
    assert sha(binding['root_audit']['path']) == binding['root_audit']['sha256']
    for path, expected in binding['independent_scripts'].items():
        assert sha(path) == expected
    if args.replay:
        from executor import Executor
        row = next(r for r in results['runs'] if r['spec']['id'] == args.replay)
        reference = json.loads(gzip.decompress((H / row['raw']).read_bytes()))
        output = Executor(reference['graph'], reference['profile']).run()
        assert output == reference, 'graph-only deterministic replay mismatch'
    print(json.dumps({'passed': True, 'publication_files': len(manifest['files']),
                      'raw_traces': len(results['runs']), 'optional_replayed': args.replay}))


if __name__ == '__main__':
    main()
