"""Readable artifacts and provenance after registered execution; no selection tuning."""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
import csv,json,time
import runner,analyze,learn
P=runner.HERE
def num(q):return f'{float(Q(q)):.6f}'
def main():
 reg=json.loads((P/'REGISTRATION.json').read_text());model=json.loads((P/'MODEL_FROZEN.json').read_text())
 for n,h in reg['frozen'].items():assert runner.sha(P/n)==h
 pairs=json.loads((P/'TRAIN_PAIRS.json').read_text());cal=json.loads((P/'CAL_PAIRS.json').read_text()) if model['activated'] else []
 if model['activated']:assert len(cal)==6
 raw=[];receipts=[]
 for p in sorted((P/'runs').glob('*.receipt.json')):
  e=json.loads(p.read_text());assert e['error'] is None and e['registration_sha256']==runner.sha(P/'REGISTRATION.json')
  assert e['native_source_sha256']==reg['frozen']['joint_history_native.cpp'] and e['binary_sha256']==reg['binary_sha256']
  assert e['started_unix_ns']>reg['frozen_unix_ns']
  if e['stage']=='CAL':assert e['model_frozen_sha256']==runner.sha(P/'MODEL_FROZEN.json') and e['started_unix_ns']>model['frozen_unix_ns']
  for k in ['input','raw','planner']:assert runner.sha(e[k])==e[k+'_sha256']
  ap=P/'audits'/(p.stem+'.audit.json');a=json.loads(ap.read_text());assert a['status']=='passed'
  receipts.append(dict(receipt=str(p),receipt_sha256=runner.sha(p),world=e['world'],policy=e['policy'],stage=e['stage'],audit=str(ap),audit_sha256=runner.sha(ap),started_unix_ns=e['started_unix_ns'],finished_unix_ns=e['finished_unix_ns'],host_seconds=e['seconds'],**{k:e[k] for k in ['input_sha256','raw_sha256','planner_sha256','native_source_sha256','binary_sha256']}))
 aliases=sum('semantic_alias' in r for r in cal)
 assert len(receipts)==26+(len(cal)-aliases if model['activated'] else 0)
 reused=[]
 for w in reg['train_worlds']+(reg['cal_worlds'] if model['activated'] else []):
  e=runner.cached_c(w);ap=runner.OLD/'audits'/(w['name']+'__macro_C.receipt.audit.json');a=json.loads(ap.read_text());assert a['status']=='passed' and a['world']==w['name']
  reused.append(dict(world=w['name'],original_audit=str(ap),original_audit_sha256=runner.sha(ap),raw_sha256=e['raw_sha256']))
 for r in pairs+cal:
  for arm in ['C','STOP']:
   o=r[arm];raw.append(dict(world=r['world'],family_key=r['family_key'],split=r['split'],budget=r['budget'],arm=arm,reused=arm=='C' or 'semantic_alias' in o,semantic_alias='semantic_alias' in o,tasks=o['tasks'],T_lower=o['T_lower'],T_upper=o['T_upper'],queries=o['queries'],remaining_budget=o['remaining_budget'],host_seconds=o['host_seconds'],raw_sha256=o['raw_sha256'],planner_sha256=o['planner_sha256'],input_sha256=o['input_sha256']))
 with (P/'RESULTS.csv').open('x') as f:
  w=csv.DictWriter(f,fieldnames=list(raw[0]));w.writeheader();w.writerows(raw)
 runner.write(P/'ARM_HASHES.json',dict(new=receipts,reused_C=reg['reused_C'],used_old_C_audits=reused))
 families=[]
 for key in sorted({r['family_key'] for r in pairs+cal}):
  rr=[r for r in pairs+cal if r['family_key']==key];families.append(dict(family_key=key,split=rr[0]['split'],C=analyze.total([r['C'] for r in rr]),STOP=analyze.total([r['STOP'] for r in rr]),delta_tasks=sum(r['delta_tasks'] for r in rr),T_gain_lower=str(sum((Q(r['T_gain_lower']) for r in rr),Q(0))),T_gain_upper=str(sum((Q(r['T_gain_upper']) for r in rr),Q(0))),queries_saved=sum(r['queries_saved'] for r in rr)))
 runner.write(P/'FAMILY_RESULTS.json',families)
 train=analyze.summarize(pairs);lines=['# R16 C/STOP complete-tail exploration report','',f"Completed {len(receipts)} new native runs, including 2 necessary C binary-compatibility checks. Reused {len(pairs)+len(cal)} exact old C outcomes plus {aliases} explicitly registered STOP semantic aliases (pointing to existing C8, not additional raw runs). TRAIN is 12 old families × 2 budgets; no old TEST opened. CAL is {len(cal)//2} preregistered old families with a new STOP action. This is developmental evidence, not a new final test.",'', '| Split/arm | FIFO tasks | Restricted T interval | Queries |', '|---|---:|---:|---:|']
 for label,pp in [('TRAIN',pairs),('CAL',cal)]:
  if not pp:continue
  for arm in ['C','STOP']:
   t=analyze.total([r[arm] for r in pp]);lines.append(f"| {label} {arm} | {t['tasks']} | [{num(t['T_lower'])}, {num(t['T_upper'])}] | {t['queries']} |")
 if cal:
  selections=json.loads((P/'CAL_SELECTIONS.json').read_text());t=selections['total'];lines.append(f"| CAL learned | {t['tasks']} | [{num(t['T_lower'])}, {num(t['T_upper'])}] | {t['queries']} |")
 lines+=['',f"TRAIN material preferences (task first; ≥1 second for equal-task time): {model['preferences']}. Tree activation: {model['activated']}. All labels and neutral or harmful contexts remain in TRAIN_PAIRS.json. Budget settings are paired within family, not independent replicates.",'','## Mechanism and validation','',f"All {len(pairs)+len(cal)-aliases} native C/STOP contexts have identical complete pre-gate physical/public prefixes and exact gate features. The {aliases} CAL B16 aliases instead have source-proved equality after projecting budget-only actor metadata; they keep the real C16 gate and real C8 source logs. No fictitious native STOP16 log is generated. Every STOP tail retains the ordinary controller and FIFO through H=128; it sends zero post-gate POSITION or SKIP. Normal END, MOVE launch and FIFO task service continue after the gate. Query counts are B/2, leaving half the registered budget unused. All new runs pass the original independent Decimal controller, ownership/collision, END/history and FIFO audit. Old C audit evidence is linked in ARM_HASHES.json.",'','Both new C compatibility raw logs are byte-for-byte identical to old C. Planner results match after excluding only host `planner_us`; the initial overstrict hash assertion and analysis-only amendment are preserved. No native run was repeated to resolve this analysis failure. All frozen scientific sources still match REGISTRATION.json.','', 'Restricted T uses each agent’s fixed first four FIFO tasks and assigns H to unfinished tasks. Raw all-service ΣT and released-head restricted flow sums are retained separately. Query count is the only unit-cost proxy; no monetary tariff or production COST was supplied. Host runtime is separate from simulated time.','', '## Waiting decomposition','', '| TRAIN arm | Physical MOVE occupancy | END feedback hold | Residual not-moving time |','|---|---:|---:|---:|']
 for arm in ['C','STOP']:
  t=train[arm];vals=[f"[{num(t[k][0])}, {num(t[k][1])}]" for k in ['motion_time_interval','feedback_hold_interval','residual_not_moving_interval']];lines.append('| '+arm+' | '+' | '.join(vals)+' |')
 lines+=['','The decomposition is over 24×16×128 agent-seconds. It includes censored active MOVEs. Residual not-moving time includes readiness/resource/planner waits and is not presented as pure resource waiting. Export intervals are numeric bounds, not statistical confidence intervals.','', '## Frozen simple selector','']
 if model['activated']:
  lines+=['One depth-one tree predicts complete-tail task difference and timing gain from the ten public gate features. Exact split and leaf values are in MODEL_FROZEN.json; no CAL threshold selection or refit occurred. Single-gate decisions choose already verified complete tails, with selected raw SHA recorded in CAL_SELECTIONS.json.','', '```json',json.dumps(model['tree'],indent=2),'```']
 else:lines+=['The activation condition failed, so no model was fit and no CAL native episodes were run. Zero or fixed-direction value does not justify a larger model.']
 lines+=['','## Every development context','', '| Family / B | Δ tasks STOP−C | T gain C−STOP interval | Queries saved | Material preference |','|---|---:|---:|---:|---|']
 for r in pairs+cal:lines.append(f"| {r['family_key']} / {r['budget']} | {r['delta_tasks']} | [{num(r['T_gain_lower'])}, {num(r['T_gain_upper'])}] | {r['queries_saved']} | {learn.preference(r)} |")
 lines+=['','## Reproduction and boundaries','','Run `rtk proxy python3 pipeline.py register`, `rtk proxy python3 pipeline.py TRAIN`, then the documented `finish_train.py` analysis recovery. For the registered CAL alias amendment run `rtk proxy python3 cal_alias.py register`, `rtk proxy python3 cal_alias.py run`, and `rtk proxy python3 close.py`. Existing output paths intentionally refuse overwrite; reproduce in a new sibling experiment directory with a fresh receipt contract. Do not rerun in this completed directory.','', 'C/STOP are internal diagnostic strategies, not new external paper baselines. This result does not establish innovation, generalization to new map files, or production controller deployment. Mentor judgment and concrete next action are recorded in MENTOR_POSTEXEC.md.']
 (P/'REPORT.md').write_text('\n'.join(lines)+'\n')
 runner.write(P/'COMPLETION_RECEIPT.json',dict(complete=True,finished_unix_ns=time.time_ns(),new_native=len(receipts),new_STOP=len(pairs)+len(cal)-aliases,STOP_semantic_aliases=aliases,C_compatibility=2,reused_C=len(pairs)+len(cal),failed_native=0,all_frozen_sources_unchanged=True,registration_sha256=runner.sha(P/'REGISTRATION.json'),model_sha256=runner.sha(P/'MODEL_FROZEN.json'),raw_and_audits_verified=True))
 print('complete artifacts',len(receipts),'new native',len(raw),'scientific arm records',flush=True)
if __name__=='__main__':main()
