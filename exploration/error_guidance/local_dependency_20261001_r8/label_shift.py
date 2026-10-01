from pathlib import Path
import json,statistics,collections
H=Path(__file__).resolve().parent;O=Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence')/H.name
from public_model import nominal,predict
model=json.loads((H/'model_freeze.json').read_text());groups=collections.defaultdict(list)
for s in json.loads((H/'runs.json').read_text())['runs']:
 if s['split']!='test' or s['policy']!='hm':continue
 rs=json.loads((O/'runs'/s['id']/'supervised_rows.json').read_text())['rows'];lookup={(r['proposal_id'],r['agent'],r['logical_step']):r for r in rs}
 for r in rs:
  v=dict(r);prev=lookup.get((r['proposal_id'],r['agent'],0)) if r['logical_step']==1 else None
  v['previous_move_prefix_ticks']=prev['duration'] if prev else 0
  v['after_previous_MOVE_END_ticks']=r['duration']-v['previous_move_prefix_ticks'];groups[(s['execution'],r['logical_step'])].append(v)
result={}
for (mode,step),rs in groups.items():
 d={'n':len(rs),'mean_batch_to_END':statistics.mean(r['duration'] for r in rs),'mean_actual_nominal':statistics.mean(nominal(r['turns']) for r in rs),'mean_batch_residual':statistics.mean(r['duration']-nominal(r['turns']) for r in rs),'mean_previous_MOVE_prefix_ticks':statistics.mean(r['previous_move_prefix_ticks'] for r in rs),'mean_after_previous_MOVE_END_ticks':statistics.mean(r['after_previous_MOVE_END_ticks'] for r in rs),'mean_feature_recent_history_residual':statistics.mean(r['features'][6]*50 for r in rs)}
 for p in ['history','learned']:
  er=[predict(r['features'],r['turns'],p,model['ridge'])-r['duration'] for r in rs];d[p]={'MAE':statistics.mean(abs(x) for x in er),'bias':statistics.mean(er)}
 result[mode+'_step'+str(step)]=d
(H/'label_shift.json').write_text(json.dumps({'posthoc_diagnostic':True,'same_original_hm_event_rows_for_both_predictors':True,'groups':result,'after_previous_MOVE_END_not_used_to_train_or_act':True,'warning':'second-step cumulative duration enters history as if a single move; domain and target mismatch, not pure motor residual'},indent=2)+'\n');print(json.dumps(result,indent=2))
