# Component export schema v1

This is a software integration fixture, not a production/AUTH export contract.
The exporter accepts ONE retained `PositionCommit::View`; structure, history,
receipts and scheduler metadata must all be read through that same view.
It must not accept a private Prepared object or a separate Scheduler instance.
JSON checks cannot authenticate same-root provenance or detect every forged
cross-root combination. Root consistency comes from the reviewed C++ export
path; identifiers, generation and timestamps alone do not prove it.

The JSON object has exactly these fields:

```
schema: "pie_query_component_snapshot_v1"
source_kind: "synthetic_component_fixture"
outer_publication_verified: false
run_id: nonempty string
snapshot_id: nonempty string (caller-assigned, not authentication)
view_id: committed structure's string label (not unique root identity)
now: exact number
committed_at: scheduler's state timestamp
policy: "SRDC" (other policies may be exported but reader rejects them)
generation: nonnegative integer
cursor: string, possibly empty
actions: list of action objects
demands: list of demand objects
receipts: list of settled receipts for distinct active profiles, if present
```

An exact number is `{ "numerator": "signed decimal integer", "denominator":
"positive decimal integer" }`, with reduced canonical representation. A
nonrational value is `{ "unsupported": "non_rational" }`. It must never be
approximated; the Python reader rejects the complete snapshot and reports the
field path. JSON duplicate keys, unknown fields, floats and interval text are
rejected. Source provenance is preserved as metadata, not model features.

Binding fields: `geometry_version`, `number_encoding`, `coordinate_frame`,
`distance_unit`, `move_occurrence`, all nonempty strings.

Action fields: `key`, `agent`, `source`, `profile`, `binding`, `q`, `cap`,
`epsilon` (exact or null), `eligible` (boolean), `history` (list).

History fields: `action`, `source`, `key`, `provenance`, `binding`, `captured`,
`delivered`, `lower`, `epsilon`, `cap_at_capture`. The source of historical
evidence is preserved and need not equal the current action's source. MOVE
binding must match, and lower must not exceed current q.

Receipt fields: `profile`, `source`, `key`, `provenance`, `epsilon` (exact or
null), `published`, `captured`, `committed`, `delivered`, `charged_work`.
Only a receipt matching current profile, source and epsilon may price that
action. Incompatible receipts remain visible in the raw record.

Demand fields: `key`, `agent`, `requester_action` (possibly empty), `weight`
(positive integer, 1 or 1+out[requester_action]), `joined`, `other_ready`,
`relations` (list).

Relation fields: `owner` (responsibility identity), `action` (possibly empty),
`retirable`, `kind` (one of the five Index::RelationKind names), `threshold`
(exact or null). Non-query owners are retained, including multiple owners with
empty action. No owner filtering or merging is permitted during export.

Actions without a precision promise remain in the raw record; the Python
projection reports them explicitly as excluded from the predictive Action
list. Their demand relations must remain in the owner count. The projection
does not authenticate sources, authorize movement, or claim original B1 cost
accounting. Production outer publication and future-label linkage remain
separate work.
