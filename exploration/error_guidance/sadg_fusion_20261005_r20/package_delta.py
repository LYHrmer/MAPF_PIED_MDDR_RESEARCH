"""Archive only new R20 evidence; verify each member after round trip."""
from pathlib import Path
import gzip
import hashlib
import json
import tarfile

HERE=Path(__file__).resolve().parent
FOLDERS=('data','episodes','evidence_store','author_cache','r0','review')
CHUNK=12*1024*1024

def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def read(p):return json.loads(Path(p).read_text())
def write(p,x):
    with Path(p).open('x') as f:json.dump(x,f,indent=2,sort_keys=True);f.write('\n')

def main():
    summary=read(HERE/'SUMMARY.json');assert not summary['missing'] and len(summary['rows'])==90
    audit=read(HERE/'INDEPENDENT_AUDIT.json');assert audit['passed'] and audit['completed_receipts_audited']==90
    failures=read(HERE/'solver_failure_review/FAILURE_PAYLOAD_AUDIT.json');assert failures['passed'] and failures['episodes_seen']==90
    receipts=list((HERE/'episodes').glob('*/*/RUN_RECEIPT.json'))
    started=list((HERE/'episodes').glob('*/*/STARTED.json'))
    assert len(receipts)==len(started)==90
    assert {p.parent for p in receipts}=={p.parent for p in started}
    audited={(r['world'],r['arm']):r for r in audit['reports']}
    assert len(audited)==len(audit['reports'])==90
    for p in receipts:
        r=read(p);assert sha(p.parent/'episode.json')==r['episode_sha256']
        a=audited[(r['spec']['world'],r['spec']['arm'])]
        assert a['passed'] and a['episode_sha256']==r['episode_sha256']
    output=HERE/'publication_delta';output.mkdir(exist_ok=True)
    assert not list(output.glob('*.tar.gz')), 'packaging already started; validate existing outputs rather than overwrite'
    entries=[];references=[]
    for folder in FOLDERS:
        for p in sorted((HERE/folder).rglob('*')):
            if '__pycache__' in p.parts or p.name.endswith('.pyc') or '.tmp.' in p.name:continue
            if p.is_symlink():
                references.append(dict(path=str(p.relative_to(HERE)),target=str(p.resolve()),sha256=sha(p)))
                continue
            if not p.is_file():continue
            entries.append(dict(path=str(p.relative_to(HERE)),bytes=p.stat().st_size,sha256=sha(p)))
    entries.sort(key=lambda e:e['path'])
    groups=[];current=[];size=0
    for entry in entries:
        if current and size+entry['bytes']>CHUNK:groups.append(current);current=[];size=0
        current.append(entry);size+=entry['bytes']
    if current:groups.append(current)
    manifest=dict(schema='r20-new-evidence-delta-v1',no_r18_repackaging=True,no_r19_repackaging=True,
        complete_science_episodes=90,initial_failure_rows=0,
        summary_sha256=sha(HERE/'SUMMARY.json'),audit_sha256=sha(HERE/'INDEPENDENT_AUDIT.json'),
        failure_payload_audit_sha256=sha(HERE/'solver_failure_review/FAILURE_PAYLOAD_AUDIT.json'),
        external_references=references,source_file_count=len(entries),source_bytes=sum(e['bytes'] for e in entries),
        files=entries,parts=[],package_script_sha256=sha(__file__))
    for i,group in enumerate(groups,1):
        target=output/f'r20_evidence_{i:03d}.tar.gz'
        with target.open('xb') as raw,gzip.GzipFile(filename='',fileobj=raw,mode='wb',mtime=0,compresslevel=6) as gz,tarfile.open(fileobj=gz,mode='w|') as tar:
            for entry in group:
                p=HERE/entry['path'];info=tarfile.TarInfo('R20/'+entry['path'])
                info.size=entry['bytes'];info.mtime=0;info.mode=0o644
                with p.open('rb') as f:tar.addfile(info,f)
        assert target.stat().st_size<50*1024*1024
        expected={'R20/'+e['path']:e for e in group};seen=set()
        with tarfile.open(target,'r:gz') as tar:
            for member in tar:
                assert member.name in expected and member.name not in seen and member.isfile()
                seen.add(member.name);entry=expected[member.name]
                h=hashlib.sha256();size=0
                with tar.extractfile(member) as f:
                    for b in iter(lambda:f.read(1024*1024),b''):h.update(b);size+=len(b)
                assert size==entry['bytes'] and h.hexdigest()==entry['sha256']
        assert seen==set(expected)
        manifest['parts'].append(dict(path=target.name,bytes=target.stat().st_size,sha256=sha(target),
            member_count=len(group),roundtrip_verified=True))
        print(json.dumps(manifest['parts'][-1]),flush=True)
    manifest.update(passed=True,roundtrip_files=len(entries),compressed_bytes=sum(p['bytes'] for p in manifest['parts']))
    write(output/'MANIFEST.json',manifest)
    print(json.dumps({k:manifest[k] for k in ('passed','roundtrip_files','source_bytes','compressed_bytes')}))

if __name__=='__main__':main()
