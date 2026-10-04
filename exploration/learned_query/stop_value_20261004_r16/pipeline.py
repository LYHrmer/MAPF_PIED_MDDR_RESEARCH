from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed,ProcessPoolExecutor
import json,time,sys,difflib
import runner,analyze,learn
P=runner.HERE
def register():
 old=json.loads((runner.OLD/'REGISTRATION.json').read_text())
 train=[w for w in old['worlds'] if w['split']=='train']
 cal=[w for w in old['worlds'] if w['seed'] in [131201,132201,131202]]
 assert len(train)==24 and len(cal)==6 and all(w['split']!='test' for w in train+cal)
 compatibility=[min([w for w in train if w['map_name']==m and w['budget']==8],key=lambda x:x['scenario_offset'])['name'] for m in ['empty-32-32','random-32-32-10']]
 baseline=[]
 for w in train+cal:
  e=runner.cached_c(w);p=runner.OLD/'runs'/(w['name']+'__macro_C.receipt.json')
  baseline.append(dict(world=w['name'],receipt=str(p),receipt_sha256=runner.sha(p),**{k:e[k] for k in ['input_sha256','raw_sha256','planner_sha256','native_source_sha256','binary_sha256','bridge_sha256','config_sha256']}))
 oldsrc=(runner.OLD/'joint_history_native.cpp').read_text();newsrc=(P/'joint_history_native.cpp').read_text()
 before='    std::string choose(';after='    void coefficient('
 # Actor state and all physical/world methods must be unchanged.
 assert oldsrc.split(before)[0]==newsrc.split(before)[0]
 tail='class World3';assert oldsrc.split(tail)[1].split('int main')[0]==newsrc.split(tail)[1].split('int main')[0]
 patch=''.join(difflib.unified_diff(oldsrc.splitlines(True),newsrc.splitlines(True),fromfile='R13/joint_history_native.cpp',tofile='R16/joint_history_native.cpp'))
 (P/'SOURCE_DELTA.patch').write_text(patch)
 runner.compile_native()
 names=['MENTOR_PREEXEC.md','PROTOCOL.md','runner.py','learn.py','analyze.py','pipeline.py','joint_history_native.cpp','audit.py','audit_reference.py','macro_audit.py','SOURCE_DELTA.patch']
 runner.write(P/'REGISTRATION.json',dict(frozen_unix_ns=time.time_ns(),train_worlds=train,cal_worlds=cal,compatibility=compatibility,reused_C=baseline,frozen={n:runner.sha(P/n) for n in names},binary_sha256=runner.sha(P/'build/joint_history_native'),bridge_sha256=runner.sha(runner.BRIDGE),config_sha256=runner.sha(runner.CONFIG),old_registration_sha256=runner.sha(runner.OLD/'REGISTRATION.json'),max_native=32,native_workers=4,audit_workers=2,scope='old TRAIN/CAL developmental C/STOP exploration; no TEST access'))
 print('REGISTERED 24 TRAIN STOP + 2 C compatibility + optional 6 CAL STOP',flush=True)
def perform_audit(path):
 import audit
 e=json.loads(Path(path).read_text());assert e['error'] is None
 a=audit.audit(e);runner.write(P/'audits'/(Path(path).stem+'.audit.json'),a);return a
def execute(stage):
 reg=json.loads((P/'REGISTRATION.json').read_text());worlds=reg['train_worlds'] if stage=='TRAIN' else reg['cal_worlds'];jobs=[(w,'macro_STOP') for w in worlds]
 if stage=='TRAIN':jobs=[(w,'macro_C') for w in worlds if w['name'] in reg['compatibility']]+jobs
 else:assert json.loads((P/'MODEL_FROZEN.json').read_text())['activated']
 runner.write(P/(stage+'_START.json'),dict(started_unix_ns=time.time_ns(),registration_sha256=runner.sha(P/'REGISTRATION.json'),jobs=[dict(world=w['name'],policy=p) for w,p in jobs]))
 with ThreadPoolExecutor(max_workers=4) as pool:
  futures=[pool.submit(runner.native,w,p,stage) for w,p in jobs]
  results=[f.result() for f in as_completed(futures)]
 assert all(e['error'] is None for e in results),'keep failures; do not fit'
 print(stage,'native complete; audit start',flush=True)
 paths=[str(P/'runs'/(e['world']+'__'+e['policy']+'.receipt.json')) for e in results]
 with ProcessPoolExecutor(max_workers=2) as pool:
  for a in pool.map(perform_audit,paths):print('audit',a['world'],a['policy'],'passed',flush=True)
 pairs=[];compat=[]
 for w in worlds:
  ce=runner.cached_c(w);se=json.loads((P/'runs'/(w['name']+'__macro_STOP.receipt.json')).read_text());c=analyze.outcome(w,ce);s=analyze.outcome(w,se);pairs.append(analyze.pair(w,c,s))
  if stage=='TRAIN' and w['name'] in reg['compatibility']:
   ne=json.loads((P/'runs'/(w['name']+'__macro_C.receipt.json')).read_text());n=analyze.outcome(w,ne)
   assert n['canonical_complete_sha256']==c['canonical_complete_sha256'] and n['planner_sha256']==c['planner_sha256'],'new C semantic equivalence failed'
   compat.append(dict(world=w['name'],canonical_complete_sha256=c['canonical_complete_sha256'],old_raw_sha256=c['raw_sha256'],new_raw_sha256=n['raw_sha256'],planner_sha256=c['planner_sha256'],passed=True))
 runner.write(P/(stage+'_PAIRS.json'),pairs);runner.write(P/(stage+'_SUMMARY.json'),analyze.summarize(pairs))
 if stage=='TRAIN':
  runner.write(P/'C_COMPATIBILITY.json',compat);model=learn.fit(pairs);model['training_pairs_sha256']=runner.sha(P/'TRAIN_PAIRS.json');model['learn_source_sha256']=runner.sha(P/'learn.py');runner.write(P/'MODEL_FROZEN.json',model);print('MODEL ACTIVATED',model['activated'],model['preferences'],flush=True)
 else:
  model=json.loads((P/'MODEL_FROZEN.json').read_text());selections=[dict(world=r['world'],selected=learn.choose(model,r['gate']),selected_raw_sha256=r[learn.choose(model,r['gate'])]['raw_sha256']) for r in pairs]
  selected=[r[learn.choose(model,r['gate'])] for r in pairs]
  runner.write(P/'CAL_SELECTIONS.json',dict(model_sha256=runner.sha(P/'MODEL_FROZEN.json'),selections=selections,total=analyze.total(selected),fixed_C=analyze.total([r['C'] for r in pairs]),fixed_STOP=analyze.total([r['STOP'] for r in pairs]),no_CAL_tuning=True))
 print(stage,'complete',flush=True)
if __name__=='__main__':
 if sys.argv[1]=='register':register()
 else:execute(sys.argv[1])
