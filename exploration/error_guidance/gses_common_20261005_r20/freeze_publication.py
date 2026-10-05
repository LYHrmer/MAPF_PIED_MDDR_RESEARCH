#!/usr/bin/env python3
"""Freeze own-file hashes; excludes independently owned root_review."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]


def own_files():
    return sorted(p for p in HERE.rglob('*') if p.is_file()
        and not any(x in ('__pycache__','root_review') for x in p.relative_to(HERE).parts)
        and p.name!='FINAL_MANIFEST.json')


def main():
    target=HERE/'FINAL_MANIFEST.json'
    if target.exists():raise RuntimeError('final manifest is frozen; no overwrite')
    publication=HERE/'PUBLICATION.md'
    publication.write_text('''# Publication receipt

All worker-owned code, protocols, reports, registrations, raw failures, successful inputs/outputs, exact-input caches and lossless CAS evidence are retained. This small preflight does not need a second archive. No external old trajectories, vendored source checkout, virtual environment, ELF or Python bytecode are included.

`FINAL_MANIFEST.json` lists every owned publication file and its SHA256/size. It excludes its own self-hash and excludes the independently produced `root_review/` directory, which root can archive separately after that worker finishes. `PATHS_TO_ADD.txt` explicitly lists repository-relative paths, including this manifest, for review before staging. The repository currently ignores `/exploration/error_guidance/*`, so root will need a scoped forced add or its normal publication allowlist. This worker has not staged, committed or pushed.

The scientific/program records are immutable: do not delete STARTED markers or rerun into their directories. There are ten program invocations, including four adapter input-constructor failures; only six reached Astar. Six common executor episodes comprise five surrogate arms and one zero-search parent control. Three arms exactly reuse a native reply, preserving its reference work metadata. All original files remain readable under their phase directories, and CAS JSON can be decoded with the unchanged R19 EvidenceStore.

The exact source used for all common episodes is `common_engine.py`, hashed by both PHASE2 and PHASE3 registration before execution. `FINAL_AUDIT.json` records zero-new-solver integrity checks of pinned source, eight phase1 inputs, 30 content-addressed objects, six episode receipts, caches and the matched positive witness truth/query payloads. The independently owned root review is not folded into that self-audit claim.
''')
    pathlist=HERE/'PATHS_TO_ADD.txt'
    names={str(p.relative_to(ROOT)) for p in own_files()}
    names.update(str(p.relative_to(ROOT)) for p in (pathlist,target))
    pathlist.write_text('\n'.join(sorted(names))+'\n')
    files={str(p.relative_to(HERE)):dict(sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size) for p in own_files()}
    manifest=dict(frozen_utc=datetime.now(timezone.utc).isoformat(),scope='this worker own files only',
        excluded=['root_review/','__pycache__/','FINAL_MANIFEST.json self hash'],
        files=files,total_bytes=sum(x['bytes'] for x in files.values()),file_count=len(files),
        scientific_calls_after_freeze=0,stage_commit_push_performed=False)
    target.write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
    print(json.dumps(dict(files=len(files),bytes=manifest['total_bytes'],
        manifest_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
        common_engine_sha256=files['common_engine.py']['sha256'])))


if __name__=='__main__':main()
