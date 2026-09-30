from collections import Counter,deque
from copy import deepcopy
from fractions import Fraction
from pathlib import Path
import hashlib,json
import numpy as np
from audit_joint_replay import Replay,HERE,ROOT,sha,require,profile,DELTA
from scheduler_prefix_successor import canonical_prefix
def write(p,o):
 if p.exists():
  require(json.loads(p.read_text())==o,"existing audit result differs");return
 with p.open("x") as f:json.dump(o,f,indent=2);f.write("\n")
def main():
 out=HERE/"native_attempt_01";reg=json.loads((out/"REGISTRATION.json").read_text());rec=json.loads((out/"RECEIPT.json").read_text());sup=json.loads((HERE/"SUPPORT_200.json").read_text());model=json.loads((out/"MODELS_FROZEN_BEFORE_TEST.json").read_text());models={k:[Fraction(z) for z in m["coefficients"]] for k,m in model["models"].items()}
 require(rec["complete"] and rec["all_native_passed"],"native whole batch not complete");require(all(sha(HERE/p)==v for p,v in reg["frozen"].items()),"pre-run frozen semantics changed")
 source=HERE/"author_200.json";d=json.loads(source.read_text());paths=[p.split(",") for p in d["actualPaths"]];positions=[[(c,r) for r,c,_ in d["start"]]]
 baseline=ROOT/"implementation_binding_evidence/baseline_selection_20260929";pre=json.loads((baseline/"pied_preflight.json").read_text());rel="lifelong_benchmark/random/maps/random-32-32-20.map";mp=baseline/"PIED-full"/rel;require(sha(mp)==pre["manifest"][rel]["sha256"],"original map changed");grid=mp.read_text().splitlines()[4:]
 for tick in range(200):
  before=positions[-1];after=[(x+DELTA[paths[a][tick]][0],y+DELTA[paths[a][tick]][1]) for a,(x,y) in enumerate(before)];require(len(set(after))==100,"source vertex collision");require(all(grid[y][x]=="." for x,y in after),"source obstacle");require(not any(before[a]==after[b] and before[b]==after[a] and before[a]!=after[a] for a in range(100) for b in range(a+1,100)),"source swap");positions.append(after)
 goals={tid:(c,r) for tid,r,c in d["tasks"]};source_tasks=0
 for a,events in enumerate(d["events"]):
  q=deque()
  for tid,t,k in events:
   if k=="assigned":q.append(tid)
   else:require(k=="finished" and q.popleft()==tid and positions[t][a]==goals[tid],"full source FIFO actual goal");source_tasks+=1
 require(source_tasks==730==d["numTaskFinished"],"source task total");generation=json.loads((HERE/"SOURCE_200_REGISTRATION.json").read_text());receipt=json.loads((HERE/"author_200.receipt.json").read_text());require(generation["command"]==receipt["command"] and receipt["returncode"]==0,"original runner command receipt");require(sha(Path(generation["binary"]))==generation["binary_sha256"] and sha(Path(generation["configuration"]))==generation["configuration_sha256"],"unmodified official binary/input")
 cohorts={c["cohort_id"]:c for c in sup["cohorts"]};used=set();splits={};excluded=set(sup["excluded_R3_R4_tasks"])
 for i,c in enumerate(cohorts.values()):
  require(c["split"]==["train","train","train","calibration","test"][i%5],"whole cohort split");t=c["source_tick"];union=set();taskids=set()
  for row in c["robots"]:
   a=row["agent"];require(list(positions[t][a])==row["start"],"source initial coordinate");q=deque()
   for tid,at,k in d["events"][a]:
    if at>t:break
    if k=="assigned":q.append(tid)
    else:require(q.popleft()==tid,"cohort initial FIFO")
   require(list(q)==row["source_revealed_queue"] and q[0]==row["heads"][0]["task"],"source actual head");begin=t;flattened=[];points=[positions[t][a]]
   for head in row["heads"]:
    tid=head["task"];taskids.add(tid);finish=next(at for x,at,k in d["events"][a] if x==tid and k=="finished");require(finish==head["source_finish_tick"] and paths[a][begin:finish]==head["route"] and list(goals[tid])==head["goal"],"full original two-task source route/service");require(next(at for x,at,k in d["events"][a] if x==tid and k=="assigned")==head["source_assigned_tick"],"task source assignment");flattened+=head["route"];begin=finish
   require(flattened==row["route"] and len(flattened)<=44 and len(row["heads"][0]["route"])<=20,"fixed route size");points=[positions[k][a] for k in range(t,begin+1)];require([list(z) for z in points]==row["route_points"],"source full path");union.update(points)
  require(len(taskids)==8 and not taskids&used and not taskids&excluded,"8 new task IDs disjoint across full groups/R3/R4");used|=taskids;require(union==set(map(tuple,c["resource_cells"])) and all(grid[y][x]=="." for x,y in union),"full support union free map");require(c["public_later_follow_relationships"],"fixed later geometric relation");splits.setdefault(c["split"],[]).append(c["cohort_id"])
 require({k:len(v) for k,v in splits.items()}==dict(train=6,calibration=2,test=2) and len(used)==80,"whole task-group partition");worlds={w["world_id"]:w for w in reg["worlds"]};audits=[];records={};by={}
 for e in rec["episodes"]:
  w=worlds[e["world_id"]];c=cohorts[w["cohort_id"]];require(e["returncode"]==0 and e["split"]==w["split"]==c["split"],"native world identity");require(sha(Path(e["raw"]))==e["raw_sha256"] and sha(Path(e["input"]))==e["input_sha256"],"receipt binding");expected=[];case=w["case"]
  for row in c["robots"]:
   a=row["agent"];theta=0 if case.get("eta0") else [-1,1][int.from_bytes(hashlib.sha256(f"{case['seed']}:{c['cohort_id']}:{a}:theta".encode()).digest()[:8],"big")%2]
   for leg,h in enumerate(row["route"]):
    eta=0
    if not case.get("eta0") and h!="W":
     bit=int.from_bytes(hashlib.sha256(f"{case['seed']}:{c['cohort_id']}:{a}:{leg}:flip".encode()).digest()[:8],"big")%10;eta=theta if bit<9 else -theta
     if case["shift"] and leg>=len(row["heads"][0]["route"]):eta=-eta
    expected.append(dict(agent=a,leg=leg,eta=eta,heading=h))
  require(expected==w["private_world_only"],"predeclared correlated error/shift law");actual=[json.loads(x) for x in Path(e["raw"]).read_text().splitlines()];actor=Replay(c,w,e["policy"],e["capacity"]);actor.coefficients=models;obj=actor.run(actual);key=(w["world_id"],e["policy"]);require(key not in by,"duplicate native arm");obj.update(world_id=w["world_id"],cohort_id=c["cohort_id"],split=c["split"],policy=e["policy"],capacity=e["capacity"],raw_sha256=e["raw_sha256"]);by[key]=obj;records[key]=actual;audits.append(obj)
 labels=json.loads((out/"ALL_LABELS.json").read_text());require(len(worlds)==54,"all registered complete worlds");expected_bindings=[]
 for w in worlds.values():
  wid=w["world_id"];decisions=[x for x in records[(wid,"WAIT")] if x["event"]=="actor_decision"][:3];policies={"WAIT"}
  for decision in decisions:
   for cand in decision["candidates"]:policies.add(f"probe_{decision['opportunity']}_{cand['agent']}");expected_bindings.append((wid,decision["opportunity"],cand["agent"]))
  if w["split"]=="test":policies|={"RR","condition","structural","ridge_history","ridge_nohistory"}
  require({p for x,p in by if x==wid}==policies,"all actual available arms, including0 opportunities")
 require(sorted((r["world_id"],r["opportunity"],r["source"]) for r in labels)==sorted(expected_bindings),"no unavailable/negative candidate omitted")
 for row in labels:
  wid=row["world_id"];p=row["chosen_policy"];wait=by[wid,"WAIT"];act=by[wid,p];gain=float(wait["restricted_flow_sum"])-float(act["restricted_flow_sum"]);require(abs(float(Fraction(row["target_flow_gain"]))-gain)<=1.00001e-6,"independent true full-stream counterfactual label");require(row["extra_tasks"]==act["served"]-wait["served"],"actual marginal task service")
  require(canonical_prefix(records[wid,"WAIT"],row["opportunity"])==canonical_prefix(records[wid,p],row["opportunity"]),"physical/public history prefix changed");decision=next(x for x in records[wid,"WAIT"] if x["event"]=="actor_decision" and x["opportunity"]==row["opportunity"]);cand=next(x for x in decision["candidates"] if x["agent"]==row["source"]);require(cand["features"]==row["features"],"offline label using future predictor data")
 train=[r for r in labels if r["split"]=="train"];require(model["same_architecture_labels_budget_split"] and model["train_label_sha256"]==sha(out/"TRAIN_CAL_LABELS.json"),"same model data contract")
 for name,m in model["models"].items():
  X=np.array([[1]+[float(Fraction(z)) if name=="ridge_history" or j<10 else 0 for j,z in enumerate(r["features"])] for r in train]);y=np.array([float(Fraction(r["target_flow_gain"])) for r in train]);penalty=np.eye(19);penalty[0,0]=0;fit=np.linalg.solve(X.T@X+penalty,X.T@y);require([Fraction(str(round(float(z),9))) for z in fit]==models[name],"independent exact rounded real trained ridge");require(m["train_rows"]==len(train) and not m["used_test_for_fit"] and not m["used_calibration_for_fit"],"cal/test leakage into fit")
  if name=="ridge_nohistory":require(all(z==0 for z in models[name][11:]),"no-history model trained hidden history")
 require(sha(out/"MODELS_FROZEN_BEFORE_TEST.json")==rec["model_sha256"],"frozen models changed")
 controls=[];example=next(e for e in rec["episodes"] if e["split"]=="train" and e["policy"]=="WAIT" and by[e["world_id"],e["policy"]]["decisions"]);w=worlds[example["world_id"]];c=cohorts[w["cohort_id"]];raw=records[w["world_id"],example["policy"]]
 bad=deepcopy(raw);next(x for x in bad if x["event"]=="actor_decision")["eta"]=1
 bad2=deepcopy(raw);next(x for x in bad2 if x["event"]=="actor_decision")["candidates"][0]["features"][10]="99"
 bad3=deepcopy(raw);next(x for x in bad3 if x["event"]=="actor_decision")["candidates"][0]["claims"][0]["task"]=999
 bad4=deepcopy(raw);next(x for x in bad4 if x["event"]=="actor_decision")["candidates"][0]["score"]="999999"
 for name,data in [("private condition",bad),("forged current-world END history",bad2),("wrong/future head claim",bad3),("wrong causal actor score",bad4),("truncated native",raw[:-1])]:
  actor=Replay(c,w,example["policy"],example["capacity"]);actor.coefficients=models
  try:actor.run(data)
  except AssertionError as e:controls.append(dict(name=name,rejected=True,reason=str(e)))
  else:raise AssertionError("negative escaped "+name)
 parent=HERE.parent/"public_value_20260930_r4";pm=json.loads((parent/"FROZEN_MANIFEST.json").read_text());require(all(sha(parent/p)==v["sha256"] for p,v in pm["frozen_files"].items()),"R4 frozen file changed");require(all(sha(ROOT/p)==v for p,v in reg["production_headers"].items()),"production9 changed")
 result=dict(status="passed",native_episodes=len(audits),worlds=54,cohorts=10,split_cohorts=splits,task_disjoint_source_tasks=80,original_source_actions=20000,original_source_services=source_tasks,native_MOVEs=sum(a["original_MOVEs"] for a in audits),normal_END_feedback=sum(a["END_feedback"] for a in audits),actual_queries=sum(a["queries"] for a in audits),world_frames=sum(a["frames"] for a in audits),head_reveals=sum(a["head_reveals"] for a in audits),true_train_only_refit=True,heldout_model_scoring_exercised=False,heldout_decision_support_missing=True,same_world_END_before_every_choice=True,current_head_only_features=True,exact_continuous_physics_and_lease_replay=True,models_sha256=rec["model_sha256"],mutations=controls,episodes=audits,source_maps=1,recognized_full_MAPF_benchmark=False,formal_external_comparison=False,production_COST=False,R4_1558_and_production9_unchanged=True)
 write(HERE/"AUDIT.json",result);print({k:v for k,v in result.items() if k not in ["episodes","mutations"]})
if __name__=="__main__":main()
