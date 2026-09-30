from concurrent.futures import ThreadPoolExecutor
from fractions import Fraction
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,tempfile,threading,time
import numpy as np
HERE=Path(__file__).resolve().parent;ROOT=Path("/home/lyh/MAPF_PIED_MDDR_RESEARCH");PARENT=HERE.parent/"public_value_20260930_r4"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,o):
 with p.open("x") as f:json.dump(o,f,indent=2);f.write("\n")
def run(cmd,timeout):
 start=time.monotonic()
 try:
  p=subprocess.run(["rtk","proxy",*cmd],text=True,capture_output=True,timeout=timeout);return dict(command=cmd,returncode=p.returncode,stdout=p.stdout,stderr=p.stderr,seconds=time.monotonic()-start)
 except subprocess.TimeoutExpired as e:
  def txt(x):return x.decode() if isinstance(x,bytes) else x or ""
  return dict(command=cmd,returncode=None,stdout=txt(e.stdout),stderr=txt(e.stderr),seconds=time.monotonic()-start,timeout=True)
def render(c,eta):
 lines=[f"C {x} {y}" for x,y in c["resource_cells"]]
 for r in c["robots"]:
  a,b=r["heads"];lines.append(" ".join(map(str,["R",r["agent"],a["task"],*r["start"],*a["goal"],",".join(a["route"])])));lines.append(" ".join(map(str,["F",r["agent"],b["task"],*b["goal"],",".join(b["route"])])))
 lines.extend(f"E {a} {leg} {e}" for (a,leg),e in sorted(eta.items()));return "\n".join(lines)+"\n"
def compile_native(out,pins):
 shutil.copy2(HERE/"joint_history_native.cpp",out/"SOURCE_AT_COMPILE.cpp")
 with tempfile.TemporaryDirectory(prefix="pied-history-r5-") as td:
  inc=Path(td)
  for p in pins:shutil.copy2(ROOT/p,inc/Path(p).name)
  lib=ROOT/"third_party/flint_host_config";sdk=ROOT/"third_party/host_sdk/usr";binary=out/"joint_history_native"
  cmd=["g++-11","-std=c++14","-O2","-Wall","-Wextra","-Werror","-pedantic","-fno-elide-constructors","-I",str(inc),"-isystem",str(sdk/"include"),"-isystem",str(lib/"src"),str(HERE/"joint_history_native.cpp"),"-L",str(lib),"-L",str(sdk/"lib/x86_64-linux-gnu"),"-Wl,-rpath,"+str(lib),"-lflint","-lmpfr","-lgmp","-o",str(binary)]
  e=run(cmd,120);write(out/"COMPILE.json",e)
 if e["returncode"]!=0:raise RuntimeError("compile failed "+e["stderr"])
 return binary
def canonical_prefix(records,op):
 i=next(i for i,x in enumerate(records) if x["event"]=="actor_decision" and x["opportunity"]==op);prefix=[]
 for x in records[:i]:
  x=json.loads(json.dumps(x))
  if x["event"]=="actor_decision":
   x.pop("policy");x["selected"]=""
   for c in x["candidates"]:c.pop("score")
  prefix.append(x)
 decision=json.loads(json.dumps(records[i]));decision.pop("policy");decision["selected"]="";decision["remaining_capacity"]=0
 for c in decision["candidates"]:c.pop("score")
 prefix.append(decision);return prefix
def flow(summary):
 v=summary["service_time_sum"];return Fraction(v["lower"]+v["upper"],2*v["denominator"])+96*(8-summary["served"])
def main():
 parser=argparse.ArgumentParser();parser.add_argument("--preflight",action="store_true");args=parser.parse_args();pins=json.loads((HERE.parent/"legal_and_sources.json").read_text());assert all(sha(ROOT/p)==v for p,v in pins.items())
 pm=json.loads((PARENT/"FROZEN_MANIFEST.json").read_text());assert all(sha(PARENT/f)==v["sha256"] for f,v in pm["frozen_files"].items())
 sup=json.loads((HERE/"SUPPORT_200.json").read_text());assert sup["selected_task_disjoint_cohorts"]==10 and sup["split_counts"]==dict(train=6,calibration=2,test=2)
 if args.preflight:
  out=HERE/"mechanical_attempt_02";out.mkdir(exist_ok=False);binary=compile_native(out,pins);c=sup["cohorts"][0];eta={(r["agent"],l):1 for r in c["robots"] for l,_ in enumerate(r["route"])};p=out/"input.txt";p.write_text(render(c,eta));records={}
  for policy in ["WAIT","RR"]:
   e=run([str(binary),str(p),policy,"0" if policy=="WAIT" else "4"],120);raw=out/(policy+".jsonl");raw.write_text(e.pop("stdout"));e.update(raw_sha256=sha(raw),input_sha256=sha(p));write(out/(policy+".receipt.json"),e);assert e["returncode"]==0,e["stderr"];records[policy]=[json.loads(x) for x in raw.read_text().splitlines()]
  dec=[x for x in records["WAIT"] if x["event"]=="actor_decision"];assert dec and all(x["END_only_known"]>=2 for x in dec);assert len([x for x in records["WAIT"] if x["event"]=="public_head_revealed"])>=1
  write(out/"PREFLIGHT.json",dict(status="passed",WAIT_summary=records["WAIT"][-1],RR_summary=records["RR"][-1],same_world_END_at_first=dec[0]["END_only_known"],first_candidates=len(dec[0]["candidates"]),source_and_contract_only_no_model_fit=True));print("MECHANICAL PASSED",records["WAIT"][-1],flush=True);return
 out=HERE/"native_attempt_01";out.mkdir(exist_ok=True);binary=HERE/"mechanical_attempt_02/joint_history_native";assert binary.exists()
 freeze={p.name:sha(p) for p in [HERE/"CONTRACT.md",HERE/"SOURCE_REGISTRATION.json",HERE/"SOURCE_200_REGISTRATION.json",HERE/"SUPPORT_200.json",HERE/"prepare.py",HERE/"pipeline.py",HERE/"joint_history_native.cpp"]}
 worlds=[]
 for c in sup["cohorts"]:
  cid=c["cohort_id"];split=c["split"];base={"train":5101,"calibration":6101,"test":7101}[split];cases=[dict(name=f"IID_{s}",seed=s,shift=False) for s in range(base,base+4)]+[dict(name="eta0",eta0=True)]
  if split=="test":cases.extend(dict(name=f"SHIFT_{s}",seed=s,shift=True) for s in [7201,7202])
  for case in cases:
   private=[];eta={}
   for r in c["robots"]:
    a=r["agent"];boundary=len(r["heads"][0]["route"]);theta=0 if case.get("eta0") else [-1,1][int.from_bytes(hashlib.sha256(f"{case['seed']}:{cid}:{a}:theta".encode()).digest()[:8],"big")%2]
    for l,heading in enumerate(r["route"]):
     e=0
     if not case.get("eta0") and heading!="W":
      bit=int.from_bytes(hashlib.sha256(f"{case['seed']}:{cid}:{a}:{l}:flip".encode()).digest()[:8],"big")%10;e=theta if bit<9 else -theta
      if case["shift"] and l>=boundary:e=-e
     eta[a,l]=e;private.append(dict(agent=a,leg=l,eta=e,heading=heading))
   wid=cid+"__"+case["name"];p=out/(wid+".input.txt");content=render(c,eta)
   if p.exists():assert p.read_text()==content
   else:p.write_text(content)
   worlds.append(dict(world_id=wid,cohort_id=cid,split=split,case=case,input=str(p),input_sha256=sha(p),private_world_only=private))
 reg=dict(frozen=freeze,worlds=worlds,production_headers=pins,parent_manifest_sha256=sha(PARENT/"FROZEN_MANIFEST.json"),binary_sha256=sha(binary),concurrent_worlds=10,no_current_END_prior=True,label_opportunities=3,budget=4,deadline=96,train_cal_then_fit_freeze_then_test=True)
 rp=out/"REGISTRATION.json"
 if rp.exists():assert json.loads(rp.read_text())==reg
 else:write(rp,reg)
 episodes=[];rows=[];lock=threading.Lock();completed=0
 def native(w,policy,model_lines=""):
  assert all(sha(HERE/k)==v for k,v in freeze.items());stem=w["world_id"]+"__"+policy;rp=out/(stem+".receipt.json");p=Path(w["input"])
  if model_lines:
   p=out/(w["world_id"]+".model.input.txt");text=Path(w["input"]).read_text()+model_lines
   if p.exists():assert p.read_text()==text
   else:p.write_text(text)
  if rp.exists():
   e=json.loads(rp.read_text());assert e["returncode"]==0 and sha(Path(e["raw"]))==e["raw_sha256"] and sha(p)==e["input_sha256"]
  else:
   b=0 if policy=="WAIT" else 1 if policy.startswith("probe_") else 4;e=run([str(binary),str(p),policy,str(b)],180);raw=out/(stem+".jsonl");raw.write_text(e.pop("stdout"));e.update(world_id=w["world_id"],cohort_id=w["cohort_id"],split=w["split"],policy=policy,capacity=b,raw=str(raw),raw_sha256=sha(raw),input=str(p),input_sha256=sha(p))
   if e["returncode"]==0:e["summary"]=json.loads(raw.read_text().splitlines()[-1])
   write(rp,e)
  if e["returncode"]!=0:raise RuntimeError("native failure "+stem+" "+e["stderr"])
  records=[json.loads(x) for x in Path(e["raw"]).read_text().splitlines()]
  with lock:episodes.append(e)
  return e,records
 def collect(w,model_lines="",deploy=False):
  nonlocal completed
  local=[];wait,wr=native(w,"WAIT",model_lines);wf=flow(wait["summary"]);dec=[x for x in wr if x["event"]=="actor_decision"][:3]
  for decision in dec:
   op=decision["opportunity"]
   for cand in decision["candidates"]:
    a=cand["agent"];e,ar=native(w,f"probe_{op}_{a}",model_lines);assert canonical_prefix(wr,op)==canonical_prefix(ar,op),"counterfactual prefix changed"
    actual=next(x for x in ar if x["event"]=="actor_decision" and x["opportunity"]==op);assert actual["selected"]==cand["move"]
    local.append(dict(world_id=w["world_id"],cohort_id=w["cohort_id"],split=w["split"],opportunity=op,source=a,move=cand["move"],features=cand["features"],END_only_known=decision["END_only_known"],at=decision["at"],target_flow_gain=str(wf-flow(e["summary"])),extra_tasks=e["summary"]["served"]-wait["summary"]["served"],chosen_policy=e["policy"],verified_identical_public_physical_prefix=True))
  if deploy:
   for policy in ["RR","condition","structural","ridge_history","ridge_nohistory"]:native(w,policy,model_lines)
  with lock:
   rows.extend(local);completed+=1;print("COMPLETE WORLDS",completed,w["world_id"],"labels",len(local),flush=True)
 def phase(ws,text="",deploy=False):
  with ThreadPoolExecutor(max_workers=10) as pool:
   futures=[pool.submit(collect,w,text,deploy) for w in ws]
   for f in futures:f.result()
 phase([w for w in worlds if w["split"]!="test"]);rows.sort(key=lambda r:(r["world_id"],r["opportunity"],r["source"]));label=out/"TRAIN_CAL_LABELS.json"
 if label.exists():assert json.loads(label.read_text())==rows
 else:write(label,rows)
 train=[r for r in rows if r["split"]=="train"];assert train;models={}
 for name in ["ridge_history","ridge_nohistory"]:
  X=np.array([[1]+[float(Fraction(z)) if name=="ridge_history" or j<10 else 0.0 for j,z in enumerate(r["features"])] for r in train]);y=np.array([float(Fraction(r["target_flow_gain"])) for r in train]);penalty=np.eye(19);penalty[0,0]=0;fit=np.linalg.solve(X.T@X+penalty,X.T@y);coef=[Fraction(str(round(float(x),9))) for x in fit]
  models[name]=dict(lambda_value=1,intercept_penalized=False,train_rows=len(train),train_cohorts=sorted({r["cohort_id"] for r in train}),used_calibration_for_fit=False,used_test_for_fit=False,features=18,nohistory_zero_slots=list(range(10,18)) if name=="ridge_nohistory" else [],coefficients=[str(x) for x in coef],fit_float_coefficients=fit.tolist(),train_rmse=float(np.sqrt(np.mean((X@np.array([float(x) for x in coef])-y)**2))))
 model=dict(models=models,train_label_sha256=sha(label),train_row_bindings=[dict(world_id=r["world_id"],opportunity=r["opportunity"],source=r["source"]) for r in train],same_architecture_labels_budget_split=True);mp=out/"MODELS_FROZEN_BEFORE_TEST.json"
 if mp.exists():assert json.loads(mp.read_text())==model
 else:write(mp,model)
 mh=sha(mp);print("MODELS FROZEN",mh,"train rows",len(train),flush=True);text="".join(f"M {name} {Fraction(z).numerator} {Fraction(z).denominator}\n" for name,m in models.items() for z in m["coefficients"]);phase([w for w in worlds if w["split"]=="test"],text,True);assert sha(mp)==mh
 rows.sort(key=lambda r:(r["world_id"],r["opportunity"],r["source"]));episodes.sort(key=lambda e:(e["world_id"],e["policy"]));write(out/"ALL_LABELS.json",rows);write(out/"RECEIPT.json",dict(complete=True,episodes=episodes,all_native_passed=True,total_native_episodes=len(episodes),worlds=len(worlds),cohorts=10,model_sha256=mh,binary_sha256=sha(binary),all_same_prefixes_verified=True));print("COMPLETE",len(episodes),"native arms",flush=True)
if __name__=="__main__":main()
