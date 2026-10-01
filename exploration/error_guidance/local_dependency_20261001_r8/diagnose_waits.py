from pathlib import Path
import json,collections,sys
H=Path(__file__).resolve().parent;O=Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence')/H.name

def diagnose(spec):
 nodes={};ended=set();admitted=set();counts=collections.Counter();offsets=[];deps={};batch=[];by_agent=[[] for _ in range(spec['N'])]
 for line in (O/'runs'/spec['id']/'events.jsonl').open():
  e=json.loads(line);kind=e['kind']
  if kind=='parsed':
   offset=[len(by_agent[a]) for a in range(spec['N'])];batch=[]
   for a,rs in enumerate(e['actions']):
    for j,row in enumerate(rs):k=(a,offset[a]+j);nodes[k]=row;deps[k]=[];by_agent[a].append(k);batch.append(k)
   for a,rs in enumerate(e['actions']):
    for b in range(a+1,spec['N']):
     for j,x in enumerate(rs):
      for k,y in enumerate(e['actions'][b]):
       ka=(a,offset[a]+j);kb=(b,offset[b]+k)
       if x['start']==y['goal'] and x['time']<=y['time']:deps[kb].append(ka)
       elif y['start']==x['goal'] and y['time']<=x['time']:deps[ka].append(kb)
  elif kind=='admit':
   for v in e['actions']:admitted.add((int(e['robot']),v[1]))
  elif kind=='end':ended.add((int(e['robot']),e['node']))
  elif kind=='observation':
   o=e['observation'];a=int(e['robot']);pending=[k for k in by_agent[a] if k not in ended]
   if o['queue_size']>0:tag='queue_active'
   elif not o['idle']:tag='physical_settling'
   elif pending:
    k=pending[0]
    if any(dep not in ended for dep in deps[k]):tag='original_ADG_dependency'
    elif spec['execution']=='global' and nodes[k]['time']>=1 and any(x not in ended and nodes[x]['time']<1 for x in batch):tag='extra_global_gate'
    else:tag='dispatch_wait'
   elif any(k not in ended for k in batch):tag='batch_boundary_wait'
   else:tag='all_complete_boundary'
   counts[tag]+=1
 assert sum(counts.values())==spec['N']*spec['horizon_ticks']
 return dict(counts)
if __name__=='__main__':
 results={s['id']:diagnose(s) for s in json.loads((H/'runs.json').read_text())['runs'] if s['split']==sys.argv[1]}
 (H/('wait_accounting_'+sys.argv[1]+'.json')).write_text(json.dumps({'agent_tick_conservation':True,'precedence':'queue active; settling; original dependency; extra global gate; dispatch; batch boundary; all complete','runs':results},indent=2)+'\n');print('diagnosed',len(results))
