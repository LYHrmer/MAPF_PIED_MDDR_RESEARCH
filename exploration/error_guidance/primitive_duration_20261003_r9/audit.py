from pathlib import Path
import json,math,hashlib,statistics,sys
from public_model import PublicHistory,forecast,predict
import mapping_replay as mapping
H=Path(__file__).resolve().parent;O=Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence')/H.name
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dependencies(es,mode):
 nodes={};ended={};admitted={};deps={};offsets=[];edges=0;first_control={};batch_keys=[]
 for e in es:
  if e['kind']=='parsed':
   offsets=[sum(k[0]==a for k in nodes) for a in range(len(e['actions']))];batch_keys=[]
   for a,rows in enumerate(e['actions']):
    for j,row in enumerate(rows):k=(a,offsets[a]+j);nodes[k]=dict(row,proposal_id=e['proposal_id']);deps[k]=[];batch_keys.append(k)
   for a,rows in enumerate(e['actions']):
    for b in range(a+1,len(e['actions'])):
     for j,x in enumerate(rows):
      for k,y in enumerate(e['actions'][b]):
       ka=(a,offsets[a]+j);kb=(b,offsets[b]+k)
       if x['start']==y['goal'] and x['time']<=y['time']:deps[kb].append(ka);edges+=1
       elif y['start']==x['goal'] and y['time']<=x['time']:deps[ka].append(kb);edges+=1
  elif e['kind']=='admit':
   for act in e['actions']:
    k=(int(e['robot']),act[1]);assert k in nodes and k not in admitted
    assert all(dep in ended for dep in deps[k]),('unclosed_original_ADG',k,deps[k])
    if mode=='global' and nodes[k]['time']>=1:
     assert all(v in ended for v in batch_keys if nodes[v]['time']<1),('global_gate',k)
    admitted[k]={'tick':e['tick'],'sequence':e['sequence']}
  elif e['kind']=='end':
   k=(int(e['robot']),e['node']);assert k in admitted and k not in ended;ended[k]={'tick':e['tick'],'sequence':e['sequence']}
  elif e['kind']=='control' and e['control']['phase']=='front':
   k=(int(e['robot']),e['control']['nodes'][0]);first_control.setdefault(k,e['tick'])
 return {'edges':edges,'nodes':nodes,'deps':deps,'admitted':admitted,'ended':ended,'first_control':first_control}
def check(spec):
 d=O/'runs'/spec['id'];r=json.loads((d/'receipt.json').read_text());assert r['error'] is None
 for p,h in r['files'].items():assert sha(d/p)==h,p
 es=[json.loads(s) for s in (d/'events.jsonl').open()];ds=[json.loads(s) for s in (d/'decisions.jsonl').open()];layout=json.loads((H/'inputs'/spec['input_id']/'map.json').read_text())['layout'];env=json.loads((H/'inputs'/spec['input_id']/'environment.json').read_text())
 filtered=[]
 for e in es:
  if e['kind']=='control' and e['control']['phase'] not in ('front','service_decrement','pause'):continue
  filtered.append(dict(e,sequence=len(filtered)))
 m=mapping.check(filtered,ds,spec['condition']=='unknown_pause',True,layout,spec['N'],spec['horizon_ticks']);dep=dependencies(es,spec['execution'])
 assert m['horizon_tick']==spec['horizon_ticks'] and m['observation_count']==spec['N']*spec['horizon_ticks']
 prefixes=[[] for _ in range(spec['N'])];owner_ord={}
 for tid,a,g in m['assigned_task_prefix']:owner_ord[str(tid)]=(a,len(prefixes[a]));prefixes[a].append(g)
 for a,p in enumerate(prefixes):assert p==env['FIFO_goals'][a][:len(p)]
 public=[json.loads(s) for s in (d/'public_events.jsonl').open()];hist=PublicHistory(json.loads((H/'model_freeze.json').read_text())['d0']);idx=0;model=json.loads((H/'model_freeze.json').read_text());nonzero=0
 for decision in ds:
  while idx<len(public) and public[idx]['sequence']<=decision['public_last_sequence']:hist.accept(public[idx]);idx+=1
  assert len(hist.rows)==decision['public_history_rows']
  for call in decision['calls']:
   assert call['public_last_sequence']==decision['public_last_sequence'] and call['completed_rows']==len(hist.rows)
   assert call['result']['objective']==3 and call['result']['network_forward_calls']==0
   nonzero+=call['result'].get('r7_nonzero_edge_cost_calls',0)
   if call['forecast']:
    view={'mapf_instance':call['request']['mapf_instance']};expected=forecast(hist,view,layout,spec['policy'],model);assert expected==call['forecast'] and expected['cost_by_agent_destination']==call['request']['edge_costs']
 while idx<len(public):hist.accept(public[idx]);idx+=1
 labels=json.loads((d/'supervised_rows.json').read_text());assert hist.rows==labels['rows'];assert [v for v in hist.moves.values() if v['duration'] is None]==labels['censored']
 assert len({(x['agent'],x['node']) for x in hist.rows})==len(hist.rows)
 services=[]
 for tid,v in m['completed_tasks'].items():
  a,ordinal=owner_ord[str(tid)];services.append({'agent':a,'ordinal':ordinal,'tick':v['tick'],'task_id':tid})
 restricted=sum(next((s['tick'] for s in services if s['agent']==a and s['ordinal']==k),spec['horizon_ticks']) for a in range(spec['N']) for k in range(10))
 metrics={}
 for step in range(2):
  rows=[r for r in hist.rows if r['logical_step']==step];metrics[str(step)]={}
  for pol in ('history','learned'):
   er=[predict(r['features'],r['group'],pol,model)-r['duration'] for r in rows];metrics[str(step)][pol]={'n':len(er),'MAE':statistics.mean(map(abs,er)) if er else None}
 mechanism=None
 if spec['split']=='mechanical' and spec.get('mechanical_case')!='midpoint':
  mechanism={'leader_first_END':dep['ended'][(0,2)]['tick'],'leader_first_half_END':dep['ended'][(0,1)]['tick'],'dependent_first_final_admit':dep['admitted'][(1,2)]['tick'],'independent_second_start':dep['first_control'][(2,3)],'initial_service_ticks':{str(s['agent']):s['tick'] for s in services if s['ordinal']==0},'first_plan':ds[0]['proposal']['plan']}
  assert mechanism['dependent_first_final_admit']>=mechanism['leader_first_half_END']
  if spec['condition']=='unknown_pause' and spec['execution']=='local':assert mechanism['independent_second_start']<mechanism['leader_first_END']
 return {'passed':True,'spec':spec,'normal_station_END':m['task_services'],'services':services,'fixed_first10_restricted_ticks':restricted,'views':len(ds),'rows':len(hist.rows),'censored':len(labels['censored']),'original_ADG_edges':dep['edges'],'candidate_nonzero_calls':nonzero,'prediction_by_logical_step':metrics,'max_ACK_endpoint_error_m':max(v['endpoint_error_m'] for v in m['ends']),'min_center_distance_m':m['sampled_min_center_distance_m'],'planner_wall':r['planner_wall'],'forecast_wall':r['forecast_wall'],'mechanism':mechanism}
def main(split):
 out={}
 for spec in json.loads((H/'runs.json').read_text())['runs']:
  if spec['split']!=split:continue
  try:r=check(spec)
  except Exception as e:
   import traceback
   r={'passed':False,'error':traceback.format_exc()}
  out[spec['id']]=r;print(spec['id'],r.get('normal_station_END'),r['passed'],r.get('error',''),flush=True)
 (H/f'audit_{split}.json').write_text(json.dumps({'all_passed':all(r['passed'] for r in out.values()),'runs':out},indent=2)+'\n');assert all(r['passed'] for r in out.values())
if __name__=='__main__':main(sys.argv[1])
