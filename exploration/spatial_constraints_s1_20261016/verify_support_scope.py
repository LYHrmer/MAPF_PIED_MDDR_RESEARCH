"""Fixed algebra/contract check; never runs a solver, trajectory or session.

Reads the frozen C1 receipts and only the three new modules plus composition
and protocol. Deliberately does not import old runners or replay old suites.
Synthetic cost examples are API rejection checks, not measured costs.
"""
import argparse
from dataclasses import replace
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import sys

BASE = Path(__file__).resolve().parent
WORKSPACE = BASE.parents[2]
SOURCE = WORKSPACE/'MAPF_GAUSSIAN_FEASIBILITY/exploration/spatial_source'
TOOLS = WORKSPACE/'MAPF_QUERY_VALUE_FEASIBILITY/exploration/execution_feedback'
PINS = {
    BASE/'composition_fixture.json': '21505bab2eceb3b86c311bf870d8c70b3c81621ff194466b3be25fc62681d68a',
    BASE/'JOINT_PHASE_CHECK.json': 'e3b23415c067bab855db800c6367ed905131c14698bb12a77e96e7b2ff43c680',
    BASE/'SUPPORT_ENDPOINT_CHECK.json': '20cdad655f585812fc7e292787c81552b8f70f2e366aded484b76608e8791642',
    SOURCE/'composition.py': 'e294be82cc6277fac462f61450685820f2d9f1b2c49f1c07c814f7abe4f08453',
    TOOLS/'protocol.py': 'ec9e516a3d1dd04da72c3935db3150d7c3b593f596a3002a725cb832fb11911d',
}


def require(condition, detail):
    if not condition:
        raise ValueError(detail)


def verify():
    pins = dict(PINS)
    endpoint = json.loads((BASE/'SUPPORT_ENDPOINT_CHECK.json').read_text())
    joint = json.loads((BASE/'JOINT_PHASE_CHECK.json').read_text())
    for receipt in (endpoint, joint):
        for path, digest in receipt['input_sha256'].items():
            path = Path(path)
            require(path not in pins or pins[path] == digest, 'inconsistent prior pins')
            pins[path] = digest
    for path, digest in pins.items():
        require(hashlib.sha256(path.read_bytes()).hexdigest() == digest, 'changed frozen input: '+str(path))
    for path in (SOURCE/'support_domain.py', TOOLS/'construction_cost.py', BASE/'support_scope.py', Path(__file__)):
        pins[path] = hashlib.sha256(path.read_bytes()).hexdigest()
    sys.path[:0] = [str(SOURCE), str(TOOLS)]
    import sympy as sp
    from composition import Chain
    from support_domain import move_domain, affine_inverse_condition, rank_condition
    from support_scope import support_scope, rational_range
    from construction_cost import common_key, cache_key, cost_coverage, paired_cost_readiness, COMMON_FIELDS, COMPONENTS, PROCESS_SCOPE

    config = json.loads((BASE/'composition_fixture.json').read_text())
    chains = {name: Chain.build(spec) for name, spec in config['robots'].items()}
    descriptors = {name+'_'+str(i): move_domain(chain, i) for name, chain in chains.items()
                   for i, action in enumerate(chain.primitives) if action.kind == 'MOVE'}
    a0, a2, b0, b2, b4 = (descriptors[k] for k in ('A_0', 'A_2', 'B_0', 'B_2', 'B_4'))
    require(a0.task_parameters == a2.task_parameters, 'A error reset at turn')
    require(b0.task_parameters == b2.task_parameters == b4.task_parameters, 'B error reset at turn')
    require((a2.displacement, a2.translation_half, a2.offset) ==
            ((Q(2), Q(0)), (Q('.02'), Q('.01')), Q('8.5')), 'A cumulative displacement/original axes/clock lost')
    require((b2.displacement, b2.translation_half, b2.offset, b4.offset) ==
            ((Q(0), Q('.78')), (Q('.01'), Q('.02')), Q('6.06'), Q('12.16')), 'B cumulative displacement/original axes/clock lost')
    require(set(a2.rotated_vertex_coefficients) ==
            {(Q('1.9'), Q('-.3')), (Q('1.9'), Q('.3')), (Q('2.1'), Q('-.3')), (Q('2.1'), Q('.3'))},
            'same-delta displaced body coefficients missing')

    boundary_checks = []

    def rejects(name, callback):
        try:
            callback()
        except ValueError:
            boundary_checks.append(name)
        else:
            raise ValueError('expected refusal: '+name)

    rejects('TURN_not_a_MOVE', lambda: move_domain(chains['A'], 1))
    rejects('changed_speed', lambda: Chain.build(config['robots']['A'], speed='.4'))
    rejects('changed_drift', lambda: Chain.build(config['robots']['A'], drift='.01'))
    rejects('changed_heading_prior', lambda: rank_condition(replace(a0, heading_half=Q('.003')), b0))
    require(affine_inverse_condition(a0, b0, max_a=a0.length-Q(1, 8), min_b=Q(1, 8))['qualified'],
            'closed inverse transition boundary lost')
    require(not affine_inverse_condition(a0, b0, max_a=a0.length, min_b=0)['qualified'],
            'braking/acceleration must not be approximated as cruise')
    # A time-only wait changes the complete-chain offset and identity. This is
    # a structural mutation check, never a new execution or performance case.
    wait_spec = {**config['robots']['A'], 'actions': [['WAIT', '1']]+config['robots']['A']['actions']}
    waited = move_domain(Chain.build(wait_spec), 3)
    require(waited.offset == a2.offset+1 and waited.displacement == a2.displacement
            and waited.task_parameters != a2.task_parameters, 'pause/switch clock not rebound')

    # Mathematical edge cases for the enclosure, not generated robot tasks.
    ta, tb = sp.symbols('ta tb', real=True)
    work = dict(rational_enclosures=0, polynomial_terms=0)
    require(rational_range(ta**2+tb, (ta, tb), ((Q(-1), Q(1)), (Q(0), Q(0))), work) == (0, 1),
            'even power must contain its interior minimum')
    require(rational_range(1/ta, (ta, tb), ((Q(-1), Q(1)), (Q(0), Q(0))), work) is None,
            'denominator containing zero must fall back')

    rows = []
    exact_pairs = {('A_0', 'B_0'), ('A_2', 'B_2')}
    known_lower = Q(endpoint['endpoint_enclosure'][0])
    for previous in joint['records']:
        tail, head = previous['tail'], previous['head']
        row = {'pair': [tail, head], 'frozen_upper': previous['refined_upper'],
               'frozen_upper_strictly_below_global_contact': Q(previous['refined_upper']) < known_lower,
               'is_release_authorization': False}
        if tail not in descriptors or head not in descriptors:
            row.update(status='FALLBACK_NON_MOVE', reason='continuous TURN geometry is outside this theorem')
        else:
            a, b = descriptors[tail], descriptors[head]
            scope = support_scope(a, b)
            inv = affine_inverse_condition(a, b, max_a=previous['joint']['max_a'], min_b=previous['joint']['min_b'])
            row.update(status=scope['status'], geometry=scope, inverse=inv)
            if scope['status'] == 'MONOTONE_RELAXED_SUPPORT' and inv['qualified']:
                row['conditional_time_upper'] = a.offset-b.offset+2*scope['max_relaxed_progress_enclosure'][1]
            if (tail, head) in exact_pairs:
                require(scope['status'] == 'MONOTONE_RELAXED_SUPPORT' and inv['qualified'],
                        'shared support theorem failed to cover fixed exact pair')
                require(scope['maximizing_heading_corner'] == [Q('-.002')]*2, 'incorrect maximizing corner')
                z = sp.symbols('z', real=True)
                c, s = (1-z*z)/(1+z*z), 2*z/(1+z*z)
                value = sp.sympify(scope['relaxed_progress_support'], locals={'ta': ta, 'tb': tb})
                expected = sp.Rational(8, 5)+sp.Rational(3, 25)*c+4*s
                require(sp.cancel(a.offset-b.offset+2*value.subs({ta: -z, tb: -z})-expected) == 0,
                        'generic expression differs from frozen exact endpoint')
                row['contact_attainment'] = 'REUSED_FIXED_C1_CERTIFICATE_NOT_GENERAL_WITNESS_SOLVER'
            else:
                require(row['frozen_upper_strictly_below_global_contact'], 'remaining pair may be active')
        rows.append(row)
    require(len(rows) == 11, 'frozen conflict pair omitted')
    require(sum(r['frozen_upper_strictly_below_global_contact'] for r in rows) == 9, 'dominance audit changed')

    # Local tool checks use explicit SYNTHETIC_API_FIXTURE values; these are
    # neither timer measurements nor scientific comparison results.
    common = {name: hashlib.sha256(('SYNTHETIC_API_FIXTURE:'+name).encode()).hexdigest() for name in COMMON_FIELDS}
    kwargs = dict(task='SYNTHETIC_API_FIXTURE', pair=['A_0', 'B_0'], offsets=['0', '0'],
                  allowed_set_sha256='a'*64, precision='1/1000', kernel_sha256='b'*64)
    key = cache_key(common, **kwargs)
    require(key != cache_key(common, **{**kwargs, 'offsets': ['1', '0']}), 'cache ignored switched clock')
    require(key != cache_key(common, **{**kwargs, 'allowed_set_sha256': 'c'*64}), 'cache ignored joint feedback domain')
    require(key == cache_key(common, **{**kwargs, 'precision': '.001'}), 'equivalent precision not normalized')
    rejects('incomplete_shared_baseline', lambda: common_key({k: v for k, v in common.items() if k != 'analytic_fast_path'}))
    no_costs = cost_coverage(None, None, {})
    require(no_costs['status'] == 'INCOMPLETE_COST_EVIDENCE' and no_costs['process_totals'] is None,
            'missing measurements promoted to zero costs')
    synthetic_costs = {'wall_ns': 10, 'cpu_ns': 8, 'aggregation': 'OUTER_ENVELOPE_ONLY_DO_NOT_SUM_NESTED',
                       'segments': [{'name': 'SYNTHETIC_API_FIXTURE', 'depth': 0, 'wall_ns': 10, 'cpu_ns': 8}]}
    synthetic_process = {'total_process_wall_ns': 15, 'total_process_cpu_ns': 12, 'cost_scope': PROCESS_SCOPE,
                         'process_success': True, 'failure_retained': False}
    coverage = {k: ['SYNTHETIC_API_FIXTURE'] for k in COMPONENTS}
    check = cost_coverage(synthetic_costs, synthetic_process, coverage)
    require(check['status'] == 'COMPLETE_DECLARED_COVERAGE' and check['process_totals']['total_process_wall_ns'] == 15
            and not check['runtime_speedup_claim_allowed'], 'nested cost sum or fixture performance claim')
    omitted = cost_coverage(synthetic_costs, synthetic_process, {**coverage, 'control_to_END': {'not_used': 'omitted'}})
    require('control_to_END' in omitted['missing'], 'complete-task cost allowed to omit END')
    rejects('failed_process_dropped', lambda: cost_coverage(synthetic_costs, {**synthetic_process, 'process_success': False}, coverage))
    rejects('invalid_boolean_time', lambda: cost_coverage({**synthetic_costs, 'wall_ns': True}, synthetic_process, coverage))
    rejects('nested_total', lambda: cost_coverage({**synthetic_costs, 'aggregation': 'SUM'}, synthetic_process, coverage))
    left = dict(task='SYNTHETIC_API_FIXTURE', arm='candidate', common=common, costs=synthetic_costs,
                process=synthetic_process, coverage=coverage)
    right = {**left, 'arm': 'baseline', 'process': {**synthetic_process, 'process_success': False, 'failure_retained': True}}
    comparison = paired_cost_readiness(left, right)
    require(not comparison['ready_for_outcome_and_cost_review'] and comparison['all_arm_outcomes_retained'],
            'failed arm hidden in comparison')
    rejects('unshared_fast_path', lambda: paired_cost_readiness(left, {**right, 'common': {**common, 'analytic_fast_path': 'd'*64}}))

    return {'status': 'FIXED_C1_SUPPORT_SCOPE_STATIC_PASS',
            'scope': 'conditional theorem and frozen-input coverage; no search or task execution',
            'source': {'whole_task_parameters_reused': True, 'A2_offset': a2.offset, 'B2_offset': b2.offset,
                       'B4_offset': b4.offset, 'wait_mutation_scope': 'structural API check only'},
            'records': rows, 'boundary_rejections': boundary_checks,
            'current_full_cost_evidence': no_costs, 'cost_test_data': 'SYNTHETIC_API_FIXTURE_NOT_MEASUREMENTS',
            'same_information_baseline': 'same descriptor, support expressions, derivative enclosure and fallback',
            'remaining_nine_pairs_cannot_change_C1_right_endpoint_by_tightening_alone': True,
            'new_algorithm_gap': 'NOT_ESTABLISHED', 'independent_task_evidence': False,
            'independent_scientific_validation': False, 'successor_run_plan_prepared': False,
            'scientific_runs': 0, 'world_steps': 0, 'task_session_calls': 0, 'training_runs': 0,
            'optimizer_calls': 0, 'author_code_calls': 0,
            'input_sha256': {str(p): digest for p, digest in pins.items()}}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-result', action='store_true')
    args = parser.parse_args()
    output = BASE/'SUPPORT_SCOPE_CHECK.json'
    if args.write_result and output.exists():
        raise FileExistsError('preserve existing receipt: '+str(output))
    try:
        result = verify()
    except Exception as exc:
        if args.write_result:
            with output.open('x') as stream:
                json.dump({'status': 'SUPPORT_SCOPE_STATIC_FAILED', 'error': type(exc).__name__, 'detail': str(exc)}, stream, indent=2)
                stream.write('\n')
        raise
    if args.write_result:
        with output.open('x') as stream:
            json.dump(result, stream, default=str, ensure_ascii=False, indent=2)
            stream.write('\n')
    print(json.dumps({'status': result['status'], 'pairs': [(r['pair'], r['status']) for r in result['records']],
                      'new_algorithm_gap': result['new_algorithm_gap'], 'scientific_runs': 0}, default=str))
