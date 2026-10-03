from pathlib import Path
import hashlib,importlib.util,json
H=Path(__file__).resolve().parent;O=Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence')/H.name
SRC=H.parent/'published_continuous_root_review_20261001_r6/verify_physical_clearance_20261001_r6.py';sp=importlib.util.spec_from_file_location('geometry',SRC);g=importlib.util.module_from_spec(sp);sp.loader.exec_module(g)
D=H/'per_run_geometry';D.mkdir(exist_ok=True)
for s in json.loads((H/'runs.json').read_text())['runs']:
 p=D/(s['id']+'.json')
 if p.exists() or not (O/'runs'/s['id']/'receipt.json').exists():continue
 r=g.audit(O/'runs'/s['id'],.095036758);assert r['ticks']==s['horizon_ticks'] and r['observations']==s['N']*s['horizon_ticks'] and r['all_sampled_circular_envelopes_separated'];p.write_text(json.dumps(r,indent=2)+'\n');print(s['id'],'geometry passed',flush=True)
rs={p.stem:json.loads(p.read_text()) for p in D.glob('*.json')};(H/'geometry_test.json').write_text(json.dumps({'runs':rs,'completed':len(rs),'all_sampled_separated':len(rs)==64 and all(r['all_sampled_circular_envelopes_separated'] for r in rs.values()),'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest()},indent=2)+'\n')
