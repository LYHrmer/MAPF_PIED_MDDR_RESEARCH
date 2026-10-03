"""Posthoc raw original-ADG wait decomposition; no future predictor features."""
from pathlib import Path
import json,statistics
from audit import dependencies
H=Path(__file__).resolve().parent;O=Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence')/H.name
out={}
for s in json.loads((H/'runs.json').read_text())['runs']:
 if s['policy']!='hm':continue
 d=O/'runs'/s['id'];es=[json.loads(line) for line in (d/'events.jsonl').open()];dep=dependencies(es,'local');rows=json.loads((d/'supervised_rows.json').read_text())['rows'];values=[]
 for r in rows:
  k=(r['agent'],r['node']);parents=dep['deps'][k];cross=max([r['proposal_tick']]+[dep['ended'][v]['tick'] for v in parents]);admitlag=r['admit_tick']-cross;assert admitlag>=0
  values.append({'group':r['group'],'cross_dependency_wait':cross-r['proposal_tick'],'post_cross_ready_admit_wait':admitlag,'own_prefix_wait':r['begin_tick']-r['admit_tick'],'D':r['duration'],'has_cross_dependency':bool(parents)})
 out[s['id']]={}
 for group in ['M_first','M_second','T','S','all']:
  rr=[r for r in values if group=='all' or r['group']==group]
  if rr:out[s['id']][group]={'n':len(rr),'cross_dependent_nodes':sum(r['has_cross_dependency'] for r in rr),**{key:{'mean':statistics.mean(r[key] for r in rr),'max':max(r[key] for r in rr)} for key in ['cross_dependency_wait','post_cross_ready_admit_wait','own_prefix_wait','D']}}
(H/'dependency_waits.json').write_text(json.dumps({'scope':'same16 hm test traces, reconstructed existing local ADG; diagnostic only, not available as future planner input','runs':out},indent=2)+'\n')
print('dependency waits',len(out))
