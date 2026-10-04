"""Corrupt selected records to ensure gate, STOP, budget and certificate checks reject."""
from pathlib import Path
import json,tempfile,copy,time
import runner,audit
P=runner.HERE
def main():
 reg=json.loads((P/'REGISTRATION.json').read_text());w=reg['train_worlds'][0]
 e=json.loads((P/'runs'/(w['name']+'__macro_STOP.receipt.json')).read_text());out=[]
 cases=[('gate_feature','macro_choice','independent ten public late target features'),('gate_choice','macro_choice','late score/margin C tie'),('stop_action','actor_decision','independent END actor selection'),('budget','actor_decision','causal history/capacity count'),('certificate','certified_POSITION_committed','independent source release')]
 for name,event,expected in cases:
  reached=False;changed=False
  with tempfile.TemporaryDirectory(prefix='r16-negative-') as tmp:
   path=Path(tmp)/'corrupt.jsonl'
   with path.open('w') as f:
    for line in Path(e['raw']).open():
     row=json.loads(line)
     if row['event']=='macro_choice':reached=True
     eligible=row['event']==event and (reached or name=='certificate')
     if eligible:
      before=copy.deepcopy(row)
      if name=='gate_feature':row['features'][0]='999'
      elif name=='gate_choice':row['selected_option']='C'
      elif name=='stop_action':row['selected_kind']='QUERY';row['selected']=row['candidates'][0]['move']
      elif name=='budget':row['remaining_capacity']-=1
      elif name=='certificate':row['removed']=['not-a-real-cell']
      changed=True
     f.write(json.dumps(row)+'\n')
     if changed:break
   assert changed
   corrupt=dict(e,raw=str(path))
   try:audit.audit(corrupt)
   except AssertionError as exc:
    assert expected in str(exc),(name,repr(exc));out.append(dict(case=name,rejected=True,reason=str(exc),original_record=before,mutated_record=row))
   else:raise AssertionError('corruption accepted '+name)
 runner.write(P/'NEGATIVE_CONTROLS.json',dict(passed=True,source_sha256=runner.sha(Path(__file__)),source_raw_sha256=e['raw_sha256'],native_runs_added=0,cases=out,finished_unix_ns=time.time_ns()))
 print('negative controls all rejected',len(out),flush=True)
if __name__=='__main__':main()
