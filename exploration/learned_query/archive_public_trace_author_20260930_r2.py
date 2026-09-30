"""Publish the exact official-run trace used by R2 without modifying that run."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence/baseline_selection_20260929')
PUBLIC = json.loads((HERE / 'public_trace_20260930_r2/semantic_successor_20260930_r2/public_source_20260930_r2.json').read_text())
TARGET = HERE / 'public_trace_author_archive_20260930_r2'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    assert not TARGET.exists(), 'immutable author archive already exists'
    files = {f'original_run/{name}': BASE / 'pied_run_01' / name
             for name in ['result.json', 'receipt.json', 'stdout.log', 'stderr.log', 'author.log']}
    for relative in PUBLIC['source_input_manifest']:
        if relative.endswith('.txt') or relative.startswith('pied_build/'): continue
        files[f'author_inputs/{relative}'] = BASE / 'PIED-full' / relative
    files['ORIGINAL_R0_REPORT.md'] = BASE / 'PIED_R0_REPORT.md'
    assert digest(files['original_run/result.json'].read_bytes()) == PUBLIC['source_sha256']
    manifest = {}
    for relative, source in files.items():
        data = source.read_bytes()
        if relative.startswith('author_inputs/'):
            expected = PUBLIC['source_input_manifest'][relative.removeprefix('author_inputs/')]
            assert digest(data) == expected['sha256'] and len(data) == expected['bytes']
        destination = TARGET / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open('xb') as f: f.write(data)
        manifest[relative] = {'bytes': len(data), 'sha256': digest(data), 'copied_from': str(source)}
    out = {'status': 'passed', 'kind': 'exact archived original author run, not a new run',
           'author_commit': PUBLIC['source_commit'], 'original_result_sha256': PUBLIC['source_sha256'],
           'source_counts': PUBLIC['source_counts'], 'files': manifest,
           'omitted_upstream_available_inputs': {r: v for r, v in PUBLIC['source_input_manifest'].items()
                                                if r.endswith('.txt') or r.startswith('pied_build/')}}
    with (TARGET / 'manifest.json').open('x') as f: json.dump(out, f, indent=2); f.write('\n')
    print(json.dumps({'status': 'passed', 'files': len(manifest), 'bytes': sum(v['bytes'] for v in manifest.values())}))


if __name__ == '__main__': main()
