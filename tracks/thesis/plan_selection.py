"""Whole-plan rule controls; no path search or scientific-run entry point.

These controls select among an incumbent, one supplied complete proposal and
one batch retention proposal. They do not modify an author's solver or claim
turn-optimal search. Every choice is checked by the same full MAPF validator.
"""
import importlib.util
import json
from pathlib import Path
import sys
import types


HERE = Path(__file__).resolve().parent
SCI = '535ee1adf3135ab79565e0b3aa5d189348fe7ab2'


def _local(name, filename):
    spec = importlib.util.spec_from_file_location(name, HERE/filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_grid_problem(repo):
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
        return loaded['address_backend'].GridProblem
    finally:
        for name, previous in saved.items():
            if previous is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = previous


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
