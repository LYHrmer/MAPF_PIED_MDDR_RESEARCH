from collections import deque,Counter
import hashlib,itertools,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
D={"EA":(1,0),"WE":(-1,0),"NO":(0,-1),"SO":(0,1),"W":(0,0)}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,o):
 with p.open("x") as f:json.dump(o,f,indent=2);f.write("\n")
def main():
 source=HERE/"author_200.json";d=json.loads(source.read_text());paths=[s.split(",") for s in d["actualPaths"]];states=[[(c,r) for r,c,_ in d["start"]]]
 for t in range(len(paths[0])):states.append([(x+D[paths[a][t]][0],y+D[paths[a][t]][1]) for a,(x,y) in enumerate(states[-1])])
 goals={tid:(c,r) for tid,r,c in d["tasks"]};old=json.loads((HERE.parent/"public_value_20260930_r4/SUPPORT_AUDIT_60.json").read_text());excluded={14,22,99,118}|{x for c in old["cohorts"] for x in c["task_group"]}
 groups={};seen_counts=Counter()
 for t in range(len(paths[0])):
  rows={}
  for a,ev in enumerate(d["events"]):
   q=deque();assigned={}
   for tid,at,k in ev:
    if at>t:break
    if k=="assigned":q.append(tid);assigned[tid]=at
    else:assert q.popleft()==tid
   if not q:continue
   tid=q[0];finished=[(i,at) for i,at,k in ev if k=="finished" and at>t]
   if len(finished)<2 or finished[0][0]!=tid:continue
   second,end=finished[1];first=finished[0][1]
   if first-t>20 or end-t>44 or first==t or goals[second]==goals[tid] or goals[tid]==states[t][a] or paths[a][t]=="W" or {tid,second}&excluded:continue
   rows[a]=dict(agent=a,start=list(states[t][a]),heads=[dict(task=tid,goal=list(goals[tid]),route=paths[a][t:first],source_assigned_tick=assigned[tid],source_finish_tick=first),dict(task=second,goal=list(goals[second]),route=paths[a][first:end],source_assigned_tick=next(at for i,at,k in ev if i==second and k=="assigned"),source_finish_tick=end)],route=paths[a][t:end],route_points=[list(states[k][a]) for k in range(t,end+1)],source_revealed_queue=list(q))
  pairs=[(a,b) for b in rows for a in rows if a!=b and states[t+1][b]==states[t][a] and states[t+1][a]!=states[t][b]]
  for u,v in itertools.combinations(pairs,2):
   aa=sorted(set(u+v))
   if len(aa)!=4:continue
   if any(states[t+1][a] in [states[t][b] for b in aa if b!=a] for a in [u[0],v[0]]):continue
   sets={a:set(map(tuple,rows[a]["route_points"])) for a in aa};seen={aa[0]}
   for _ in aa:seen|={b for b in aa if any(sets[b]&sets[a] for a in seen)}
   if len(seen)!=4:continue
   # Fixed public geometric evidence of later conflict: at least one later
   # source follow relationship among the four after 2 original moves/ticks.
   later=[]
   for at in range(t+2,min(r["heads"][-1]["source_finish_tick"] for r in [rows[a] for a in aa])):
    pp=[(a,b) for b in aa for a in aa if a!=b and states[at+1][b]==states[at][a] and states[at+1][a]!=states[at][b]]
    if pp:later.append(dict(source_tick=at,pairs=[list(x) for x in pp]))
   if not later:continue
   tt=tuple(sorted(h["task"] for a in aa for h in rows[a]["heads"]));groups.setdefault(tt,dict(source_tick=t,agents=aa,initial_follow_pairs=[list(u),list(v)],robots=[rows[a] for a in aa],resource_cells=[list(x) for x in sorted(set().union(*[sets[a] for a in aa]))],source=str(source),source_sha256=sha(source),task_group=list(tt),public_later_follow_relationships=later))
 selected=[];used=set()
 for k,c in groups.items():
  if set(k)&used:continue
  c["cohort_id"]=f"cohort_{len(selected):02d}";c["split"]=["train","train","train","calibration","test"][len(selected)%5];selected.append(c);used.update(k)
  if len(selected)==10:break
 result=dict(source_sha256=sha(source),source_actions=len(paths)*len(paths[0]),source_tasks=d["numTaskFinished"],unique_eligible_task_groups=len(groups),selected_task_disjoint_cohorts=len(selected),split_counts=dict(Counter(c["split"] for c in selected)),cohorts=selected,excluded_R3_R4_tasks=sorted(excluded),source_maps=1,shared_original_configuration_and_background_with_R4=True,no_query_outcome_selection=True)
 write(HERE/"SUPPORT_200.json",result);print({k:v for k,v in result.items() if k not in ["cohorts","excluded_R3_R4_tasks"]})
if __name__=="__main__":main()
