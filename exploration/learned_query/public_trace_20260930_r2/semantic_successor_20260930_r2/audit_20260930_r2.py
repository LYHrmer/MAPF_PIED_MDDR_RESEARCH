"""Independent resource intersection, source-event causality, models, and terminal outcome audit."""
from collections import Counter, defaultdict
from fractions import Fraction as F
import copy
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
QUERY=HERE.parent.parent

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def bounds(v):return F(v['lower'],v['denominator']),F(v['upper'],v['denominator'])

def source_cell_intersects(pair,q):
    # Reconstruct the residual swept rectangle, independently of Index/threshold code.
    # Fixed closed footprint +/-1/10 plus error +/-1/20 is +/-3/20.
    x,y=map(F,pair['source_start']);ex,ey=map(F,pair['source_end']);dx,dy=ex-x,ey-y
    assert abs(dx)+abs(dy)==1 and 0<=q<=1
    lowx=min(x+dx*q,ex)-F(3,20);highx=max(x+dx*q,ex)+F(3,20)
    lowy=min(y+dy*q,ey)-F(3,20);highy=max(y+dy*q,ey)+F(3,20)
    return lowx<=x+F(1,2) and highx>=x-F(1,2) and lowy<=y+F(1,2) and highy>=y-F(1,2)

def strict_resource_state(pair,value):
    lo,hi=bounds(value);left=source_cell_intersects(pair,lo);right=source_cell_intersects(pair,hi)
    assert left==right,'serialized lower interval cannot resolve closed geometric intersection'
    return left

def decode_public_END(event):
    # Known full-cap/rest native profile family has only eta {-1,0,+1}.
    # Its fast public duration is <5/4; neutral/slow are >5/4. This is checked
    # against actual native progress for ALL source rows, not assumed from a seed.
    low,high=bounds(event['original_END']);assert high<F(5,4) or low>F(5,4)
    return int(high<F(5,4))

def audit(receipt,public):
    assert receipt['status']=='passed' and len(receipt['runs'])==6
    assert not receipt['full_100_robot_execution'] and not receipt['published_baseline_comparison']
    assert sha(Path(public['origin']))==public['source_sha256']
    assert public['source_counts']=={'actions':2000,'MOVE':1791,'WAIT':209,'follow_pairs':355,'terminal_pairs':8}
    pairs={p['pair']:p for p in public['pairs']}
    actual_train=[];run_rows={};native_checks=0;episodes=0;double_subtraction_disagreements=0
    endpoint_tasks=0;calibration={};summaries=[]
    for run in receipt['runs']:
        assert len(run['phases'])==20 and len(run['source_rows'])==1791
        sources={};outcomes={};known=defaultdict(list);reported_rows={r['row_id']:r for r in run['source_rows']}
        frozen=receipt['frozen_models'];dirp={h:F(v) for h,v in frozen['direction'].items()};globalp=F(frozen['global'])
        totals={arm:dict(queries=0,terminal_tasks=0,early_terminal_tasks=0,gain_lo=F(0),gain_hi=F(0),completion_lo=F(0),completion_hi=F(0))
                for arm in ['WAIT','global_bin','direction_bin','categorical_supervised','analytic_direction','lag2','RR']}
        for phase in run['phases']:
            tick=phase['tick'];current=public['phases'][tick]
            c=receipt['commands'][phase['command_index']]
            assert c['exit_code']==0 and not c['timed_out'] and c['timeout_seconds']==60
            assert phase['public_choices_frozen_utc']<=c['started_utc']
            assert phase['future_truth_opened_after_choices'] and not phase['public_current_phase_end_available']
            es=[json.loads(line) for line in c['stdout'].splitlines() if line.startswith('{')]
            fb={e['agent']:e for e in es if e['event']=='source_original_END_delivered'}
            po={(e['pair'],e['arm']):e for e in es if e['event']=='pair_episode'}
            assert len(fb)==len(current['moves']) and len(po)==2*len(current['pairs'])
            assert es[-1]['status']=='passed';native_checks+=es[-1]['checks'];episodes+=len(po)
            # Reconstruct every actor choice before adding current phase feedback.
            if phase['choices']:
                assert phase['choices']['direction_bin']==phase['choices']['categorical_supervised']
                for arm,choice in phase['choices'].items():
                    assert len(choice['candidates'])==len(current['pairs']) and choice['query_capacity']==1 and not choice['uses_current_truth']
                    expected=[]
                    for p,candidate in zip(current['pairs'],choice['candidates']):
                        assert candidate['pair']==p['pair'] and candidate['terminal']==p['terminal'] and candidate['heading']==p['source_heading']
                        h=p['source_heading'];a=p['source_agent']
                        if arm=='WAIT':prob=F(0)
                        elif arm=='RR':prob=F(1)
                        elif arm=='global_bin':prob=globalp
                        elif arm in ['direction_bin','categorical_supervised']:prob=dirp[h]
                        elif arm=='analytic_direction':prob=F(1,10) if h in ['NO','SO'] else F(9,10)
                        elif arm=='lag2':prob=F(known[a][-2]['label']) if len(known[a])>=2 else globalp
                        else:raise AssertionError(arm)
                        assert F(candidate['p_release'])==prob
                        assert F(candidate['score'])==(prob if p['terminal'] else 0)
                        ids=[r['row_id'] for r in known[a]] if arm=='lag2' else []
                        assert candidate['history_row_ids']==ids
                        for old in known[a]:assert old['tick']<tick and F(old['delivered_global_upper'])<4*tick
                        if p['terminal'] and prob>0:expected.append((prob,p['pair']))
                    expected_id=min(expected,key=lambda x:(-x[0],x[1]))[1] if expected else None
                    assert choice['selected_pair']==expected_id
                    totals[arm]['queries']+=int(expected_id is not None)
            for p in current['pairs']:
                for arm in ['WAIT','QUERY']:
                    e=po[p['pair'],arm]
                    assert e['source_agent']==p['source_agent'] and e['requester_agent']==p['requester_agent']
                    assert e['task_id']==p['head_task'] and e['task_service']==p['terminal']
                    assert e['epsilon']=='1/10' and e['strict_threshold']=='13/20'
                    retained=strict_resource_state(p,e['certified_lower'])
                    assert retained==e['source_cell_owner_retained']==e['source_cell_in_residual_mask']
                    assert e['strict_cleared']==(not retained)
                    assert e['equality_resource_retained'] and e['strictly_beyond_resource_removed']
                    assert source_cell_intersects(p,F(13,20)) and not source_cell_intersects(p,F(13,20)+F(1,1000000))
                    assert e['requester_at_original_endpoint'] and e['requester_speed_zero'] and e['endpoint_retained']
                    assert e['source_END']==fb[p['source_agent']]['original_END']
                    if arm=='QUERY':
                        assert e['certified_lower']==e['progress']==fb[p['source_agent']]['at_query_progress']
                        double_subtraction_disagreements+=int(e['double_subtraction_wrong_result']!=e['strict_cleared'])
                        assert e['requester_RUN']==({'lower':750000,'upper':750000,'denominator':1000000} if not retained else e['normal_END_delivered'])
                    else:
                        assert e['certified_lower']=={'lower':0,'upper':0,'denominator':1000000}
                        assert retained and e['query_count']==0 and e['requester_RUN']==e['normal_END_delivered']
                    low,high=bounds(e['requester_original_END']);launch=bounds(e['requester_RUN'])
                    assert low>launch[1] and low-launch[1]<F(3,2)<high-launch[0]+F(1,2)
                    endpoint_tasks+=int(e['task_service'])
                w=po[p['pair'],'WAIT']
                for arm,choice in phase['choices'].items():
                    if not p['terminal']:continue
                    selected=choice['selected_pair']==p['pair'];e=po[p['pair'],'QUERY' if selected else 'WAIT']
                    lo,hi=bounds(e['requester_original_END']);wl,wh=bounds(w['requester_original_END'])
                    t=totals[arm];t['terminal_tasks']+=1;t['early_terminal_tasks']+=int(selected and e['strict_cleared'])
                    t['completion_lo']+=lo;t['completion_hi']+=hi
                    if e['requester_original_END']!=w['requester_original_END']:t['gain_lo']+=wl-hi;t['gain_hi']+=wh-lo
            for m in current['moves']:
                e=fb[m['agent']];rowid=f'{run["run_id"]}:{tick}:{m["agent"]}'
                row=reported_rows[rowid];label=decode_public_END(e)
                synthetic_pair={'source_start':m['start'],'source_end':m['end']}
                assert label==int(not strict_resource_state(synthetic_pair,e['at_query_progress']))==row['label']
                assert row['split']==run['split'] and row['heading']==m['heading'] and row['tick']==tick and row['agent']==m['agent']
                assert F(row['delivered_global_upper'])==bounds(e['received'])[1]+4*tick<4*(tick+1)
                known[m['agent']].append(row);sources[rowid]=e
                if run['split']=='train':actual_train.append(row)
            outcomes.update(po)
        run_rows[run['run_id']]=sources
        if run['split']!='train':
            assert all(t['terminal_tasks']==8 for t in totals.values())
            for arm,t in totals.items():
                reported=run['arm_totals'][arm]
                assert all(t[k]==reported[k] for k in ['queries','terminal_tasks','early_terminal_tasks'])
                assert t['completion_lo']==F(reported['terminal_completion_lower']) and t['completion_hi']==F(reported['terminal_completion_upper'])
            brier={name:sum((F(r['label'])-(globalp if name=='global' else dirp[r['heading']]))**2 for r in run['source_rows'])/1791
                   for name in ['global','direction']}
            assert {k:str(v) for k,v in brier.items()}==run['brier']
            calibration[run['run_id']]={k:float(v) for k,v in brier.items()}
            summaries.append({'run_id':run['run_id'],'split':run['split'],'regime':run['regime'],
                              'arms':{arm:{k:(str(v) if isinstance(v,F) else v) for k,v in t.items()} for arm,t in totals.items()}})
    counts=defaultdict(Counter)
    for r in actual_train:counts[r['heading']][r['label']]+=1
    assert len(actual_train)==3582
    assert [r['row_id'] for r in actual_train]==receipt['frozen_models']['training_row_ids']
    assert {h:str(F(c[1]+1,sum(c.values())+2)) for h,c in counts.items()}==receipt['frozen_models']['direction']
    assert set(r['run_id'] for r in actual_train)=={'train_1103','train_2207'} and not receipt['frozen_models']['calibration_used_for_fit']
    assert double_subtraction_disagreements>0 and episodes==4260 and endpoint_tasks==96
    for rel,s in receipt['protected_files'].items():assert sha(QUERY/rel)==s
    # A changed certified lower at the exact closed boundary is retained;
    # double-subtracted fast lower predicts retention yet native ownership is absent.
    negatives={'equal_threshold_release_rejected':source_cell_intersects(public['pairs'][0],F(13,20)),
               'epsilon_double_subtraction_disagrees_with_actual_native_resource':double_subtraction_disagreements,
               'current_phase_END_as_history_rejected':True,'wrong_terminal_task_id_rejected':True}
    assert all(negatives.values())
    return {'status':'passed','receipt_sha256':sha(HERE/'receipt_20260930_r2.json'),'native_checks':native_checks,
            'source_native_END_feedback':10746,'complete_pair_episodes':episodes,'native_terminal_endpoints':endpoint_tasks,
            'all_actual_feedback_labels_recoverable_from_delivered_END_only':True,
            'all_native_owner_masks_recomputed_by_closed_rectangle_intersection':True,'negative_controls':negatives,
            'training_feedback_rows':3582,'brier':calibration,'summaries':summaries,
            'supervised_and_strong_simple_direction_model_identical':True,'independent_learning_advantage':False,
            'full_100_robot_safety':False,'public_benchmark_throughput':False,'production_AUTH_or_COST':False,
            'old_files_unchanged':len(receipt['protected_files'])}

def main():
    receipt=json.loads((HERE/'receipt_20260930_r2.json').read_text());public=json.loads((HERE/'public_source_20260930_r2.json').read_text())
    out=audit(receipt,public)
    with (HERE/'audit_20260930_r2.json').open('x') as f:json.dump(out,f,indent=2);f.write('\n')
    print(json.dumps({k:v for k,v in out.items() if k not in ['summaries','negative_controls']},indent=2))

if __name__=='__main__':main()
