from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import hashlib,importlib.util,json,threading
HERE=Path(__file__).resolve().parent;PARENT=HERE.parent/"public_history_20260930_r5"
spec=importlib.util.spec_from_file_location("r5_immutable_helpers",PARENT/"pipeline.py");m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.HERE=HERE
sha=m.sha;write=m.write;run=m.run
def main():
 out=HERE/"mechanical_attempt_01";out.mkdir(exist_ok=False);pins=json.loads((HERE.parent/"legal_and_sources.json").read_text());sup=json.loads((PARENT/"SUPPORT_200.json").read_text());worlds=[]
 for c in sup["cohorts"]:
  if c["split"]=="test":continue
  cid=c["cohort_id"];eta={};private=[]
  for r in c["robots"]:
   a=r["agent"];theta=[-1,1][int.from_bytes(hashlib.sha256(f"8101:{cid}:{a}:theta".encode()).digest()[:8],"big")%2]
   for leg,h in enumerate(r["route"]):
    v=int.from_bytes(hashlib.sha256(f"8101:{cid}:{a}:{leg}:flip".encode()).digest()[:8],"big")%10;e=0 if h=="W" else theta if v<9 else -theta;eta[a,leg]=e;private.append(dict(agent=a,leg=leg,heading=h,eta=e))
  p=out/(cid+".input.txt");p.write_text(m.render(c,eta));worlds.append(dict(world_id=cid+"__MECHANICAL_8101",cohort_id=cid,split=c["split"],input=str(p),input_sha256=sha(p),private_world_only=private))
 frozen={p.name:sha(p) for p in [HERE/"CONTRACT.md",HERE/"joint_history_native.cpp",HERE/"run_mechanical.py"]};write(out/"REGISTRATION.json",dict(worlds=worlds,frozen=frozen,production_headers=pins,seed=8101,all8_train_cal_cohorts=True,test_not_used=True,trained_model=False,public_age_schema=19,policies=["WAIT","RR","condition"],B4=True,parent_source_support_sha256=sha(PARENT/"SUPPORT_200.json"),concurrent_worlds=10))
 binary=m.compile_native(out,pins);episodes=[];lock=threading.Lock()
 def collect(w):
  for policy in ["WAIT","RR","condition"]:
   assert all(sha(HERE/p)==v for p,v in frozen.items());e=run([str(binary),w["input"],policy,"0" if policy=="WAIT" else "4"],180);stem=w["world_id"]+"__"+policy;p=out/(stem+".jsonl");p.write_text(e.pop("stdout"));e.update(world_id=w["world_id"],cohort_id=w["cohort_id"],split=w["split"],policy=policy,capacity=0 if policy=="WAIT" else 4,raw=str(p),raw_sha256=sha(p),input=w["input"],input_sha256=w["input_sha256"]);
   if e["returncode"]==0:e["summary"]=json.loads(p.read_text().splitlines()[-1])
   write(out/(stem+".receipt.json"),e)
   if e["returncode"]!=0:raise RuntimeError(stem+e["stderr"])
   with lock:episodes.append(e)
  print("MECHANICAL WORLD",w["world_id"],flush=True)
 with ThreadPoolExecutor(max_workers=10) as pool:
  futures=[pool.submit(collect,w) for w in worlds]
  for f in futures:f.result()
 episodes.sort(key=lambda e:(e["world_id"],e["policy"]));write(out/"RECEIPT.json",dict(complete=True,all_native_passed=True,episodes=episodes,native_episodes=len(episodes),worlds=len(worlds),test_not_used=True,trained_model=False,binary_sha256=sha(binary)));print("MECHANICAL COMPLETE",len(episodes),flush=True)
if __name__=="__main__":main()
