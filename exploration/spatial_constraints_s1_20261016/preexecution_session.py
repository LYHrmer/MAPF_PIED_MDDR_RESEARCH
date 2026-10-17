"""In-process joint installation of an already certified complete v2 schedule.

This event adapter assumes exclusive access to the supplied Plant objects and
one synchronous callback; it is not a distributed atomic-start protocol. The
caller drives prepare/capture/delivery/launch and supplies any process budgets.
The physical task origin is zero. All chains share a later exact epoch; their
preceding stationary wait is covered by v2's zero-drift initial occupancy.
Calling these methods executes source feedback/control and needs run authority.
"""
from contextlib import contextmanager
from copy import deepcopy
from fractions import Fraction as Q
from itertools import combinations
from pathlib import Path
import hashlib
import json

from composition import Chain, CONDITION, contract, exact
from preexecution_schedule import ScheduleIncumbent, _code_identity, _digest
from timed import CLOCK_CONTRACT, Plant, SharedClock, Trajectory
from timed_protocol import Binding, Costs, TaskInbox, TaskPacket, TaskProducer, task_receipt


def _wire(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def _channel(wires):
    return {'count': len(wires), 'bytes': sum(map(len, wires)),
            'sha256': hashlib.sha256(b'\n'.join(wires)).hexdigest()}


def _input_identity(manager):
    return _digest({'specs': manager._specs, 'world': manager._world,
                    'obstacles': manager._obstacles, 'order_declaration': manager._declaration,
                    'group_catalog': None if manager._catalog is None else manager._catalog.sha256,
                    'order_mode': manager._order_mode, 'separation_gap': manager._gap,
                    'source': contract(), 'budget': manager._budget.__dict__})


class JointTaskSession:
    """Trusted local endpoints; completion requires their delivered public END.

    prepare(now) registers every exact program and emits ordinary STOPPED
    packets. receive(packet, now=...) admits a delivered packet. launch(now)
    requires now == epoch and fresh STOPPED feedback for EVERY registered
    program, then installs all committed clock copies in one callback. A
    STOPPED packet alone never registers readiness. capture(now) supplies
    later public packets; receipt() closes only this ledger, never the clocks.

    Plant instances and their task-initial parameters are retained. Their
    owner must not mutate them concurrently or replace source methods. Runtime
    failures remain in the receipt and never silently pause a committed chain.
    """
    def __init__(self, manager, plants, *, task, epoch, horizon,
                 feedback_delay, feedback_ttl, engine='preexecution_joint', costs=None):
        self.costs = costs if costs is not None else Costs()
        with self.costs.measure('joint_session_constructor_and_qualification'):
            if type(manager) is not ScheduleIncumbent:
                raise ValueError('live exact ScheduleIncumbent required, not a JSON safety assertion')
            self._manager, self._plan = manager, manager.incumbent
            if self._plan is None:
                raise ValueError('NO_CERTIFIED_INCUMBENT')
            self._code = _code_identity()
            self._session_code = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
            self._qualify()
            if not isinstance(task, str) or not task or not isinstance(engine, str) or not engine:
                raise ValueError('nonempty task and engine identifiers required')
            self.task, self.engine = task, engine
            self.epoch, self.horizon = exact(epoch), exact(horizon)
            self._delay, self._ttl = exact(feedback_delay), exact(feedback_ttl)
            if self.epoch <= 0 or self._delay < 0 or self._ttl <= 0 or self._delay > self._ttl:
                raise ValueError('positive future epoch/TTL and delay within TTL required')
            self._robots = tuple(sorted(self._plan['scheduled_specs']))
            if not isinstance(plants, dict) or set(plants) != set(self._robots):
                raise ValueError('all certified participants must supply their existing Plant')
            self._plants = dict(plants)
            self._trajectories = {r: Trajectory(r, Chain.build(self._plan['scheduled_specs'][r]))
                                  for r in self._robots}
            if any(t.chain.duration <= 0 for t in self._trajectories.values()):
                raise ValueError('zero-duration programs have no qualified joint resume/END')
            if self.horizon < self.epoch+max(t.chain.duration for t in self._trajectories.values()):
                raise ValueError('task-origin horizon must cover epoch plus complete program duration')
            self._clocks = {}
            for r, p in self._plants.items():
                if (type(p) is not Plant or type(p.clock) is not SharedClock
                        or p.trajectory != self._trajectories[r]
                        or p.clock.trajectory != p.trajectory
                        or p.clock.running or p.clock.locked or p.clock.saved != 0 or p.clock.at != 0
                        or p.clock.completed is not None or p.clock.phase(Q(0)) != 0):
                    raise ValueError('unaltered full certified trajectory and uncommitted phase-zero Plant required')
                self._clocks[r] = p.clock
            self.commitment = _digest({'schedule': self._plan['schedule_sha256'], 'task': task,
                                       'input': self._plan['input_sha256'], 'code': self._code,
                                       'session_code': self._session_code, 'robots': self._robots,
                                       'epoch': self.epoch, 'horizon': self.horizon,
                                       'delay': self._delay, 'ttl': self._ttl,
                                       'condition': CONDITION, 'clock': CLOCK_CONTRACT})
            self._bindings = {r: Binding(task, r, r+'_TASK', CONDITION, self.commitment) for r in self._robots}
            self._producers = {r: TaskProducer(b, delay=self._delay) for r, b in self._bindings.items()}
            self._inboxes = {r: TaskInbox(self._bindings[r], self._trajectories[r].chain.duration)
                             for r in self._robots}
            self._registered, self._latest, self._generated = {}, {}, {}
            self._packets, self._feedback_wires, self._command_wires = [], [], []
            self._sent_wires, self._incoming_wires, self._evaluation_records = [], [], []
            self._receive_attempts, self._failures, self._commands = [], [], []
            self._completion, self._input_ack = dict.fromkeys(self._robots), dict.fromkeys(self._robots)
            self._frontier, self._prepared, self._launched, self._closed = Q(0), False, False, False
            self._prepare_attempted, self._launch_attempted = False, False

    def _qualify(self):
        p, m = self._plan, self._manager
        unsigned = {k: v for k, v in p.items() if k != 'schedule_sha256'}
        if (p.get('schedule_sha256') != _digest(unsigned) or m.incumbent != p
                or p.get('input_sha256') != m._identity or _input_identity(m) != m._identity
                or p.get('code_sha256') != m._code or m._code != self._code
                or self._code != _code_identity()
                or hashlib.sha256(Path(__file__).read_bytes()).hexdigest() != self._session_code):
            raise ValueError('current incumbent/input/source/checker identity changed')
        v, order = p['validation'], p['declared_orders']
        catalog_order = (m._catalog is not None
                         and p.get('group_catalog_sha256') == m._catalog.sha256
                         and order.get('group_catalog_sha256') == m._catalog.sha256
                         and order.get('physical_event_order') == 'PHYSICAL_EXIT_ENTRY_ORDERS_VERIFIED_BY_EXACT_TIMES'
                         and order.get('semantics') == 'WINDOW_CLAUSE_LAGS'
                         and p['order_construction'].get('status') == 'BUILT_ACTION_DWELL_WINDOW_CLAUSES'
                         and p['order_construction'].get('catalog_sha256') == m._catalog.sha256
                         and p['order_construction'].get('contract_sha256') == m._order.sha256
                         and bool(order.get('lag_provenance'))
                         and order['lag_provenance'] == p['order_construction'].get('proof_sha256'))
        robots = tuple(sorted(p['scheduled_specs']))
        pair_keys = {json.dumps(pair, separators=(',', ':')) for pair in combinations(robots, 2)}
        if (not 2 <= len(robots) <= 3 or p.get('execution_status') != 'NOT_EXECUTED'
                or p.get('problem_admissibility') != 'DECLARED_PRESTART_ORDERS_AND_CONDITIONAL_GEOMETRY'
                or order.get('valid') is not True
                or (not catalog_order if m._catalog is not None
                    else order.get('action_graph_acyclic') is not True)
                or order.get('contract_sha256') != m._order.sha256
                or order.get('specs_sha256') != _digest(m._specs)
                or p.get('static_obstacles_checked') is not True
                or p.get('obstacle_scope') != 'EXPLICIT_CLOSED_AXIS_ALIGNED_RECTANGLES_ONLY'
                or v.get('status') != 'CERTIFIED_CONDITIONAL_GEOMETRY'
                or v.get('coverage_certified') != 'ALL_TASK_SHARED_INITIAL_PARAMETERS_CONTINUOUS_TIME_AND_HOLDS'
                or v.get('condition') != 'COMMON_ZERO_JITTER_EPOCH_IMMUTABLE_V2_CHAINS'
                or v.get('unchecked_pairs') != [] or set(v['pairs']) != pair_keys
                or any(row.get('status') != 'CERTIFIED_SEPARATED' for row in v['pairs'].values())):
            raise ValueError('complete static/order/all-pair conditional certificate required')

    def _check(self):
        self._qualify()
        for r, p in self._plants.items():
            c = p.clock
            if (type(p) is not Plant or c is not self._clocks[r]
                    or p.trajectory != self._trajectories[r] or c.trajectory != p.trajectory
                    or c.saved != 0 or c.completed is not None
                    or c.running is not self._launched or c.locked is not self._launched
                    or (self._launched and c.at != self.epoch)
                    or (not self._launched and (c.at != 0 or c.phase(Q(0)) != 0))):
                raise ValueError('committed program/clock changed; no automatic pause or repair')

    @contextmanager
    def _event(self, name, now):
        with self.costs.measure(name):
            try:
                if self._closed:
                    raise ValueError('ledger already closed')
                t = exact(now)
                if not self._frontier <= t <= self.horizon+self._delay:
                    raise ValueError('event time reversed or beyond declared delivery horizon')
                self._check()
                self._frontier = t
                yield t
            except BaseException as exc:
                self._failures.append({'event': name, 'now': str(now),
                                       'reason': type(exc).__name__+': '+str(exc)})
                raise

    def _command(self, kind, now):
        for r in self._robots:
            row = {'kind': kind, 'task': self.task, 'robot': r, 'now': str(now),
                   'epoch': str(self.epoch), 'commitment': self.commitment,
                   'program_sha256': _digest(self._plan['scheduled_specs'][r])}
            self._commands.append(row)
            wire = _wire(row)
            self._command_wires.append(wire)
            self._sent_wires.append(wire)

    def _capture(self, now):
        packets = []
        for r in self._robots:
            producer = self._producers[r]
            if producer.ended:
                continue
            # Only this local source endpoint observes its private state.
            p = producer.capture(self._plants[r].observe(now), now=now)
            wire = p.wire()
            self._generated[(r, p.seq)] = wire
            self._feedback_wires.append(wire)
            self._sent_wires.append(wire)
            packets.append(p)
            # Local evaluation-only side channel: never read by any guard.
            # observe() already evaluates internally; this second evaluation
            # is deliberate, same-time, and charged rather than hidden.
            with self.costs.measure('controller_evaluation_only_capture'):
                self._evaluation_records.append({'robot': r, 'capture': str(now),
                                                 'data': self._plants[r].evaluate(now)})
        return tuple(packets)

    @property
    def evaluation_records(self):
        """Export labels only after ledger closure; not an online information API."""
        if not self._closed:
            raise ValueError('evaluation labels are unavailable to the active session')
        return deepcopy(self._evaluation_records)

    def prepare(self, now):
        with self._event('joint_prepare_and_public_capture', now) as t:
            if self._prepare_attempted or self._launched or t >= self.epoch:
                raise ValueError('one pre-epoch prepare only; no silent retry')
            self._prepare_attempted = True
            self._command('PREPARE', t)
            self._registered = {r: (_digest(self._plan['scheduled_specs'][r]), self._clocks[r])
                                for r in self._robots}
            packets = self._capture(t)
            if len(packets) != len(self._robots) or any(p.state != 'STOPPED' for p in packets):
                raise ValueError('local prepared programs must still report phase-zero STOPPED')
            self._prepared = True
            return packets

    def capture(self, now):
        with self._event('joint_public_source_capture', now) as t:
            if not self._prepared or t > self.horizon or (not self._launched and t >= self.epoch):
                raise ValueError('capture requires prepared programs and the declared task horizon')
            return self._capture(t)

    def receive(self, packet, *, now):
        # Include rejected/replayed arrivals even if subsequent identity/time
        # preflight fails. Non-packet objects have no defined protocol bytes.
        if self._closed:
            raise ValueError('ledger already closed')
        with self.costs.measure('joint_incoming_wire_accounting'):
            attempt = {'now': str(now), 'accepted': False, 'bytes': None, 'sha256': None}
            self._receive_attempts.append(attempt)
            if type(packet) is TaskPacket:
                try:
                    wire = packet.wire()
                except Exception as exc:
                    self._failures.append({'event': 'incoming_wire_serialization', 'now': str(now),
                                           'reason': type(exc).__name__+': '+str(exc)})
                    raise
                self._incoming_wires.append(wire)
                attempt.update(bytes=len(wire), sha256=hashlib.sha256(wire).hexdigest())
        with self._event('joint_public_feedback_validation', now) as t:
            if type(packet) is not TaskPacket:
                raise ValueError('typed locally produced public packet required')
            wire, r = packet.wire(), packet.binding.robot
            if not self._prepared or self._generated.get((r, packet.seq)) != wire:
                raise ValueError('packet was not emitted by a registered local source endpoint')
            inbox = self._inboxes[r]
            inbox.validate(packet, now=t)
            capture, lo, hi = exact(packet.capture), exact(packet.phase_lo), exact(packet.phase_hi)
            if packet.kind != 'END' and t-capture > self._ttl:
                raise ValueError('stale public state; no new launch qualification')
            if not self._launched:
                if packet.state != 'STOPPED' or capture >= self.epoch:
                    raise ValueError('prepare requires an uncommitted stopped program')
            else:
                if packet.state == 'STOPPED' or capture < self.epoch:
                    raise ValueError('committed chain requires actual-input ACK or END')
                duration = self._trajectories[r].chain.duration
                if not lo <= min(duration, capture-self.epoch) <= hi:
                    raise ValueError('public phase inconsistent with common zero-jitter epoch')
                if packet.kind == 'END' and exact(packet.completion_time) != self.epoch+duration:
                    raise ValueError('END inconsistent with complete immutable program')
            bounds = self._trajectories[r].box(lo, hi, body=False)
            x, y, loc = exact(packet.observed_x), exact(packet.observed_y), exact(packet.localization_bound)
            if not (bounds[0]-loc <= x <= bounds[1]+loc and bounds[2]-loc <= y <= bounds[3]+loc):
                raise ValueError('public localization outside declared source/phase range')
            inbox.admit(packet, now=t)
            self._latest[r] = packet
            self._packets.append(packet)
            attempt['accepted'] = True
            if packet.state in ('RUNNING', 'DONE'):
                self._input_ack[r] = packet.seq
            if packet.kind == 'END':
                self._completion[r] = packet.completion_time

    def launch(self, now):
        with self._event('joint_epoch_validation_and_atomic_install', now) as t:
            if not self._prepared or self._launch_attempted or self._launched or t != self.epoch:
                raise ValueError('single common-epoch launch of all prepared programs required')
            self._launch_attempted = True
            if set(self._registered) != set(self._robots) or set(self._latest) != set(self._robots):
                raise ValueError('every registered program needs delivered public STOPPED feedback')
            replacements = {}
            for r in self._robots:
                p = self._latest[r]
                if (p.state != 'STOPPED' or t-exact(p.capture) > self._ttl
                        or self._registered[r] != (_digest(self._plan['scheduled_specs'][r]), self._clocks[r])):
                    raise ValueError('missing/stale program-bound readiness')
                replacements[r] = deepcopy(self._clocks[r])
                replacements[r].resume(t, commit=True)
            self._command('LAUNCH', t)
            # Logical atomicity requires the documented exclusive synchronous
            # callback. No observer/control/feedback runs between assignments.
            previous = dict(self._clocks)
            try:
                for r in self._robots:
                    self._plants[r].clock = replacements[r]
                self._clocks = replacements
                self._launched = True
            except BaseException:
                for r in self._robots:
                    self._plants[r].clock = previous[r]
                self._clocks, self._launched = previous, False
                raise
            return {'accepted': True, 'epoch': str(t), 'commitment': self.commitment,
                    'actual_input_ack_received': False, 'completion_inferred': False}

    def receipt(self):
        """Close the event ledger; an unfinished controller is never paused."""
        if self._closed:
            raise ValueError('receipt already issued')
        provisional = self.costs.finish()
        with self.costs.measure('joint_final_audit_and_receipt_accounting'):
            audit_passed = True
            try:
                self._check()
            except Exception as exc:
                audit_passed = False
                self._failures.append({'event': 'final_audit', 'now': str(self._frontier),
                                       'reason': type(exc).__name__+': '+str(exc)})
            result = task_receipt(self._packets, task=self.task, robots=self._robots,
                                  engine=self.engine, completion=self._completion,
                                  costs=provisional, horizon=str(self.horizon),
                                  status='FAILED' if self._failures else None)
            result.update(commitment=self.commitment, schedule_sha256=self._plan['schedule_sha256'],
                          failures=deepcopy(self._failures), commands=deepcopy(self._commands),
                          receive_attempts=deepcopy(self._receive_attempts),
                          feedback_generated=_channel(self._feedback_wires),
                          commands_sent=_channel(self._command_wires),
                          sent_total=_channel(self._sent_wires),
                          incoming_feedback_attempts=_channel(self._incoming_wires),
                          incoming_nonpacket_attempts=sum(row['bytes'] is None for row in self._receive_attempts),
                          evaluation_records_count=len(self._evaluation_records),
                          evaluation_records_sha256=hashlib.sha256(_wire(self._evaluation_records)).hexdigest(),
                          evaluation_scope='LOCAL_LABELS_REFERENCE_TRUTH_OBSERVATION_CONTROL_NOT_GUARD_INPUT',
                          conditional_safety_final_audit_passed=audit_passed,
                          input_ack_sequences=deepcopy(self._input_ack),
                          common_epoch=str(self.epoch), task_origin='0',
                          planned_sum_from_epoch=self._plan['sum_completion'],
                          actual_sum_from_epoch=(str(sum(exact(t)-self.epoch for t in self._completion.values()))
                                                 if all(t is not None for t in self._completion.values()) else None),
                          metric_scope='PRIMARY_COMPLETION_FROM_TASK_ORIGIN_ZERO; PLAN_AND_EPOCH_METRICS_SEPARATE',
                          safety_scope='DECLARED_V2_MODEL_STATIC_MAP_ALL_PAIR_CERTIFICATE_AND_UNCHANGED_PROGRAMS',
                          transport_scope='TRUSTED_IN_PROCESS_EXCLUSIVE_CALLBACK_NOT_NETWORK_ATOMICITY',
                          communication_scope='ONE_LOCAL_COMMAND_PER_ROBOT; GENERATED_FEEDBACK_INCLUDES_UNDELIVERED',
                          receipt_closure_does_not_pause=True,
                          outer_process_budget='CALLER_DRIVER_AND_SUPERVISOR_REQUIRED',
                          cost_scope='SHARED_COSTS_FROM_CREATION; IMPORTS_CONSTRUCTOR_FAILURE_LEDGER_FINAL_METADATA_SERIALIZATION_IO_EXTERNAL')
            self._closed = True
        result['costs'] = self.costs.finish()
        return result
