from pathlib import Path
from fractions import Fraction as F
import copy,gzip,hashlib,json
from executor import Executor,adoption_guard
from checkpoint_guard import guarded_restore
from audit_events import audit
H=Path(__file__).resolve().parent;O=Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence')/H.name
sha=lambda data:hashlib.sha256(data).hexdigest()
def trace(name):
 r=next(r for p in H.glob('RESULTS_attempt*.json') for r in json.loads(p.read_text()) if r['spec']['id']==name)
 return json.loads(gzip.decompress((H/r['raw']).read_bytes()))
base=trace('random60__Improved_GSES__midpoint_pause');engine=Executor(base['graph'],'midpoint_pause')
while not any(e['kind']=='HALF_END' for e in engine.events[-200:]):assert engine.step()
# Select the first timestamp containing a half-end, never a benefit-selected state.
snapshot=json.loads(json.dumps(engine.snapshot()));resumed,guard=guarded_restore(snapshot,base['graph']);result=resumed.run();assert result==base,'midpoint resume diverged'
snapshot_bytes=(json.dumps(snapshot,separators=(',',':'))+'\n').encode();folder=O/'mechanics';folder.mkdir(exist_ok=True);(folder/'checkpoint.json').write_bytes(snapshot_bytes)
packed=H/'mechanical_checkpoint.json.gz'
with packed.open('wb') as f:
 with gzip.GzipFile(filename='',mode='wb',fileobj=f,mtime=0) as z:z.write(snapshot_bytes)
negative=[]
def reject(name,fn):
 try:fn()
 except (AssertionError,KeyError) as e:negative.append({'name':name,'rejected':True,'reason':str(e)})
 else:raise AssertionError('negative accepted '+name)
def badtrace(name):
 d=copy.deepcopy(base)
 if name=='midpoint_state':next(e for e in d['events'] if e['kind']=='HALF_END')['state']+=1
 elif name=='premature_source_exit':
  e=next(e for e in d['events'] if e['kind']=='CELL_EXIT');e['t']=str(F(e['t'])-F(1,10));d['events'].sort(key=lambda x:(F(x['t']),x['seq']))
  for seq,e in enumerate(d['events']):e['seq']=seq
 elif name=='release_during_station':
  i=next(i for i,e in enumerate(d['events']) if e['kind']=='STATION_START');e=d['events'][i];d['events'].insert(i+1,dict(e,kind='RELEASE_SOURCE'))
  for seq,e in enumerate(d['events']):e['seq']=seq
 elif name=='missing_type2_binding':next(e for e in d['events'] if e['kind']=='MOVE_START' and e['dependencies'])['dependencies']=[]
 elif name=='half_geometry_corrupt':next(s for s in d['segments'] if s['kind']=='MOVE_HALF1')['p1'][0]='999'
 elif name=='lost_goal_residence':
  i=next(i for i,s in enumerate(d['segments']) if s['kind']=='GOAL_HOLD');del d['segments'][i]
 return audit(d)
for name in ['midpoint_state','premature_source_exit','release_during_station','missing_type2_binding','half_geometry_corrupt','lost_goal_residence']:reject(name,lambda name=name:badtrace(name))
def corrupt_prefix():
 g=copy.deepcopy(base['graph']);a=guard['active_move_identities'][0][0];g['paths'][a][g['current'][a]][0][0]+=1;guarded_restore(snapshot,g)
reject('changed_active_path_prefix',corrupt_prefix)
# Use a genuine original-vs-adopted dependency reversal as a commitment conflict.
orig=trace('random60__original__primitive_nominal')['graph'];selected=trace('random60__Improved_GSES__primitive_nominal')['graph'];changed=next(e for e in orig['type2'] if e not in selected['type2']);target=changed[1]
a=next(a for a,offset in enumerate(orig['offsets']) if offset<=target<offset+len(orig['paths'][a]));s=target-orig['offsets'][a]-1
reject('author_adoption_changes_committed_dependency',lambda:adoption_guard(orig,selected,[(a,s)]))
adoption_guard(orig,selected,[])
def wrong_timeout():
 old=trace('lak41__timeout_original__primitive_nominal');wrong=copy.deepcopy(trace('lak41__timeout_selected__primitive_nominal'));wrong['events'][5]['kind']='FAKE';assert old==wrong,'timeout fallback not original'
reject('fake_timeout_adoption',wrong_timeout)
positive={'snapshot_at':str(engine.t),'snapshot_active_moves':guard['active_move_identities'],'protected_transitions':guard['protected_transitions'],'checkpoint_sha256':sha(snapshot_bytes),'checkpoint_raw':packed.name,'checkpoint_raw_sha256':sha(packed.read_bytes()),'serialized_roundtrip_exact':True,'full_resumed_trace_exact':True,'resume_profile':'midpoint_pause','actual_author_adoption_without_committed_moves_valid':True,'commitment_conflict_uses_genuine_author_reversal':changed,'one_conflicting_protected_transition':[a,s]}
out={'passed':True,'positive':positive,'negative_controls':negative,'negative_count':len(negative),'scope':'finite prefix guard and exact same-graph live midpoint resume; not a general online replanning service'}
(H/'MECHANICS.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
