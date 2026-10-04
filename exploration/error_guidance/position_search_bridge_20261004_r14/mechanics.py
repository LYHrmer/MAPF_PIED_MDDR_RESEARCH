"""Small registered mechanical controls; no optimizer or full physical continuation."""
import copy,json,math
from fractions import Fraction as F
from pipeline import registration,readpacked,load,write,HERE,R13,sha
from bridge import *
from measurement import issue
from executor import adoption_guard

def run():
 reg=registration();records=[]
 def reject(name,fn):
  try:fn()
  except (AssertionError,KeyError,ValueError,IndexError,TypeError) as e:records.append({'name':name,'rejected':True,'reason':str(e)});return
  raise AssertionError('accepted '+name)
 assert residual(F(1,4),F(1,6))==F(5,4) and max(1,math.ceil(residual(F(1,4),F(1,4))))==1
 records.append({'name':'exact_residual_and_ceil_boundary','passed':True})
 chosen=None
 for spec in reg['runs']:
  cp=R13/'raw'/(spec['id']+'__checkpoint.json.gz');snap=readpacked(cp);e=Executor.restore(snap);b=public_base(e)
  if target(b):chosen=(spec,cp,snap,e,b);break
 assert chosen;spec,cp,snap,e,b=chosen
 req=request_for(b);body,receipt=issue(snap,sha(cp),req);trusted=digest(receipt)
 verified=verify_evidence(b,body,receipt,trusted);view=search_view(b,verified)
 unchanged,guard=adopt(snap,b,view,copy.deepcopy(view['solver_graph']),body,receipt,trusted)
 assert unchanged.g==e.g and unchanged.heap==e.heap and unchanged.ag==e.ag
 records.append({'name':'search_only_weights_restore_full_execution_type1_current_and_commitments','passed':True})
 bad=copy.deepcopy(body);bad['position'][0]=str(F(bad['position'][0])+1)
 reject('body_tamper_receipt_binding',lambda:verify_evidence(b,bad,receipt,trusted))
 def issued_bad(field,value):
  bad=copy.deepcopy(body)
  if field in ('agent','from_state','to_state'):bad['request'][field]=value
  else:bad[field]=value
  r=copy.deepcopy(receipt);r['body_sha256']=digest(bad)
  return bad,r,digest(r)
 for field,value in [('agent',req['agent']+1),('from_state',req['from_state']+1),('captured_at',str(F(b['public_at'])+1)),('domain','main_real_POSITION'),('current_arrived',req['to_state'])]:
  bad,r,h=issued_bad(field,value)
  reject('malformed_issued_'+field,lambda bad=bad,r=r,h=h:verify_evidence(b,bad,r,h))
 bad=copy.deepcopy(view);bad['solver_graph']['type1'][0][2]+=1
 reject('unbacked_search_weight',lambda:adopt(snap,b,bad,view['solver_graph'],body,receipt,trusted))
 bad=copy.deepcopy(b);bad['arrived_states'][req['agent']]+=1
 reject('POSITION_cannot_promote_actual_ARRIVE',lambda:adopt(snap,bad,view,view['solver_graph'],body,receipt,trusted))
 found=False
 for spec2 in reg['runs']:
  snap2=readpacked(R13/'raw'/(spec2['id']+'__checkpoint.json.gz'));eng=Executor.restore(snap2)
  for a,r in enumerate(eng.ag):
   if 'active' not in r:continue
   dest=eng.g['offsets'][a]+r['state']+1
   edges=[v for v in eng.g['type2'] if v[1]==dest]
   if not edges:continue
   old=edges[0];new=copy.deepcopy(eng.g);new['type2'].remove(old);new['type2'].append([old[1]+1,old[0]-1,old[2]])
   reject('actual_active_incoming_orientation',lambda:adoption_guard(eng.g,new,[(a,r['state'])]));found=True;break
  if found:break
 assert found,'registered contexts lack active incoming test'
 altered=Executor.restore(copy.deepcopy(snap));altered.profile='unseen_private_future_profile'
 altered.heap=[(t+100,ticket,a,k,kw) for t,ticket,a,k,kw in altered.heap]
 for seg in altered.segments:
  if F(seg['t0'])>altered.t:seg['p1']=['999','999']
 assert public_base(altered)==b
 body2,_=issue(altered.snapshot(),sha(cp),req);assert body2==body
 assert search_view(b,verify_evidence(b,body,receipt,trusted))==view
 records.append({'name':'private_profile_heap_and_strict_future_segments_do_not_change_public_or_current_measurement','passed':True})
 g=copy.deepcopy(view['solver_graph']);g['type1']=[list(v[:2])+[float(v[2])] for v in g['type1']]
 assert graph_digest(g)==graph_digest(view['solver_graph'])
 records.append({'name':'integral_json_graph_key_normalization','passed':True})
 result={'passed':True,'checks':records,'negative_count':sum(r.get('rejected',False) for r in records),'positive_count':sum(r.get('passed',False) for r in records),
         'scope':'mechanical controls using existing checkpoint; no solver or complete execution calls','registration_sha256':sha(HERE/'REGISTRATION.json'),'source_sha256':sha(__file__)}
 write(HERE/'MECHANICS.json',result);print(json.dumps(result))
if __name__=='__main__':run()
