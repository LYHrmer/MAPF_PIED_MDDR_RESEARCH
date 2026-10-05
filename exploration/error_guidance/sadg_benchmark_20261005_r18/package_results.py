#!/usr/bin/env python3
"""Read-only live inventory; explicitly invoked, gated, local evidence packaging.

No engine/policy import, subprocess, solver call, scientific-file write or deletion.
Output is new files under package_results/; all source evidence remains in place.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import gzip
import hashlib
import json
import os
from pathlib import Path
import shutil
import tarfile

ROOT = Path(__file__).resolve().parent
LIMIT = 50 * 1024 * 1024
DATA_NAME = 'r18_initial_paths_publication.tar.gz'
EPHEMERAL = {'__pycache__', '.git', '.pytest_cache', '.mypy_cache', 'package_results'}


def utc(): return datetime.now(timezone.utc).isoformat()
def read(p): return json.loads(Path(p).read_text())
def require(ok, message):
    if not ok: raise RuntimeError(message)


def sha(p):
    h = hashlib.sha256()
    with Path(p).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''): h.update(block)
    return h.hexdigest()


def canonical(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def excluded(p):
    p = Path(p)
    return (any(x in EPHEMERAL for x in p.parts) or p.name.endswith(('.pyc', '.tmp', '.lock', '.swp'))
            or '.tmp.' in p.name or p.name.startswith('.nfs'))


def regular_files(directory):
    if not directory.exists(): return []
    result = []
    for base, dirs, names in os.walk(directory, followlinks=False):
        dirs[:] = sorted(d for d in dirs if not excluded(Path(d)) and not (Path(base)/d).is_symlink())
        for name in sorted(names):
            p = Path(base)/name
            if not excluded(p.relative_to(directory)) and p.is_file():
                require(not p.is_symlink(), 'Refuse symlink evidence: '+str(p))
                result.append(p)
    return result


def completed_directories(root):
    return sorted({p.parent for p in (root/'episodes').glob('*/*/*/RUN_RECEIPT.json')})


def inventory(root):
    """No raw episode, model, cache JSON, or TEST result contents are opened."""
    complete = completed_directories(root)
    complete_set = set(complete)
    pending = sorted(str(p.parent.relative_to(root)) for p in (root/'episodes').glob('*/*/*/STARTED.json')
                     if p.parent not in complete_set)
    groups = Counter(); sizes = Counter(); largest = []
    for folder in complete:
        split, world, _ = folder.relative_to(root/'episodes').parts
        map_name = world.split('__s', 1)[0]
        group = split+'__'+map_name
        groups[group] += 1
        for p in regular_files(folder):
            size = p.stat().st_size; sizes[group] += size
            largest.append((size, str(p.relative_to(root))))
    cache = regular_files(root/'author_cache')
    result = dict(schema='r18-readonly-live-packaging-inventory-v1', observed_utc=utc(),
        root=str(root), completed_episodes=len(complete), completed_by_split_map=dict(groups),
        episode_uncompressed_bytes_by_split_map=dict(sizes), incomplete_started_directories=pending,
        author_cache_files=len(cache), author_cache_uncompressed_bytes=sum(p.stat().st_size for p in cache),
        largest_completed_episode_files=[dict(bytes=n,path=p) for n,p in sorted(largest,reverse=True)[:10]],
        prerequisites_present={name:(root/name).is_file() for name in ['SUMMARY.json','MODEL_FROZEN.json','MODEL_FREEZE_RECEIPT.json']},
        no_evidence_content_read=True, no_files_written=True, packaging_performed=False,
        note='Sizes/counts are a live snapshot, not completion or compressed-size estimates.')
    return result


def gates(root, audit_path):
    reg = read(root/'EXPERIMENT_REGISTRATION.json')
    for name, digest in reg['source_pins'].items():
        require(sha(root/name)==digest, 'Registration source pin differs: '+name)
    require('engine.py' in reg['source_pins'] and 'policies.py' in reg['source_pins'], 'Missing engine/policy pins')
    summary = read(root/'SUMMARY.json')
    require(summary.get('missing')==[], 'SUMMARY.missing is not an empty list')
    rows = summary['rows']
    key = lambda r:(r['case_id'],r['disturbance'],r['arm'])
    expected = {(c['case_id'], d, a) for c in reg['cases'] if c['split'] in reg['evaluation_splits']
                for d in reg['disturbances'] for a in reg['arms']}
    require(len(rows)==len(expected) and {key(r) for r in rows}==expected, 'Summary denominator differs from registration')
    freeze = read(root/'MODEL_FREEZE_RECEIPT.json')
    require(freeze['model_sha256']==sha(root/'MODEL_FROZEN.json'), 'Frozen model hash differs')
    require(freeze['label_sha256']==sha(root/'training/LABELS.json'), 'Frozen training label file differs')
    require(freeze['source_pins']==reg['source_pins'], 'Model source pins differ')
    require(freeze['before_any_calibration_or_test_learned_execution'] is True, 'Missing model isolation receipt')
    require((root/'training/COLLECTION_COMPLETE.json').is_file(), 'Training collection is incomplete')
    collection=read(root/'training/COLLECTION_COMPLETE.json')
    labels=read(root/'training/LABELS.json');omissions=read(root/'training/OMISSIONS.json')
    pairs=read(root/'training/PAIRS.json')
    for name,value in [('labels',labels),('omissions',omissions),('pairs',pairs)]:
        require(collection[name]==len(value) and collection[name+'_sha256']==canonical(value), 'Frozen collection differs: '+name)
    expected_labels={c['case_id']+'__'+d+'__g'+str(g) for c in reg['cases'] if c['split']=='TRAIN'
                     for d in reg['disturbances'] for g in reg['training_probe_gates']}
    accounted=[r.get('pair_id') for r in labels+omissions]
    require(len(expected_labels)==108 and len(accounted)==108 and set(accounted)==expected_labels,
            'Expected 108 unique TRAIN labels or registered omissions')
    require(all(row['split']=='TRAIN' for row in labels), 'Non-TRAIN fit row')
    learning=read(root/'review/LEARNING_AUDIT.json')
    require(learning.get('passed') is True, 'Standalone LEARNING_AUDIT is not PASS')
    # Registration/data already normalize split names; confirm the full original matrix binding.
    data_rows={c['case_id']:c for c in read(root/'data/CASES.json')['cases']}
    normalize={'train':'TRAIN','calibration':'CAL','cal':'CAL','test':'TEST'}
    require(len(data_rows)==len(reg['cases'])==45,'Dataset denominator differs')
    for case in reg['cases']:
        row=data_rows[case['case_id']]
        require(normalize[row['split'].lower()]==case['split'],'Dataset split normalization differs')
        require(sha(root/case['case_path'])==case['case_sha256']==row['plan_sha256'],'Normalized dataset plan hash differs')
    inv = inventory(root)
    require(not inv['incomplete_started_directories'], 'Unfinished STARTED attempt exists; do not silently omit it')
    completed = completed_directories(root); receipts = {}
    for folder in completed:
        receipt = read(folder/'RUN_RECEIPT.json'); spec = receipt['spec']; episode = folder/'episode.json'
        relative = str(episode.relative_to(root))
        require(receipt['spec_sha256']==canonical(spec), 'Receipt specification mismatch: '+relative)
        require(spec['source_pins']==reg['source_pins'], 'Episode source pins mismatch: '+relative)
        require(sha(episode)==receipt['episode_sha256'], 'Episode raw hash mismatch: '+relative)
        require(sha(root/spec['case']['case_path'])==spec['case']['case_sha256'], 'Episode case mismatch: '+relative)
        if spec['arm']=='learned_query':
            require(spec['model_sha256']==freeze['model_sha256'], 'Episode model mismatch: '+relative)
            require(freeze['frozen_utc']<=receipt['started_utc'], 'Learned episode preceded model freeze')
        receipts[relative] = receipt
    for row in rows:
        relative = row.get('episode_path')
        if relative:
            require(relative in receipts and receipts[relative]['episode_sha256']==row['episode_sha256'], 'Summary raw receipt mismatch')
        else: require(row['status'].startswith('initial_planner_'), 'Missing execution without recorded initial planner failure')
    audit = read(audit_path)
    require(audit.get('passed') is True, 'Final audit is not PASS')
    require(set(audit.get('requested_splits',[]))=={'TRAIN','CAL','TEST'}, 'Final audit does not cover all three splits')
    require(audit.get('learning',{}).get('passed') is True, 'Learning audit is not PASS')
    audited = {r['episode']:r for r in audit.get('episodes',[])}
    require(len(audited)==len(audit.get('episodes',[]))==len(receipts), 'Audit receipt count/uniqueness mismatch')
    require(set(audited)==set(receipts), 'Final audit omits or adds completed episodes')
    require(audit.get('completed_receipts_audited')==len(receipts), 'Audit reported count mismatch')
    for relative, receipt in receipts.items():
        row = audited[relative]
        require(row['passed'] is True and row['episode_sha256']==receipt['episode_sha256'], 'Final audit row not current/PASS: '+relative)
        detail = read(root/row['audit'])
        require(detail['passed'] is True and detail['episode_sha256']==receipt['episode_sha256'], 'Detailed audit not current/PASS: '+relative)
        require(detail['auditor_sha256']==sha(root/'review/audit_episode.py'), 'Auditor changed after detailed audit')
    data_receipt = read(root/'data/PUBLICATION_BUNDLE_RECEIPT.json')
    data_archive = root/'data'/DATA_NAME
    require(sha(data_archive)==data_receipt['sha256'], 'Pinned data bundle differs')
    require(data_archive.stat().st_size<=LIMIT, 'Data bundle itself exceeds file limit')
    return reg, completed, dict(passed=True, checked_utc=utc(), final_audit_path=str(audit_path.relative_to(root)),
        final_audit_sha256=sha(audit_path), summary_sha256=sha(root/'SUMMARY.json'),
        model_sha256=freeze['model_sha256'], registration_sha256=sha(root/'EXPERIMENT_REGISTRATION.json'),
        learning_audit_sha256=sha(root/'review/LEARNING_AUDIT.json'),training_labels_or_omissions=len(accounted),
        source_pins=reg['source_pins'], completed_receipts=len(receipts), summary_rows=len(rows), data=data_receipt)


def collect(root, completed):
    groups = defaultdict(list); used = set()
    def add(group, p, name=None):
        require(p.is_file() and not p.is_symlink(), 'Not regular evidence: '+str(p))
        arc = name or 'R18/'+str(p.relative_to(root))
        require(arc not in used, 'Duplicate archive path: '+arc); used.add(arc)
        groups[group].append((p,arc))
    for folder in completed:
        split,world,_ = folder.relative_to(root/'episodes').parts
        name = 'episodes__'+split+'__'+world.split('__s',1)[0]
        for p in regular_files(folder): add(name,p)
    for p in regular_files(root/'author_cache'): add('author_cache',p)
    for p in regular_files(root):
        relative = p.relative_to(root)
        if relative.parts[0] in {'data','episodes','author_cache','package_results'}: continue
        add('artifacts',p)
    # Preserve the exact R16 adapter dependencies without copying the historical experiment tree.
    previous = root.parent/'sadg_preflight_20261004_r16'
    for name in ('isolated_patch/compiler.py','isolated_patch/r16_guard_group.py'):
        add('source_dependencies',previous/name,'dependencies/sadg_preflight_20261004_r16/'+name)
    return {g:sorted(items,key=lambda x:x[1]) for g,items in sorted(groups.items())}


def save(p, obj):
    payload=(json.dumps(obj,indent=2,sort_keys=True,allow_nan=False)+'\n').encode()
    require(len(payload)<=LIMIT, 'Generated manifest exceeds 50 MiB; reduce --raw-chunk-mib')
    with p.open('xb') as out:out.write(payload)


class MemberReader:
    def __init__(self, entry):
        self.entry=entry;self.stream=entry['source'].open('rb');self.stream.seek(entry['offset'])
        self.remaining=entry['length'];self.hasher=hashlib.sha256()
    def read(self, n=-1):
        n=self.remaining if n<0 else min(n,self.remaining)
        data=self.stream.read(n);self.remaining-=len(data);self.hasher.update(data)
        return data
    def close(self):self.stream.close()


def archive_once(target, entries):
    members=[]
    with target.open('xb') as raw,gzip.GzipFile(filename='',mode='wb',fileobj=raw,mtime=0,compresslevel=6) as gz,tarfile.open(fileobj=gz,mode='w|') as archive:
        for entry in sorted(entries,key=lambda e:e['member']):
            info=tarfile.TarInfo(entry['member']);info.size=entry['length'];info.mtime=0
            info.mode=0o755 if entry['source'].stat().st_mode & 0o111 else 0o644
            reader=MemberReader(entry)
            try:archive.addfile(info,reader)
            finally:reader.close()
            require(reader.remaining==0,'Short read while packaging')
            members.append(dict(member=entry['member'],bytes=entry['length'],sha256=reader.hasher.hexdigest(),
                original_path=entry['original'],original_sha256=entry['full_sha256'],
                offset=entry['offset'],original_bytes=entry['full_length'],fragment=entry['fragment']))
    return members


def split_entry(entry):
    require(entry['length']>1,'A one-byte member cannot fit; file limit is invalid')
    half=entry['length']//2
    result=[]
    for offset,length in [(entry['offset'],half),(entry['offset']+half,entry['length']-half)]:
        new=dict(entry,offset=offset,length=length,fragment=True)
        ident=hashlib.sha256(entry['original'].encode()).hexdigest()
        new['member']=f'__fragments__/{ident}/{offset:020d}-{length:020d}.bin';result.append(new)
    return result


def package_group(output, name, entries, raw_limit, result):
    """Bound initial work by raw bytes, then enforce the actual compressed size."""
    batches=[];batch=[];size=0
    for entry in entries:
        if batch and size+entry['length']>raw_limit:batches.append(batch);batch=[];size=0
        batch.append(entry);size+=entry['length']
    if batch:batches.append(batch)
    serial=0
    def emit(batch):
        nonlocal serial
        serial+=1;stem=f'{name}__{serial:05d}'
        staging=output/(stem+'.candidate.tar.gz')
        members=archive_once(staging,batch)
        if staging.stat().st_size>LIMIT:
            # These are disposable newly-created packaging candidates, never source evidence.
            staging.unlink()
            if len(batch)>1:
                middle=len(batch)//2;emit(batch[:middle]);emit(batch[middle:])
            else:
                for fragment in split_entry(batch[0]):emit([fragment])
            return
        final=output/(stem+'.tar.gz');staging.rename(final)
        record=dict(archive=final.name,sha256=sha(final),bytes=final.stat().st_size,members=members)
        manifest=output/(stem+'.members.json');save(manifest,record)
        result.append(dict(archive=final.name,sha256=record['sha256'],bytes=record['bytes'],
            manifest=manifest.name,manifest_sha256=sha(manifest),member_count=len(members)))
    for batch in batches:emit(batch)


def staging_plan(root, output):
    """Explicit paths and measured payload batches; never run Git or stage files."""
    thin=[]
    for folder in [root,root/'training',root/'review']:
        if folder.exists():
            thin.extend(p for p in folder.iterdir() if p.is_file() and
                        p.suffix in {'.py','.md','.json','.csv'} and not excluded(p.name))
    thin.extend(regular_files(root/'figures'))
    thin.extend(p for p in regular_files(root/'parallel') if p.suffix in {'.py','.json'})
    # Human-readable data provenance stays visible; the raw data/source has one archive copy.
    for name in ['README.md','MENTOR_DATA_REVIEW.md','REGISTERED_MATRIX.json','AUTHOR_PIN.json',
                 'CASES.json','prepare_data.py',
                 'SOURCE_DATA_MANIFEST.json','VALIDATION_AUDIT.json','DATA_FREEZE.json',
                 'LOCAL_INPUT_REUSE_AUDIT.json','PUBLICATION_BUNDLE_RECEIPT.json']:
        p=root/'data'/name
        if p.is_file():thin.append(p)
    paths=sorted(set(thin+regular_files(output)))
    records=[]
    for p in paths:
        require(p.stat().st_size<=LIMIT,'Staging candidate exceeds 50 MiB: '+str(p))
        records.append(dict(path=str(p.relative_to(root)),bytes=p.stat().st_size,sha256=sha(p)))
    # One-GiB new payload gives room below the requested two-GiB single-push ceiling.
    # This does not measure existing unpushed Git history or Git's generated pack overhead.
    bound=1024**3;batches=[];batch=[];size=0
    for row in records:
        if batch and size+row['bytes']>bound:
            batches.append(dict(index=len(batches)+1,bytes=size,paths=batch));batch=[];size=0
        batch.append(row['path']);size+=row['bytes']
    if batch:batches.append(dict(index=len(batches)+1,bytes=size,paths=batch))
    save(output/'GIT_STAGING_PLAN.json',dict(schema='r18-explicit-staging-plan-v1',created_utc=utc(),
        path_base=str(root),files=records,total_measured_bytes=sum(r['bytes'] for r in records),
        raw_episode_or_cache_paths_included=False,max_new_payload_bytes_per_batch=bound,batches=batches,
        include_this_plan_separately='package_results/GIT_STAGING_PLAN.json',
        scientific_raw_recovery='Every omitted raw episode/cache/data file is retained in the lossless archives; original workspace files are untouched.',
        use='Review exact paths, stage one listed batch with git add --pathspec-from-file=<NUL list> --pathspec-file-nul from this root, review staged diff, then commit/push each batch before committing the next if a single push would exceed the transport limit.',
        transport_scope='Measured new-file bytes only. Existing unpushed history and Git pack overhead are not included; batching commits without pushing between them does not split a push.',
        staged=False,committed=False,pushed=False))


def pack(root, audit_path, raw_limit):
    reg, completed, acceptance=gates(root,audit_path)
    groups=collect(root,completed)
    snapshot={};entries={};source_figure=[]
    for group,items in groups.items():
        entries[group]=[]
        for p,member in items:
            stat=p.stat();digest=sha(p)
            snapshot[str(p)]=(stat.st_size,stat.st_mtime_ns,digest)
            entry=dict(source=p,member=member,original=member,offset=0,length=stat.st_size,
                full_length=stat.st_size,full_sha256=digest,fragment=False)
            entries[group].append(entry)
            if p.suffix in {'.py','.md','.yaml','.yml','.toml','.cpp','.hpp','.svg','.pdf','.png','.csv'} or 'figures' in p.parts:
                source_figure.append(dict(path=member,bytes=stat.st_size,sha256=digest))
    output=root/'package_results';require(not output.exists(),'Output exists; preserve previous attempt and choose a reviewed new output location in source')
    output.mkdir()
    save(output/'ACCEPTANCE_GATE.json',acceptance)
    save(output/'SOURCE_FIGURE_MANIFEST.json',dict(files=source_figure,source_pins=reg['source_pins']))
    parts=[]
    for group in sorted(entries):package_group(output,group,entries[group],raw_limit,parts)
    # No recompression/duplication of unpacked data: one pinned dependency archive.
    dep=output/DATA_NAME;shutil.copyfile(root/'data'/DATA_NAME,dep)
    require(sha(dep)==acceptance['data']['sha256'],'Data archive copy failed')
    # Detect new receipts, late raw files, or changed sources; never certify a moving snapshot.
    require(completed_directories(root)==completed,'Completed episode set changed during packaging')
    current=collect(root,completed)
    require({str(p) for items in current.values() for p,_ in items}==set(snapshot),'Evidence inventory changed during packaging')
    for path,(size,mtime,digest) in snapshot.items():
        p=Path(path);stat=p.stat()
        require((stat.st_size,stat.st_mtime_ns)==(size,mtime) and sha(p)==digest,'Evidence changed during packaging: '+path)
    # Compare final gate content identities again, excluding the observation timestamp.
    _,_,final_gate=gates(root,audit_path)
    require({k:v for k,v in final_gate.items() if k!='checked_utc'}=={k:v for k,v in acceptance.items() if k!='checked_utc'},'Acceptance evidence changed')
    save(output/'PACKAGE_MANIFEST.json',dict(schema='r18-local-lossless-evidence-parts-v1',completed_utc=utc(),
        max_file_bytes=LIMIT,parts=parts,data_dependency=dict(file=dep.name,sha256=sha(dep),bytes=dep.stat().st_size,
            extraction='Extract separately: existing archive root r18_initial_paths/ is the R18 data/ directory.'),
        source_figure_manifest_sha256=sha(output/'SOURCE_FIGURE_MANIFEST.json'),
        acceptance_sha256=sha(output/'ACCEPTANCE_GATE.json'),source_file_count=len(snapshot),
        reconstruction='Normal members retain paths. Fragmented original files: sort all matching original_path entries by offset, concatenate member bytes, verify original_bytes and original_sha256. Never execute extracted code automatically.',
        adapter_dependency='dependencies/sadg_preflight_20261004_r16/isolated_patch; restore as sibling of R18 or explicitly configure the same pinned paths.',
        author_dependency='Author source/license and exact ECBS binary are already inside the one data archive; no duplicate author checkout.',
        exclusions='__pycache__, bytecode, ephemeral tmp/lock/swap files, unfinished episodes (pack fails if STARTED remains), packaging output itself.',
        source_evidence_deleted=False,uploaded=False))
    # Container round-trip: verify every actual member's bytes against its SHA manifest.
    for part in parts:
        members=read(output/part['manifest'])['members'];expected={m['member']:m for m in members}
        with tarfile.open(output/part['archive'],'r:gz') as archive:
            actual=archive.getmembers();require(len(actual)==len(expected),'Archive member count mismatch')
            for info in actual:
                require(info.isfile() and info.name in expected,'Unexpected/nonregular tar member')
                h=hashlib.sha256();stream=archive.extractfile(info)
                for block in iter(lambda:stream.read(1024*1024),b''):h.update(block)
                require(info.size==expected[info.name]['bytes'] and h.hexdigest()==expected[info.name]['sha256'],'Archive round-trip mismatch')
    require(all(p.stat().st_size<=LIMIT for p in regular_files(output)),'A final output exceeds 50 MiB')
    save(output/'PACKAGE_COMPLETE.json',dict(completed_utc=utc(),passed=True,archive_members_rehashed=True,
        source_snapshot_rehashed=True,package_manifest_sha256=sha(output/'PACKAGE_MANIFEST.json'),
        parts=len(parts),source_evidence_deleted=False,uploaded=False))
    staging_plan(root,output)
    return dict(passed=True,output=str(output),parts=len(parts),max_file_bytes=LIMIT)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode',choices=['inventory','pack'])
    parser.add_argument('--root',type=Path,default=ROOT)
    parser.add_argument('--audit',default='review/COMPLETED_ARTIFACTS_AUDIT.json')
    parser.add_argument('--raw-chunk-mib',type=int,default=128)
    args=parser.parse_args();root=args.root.resolve()
    require(args.raw_chunk_mib>0,'Chunk size must be positive')
    if args.mode=='inventory':result=inventory(root)
    else:
        audit=(root/args.audit).resolve();require(audit.is_relative_to(root),'Audit must belong to this R18 root')
        result=pack(root,audit,args.raw_chunk_mib*1024*1024)
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__=='__main__':main()
