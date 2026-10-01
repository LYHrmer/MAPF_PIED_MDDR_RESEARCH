"""Fixed calibration-only snapshots, exact zero-cost prefix, one changed call."""
from pathlib import Path
import hashlib,json,os,subprocess
from public_model import PublicHistory,forecast
HERE=Path(__file__).resolve().parent;OUT=Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence')/HERE.name

def call_at(spec, decisions, index, costs):
 cfg=HERE/'configs'/(spec['id']+'.json')
 env=os.environ.copy();env['LD_LIBRARY_PATH']='/home/lyh/.local/lib:'+env.get('LD_LIBRARY_PATH','')
 p=subprocess.Popen(['rtk','proxy',str(OUT/'bridge_candidate'),str(cfg)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,env=env)
 try:
  for k,d in enumerate(decisions[:index+1]):
   req=dict(d['request']);req['edge_costs']=costs if k==index else [[0.]*1024 for _ in range(8)]
   p.stdin.write(json.dumps(req)+'\n');p.stdin.flush();line=p.stdout.readline();assert line,p.stderr.read()
   result=json.loads(line)
   if k<index:assert result['actions']==d['result']['actions'] and result['p_after']==d['result']['p_after']
  p.stdin.close();p.wait(timeout=5);assert p.returncode==0
  return result
 finally:
  if p.poll() is None:p.kill();p.wait()

def main():
 model=json.loads((HERE/'model_freeze.json').read_text());out=[];zero_checks=0
 for spec in json.loads((HERE/'runs.json').read_text())['runs']:
  if spec['split']!='calibration':continue
  dst=OUT/'runs'/spec['id'];ds=[json.loads(s) for s in (dst/'decisions.jsonl').open()]
  public=[json.loads(s) for s in (dst/'public_events.jsonl').open()]
  layout=json.loads((HERE/'inputs'/spec['input_id']/'map.json').read_text())['layout']
  goals=None;selected=[]
  for k,d in enumerate(ds):
   gs=[g[0]['id'] for g in d['view']['mapf_instance']['goals']]
   if goals!=gs:selected.append(k)
   goals=gs
  selected=selected[:4] # Fixed public head-change occasions, never action-gain selection.
  for k in selected:
   hist=PublicHistory()
   for e in public:
    if e['sequence']<=ds[k]['public_last_sequence']:hist.accept(e)
   z=call_at(spec,ds,k,[[0.]*1024 for _ in range(8)])
   assert z['actions']==ds[k]['result']['actions'] and z['p_after']==ds[k]['result']['p_after'];zero_checks+=1
   row={'run':spec['id'],'decision':k,'tick':ds[k]['snapshot']['tick'],'original_actions':z['actions'],'history_rows':len(hist.rows),'policies':{}}
   for policy in ('history','learned'):
    fc=forecast(hist,ds[k]['view'],layout,policy,model);r=call_at(spec,ds,k,fc['cost_by_agent_destination'])
    row['policies'][policy]={'actions':r['actions'],'changed_agents':sum(x!=y for x,y in zip(z['actions'],r['actions'])),'edge_cost_calls':r['r7_edge_cost_calls'],'nonzero_calls':r['r7_nonzero_edge_cost_calls'],'cost_sum':sum(map(sum,fc['cost_by_agent_destination'])),'forecast_sha256':hashlib.sha256(json.dumps(fc,sort_keys=True).encode()).hexdigest()}
   out.append(row)
  print(spec['id'],'calibration snapshots',len(selected),flush=True)
 result={'scope':'first four public head-change decisions per calibration run; zero-cost replay restores exact official prefix; one altered current call; no fabricated physical continuation','zero_overlay_matches':zero_checks,'snapshots':out}
 (HERE/'calibration_sensitivity.json').write_text(json.dumps(result,indent=2)+'\n')
 print('changed snapshots',{p:sum(r['policies'][p]['changed_agents']>0 for r in out) for p in ('history','learned')})
if __name__=='__main__':main()
