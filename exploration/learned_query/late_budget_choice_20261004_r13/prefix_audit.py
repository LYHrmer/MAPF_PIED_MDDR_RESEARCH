"""Full physical/public condition prefix equality before true late intervention."""
from pathlib import Path
import json,hashlib
import runner
P=runner.HERE
def prefix(e):
 records=[];gate=None
 for line in Path(e['raw']).open():
  r=json.loads(line)
  if r['event']=='macro_choice':gate=r;break
  r.pop('policy',None)
  if r['event']=='joint_summary':r.pop('native_checks',None)
  records.append(r)
 return records,gate
def main():
 reg=json.loads((P/'REGISTRATION.json').read_text());checks=[];families=set()
 for w in reg['worlds']:
  if w['split']=='test':continue
  reference=None;reference_gate=None
  for option in reg['options']:
   e=json.loads((P/'runs'/(w['name']+'__macro_'+option+'.receipt.json')).read_text());assert e['error'] is None;assert runner.sha(e['raw'])==e['raw_sha256'];records,gate=prefix(e)
   signature={k:gate[k] for k in ['at','opportunity','initial_capacity','remaining_capacity','spent','target_agent','target_move','features']} if gate else None
   if reference is None:reference=records;reference_gate=signature
   else:assert records==reference and signature==reference_gate,'complete C/LD condition prefix mismatch'
  families.add(w['family_key']);checks.append(dict(world=w['name'],prefix_records=len(reference),gate_present=gate is not None,canonical_prefix_sha256=hashlib.sha256(json.dumps(reference,sort_keys=True).encode()).hexdigest()))
 runner.write(P/'PREFIX_BEFORE_FIT.json',dict(passed=True,world_budget_contexts=len(checks),independent_families=len(families),complete_physical_public_prefix=True,cross_budget_gate_equality_not_assumed=True,checks=checks));print('complete late common prefixes PASS',len(checks),flush=True)
if __name__=='__main__':main()
