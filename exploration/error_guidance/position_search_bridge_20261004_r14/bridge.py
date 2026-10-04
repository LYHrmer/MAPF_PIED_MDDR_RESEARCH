"""Public estimator and receipt-checked search view. No private future input."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
from fractions import Fraction as F
import copy,hashlib,json,math
HERE=Path(__file__).resolve().parent
R13=HERE.parent/'gses_online_adoption_20261004_r13'
sys.path.insert(0,str(R13))
from executor import Executor,validate_graph
from online import public_input,merge_candidate,guarded_adopt,dag,digest,finish
KINDS={'INITIAL','INITIAL_READY','TURN_START','TURN_END','MOVE_START','CELL_ENTER','CELL_EXIT','ARRIVE','STATION_START','STATION_END','GOAL_COMPLETE'}
DOMAIN='r14_affine_simulated_position_v1'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def canonical(v):
 if isinstance(v,float):
  assert v.is_integer();return int(v)
 if isinstance(v,list):return [canonical(x) for x in v]
 if isinstance(v,dict):return {k:canonical(x) for k,x in v.items()}
 return v

def graph_digest(g):
 g=canonical(copy.deepcopy(g));g['type1']=sorted(g['type1']);g['type2']=sorted(g['type2']);return digest(g)
def public_base(engine):
 base=public_input(engine)
 base['observed_events']=[copy.deepcopy(e) for e in engine.events if e['kind'] in KINDS and F(e['t'])<=engine.t]
 base['schema']='r14_public_base_v1'
 return base

def active_details(base):
 ids,_,_=validate_graph(base['solver_graph']);g=base['solver_graph'];result=[]
 for c in base['active_commitments']:
  a=c['agent'];s=c['from_state'];assert base['arrived_states'][a]==s and c['to_state']==s+1
  starts=[e for e in base['observed_events'] if e['agent']==a and e['kind']=='MOVE_START' and e['from_state']==s and e['to_state']==s+1]
  assert len(starts)==1;start=starts[0];age=F(base['public_at'])-F(start['t']);assert age>=0
  cells={tuple(v) for v in base['physical_cells'][a]};o=tuple(c['origin']);d=tuple(c['destination'])
  if cells=={o}:lo,hi=F(0),F(2,5)
  elif cells=={o,d}:lo,hi=F(2,5),F(3,5)
  elif cells=={d}:lo,hi=F(3,5),F(1)
  else:raise AssertionError('public physical interval')
  landmarks=[]
  for e in base['observed_events']:
   if e['agent']!=a or e['seq']<start['seq']:continue
   if e['kind']=='CELL_ENTER' and tuple(e['cell'])==d:landmarks.append((e,F(2,5)))
   if e['kind']=='CELL_EXIT' and tuple(e['cell'])==o:landmarks.append((e,F(3,5)))
  speed=F(1);landmark=None
  if landmarks:
   landmark,progress=landmarks[-1];elapsed=F(landmark['t'])-F(start['t']);assert elapsed>0;speed=progress/elapsed
  alpha=min(hi,max(lo,min(F(1),max(F(0),age*speed))))
  outgoing=sum(1 for e in g['type2'] if ids[e[0]]==(a,s+1))
  result.append(dict(c,started_at=start['t'],age=str(age),public_lower=str(lo),public_upper=str(hi),public_alpha=str(alpha),landmark=landmark,public_mean_speed=str(speed),unmet_release_count=outgoing))
 return result

def target(base):
 rows=active_details(base)
 return min(rows,key=lambda r:(-r['unmet_release_count'],r['agent'],r['from_state'])) if rows else None

def request_for(base):
 t=target(base)
 if t is None:return None
 return {'domain':DOMAIN,'public_base_sha256':digest(base),'captured_at':base['public_at'],
         'agent':t['agent'],'from_state':t['from_state'],'to_state':t['to_state'],'origin':t['origin'],'destination':t['destination'],
         'move_started_at':t['started_at'],'request_count':1}

def verify_evidence(base,body,receipt,trusted_receipt_sha):
 req=request_for(base);assert req is not None,'no public target'
 assert set(body)=={'domain','source','request','captured_at','delivered_at','position','progress_lower','progress_upper','request_count','production_cost'},'unexpected body capability'
 assert digest(receipt)==trusted_receipt_sha,'unissued receipt'
 assert receipt['body_sha256']==digest(body) and receipt['request_sha256']==digest(req),'unbound measurement body'
 assert receipt['source']=='synthetic_position_measurement' and receipt['production_cost'] is None
 assert body['domain']==DOMAIN and body['request']==req,'measurement domain/agent/occurrence/time mismatch'
 assert body['production_cost'] is None and body['source']=='synthetic_position_measurement' and body['request_count']==1
 assert body['captured_at']==base['public_at'] and body['delivered_at']==base['public_at'],'stale measurement'
 o=list(map(F,req['origin']));d=list(map(F,req['destination']));point=list(map(F,body['position']))
 assert len(point)==2;alpha=sum((v-x)*(y-x) for v,x,y in zip(point,o,d))
 assert F(0)<=alpha<=F(1) and point==[x+alpha*(y-x) for x,y in zip(o,d)],'off-segment position'
 assert F(body['progress_lower'])==alpha==F(body['progress_upper']),'progress/position mismatch'
 t=target(base);assert F(t['public_lower'])<=alpha<=F(t['public_upper']),'public position contradiction'
 return {'agent':req['agent'],'from_state':req['from_state'],'to_state':req['to_state'],'alpha':str(alpha),
         'body_sha256':digest(body),'receipt_sha256':trusted_receipt_sha,'source':'verified_local_simulated_position'}

def residual(age,alpha):
 age,alpha=F(age),F(alpha)
 return age*(1-alpha)/alpha if age>0 and alpha>0 else F(1)

def search_view(base,verified=None):
 g=copy.deepcopy(base['solver_graph']);byedge={(e[0],e[1]):e for e in g['type1']};rows=[]
 if verified is not None:
  t=target(base);assert t and all(verified[k]==t[k] for k in ('agent','from_state','to_state')),'unselected evidence target'
 for r in active_details(base):
  alpha=F(r['public_alpha']);source='public'
  if verified is not None and r['agent']==verified['agent']:
   alpha=F(verified['alpha']);source='verified_position'
  estimate=residual(r['age'],alpha);weight=max(1,math.ceil(estimate));u=g['offsets'][r['agent']]+r['from_state']
  edge=byedge[u,u+1];old=edge[2];edge[2]=weight
  rows.append(dict(r,used_alpha=str(alpha),residual_estimate=str(estimate),search_weight=weight,R13_weight=old,estimate_source=source))
 validate_graph(g);dag(g)
 return {'schema':'r14_search_view_v1','public_base_sha256':digest(base),'evidence_sha256':verified['body_sha256'] if verified else None,
         'solver_graph':g,'estimates':rows}

def verified_view(base,body=None,receipt=None,trusted=None):
 verified=None if body is None else verify_evidence(base,body,receipt,trusted)
 assert (body is None)==(receipt is None)==(trusted is None)
 return search_view(base,verified)

def adopt(snapshot,base,view,candidate,body=None,receipt=None,trusted=None):
 engine=Executor.restore(copy.deepcopy(snapshot));assert public_base(engine)==base,'public base changed'
 assert verified_view(base,body,receipt,trusted)==view,'unbacked search-view mutation'
 # Verify candidate against actual weighted search graph before erasing search-only weights.
 merge_candidate(engine.g,view,candidate)
 original_public=public_input(engine);restored=copy.deepcopy(candidate)
 restored['type1']=copy.deepcopy(original_public['solver_graph']['type1'])
 # The unmodified R13 full-family/ARRIVE/current/active/DAG guard performs actual adoption.
 return guarded_adopt(snapshot,original_public,restored)
