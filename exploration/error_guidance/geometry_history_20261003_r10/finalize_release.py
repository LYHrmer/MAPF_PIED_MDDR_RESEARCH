from pathlib import Path
import hashlib,json,py_compile
H=Path(__file__).resolve().parent;O=Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence')/H.name
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
pins=json.loads((H/'freeze.json').read_text())['pins'];assert all(sha(p)==v for p,v in pins.items())
for p in H.glob('*.py'):py_compile.compile(str(p),doraise=True)
for name,key in [('audit_test.json','all_passed'),('geometry_test.json','all_sampled_separated'),('INDEPENDENT_REFIT.json','passed'),('INDEPENDENT_LIVE_LABELS.json','passed'),('INDEPENDENT_FIFO_REPLAY.json','passed'),('negative_checks.json','passed'),('DATA_ISOLATION.json','passed'),('counterfactual_decisions.json','passed')]:assert json.loads((H/name).read_text())[key],name
a=json.loads((H/'archive_manifest.json').read_text());assert a['all_member_sha256_verified'] and len(a['archives'])==68
for r in a['archives']:assert sha(H/r['path'])==r['sha256'] and (H/r['path']).stat().st_size==r['bytes'] and r['bytes']<45000000
specs=json.loads((H/'runs.json').read_text())['runs'];assert len(specs)==64
for s in specs:
 r=json.loads((O/'runs'/s['id']/'receipt.json').read_text());assert r['error'] is None and r['true_horizon_tick']==4000
failed=list((O/'sandbox_attempt01').glob('*/receipt.json'));assert len(failed)==4
for p in failed:
 r=json.loads(p.read_text());assert 'PermissionError' in r['error'] and r['decisions']==0
checks={'passed':True,'execution_freeze_pins':len(pins),'freeze_unchanged':True,'heldout_native_runs':64,'independent_task_families':8,'retained_socket_failures':4,'archives':68,'archives_all_member_verified':True,'max_archive_bytes':max(r['bytes'] for r in a['archives']),'compiled_native_delta':[],'model_sha256':sha(H/'model_freeze.json')}
(H/'FINAL_VERIFICATION.json').write_text(json.dumps(checks,indent=2)+'\n')
members=[{'path':str(p.relative_to(H)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(H.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.name!='PUBLICATION_MEMBERS.json']
outside=[]
for name in ['MENTOR_PREEXEC_20261003_R10.md','MENTOR_POSTUPDATE_20261003_R10.md']:
 p=H.parent/name
 if p.exists():outside.append({'path':str(p.relative_to(H.parent.parent.parent)),'bytes':p.stat().st_size,'sha256':sha(p)})
out={'directory':str(H),'status':'verified R10 isolated exploration; root owns Git publication','members':members,'include_manifest_itself':True,'outside_directory_members':outside,'exclude':['__pycache__','expanded ignored raw','parent R8/R7/R9 files','entry README','manuscript'],'total_member_bytes':sum(r['bytes'] for r in members)}
(H/'PUBLICATION_MEMBERS.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(checks,publication_members=len(members)+1,total_member_bytes=out['total_member_bytes']),indent=2))
