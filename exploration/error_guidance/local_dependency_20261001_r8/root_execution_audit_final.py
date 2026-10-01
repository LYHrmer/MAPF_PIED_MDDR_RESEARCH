"""Extend the frozen root replay to the two added midpoint mechanical arms."""
import json
import root_execution_audit as replay


def main():
    specs = replay.load(replay.HERE/'runs.json')['runs']
    assert len(specs)==54
    rows = [replay.audit(spec) for spec in specs]
    index = {(r['map'],r['seed'],r['condition'],r['execution'],r['policy']):r
             for r in rows if r['split']=='test'}
    totals = []
    for execution in ('global','local'):
        for policy in ('hm','history','learned'):
            group = [r for r in index.values() if r['execution']==execution and r['policy']==policy]
            good = [r for r in group if r['error'] is None]
            totals.append(dict(execution=execution,policy=policy,expected=len(group),success=len(good),
                               served=sum(r['served'] for r in good),
                               fixed_first10_ticks=sum(r['fixed_first10_ticks'] for r in good),
                               early_step2_admitted=sum(r['step2_admitted_before_other_step1_END'] for r in good)))
    pairs, interaction = [], []
    for (map_name,seed,condition,execution,policy),row in index.items():
        if row['error'] is not None:
            continue
        if policy=='learned':
            for reference in ('hm','history'):
                other=index[map_name,seed,condition,execution,reference]
                if other['error'] is None:
                    pairs.append(dict(map=map_name,seed=seed,condition=condition,execution=execution,
                                      policy=policy,reference=reference,
                                      task_delta=row['served']-other['served'],
                                      fixed_time_gain_ticks=other['fixed_first10_ticks']-row['fixed_first10_ticks']))
        if execution=='local':
            other=index[map_name,seed,condition,'global',policy]
            if other['error'] is None:
                pairs.append(dict(map=map_name,seed=seed,condition=condition,execution='local',
                                  policy=policy,reference='global_same_policy',
                                  task_delta=row['served']-other['served'],
                                  fixed_time_gain_ticks=other['fixed_first10_ticks']-row['fixed_first10_ticks']))
        if execution=='local' and policy=='learned':
            lh=index[map_name,seed,condition,'local','hm']
            gl=index[map_name,seed,condition,'global','learned']
            gh=index[map_name,seed,condition,'global','hm']
            if all(r['error'] is None for r in (lh,gl,gh)):
                interaction.append(dict(map=map_name,seed=seed,condition=condition,
                    learned_vs_hm_task_delta_local=row['served']-lh['served'],
                    learned_vs_hm_task_delta_global=gl['served']-gh['served'],
                    task_difference_in_differences=(row['served']-lh['served'])-(gl['served']-gh['served'])))
    result=dict(passed=True,experiment_implementation_imported=False,episodes=len(rows),rows=rows,totals=totals,
                pairs=pairs,learning_execution_interaction=interaction,
                mechanical_same_name_distinguished_by_trial_id=True,
                interpretation='Global extra gate is an internal ablation, not published SOTA. Four independent map/task families; conditions and policies are paired. Prediction accuracy and throughput claims are separate.')
    (replay.HERE/'ROOT_EXECUTION_AUDIT.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('rows','pairs')},indent=2))


if __name__=='__main__':
    main()
