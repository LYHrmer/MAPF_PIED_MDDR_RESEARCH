"""Resume only analysis after the documented planner_us comparison failure."""
import json,hashlib,time
from pathlib import Path
import runner,analyze,learn
P=runner.HERE
def planner_signature(path):
 digest=hashlib.sha256();n=0
 for line in Path(path).open():
  row=json.loads(line);row['result'].pop('planner_us');digest.update((json.dumps(row,sort_keys=True,separators=(',',':'))+'\n').encode());n+=1
 return dict(canonical_sha256=digest.hexdigest(),records=n)
def main():
 reg=json.loads((P/'REGISTRATION.json').read_text());pairs=[];compat=[]
 for w in reg['train_worlds']:
  e=json.loads((P/'runs'/(w['name']+'__macro_STOP.receipt.json')).read_text());assert e['error'] is None
  a=json.loads((P/'audits'/(w['name']+'__macro_STOP.receipt.audit.json')).read_text());assert a['status']=='passed'
  c=analyze.outcome(w,runner.cached_c(w));s=analyze.outcome(w,e);pairs.append(analyze.pair(w,c,s))
  if w['name'] in reg['compatibility']:
   ne=json.loads((P/'runs'/(w['name']+'__macro_C.receipt.json')).read_text());n=analyze.outcome(w,ne)
   assert n['raw_sha256']==c['raw_sha256'],'full raw stream not byte identical'
   old=planner_signature(c['planner']);new=planner_signature(n['planner']);assert old==new
   compat.append(dict(world=w['name'],raw_sha256=c['raw_sha256'],old_planner_sha256=c['planner_sha256'],new_planner_sha256=n['planner_sha256'],planner_canonical=old,only_excluded_field='result.planner_us',passed=True))
 runner.write(P/'C_COMPATIBILITY.json',compat);runner.write(P/'TRAIN_PAIRS.json',pairs);runner.write(P/'TRAIN_SUMMARY.json',analyze.summarize(pairs))
 model=learn.fit(pairs);model['training_pairs_sha256']=runner.sha(P/'TRAIN_PAIRS.json');model['learn_source_sha256']=runner.sha(P/'learn.py');runner.write(P/'MODEL_FROZEN.json',model)
 runner.write(P/'POSTPROCESS_RECEIPT.json',dict(finished_unix_ns=time.time_ns(),amendment_sha256=runner.sha(P/'POSTPROCESS_AMENDMENT.md'),finish_source_sha256=runner.sha(Path(__file__)),registration_sha256=runner.sha(P/'REGISTRATION.json'),no_native_rerun=True,model_source_unchanged=runner.sha(P/'learn.py')==reg['frozen']['learn.py']))
 print(json.dumps({'activated':model['activated'],'preferences':model['preferences'],'summary':analyze.summarize(pairs)},indent=2),flush=True)
if __name__=='__main__':main()
