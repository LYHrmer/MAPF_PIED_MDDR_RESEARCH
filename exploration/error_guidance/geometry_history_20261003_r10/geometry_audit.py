from pathlib import Path
import hashlib,importlib.util,json,sys
H=Path(__file__).resolve().parent;O=Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence')/H.name
SRC=H.parent/'published_continuous_root_review_20261001_r6/verify_physical_clearance_20261001_r6.py';sp=importlib.util.spec_from_file_location('geometry',SRC);g=importlib.util.module_from_spec(sp);sp.loader.exec_module(g)
rs={}
for s in json.loads((H/'runs.json').read_text())['runs']:
 if s['split']!=sys.argv[1]:continue
 r=g.audit(O/'runs'/s['id'],.095036758);assert r['ticks']==s['horizon_ticks'] and r['observations']==s['N']*s['horizon_ticks'];rs[s['id']]=r;print(s['id'],r['all_sampled_circular_envelopes_separated'],flush=True)
(H/('geometry_'+sys.argv[1]+'.json')).write_text(json.dumps({'runs':rs,'all_sampled_separated':all(r['all_sampled_circular_envelopes_separated'] for r in rs.values()),'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest()},indent=2)+'\n');assert all(r['all_sampled_circular_envelopes_separated'] for r in rs.values())
