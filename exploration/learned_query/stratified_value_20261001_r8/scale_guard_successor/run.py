from concurrent.futures import ThreadPoolExecutor,as_completed
from pathlib import Path
import json
import runner
P=runner.HERE;PARENT=P.parent;OUT=P/'runs'
def main():
 parent=json.loads((PARENT/'REGISTRATION.json').read_text());ws=[w for w in parent['worlds'] if w['split']=='scale'];modelpath=PARENT/'MODELS_FROZEN_BEFORE_TEST.json';model=json.loads(modelpath.read_text());models=model['models'];mh=runner.sha(modelpath)
 old=(PARENT/'joint_history_native.cpp').read_text();new=(P/'joint_history_native.cpp').read_text();assert new==old.replace('robots.size()<=16','robots.size()<=32')
 assert runner.sha(PARENT/'joint_history_native.cpp')==parent['frozen']['joint_history_native.cpp']
 binary=runner.compile_native();failed=[]
 for w in ws:
  for policy in parent['policies']:
   receipt=PARENT/'runs'/(w['name']+'__'+policy+'.receipt.json');e=json.loads(receipt.read_text());assert e['error'] and 'fixed joint support/training identity differs' in e['native_stderr'];assert runner.render(w,models)==Path(e['input']).read_text();failed.append(dict(world=w['name'],policy=policy,parent_receipt_sha256=runner.sha(receipt),input_sha256=e['input_sha256']))
 runner.write(P/'REGISTRATION.json',dict(worlds=ws,policies=parent['policies'],frozen={n:runner.sha(P/n) for n in ['CONTRACT.md','joint_history_native.cpp','runner.py','run.py','audit.py','audit_reference.py','audit_all.py','NATIVE_EXACT_DIFF.patch']},binary_sha256=runner.sha(binary),bridge_sha256=runner.sha(runner.BRIDGE),config_sha256=runner.sha(runner.CONFIG),parent_model_path=str(modelpath),parent_model_sha256=mh,parent_registration_sha256=runner.sha(PARENT/'REGISTRATION.json'),parent_native_source_sha256=runner.sha(PARENT/'joint_history_native.cpp'),native_semantic_diff='constructor N maximum16 to32 only',original_guard_failures=failed,post_outcome_compatibility_correction=True,new_independent_test_worlds=False,workers=8))
 entries=[]
 with ThreadPoolExecutor(max_workers=8) as pool:
  futures=[pool.submit(runner.native,w,policy,OUT,models) for w in ws for policy in parent['policies']]
  for f in as_completed(futures):entries.append(f.result())
 assert runner.sha(modelpath)==mh
 runner.write(P/'RECEIPT.json',dict(complete=True,native_episodes=len(entries),successful=sum(e['error'] is None for e in entries),failed=sum(e['error'] is not None for e in entries),all_inputs_identical_to_original_guard_rejections=True,parent_model_sha256=mh,parent_native_source_unchanged=True))
if __name__=='__main__':main()
