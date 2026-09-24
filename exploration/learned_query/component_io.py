"""Strict, rational-only projection of synthetic committed component exports.

Schema/provenance strings are checked, not authenticated.  This reader cannot
establish an outer publication, accept production events, or authorize motion.
The recursively immutable raw record retains identities and excluded actions;
only compatible historical receipts enter the advisory scoring projection.
"""

from dataclasses import dataclass
from fractions import Fraction
import json
import re
from types import MappingProxyType
from typing import Mapping

from .shadow import Action, Certificate, Demand, Receipt, Relation, Snapshot


class UnsupportedNumberDomain(ValueError):
    """A field contains an exact value outside this reader's rational domain."""


@dataclass(frozen=True)
class ImportedSnapshot:
    snapshot: Snapshot
    run_id: str
    snapshot_id: str
    generation: int
    committed_at: Fraction
    excluded_actions: tuple[tuple[str, str], ...]
    raw: Mapping[str, object]


_TOP = frozenset((
    "schema", "source_kind", "outer_publication_verified", "run_id",
    "snapshot_id", "view_id", "now", "committed_at", "policy", "generation",
    "cursor", "actions", "demands", "receipts",
))
_BINDING = frozenset(("geometry_version", "number_encoding", "coordinate_frame",
                      "distance_unit", "move_occurrence"))
_ACTION = frozenset(("key", "agent", "source", "profile", "binding", "q",
                     "cap", "epsilon", "eligible", "history"))
_HISTORY = frozenset(("action", "source", "key", "provenance", "binding",
                      "captured", "delivered", "lower", "epsilon", "cap_at_capture"))
_RECEIPT = frozenset(("profile", "source", "key", "provenance", "epsilon",
                      "published", "captured", "committed", "delivered", "charged_work"))
_DEMAND = frozenset(("key", "agent", "requester_action", "weight", "joined",
                     "other_ready", "relations"))
_RELATION = frozenset(("owner", "action", "retirable", "kind", "threshold"))
_KINDS = frozenset(("RetirableAtCurrentCap", "CapInsufficient", "EndpointRetained",
                    "OtherRetainedResponsibility", "NonQueryOwner"))
_INTEGER = re.compile(r"(?:0|-[1-9][0-9]*|[1-9][0-9]*)\Z")
_POSITIVE = re.compile(r"[1-9][0-9]*\Z")


class _Pairs(list):
    pass


def _decode(value, path="$"):
    if isinstance(value, _Pairs):
        result = {}
        for key, child in value:
            if key in result:
                raise ValueError(f"{path}.{key}: duplicate JSON key")
            result[key] = _decode(child, f"{path}.{key}")
        return result
    if isinstance(value, list):
        return [_decode(child, f"{path}[{i}]") for i, child in enumerate(value)]
    if isinstance(value, float):
        raise ValueError(f"{path}: JSON floating point is not supported")
    return value


def _constant(value):
    raise ValueError(f"JSON constant {value} is not supported")


def _object(value, fields, path):
    if type(value) is not dict:
        raise ValueError(f"{path}: expected an object")
    missing, unknown = fields - value.keys(), value.keys() - fields
    if missing or unknown:
        raise ValueError(f"{path}: missing fields {sorted(missing)}, unknown fields {sorted(unknown)}")
    return value


def _list(value, path):
    if type(value) is not list:
        raise ValueError(f"{path}: expected an array")
    return value


def _string(value, path, *, empty=False):
    if type(value) is not str or (not value.strip() and not (empty and value == "")):
        raise ValueError(f"{path}: expected {'a' if empty else 'a nonempty'} string")
    return value


def _boolean(value, path):
    if type(value) is not bool:
        raise ValueError(f"{path}: expected a boolean")
    return value


def _integer(value, path, *, minimum=0):
    if type(value) is not int or value < minimum:
        raise ValueError(f"{path}: expected an integer >= {minimum}")
    return value


def _number(value, path, *, nullable=False, positive=False):
    if nullable and value is None:
        return None
    if value == {"unsupported": "non_rational"}:
        raise UnsupportedNumberDomain(f"{path}: unsupported_number_domain (non_rational)")
    obj = _object(value, frozenset(("numerator", "denominator")), path)
    numerator, denominator = obj["numerator"], obj["denominator"]
    if (type(numerator) is not str or not _INTEGER.fullmatch(numerator)
            or type(denominator) is not str or not _POSITIVE.fullmatch(denominator)):
        raise ValueError(f"{path}: expected canonical decimal numerator/positive denominator strings")
    result = Fraction(int(numerator), int(denominator))
    if str(result.numerator) != numerator or str(result.denominator) != denominator:
        raise ValueError(f"{path}: rational representation must be reduced and canonical")
    if result < 0 or (positive and result == 0):
        raise ValueError(f"{path}: expected a {'positive' if positive else 'nonnegative'} value")
    return result


def _binding(value, path):
    obj = _object(value, _BINDING, path)
    return {name: _string(obj[name], f"{path}.{name}") for name in _BINDING}


def _freeze(value):
    if isinstance(value, dict):
        return MappingProxyType({key: _freeze(child) for key, child in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(child) for child in value)
    return value


def load_snapshot(text: str) -> ImportedSnapshot:
    """Validate one whole export, retaining exact values or rejecting it all."""
    if type(text) is not str:
        raise ValueError("snapshot input must be JSON text")
    raw = _object(_decode(json.loads(text, object_pairs_hook=_Pairs,
                                    parse_constant=_constant)), _TOP, "$")
    for field, expected in (("schema", "pie_query_component_snapshot_v1"),
                            ("source_kind", "synthetic_component_fixture"),
                            ("policy", "SRDC")):
        if raw[field] != expected:
            raise ValueError(f"$.{field}: expected {expected!r}")
    if raw["outer_publication_verified"] is not False:
        raise ValueError("$.outer_publication_verified: component fixtures must explicitly be false")
    run_id = _string(raw["run_id"], "$.run_id")
    snapshot_id = _string(raw["snapshot_id"], "$.snapshot_id")
    view_id = _string(raw["view_id"], "$.view_id")
    generation = _integer(raw["generation"], "$.generation")
    _string(raw["cursor"], "$.cursor", empty=True)
    now = _number(raw["now"], "$.now")
    committed_at = _number(raw["committed_at"], "$.committed_at")
    if committed_at > now:
        raise ValueError("$.committed_at: cannot exceed now")

    receipts, profiles = [], set()
    for i, obj in enumerate(_list(raw["receipts"], "$.receipts")):
        path = f"$.receipts[{i}]"
        _object(obj, _RECEIPT, path)
        for field in ("profile", "source", "key", "provenance"):
            _string(obj[field], f"{path}.{field}")
        if obj["profile"] in profiles:
            raise ValueError(f"{path}: duplicate settled receipt profile")
        profiles.add(obj["profile"])
        epsilon = _number(obj["epsilon"], f"{path}.epsilon", nullable=True, positive=True)
        times = [_number(obj[name], f"{path}.{name}")
                 for name in ("published", "captured", "committed", "delivered")]
        if not times[0] <= times[1] <= times[2] <= times[3] <= committed_at:
            raise ValueError(f"{path}: settlement chronology exceeds committed snapshot or is unordered")
        work = _number(obj["charged_work"], f"{path}.charged_work", positive=True)
        # A missing precision promise remains in raw metadata, never fabricated.
        if epsilon is not None:
            receipts.append((obj["source"], Receipt(obj["key"], obj["profile"], epsilon,
                                                   *times, work)))

    actions, raw_actions, excluded = [], {}, []
    for i, obj in enumerate(_list(raw["actions"], "$.actions")):
        path = f"$.actions[{i}]"
        _object(obj, _ACTION, path)
        for field in ("key", "agent", "source", "profile"):
            _string(obj[field], f"{path}.{field}")
        key = obj["key"]
        if key in raw_actions:
            raise ValueError(f"{path}.key: duplicate action")
        raw_actions[key] = obj
        binding = _binding(obj["binding"], f"{path}.binding")
        if binding["move_occurrence"] != key:
            raise ValueError(f"{path}.binding.move_occurrence: action key mismatch")
        q, cap = (_number(obj[field], f"{path}.{field}") for field in ("q", "cap"))
        if q > cap:
            raise ValueError(f"{path}: q must not exceed cap")
        epsilon = _number(obj["epsilon"], f"{path}.epsilon", nullable=True, positive=True)
        eligible = _boolean(obj["eligible"], f"{path}.eligible")
        history = []
        for j, item in enumerate(_list(obj["history"], f"{path}.history")):
            hp = f"{path}.history[{j}]"
            _object(item, _HISTORY, hp)
            for field in ("action", "source", "key", "provenance"):
                _string(item[field], f"{hp}.{field}")
            if item["action"] != key or _binding(item["binding"], f"{hp}.binding") != binding:
                raise ValueError(f"{hp}: history MOVE binding mismatch")
            captured, delivered, lower, old_cap = (
                _number(item[field], f"{hp}.{field}")
                for field in ("captured", "delivered", "lower", "cap_at_capture"))
            old_epsilon = _number(item["epsilon"], f"{hp}.epsilon", positive=True)
            if not captured <= delivered <= committed_at:
                raise ValueError(f"{hp}: history chronology exceeds committed snapshot or is unordered")
            if lower > q or not lower <= old_cap <= cap:
                raise ValueError(f"{hp}: history lower/cap inconsistent with current committed q/cap")
            history.append(Certificate(key, item["key"], captured, delivered,
                                       lower, old_epsilon, old_cap))
        if epsilon is None:
            excluded.append((key, "missing_precision_promise"))
            continue
        matched = tuple(receipt for source, receipt in receipts
                        if source == obj["source"] and receipt.profile == obj["profile"]
                        and receipt.epsilon == epsilon)
        actions.append(Action(key, obj["profile"], epsilon, q, cap,
                              tuple(history), matched, eligible))

    demands = []
    for i, obj in enumerate(_list(raw["demands"], "$.demands")):
        path = f"$.demands[{i}]"
        _object(obj, _DEMAND, path)
        key = _string(obj["key"], f"{path}.key")
        agent = _string(obj["agent"], f"{path}.agent")
        requester = _string(obj["requester_action"], f"{path}.requester_action", empty=True)
        if requester and (requester not in raw_actions or raw_actions[requester]["agent"] != agent):
            raise ValueError(f"{path}.requester_action: missing action or agent mismatch")
        weight = _integer(obj["weight"], f"{path}.weight", minimum=1)
        joined = _number(obj["joined"], f"{path}.joined")
        if joined > committed_at:
            raise ValueError(f"{path}.joined: cannot exceed committed_at")
        ready = _boolean(obj["other_ready"], f"{path}.other_ready")
        relations = []
        for j, item in enumerate(_list(obj["relations"], f"{path}.relations")):
            rp = f"{path}.relations[{j}]"
            _object(item, _RELATION, rp)
            owner = _string(item["owner"], f"{rp}.owner")
            action = _string(item["action"], f"{rp}.action", empty=True)
            retirable = _boolean(item["retirable"], f"{rp}.retirable")
            kind = _string(item["kind"], f"{rp}.kind")
            if kind not in _KINDS:
                raise ValueError(f"{rp}.kind: unknown relation kind")
            threshold = _number(item["threshold"], f"{rp}.threshold", nullable=True)
            if action and (action not in raw_actions or owner != action):
                raise ValueError(f"{rp}: active responsibility/action mismatch")
            if not action and (kind != "NonQueryOwner" or retirable or threshold is not None):
                raise ValueError(f"{rp}: empty action must be a retained non-query owner")
            if action and kind == "NonQueryOwner":
                raise ValueError(f"{rp}: non-query owner must have an empty action")
            if retirable != (kind == "RetirableAtCurrentCap") or (retirable and threshold is None):
                raise ValueError(f"{rp}: inconsistent retirement kind/threshold")
            if threshold is not None and action:
                q = _number(raw_actions[action]["q"], f"{rp}.action.q")
                cap = _number(raw_actions[action]["cap"], f"{rp}.action.cap")
                if threshold < q or (retirable and threshold >= cap):
                    raise ValueError(f"{rp}.threshold: inconsistent with current q/cap")
                if kind == "CapInsufficient" and threshold < cap:
                    raise ValueError(f"{rp}.threshold: cap-insufficient relation below cap")
            relations.append(Relation(owner, threshold, retirable, action=action))
        demands.append(Demand(key, weight, tuple(relations), joined, ready))
    snapshot = Snapshot(view_id, now, tuple(actions), tuple(demands))
    return ImportedSnapshot(snapshot, run_id, snapshot_id, generation,
                            committed_at, tuple(excluded), _freeze(raw))
