#!/usr/bin/env python3
"""Deterministic scientific-record packaging. Never stage, remove or solve."""
import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import tarfile

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
PREFIX=HERE.relative_to(REPO).as_posix()
MANIFEST=HERE/'PUBLICATION_MANIFEST.json'
PATHSPEC=HERE/'PUBLICATION_PATHSPEC.txt'
GROUPS={
    'sadg_models_inputs_r16.tar.gz':['cases','inputs'],
    'sadg_mapping_r16.tar.gz':['mapping'],
    'sadg_attempt_logs_r16.tar.gz':['cases_attempt01_instrumentation_failure','logs'],
}


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()


def regular_files(directory):
    return sorted(p for p in directory.rglob('*') if p.is_file() and '__pycache__' not in p.parts)


def members_for(roots):
    return sorted(p for name in roots for p in regular_files(HERE/name))


def package():
    archives=[]
    (HERE/'archives').mkdir(exist_ok=True)
    for name,roots in GROUPS.items():
        target=HERE/'archives'/name
        members=members_for(roots)
        # Archiving changes no original member; gzip and tar metadata are frozen.
        with target.open('wb') as raw,gzip.GzipFile(filename='',mode='wb',fileobj=raw,mtime=0,compresslevel=9) as gz,tarfile.open(fileobj=gz,mode='w') as tf:
            for p in members:
                assert not p.is_symlink()
                info=tarfile.TarInfo(p.relative_to(HERE).as_posix())
                info.size=p.stat().st_size;info.mode=0o644;info.mtime=0;info.uid=0;info.gid=0
                with p.open('rb') as f:tf.addfile(info,f)
        archives.append(dict(path=target.relative_to(HERE).as_posix(),sha256=sha(target),bytes=target.stat().st_size,
            members=[dict(path=p.relative_to(HERE).as_posix(),sha256=sha(p),bytes=p.stat().st_size) for p in members]))
    # Top-level scientific documents/scripts remain human-readable, including
    # failure summaries and the immutable pre-package scientific manifest.
    readable=sorted(p for p in HERE.iterdir() if p.is_file() and p.name not in {MANIFEST.name,PATHSPEC.name})
    readable+=regular_files(HERE/'isolated_patch')
    readable+=regular_files(HERE/'suffix')
    published=sorted(set(readable+[HERE/a['path'] for a in archives]+[MANIFEST,PATHSPEC]))
    PATHSPEC.write_text(''.join(p.relative_to(REPO).as_posix()+'\n' for p in published))
    files=[dict(path=p.relative_to(HERE).as_posix(),git_path=p.relative_to(REPO).as_posix(),
                sha256=sha(p),bytes=p.stat().st_size) for p in published if p!=MANIFEST]
    obj=dict(schema='sadg_r16_publication_v1',repository_root=str(REPO),publication_prefix=PREFIX,
        no_stage_commit_push_performed=True,original_files_preserved=True,
        archives=archives,publication_files=files,
        explicit_git_add_paths=[p.relative_to(REPO).as_posix() for p in published],
        self_hash_exclusion='PUBLICATION_MANIFEST.json lists itself as a publication path but cannot hash its own bytes.',
        excluded=['__pycache__/**','*.pyc','compiled executables','venv/**','external R13/R14 raw trajectories','raw generated dirs (preserved locally; archived for publication)'],
        allowed_binary_archives='Only explicitly requested generated-record .tar.gz bundles and original author core source .tar.gz; no executable binaries.')
    MANIFEST.write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')
    verify()


def verify():
    obj=json.loads(MANIFEST.read_text())
    for row in obj['publication_files']:
        p=HERE/row['path'];assert p.stat().st_size==row['bytes'] and sha(p)==row['sha256'],row['path']
    total=0
    for archive in obj['archives']:
        p=HERE/archive['path'];assert sha(p)==archive['sha256']
        expected={r['path']:r for r in archive['members']}
        with tarfile.open(p,'r:gz') as tf:
            actual=tf.getmembers();assert {m.name for m in actual}==set(expected)
            assert len(actual)==len(expected)
            for m in actual:
                assert m.isfile() and not m.issym() and not m.islnk()
                row=expected[m.name];f=tf.extractfile(m);assert f is not None
                data=f.read();assert len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256'],m.name
                total+=1
    print(json.dumps(dict(publication_files_including_manifest=len(obj['explicit_git_add_paths']),
        archive_members_verified=total,original_generated_bytes=sum(r['bytes'] for a in obj['archives'] for r in a['members']),
        compressed_generated_bytes=sum(a['bytes'] for a in obj['archives']),
        verification='PASS',scientific_calls=0,git_mutations=0)))


def extract(destination):
    verify();dest=Path(destination).expanduser().resolve()
    if dest.exists() and any(dest.iterdir()):raise ValueError('Destination must be new or empty; refusing overwrite')
    dest.mkdir(parents=True,exist_ok=True)
    obj=json.loads(MANIFEST.read_text())
    for archive in obj['archives']:
        expected={r['path']:r for r in archive['members']}
        with tarfile.open(HERE/archive['path'],'r:gz') as tf:
            for m in tf:
                rel=PurePosixPath(m.name)
                assert not rel.is_absolute() and '..' not in rel.parts and m.isfile() and m.name in expected
                target=dest/Path(*rel.parts);assert target.is_relative_to(dest) and not target.exists()
                target.parent.mkdir(parents=True,exist_ok=True)
                data=tf.extractfile(m).read()
                assert hashlib.sha256(data).hexdigest()==expected[m.name]['sha256']
                with target.open('xb') as f:f.write(data)
    print(json.dumps(dict(restored_to=str(dest),originals_preserved=True)))


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('action',choices=['package','verify','extract']);ap.add_argument('--destination');a=ap.parse_args()
    if a.action=='package':package()
    elif a.action=='verify':verify()
    else:
        if not a.destination:ap.error('--destination is required')
        extract(a.destination)
