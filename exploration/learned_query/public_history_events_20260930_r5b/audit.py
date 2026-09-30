from copy import deepcopy
from pathlib import Path
import hashlib,json
from audit_joint_replay import Replay,sha,require,HERE
def write(p,o):
 if p.exists():require(json.loads(p.read_text())==o,"different saved audit");return
 with p.open("x") as f:json.dump(o,f,indent=2);f.write("\n")
def main():
 parent=HERE.parent/"public_history_20260930_r5";out=HERE/"mechanical_attempt_01";reg=json.loads((out/"REGISTRATION.json").read_text());rec=json.loads((out/"RECEIPT.json").read_text());sup=json.loads((parent/"SUPPORT_200.json").read_text());cohorts={c["cohort_id"]:c for c in sup["cohorts"]};worlds={w["world_id"]:w for w in reg["worlds"]};require(rec["complete"] and rec["all_native_passed"] and len(rec["episodes"])==24 and len(worlds)==8,"all mechanical runs");require(reg["test_not_used"] and not reg["trained_model"],"scope misclaim");require(all(sha(HERE/f)==v for f,v in reg["frozen"].items()),"preregistered protocol/native changes");require(sha(parent/"SUPPORT_200.json")==reg["parent_source_support_sha256"],"same fixed training/cal geometry")
 audits=[];records={};seen=set()
 for e in rec["episodes"]:
  w=worlds[e["world_id"]];c=cohorts[e["cohort_id"]];require(c["split"] in ["train","calibration"] and e["split"]==c["split"]==w["split"],"mechanical used test cohort");require(e["returncode"]==0 and sha(Path(e["raw"]))==e["raw_sha256"] and sha(Path(e["input"]))==e["input_sha256"]==w["input_sha256"],"raw/input native identity");expected=[]
  for r in c["robots"]:
   a=r["agent"];theta=[-1,1][int.from_bytes(hashlib.sha256(f"8101:{c['cohort_id']}:{a}:theta".encode()).digest()[:8],"big")%2]
   for leg,h in enumerate(r["route"]):
    bit=int.from_bytes(hashlib.sha256(f"8101:{c['cohort_id']}:{a}:{leg}:flip".encode()).digest()[:8],"big")%10;eta=0 if h=="W" else theta if bit<9 else -theta;expected.append(dict(agent=a,leg=leg,heading=h,eta=eta))
  require(expected==w["private_world_only"],"registered newseed/private dynamics law");actualE=[tuple(map(int,s.split()[1:])) for s in Path(e["input"]).read_text().splitlines() if s.startswith("E ")];require(sorted(actualE)==sorted((r["agent"],r["leg"],r["eta"]) for r in expected),"input E differs");require(not any(s.startswith("M ") or s.startswith("H ") for s in Path(e["input"]).read_text().splitlines()),"R5b imported old weights/prior")
  raw=[json.loads(s) for s in Path(e["raw"]).read_text().splitlines()];actor=Replay(c,w,e["policy"],e["capacity"]);obj=actor.run(raw);obj.update(world_id=e["world_id"],cohort_id=c["cohort_id"],split=c["split"],policy=e["policy"],capacity=e["capacity"],raw_sha256=e["raw_sha256"]);audits.append(obj);key=(w["world_id"],e["policy"]);require(key not in seen,"duplicate arm");seen.add(key);records[key]=raw
 require(seen=={(w,p) for w in worlds for p in ["WAIT","RR","condition"]},"complete same-world three arms")
 controls=[];example=next(e for e in rec["episodes"] if e["policy"]=="condition" and e["summary"]["eligible_opportunities"]>2);w=worlds[example["world_id"]];c=cohorts[w["cohort_id"]];original=records[w["world_id"],"condition"]
 bad=deepcopy(original);next(x for x in bad if x["event"]=="actor_decision")["eta"]=1
 bad2=deepcopy(original);next(x for x in bad2 if x["event"]=="actor_decision")["trigger"]="private_motor_boundary"
 bad3=deepcopy(original);next(x for x in bad3 if x["event"]=="actor_decision")["candidates"][0]["features"][18]="99"
 bad4=deepcopy(original);next(x for x in bad4 if x["event"]=="actor_decision")["candidates"][0]["probability"]="99"
 bad5=deepcopy(original);next(x for x in bad5 if x["event"]=="actor_decision")["candidates"][0]["claims"][0]["task"]=999
 for name,data in [("private condition",bad),("private motor event trigger",bad2),("future/nonpublic age",bad3),("wrong survival-conditioned probability",bad4),("future task claim",bad5),("truncated native",original[:-1])]:
  actor=Replay(c,w,"condition",4)
  try:actor.run(data)
  except AssertionError as e:controls.append(dict(name=name,rejected=True,reason=str(e)))
  else:raise AssertionError("negative escaped "+name)
 pm=json.loads((parent/"FROZEN_MANIFEST.json").read_text());require(all(sha(parent/f)==v["sha256"] for f,v in pm["frozen_files"].items()),"R5 frozen changed");root=Path("/home/lyh/MAPF_PIED_MDDR_RESEARCH");require(all(sha(root/f)==v for f,v in reg["production_headers"].items()),"production9 changed")
 result=dict(status="passed",native_episodes=24,cohorts=8,train_cal_only=True,test_used=False,trained_model=False,public_feature_schema=19,exact_public_trigger_gate=True,same_world_END_before_every_choice=True,current_head_only=True,true_RR_cursor=True,strong_rule_survival_conditioned=True,strong_rule_known_law=True,source_task_count=64,native_MOVEs=sum(o["original_MOVEs"] for o in audits),normal_END=sum(o["END_feedback"] for o in audits),frames=sum(o["frames"] for o in audits),queries=sum(o["queries"] for o in audits),head_reveals=sum(o["head_reveals"] for o in audits),survival_hypothesis_exclusions=sum(o["survival_hypothesis_exclusions"] for o in audits),multiple_legal_opportunities_observed=any(o["decisions"]>1 for o in audits),max_competing_candidates=max(o["max_candidates"] for o in audits),competition_observed=any(o["max_candidates"]>1 for o in audits),mutations=controls,episodes=audits,R5_432_and_production9_unchanged=True,formal_external_benchmark=False,production_COST=False)
 write(HERE/"AUDIT.json",result);print({k:v for k,v in result.items() if k not in ["episodes","mutations"]})
if __name__=="__main__":main()
