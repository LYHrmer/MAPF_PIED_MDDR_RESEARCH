"""Whole-plan rule controls; no path search or scientific-run entry point.

These controls select among an incumbent, one supplied complete proposal and
one batch retention proposal. They do not modify an author's solver or claim
turn-optimal search. Every choice is checked by the same full MAPF validator.
"""
import importlib.util
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import sys
from threading import Lock
import types


HERE = Path(__file__).resolve().parent
SCI = '535ee1adf3135ab79565e0b3aa5d189348fe7ab2'


def _local(name, filename):
    spec = importlib.util.spec_from_file_location(name, HERE/filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_fixed_sci_components(repo):
    """Load only a fixed SCI module's class; never construct NativeBackend.

    The byte/commit checks occur for both modules before either is executed.
    Temporary dependency names are restored after import. No sibling worktree
    content or on-disk Python import cache is trusted for these modules.
    """
    exporter = _local('_plan_trace_export', 'export_frozen_trace.py')
    reader = exporter.load_reader(repo, json.loads((HERE/'shared.lock.json').read_bytes()))
    lock = json.loads((HERE/'plan_selection.lock.json').read_bytes())
    expected = {'pp_repair': 'tracks/sci/pp_repair.py',
                'address_backend': 'tracks/sci/address_backend.py'}
    if (lock['schema'] != 'thesis_whole_plan_validator_v1' or lock['commit'] != SCI
            or set(lock['modules']) != set(expected)):
        raise ValueError('unexpected fixed validator lock')
    raw = {}
    for name, path in expected.items():
        pin = lock['modules'][name]
        if pin['commit'] != SCI or pin['path'] != path:
            raise ValueError('unexpected validator dependency pin')
        raw[name] = reader.read_blob(repo, pin)
    saved = {name: sys.modules.get(name) for name in expected}
    loaded = {}
    try:
        for name in expected:
            module = types.ModuleType(name)
            module.__file__ = SCI + ':' + expected[name]
            sys.modules[name] = module
            exec(compile(raw[name], module.__file__, 'exec'), module.__dict__)
            loaded[name] = module
        return loaded
    finally:
        for name, previous in saved.items():
            if previous is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = previous


def load_grid_problem(repo):
    return load_fixed_sci_components(repo)['address_backend'].GridProblem


class InvalidMotionCandidate(ValueError):
    """A supplied path set failed explicit input/discrete validation."""


class InitialMotionCertificationError(ValueError):
    """No certified initial incumbent exists; preserve the structured reason."""

    def __init__(self, reason):
        self.reason = reason
        super().__init__('INITIAL_NOT_CERTIFIED: '+str(reason))


class MotionPlanSelector:
    """Transactional selection within supplied plans, never new path search.

    The initial certificate is established here, not trusted from a caller's
    `certified=True`. A private cloned problem, cardinal headings, immutable
    paths and serialized certificate bind the retained plan to one context.
    A successful replacement is checked against the SAME absolute SharedBudget
    immediately before commit. Fixed callbacks still require the outer process
    supervisor; cooperative polling is not an arbitrary-size real-time proof.
    """

    def __init__(self, problem, paths, model, headings, *, budget, expired_exception,
                 scheduler='local_dependency'):
        import local_scheduler as local
        self.budget, self.expired_exception = budget, expired_exception
        self._lock, self._state, self._version = Lock(), None, 0
        self._local = local

        def prepare():
            if scheduler != 'local_dependency':
                raise ValueError('motion acceptance uses the fixed local dependency scheduler')
            # Clone data through the same fixed GridProblem constructor. The
            # caller cannot invalidate an incumbent by mutating its own problem.
            self._problem = type(problem)(problem.rows, problem.cols,
                                          tuple(problem.blocked), dict(problem.endpoints))
            self._model, self._headings, self._scheduler = model, dict(headings), scheduler
            self._context = dict(rows=self._problem.rows, cols=self._problem.cols,
                blocked=sorted(self._problem.blocked),
                endpoints=sorted(self._problem.endpoints.items()), model=model.record(),
                headings=sorted(self._headings.items()), scheduler=scheduler,
                checker=dict(pair_max_depth=local.PAIR_MAX_DEPTH, pair_max_boxes=local.PAIR_MAX_BOXES),
                timing='RATIONAL_REST_TO_REST_COMMON_TO_BOTH_SCHEDULERS')
            self._context_sha = sha256(self._encode(self._context)).hexdigest()
            return {a: tuple(p) for a, p in paths.items()}

        initial = budget.measure('initial_snapshot', prepare)
        answer = budget.measure('initial_full_certification', lambda: self._compile(initial))
        if not answer.get('certified_nominal_reference'):
            raise InitialMotionCertificationError(answer.get('reason'))
        raw = budget.measure('initial_state_serialization', lambda: self._pack(initial, answer))
        budget.check()
        self._state = raw

    @staticmethod
    def _encode(value):
        return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()

    def _compile(self, paths):
        return self._local.compile_schedule(self._problem, paths, self._model,
            self._headings, self._scheduler, checkpoint=self.budget.check, measure=self._measure_motion_stage)

    def _measure_motion_stage(self, stage, callback):
        try:
            return self.budget.measure(stage, callback)
        except Exception:
            # SharedBudget itself remains the fixed SCI implementation. This
            # diagnostic only records the deepest observed failing motion stage;
            # it does not change its clock, deadline or exception classification.
            if getattr(self.budget, 'motion_first_failed_stage', None) is None:
                self.budget.motion_first_failed_stage = stage
            raise

    def _prepare_candidate(self, paths):
        try:
            if not isinstance(paths, dict):
                raise ValueError('candidate must be an explicit complete path mapping')
            candidate = {}
            for agent, path in paths.items():
                self.budget.check()
                if type(agent) is not int or not isinstance(path, (tuple, list)):
                    raise ValueError('integer agent and concrete path sequence required')
                candidate[agent] = tuple(path)
            if self._problem.validate(candidate, complete=True) is not True:
                raise ValueError('complete discrete validator did not return True')
            return candidate
        except ValueError as error:
            raise InvalidMotionCandidate(str(error)) from error

    def _pack(self, paths, answer):
        if answer.get('status') != 'CERTIFIED_NOMINAL_REFERENCE' or not answer.get('schedule'):
            raise ValueError('a complete certified schedule is required')
        completion = answer['schedule']['completion_exact_s']
        if set(completion) != set(self._problem.ids):
            raise ValueError('complete exact completion coverage is required')
        values = [Fraction(v) for v in completion.values()]
        if any(v < 0 for v in values):
            raise ValueError('negative exact completion')
        paths_record = {str(a): list(p) for a, p in paths.items()}
        return self._encode(dict(paths=paths_record, motion=answer,
            objective_exact_s=str(sum(values, Fraction(0))),
            paths_sha256=sha256(self._encode(paths_record)).hexdigest(),
            context_sha256=self._context_sha, context=self._context))

    def snapshot(self):
        with self._lock:
            if self._state is None:
                raise ValueError('initial motion certificate has not been established')
            # Each caller receives a detached value; changing it cannot alter
            # the next transaction's certified incumbent or model identity.
            value = json.loads(self._state)
            value['version'] = self._version
            return value

    def consider(self, paths, *, label, use_lower_bound=True):
        """Commit only a fully certified strict decrease in exact sum T_i."""
        budget = self.budget
        started, cpu = budget.clock_ns(), budget.cpu_clock_ns()
        wall_before, cpu_before = dict(budget.stage_wall_ns), dict(budget.stage_cpu_ns)
        with self._lock:
            before, version = self._state, self._version
        if before is None:
            raise ValueError('cannot consider a candidate without a certified initial plan')
        old = json.loads(before)
        old_j, lower, candidate_j = Fraction(old['objective_exact_s']), None, None
        status, reason = 'CANDIDATE_FAILED', None
        try:
            if type(use_lower_bound) is not bool or not isinstance(label, str) or not label:
                raise ValueError('explicit candidate label and boolean bound policy required')
            candidate = budget.measure('candidate_snapshot_and_discrete_validation',
                lambda: self._prepare_candidate(paths))
            if use_lower_bound:
                lower = budget.measure('primitive_lower_bound', lambda:
                    self._local.primitive_completion_lower_bound(self._problem, candidate,
                        self._model, self._headings, checkpoint=budget.check))
            if lower is not None and lower >= old_j:
                status, reason = 'LOWER_BOUND_REJECTED', 'L >= incumbent exact sum of completion times'
            else:
                answer = budget.measure('candidate_full_evaluation', lambda: self._compile(candidate))
                if not answer.get('certified_nominal_reference'):
                    status, reason = 'CERTIFICATE_NOT_ESTABLISHED', answer.get('reason')
                    if reason and reason.get('kind') == 'INVALID_INPUT_OR_UNREPRESENTABLE_SCHEDULE':
                        # The complete discrete input and unchanged model were
                        # checked already; do not hide an internal construction
                        # error as an ordinary geometrically inconclusive plan.
                        status = 'IMPLEMENTATION_FAILED'
                else:
                    packed = budget.measure('candidate_state_serialization',
                                             lambda: self._pack(candidate, answer))
                    candidate_j = Fraction(json.loads(packed)['objective_exact_s'])
                    if candidate_j >= old_j:
                        status, reason = 'NO_STRICT_IMPROVEMENT', 'candidate exact J >= incumbent J'
                    else:
                        def commit():
                            with self._lock:
                                budget.check()
                                if self._state is not before:
                                    return False
                                self._state, self._version = packed, version+1
                                return True
                        committed = budget.measure('commit', commit, check_after=False)
                        status = 'ACCEPTED' if committed else 'STALE_INCUMBENT'
                        reason = 'complete certificate and exact strict improvement' if committed else 'incumbent changed'
        except (self.expired_exception, TimeoutError) as error:
            status, reason = 'BUDGET_CENSORED', str(error)
        except InvalidMotionCandidate as error:
            status, reason = 'INVALID_CANDIDATE', type(error).__name__+': '+str(error)
        except Exception as error:
            # Retain the private certificate but make the software error a hard
            # batch failure; the runner must not relabel it ordinary no-gain.
            status, reason = 'IMPLEMENTATION_FAILED', type(error).__name__+': '+str(error)
        after = self.snapshot()
        return dict(label=label, status=status, reason=reason, use_lower_bound=use_lower_bound,
            incumbent_before_exact_s=str(old_j),
            lower_bound_exact_s=None if lower is None else str(lower),
            candidate_objective_exact_s=None if candidate_j is None else str(candidate_j),
            incumbent_after_exact_s=after['objective_exact_s'],
            retained_paths_sha256=after['paths_sha256'], version_before=version, version_after=after['version'],
            stage_wall_ns={k: v-wall_before.get(k, 0) for k, v in budget.stage_wall_ns.items()
                           if v != wall_before.get(k, 0)},
            stage_cpu_ns={k: v-cpu_before.get(k, 0) for k, v in budget.stage_cpu_ns.items()
                          if v != cpu_before.get(k, 0)},
            transaction_wall_ns=budget.clock_ns()-started,
            transaction_cpu_ns=budget.cpu_clock_ns()-cpu,
            scope='SUPPLIED_CANDIDATE_SET_ONLY_NO_SEARCH_OR_OPTIMALITY',
            new_search_calls=0, common_end_received=False)


def select_complete_plan(problem, incumbent, proposal, *, rule):
    """Select one fully checked plan under an explicit secondary objective.

    `soc_only` considers incumbent/proposal only and retains the incumbent on
    equal SOC. `preserve_equal_cost` additionally offers one simultaneous batch
    restoration of equal-cost changed paths, breaking equal SOC by fewer changed
    paths. `turn_aware` offers the same three plans, breaking equal SOC by the
    internal quarter-turn count, then by fewer changes. Neither rule enumerates
    path mixtures nor establishes a motion-time or continuous-safety guarantee.

    `problem` must expose the common complete validator plus rows/cols/blocked.
    A validator error rejects the whole proposal; it never partially commits it.
    The wrapper must include these checks and selection in the total run budget.
    This function has no benchmark runner and is currently tested on fixtures.
    """
    if rule not in ('soc_only', 'preserve_equal_cost', 'turn_aware'):
        raise ValueError('unknown whole-plan selection rule')
    audit = _local('_plan_shape', 'inspect_sci_paths.py')
    base = {agent: tuple(path) for agent, path in incumbent.items()}
    candidate = {agent: tuple(path) for agent, path in proposal.items()}
    plans = [('incumbent', base), ('proposal', candidate)]
    if rule != 'soc_only' and set(candidate) == set(base):
        retained = {a: base[a] if len(base[a]) == len(path) else path
                    for a, path in candidate.items()}
        # Exactly one whole-plan proposal; do not greedily accept per-agent swaps.
        plans.append(('retain_equal_cost_batch', retained))
    checked, best, best_key = [], None, None
    for label, paths in plans:
        try:
            # Each selectable record receives an explicit complete check.
            if problem.validate(paths, complete=True) is not True:
                raise ValueError('complete validation did not return True')
            soc = sum(len(path)-1 for path in paths.values())
            turns = sum(audit.path_shape(list(path), problem.rows, problem.cols,
                        problem.blocked)['internal_quarter_turns'] for path in paths.values())
            changed = sum(paths[a] != base[a] for a in base)
            key = ((soc,) if rule == 'soc_only' else (soc, changed) if rule == 'preserve_equal_cost'
                   else (soc, turns, changed))
            checked.append({'name': label, 'valid': True, 'soc': soc,
                            'internal_quarter_turns': turns, 'changed_paths': changed})
            if best_key is None or key < best_key:
                best, best_key = (label, paths), key
        except ValueError as error:
            if label == 'incumbent':
                raise
            checked.append({'name': label, 'valid': False, 'reason': str(error)})
    # Independent final full check protects the exact returned set, including
    # permanent goal holds. Validity is discrete MAPF only.
    if problem.validate(best[1], complete=True) is not True:
        raise ValueError('selected full plan failed final validation')
    return {'rule': rule, 'selected': best[0], 'paths': dict(best[1]), 'candidates': checked,
            'scope': 'DISCRETE_WHOLE_PLAN_CONTROL_ONLY', 'final_validated': True,
            'continuous_safety_checked': False, 'search_calls': 0}
