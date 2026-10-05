"""Independent public-cut/label and macro-score check; no scorer import."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
import gzip
import json
import hashlib
from collections import defaultdict
from datetime import datetime,timezone
import numpy as np
from independent_math import evaluate_position,evaluate_end,history_summary


def read(p):return json.loads(Path(p).read_text())


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    result=read(HERE/'RESULTS.json');sources=read(HERE/'SOURCES.json');model=read(HERE.parent/'MODEL.json');end=read(HERE.parent/'PINNED_END_MODEL.json')
    raw={};checked=0;metric_checks=0;max_delta=0.;count=0
    for source in sources:
        directory=Path(source['directory']);assert sha(directory/'episode.json')==source['episode_sha256']
        assert sha(source['receipt'])==source['receipt_sha256']
        ep=read(directory/'episode.json');assert read(source['receipt'])['spec']['arm']=='learned_linear_structural'
        starts={(e['agent'],e['vertex']):e['time'] for e in ep['events'] if e['kind']=='START'}
        ends={(e['agent'],e['vertex']):e['time'] for e in ep['events'] if e['kind']=='END'}
        raw[source['world']]=(ep,starts,ends)
    for cohort in ['capture','delivery','consumer']:
        with gzip.open(HERE/(cohort.upper()+'_PREDICTIONS.jsonl.gz'),'rt') as f:rows=[json.loads(line) for line in f]
        groups=defaultdict(lambda:defaultdict(list))
        for row in rows:
            world,aid,uid,qtext,*_=row['key'].split('|');assert world==row['world']
            ep,starts,ends=raw[world];q=ep['queries'][int(qtext[1:])];ctx=row['context'];pos=ctx['position'];time=row['time']
            assert (q['agent'],q['vertex'])==(aid,uid) and ctx['occurrence_id']==pos['occurrence_id']==uid
            assert abs(row['actual']-(ends[(aid,uid)]-time))<1e-8 and row['actual']>0
            assert abs(ctx['elapsed']-(time-starts[(aid,uid)]))<1e-8
            assert abs(pos['captured_elapsed']-(q['captured']-starts[(aid,uid)]))<1e-8
            assert abs(pos['age']-(time-q['captured']))<1e-8 and pos['progress']==q['progress']
            h=[v for v in ep['delivered_end_history'][aid] if v['delivered']<=q['captured']+1e-8]
            assert ctx['completed_history']==h and all(v['vertex']!=uid for v in h)
            if cohort=='capture':assert time==q['captured'] and pos['delivered_age']==0.
            else:assert q['delivery_status']=='accepted' and q['delivered_at']<=time+1e-8 and abs(pos['delivered_age']-(q['delivered_at']-q['captured']))<1e-8
            if cohort=='delivery':assert time==q['delivered_at']
            s=history_summary(h);n=ctx['nominal_duration'];e=pos['captured_elapsed'];a=pos['age'];p=pos['progress']
            predicted={'position_learned':evaluate_position(ctx,model)['remaining_time'],
                'position_constant':evaluate_position(ctx,model,True)['remaining_time'],
                'history_linear':max(0.,(1-p)*n*s['all_history']-a),
                'ewma_linear':max(0.,(1-p)*n*s['ewma03']-a),
                'end_learned':evaluate_end(end,h,n,e+a,'learned'),
                'end_ewma_survival':evaluate_end(end,h,n,e+a,'ewma03_survival')}
            predicted['observed_average']=max(0.,e*(1-p)/p-a) if p>1e-6 else predicted['end_ewma_survival']
            for mode,v in predicted.items():
                delta=abs(row['predictions'][mode]-v);assert delta<1e-8*max(1.,abs(v));max_delta=max(max_delta,delta);count+=1
            groups[row['family']][world].append(row);checked+=1
        # Different aggregation implementation: equal explicit row weights,
        # checked against both world/family reports and the overall result.
        cohorts=[('metrics',rows)]
        for family,worlds in groups.items():cohorts.append(('per_family/'+family,[r for values in worlds.values() for r in values]))
        for family,worlds in groups.items():
            for world,values in worlds.items():cohorts.append(('per_world/'+world,values))
        for key,records in cohorts:
            group_worlds=defaultdict(set);counts=defaultdict(int)
            for r in records:group_worlds[r['family']].add(r['world']);counts[r['world']]+=1
            if not records:continue
            w=np.asarray([1/len(group_worlds)/len(group_worlds[r['family']])/counts[r['world']] for r in records])
            table=result[cohort]['metrics'] if key=='metrics' else result[cohort][key.split('/')[0]][key.split('/')[1]]
            for mode,score in table.items():
                err=np.asarray([r['predictions'][mode]-r['actual'] for r in records])
                for metric,v in [('mae',float(w@abs(err))),('mse',float(w@(err*err))),('bias',float(w@err))]:
                    assert abs(score[metric]-v)<1e-10;metric_checks+=1
                assert score['rows']==len(records) and score['families']==len(group_worlds) and score['worlds']==len(counts)
    report=dict(schema='r20-secondary-independent-score-check-v1',passed=True,verified_utc=datetime.now(timezone.utc).isoformat(),
        source_worlds=len(sources),row_cut_and_label_checks=checked,predictions_recomputed=count,
        max_prediction_difference=max_delta,macro_metric_checks=metric_checks,
        scorer_imported=False,trainer_imported=False,engine_imported=False,new_training_runs=0,new_solver_or_physical_episodes=0,
        source_manifest_sha256=sha(HERE/'SOURCES.json'),results_sha256=sha(HERE/'RESULTS.json'),checker_sha256=sha(__file__))
    (HERE/'INDEPENDENT_CHECK.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n');print(json.dumps(report,indent=2))


if __name__=='__main__':main()
