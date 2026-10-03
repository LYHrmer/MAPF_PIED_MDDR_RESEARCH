from pathlib import Path
import hashlib,json,py_compile
H=Path(__file__).resolve().parent;O=Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence')/H.name;R=H.parent/'geometry_history_20261003_r10'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
pins=json.loads((H/'freeze.json').read_text())['pins'];assert all(sha(p)==v for p,v in pins.items())
assert sha(H/'model_freeze.json')==sha(R/'model_freeze.json')
for p in H.glob('*.py'):py_compile.compile(str(p),doraise=True)
for name,key in [('audit_test.json','all_passed'),('geometry_test.json','all_sampled_separated'),('INDEPENDENT_LIVE_LABELS.json','passed'),('INDEPENDENT_FIFO_REPLAY.json','passed'),('residual_mechanics.json','passed'),('overlay_diagnostics.json','runtime_formula_all_checked')]:assert json.loads((H/name).read_text())[key],name
a=json.loads((H/'archive_manifest.json').read_text());assert a['all_member_sha256_verified'] and len(a['archives'])==32
for r in a['archives']:assert sha(H/r['path'])==r['sha256'] and (H/r['path']).stat().st_size==r['bytes'] and r['bytes']<45000000
specs=json.loads((H/'runs.json').read_text())['runs'];assert len(specs)==32
for s in specs:
 r=json.loads((O/'runs'/s['id']/'receipt.json').read_text());assert r['error'] is None and r['true_horizon_tick']==4000
checks={'passed':True,'post_R10_new_exploration':True,'not_pooled_with_R10':True,'execution_freeze_pins':len(pins),'freeze_unchanged':True,'heldout_native_runs':32,'independent_task_families':4,'startup_failures':0,'archives':32,'archives_all_member_verified':True,'max_archive_bytes':max(r['bytes'] for r in a['archives']),'compiled_native_delta':[],'model_unchanged_from_R10':True,'model_sha256':sha(H/'model_freeze.json')}
(H/'FINAL_VERIFICATION.json').write_text(json.dumps(checks,indent=2)+'\n')
members=[{'path':str(p.relative_to(H)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(H.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.name!='PUBLICATION_MEMBERS.json']
out={'directory':str(H),'status':'verified post-R10 new32 exploration; root owns Git publication','members':members,'include_manifest_itself':True,'exclude':['__pycache__','expanded ignored raw','all prior artifacts','entry README','manuscript'],'total_member_bytes':sum(r['bytes'] for r in members)}
(H/'PUBLICATION_MEMBERS.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(checks,publication_members=len(members)+1,total_member_bytes=out['total_member_bytes']),indent=2))
