// Finite, program-local native mechanism precheck; not AUTH or a paid service.
// All masks/thresholds come from real Geometry/Index. Motion witnesses come from
// the real same-MOVE ReferenceController. No research payload is read.
#include "pie_geometry_flint.hpp"
#include "pie_position_commit.hpp"
#include "pie_reference_controller.hpp"
#include <algorithm>
#include <iostream>
#include <memory>
#include <stdexcept>
#include <string>
#include <vector>

namespace {
using O = pie_geometry::FlintOps;
using R = O::Real;
using P = pie_position_commit::PositionCommit<O>;
using S = P::Scheduler;
using I = P::Structure;
using G = P::Geometry;
using Controller = pie_reference::ReferenceController;
unsigned checks = 0;

void check(bool condition, const char* message) {
    ++checks;
    if (!condition) throw std::runtime_error(message);
}
R rat(long n, unsigned long d = 1) {
    struct Integers {
        fmpz_t n, d;
        Integers() { fmpz_init(n); fmpz_init(d); }
        ~Integers() { fmpz_clear(n); fmpz_clear(d); }
    } z;
    fmpz_set_si(z.n, n); fmpz_set_ui(z.d, d);
    return R::from_rational(z.n, z.d);
}
bool same(const R& a, const R& b) { return O::cmp(a, b) == 0; }
std::string exact(const R& value) {
    fmpq_t q;
    fmpq_init(q);
    const bool rational = O::copy_rational(value, q);
    if (!rational) { fmpq_clear(q); throw std::runtime_error("nonrational output"); }
    char* bytes = fmpq_get_str(nullptr, 10, q);
    const std::string result(bytes);
    flint_free(bytes); fmpq_clear(q);
    return result;
}
G::Piece square(const R& x, const R& y, const R& half) {
    return {{O::sub(x, half), O::sub(y, half)},
            {O::add(x, half), O::sub(y, half)},
            {O::add(x, half), O::add(y, half)},
            {O::sub(x, half), O::add(y, half)}};
}
std::vector<G::Resource> resources() {
    // A finite covering of every swept footprint, including the full error box.
    std::vector<G::Resource> cells;
    for (long x = -3; x <= 11; ++x)
        for (long y = -1; y <= 4; ++y)
            cells.push_back({"cell-" + std::to_string(x + 3) + "-" + std::to_string(y + 1),
                             {square(rat(x), rat(y), rat(1, 2))}});
    return cells;
}
G geometry(const std::string& key, long ux, long uy, long vx, long vy) {
    return G({{"legal-and-v1", "exact-flint", "fixture-plane", "unit", key},
        {rat(ux), rat(uy)}, {rat(vx), rat(vy)}, {square(rat(0), rat(0), rat(1, 10))},
        {{rat(-1, 20), rat(-1, 20)}, {rat(1, 20), rat(1, 20)}}, resources()}, true);
}
G blocker(const std::string& key) {
    const long x = key == "A" ? 0 : key == "B" ? 2 : 8;
    return geometry(key, x, 0, x, 3);
}
G requester(const std::string& key) {
    return key == "D3" ? geometry(key, 6, 1, 10, 1) :
        geometry(key, -2, key == "D1" ? 1 : 2, 4, key == "D1" ? 1 : 2);
}
std::shared_ptr<const I::Action> action(const std::string& agent, const G& g) {
    return std::make_shared<const I::Action>(I::Action{
        agent, "artificial-native-source", "exact-fixture-profile", g, rat(0), g.length(),
        std::make_shared<const R>(rat(1, 10)), true});
}
void add_owned_mask(S::Delta& delta, const G& g, const std::string& agent,
                    bool active) {
    const auto mask = g.n_mask(rat(0), active ? g.length() : rat(0));
    for (const auto& resource : mask.mask())
        check(delta.structure.owners.emplace(resource, std::make_shared<const I::Owner>(
            I::Owner{g.binding().move_occurrence, agent,
                     active ? g.binding().move_occurrence : "", active})).second,
              "initial geometric owners overlap");
}
std::unique_ptr<P> initial() {
    S scheduler("empty", rat(0));
    S::Delta delta{{"empty", "residents", {}, {}, {}}, rat(0), {}, {}};
    for (const std::string key : {"A", "B", "C"}) {
        G g = blocker(key);
        check(g.g_init(g.length(), "seed-" + key).mask() == g.n_mask(rat(0), g.length()).mask(),
              "incremental and direct initial masks differ");
        add_owned_mask(delta, g, "agent-" + key, false);
    }
    for (const std::string key : {"D1", "D2", "D3"}) {
        G g = requester(key);
        add_owned_mask(delta, g, "agent-" + key, false);
    }
    auto prepared = scheduler.prepare(delta);
    scheduler.commit(std::move(prepared));
    std::unique_ptr<P> p(new P(scheduler, {}));
    // Start with six disjoint stationary owners. Each initial blocker cap is
    // granted only after checking its ENTIRE swept mask against the current
    // actual owner table, including every waiting requester's starting cell.
    for (const std::string key : {"A", "B", "C"}) {
        const auto before = p->view();
        G g = blocker(key);
        S::Delta grant{{before.structure().view_id, "grant-" + key, {}, {}, {}}, rat(0), {}, {}};
        grant.structure.actions.emplace(key, action("agent-" + key, g));
        const auto full = g.n_mask(rat(0), g.length());
        for (const auto& cell : full.mask()) {
            const auto old = before.structure().owners.find(cell);
            check(old == before.structure().owners.end() || old->second.agent == "agent-" + key,
                  "initial blocker cap conflicts with another robot or waiting start");
            grant.structure.owners.emplace(cell, std::make_shared<const I::Owner>(
                I::Owner{key, "agent-" + key, key, true}));
        }
        auto pending = p->prepare_admitted_update(grant, {{key, {key + "-seed", key + "-current", "", ""}}});
        p->commit(std::move(pending));
    }
    S::Delta requests{{p->view().structure().view_id, "initial", {}, {}, {}}, rat(0), {}, {}};
    for (const std::string key : {"D1", "D2", "D3"}) {
        G g = requester(key);
        const auto desired = g.n_mask(rat(0), g.length());
        requests.structure.demands.emplace(key, std::make_shared<const I::Demand>(I::Demand{
            "agent-" + key, "", desired.mask(), rat(0), true}));
    }
    auto requests_pending = p->prepare_admitted_update(requests, {});
    p->commit(std::move(requests_pending));
    return p;
}
Controller controller(const std::string& key) {
    // Existing reference-controller test coefficients, not robot capabilities
    // or protected research configuration. Fixed original ell=cap=3, eta=-1.
    Controller c({rat(1), rat(2), rat(6), rat(1)}, rat(3), rat(0), rat(3), rat(-1), key);
    check(c.run(rat(0)), "reference MOVE did not launch");
    return c;
}
struct Certificate {
    S::Evidence evidence;
    const G::Binding& binding() const { return evidence.binding; }
    const R& lower_bound() const { return evidence.lower; }
    const R& captured_at() const { return evidence.captured; }
    const R& delivered_at() const { return evidence.delivered; }
    const S::Evidence* precision_evidence() const { return &evidence; }
};
struct NoExtensions {
    bool operator()(const I::Demand&, const P::OwnerMap&, const R&) const {
        throw std::logic_error("this precheck has no CAP_EXTEND demands");
    }
};
void query(P& p, Controller& c, const R& at, const std::string& tag) {
    c.advance_to(at);
    const auto witness = c.snapshot();
    const auto before = p.view();
    const std::string key = witness.move_id();
    const auto& a = *before.structure().actions.at(key)->input;
    check(same(witness.length(), a.geometry.length()) && same(witness.cap(), a.b),
          "reference motion changed original MOVE or cap");
    // Artificial admitted source: exact [s,s] has width 0 <= epsilon. It is
    // linked to a reachable local state, but does not establish causal AUTH.
    Certificate certificate{{key, a.source, tag, "artificial-native-not-AUTH",
        a.geometry.binding(), at, at, witness.state().s, *a.epsilon, witness.cap()}};
    NoExtensions guard;
    auto prepared = p.prepare_position(certificate, {at, "view-" + tag, "g-" + tag, ""}, guard);
    check(p.view().same_identity(before), "POSITION prepare leaked a root");
    p.commit(std::move(prepared));
    const auto after = p.view();
    check(same(after.structure().actions.at(key)->input->q, witness.state().s),
          "committed lower disagrees with reachable witness");
    check(after.current_snapshot(key).mask() == a.geometry.n_mask(witness.state().s, a.b).mask(),
          "retirement and direct residual geometry disagree");
    const auto endpoint = a.geometry.n_mask(a.geometry.length(), a.geometry.length());
    for (const auto& cell : endpoint.mask())
        check(after.structure().owners.count(cell) && after.structure().owners.at(cell).action == key,
              "query removed original endpoint responsibility");
}
bool ready(const P::View& view, const std::string& demand) {
    const auto& d = *view.structure().demands.at(demand);
    bool no_foreign = true;
    for (const auto& cell : d.input->resources) {
        const auto owner = view.structure().owners.find(cell);
        if (owner != view.structure().owners.end() && owner->second.agent != d.input->agent)
            no_foreign = false;
    }
    check(no_foreign == d.relations.empty(), "Index and actual resource conflicts differ");
    return d.input->non_owner_eligible && no_foreign;
}
unsigned ready_count(const P::View& view) {
    unsigned result = 0;
    for (const std::string key : {"D1", "D2", "D3"}) if (ready(view, key)) ++result;
    return result;
}
void admit_ready(P& p, const R& at) {
    // Native admitted-update witness under stated ready/non-owner premises.
    // This is not an execution of AUTH or CenterService admission.
    for (const std::string key : {"D1", "D2", "D3"}) {
        const auto before = p.view();
        if (!ready(before, key)) continue;
        G g = requester(key);
        S::Delta delta{{before.structure().view_id, "admit-" + key, {}, {}, {}}, at, {}, {}};
        delta.structure.actions.emplace(key, action("agent-" + key, g));
        const auto full = g.n_mask(rat(0), g.length());
        for (const auto& cell : full.mask()) {
            const auto prior = before.structure().owners.find(cell);
            check(prior == before.structure().owners.end() || prior->second.agent == "agent-" + key,
                  "requester acquisition conflicts with a foreign owner");
            delta.structure.owners.emplace(cell, std::make_shared<const I::Owner>(
                I::Owner{key, "agent-" + key, key, true}));
        }
        delta.structure.demands.emplace(key, nullptr);
        auto prepared = p.prepare_admitted_update(delta, {{key, {key + "-seed", key + "-current", "", ""}}});
        p.commit(std::move(prepared));
        check(p.view().structure().actions.count(key) == 1 && !p.view().structure().demands.count(key),
              "ready requester did not become an admitted native action");
    }
}
void inspect_initial(const P::View& seed) {
    const auto& state = seed.structure();
    for (const std::string key : {"D1", "D2", "D3"}) {
        const auto& d = *state.demands.at(key);
        check(d.relations.size() == (key == "D3" ? 1u : 2u), "wrong geometry-derived owner count");
        const R expected = key == "D2" ? rat(53, 20) : rat(33, 20);
        for (const auto& relation : d.relations) {
            check(relation.retirable && relation.threshold && same(*relation.threshold, expected),
                  "wrong geometry-derived strict release threshold");
            check(relation.action == (key == "D3" ? "C" : relation.owner) &&
                  (key == "D3" || relation.owner == "A" || relation.owner == "B"),
                  "unexpected physical responsibility");
            std::vector<std::string> hits;
            for (const auto& cell : d.input->resources) {
                const auto owner = state.owners.find(cell);
                if (owner != state.owners.end() && owner->second.action == relation.action) hits.push_back(cell);
            }
            const auto& a = *state.actions.at(relation.action)->input;
            const auto threshold = pie_query_geometry::extract<O>(a.geometry, a.q, a.b, hits);
            check(same(threshold.physical_exit, expected) && !threshold.crossed_by(expected),
                  "strict threshold equality released a responsibility");
        }
    }
}
void strict_and_endpoint_controls() {
    auto held = initial();
    P& p = *held;
    Controller a = controller("A"), b = controller("B");
    // On APPROACH s(t)=3-(3-t)^2. These exact algebraic times attain the
    // exact two geometry thresholds; equality must retain the affected row.
    const R t1 = O::sqrt(rat(33, 10)); // LAUNCH s=t^2/2 = 33/20.
    query(p, a, t1, "A-at-first-threshold");
    check(p.view().structure().demands.at("D1")->relations.size() == 2,
          "first strict boundary was treated as open");
    const R t2 = O::sub(rat(3), O::sqrt(rat(7, 20)));
    query(p, a, t2, "A-at-second-threshold");
    check(same(p.view().structure().actions.at("A")->input->q, rat(53, 20)) &&
          p.view().structure().demands.at("D2")->relations.size() == 2,
          "second strict boundary was treated as open");
    query(p, b, rat(5, 2), "B-alone-for-second-row");
    check(!ready(p.view(), "D2"), "B alone cleared equality-retained A responsibility");
    query(p, a, rat(11, 4), "A-strictly-after-both");
    check(ready(p.view(), "D1") && ready(p.view(), "D2"), "strictly crossed pair did not clear both demands");
    // Center still holds the active action until an external END; POSITION at
    // exact ell only shrinks to endpoint cells. No END is synthesized here.
    query(p, a, rat(3), "A-at-original-end");
    check(a.snapshot().closed(), "reference controller did not close at original end");
    check(!p.view().current_snapshot("A").mask().empty(), "endpoint mask disappeared");
}
void run() {
    const auto seed = initial();
    inspect_initial(seed->view());
    strict_and_endpoint_controls();
    std::cout << "{\"source_kind\":\"artificial_native_legal_and_precheck\",\"initial_relations\":{";
    bool demand_comma = false;
    for (const auto& item : seed->view().structure().demands) {
        if (demand_comma) std::cout << ',';
        demand_comma = true;
        std::cout << '"' << item.first << "\":[";
        bool relation_comma = false;
        for (const auto& relation : item.second->relations) {
            if (relation_comma) std::cout << ',';
            relation_comma = true;
            std::cout << "{\"owner\":\"" << relation.owner << "\",\"threshold\":\""
                      << exact(*relation.threshold) << "\",\"retirable\":"
                      << (relation.retirable ? "true" : "false") << '}';
        }
        std::cout << ']';
    }
    std::cout << "},\"sequences\":[";
    bool comma = false;
    for (const std::string first : {"A", "B", "C"}) for (const std::string second : {"A", "B", "C"}) {
        if (first == second) continue;
        auto held = initial();
        P& p = *held;
        std::vector<Controller> trajectories{controller("A"), controller("B"), controller("C")};
        Controller& c1 = trajectories.at(static_cast<unsigned>(first[0] - 'A'));
        Controller& c2 = trajectories.at(static_cast<unsigned>(second[0] - 'A'));
        check(ready_count(p.view()) == 0, "a demand was initially unblocked");
        for (auto& c : trajectories) c.advance_to(rat(5, 2));
        query(p, c1, rat(5, 2), first + second + "-first");
        check(same(c1.snapshot().state().s, rat(11, 4)), "first reachable progress differs");
        for (const auto& c : trajectories) {
            check(same(c.snapshot().state().s, rat(11, 4)), "query order changed physical trajectory");
            if (c.snapshot().move_id() != first)
                check(same(p.view().structure().actions.at(c.snapshot().move_id())->input->q, rat(0)),
                      "unqueried true progress leaked into committed knowledge");
        }
        const unsigned after_first = ready_count(p.view());
        check(after_first == (first == "C" ? 1u : 0u), "one owner incorrectly satisfied AND");
        for (auto& c : trajectories) c.advance_to(rat(11, 4));
        query(p, c2, rat(11, 4), first + second + "-second");
        check(same(c2.snapshot().state().s, rat(47, 16)), "second reachable progress differs");
        for (const auto& c : trajectories) {
            check(same(c.snapshot().state().s, rat(47, 16)), "second opportunity changed physical trajectory");
            const R expected_q = c.snapshot().move_id() == first ? rat(11, 4) :
                c.snapshot().move_id() == second ? rat(47, 16) : rat(0);
            check(same(p.view().structure().actions.at(c.snapshot().move_id())->input->q, expected_q),
                  "knowledge did not retain exactly the delivered query observations");
        }
        const unsigned after_second = ready_count(p.view());
        const unsigned expected = first != "C" && second != "C" ? 2u : 1u;
        check(after_second == expected, "two-opportunity native AND count differs");
        admit_ready(p, rat(11, 4));
        check(p.view().structure().actions.size() == 3u + expected,
              "simultaneously ready demand admissions conflict");
        if (comma) std::cout << ',';
        comma = true;
        std::cout << "{\"order\":[\"" << first << "\",\"" << second
                  << "\"],\"ready_after_first\":" << after_first
                  << ",\"ready_after_second\":" << after_second
                  << ",\"native_admitted_actions\":" << expected << '}';
    }
    std::cout << "],\"checks\":" << checks
              << ",\"endpoint_retained\":true}\n";
}
} // namespace
int main() {
    try { run(); return 0; }
    catch (const std::exception& e) { std::cerr << "legal_and_precheck failed after " << checks << " checks: " << e.what() << '\n'; return 1; }
}
