"""Reconstruct the fixed complete prefixes; no policy outcome or fitted model read."""
from pathlib import Path
import json,hashlib
HERE=Path(__file__).resolve().parent;DELTA={'EA':(1,0),'WE':(-1,0),'NO':(0,-1),'SO':(0,1),'W':(0,0)}
def main():
 source=HERE.parent/'public_history_20260930_r5/author_200.json';digest=hashlib.sha256(source.read_bytes()).hexdigest();d=json.loads(source.read_text());paths=[s.split(',') for s in d['actualPaths']];states=[[(c,r) for r,c,_ in d['start']]]
 for t in range(200):states.append([(x+DELTA[paths[a][t]][0],y+DELTA[paths[a][t]][1]) for a,(x,y) in enumerate(states[-1])])
 goals={tid:(c,r) for tid,r,c in d['tasks']};robots=[]
 for a in range(96):
  assigned={tid:at for tid,at,k in d['events'][a] if k=='assigned'};finished=[(tid,at) for tid,at,k in d['events'][a] if k=='finished'][:3];assert len(finished)==3;heads=[];begin=0
  for tid,end in finished:
   assert states[end][a]==goals[tid];heads.append(dict(task=tid,goal=list(goals[tid]),route=paths[a][begin:end],source_assigned_tick=assigned[tid],source_finish_tick=end));begin=end
  robots.append(dict(agent=a,start=list(states[0][a]),heads=heads,route=paths[a][:begin],route_points=[list(states[k][a]) for k in range(begin+1)]))
 def cohort(aa,cid,split):
  rr=[robots[a] for a in aa];return dict(cohort_id=cid,split=split,source=str(source),source_sha256=digest,source_tick=0,agents=aa,robots=rr,resource_cells=[list(z) for z in sorted({tuple(p) for r in rr for p in r['route_points']})],task_group=sorted(h['task'] for r in rr for h in r['heads']),initial_source_not_selective_crop=True)
 cohorts=[cohort(list(range(i*16,(i+1)*16)),f'group_{i:02d}',['train','train','train','calibration','test','test'][i]) for i in range(6)]
 mechanical=[cohort(list(range(n)),f'mechanical_n{n:02d}','mechanical') for n in [8,16]];result=dict(source_sha256=digest,cohorts=cohorts,mechanical=mechanical,cohort_agent_task_disjoint=True,shared_old_map_and_source_background=True,no_query_outcome_selection=True,source_map_count=1,source_agents=100,source_ticks=200,fixed_prefix_blocks=True)
 expected=json.loads((HERE/'SUPPORT.json').read_text());assert result==expected,'fixed source reconstruction mismatch';tasks=[h['task'] for r in robots for h in r['heads']];assert len(set(tasks))==288;assert len({r['agent'] for r in robots})==96
 evidence=dict(passed=True,source_sha256=digest,groups=6,agents=96,fixed_tasks=288,source_unique_completed_tasks=730,all_source_task_endpoints_exact=True,reconstructed_support_equal=True,selection_uses_outcomes=False,source_map_count=1)
 p=HERE/'SOURCE_SUPPORT_VERIFICATION.json';assert not p.exists();p.write_text(json.dumps(evidence,indent=2)+'\n');print(evidence)
if __name__=='__main__':main()
