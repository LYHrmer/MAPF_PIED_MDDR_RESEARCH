# Source identity and scope

The original baselines call OnlineGGO@ff6d830e2fd5bf85ccbb72eaec0fb8df1cf1c256
OBJ3 SUM_OVC and OBJ4 quad560 through the exact R6c bridge binaries. Source:
https://github.com/zanghz21/OnlineGGO. Original algorithm-object and binary
identities are in inherited_binary_manifest.json and the inherited R6c freeze.
The 560 parameters are the unchanged shortened 200-candidate sortation model;
they are neither a new execution-error model nor the full published training.

The candidate replaces only the OBJ3 traffic_mapf/search.cpp object with
search_overlay.cpp; search_overlay.patch records the one edge-cost addition
and its external function declaration. candidate_bridge.cpp binds public
current-start IDs to the nonnegative per-agent destination-cost matrix.
candidate_identity.json identifies every retained object and the replaced
object. The candidate is a modified algorithm, not an unchanged author baseline.

The unchanged common S1 binaries come from R6c, with LSMART
a3780a45eb101f5b6834236f86bad39025f1e99f and documented FIFO/S1/mapping adaptations.
Source: https://github.com/smart-mapf/lifelong-smart. All original ACK,
ADG/parser, controller equations and normal STATION timing are reused; this
experiment changes neither the controller nor the execution barrier.

Both source projects are MIT licensed. Full notices are copied alongside
this file as OnlineGGO_LICENSE.txt and LSMART_LICENSE.txt. Maps/scenario origins
and original-byte hashes remain in each generated environment.json; fresh FIFO
streams and all seeds are recorded before native runs.
