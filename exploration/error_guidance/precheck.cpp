// Artificial, finite paired-route precheck. No model, AUTH, research input,
// production service or billed query is run. Main headers are read-only pins.
#include "pie_geometry_flint.hpp"
#include "pie_position_commit.hpp"
#include "pie_reference_controller.hpp"
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
void check(bool yes, const char* message) {
    ++checks;
    if (!yes) throw std::runtime_error(message);
}
R rat(long n, unsigned long d = 1) {
    struct Z {
        fmpz_t n, d;
        Z() { fmpz_init(n); fmpz_init(d); }
        ~Z() { fmpz_clear(n); fmpz_clear(d); }
    } z;
    fmpz_set_si(z.n, n); fmpz_set_ui(z.d, d);
    return R::from_rational(z.n, z.d);
}
bool same(const R& a, const R& b) { return O::cmp(a, b) == 0; }
std::string rational_text(const R& value) {
    fmpq_t q; fmpq_init(q);
    if (!O::copy_rational(value, q)) { fmpq_clear(q); throw std::runtime_error("expected rational threshold"); }
    char* text = fmpq_get_str(nullptr, 10, q);
    std::string result(text); flint_free(text); fmpq_clear(q);
    return result;
}
void interval(const R& value) {
    // Exact outward display only. All decisions use the original algebraic R.
    const long scale = 1000000;
    check(O::cmp(value, rat(0)) >= 0 && O::cmp(value, rat(64)) < 0, "display interval out of finite range");
    long lo = 0, hi = 64 * scale;
    while (hi - lo > 1) {
        const long mid = lo + (hi - lo) / 2;
        if (O::cmp(rat(mid, scale), value) <= 0) lo = mid; else hi = mid;
    }
    std::cout << "{\"lower_numerator\":" << lo << ",\"upper_numerator\":"
              << (same(value, rat(lo, scale)) ? lo : hi) << ",\"denominator\":" << scale << '}';
}
G::Piece square(const R& x, const R& y, const R& half) {
    return {{O::sub(x, half), O::sub(y, half)}, {O::add(x, half), O::sub(y, half)},
            {O::add(x, half), O::add(y, half)}, {O::sub(x, half), O::add(y, half)}};
}
std::vector<G::Resource> cells() {
    std::vector<G::Resource> result;
    for (long x = -2; x <= 18; ++x) for (long y = -6; y <= 6; ++y)
        result.push_back({"cell-" + std::to_string(x + 2) + "-" + std::to_string(y + 6),
                          {square(rat(x, 2), rat(y, 2), rat(1, 4))}});
    return result;
}
G geometry(const std::string& move, G::Point u, G::Point v, const R& error) {
    const R negative = O::sub(rat(0), error);
    return G({{"error-guidance-precheck-v1", "exact-flint", "fixture-plane", "unit", move},
        u, v, {square(rat(0), rat(0), rat(1, 10))},
        {{negative, negative}, {error, error}}, cells()}, true);
}
Controller motion(const G& g, const R& start) {
    Controller c({rat(1), rat(2), rat(6), rat(1)}, g.length(), start,
                 g.length(), rat(-1), g.binding().move_occurrence);
    check(c.run(start), "fixed MOVE failed to start from rest");
    return c;
}
std::shared_ptr<const I::Action> action(const G& g, const std::string& agent) {
    return std::make_shared<const I::Action>(I::Action{agent, "artificial-native-source",
        "exact-fixture", g, rat(0), g.length(), std::make_shared<const R>(rat(1, 100)), true});
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
        throw std::logic_error("no CAP_EXTEND in finite route precheck");
    }
};
struct Result { R arrival, waiting; unsigned observations, edges; };

class World {
    G blocker_;
    Controller blocker_motion_;
    std::unique_ptr<P> position_;
    R now_ = rat(0), waiting_ = rat(0);
    unsigned serial_ = 0, observations_ = 0, edges_ = 0;
    std::string tag() { return "view-" + std::to_string(++serial_); }
    S::Delta delta() {
        return {{position_->view().structure().view_id, tag(), {}, {}, {}}, now_, {}, {}};
    }
    void commit(S::Delta& d, const pie_query::Map<P::SnapshotIds>& ids = {}) {
        auto prepared = position_->prepare_admitted_update(d, ids);
        position_->commit(std::move(prepared));
    }
    void resident(const G& g) const {
        const auto occupied = g.n_mask(rat(0), rat(0));
        const auto view = position_->view();
        for (const auto& cell : occupied.mask()) {
            const auto& owner = view.structure().owners.at(cell);
            check(owner.agent == "requester" && owner.action.empty() && !owner.geometric,
                  "waiting/start footprint lacks stationary owner");
        }
    }
    bool ready(const std::string& demand) const {
        const auto view = position_->view();
        const auto& d = *view.structure().demands.at(demand);
        bool free = true;
        for (const auto& cell : d.input->resources) {
            const auto found = view.structure().owners.find(cell);
            if (found != view.structure().owners.end() && found->second.agent != d.input->agent) free = false;
        }
        check(free == d.relations.empty(), "Index readiness differs from real owner table");
        return d.input->non_owner_eligible && free;
    }
    void observe_at_four() {
        check(observations_ == 0 && O::cmp(now_, rat(4)) <= 0, "observation opportunity changed");
        blocker_motion_.advance_to(rat(4));
        const auto witness = blocker_motion_.snapshot();
        check(!witness.closed() && same(witness.state().s,
              O::sub(O::mul(rat(24), O::sqrt(rat(2))), rat(28))), "blocker witness is not expected same-MOVE state");
        const auto before = position_->view();
        const auto& a = *before.structure().actions.at("blocker")->input;
        check(same(a.q, rat(0)), "uncertified blocker truth entered committed progress");
        Certificate c{{"blocker", a.source, "one-common-observation", "artificial-native-not-AUTH",
            a.geometry.binding(), rat(4), rat(4), witness.state().s, *a.epsilon, witness.cap()}};
        NoExtensions guard;
        auto prepared = position_->prepare_position(c, {rat(4), tag(), "blocker-at-four", ""}, guard);
        check(position_->view().same_identity(before), "prepared certificate released ownership early");
        position_->commit(std::move(prepared));
        check(same(position_->view().structure().actions.at("blocker")->input->q, witness.state().s),
              "committed blocker progress does not match exact certificate");
        const auto endpoint = blocker_.n_mask(blocker_.length(), blocker_.length());
        for (const auto& cell : endpoint.mask())
            check(position_->view().structure().owners.at(cell).action == "blocker",
                  "query removed blocker endpoint responsibility");
        ++observations_;
    }
    void advance(const R& target) {
        check(O::cmp(target, now_) >= 0, "world time moved backwards");
        if (observations_ == 0 && O::cmp(target, rat(4)) >= 0) observe_at_four();
        blocker_motion_.advance_to(target);
        now_ = target;
        // Private true motion is a witness only, never an admission input.
        if (!observations_)
            check(same(position_->view().structure().actions.at("blocker")->input->q, rat(0)),
                  "motion without observation advanced knowledge");
    }
public:
    World(const R& error, const G& first)
        : blocker_(geometry("blocker", {rat(2), rat(3, 2)}, {rat(8), rat(3, 2)}, error)),
          blocker_motion_(motion(blocker_, rat(0))) {
        S seed("empty", rat(0));
        S::Delta residents{{"empty", "residents", {}, {}, {}}, rat(0), {}, {}};
        const auto b = blocker_.n_mask(rat(0), rat(0));
        const auto r = first.n_mask(rat(0), rat(0));
        for (const auto& cell : b.mask())
            check(residents.structure.owners.emplace(cell, std::make_shared<const I::Owner>(
                I::Owner{"blocker-resident", "blocker-agent", "", false})).second, "duplicate blocker start");
        for (const auto& cell : r.mask())
            check(residents.structure.owners.emplace(cell, std::make_shared<const I::Owner>(
                I::Owner{"requester-resident", "requester", "", false})).second, "initial robots overlap");
        auto prepared = seed.prepare(residents); seed.commit(std::move(prepared));
        position_.reset(new P(seed, {}));
        auto grant = delta();
        grant.structure.actions.emplace("blocker", action(blocker_, "blocker-agent"));
        const auto full = blocker_.n_mask(rat(0), blocker_.length());
        for (const auto& cell : full.mask()) {
            const auto& owners = position_->view().structure().owners;
            const auto found = owners.find(cell);
            check(found == owners.end() || found->second.agent == "blocker-agent", "blocker full cap hits waiting start");
            grant.structure.owners.emplace(cell, std::make_shared<const I::Owner>(
                I::Owner{"blocker", "blocker-agent", "blocker", true}));
        }
        commit(grant, {{"blocker", {"blocker-seed", "blocker-current", "", ""}}});
    }
    void edge(const G& g) {
        const std::string move = g.binding().move_occurrence;
        resident(g);
        const auto desired = g.n_mask(rat(0), g.length());
        auto request = delta();
        request.structure.demands.emplace(move, std::make_shared<const I::Demand>(
            I::Demand{"requester", "", desired.mask(), now_, true}));
        commit(request);
        if (!ready(move)) {
            const auto frozen = position_->view();
            const auto& relations = frozen.structure().demands.at(move)->relations;
            check(relations.size() == 1 && relations.front().action == "blocker" && relations.front().retirable,
                  "route has an unexpected or nonretirable blocker");
            std::cout << "{\"event\":\"waiting\",\"move\":\"" << move
                      << "\",\"owner\":\"" << relations.front().owner
                      << "\",\"threshold\":\"" << rational_text(*relations.front().threshold) << "\",\"at\":";
            interval(now_); std::cout << "}\n";
            check(observations_ == 0 && O::cmp(now_, rat(4)) < 0, "no future common evidence can release this route");
            waiting_ = O::add(waiting_, O::sub(rat(4), now_));
            advance(rat(4));
            resident(g);
            check(ready(move), "actual committed evidence did not unblock the requested route");
        }
        auto grant = delta();
        grant.structure.demands.emplace(move, nullptr);
        grant.structure.actions.emplace(move, action(g, "requester"));
        for (const auto& cell : desired.mask()) {
            const auto& owners = position_->view().structure().owners;
            const auto found = owners.find(cell);
            check(found == owners.end() || found->second.agent == "requester", "full MOVE admission hits foreign owner");
            grant.structure.owners.emplace(cell, std::make_shared<const I::Owner>(
                I::Owner{move, "requester", move, true}));
        }
        commit(grant, {{move, {move + "-seed", move + "-current", "", ""}}});
        Controller c = motion(g, now_);
        while (!c.snapshot().closed()) {
            const auto before = c.snapshot();
            const R boundary = O::add(before.segment_start(), before.segment().duration());
            advance(boundary);
            c.advance_to(boundary);
            check(c.snapshot().move_id() == move && same(c.snapshot().length(), g.length()) &&
                  same(c.snapshot().cap(), g.length()), "edge changed original MOVE or installed cap");
        }
        check(same(c.snapshot().state().s, g.length()) && same(c.snapshot().state().v, rat(0)),
              "native END lacks a reached original endpoint at rest");
        // Explicit native lifecycle premise: exact closed same-MOVE witness
        // authorizes END; production END/authentication are not implemented.
        auto end = delta();
        end.structure.actions.emplace(move, nullptr);
        for (const auto& cell : desired.mask()) {
            check(position_->view().structure().owners.at(cell).action == move, "END attempted foreign owner deletion");
            end.structure.owners.emplace(cell, nullptr);
        }
        const auto endpoint = g.n_mask(g.length(), g.length());
        for (const auto& cell : endpoint.mask())
            end.structure.owners[cell] = std::make_shared<const I::Owner>(
                I::Owner{"requester-resident", "requester", "", false});
        commit(end);
        for (const auto& cell : endpoint.mask())
            check(position_->view().structure().owners.at(cell).agent == "requester" &&
                  position_->view().structure().owners.at(cell).action.empty(), "END lost endpoint resident");
        ++edges_;
    }
    Result result() const { return {now_, waiting_, observations_, edges_}; }
};

Result route(bool upper, bool error_enabled) {
    const R error = error_enabled ? rat(1, 5) : rat(0);
    const long y = upper ? 1 : -2;
    const std::string prefix = std::string(error_enabled ? "bounded-" : "zero-") + (upper ? "upper-" : "lower-");
    std::vector<G> edges;
    edges.push_back(geometry(prefix + "1", {rat(0), rat(0)}, {rat(0), rat(y)}, error));
    edges.push_back(geometry(prefix + "2", {rat(0), rat(y)}, {rat(4), rat(y)}, error));
    edges.push_back(geometry(prefix + "3", {rat(4), rat(y)}, {rat(4), rat(0)}, error));
    World w(error, edges.front());
    for (const auto& edge : edges) w.edge(edge);
    const Result result = w.result();
    check(result.observations == 1 && result.edges == 3, "candidate did not use common one-observation complete route");
    std::cout << "{\"event\":\"route_result\",\"path\":\"" << (upper ? "upper" : "lower")
              << "\",\"error_halfwidth\":\"" << rational_text(error) << "\",\"arrival\":";
    interval(result.arrival); std::cout << ",\"waiting\":"; interval(result.waiting);
    std::cout << ",\"completed_original_moves\":" << result.edges
              << ",\"committed_observations\":" << result.observations << "}\n";
    return result;
}
void run() {
    const Result zu = route(true, false), zl = route(false, false);
    const Result eu = route(true, true), el = route(false, true);
    const R root3 = O::sqrt(rat(3)), root6 = O::sqrt(rat(6));
    // Independent closed-form checks of the actual controller-derived totals;
    // these expressions never select an edge, set waiting, or supply a cost.
    check(same(zu.arrival, O::mul(rat(4), root3)), "zero-error upper arrival mismatch");
    check(same(zl.arrival, O::mul(rat(2), O::add(root3, root6))), "lower arrival mismatch");
    check(same(eu.arrival, O::add(rat(4), O::mul(rat(3), root3))), "bounded-error upper arrival mismatch");
    check(same(el.arrival, zl.arrival), "error changed unblocked lower route controller time");
    check(same(zu.waiting, rat(0)) && same(zl.waiting, rat(0)) && same(el.waiting, rat(0)), "unexpected waiting");
    check(same(eu.waiting, O::sub(rat(4), root3)), "waiting not caused by common evidence opportunity");
    check(O::cmp(zu.arrival, zl.arrival) < 0 && O::cmp(eu.arrival, el.arrival) > 0,
          "paired-path waiting reversal was falsified");
    std::cout << "{\"event\":\"summary\",\"status\":\"passed\",\"checks\":" << checks
              << ",\"zero_error_preferred\":\"upper\",\"bounded_error_preferred\":\"lower\","
              << "\"scope\":\"finite_offline_reference_potential_not_learning_or_full_cost\"}\n";
}
} // namespace
int main() {
    try { run(); return 0; }
    catch (const std::exception& e) { std::cerr << "precheck failed after " << checks << " checks: " << e.what() << '\n'; return 1; }
}
