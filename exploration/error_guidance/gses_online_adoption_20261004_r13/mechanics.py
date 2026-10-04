"""Post-matrix registered corruptions of existing artifacts, no new solver cases."""
from pathlib import Path
from fractions import Fraction as F
import copy,gzip,hashlib,json,time
from executor import Executor,adoption_guard
from online import public_input,guarded_adopt,continue_candidate,finish,dag
HERE=Path(__file__).resolve().parent
def load(p):return json.loads(p.read_text())
def archive(p):return json.loads(gzip.decompress(p.read_bytes()))
def write(p,x):p.write_text(json.dumps(x,indent=2,default=str)+'\n')
def main():
 assert (HERE/'COMPLETE.json').exists()
 write(HERE/'MECHANICS_FREEZE.json',{'before_ns':time.time_ns(),'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'new_solver_calls':0})
 rows=load(HERE/'RESULTS.json');row=next(r for r in rows if r['changed'])
 spec=row['spec'];stem=spec['id'];snapshot=archive(HERE/'raw'/(stem+'__checkpoint.json.gz'))
 public=load(HERE/'public'/(stem+'.json'));reply=load(HERE/'calls'/(row['id'])/'author_reply.json')
 base=archive(HERE/'raw'/(stem+'__original.json.gz'));old=base['graph'];negative=[]
 def reject(name,fn):
  try:fn()
  except (AssertionError,KeyError,IndexError,TypeError,ValueError) as exc:negative.append({'name':name,'rejected':True,'reason':str(exc)})
  else:raise AssertionError('negative accepted: '+name)
 # Identical suffix is lifted to the same full graph and reproduces the old continuation.
 engine,same_guard=guarded_adopt(snapshot,public,public['solver_graph']);same=finish(engine,old,same_guard)
 assert same['events']==base['events'] and same['segments']==base['segments'] and same['completion_times']==base['completion_times']
 stale=copy.deepcopy(public);stale['public_at']='999'
 reject('stale_public_checkpoint',lambda:guarded_adopt(snapshot,stale,reply['selected_graph']))
 for kind in ['path','type1','current','non_author_edge','cycle']:
  candidate=copy.deepcopy(reply['selected_graph'])
  if kind=='path':
   for path in candidate['paths']:
    for v in path:v[0][0]+=1000
  elif kind=='type1':candidate['type1'][0][2]+=1
  elif kind=='current':candidate['current'][0]+=1
  elif kind=='non_author_edge':candidate['type2'].pop()
  elif kind=='cycle':
   u,v,w=candidate['type1'][0];candidate['type1'].append([v,u,w])
   reject('explicit_cycle_DAG_guard',lambda:dag(candidate));continue
  reject('candidate_changed_'+kind,lambda:guarded_adopt(snapshot,public,candidate))
 adopted=archive(HERE/row['raw']);edge=next(e for e in old['type2'] if e not in adopted['final_graph']['type2'])
 ids=[(a,s) for a,p in enumerate(old['paths']) for s in range(len(p))];a,s=ids[edge[1]]
 reject('genuine_author_reversal_if_target_transition_committed',lambda:adoption_guard(old,adopted['final_graph'],[(a,s-1)]))
 # Fault-injected transport statuses, not a claim of a naturally observed author timeout.
 fallbacks=[]
 for status in ['Timeout','HostTimeout','AuthorError']:
  trace,meta=continue_candidate(snapshot,public,reply,status)
  assert trace['events']==base['events'] and trace['segments']==base['segments'] and trace['completion_times']==base['completion_times']
  assert meta['guard'] is None and meta['status']==status
  fallbacks.append({'status':status,'exact_original_continuation':True,'injection':True})
 bad=copy.deepcopy(reply);bad['selected_graph']['type1'][0][2]+=1
 rejected,meta=continue_candidate(snapshot,public,bad,'Succ')
 assert meta['status']=='Rejected' and rejected['events']==base['events'] and rejected['segments']==base['segments']
 private=Executor.restore(copy.deepcopy(snapshot));view=public_input(private)
 # Future scheduling truth is deliberately corrupted without altering current public state.
 private.heap=[(t+1234,ticket,a,kind,kw) for t,ticket,a,kind,kw in private.heap]
 for seg in private.segments:
  if F(seg['t1'])>private.t:seg['t1']='123456'
 private.profile='arbitrary_private_future_law'
 assert public_input(private)==view==public
 out={'passed':True,'source_context':stem,'negative_controls':negative,'negative_count':len(negative),
      'same_graph_resume_exact':True,'rejected_candidate_fallback_exact':True,'injected_fallbacks':fallbacks,
      'private_heap_segments_profile_not_in_solver_input':True,'new_solver_calls':0,
      'commitment_control_scope':'real author reversal tested against an explicitly protected target; not a new physical scenario',
      'timeout_scope':'fault-injected transport statuses; natural timeout counts reported separately'}
 write(HERE/'MECHANICS.json',out);print(json.dumps(out,indent=2))
if __name__=='__main__':main()
