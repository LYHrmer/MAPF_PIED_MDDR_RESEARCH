"""Independent deployment bindings, paired-budget invariance and identical-macro controls."""
from pathlib import Path
from fractions import Fraction as Q
import json,hashlib
import runner
P=runner.HERE
def trajectory(e):
 h=hashlib.sha256();gate=None;calls=0;previous=None;query_count=0;interventions=0
 for line in Path(e['raw']).open():
  r=json.loads(line);kind=r['event']
  if kind=='macro_choice':
   assert gate is None;gate=dict(r);calls+=r['inference_calls'];r={k:r[k] for k in ['event','at','opportunity','initial_capacity','features']}
  elif kind=='actor_decision':
   now=r['at'];assert previous is None or now!=previous,'same-event compensation/reselection';previous=now
   assert r['remaining_capacity']==e['capacity']-query_count
   if r['selected_kind']=='QUERY':query_count+=1
   interventions+=int(r['intervention_index']>0)
   for key in ['policy','decision_mode','macro','intervention_index','pair_stage','anchor_agent','anchor_move','anchor_tasks','second_eligible','head_lineage_count']:r.pop(key)
   for c in r['candidates']:c.pop('score');c.pop('skip_score')
  elif kind=='joint_summary':r.pop('policy');r.pop('native_checks')
  h.update(json.dumps(r,sort_keys=True,separators=(',',':')).encode());h.update(b'\n')
 assert query_count==e['summary']['queries'] and query_count<=e['capacity'] and interventions<=2
 assert calls==(int(e['policy'] in ['full','nohistory','nobudget','tasks_only']) if gate else 0)
 return dict(hash=h.hexdigest(),gate=gate,inference_calls=calls,interventions=interventions)
def main():
 reg=json.loads((P/'REGISTRATION.json').read_text());worlds={w['name']:w for w in reg['worlds']};freeze=json.loads((P/'MODEL_FREEZE_RECEIPT.json').read_text());models=json.loads((P/'MODELS_FROZEN_BEFORE_TEST.json').read_text());test_start=json.loads((P/'TEST_START.json').read_text());fit_start=json.loads((P/'FIT_START.json').read_text());es=[json.loads(p.read_text()) for p in (P/'runs').glob('*.receipt.json')]
 assert len(es)==152 and freeze['TC_receipts']==96 and freeze['existing_test_receipts']==0
 assert freeze['model_sha256']==test_start['model_sha256']==runner.sha(P/'MODELS_FROZEN_BEFORE_TEST.json') and freeze['labels_sha256']==runner.sha(P/'TRAIN_CAL_LABELS.json')
 assert reg['frozen_unix_ns']<fit_start['unix_time_ns']<freeze['unix_time_ns']<test_start['unix_time_ns']
 assert fit_start['TC_latest_finish_ns']<fit_start['unix_time_ns']
 for name,digest in reg['frozen'].items():assert runner.sha(P/name)==digest
 grouped={};results=[];paired={};identical=0
 for e in es:
  w=worlds[e['world']];assert e['started_unix_ns']>reg['frozen_unix_ns'] and e['finished_unix_ns']>=e['started_unix_ns'];assert e['registration_sha256']==runner.sha(P/'REGISTRATION.json')
  for key in ['binary_sha256','bridge_sha256','config_sha256']:assert e[key]==reg[key]
  assert e['native_source_sha256']==reg['frozen']['joint_history_native.cpp']
  if w['split']=='test':
   assert e['started_unix_ns']>=test_start['unix_time_ns'] and e['model_artifact_sha256']==freeze['model_sha256'] and e['model_freeze_receipt_sha256']==runner.sha(P/'MODEL_FREEZE_RECEIPT.json')
   parsed={}
   for line in Path(e['input']).open():
    f=line.split()
    if f[0]=='M':parsed.setdefault(f[1],[]).append(Q(int(f[2]),int(f[3])))
   assert parsed=={k:list(map(Q,v['coefficients'])) for k,v in models['parameters'].items()},'TEST models/margin/lookup differ from frozen file'
  else:assert e['finished_unix_ns']<=fit_start['TC_latest_finish_ns'] and e['model_artifact_sha256'] is None
  z=trajectory(e);gate=z['gate'];option=gate['selected_option'] if gate else 'NO_GATE';key=(e['world'],option)
  if key in grouped:assert grouped[key]==z['hash'],'same chosen complete macro changed full public/physical trajectory';identical+=1
  else:grouped[key]=z['hash']
  if w['split']=='test' and e['policy']=='nobudget':
   signature=None if gate is None else dict(features=[x for j,x in enumerate(gate['features']) if j not in [20,22,23]],at=gate['at'],scores=gate['scores'],selected_option=option,margin=gate['margin'],margin_infinite=gate['margin_infinite'])
   if w['family_key'] in paired:assert paired[w['family_key']]==signature,'nobudget policy depends on paired B'
   else:paired[w['family_key']]=signature
  results.append(dict(world=e['world'],policy=e['policy'],selected_option=option,canonical_trajectory_sha256=z['hash'],inference_calls=z['inference_calls'],interventions=z['interventions']))
 runner.write(P/'DEPLOYMENT_AUDIT.json',dict(passed=True,episodes=len(es),same_macro_full_trajectory_controls=identical,paired_nobudget_families=len(paired),source_and_model_temporal_hash_bindings=True,only_one_macro_choice=True,checks=results));print('deployment bindings/full macro controls PASS',len(es),identical,flush=True)
if __name__=='__main__':main()
