"""Recompute the six consumed DEV receipts; no solver imports or new runs."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def summarize():
    config_path = HERE/'config/repair_dev_manifest.json'
    config_raw = config_path.read_bytes()
    config = json.loads(config_raw)
    inputs_raw = (HERE/'config'/config['input_file']).read_bytes()
    assert sha(inputs_raw) == config['input_sha256']
    bundle = json.loads(inputs_raw)
    root = HERE/'results'/config['batch_id']
    rows, evidence = [], {}
    for job in config['jobs']:
        folder = root/job['id']
        receipt_raw = (folder/'receipt.json').read_bytes()
        receipt = json.loads(receipt_raw)
        result_raw = (folder/'result.json').read_bytes()
        result = json.loads(result_raw)
        assert receipt['manifest_sha256'] == result['manifest_sha256'] == sha(config_raw)
        assert receipt['job'] == job
        for name, record in receipt['artifacts'].items():
            raw = (folder/name).read_bytes()
            assert sha(raw) == record['sha256'] and len(raw) == record['bytes'], (job['id'], name)
        evidence[job['id']] = {'receipt_sha256': sha(receipt_raw), 'result_sha256': sha(result_raw)}
        case = next(case for case in bundle['cases'] if case['id'] == job['case'])
        lower = sum(result['lower_bounds'].values())
        costs = receipt['costs']
        rows.append({'case': job['case'], 'policy': job['policy'], 'status': receipt['status'],
            'initial_soc': result['initial_soc'], 'final_soc': result['final_soc'],
            'final_makespan': result['final_makespan'], 'static_h_sum': lower,
            'soc_minus_static_h': result['initial_soc']-lower,
            'final_sha256': result['final_sha256'], 'search_calls': result['search_calls'],
            'expanded': sum(r.get('response', {}).get('num_expanded', 0) for r in result['rpc'] if r['op']=='search'),
            'attempt_statuses': [r['status'] for r in result['attempts']],
            'root_lower_bound_stops': sum(r['reason']=='remaining lower bound exceeds strict target' for r in result['attempts']),
            'worker_wall_ns': costs['wall_ns'],
            'all_descendant_cpu_s': costs['all_descendant_user_s']+costs['all_descendant_system_s'],
            'supervisor_inclusive_before_final_receipt_ns': receipt['supervisor_entry_through_artifact_hash_ns'],
            'supervisor_self_cpu_s': receipt['supervisor_self_cpu_s'],
            'combined_cpu_before_final_receipt_s': receipt['supervisor_self_cpu_s']+costs['all_descendant_user_s']+costs['all_descendant_system_s'],
            'bootstrap_ns': result['bootstrap_through_native_ready_ns'],
            'repair_search_stage_ns': result['stage_wall_ns'].get('search',0),
            'largest_child_maxrss_kib': costs['largest_child_maxrss_kib'],
            'final_validated': result['final_validated'], 'forced_cleanup': costs['forced_cleanup']})
    pairs = []
    for case in bundle['cases']:
        pair = [row for row in rows if row['case']==case['id']]
        assert len(pair)==2
        assert all(row['status']=='COMPLETE' and row['final_validated'] and not row['forced_cleanup'] for row in pair)
        assert pair[0]['final_sha256']==pair[1]['final_sha256']
        pairs.append({'case':case['id'], 'same_final_plan':True,
                      'initial_soc_equals_author_static_h': all(row['soc_minus_static_h']==0 for row in pair)})
    # Do not use the scenario's reference distance as a same-model coordination
    # slack. Compare only its frozen first eight rows against observed author h.
    reference_checks = []
    for case in bundle['cases']:
        names = [name for name in case['source_files'] if name.endswith('.scen')]
        assert len(names)==1
        name = names[0]
        raw = (Path(case['source_root'])/name).read_bytes()
        assert sha(raw)==case['source_files'][name]['sha256']
        reference_sum = sum(float(row.split()[8]) for row in raw.decode().splitlines()[1:9])
        h = next(row['static_h_sum'] for row in rows if row['case']==case['id'])
        reference_checks.append({'case':case['id'], 'frozen_scenario_sha256':sha(raw),
                                 'column_9_first_eight_sum':reference_sum,
                                 'four_neighbor_author_h_sum':h, 'equal':reference_sum==h})
    summary = {'scope':'SIX_AUTHORIZED_COMPUTATIONAL_DEV_ARMS_NO_RETRY',
               'code_commit':'818f1e99672e59db57f0720953fef5809a6331ee',
               'manifest_sha256':sha(config_raw), 'input_sha256':sha(inputs_raw),
               'postprocessor_sha256':sha(Path(__file__).read_bytes()),
               'evidence':evidence, 'rows':rows, 'pairs':pairs,
               'scenario_reference_checks':reference_checks,
               'decision':'KEEP_CLASSICAL_BOUND_AS_BASELINE_STOP_LEARNING_ON_THESE_ZERO_SLACK_TASKS',
               'independent_speedup_or_novelty_proven':False}
    target = root/'summary.json'
    with target.open('x') as stream:
        json.dump(summary, stream, indent=2, sort_keys=True)
        stream.write('\n')
    print(json.dumps({'summary':str(target), 'sha256':sha(target.read_bytes()),
                      'arms':len(rows), 'decision':summary['decision']}))


if __name__ == '__main__':
    summarize()
