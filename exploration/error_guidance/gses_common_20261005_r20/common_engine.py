"""Unchanged Improved GSES ordering surrogate, inherited R19 execution guard.

Arrival states and integer/unit-gap semantics are explicit. This adapter does
not claim equivalence to arbitrary continuous SADG completion objectives.
"""
from dataclasses import dataclass
from pathlib import Path
import copy
import hashlib
import importlib.util
import json
import math
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
R19 = HERE.parent / 'sadg_structural_20261005_r19'
R19_SHA = '55c5e99ce1e17c82e73f41545ca536cf6b449eefbda648d1f5e1b027ad1de7c2'
if hashlib.sha256((R19/'engine.py').read_bytes()).hexdigest() != R19_SHA:
    raise RuntimeError('R19 frozen inheritance source changed')
sys.path.insert(0, str(R19))
spec = importlib.util.spec_from_file_location('r20_frozen_r19_engine', R19/'engine.py')
r19 = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = r19
spec.loader.exec_module(r19)
from fraction_oracle import objective, enumerate_legal

write_json = r19.write_json
file_sha = r19.file_sha
NoQueryPolicy = r19.NoQueryPolicy
DensePositionPolicy = r19.DensePositionPolicy


@dataclass(frozen=True)
class EngineConfig(r19.EngineConfig):
    gses_quantum: float = 1.
    gses_max_new_calls: int = 4


def encode_arrivals(snapshot, quantum):
    """Public predictions only: action END maps to arrival index i+1.

    Native unit type2 cost represents the entering head action's one-tick
    movement. Different head durations make it an ordering surrogate. The
    exact event executor always retains tail-END -> head-START dependencies.
    """
    if not math.isfinite(quantum) or quantum <= 0:
        raise ValueError('positive finite quantum required')
    by_agent = {}
    for v in snapshot['vertices']:
        by_agent.setdefault(v['agent'], []).append(v)
    paths, current, offsets, type1, uid_map = [], [], [], [], {}
    vertex_by_uid = {v['uid']: v for v in snapshot['vertices']}
    total = 0
    for aid in sorted(by_agent):
        row = sorted(by_agent[aid], key=lambda v: v['index'])
        points = [row[0]['path'][0]] + [v['path'][-1] for v in row]
        if any(any(abs(x-round(x)) > 1e-8 for x in p) for p in points):
            raise ValueError('native Graph path requires integral coordinates/timestamps')
        paths.append([[[round(p[0]), round(p[1])], round(p[2])] for p in points])
        offsets.append(total)
        completed = 0
        for i, v in enumerate(row):
            if v['status'] == 'COMPLETED':
                if i != completed:
                    raise ValueError('completed actions must be a prefix')
                completed += 1
            uid_map[v['uid']] = total+i+1
            duration = v['duration']*(1-v['progress']) if v['status'] == 'IN_PROGRESS' else v['duration']
            weight = max(1, math.ceil(duration/quantum-1e-12))
            type1.append([total+i, total+i+1, weight])
        current.append(completed)
        total += len(points)
    type2, mapping = [], []
    for group in snapshot['groups']:
        for j, dep in enumerate(group['dependencies']):
            tail, head = dep['active']
            # Satisfied dependencies cannot constrain the live suffix or switch.
            pruned = vertex_by_uid[tail]['status'] == 'COMPLETED'
            active = [uid_map[tail], uid_map[head], 1]
            forward = [uid_map[u] for u in dep['forward']]+[1]
            reverse = None if dep['reverse'] is None else [uid_map[u] for u in dep['reverse']]+[1]
            if reverse is not None and reverse != [forward[1]+1, forward[0]-1, 1]:
                raise ValueError('SADG reverse family differs from STPG adjacent inverse')
            if not pruned:
                type2.append(active)
            mapping.append(dict(group=group['uid'], dependency=j, active=active,
                                forward=forward, reverse=reverse, pruned_satisfied=pruned))
    if len({tuple(e) for e in type2}) != len(type2):
        raise ValueError('duplicate translated dependency family')
    graph = dict(paths=paths, current=current, offsets=offsets,
                 type1=sorted(type1), type2=sorted(type2))
    return dict(solver_graph=graph, mapping=mapping, uid_map=uid_map,
                quantum=quantum, duration_rounding='ceil_minimum_one_tick',
                native_type2_ticks=1, objective_contract='integer arrival ordering surrogate')


def lift_candidate(before, encoded, selected):
    """All-or-nothing lift: full family membership and uniform group choices."""
    old = encoded['solver_graph']
    if any(selected[k] != old[k] for k in ('paths', 'current', 'offsets', 'type1')):
        raise ValueError('author changed immutable paths/current/type1')
    chosen = {tuple(e) for e in selected['type2']}
    if len(chosen) != len(selected['type2']):
        raise ValueError('duplicate candidate edge')
    after = copy.deepcopy(before)
    groups = {g['uid']:g for g in after['groups']}
    used = set()
    for entry in encoded['mapping']:
        if entry['pruned_satisfied']:
            continue
        dep = groups[entry['group']]['dependencies'][entry['dependency']]
        f = tuple(entry['forward'])
        r = None if entry['reverse'] is None else tuple(entry['reverse'])
        members = [e for e in (f, r) if e is not None and e in chosen]
        if len(members) != 1:
            raise ValueError('candidate omitted/duplicated an original direction family')
        edge = members[0]
        if edge in used:
            raise ValueError('candidate edge shared by two families')
        used.add(edge)
        desired = dep['forward'] if edge == f else dep['reverse']
        if desired != dep['active']:
            dep['b'] = not dep['b']
            dep['active'] = desired
    if used != chosen:
        raise ValueError('candidate introduced an unknown direction')
    for group in after['groups']:
        if len({d['b'] for d in group['dependencies']}) > 1:
            raise ValueError('author grouping produced a partial SADG group switch')
    return after


class GSESCommonSimulator(r19.Simulator):
    """run(policy) uses the identical event/END/POSITION/guard implementation.

    Caller must supply common EngineConfig with explicit evidence/output/cache
    directories. Runtime invocation cap is mechanical, not a benchmark stop.
    """
    def __init__(self, case, disturbance=None, seed=0, *, predictor=None, config=None, **kwargs):
        cfg = config or EngineConfig(**kwargs)
        if not isinstance(cfg, EngineConfig):
            raise TypeError('use common_engine.EngineConfig')
        if not cfg.output_dir or not cfg.cache_dir:
            raise ValueError('auditable output_dir and cache_dir are required')
        self.gses_registration = json.loads((HERE/'valid_nominal_schedule/PHASE1_REGISTRATION.json').read_text())
        reg = self.gses_registration
        if file_sha(reg['binary']) != reg['binary_sha256']:
            raise RuntimeError('pinned author ELF changed')
        for name, value in reg['author_source'].items():
            if file_sha(Path(reg['author_source_root'])/name) != value:
                raise RuntimeError('pinned author source changed: '+name)
        self.gses_new_calls = 0
        super().__init__(case, disturbance, seed, predictor=predictor, config=cfg)

    def _solve(self, gate):
        self._update_predictor()
        before = r19.graph_snapshot(self.graph, self.config.horizon)
        saved_heads = {g.get_uid():(g.first_head_active,getattr(g,'first_head_inactive',None))
                       for gs in self.graph.switchable_dep_groups.values() for g in gs}
        before_ref = self.store.put_graph(before)
        record = dict(gate_index=gate['gate_index'], time=self.now, before_ref=before_ref,
                      prediction_keys=dict(self._last_predictions), adopted=False,
                      new_author_calls=0, new_solver_seconds=0., new_author_wall_seconds=0.,
                      model=dict(reference_solver_seconds=0.,reference_author_seconds=0.,status='NOT_CALLED'))
        try:
            encoded = encode_arrivals(before, self.config.gses_quantum)
            record['encoded_public_input_ref'] = self.store.put(encoded)
            semantic_key = r19.digest(dict(graph=encoded['solver_graph'],
                binary_sha256=self.gses_registration['binary_sha256'],method='Improved_GSES'))
            record['input_key'] = semantic_key
            cache_path = self.cache/(semantic_key+'.json')
            reused = cache_path.exists()
            if reused:
                cached = json.loads(cache_path.read_text())
                if cached['input_key'] != semantic_key:
                    raise RuntimeError('cache key mismatch')
                if r19.digest(cached['solver_graph']) != r19.digest(encoded['solver_graph']):
                    raise RuntimeError('cache graph mismatch')
                reply = self.store.get(cached['reply_ref']) if cached['reply_ref'] else None
                receipt = cached['receipt']
            else:
                if self.gses_new_calls >= self.config.gses_max_new_calls:
                    raise RuntimeError('explicit mechanical author call cap reached')
                out = self.output_dir/'native'/('gate_'+str(gate['gate_index']))
                if out.exists():
                    raise RuntimeError('refuse unfinished/repeated native directory')
                out.mkdir(parents=True)
                input_path = out/'input.json'
                write_json(input_path, dict(solver_graph=encoded['solver_graph']))
                write_json(out/'STARTED.json',dict(input_key=semantic_key,time=self.now))
                command = ['rtk','proxy',self.gses_registration['binary'],str(input_path),
                           'Improved_GSES',str(out/'reply.json')]
                start = time.perf_counter()
                self.gses_new_calls += 1
                record['new_author_calls'] = 1
                try:
                    proc = subprocess.run(command,capture_output=True,text=True,timeout=20)
                    rc,error,stdout,stderr = proc.returncode,None,proc.stdout,proc.stderr
                except subprocess.TimeoutExpired as exc:
                    rc,error,stdout,stderr = None,'HostTimeout',exc.stdout or b'',exc.stderr or b''
                wall = time.perf_counter()-start
                for name,value in [('stdout',stdout),('stderr',stderr)]:
                    (out/(name+'.txt')).write_text(value.decode(errors='replace') if isinstance(value,bytes) else value)
                receipt = dict(command=command,returncode=rc,error=error,wall_seconds=wall,
                               input_sha256=file_sha(input_path),binary_sha256=self.gses_registration['binary_sha256'])
                write_json(out/'receipt.json',receipt)
                reply = json.loads((out/'reply.json').read_text()) if (out/'reply.json').exists() else None
                cached = dict(input_key=semantic_key,solver_graph=encoded['solver_graph'],receipt=receipt,
                              reply_ref=self.store.put(reply) if reply else None)
                write_json(cache_path,cached)
                record['new_author_wall_seconds'] = wall
            record.update(cache_reused=reused,cache_path=str(cache_path),cache_sha256=file_sha(cache_path),
                          native_receipt=receipt,author_reply_ref=cached['reply_ref'])
            record['model'] = dict(status=reply['status'] if reply else 'AuthorError',
                reference_solver_seconds=reply['search_elapsed_us']/1e6 if reply else 0.,
                reference_author_seconds=receipt['wall_seconds'],original_search_cap_seconds=16,
                wrapper_watchdog_seconds=20)
            record['new_solver_seconds'] = 0. if reused else record['model']['reference_solver_seconds']
            if not reply or reply['status'] != 'Succ':
                raise RuntimeError('author returned no successful candidate')
            record['native_graph_objective'] = objective(reply['selected_graph'])
            candidate = lift_candidate(before,encoded,reply['selected_graph'])
            record['candidate_ref'] = self.store.put_graph(candidate)
            check = r19.adoption_guard(before,candidate)
            record['guard'] = check
            if not check['passed']:
                raise RuntimeError('common adoption guard rejected: '+str(check))
            self._restore_directions(candidate)
            actual = r19.graph_snapshot(self.graph,self.config.horizon)
            actual_check = r19.adoption_guard(before,actual)
            if not actual_check['passed']:
                raise RuntimeError('post-lift guard rejected')
            record['adopted'] = True
        except Exception as exc:
            self._restore_directions(before,saved_heads)
            record['error'] = repr(exc)
            self.failures.append(dict(time=self.now,kind='GSES_SURROGATE_FALLBACK',error=repr(exc)))
        record['after_ref'] = self.store.put_graph(r19.graph_snapshot(self.graph,self.config.horizon))
        self.solves.append(record)

    def run(self, policy=None, probe_override=None):
        result = super().run(policy,probe_override)
        result.update(schema='r20-gses-common-surrogate-v1',
            optimizer=dict(name='Improved_GSES',commit=self.gses_registration['author_commit'],
                binary_sha256=self.gses_registration['binary_sha256'],adapter_sha256=file_sha(__file__)),
            optimizer_contract='integer ceil type1 durations and unit type2 arrival gap; not equivalent to arbitrary continuous SADG objectives',
            executor_contract='unchanged R19 point-event executor, original SADG dependency release and full adoption guard')
        write_json(self.output_dir/'episode.json',result)
        return result
