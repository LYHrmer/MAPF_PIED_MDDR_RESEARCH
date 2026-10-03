from pathlib import Path
import datetime,hashlib,json
H=Path(__file__).resolve().parent;R=H.parent/'gses_fixed_path_20261003_r10'
V=Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence/gses_author_preflight_20261003_r9/vendor/STPG')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
rows=json.loads((R/'RESULTS_attempt01.json').read_text());runs=[];pins={}
for row in rows:
 p=R/row['raw'];assert sha(p)==row['raw_sha256'];pins[str(p)]=sha(p)
 for part in ['original','selected']:runs.append({'id':row['case']+'__'+row['method']+'__'+part+'__author_unit','source':str(p),'part':part,'profile':'author_unit','author_status':row['status'],'case':row['case'],'method':row['method']})
for profile in ['primitive_nominal','axis_slow','midpoint_pause']:
 for method,part in [('GSES','original'),('GSES','selected'),('Improved_GSES','selected')]:
  row=next(r for r in rows if r['case']=='random-32-32-10' and r['method']==method);label='original' if part=='original' else method
  runs.append({'id':'random60__'+label+'__'+profile,'source':str(R/row['raw']),'part':part,'profile':profile,'author_status':row['status'],'case':row['case'],'method':label})
row=next(r for r in rows if r['case']=='lak303d' and r['method']=='GSES');assert row['status']=='Timeout'
for part in ['original','selected']:runs.append({'id':'lak41__timeout_'+part+'__primitive_nominal','source':str(R/row['raw']),'part':part,'profile':'primitive_nominal','author_status':row['status'],'case':row['case'],'method':'original' if part=='original' else 'GSES_timeout'})
bindings=json.loads((R/'SOURCE_BINDINGS_01.json').read_text());assert len(bindings['files'])==43
for name,item in bindings['files'].items():assert sha(V/name)==item['sha256'];pins[str(V/name)]=item['sha256']
for name in ['REGISTERED_CASES.json','RESULTS_attempt01.json','SOURCE_BINDINGS_01.json','INDEPENDENT_REPLAY.json']:pins[str(R/name)]=sha(R/name)
for p in H.glob('*.py'):pins[str(p)]=sha(p)
pins[str(H/'PROTOCOL.md')]=sha(H/'PROTOCOL.md')
assert len(runs)==27 and not (H/'REGISTRATION.json').exists()
reg={'created_UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'16 author trajectory regressions plus11 primitive mechanism runs','author_commit':bindings['author_commit'],'runs':runs}
(H/'REGISTRATION.json').write_text(json.dumps(reg,indent=2)+'\n');pins[str(H/'REGISTRATION.json')]=sha(H/'REGISTRATION.json')
(H/'FREEZE_01.json').write_text(json.dumps({'pins':pins,'author_sources':43,'native_modifications':[],'registration_sha256':sha(H/'REGISTRATION.json')},indent=2)+'\n');print('registered',len(runs),'pins',len(pins))
