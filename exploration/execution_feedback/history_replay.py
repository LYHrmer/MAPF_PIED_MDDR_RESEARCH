"""Recover frozen C1 public bytes; neither a sensor nor a T1 phase source."""
import hashlib
import json

from protocol import Binding, Producer, Inbox, exact


def recover_c1(fixture, evidence):
    """Public inputs -> original serialization -> frozen digest -> admission.

    The original static receipt authenticates the byte identity, not a real
    sensor. Never consult initial conditions, source.sample or a planned clock.
    """
    commitments = {d['guard']['commitment'] for d in evidence['decisions']}
    rows = fixture['public_progress']
    if len(commitments) != 1 or len(rows) != 2:
        raise ValueError('unsupported frozen C1 history')
    commitment = commitments.pop()
    actual = hashlib.sha256(json.dumps({'fixture': fixture, 'source': evidence['source_contract']},
                                      sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    if actual != commitment:
        raise ValueError('full path/order/controller/public-fixture commitment changed')
    binding = Binding(fixture['task'], 'A', 'A_2', fixture['condition'], commitment)
    producer = Producer(binding)
    packets = []
    for row in rows:
        if set(row) != {'action', 'capture', 'delivery', 'observed_x', 'observed_y'}:
            raise ValueError('public C1 fields only; no inferred phase or truth')
        sensor = {k: row[k] for k in ('action', 'capture', 'observed_x', 'observed_y')}
        sensor.update(task=binding.task, robot=binding.robot, condition=binding.condition)
        packet = producer.capture(sensor, now=row['capture'])
        if exact(row['delivery']) != exact(packet.delivery):
            raise ValueError('changed delivery')
        packets.append(packet)
    wires = [p.wire() for p in packets]
    digest = hashlib.sha256(b'\n'.join(wires)).hexdigest()
    prior = evidence['same_information']
    if (digest != prior['wire_sha256'] or len(packets) != prior['messages_per_arm']
            or sum(map(len, wires)) != prior['bytes_per_arm']):
        raise ValueError('frozen public bytes do not match')
    inboxes = [Inbox(binding), Inbox(binding)]
    for packet in packets:
        for inbox in inboxes:
            inbox.admit(packet, now=packet.delivery)
    return tuple(packets), {
        'evidence_kind': 'recovered_frozen_public_fixture_NOT_new_sensor_recording',
        'messages_per_arm': len(packets), 'bytes_per_arm': sum(map(len, wires)),
        'wire_sha256': digest, 'wire_utf8': [w.decode() for w in wires],
        'packet_reconstructions': len(packets), 'digest_checks': 1,
        'receiver_admissions_for_two_arms': 2*len(packets),
        'new_sensor_captures': 0, 'T1_phase_replay_available': False}


def require_task_phase(packet):
    """C1 action identity is not a T1 actual-input-clock interval."""
    from timed_protocol import TaskPacket
    if type(packet) is not TaskPacket:
        raise ValueError('C1 packet cannot be promoted to T1 phase evidence')
    return packet
