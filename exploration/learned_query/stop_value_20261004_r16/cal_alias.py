"""Source-qualified C8 -> STOP16 alias; never fabricate native STOP16 records."""
from pathlib import Path
from fractions import Fraction as Q
from concurrent.futures import ThreadPoolExecutor,ProcessPoolExecutor
from collections import Counter
import json,hashlib,copy,time,sys
import runner,analyze,learn,pipeline
P=runner.HERE
EXCLUDE={'macro_choice','actor_decision','joint_summary'}
def digest(rows):
 h=hashlib.sha256()
 for r in rows:h.update((json.dumps(r,sort_keys=True,separators=(',',':'))+'\n').encode())
 return h.hexdigest()
def raw(path):
 with Path(path).open() as f:
  for line in f:yield json.loads(line)
def inspect(c8,c16):
 prefix16=[];gate=None;actor16=None;before_queries=[]
 for r in raw(c16['raw']):
  if r['event']=='macro_choice':gate=r;continue
  if gate:
   if r['event']=='actor_decision':actor16=r;break
   raise AssertionError('gate not followed by same actor call')
  if r['event'] not in EXCLUDE:prefix16.append(r)
  if r['event']=='certified_POSITION_committed':before_queries.append(r)
 assert gate and gate['spent']==8 and gate['remaining_capacity']==8 and len(before_queries)==8
 source_prefix=[];actor8=None;source_queries=[];after_counts=Counter();at_gate=False
 for r in raw(c8['raw']):
  kind=r['event']
  if not at_gate and kind not in EXCLUDE:
   source_prefix.append(r)
   if len(source_prefix)==len(prefix16):at_gate=True
  elif at_gate:after_counts[kind]+=1
  if kind=='certified_POSITION_committed':source_queries.append(r)
  if at_gate and kind=='actor_decision' and actor8 is None:actor8=r
 assert source_prefix==prefix16 and source_queries==before_queries
 assert actor8 and actor8['remaining_capacity']==0 and actor8['selected_kind']=='WAIT' and not actor8['selected']
 for k in ['at','opportunity','trigger','RR_cursor','END_only_known','END_unknown','private_progress_input','regime_input','future_head_input']:
  assert actor8[k]==actor16[k],k
 assert len(actor8['candidates'])==len(actor16['candidates'])
 for a,b in zip(actor8['candidates'],actor16['candidates']):
  for k in ['move','agent','heading','public_launch','probability','claims']:assert a[k]==b[k],k
  assert all(a['features'][i]==b['features'][i] for i in range(24) if i not in [20,22,23])
 assert after_counts['certified_POSITION_committed']==after_counts['public_SKIP_installed']==0
 return dict(physical_public_prefix_sha256=digest(prefix16),prefix_records=len(prefix16),first8_position_sha256=digest(before_queries),gate=gate,after_gate_source_events=dict(after_counts),nonbudget_candidate_features_equal=True,full_input_equal=c8['input_sha256']==c16['input_sha256'],source_query_count=len(source_queries),source_gate_actor_sha256=digest([actor8]),target_gate_actor_sha256=digest([actor16]))
def register():
 reg=json.loads((P/'REGISTRATION.json').read_text());model=json.loads((P/'MODEL_FROZEN.json').read_text());assert model['activated']
 train=json.loads((P/'BUDGET_ALIAS_OBSERVATION.json').read_text());assert train['all_equal'] and len(train['checks'])==12
 for n,h in reg['frozen'].items():assert runner.sha(P/n)==h
 worlds=reg['cal_worlds'];checks=[]
 for family in sorted({w['family_key'] for w in worlds}):
  a=next(w for w in worlds if w['family_key']==family and w['budget']==8);b=next(w for w in worlds if w['family_key']==family and w['budget']==16)
  c8=runner.cached_c(a);c16=runner.cached_c(b);assert c8['summary']['queries']==8
  proof=inspect(c8,c16);assert proof['full_input_equal']
  ap=runner.OLD/'audits'/(a['name']+'__macro_C.receipt.audit.json');assert json.loads(ap.read_text())['status']=='passed'
  checks.append(dict(source_world=a['name'],target_world=b['name'],source_policy='macro_C',target_policy='macro_STOP_semantic_alias',source_raw_sha256=c8['raw_sha256'],source_receipt_sha256=runner.sha(runner.OLD/'runs'/(a['name']+'__macro_C.receipt.json')),source_audit_sha256=runner.sha(ap),target_gate_raw_sha256=c16['raw_sha256'],target_gate_receipt_sha256=runner.sha(runner.OLD/'runs'/(b['name']+'__macro_C.receipt.json')),**proof))
 runner.write(P/'CAL_ALIAS_REGISTRATION.json',dict(frozen_unix_ns=time.time_ns(),amendment_sha256=runner.sha(P/'CAL_ALIAS_AMENDMENT.md'),alias_source_sha256=runner.sha(Path(__file__)),original_registration_sha256=runner.sha(P/'REGISTRATION.json'),model_frozen_sha256=runner.sha(P/'MODEL_FROZEN.json'),train_equivalence_sha256=runner.sha(P/'BUDGET_ALIAS_OBSERVATION.json'),new_native=3,aliases=3,checks=checks))
 print('CAL alias qualification passed for all three families; registered 3 new B8 STOP',flush=True)
def execute():
 ar=json.loads((P/'CAL_ALIAS_REGISTRATION.json').read_text());assert runner.sha(Path(__file__))==ar['alias_source_sha256'];assert runner.sha(P/'MODEL_FROZEN.json')==ar['model_frozen_sha256']
 reg=json.loads((P/'REGISTRATION.json').read_text());worlds=reg['cal_worlds'];jobs=[w for w in worlds if w['budget']==8]
 runner.write(P/'CAL_START.json',dict(started_unix_ns=time.time_ns(),alias_registration_sha256=runner.sha(P/'CAL_ALIAS_REGISTRATION.json'),new_native=[w['name'] for w in jobs],semantic_aliases=[x['target_world'] for x in ar['checks']]))
 with ThreadPoolExecutor(max_workers=3) as pool:results=list(pool.map(lambda w:runner.native(w,'macro_STOP','CAL'),jobs))
 assert all(e['error'] is None for e in results)
 with ProcessPoolExecutor(max_workers=2) as pool:
  for a in pool.map(pipeline.perform_audit,[str(P/'runs'/(e['world']+'__macro_STOP.receipt.json')) for e in results]):print('CAL audit passed',a['world'],flush=True)
 pairs=[]
 for w in worlds:
  ce=runner.cached_c(w);c=analyze.outcome(w,ce)
  if w['budget']==8:
   se=json.loads((P/'runs'/(w['name']+'__macro_STOP.receipt.json')).read_text());s=analyze.outcome(w,se);r=analyze.pair(w,c,s)
  else:
   proof=next(x for x in ar['checks'] if x['target_world']==w['name']);sw=next(x for x in worlds if x['name']==proof['source_world']);source=runner.cached_c(sw);assert source['raw_sha256']==proof['source_raw_sha256'];s=analyze.outcome(sw,source)
   original_gate=s['gate'];s.update(world=w['name'],budget=16,remaining_budget=16-s['queries'],policy='macro_STOP_semantic_alias',gate=c['gate'],prefix_sha256=None,gate_source_policy='macro_C_B16',source_gate=original_gate,semantic_choice='STOP',stop_decisions=None,after_gate_events=proof['after_gate_source_events'],semantic_alias=dict(source_world=sw['name'],source_policy='macro_C',source_budget=8,source_raw=source['raw'],source_raw_sha256=source['raw_sha256'],source_receipt_sha256=proof['source_receipt_sha256'],target_gate_raw_sha256=proof['target_gate_raw_sha256'],alias_registration_sha256=runner.sha(P/'CAL_ALIAS_REGISTRATION.json'),physical_public_prefix_sha256=proof['physical_public_prefix_sha256']))
   r=dict(world=w['name'],family_key=w['family_key'],map=w['map_name'],split=w['split'],budget=16,delta_tasks=s['tasks']-c['tasks'],T_gain_lower=str(Q(c['T_lower'])-Q(s['T_upper'])),T_gain_upper=str(Q(c['T_upper'])-Q(s['T_lower'])),queries_saved=c['queries']-s['queries'],gate=c['gate'],C=c,STOP=s,prefix_equal=True,prefix_equality_scope='source-proved physical/public budget-metadata projection; not identical actor logs',input_equal=True,semantic_alias=proof)
  pairs.append(r)
 runner.write(P/'CAL_PAIRS.json',pairs);runner.write(P/'CAL_SUMMARY.json',analyze.summarize(pairs))
 model=json.loads((P/'MODEL_FROZEN.json').read_text());selections=[dict(world=r['world'],selected=learn.choose(model,r['gate']),selected_raw_sha256=r[learn.choose(model,r['gate'])]['raw_sha256'],selected_is_semantic_alias='semantic_alias' in r[learn.choose(model,r['gate'])]) for r in pairs]
 runner.write(P/'CAL_SELECTIONS.json',dict(model_sha256=runner.sha(P/'MODEL_FROZEN.json'),selections=selections,total=analyze.total([r[learn.choose(model,r['gate'])] for r in pairs]),fixed_C=analyze.total([r['C'] for r in pairs]),fixed_STOP=analyze.total([r['STOP'] for r in pairs]),no_CAL_tuning=True,new_native=3,semantic_aliases=3))
 print('CAL completed 3 native + 3 certified semantic aliases',flush=True)
if __name__=='__main__':register() if sys.argv[1]=='register' else execute()
