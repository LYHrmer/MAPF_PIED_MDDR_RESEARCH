"""Software contracts only: no author Instance or SIPP/search construction."""
import os
from pathlib import Path
import subprocess
import tempfile
import time
import unittest
from unittest.mock import patch

from address_adapter import adapt, replace_exact
from build_address_full import AUTHOR, build, source_identity
from run_address_adapter import (load, parse_paths, verify_attempt_trace, verify_budget_receipt,
                                 verify_phase_profile, verify_seed_comparison, comparison_settings,
                                 PHASE_NAMES, worker)
from run_repair_dev import unpack
from reward_analysis import (diagnose_legacy, verify_reward_trace, committed_magnitude_feedback,
                             verify_deadline_observations)


class AdapterContracts(unittest.TestCase):
    def test_cost_inspection_never_constructs_problem_or_search(self):
        import io
        import json
        import run_address_adapter
        job=dict(case='fixture',top_k=32)
        config=dict(comparison_protocol='reward_cost_diagnostic_v1',jobs=[job])
        bundle=dict(cases=[dict(id='fixture',paths={str(i):[i,i] for i in range(32)})])
        output=io.StringIO()
        with patch('sys.argv',['runner','inspect','--manifest','unused.json','--sha256','unused']), \
                patch('run_address_adapter.load',return_value=(config,bundle,Path('unused'))), \
                patch('run_address_adapter.unpack',side_effect=AssertionError('must not construct GridProblem')), \
                patch('sys.stdout',output):
            self.assertEqual(run_address_adapter.main(),0)
        value=json.loads(output.getvalue())
        self.assertFalse(value['problem_constructed'])
        self.assertFalse(value['search_executed'])

    def test_cost_diagnostic_requires_explicit_protocol_and_fixed_author_rule(self):
        config=dict(variant='reward_contract',comparison_protocol='reward_cost_diagnostic_v1',cost_diagnostics=True)
        job=dict(seed_admission='positive_delay',effort_mode='total_budget',iterations=0,
                 reward_memory='author',reward_window=0)
        self.assertEqual(comparison_settings(config,job),('positive_delay','total_budget'))
        for changed in (dict(job,reward_memory='cumulative'),dict(job,reward_memory='window',reward_window=16)):
            with self.assertRaises(ValueError):comparison_settings(config,changed)
        with self.assertRaises(ValueError):comparison_settings(dict(config,cost_diagnostics=False),job)

    def test_first_observation_rejects_missing_simultaneous_scope_and_false_trigger(self):
        import copy
        o=dict(stage='SIPP_RETURN',resource='WALL_AND_CPU',scope='LOCAL_AND_GLOBAL',
               observed_wall_ns=100,observed_cpu_ns=90,global_wall_limit_ns=200,global_cpu_limit_ns=90,
               local_wall_limit_ns=100,local_wall_triggered=True,global_wall_triggered=False,global_cpu_triggered=True)
        data=dict(first_observed_deadline=o,first_observed_local_deadline=o,first_observed_global_deadline=o,
                  wall_clock='STEADY_ABSOLUTE_NS',cpu_clock='PROCESS_CPU_ABSOLUTE_NS')
        verify_deadline_observations(data)
        # A false global-wall flag may share its integer-ns bin with the limit.
        rounded={key:dict(value,global_wall_limit_ns=100) if isinstance(value,dict) else value
                 for key,value in data.items()}
        verify_deadline_observations(rounded)
        with self.assertRaises(ValueError):verify_deadline_observations(dict(data,first_observed_global_deadline=None))
        overwritten=dict(data,first_observed_global_deadline=dict(o,
            observed_wall_ns=110,observed_cpu_ns=95,stage='REWARD_VALIDATION'))
        with self.assertRaises(ValueError):verify_deadline_observations(overwritten)
        bad=copy.deepcopy(data)
        for key in ('first_observed_deadline','first_observed_local_deadline','first_observed_global_deadline'):
            bad[key]['observed_wall_ns']=201
        with self.assertRaises(ValueError):verify_deadline_observations(bad)

    def test_magnitude_feedback_preserves_terminal_objective_and_censor_unknown(self):
        rows = [dict(old_task_soc=10, committed_task_soc=8, committed_gain=2,
                     selection_wall_before_log_ns=20, outcome='ACCEPTED',
                     accepted=True, candidate_validated=True, censored=False, seed_id=0),
                dict(old_task_soc=8, committed_task_soc=8, committed_gain=0,
                     selection_wall_before_log_ns=80, outcome='CENSORED',
                     accepted=False, candidate_validated=False, censored=True, seed_id=1),
                dict(old_task_soc=8, committed_task_soc=3, committed_gain=5,
                     selection_wall_before_log_ns=50, outcome='ACCEPTED',
                     accepted=True, candidate_validated=True, censored=False, seed_id=0),
                dict(old_task_soc=3, committed_task_soc=3, committed_gain=0,
                     selection_wall_before_log_ns=0, outcome='NO_GROUP',
                     accepted=False, candidate_validated=False, censored=False, seed_id=None)]
        summary = committed_magnitude_feedback(rows, 10, 3)
        self.assertEqual(summary['normalized_reward_sum_exact'], [7, 10])
        self.assertEqual(summary['positive_gain_events'], 2)  # Magnitudes 2 and 5 retained.
        self.assertEqual(summary['gain_event_counts'], {0: 2, 2: 1, 5: 1})
        self.assertEqual(summary['censored_actual_committed_gain'], 0)
        self.assertEqual(summary['censored_candidate_gain_unobserved_events'], 1)
        self.assertIsNone(summary['counterfactual_gain_if_given_more_time'])
        self.assertEqual(summary['recorded_selection_wall_ns'], 150)
        self.assertEqual(summary['per_seed']['1']['recorded_selection_wall_ns'], 80)
        self.assertEqual(summary['zero_recorded_wall_events'], 1)
        self.assertFalse(summary['continuous_reward_passed_to_beta'])
        self.assertFalse(summary['policy_performance_estimated'])
        # No implicit denominator change, phantom improvement or missing tail.
        for changed in (dict(rows[1], committed_gain=1),
                        dict(rows[1], outcome='ACCEPTED', accepted=True, committed_task_soc=7,
                             committed_gain=1), dict(rows[1], outcome='UNSETTLED_ERROR')):
            with self.assertRaises(ValueError):
                committed_magnitude_feedback([rows[0], changed, *rows[2:]], 10, 3)
        with self.assertRaises(ValueError): committed_magnitude_feedback(rows[:-2], 10, 3)

    def test_magnitude_feedback_zero_task_and_regression_rejection(self):
        self.assertEqual(committed_magnitude_feedback([], 0, 0)['normalized_reward_sum_exact'], [0, 1])
        bad = dict(old_task_soc=1, committed_task_soc=2, committed_gain=-1,
                   selection_wall_before_log_ns=10, outcome='ROLLED_BACK',
                   accepted=False, candidate_validated=True, censored=False, seed_id=0)
        with self.assertRaises(ValueError): committed_magnitude_feedback([bad], 1, 2)
        for invalid in (-1, True, 1.5):
            with self.assertRaises(ValueError): committed_magnitude_feedback([], invalid, 0)

    def test_reward_protocol_keeps_seed_rule_budget_and_feedback_fixed(self):
        cfg = {'variant': 'reward_contract', 'comparison_protocol': 'reward_memory_v1'}
        job = {'seed_admission': 'positive_delay', 'effort_mode': 'total_budget',
               'iterations': 0, 'reward_memory': 'window', 'reward_window': 16}
        self.assertEqual(comparison_settings(cfg, job), ('positive_delay', 'total_budget'))
        for changed in (dict(job, reward_window=0), dict(job, reward_window=True),
                        dict(job, seed_admission='all'), dict(job, reward_memory='cumulative'),
                        dict(job, effort_mode='fixed_repairs', iterations=16)):
            with self.assertRaises(ValueError): comparison_settings(cfg, changed)

    def test_reward_ledger_closes_censor_commit_and_per_seed_window(self):
        import copy, json
        base = dict(schema='ADDRESS_REWARD_V1', operator_id=0, seed_id=0,
                    group_size=2, outcome='ACCEPTED', stop='FOUND', old_task_soc=10,
                    old_subset_soc=10, fresh_paths=2, candidate_validated=True,
                    candidate_subset_soc=8, candidate_reward=2, committed_task_soc=8,
                    committed_gain=2, accepted=True, censored=False, local_deadline=False,
                    global_deadline=False, deadline_stage='NONE', deadline_resource='NONE',
                    memory_eligible=True, bernoulli_reward=1, selection_wall_before_log_ns=20,
                    selection_cpu_before_log_ns=10)
        rows = [dict(base, selection_id=1, repair_attempt_id=1)]
        rows.append(dict(base, selection_id=2, repair_attempt_id=2, outcome='ROLLED_BACK',
                         old_task_soc=8, old_subset_soc=8, candidate_subset_soc=9,
                         candidate_reward=-1, committed_gain=0, accepted=False, bernoulli_reward=0))
        rows.append(dict(rows[1], selection_id=3, repair_attempt_id=3, outcome='CENSORED',
                         fresh_paths=1, candidate_validated=False, candidate_subset_soc=None,
                         candidate_reward=None, censored=True, global_deadline=True,
                         deadline_stage='SIPP', deadline_resource='WALL', memory_eligible=False,
                         bernoulli_reward=None))
        # A synthetic helper sequence, not a scientific trajectory: non-global
        # local censor permits another selection and has no global resource.
        rows[-1].update(global_deadline=False, local_deadline=True, deadline_resource='NONE')
        rows.append(dict(rows[1], selection_id=4, repair_attempt_id=None, seed_id=1,
                         outcome='NO_GROUP', group_size=0, fresh_paths=0, old_subset_soc=None,
                         candidate_validated=False, candidate_subset_soc=None, candidate_reward=None))
        rows.append(dict(rows[-1], selection_id=5, seed_id=None, memory_eligible=False, bernoulli_reward=None))
        native = dict(initial_soc=10, final_soc=8, group_calls=5, repair_attempts=3)
        def encoded(events): return ('\n'.join(json.dumps(r) for r in events)+'\n').encode()
        for mode in ('author', 'cumulative', 'window'):
            width = 1 if mode == 'window' else 0
            native['reward_contract'] = dict(schema='ADDRESS_REWARD_V1', memory=mode, window=width,
                decision='VEHICLE_SEED_PROJECT_ADAPTATION', reward='COMMITTED_GAIN_POSITIVE_BERNOULLI',
                posterior_rule='AUTHOR_ATTEMPT_BEFORE_ROLLBACK' if mode == 'author' else 'POST_COMMIT_BERNOULLI',
                prior_alpha=1, prior_beta=1, selections=5, settlements=5, log_wall_ns=5, log_cpu_ns=3,
                arms=[dict(seed=0, completed=2, censored=1, retained_successes=0 if width else 1, retained_failures=1),
                      dict(seed=1, completed=1, censored=0, retained_successes=0, retained_failures=1)])
            job = dict(reward_memory=mode, reward_window=width)
            out = verify_reward_trace(encoded(rows), native, job, 2)
            self.assertEqual(out['actual_committed_gain'], 2)
            self.assertEqual(out['outcomes']['CENSORED'], 1)
            projected = committed_magnitude_feedback(rows, 10, 8)
            self.assertEqual(projected['normalized_reward_sum_exact'], [2, 10])
            self.assertEqual(projected['gain_event_counts'], {0: 4, 2: 1})
            # A complete worse candidate is rolled back, not a negative
            # retained-plan reward. A validated candidate can also lose its
            # commit opportunity at the deadline; its known gain is not earned.
            validated_censor = copy.deepcopy(rows)
            validated_censor[2].update(fresh_paths=2, candidate_validated=True,
                                      candidate_subset_soc=4, candidate_reward=4)
            verify_reward_trace(encoded(validated_censor), native, job, 2)
            projected = committed_magnitude_feedback(validated_censor, 10, 8)
            self.assertEqual(projected['committed_gain'], 2)
            self.assertEqual(projected['censored_actual_committed_gain'], 0)
            self.assertEqual(projected['censored_candidate_gain_unobserved_events'], 0)
            self.assertIsNone(projected['counterfactual_gain_if_given_more_time'])
            for index, changes in ((0, dict(selection_id=2)), (1, dict(old_task_soc=9)),
                                   (2, dict(candidate_subset_soc=3, candidate_reward=5)),
                                   (2, dict(memory_eligible=True, bernoulli_reward=0)),
                                   (3, dict(committed_gain=1)), (4, dict(seed_id=2))):
                bad = copy.deepcopy(rows); bad[index].update(changes)
                with self.assertRaises(ValueError): verify_reward_trace(encoded(bad), native, job, 2)
            with self.assertRaises(ValueError): verify_reward_trace(encoded(rows[:-1]), native, job, 2)
            with self.assertRaises(ValueError): verify_reward_trace(encoded(rows)[:-1], native, job, 2)

    def test_legacy_partial_positive_is_not_a_valid_complete_reward(self):
        row = dict(attempt_id=1, primary_stop='FOCAL_DRAINED_EMPTY', group_size=3,
                   old_group_cost=10, final_group_cost=10, local_deadline_reached=False,
                   global_deadline_reached=False, primary_returns=[dict(empty=False, path_cost=2),
                                                                 dict(empty=True, path_cost=-1)],
                   cost=dict(attempt_wall_before_trace_ns=20, attempt_cpu_before_trace_ns=10))
        result = diagnose_legacy([row])
        self.assertEqual(result['positive_predicate_zero_commit_ids'], [1])
        self.assertFalse(result['rows'][0]['all_fresh_paths_returned'])
        self.assertEqual(result['rows'][0]['pre_rollback_cost_difference'], 8)
        self.assertEqual(result['committed_gain'], 0)

    def _incomplete_batch_fixture(self, root, result_bytes, receipt_kind='valid'):
        import hashlib, json
        batch = root/'results'/'fixture'
        folder = batch/'first'
        folder.mkdir(parents=True)
        (folder/'worker.stderr.log').write_text('synthetic interrupted worker\n')
        jobs = [dict(id=name, case='case') for name in ('first', 'second')]
        inputs = json.dumps({'cases': [dict(id='case', rows=1, cols=2, blocked=[],
            endpoints={'0': [0, 1]}, paths={'0': [0, 1]}, orders=[])]}).encode()
        (root/'inputs.json').write_bytes(inputs)
        cfg = dict(schema='address_common_initial_dev_v1', retry=0, batch_id='fixture', jobs=jobs,
                   input_file='inputs.json', input_sha256=hashlib.sha256(inputs).hexdigest())
        raw = json.dumps(cfg).encode(); expected = hashlib.sha256(raw).hexdigest()
        (root/'manifest.json').write_bytes(raw)
        (batch/'AUTHORIZATION.json').write_text(json.dumps(dict(manifest_sha256=expected,
            jobs=['first', 'second'], scientific_code_commit='synthetic fixture, no execution')))
        (folder/'attempt.json').write_text(json.dumps(dict(job=jobs[0], manifest_sha256=expected)))
        if result_bytes is not None:
            (folder/'result.json').write_bytes(result_bytes)
        receipt = dict(status='FAILED_OR_INCOMPLETE', job=jobs[0], manifest_sha256=expected,
            total_entry_through_output_validation_and_hash_ns=5010000000,
            costs=None if receipt_kind == 'before_worker' else dict(exit_code=-9, wall_s=5, forced_cleanup=True),
            artifacts={p.name: dict(sha256=hashlib.sha256(p.read_bytes()).hexdigest(), bytes=p.stat().st_size)
                       for p in folder.iterdir()})
        if receipt_kind != 'missing':
            (folder/'receipt.json').write_text('{"status":' if receipt_kind == 'truncated' else json.dumps(receipt))
        return expected, receipt

    def test_batch_audit_retains_killed_job_costs_and_unattempted_tail(self):
        import io, json
        from contextlib import redirect_stdout
        from repair_profile import address_results
        for result_bytes, receipt_kind in ((None, 'valid'), (b'{"status":', 'valid'),
                                           (None, 'missing'), (None, 'truncated'), (None, 'before_worker')):
            with self.subTest(result=result_bytes, receipt=receipt_kind), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                expected, receipt = self._incomplete_batch_fixture(root, result_bytes, receipt_kind)
                with patch('repair_profile.HERE', root), redirect_stdout(io.StringIO()):
                    address_results(root/'manifest.json', expected)
                result = json.loads((root/'results/fixture/RUN_RECEIPT.json').read_text())
                self.assertEqual(result['counts']['FAILED_OR_INCOMPLETE'], 1)
                self.assertEqual(result['counts']['NOT_RUN_AFTER_BATCH_STOP'], 1)
                row = result['jobs'][0]
                self.assertIsNone(row['final_soc'])
                known_receipt = receipt_kind in ('valid', 'before_worker')
                self.assertEqual(row['costs'], receipt['costs'] if known_receipt else None)
                self.assertEqual(row['total_entry_through_output_validation_and_hash_ns'],
                                 receipt['total_entry_through_output_validation_and_hash_ns'] if known_receipt else None)
                if result_bytes is not None:
                    self.assertIn('result.json', row['unreadable_artifacts'])

    def test_incomplete_batch_still_rejects_identity_and_artifact_changes(self):
        import io, json
        from contextlib import redirect_stdout
        from repair_profile import address_results
        for changed in ('receipt_job', 'receipt_manifest', 'attempt_job', 'artifact', 'partial_result'):
            with self.subTest(changed=changed), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                expected, receipt = self._incomplete_batch_fixture(
                    root, b'{"status":' if changed == 'partial_result' else None)
                folder = root/'results/fixture/first'
                if changed == 'receipt_job':
                    receipt['job'] = dict(id='different', case='case')
                elif changed == 'receipt_manifest':
                    receipt['manifest_sha256'] = '0'*64
                elif changed == 'attempt_job':
                    (folder/'attempt.json').write_text(json.dumps(dict(job={}, manifest_sha256=expected)))
                elif changed == 'artifact':
                    (folder/'worker.stderr.log').write_text('changed bytes\n')
                else:
                    (folder/'result.json').write_bytes(b'{"status":"FAILED"')
                (folder/'receipt.json').write_text(json.dumps(receipt))
                message = 'identity mismatch' if changed in ('receipt_job', 'receipt_manifest', 'attempt_job') else 'evidence bytes changed'
                with patch('repair_profile.HERE', root), redirect_stdout(io.StringIO()), self.assertRaisesRegex(ValueError, message):
                    address_results(root/'manifest.json', expected)
                self.assertFalse((root/'results/fixture/RUN_RECEIPT.json').exists())

    def test_seed_comparison_requires_explicit_policy_and_uncapped_time_mode(self):
        config = {'comparison_protocol': 'seed_admission_v1', 'variant': 'budget_guard'}
        job = {'seed_admission': 'positive_delay', 'effort_mode': 'total_budget', 'iterations': 0}
        self.assertEqual(comparison_settings(config, job), ('positive_delay', 'total_budget'))
        self.assertIsNone(comparison_settings({}, {'iterations': 16}))
        bad = [({}, job), (dict(config, variant='base'), job),
               (dict(config, attempt_trace=True), job), (dict(config, phase_profile=True), job),
               (config, dict(job, iterations=16)), (config, dict(job, iterations=True)),
               (config, dict(job, effort_mode='fixed_repairs')),
               (config, dict(job, seed_admission='unknown'))]
        for cfg, setting in bad:
            with self.subTest(config=cfg, job=setting), self.assertRaises(ValueError):
                comparison_settings(cfg, setting)

    def test_seed_receipt_does_not_turn_censored_work_into_equal_work_speedup(self):
        import copy
        config = {'comparison_protocol': 'seed_admission_v1', 'variant': 'budget_guard'}
        job = {'seed_admission': 'all', 'effort_mode': 'fixed_repairs', 'iterations': 16}
        admission = {'schema': 'ADDRESS_SEED_ADMISSION_V1', 'policy': 'all',
                     'selection_calls': 6, 'agents_checked': 0, 'topk_candidates': 48,
                     'filtered_zero_candidates': 0, 'retained_topk_candidates': 48,
                     'empty_eligible_calls': 0, 'deadline_calls': 1, 'selected_calls': 5,
                     'static_soc_lower_bound_reached': False}
        native = {'effort_mode': 'fixed_repairs', 'repair_cap': 16, 'repair_attempts': 4,
                  'attempt_trace_rows': 0, 'attempt_trace_enabled': False, 'group_calls': 6,
                  'trace_io_wall_ns': 0, 'trace_io_cpu_ns': 0,
                  'rollbacks': 4, 'loop_exit_reason': 'GLOBAL_DEADLINE', 'termination': 'GLOBAL_DEADLINE',
                  'global_deadline': True, 'deadline_resource': 'CPU', 'preprocessing_fallback': False,
                  'static_soc_lower_bound_reached': False, 'seed_admission': admission}
        out = verify_seed_comparison(native, config, job)
        self.assertFalse(out['repair_target_met'])
        self.assertFalse(out['equal_work_timing_eligible'])
        for mutate in (lambda x: x.update(repair_attempts=17),
                       lambda x: x.update(repair_cap=True),
                       lambda x: x.update(termination='REPAIR_CAP', loop_exit_reason='REPAIR_CAP'),
                       lambda x: x.update(deadline_resource='NONE'),
                       lambda x: x.update(attempt_trace_rows=4),
                       lambda x: x.update(trace_io_wall_ns=1),
                       lambda x: x['seed_admission'].update(filtered_zero_candidates=1),
                       lambda x: x['seed_admission'].update(policy='positive_delay'),
                       lambda x: x['seed_admission'].update(selected_calls=6)):
            bad = copy.deepcopy(native); mutate(bad)
            with self.assertRaises(ValueError): verify_seed_comparison(bad, config, job)
        total = dict(native, effort_mode='total_budget', repair_cap=None)
        total_job = dict(job, effort_mode='total_budget', iterations=0)
        self.assertIsNone(verify_seed_comparison(total, config, total_job)['repair_target_met'])
        with self.assertRaises(ValueError):
            verify_seed_comparison(dict(total, termination='REPAIR_CAP', loop_exit_reason='REPAIR_CAP'), config, total_job)
        completed = dict(native, repair_attempts=16, group_calls=16,
                         termination='REPAIR_CAP', loop_exit_reason='REPAIR_CAP',
                         global_deadline=False, deadline_resource='NONE')
        self.assertTrue(verify_seed_comparison(completed, config, job)['repair_target_met'])

    def test_materialization_failure_retains_build_receipt(self):
        import json
        for error in (ValueError('anchor mismatch'), FileNotFoundError('missing header'),
                      OSError('overlay write failed')):
            with self.subTest(error=type(error).__name__), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                with patch('build_address_full.source_identity', return_value={}), \
                     patch('address_adapter.materialize', side_effect=error):
                    with self.assertRaises(type(error)):
                        build(root/'fake-author', root/'new-build', adapter=True)
                receipt = json.loads((root/'new-build/build_receipt.json').read_bytes())
                self.assertEqual(receipt['status'], 'FAILED')
                self.assertIn(str(error), receipt['error'])
                self.assertEqual(receipt['stages'], [])

    def test_load_binds_receipt_status_author_and_binary(self):
        import hashlib, json
        def sha(raw):
            return hashlib.sha256(raw).hexdigest()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            names = ['run_address_adapter.py', 'run_repair_dev.py', 'address_backend.py', 'pp_repair.py']
            for name in names:
                (root/name).write_text('# fixture only\n')
            binary_raw = b'fixture binary bytes; never executed'
            (root/'binary').write_bytes(binary_raw)
            inputs = b'{"cases": []}'
            (root/'inputs.json').write_bytes(inputs)
            good = {'status': 'COMPILED_HELP_ONLY',
                    'scope': 'ADDRESS_COMMON_INITIAL_ADAPTER_COMPILE_AND_HELP_ONLY',
                    'author_commit': AUTHOR, 'author_unchanged': True,
                    'solver_instance_constructed': False, 'scientific_search_executed': False,
                    'binary_sha256': sha(binary_raw)}
            config = {'schema': 'address_common_initial_dev_v1', 'authorization': 'PENDING_USER',
                      'binary': 'binary', 'binary_sha256': sha(binary_raw), 'input_file': 'inputs.json',
                      'input_sha256': sha(inputs), 'retry': 0, 'batch_id': 'fixture', 'jobs': [],
                      'limits': {'total_wall_s': 15, 'worker_cpu_s': 10, 'native_cpu_s': 10,
                                 'per_process_as_mib': 512, 'external_final_reserve_s': .5,
                                 'inner_final_reserve_s': .25}}
            def inspect(receipt):
                receipt_name = config.get('build_receipt', 'adapter_build_receipt.json')
                (root/receipt_name).write_text(json.dumps(receipt))
                config['code_sha256'] = {name: sha((root/name).read_bytes())
                                        for name in names+[receipt_name]}
                raw = json.dumps(config).encode()
                (root/'manifest.json').write_bytes(raw)
                with patch('run_address_adapter.HERE', root):
                    return load(root/'manifest.json', sha(raw))
            self.assertEqual(inspect(good)[2], root/'binary')
            for key, bad in [('status', 'FAILED'), ('scope', 'PRISTINE_FULL_ADDRESS_COMPILE_AND_HELP_ONLY'),
                             ('author_commit', '0'*40), ('binary_sha256', '0'*64),
                             ('author_unchanged', False)]:
                with self.subTest(key=key), self.assertRaisesRegex(ValueError, 'build receipt'):
                    inspect(dict(good, **{key: bad}))
            config.update(variant='loop_guard', build_receipt='loop_guard_build_receipt.json')
            guarded = dict(good, scope='ADDRESS_COMMON_INITIAL_LOOP_GUARD_COMPILE_AND_HELP_ONLY',
                           extension='loop_guard')
            self.assertEqual(inspect(guarded)[2], root/'binary')
            with self.assertRaisesRegex(ValueError, 'build receipt'):
                inspect(good)  # A pristine/base receipt cannot certify the guard.
            with self.assertRaisesRegex(ValueError, 'root bound'):
                inspect(dict(guarded, extension=None))
            config.update(variant='budget_guard', build_receipt='budget_guard_build_receipt.json')
            config['limits']['native_cpu_reserve_s'] = 1
            budgeted = dict(good, scope='ADDRESS_COMMON_INITIAL_BUDGET_GUARD_COMPILE_AND_HELP_ONLY',
                            extension='budget_guard')
            self.assertEqual(inspect(budgeted)[2], root/'binary')
            with self.assertRaisesRegex(ValueError, 'budget extension'):
                inspect(dict(budgeted, extension='loop_guard'))
            for reserve in (0, 10, float('nan'), True):
                config['limits']['native_cpu_reserve_s'] = reserve
                with self.assertRaisesRegex(ValueError, 'CPU reserve'):
                    inspect(budgeted)
            config['limits']['native_cpu_reserve_s'] = 1
            config['variant'] = 'recovery'
            with self.assertRaisesRegex(ValueError, 'unreviewed runner variant'):
                inspect(guarded)  # Recovery is not a runnable scientific arm yet.
            config['variant'] = 'budget_recovery'
            with self.assertRaisesRegex(ValueError, 'unreviewed runner variant'):
                inspect(budgeted)

    def test_soft_stop_receipt_is_distinct_from_failed_or_over_budget_output(self):
        config = {'variant': 'budget_guard', 'limits': {
            'native_cpu_s': 10, 'native_cpu_reserve_s': 1}}
        native = {'budget_scope': 'SHARED_WALL_PROCESS_CPU_WITH_FINAL_RESERVE',
                  'cpu_limit_s': 10, 'cpu_reserve_s': 1, 'inner_cpu_s': 9.1,
                  'global_deadline': True, 'preprocessing_fallback': False,
                  'last_stage': 'SIPP', 'termination': 'DEADLINE', 'last_sipp_end': 'DEADLINE',
                  'group_calls': 7, 'sipp_calls': 20, 'sipp_deadlines': 1,
                  'repair_deadlines': 1, 'rollbacks': 1}
        verify_budget_receipt(native, config)  # A soft stop is not itself a failed final output.
        for key, value in [('cpu_reserve_s', 0), ('cpu_limit_s', 11), ('inner_cpu_s', 10),
                           ('inner_cpu_s', float('nan')), ('global_deadline', 'true'),
                           ('sipp_deadlines', 21), ('rollbacks', -1), ('termination', '')]:
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                verify_budget_receipt(dict(native, **{key: value}), config)

    def test_fail_closed_patch_anchor(self):
        with self.assertRaises(ValueError):
            replace_exact('a a', 'a', 'b')

    def test_exclusive_phase_profile_closes_without_extrapolating_clock_samples(self):
        import copy
        phases = {name: {'wall_ns': 0, 'scope_entries': 0, 'expired_calls': 0,
                         'expired_samples': 0, 'expired_sampled_wall_ns': 0} for name in PHASE_NAMES}
        phases['TOPK'].update(wall_ns=800, scope_entries=2, expired_calls=2048,
                             expired_samples=2, expired_sampled_wall_ns=40)
        phases['DRIVER_OTHER'].update(wall_ns=200, scope_entries=1, expired_calls=1)
        phases['GROUP_OTHER']['scope_entries'] = 2
        phases['WALK']['scope_entries'] = 3
        phases['REPAIR']['scope_entries'] = 1
        profile = {'schema': 'ADDRESS_PHASE_PROFILE_V1', 'clock': 'STEADY_WALL_NS',
                   'window': 'CONFIGURED_TO_FINISH_BEFORE_RECEIPT',
                   'window_wall_ns': 1000, 'accounted_wall_ns': 1000, 'residual_wall_ns': 0,
                   'exclusive': True, 'includes_instrumentation': True, 'phases': phases,
                   'expired_sampling': {'sampled': True, 'stride': 1024, 'calls': 2049,
                                        'samples': 2, 'sampled_wall_ns': 40, 'extrapolated': False},
                   'counters': {'group_calls': 2, 'groups_formed': 1, 'groups_no_seed': 0,
                                'groups_too_small': 1, 'groups_deadline': 0, 'seed_calls': 2, 'walk_calls': 3,
                                'seed_zero_delay_selected': 1, 'seed_positive_delay_selected': 1}}
        native = {'phase_profile': profile, 'inner_wall_before_receipt_s': .000002,
                  'group_calls': 2, 'attempt_trace_rows': 1}
        config = {'phase_profile': True}
        self.assertEqual(verify_phase_profile(native, config), profile)
        for mutate in (lambda p: p.update(exclusive=False),
                       lambda p: p.update(accounted_wall_ns=1040),
                       lambda p: p.update(residual_wall_ns=1),
                       lambda p: p['expired_sampling'].update(extrapolated=True),
                       lambda p: p['expired_sampling'].update(samples=3),
                       lambda p: p['phases']['TOPK'].update(expired_sampled_wall_ns=900),
                       lambda p: p['counters'].update(groups_too_small=0),
                       lambda p: p['counters'].update(seed_zero_delay_selected=3),
                       lambda p: p['phases']['WALK'].update(scope_entries=2),
                       lambda p: p['phases']['TOPK'].update(wall_ns=True)):
            bad = copy.deepcopy(native); mutate(bad['phase_profile'])
            with self.assertRaises(ValueError): verify_phase_profile(bad, config)
        with self.assertRaisesRegex(ValueError, 'missing phase'):
            verify_phase_profile({}, config)
        with self.assertRaisesRegex(ValueError, 'unexpected phase'):
            verify_phase_profile(native, {})
        self.assertIsNone(verify_phase_profile({}, {}))
        with self.assertRaisesRegex(ValueError, 'native wall'):
            verify_phase_profile(dict(native, inner_wall_before_receipt_s=float('nan')), config)

    def test_attempt_trace_distinguishes_normal_failure_deadline_and_unknown(self):
        import copy, json
        row = {'schema': 'ADDRESS_ATTEMPT_V2', 'attempt_id': 1, 'order': [0, 1],
               'group_size': 2, 'old_group_cost': 8, 'final_group_cost': 8,
               'primary_calls': 2, 'primary_stop': 'FOCAL_DRAINED_EMPTY',
               'primary_complete': False, 'failed_position_zero_based': 1, 'failed_agent': 1,
               'failed_agent_attempted': True, 'failure_site': 'RETURN',
               'local_deadline_reached': False, 'global_deadline_reached': False,
               'accepted': False, 'recovery_decision': 'NONE', 'group_calls_so_far': 3,
               'blockers_checked': False, 'recoverability_established': False,
               'primary_returns': [
                   {'position_zero_based': 0, 'agent': 0, 'stop': 'FOUND', 'native_end': 'FOUND',
                    'empty': False, 'path_cost': 3, 'wall_ns': 4, 'cpu_ns': 2},
                   {'position_zero_based': 1, 'agent': 1, 'stop': 'FOCAL_DRAINED_EMPTY',
                    'native_end': 'FOCAL_DRAINED_EMPTY', 'empty': True, 'path_cost': -1,
                    'wall_ns': 5, 'cpu_ns': 3}],
               'cost': {'primary_search_wall_ns': 9, 'primary_search_cpu_ns': 5,
                        'rollback_wall_ns': 1, 'rollback_cpu_ns': 1,
                        'attempt_wall_before_trace_ns': 13, 'attempt_cpu_before_trace_ns': 8}}
        native = {'attempt_trace_enabled': True, 'attempt_trace_rows': 1, 'sipp_calls': 2, 'rollbacks': 1,
                  'trace_io_wall_ns': 2, 'trace_io_cpu_ns': 1}
        def audit(record, receipt=native):
            return verify_attempt_trace((json.dumps(record)+'\n').encode(), receipt, 2)
        result = audit(row)
        self.assertEqual(result['late_normal_empty_attempt_ids'], [1])
        self.assertFalse(result['recoverability_established'])
        self.assertFalse(result['blockers_checked'])
        for stop in ('DEADLINE', 'COST_STOP', 'EMPTY_UNCLASSIFIED', 'START_BLOCKED'):
            changed = copy.deepcopy(row)
            changed['primary_stop'] = stop
            if stop == 'DEADLINE':
                changed['local_deadline_reached'] = True
                changed['primary_returns'][-1]['stop'] = 'DEADLINE'
            self.assertEqual(audit(changed)['late_normal_empty_attempt_ids'], [])
        for key, value in [('failed_agent', 0), ('primary_calls', 1), ('accepted', True),
                           ('recovery_decision', 'RECOVERY_ACCEPTED')]:
            changed = copy.deepcopy(row)
            changed[key] = value
            if key == 'accepted':
                changed['local_deadline_reached'] = True
            with self.subTest(key=key), self.assertRaises(ValueError):
                audit(changed)
        with self.assertRaisesRegex(ValueError, 'counters'):
            audit(row, dict(native, sipp_calls=3))
        with self.assertRaisesRegex(ValueError, 'partial'):
            verify_attempt_trace(json.dumps(row).encode(), native, 2)
        empty = verify_attempt_trace(b'', dict(native, attempt_trace_rows=0,
                                              sipp_calls=0, rollbacks=0), 2)
        self.assertEqual(empty['attempts'], 0)
        self.assertFalse(empty['group_construction_in_attempt_denominator'])

    def test_author_reward_and_acceptance_bodies_unchanged(self):
        root = Path(os.environ.get('ADDRESS_AUTHOR_ROOT', '/home/lyh/.cache/mapf_research/address-b3d35c4'))
        pins = source_identity(root)
        files = {name: (root/name).read_bytes() for name in pins}
        changed = adapt(files)
        old, new = files['src/LNS.cpp'], changed['src/LNS.cpp']
        def body(raw):
            return raw.split(b'bool LNS::runPP()')[1].split(b'bool LNS::runPPS()')[0]
        self.assertEqual(body(old), body(new))
        self.assertNotIn('src/BasicLNS.cpp', changed)
        self.assertNotIn(b'std::random_device', new)
        self.assertIn(b'this->neighbor_size = 8;', new)
        self.assertIn(b'neighbor.sum_of_costs = initial_sum_of_costs = sum_of_costs = cost;', new)

    def test_cpp_geometry_and_seed_contracts_without_solver(self):
        source = r'''
#include "address_adapter_support.h"
#include <cassert>
using namespace address_adapter;
void invalid(Paths p, std::vector<int> s, std::vector<int> g) {
    bool threw=false;
    try { validate(p, 2, 3, std::vector<bool>(6, false), s, g); }
    catch (const std::runtime_error&) { threw=true; }
    assert(threw);
}
int main() {
    assert(validate({{0,1,2},{3,4,5}},2,3,std::vector<bool>(6,false),{0,3},{2,5})==4);
    invalid({{0,1},{2,1}}, {0,2}, {1,1}); // vertex
    invalid({{0,1},{1,0}}, {0,1}, {1,0}); // opposing edge
    invalid({{0,1},{5,4,1,2}}, {0,5}, {1,2}); // stationary terminal hit
    invalid({{2,3},{4,5}}, {2,4}, {3,5}); // row wrap
    invalid({{0,1},{3,4}}, {1,3}, {1,4}); // endpoint
    state().seeds.seed(41); const auto a=next_seed(), b=next_seed();
    state().seeds.seed(41); assert(a==next_seed() && b==next_seed());
}
'''
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root/'contract.cpp').write_text(source)
            subprocess.run(['g++', '-std=c++14', '-O0', '-I', str(Path(__file__).parent),
                            str(root/'contract.cpp'), '-o', str(root/'contract')], check=True,
                           capture_output=True, timeout=30)
            subprocess.run([str(root/'contract')], check=True, capture_output=True, timeout=5)

    def test_external_worker_fake_child_and_final_validation(self):
        # Eight stationary paths are software fixtures; the child only writes
        # known bytes and never imports/constructs an author Instance or solver.
        case = {'id': 'fixture', 'rows': 2, 'cols': 4, 'blocked': [],
                'paths': {str(i): [i] for i in range(8)},
                'endpoints': {str(i): [i, i] for i in range(8)}, 'orders': []}
        config = {'manifest_sha256': 'fixture', 'limits': {'external_final_reserve_s': .1,
            'inner_final_reserve_s': .1, 'native_cpu_s': 2, 'per_process_as_mib': 128}}
        job = {'seed': 1, 'iterations': 1, 'top_k': 4}
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            script = folder/'fake.py'
            script.write_text('''from pathlib import Path
import json, sys
root=Path(sys.argv[1])
(root/'final.paths').write_text(''.join(f'Agent {i}:({i//4},{i%4})->\\n' for i in range(8)))
(root/'native_receipt.json').write_text(json.dumps({'initial_and_final_validated':True,
    'seed':1, 'initial_soc':0, 'final_soc':0}))
''')
            import sys
            factory = lambda *args: [sys.executable, '-B', str(script), str(folder)]
            self.assertTrue(worker(config, case, job, None, folder, time.monotonic_ns()+3_000_000_000, factory))
            import json
            result = json.loads((folder/'result.json').read_bytes())
            self.assertEqual(result['final_soc'], 0)
            self.assertTrue(result['final_validated'])
        problem, _ = unpack(case)
        malformed = ''.join(f'Agent {i}:(0,0)->\n' for i in range(8)).encode()
        with self.assertRaises(ValueError):
            parse_paths(malformed, problem)

    def test_failed_fake_child_retains_result(self):
        case = {'id': 'fixture', 'rows': 2, 'cols': 4, 'blocked': [],
                'paths': {str(i): [i] for i in range(8)},
                'endpoints': {str(i): [i, i] for i in range(8)}, 'orders': []}
        config = {'manifest_sha256': 'fixture', 'limits': {'external_final_reserve_s': .1,
            'inner_final_reserve_s': .1, 'native_cpu_s': 2, 'per_process_as_mib': 128}}
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            import sys, json
            factory = lambda *args: [sys.executable, '-B', '-c', 'raise SystemExit(7)']
            self.assertFalse(worker(config, case, {'seed': 1, 'iterations': 1, 'top_k': 4},
                None, folder, time.monotonic_ns()+3_000_000_000, factory))
            result = json.loads((folder/'result.json').read_bytes())
            self.assertEqual(result['status'], 'FAILED')
            self.assertIn('exited 7', result['reason'])
            self.assertTrue((folder/'initial.txt').exists())

    def test_optional_trace_is_charged_and_required_for_traced_worker(self):
        import json, sys
        case = {'id': 'fixture', 'rows': 2, 'cols': 4, 'blocked': [],
                'paths': {str(i): [i] for i in range(8)},
                'endpoints': {str(i): [i, i] for i in range(8)}, 'orders': []}
        config = {'variant': 'budget_guard', 'attempt_trace': True,
                  'manifest_sha256': 'fixture', 'limits': {
                      'external_final_reserve_s': .1, 'inner_final_reserve_s': .1,
                      'native_cpu_s': 2, 'native_cpu_reserve_s': 1, 'per_process_as_mib': 128}}
        native = {'initial_and_final_validated': True, 'seed': 1, 'initial_soc': 0, 'final_soc': 0,
                  'budget_scope': 'SHARED_WALL_PROCESS_CPU_WITH_FINAL_RESERVE',
                  'cpu_limit_s': 2, 'cpu_reserve_s': 1, 'inner_cpu_s': .01,
                  'global_deadline': False, 'preprocessing_fallback': False,
                  'last_stage': 'NONE', 'termination': 'NORMAL', 'last_sipp_end': 'NONE',
                  'group_calls': 0, 'sipp_calls': 0, 'sipp_deadlines': 0,
                  'repair_deadlines': 0, 'rollbacks': 0, 'attempt_trace_enabled': True,
                  'attempt_trace_rows': 0, 'trace_io_wall_ns': 0, 'trace_io_cpu_ns': 0}
        # Only materializes known fixture outputs, never runs a solver.
        for trace in ('EMPTY', 'MISSING', 'TRUNCATED'):
            with self.subTest(trace=trace), tempfile.TemporaryDirectory() as directory:
                folder = Path(directory)
                child = folder/'fake.py'
                child.write_text('from pathlib import Path\nimport sys\np=Path(sys.argv[1])\n'
                    +'assert "--attemptTrace" in sys.argv\n'
                    +"(p/'final.paths').write_text(''.join(f'Agent {i}:({i//4},{i%4})->\\n' for i in range(8)))\n"
                    +"(p/'native_receipt.json').write_text("+repr(json.dumps(native))+')\n'
                    +( "(p/'attempts.jsonl').write_text("+repr('' if trace=='EMPTY' else '{')+')\n'
                       if trace!='MISSING' else ''))
                factory = lambda *args: [sys.executable, '-B', str(child), str(folder)]
                okay = worker(config, case, {'seed': 1, 'iterations': 1, 'top_k': 4},
                              None, folder, time.monotonic_ns()+3_000_000_000, factory)
                self.assertEqual(okay, trace=='EMPTY')
                result = json.loads((folder/'result.json').read_bytes())
                if okay:
                    self.assertEqual(result['attempt_diagnostics']['attempts'], 0)
                    self.assertFalse(result['attempt_diagnostics']['recoverability_established'])
                    self.assertIn('output_parse_and_external_final_validation', result['stage_wall_ns'])
                else:
                    self.assertFalse(result['final_validated'])
                    self.assertEqual(result['status'], 'FAILED')


if __name__ == '__main__':
    unittest.main()
