"""Frozen R20 predictions on consumed R19 trajectories; descriptive only."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
import json
from datetime import datetime,timezone
from collections import Counter
import numpy as np
import study
from position_predictor import MODES
from independent_math import evaluate_position,evaluate_end,make_context,history_summary


def main():
    root=Path('/home/lyh/MAPF_LMAPF_ERROR_GUIDANCE_EXPLORE/exploration/error_guidance/sadg_structural_20261005_r19')
    paths=sorted((root/'episodes').glob('*/learned_structural/episode.json'))
    c,d,k,s=study.extract(paths,source_split='CONSUMED_R19_DEVELOPMENT')
    assert len(paths)==42
    model=json.loads((HERE.parent/'MODEL.json').read_text());end=json.loads((HERE.parent/'PINNED_END_MODEL.json').read_text())
    assert study.sha(HERE.parent/'MODEL.json')==json.loads((HERE/'REGISTRATION.json').read_text())['model_sha256']
    study.HERE=HERE
    study.save('SOURCES.json',s)
    outputs={};max_error=0.;recomputed=0
    for cohort in ['core','scale_N64']:
        outputs[cohort]={}
        for name,records in [('capture',c),('delivery',d),('consumer',k)]:
            records=[r for r in records if ('__n64__' in r['world'])==(cohort=='scale_N64')]
            out=[]
            for r in records:
                pred={mode:study.predict(model,end,mode,r) for mode in MODES}
                ctx=make_context(r);stats=history_summary(r['history']);p=r['progress'];n=r['nominal'];e=r['capture_elapsed'];a=r['age']
                independent={'position_learned':evaluate_position(ctx,model)['remaining_time'],
                    'position_constant':evaluate_position(ctx,model,True)['remaining_time'],
                    'history_linear':max(0.,(1-p)*n*stats['all_history']-a),
                    'ewma_linear':max(0.,(1-p)*n*stats['ewma03']-a),
                    'end_learned':evaluate_end(end,r['history'],n,e+a,'learned'),
                    'end_ewma_survival':evaluate_end(end,r['history'],n,e+a,'ewma03_survival')}
                independent['observed_average']=max(0.,e*(1-p)/p-a) if p>1e-6 else independent['end_ewma_survival']
                for mode in MODES:
                    err=abs(pred[mode]-independent[mode]);assert err<1e-6*max(1.,abs(independent[mode]));max_error=max(max_error,err);recomputed+=1
                out.append(dict(key=r['key'],world=r['world'],family=r['family'],actual=r['remaining'],
                    predictions=pred,nominal=n,progress=p,capture_elapsed=e,observation_age=a))
            study.save_rows(cohort.upper()+'_'+name.upper()+'.jsonl.gz',out)
            outputs[cohort][name]={mode:study.metrics(records,[r['predictions'][mode] for r in out]) for mode in MODES}
            outputs[cohort][name+'_worlds']={world:{mode:study.metrics([r for r in records if r['world']==world],
                [r['predictions'][mode] for r in out if r['world']==world]) for mode in MODES} for world in sorted({r['world'] for r in records})}
    outputs.update(scope='Consumed R19 development diagnostics, no tuning or new TEST claim',canonical_arm='learned_structural',
        source_worlds=42,source_families=dict(Counter(z['family'] for z in s)),
        source_captures=len(c),accepted_deliveries=len(d),actual_consumers=len(k),
        independent_prediction_recomputations=recomputed,max_independent_prediction_difference=max_error,
        model_sha256=study.sha(HERE.parent/'MODEL.json'),new_training_runs=0,new_physical_or_solver_episodes=0,
        scored_utc=datetime.now(timezone.utc).isoformat())
    study.save('RESULTS.json',outputs)
    print(json.dumps({cohort:{name:outputs[cohort][name] for name in ['capture','delivery','consumer']} for cohort in ['core','scale_N64']},indent=2))


if __name__=='__main__':main()
