#!/usr/bin/env python3
"""TRAIN-only post-fit support diagnostics; never refits or selects a policy."""
from collections import defaultdict
import hashlib
import json
from pathlib import Path


def main():
    root=Path(__file__).resolve().parent.parent
    read=lambda p:json.loads(p.read_text())
    rows=read(root/'training/LABELS.json');pairs=read(root/'training/PAIRS.json')
    model=read(root/'MODEL_FROZEN.json');selection=read(root/'training/GROUPED_MODEL_SELECTION.json')
    assert all(r['split']=='TRAIN' for r in rows)
    grouped=defaultdict(list)
    for row in rows:grouped[row['family']].append(row['value'])
    families={f:{'rows':len(v),'zero_prediction_mse':sum(x*x for x in v)/len(v),
        'aggregation_weight':1/len(grouped)} for f,v in sorted(grouped.items())}
    zero_mse=sum(v['zero_prediction_mse'] for v in families.values())/len(families)
    chosen=next(v for v in selection['candidates'] if v['alpha']==model['alpha'])
    frozen_mse=sum(f['mse'] for f in chosen['folds'])/len(chosen['folds'])
    assert abs(frozen_mse-chosen['family_mean_mse'])<1e-10
    complete=[]
    for pair in pairs:
        if abs(pair.get('value',0))<=1e-8:continue
        arms=[]
        for key in ('noquery_episode','query_episode'):
            e=read(root/pair[key]);arms.append({k:e[k] for k in ('status','completed_agents','restricted_sum_completion','makespan','query_count','solver_calls')})
        complete.append({'pair_id':pair['pair_id'],'value':pair['value'],'noquery':arms[0],'query':arms[1]})
    report={'training_pairs':len(pairs),'zero_labels':sum(abs(r['value'])<=1e-8 for r in rows),
        'nonzero_complete_outcomes':complete,'labels_sha256':hashlib.sha256((root/'training/LABELS.json').read_bytes()).hexdigest(),
        'model_sha256':hashlib.sha256((root/'MODEL_FROZEN.json').read_bytes()).hexdigest(),
        'post_fit_diagnostic_only':True,'no_refit_or_new_episodes':True,
        'zero_prediction_reference':{'families':families,'family_mean_mse':zero_mse,
            'row_mean_mse':sum(r['value']**2 for r in rows)/len(rows),
            'all_families_same_size':len({x['rows'] for x in families.values()})==1,
            'frozen_alpha':model['alpha'],'frozen_selected_LOFO_family_mean_mse':frozen_mse,
            'frozen_minus_zero_mse':frozen_mse-zero_mse,
            'used_for_model_selection':False,'is_external_algorithm':False,'is_executed_policy':False,
            'scope':'Pure TRAIN post-fit diagnostic against always predicting value zero. It neither retunes the frozen model nor establishes policy performance.'}}
    (root/'review/LEARNING_SUPPORT.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(json.dumps(report['zero_prediction_reference'],indent=2))


if __name__=='__main__':main()
