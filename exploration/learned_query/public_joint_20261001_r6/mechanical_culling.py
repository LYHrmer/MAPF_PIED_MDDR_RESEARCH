from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import hashlib,importlib.util,json,threading
HERE=Path(__file__).resolve().parent;old=HERE.parent/"public_history_20260930_r5/pipeline.py";spec=importlib.util.spec_from_file_location("r5_helpers",old);helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper);helper.HERE=HERE
sha=helper.sha;write=helper.write;run=helper.run
def render(c,private):
 lines=[f"C {x} {y}" for x,y in c["resource_cells"]]
 for r in c["robots"]:
  first=r["heads"][0];lines.append(" ".join(map(str,["R",r["agent"],first["task"],*r["start"],*first["goal"],",".join(first["route"])])))
  for head in r["heads"][1:]:lines.append(" ".join(map(str,["F",r["agent"],head["task"],*head["goal"],",".join(head["route"])])))
 lines.extend(f"E {x['agent']} {x['leg']} {x['eta']}" for x in private);return "\n".join(lines)+"\n"
def dynamics(c,seed,shift=False,zero=False):
 result=[];cid=c["cohort_id"]
 for r in c["robots"]:
  a=r["agent"];theta=[-1,1][int.from_bytes(hashlib.sha256(f"{seed}:{cid}:{a}:theta".encode()).digest()[:8],"big")%2]
  for leg,h in enumerate(r["route"]):
   bit=int.from_bytes(hashlib.sha256(f"{seed}:{cid}:{a}:{leg}:flip".encode()).digest()[:8],"big")%10;e=0 if zero or h=="W" else theta if bit<9 else -theta
   if shift and leg>=len(r["heads"][0]["route"]):e=-e
   result.append(dict(agent=a,leg=leg,heading=h,eta=e))
 return result
def main():
 out=HERE/"mechanical_attempt_02";out.mkdir(exist_ok=False);sup=json.loads((HERE/"SUPPORT.json").read_text());pins=json.loads((HERE.parent/"legal_and_sources.json").read_text());worlds=[]
 for c in sup["mechanical"]:
  private=dynamics(c,9101);p=out/(c["cohort_id"]+".input.txt");p.write_text(render(c,private));worlds.append(dict(world_id=c["cohort_id"]+"__9101",cohort_id=c["cohort_id"],input=str(p),input_sha256=sha(p),private_world_only=private,seed=9101))
 frozen={p.name:sha(p) for p in [HERE/"CONTRACT.md",HERE/"SUPPORT.json",HERE/"joint_history_native.cpp",HERE/"mechanical_culling.py"]};write(out/"REGISTRATION.json",dict(worlds=worlds,frozen=frozen,production_headers=pins,prefixN8_N16=True,test_not_used=True,B16=True,deadline=384));binary=helper.compile_native(out,pins);episodes=[];lock=threading.Lock()
 def collect(w):
  for policy in ["WAIT","RR","condition"]:
   e=run([str(binary),w["input"],policy,"0" if policy=="WAIT" else"16"],300);stem=w["world_id"]+"__"+policy;p=out/(stem+".jsonl");p.write_text(e.pop("stdout"));e.update(world_id=w["world_id"],cohort_id=w["cohort_id"],policy=policy,capacity=0 if policy=="WAIT" else 16,input=w["input"],input_sha256=w["input_sha256"],raw=str(p),raw_sha256=sha(p));
   if e["returncode"]==0:e["summary"]=json.loads(p.read_text().splitlines()[-1])
   write(out/(stem+".receipt.json"),e)
   with lock:episodes.append(e)
   if e["returncode"]!=0:raise RuntimeError(stem+e["stderr"])
  print("MECHANICAL GROUP",w["cohort_id"],flush=True)
 with ThreadPoolExecutor(max_workers=2) as pool:
  futures=[pool.submit(collect,w) for w in worlds]
  for f in futures:f.result()
 write(out/"RECEIPT.json",dict(complete=True,episodes=episodes,all_native_passed=True,binary_sha256=sha(binary)));print("MECHANICAL COMPLETE",len(episodes),flush=True)
if __name__=="__main__":main()
