"""Fixed C1 support/monotonicity certificate, not a trajectory or B&B runner.

For nonparallel straight motions let M=[e_A,-e_B], r=r0+M(x,y),
n=M^{-T}(1,-1). If r belongs to the Minkowski sum Z of both bodies
and B_B-B_A, then x-y <= h_Z(n)-n.r0. This keeps the SAME heading
error in motion and body. In C1, n.e_A=n.e_B=1 and all support signs
are fixed on the original heading box. A rational half-angle substitution
verifies the support identities and four symbolic derivative identities.
Rational inequalities then certify negative derivatives over the whole box.

Frozen one-sided inverse conditions imply tau_A-tau_B <= 2(x-y).
The support maximum is attained at alpha=beta=-.002, at a physical
body contact with both progresses in cruise. Thus the two bottlenecks
have the exact right endpoint 1.6+.12*cos(.002)+4*sin(.002).
The other nine old upper bounds are smaller. No point sampling or optimizer
is used; no certificate authorizes release. Numerical release guards remain.

The scope is deliberately pinned C1. This is a shared analytic comparator,
not an independent validation, general solver, or claimed new MAPF method.
"""
import argparse
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import sympy as sp

BASE = Path(__file__).resolve().parent
SOURCE = BASE.parents[2] / 'MAPF_GAUSSIAN_FEASIBILITY/exploration/spatial_source/composition.py'
PINS = {
    'composition_fixture.json': '21505bab2eceb3b86c311bf870d8c70b3c81621ff194466b3be25fc62681d68a',
    'JOINT_PHASE_CHECK.json': 'e3b23415c067bab855db800c6367ed905131c14698bb12a77e96e7b2ff43c680',
    'SUPPORT_CHECK.json': '2abdd3448f6820a253782b4c09a3f51a78764c1ce8bcb009112c37b671cb3b4c',
    'DEPARTURE_CHECK.json': 'c0ad00946f7bd1b814200af23f81e1dbe0b02f85097e0e0b97e3d3365ada2cf4',
    'DEPARTURE_NOTICE.md': 'f4be9006f1064652c6541077f1875acba92a5108bdfa600bb8c82692a5fd461e',
    'SOLVER_RULE_CHECK.json': '4c394f99a9881c67bbeb4f63dca53a2015d42f58a773931592a42e7bf32d38c6',
}


def require(condition, detail):
    if not condition:
        raise ValueError(detail)


def symbolic_identities():
    """Finite polynomial/rational identities; no numeric optimization."""
    a, b, z = sp.symbols('a b z', real=True)
    rational = sp.Rational
    ca, sa = (1-a*a)/(1+a*a), 2*a/(1+a*a)
    cb, sb = (1-b*b)/(1+b*b), 2*b/(1+b*b)
    cd, sd = ca*cb+sa*sb, sa*cb-ca*sb
    ra, rb = sp.Matrix([[ca, -sa], [sa, ca]]), sp.Matrix([[cb, -sb], [sb, cb]])
    ex, ey = sp.Matrix([1, 0]), sp.Matrix([0, 1])
    rotate = sp.Matrix([[0, -1], [1, 0]])
    origins = sp.Matrix([-1, 1])
    records = []

    def equal(lhs, rhs, label):
        require(sp.cancel(lhs-rhs) == 0, label)

    for case in (0, 2):
        ea, eb = (ra*ex, rb*ey) if case == 0 else (ra*ey, rb*ex)
        r0 = origins if case == 0 else origins+2*ra*ex-rational(39, 50)*rb*ey
        matrix = sp.Matrix.hstack(ea, -eb)
        n = matrix.T.inv()*sp.Matrix([1, -1])
        n = n.applyfunc(sp.cancel)
        equal(n.dot(ea), 1, 'dual forward A')
        equal(n.dot(eb), 1, 'dual forward B')
        signs = (1, -1) if case == 0 else (-1, 1)
        t = (1-sd)/cd if case == 0 else (1+sd)/cd
        equal(n.dot(rotate*ea), signs[0]*t, 'transverse support A')
        equal(n.dot(rotate*eb), signs[1]*t, 'transverse support B')
        # .03 is the exact per-axis support of B_B-B_A in the fixed prior.
        hz = (rational(3, 10)*(n.dot(ea)+n.dot(eb))
              + rational(1, 10)*(signs[0]*n.dot(rotate*ea)+signs[1]*n.dot(rotate*eb))
              + rational(3, 100)*(n[0]+n[1]))
        value = sp.cancel(hz-n.dot(r0))
        compact = (rational(3, 5)+(rational(1, 5) if case == 0 else -rational(51, 50))*t
                   + rational(103, 100)*n[0]-rational(97, 100)*n[1])
        equal(value, compact, 'full body support value')
        if case == 0:
            expected = ((-rational(1, 5)-rational(103, 100)*cb+rational(97, 100)*sb)/(1+sd),
                        (rational(1, 5)-rational(103, 100)*sa-rational(97, 100)*ca)/(1+sd))
        else:
            expected = ((-rational(51, 50)-rational(103, 100)*sb-rational(97, 100)*cb)/(1-sd),
                        (rational(51, 50)-rational(103, 100)*ca+rational(97, 100)*sa)/(1-sd))
        for variable, target in zip((a, b), expected):
            equal(sp.diff(value, variable)*(1+variable**2)/2, target, 'physical-angle derivative')

        # z=tan(H/2), alpha=beta=-H. These expressions are symbolic, not samples.
        c, s = (1-z*z)/(1+z*z), 2*z/(1+z*z)
        offset = 0 if case == 0 else rational(61, 25)
        endpoint = rational(8, 5)+rational(3, 25)*c+4*s
        equal(offset+2*value.subs({a: -z, b: -z}), endpoint, 'attained endpoint')
        if case == 0:
            x, y = rational(2, 5)+rational(103, 100)*c+rational(97, 100)*s, -rational(2, 5)-rational(103, 100)*s+rational(97, 100)*c
        else:
            x, y = rational(59, 50)+rational(103, 100)*s-rational(97, 100)*c, rational(8, 5)-rational(103, 100)*c-rational(97, 100)*s
        world_delta = (r0+matrix*sp.Matrix([x, y])).subs({a: -z, b: -z})-sp.Matrix([rational(3, 100), rational(3, 100)])
        rotated = sp.Matrix([[c, -s], [s, c]])*world_delta
        equal(rotated[0], rational(2, 5), 'contact x in common body frame')
        equal(rotated[1], rational(2, 5), 'contact y in common body frame')
        equal(offset+2*(x-y), endpoint, 'witness physical time')
        records.append({'pair': ['A_'+str(case), 'B_'+str(case)],
                        'support_identity': True, 'both_derivative_identities': True,
                        'same_delta_body_and_motion_contact': True})
    return records


def fixed_certificate():
    pins = {}

    def bind(path, expected=None):
        raw = path.read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        require(expected is None or digest == expected, 'changed frozen input: '+str(path))
        pins[str(path.resolve())] = digest
        return raw

    for name, expected in PINS.items():
        bind(BASE/name, expected)
    bind(SOURCE, 'e294be82cc6277fac462f61450685820f2d9f1b2c49f1c07c814f7abe4f08453')
    for name in ('JOINT_PHASE_CHECK.json', 'SUPPORT_CHECK.json', 'DEPARTURE_CHECK.json', 'SOLVER_RULE_CHECK.json'):
        for path, expected in json.loads((BASE/name).read_text())['input_sha256'].items():
            bind(Path(path), expected)
    joint = json.loads((BASE/'JOINT_PHASE_CHECK.json').read_text())
    rows = {(r['tail'], r['head']): r for r in joint['records']}
    h = Q(1, 500)
    cos_min, denominator_min = 1-h*h/2, 1-2*h
    require(1-(2*h)**2/2 > 0 and cos_min-h > 0 and denominator_min > 0,
            'support sign or invertibility not certified')
    signs = {
        'A0_B0_d_alpha_numerator_upper': -Q('.2')-Q('1.03')*cos_min+Q('.97')*h,
        'A0_B0_d_beta_numerator_upper': Q('.2')+Q('1.03')*h-Q('.97')*cos_min,
        'A2_B2_d_alpha_numerator_upper': -Q('1.02')+Q('1.03')*h-Q('.97')*cos_min,
        'A2_B2_d_beta_numerator_upper': Q('1.02')-Q('1.03')*cos_min+Q('.97')*h,
    }
    require(all(v < 0 for v in signs.values()), 'monotonicity unresolved')
    c = (cos_min, cos_min+h**4/24)
    s = (h-h**3/6, h-h**3/6+h**5/120)

    def linear(constant, cc, ss):
        constant, cc, ss = Q(constant), Q(cc), Q(ss)
        return (constant+cc*c[0 if cc >= 0 else 1]+ss*s[0 if ss >= 0 else 1],
                constant+cc*c[1 if cc >= 0 else 0]+ss*s[1 if ss >= 0 else 0])

    progresses = {'A_0': linear('.4', '1.03', '.97'),
                  'B_0': linear('-.4', '.97', '-1.03'),
                  'A_2': linear('1.18', '-.97', '1.03'),
                  'B_2': linear('1.6', '-1.03', '-.97')}
    lengths = {'A_0': Q(2), 'B_0': Q('.78'), 'A_2': Q(1), 'B_2': Q('.8')}
    for name, (lo, hi) in progresses.items():
        require(Q(1, 8) < lo <= hi < lengths[name]-Q(1, 8), 'witness outside cruise')
    for pair in (('A_0', 'B_0'), ('A_2', 'B_2')):
        eligibility = rows[pair]['joint']
        require(Q(eligibility['max_a']) <= lengths[pair[0]]-Q(1, 8), 'A brake not excluded')
        require(Q(eligibility['min_b']) >= Q(1, 8), 'B acceleration not excluded')
    endpoint = linear('1.6', '.12', '4')
    others = [r for pair, r in rows.items() if pair not in (('A_0', 'B_0'), ('A_2', 'B_2'))]
    require(len(others) == 9 and all(Q(r['refined_upper']) < endpoint[0] for r in others),
            'unhandled pair may dominate')
    require(Q(joint['original_order_lower']) < endpoint[0], 'original order dominates')
    identities = symbolic_identities()
    bind(Path(__file__))
    old = Q(joint['joint_ordered_upper'])
    return {
        'status': 'FIXED_C1_SUPPORT_ENDPOINT_ALGEBRAIC_PASS',
        'scope': 'original prior and frozen C1 only; exact physical contact endpoint, no release authority',
        'symbolic_identities': identities, 'sympy_version': sp.__version__,
        'derivative_numerator_upper_bounds': signs, 'derivative_denominator_lower_bound': denominator_min,
        'support_sign_domain': {'heading_half_width': h, 'cos_difference_lower': 1-2*h*h,
                                'normal_component_numerator_lower': cos_min-h},
        'exact_endpoint_expression': '8/5 + (3/25)*cos(1/500) + 4*sin(1/500)',
        'endpoint_enclosure': endpoint, 'enclosure_width_seconds': endpoint[1]-endpoint[0],
        'old_geometric_upper': old, 'old_upper_minus_exact_endpoint_enclosure': [old-endpoint[1], old-endpoint[0]],
        'witness': {'b_A': ['-.02', '-.01'], 'b_B': ['.01', '.02'], 'delta_A': '-.002', 'delta_B': '-.002',
                    'progress_enclosures': progresses, 'both_contacts_in_rotated_frame': ['.4', '.4'],
                    'contact_type': 'closed body boundary; original strict-interior witness preserved',
                    'task_constant_parameters': True, 'private_online_truth_used': False},
        'other_nine_bounds_reused': [{'pair': [r['tail'], r['head']], 'upper': r['refined_upper']} for r in others],
        'guard_and_coverage': 'reuse frozen start/goal, original order and one-sided inverse qualifications; release numerical guard unchanged',
        'baseline_comparison': {'same_reduced_support_objective_and_sign_bounds': 'generic monotonicity can use the same root certificate',
                                'angle_bisections_required_by_this_certificate': 0,
                                'author_baseline_executed': False, 'whole_cost_advantage': 'NOT_MEASURED',
                                'novel_algorithm_advantage': 'NOT_ESTABLISHED', 'same_feedback_release': 'old negative result retained; no replay'},
        'operations_scope': 'finite symbolic identities and rational signs/Taylor enclosures, no search tree or sampled trajectory',
        'independent_scientific_validation': False, 'successor_run_plan_prepared': False,
        'scientific_runs': 0, 'world_steps': 0, 'task_session_calls': 0, 'training_runs': 0,
        'author_code_calls': 0, 'optimizer_calls': 0, 'input_sha256': pins,
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--write-result', action='store_true')
    args = parser.parse_args()
    output = BASE/'SUPPORT_ENDPOINT_CHECK.json'
    if args.write_result and output.exists():
        raise FileExistsError('preserve receipt: '+str(output))
    try:
        result = fixed_certificate()
    except Exception as exc:
        if args.write_result:
            with output.open('x') as stream:
                json.dump({'status': 'FIXED_C1_SUPPORT_ENDPOINT_FAILED', 'error': type(exc).__name__,
                           'detail': str(exc)}, stream, ensure_ascii=False, indent=2)
                stream.write('\n')
        raise
    if args.write_result:
        with output.open('x') as stream:
            json.dump(result, stream, default=str, ensure_ascii=False, indent=2)
            stream.write('\n')
    print(json.dumps({k: result[k] for k in ('status', 'endpoint_enclosure', 'enclosure_width_seconds',
                     'old_upper_minus_exact_endpoint_enclosure', 'optimizer_calls')}, default=str))
