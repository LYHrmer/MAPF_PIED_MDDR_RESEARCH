"""Complete only the preregistered stages; no adaptive sample extension."""
import json,time,subprocess,os
import runner
P=runner.HERE
while not (P/'PROBES_SCHEDULING.json').exists():time.sleep(5)
assert json.loads((P/'PROBES_SCHEDULING.json').read_text())['failed']==0
subprocess.run(['rtk','proxy','python3',str(P/'pipeline.py'),'train'],check=True,cwd=P)
reg=json.loads((P/'REGISTRATION.json').read_text());test_names={w['name'] for w in reg['worlds'] if w['split']=='test'};n=sum(json.loads(p.read_text())['world'] in test_names for p in (P/'runs').glob('*.receipt.json'));assert n==0
runner.write(P/'MODEL_FREEZE_RECEIPT.json',dict(unix_time=time.time(),existing_test_receipts=n,model_sha256=runner.sha(P/'MODELS_FROZEN_BEFORE_TEST.json'),labels_sha256=runner.sha(P/'TRAIN_CAL_LABELS.json')))
env=dict(os.environ,R10_WORKERS='6');subprocess.run(['rtk','proxy','python3',str(P/'pipeline.py'),'test'],check=True,cwd=P,env=env)
