"""Independent complete raw-state prefix identity before any macro consequence label."""
from pathlib import Path
import json,hashlib
import runner
P=runner.HERE
def prefix(e,budget_neutral=False):
 records=[];gate=None
 for line in Path(e['raw']).open():
  r=json.loads(line)
  if r['event']=='macro_choice':gate=r;break
  r.pop('policy',None)
  if r['event']=='joint_summary':r.pop('native_checks',None)
  if budget_neutral:
   for key in ['capacity','remaining_capacity','initial_capacity']:r.pop(key,None)
  records.append(r)
 return records,gate
def main():
 reg=json.loads((P/'REGISTRATION.json').read_text());checks=[];paired={}
 for w in reg['worlds']:
  if w['split']=='test':continue
  reference=None;reference_gate=None
  for option in reg['options']:
   e=json.loads((P/'runs'/(w['name']+'__macro_'+option+'.receipt.json')).read_text());assert e['error'] is None;assert runner.sha(e['raw'])==e['raw_sha256'];records,gate=prefix(e)
   signature={k:gate[k] for k in ['at','opportunity','initial_capacity','features']} if gate else None
   if reference is None:reference=records;reference_gate=signature
   else:assert records==reference and signature==reference_gate,'complete macro physical/public prefix mismatch'
  neutral,gate=prefix(json.loads((P/'runs'/(w['name']+'__macro_C.receipt.json')).read_text()),True)
  nongate=None if gate is None else (gate['at'],gate['opportunity'],[v for j,v in enumerate(gate['features']) if j not in [20,22,23]])
  if w['family_key'] in paired:assert paired[w['family_key']]==(neutral,nongate),'paired B8/B16 nonbudget prefix/features differ'
  else:paired[w['family_key']]=(neutral,nongate)
  checks.append(dict(world=w['name'],prefix_records=len(reference),gate_present=gate is not None,canonical_prefix_sha256=hashlib.sha256(json.dumps(reference,sort_keys=True).encode()).hexdigest()))
 runner.write(P/'PREFIX_BEFORE_FIT.json',dict(passed=True,world_budget_contexts=len(checks),independent_families=len(paired),complete_physical_public_prefix=True,paired_nonbudget_features_exact=True,checks=checks));print('complete common prefixes PASS',len(checks),flush=True)
if __name__=='__main__':main()
