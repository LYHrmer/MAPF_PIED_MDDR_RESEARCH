"""Read committed Git blobs and audit Python syntax; never import project code."""
import argparse
import ast
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess


SCHEMA = 'mapf_shared_git_objects_v1'
SCOPE = 'STATIC_AUDIT_ONLY_NOT_RUNTIME_IMPORT'
FIELDS = {'commit', 'path', 'blob_oid', 'sha256'}
MODULES = {'preexecution_driver', 'preexecution_input', 'preexecution_order',
           'preexecution_schedule', 'preexecution_session', 'interface',
           'timed_constraints', 'composition_constraints', 'composition',
           'timed', 'protocol', 'timed_protocol'}


def _git(repo, *args):
    result = subprocess.run(['git', '--no-replace-objects', '--literal-pathspecs',
                             '-C', str(repo), *args], capture_output=True, check=False)
    if result.returncode:
        raise ValueError('Git object unavailable or invalid: '+result.stderr.decode(errors='replace').strip())
    return result.stdout


def _hex(value, size):
    return isinstance(value, str) and re.fullmatch('[0-9a-f]{%d}' % size, value) is not None


def read_blob(repo, pin):
    """Return bytes only after exact commit, regular-file blob and SHA checks."""
    if not isinstance(pin, dict) or set(pin) != FIELDS:
        raise ValueError('pin requires exactly commit/path/blob_oid/sha256')
    commit, path = pin['commit'], pin['path']
    if not _hex(commit, 40) or not _hex(pin['blob_oid'], 40) or not _hex(pin['sha256'], 64):
        raise ValueError('full lowercase SHA-1 commit/blob and SHA-256 content IDs required; no refs')
    if (not isinstance(path, str) or not path or '\\' in path or ':' in path or '\x00' in path
            or PurePosixPath(path).is_absolute() or '..' in PurePosixPath(path).parts
            or str(PurePosixPath(path)) != path):
        raise ValueError('canonical repository-relative file path required')
    if _git(repo, 'cat-file', '-t', commit).strip() != b'commit':
        raise ValueError('pin must identify a commit object')
    entries = _git(repo, 'ls-tree', '-z', '--full-tree', commit, '--', path).split(b'\0')
    if len(entries) != 2 or entries[1]:
        raise ValueError('path must identify exactly one committed file')
    header, name = entries[0].split(b'\t', 1)
    mode, kind, oid = header.decode().split()
    if name.decode() != path or mode not in ('100644', '100755') or kind != 'blob':
        raise ValueError('regular committed blob required; no directory/symlink')
    if oid != pin['blob_oid']:
        raise ValueError('blob ID mismatch')
    raw = _git(repo, 'cat-file', 'blob', oid)
    if hashlib.sha256(raw).hexdigest() != pin['sha256']:
        raise ValueError('content SHA-256 mismatch')
    return raw


def audit_manifest(repo, manifest):
    """Audit an index's committed modules without importing or executing them."""
    if (not isinstance(manifest, dict) or set(manifest) != {'schema', 'scope', 'modules', 'evidence'}
            or manifest['schema'] != SCHEMA or manifest['scope'] != SCOPE
            or not isinstance(manifest['modules'], dict) or set(manifest['modules']) != MODULES):
        raise ValueError('unexpected shared manifest schema or 12-module closure')
    evidence = manifest['evidence']
    if (not isinstance(evidence, dict) or set(evidence) != {'status', 'entries'}
            or evidence['status'] not in ('PENDING_COMMITTED_DEV_EVIDENCE', 'PINNED')
            or not isinstance(evidence['entries'], dict)
            or (evidence['status'] == 'PINNED') != bool(evidence['entries'])):
        raise ValueError('evidence must be explicitly pending or contain real Git pins')
    result = {'scope': SCOPE, 'modules': {}, 'evidence': {'status': evidence['status'], 'entries': {}}}
    for name, pin in manifest['modules'].items():
        raw = read_blob(repo, pin)
        if Path(pin['path']).name != name+'.py':
            raise ValueError('module name/path mismatch')
        tree = ast.parse(raw, filename=pin['commit']+':'+pin['path'])
        imports = sorted({n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.module}
                         | {a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names})
        result['modules'][name] = {**pin, 'bytes': len(raw), 'ast': 'PASS', 'imports': imports}
    for name, pin in evidence['entries'].items():
        raw = read_blob(repo, pin)
        result['evidence']['entries'][name] = {**pin, 'bytes': len(raw)}
    return result


def resolve(repo, manifest_pin):
    """Resolve a committed manifest and return verified module bytes plus audit."""
    manifest = json.loads(read_blob(repo, manifest_pin))
    audit = audit_manifest(repo, manifest)
    return {'manifest_pin': dict(manifest_pin), 'audit': audit,
            'modules': {name: read_blob(repo, pin) for name, pin in manifest['modules'].items()}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', required=True)
    choice = parser.add_mutually_exclusive_group(required=True)
    choice.add_argument('--candidate-manifest', help='local index preparation only; modules still read from Git')
    choice.add_argument('--manifest-pin', help='JSON containing the committed manifest pin')
    args = parser.parse_args()
    if args.candidate_manifest:
        audit = audit_manifest(args.repo, json.loads(Path(args.candidate_manifest).read_bytes()))
        mode = 'WORKING_INDEX_PREPARATION_ONLY'
    else:
        resolved = resolve(args.repo, json.loads(Path(args.manifest_pin).read_bytes()))
        audit, mode = resolved['audit'], 'PINNED_GIT_OBJECT'
    print(json.dumps({'mode': mode, **audit}, sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
