// Finite common-observation timing successor; original precheck is unchanged.
// No model, AUTH, research payload, production service or billed query is run.
// Four named opportunities only; insufficient evidence ends at lawful waiting.
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
struct Opportunity { const char* name; R at, expected_lower; bool releases; };
struct Result { R stopped_at, waiting, observed_lower; unsigned observations, edges; bool completed; };

class World {
    G blocker_;
    Controller blocker_motion_;
    std::unique_ptr<P> position_;
    R now_ = rat(0), waiting_ = rat(0), observed_lower_ = rat(0);
    R opportunity_;
    std::string opportunity_name_;
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
    void observe() {
        check(observations_ == 0 && O::cmp(now_, opportunity_) <= 0, "common observation opportunity changed");
        blocker_motion_.advance_to(opportunity_);
        const auto witness = blocker_motion_.snapshot();
        check(!witness.closed() && witness.move_id() == "blocker" &&
              same(witness.length(), blocker_.length()) && same(witness.cap(), blocker_.length()),
              "observation does not belong to the active original blocker MOVE");
        const auto before = position_->view();
        const auto& a = *before.structure().actions.at("blocker")->input;
        check(same(a.q, rat(0)), "uncertified blocker truth entered committed progress");
        // The exact source interval is [s,s]. No predicted/expected lower is used.
        Certificate c{{"blocker", a.source, "one-common-observation", "artificial-native-not-AUTH",
            a.geometry.binding(), opportunity_, opportunity_, witness.state().s, *a.epsilon, witness.cap()}};
        NoExtensions guard;
        auto prepared = position_->prepare_position(c, {opportunity_, tag(), "blocker-observed", ""}, guard);
        check(position_->view().same_identity(before), "prepared certificate released ownership early");
        position_->commit(std::move(prepared));
        observed_lower_ = witness.state().s;
        check(same(position_->view().structure().actions.at("blocker")->input->q, observed_lower_),
              "committed progress differs from exact controller certificate");
        check(position_->view().current_snapshot("blocker").mask() ==
              blocker_.n_mask(observed_lower_, blocker_.length()).mask(),
              "committed retirement differs from direct residual geometry");
        const auto endpoint = blocker_.n_mask(blocker_.length(), blocker_.length());
        for (const auto& cell : endpoint.mask())
            check(position_->view().structure().owners.at(cell).action == "blocker",
                  "query removed blocker endpoint responsibility");
        ++observations_;
    }
    void advance(const R& target) {
        check(O::cmp(target, now_) >= 0, "world time moved backwards");
        if (observations_ == 0 && O::cmp(target, opportunity_) >= 0) observe();
        blocker_motion_.advance_to(target);
        now_ = target;
        // Later private true progress may NOT replace the only committed sample.
        check(same(position_->view().structure().actions.at("blocker")->input->q,
                   observations_ ? observed_lower_ : rat(0)),
              "unobserved motion leaked into committed progress");
    }
public:
    World(const R& error, const G& first, const Opportunity& opportunity)
        : blocker_(geometry("blocker", {rat(2), rat(3, 2)}, {rat(8), rat(3, 2)}, error)),
          blocker_motion_(motion(blocker_, rat(0))), opportunity_(opportunity.at),
          opportunity_name_(opportunity.name) {
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
    bool edge(const G& g) {
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
            check(relations.size() == 1 && relations.front().action == "blocker" &&
                  relations.front().retirable && relations.front().threshold,
                  "unexpected or nonretirable route blocker");
            const R threshold = *relations.front().threshold;
            check(same(threshold, rat(61, 20)), "geometry-derived route threshold changed");
            std::cout << "{\"event\":\"waiting\",\"opportunity\":\"" << opportunity_name_
                      << "\",\"move\":\"" << move << "\",\"owner\":\"" << relations.front().owner
                      << "\",\"threshold\":\"" << rational_text(threshold) << "\",\"at\":";
            interval(now_); std::cout << "}\n";
            if (observations_ == 0) {
                check(O::cmp(now_, opportunity_) < 0, "missed the common observation opportunity");
                waiting_ = O::add(waiting_, O::sub(opportunity_, now_));
                advance(opportunity_);
            }
            resident(g);
            const bool released = ready(move);
            check(released == (O::cmp(observed_lower_, threshold) > 0),
                  "actual PositionCommit retirement violates strict threshold");
            if (!released) {
                const auto after = position_->view();
                const auto& still = after.structure().demands.at(move)->relations;
                check(observations_ == 1 && still.size() == 1 && still.front().owner == "blocker" &&
                      same(*still.front().threshold, threshold) && !after.structure().actions.count(move),
                      "insufficient evidence lost pending demand or installed an unauthorized MOVE");
                // Finite censoring point: preserve the resident and pending demand.
                // No new observation, END, cap grant, or later true progress is invented.
                std::cout << "{\"event\":\"blocked_after_only_observation\",\"opportunity\":\""
                          << opportunity_name_ << "\",\"move\":\"" << move
                          << "\",\"threshold\":\"" << rational_text(threshold)
                          << "\",\"resident_retained\":true,\"observed_lower\":";
                interval(observed_lower_); std::cout << "}\n";
                return false;
            }
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
        return true;
    }
    Result result(bool complete) const { return {now_, waiting_, observed_lower_, observations_, edges_, complete}; }
};

Result route(bool upper, bool error_enabled, const Opportunity& opportunity) {
    const R error = error_enabled ? rat(1, 5) : rat(0);
    const long y = upper ? 1 : -2;
    const std::string prefix = std::string(opportunity.name) + "-" +
        (error_enabled ? "bounded-" : "zero-") + (upper ? "upper-" : "lower-");
    std::vector<G> edges;
    edges.push_back(geometry(prefix + "1", {rat(0), rat(0)}, {rat(0), rat(y)}, error));
    edges.push_back(geometry(prefix + "2", {rat(0), rat(y)}, {rat(4), rat(y)}, error));
    edges.push_back(geometry(prefix + "3", {rat(4), rat(y)}, {rat(4), rat(0)}, error));
    World world(error, edges.front(), opportunity);
    bool complete = true;
    for (const auto& edge : edges) if (!world.edge(edge)) { complete = false; break; }
    const Result result = world.result(complete);
    check(result.observations == 1, "not exactly one common committed observation");
    check(result.edges == (complete ? 3u : 1u), "unexpected complete-route or censored-prefix length");
    // Expected expressions are independent checks, never inputs to admission.
    check(same(result.observed_lower, opportunity.expected_lower), "actual observation disagrees with independent motion derivation");
    std::cout << "{\"event\":\"route_result\",\"opportunity\":\"" << opportunity.name
              << "\",\"path\":\"" << (upper ? "upper" : "lower")
              << "\",\"error_halfwidth\":\"" << rational_text(error)
              << "\",\"status\":\"" << (complete ? "completed" : "blocked_after_only_observation")
              << "\",\"arrival\":";
    if (complete) interval(result.stopped_at); else std::cout << "null";
    std::cout << ",\"stopped_at\":"; interval(result.stopped_at);
    std::cout << ",\"waiting_observed\":"; interval(result.waiting);
    std::cout << ",\"observed_lower\":"; interval(result.observed_lower);
    std::cout << ",\"completed_original_moves\":" << result.edges
              << ",\"committed_observations\":" << result.observations << "}\n";
    return result;
}
void group(const Opportunity& opportunity) {
    const Result zu = route(true, false, opportunity), zl = route(false, false, opportunity);
    const Result eu = route(true, true, opportunity), el = route(false, true, opportunity);
    const R root3 = O::sqrt(rat(3)), root6 = O::sqrt(rat(6));
    check(zu.completed && zl.completed && el.completed, "a common unblocked path did not complete");
    check(same(zu.stopped_at, O::mul(rat(4), root3)), "zero-error upper changed with observation time");
    check(same(zl.stopped_at, O::mul(rat(2), O::add(root3, root6))) &&
          same(el.stopped_at, zl.stopped_at), "lower route changed with observation time or error");
    check(same(zu.waiting, rat(0)) && same(zl.waiting, rat(0)) && same(el.waiting, rat(0)), "unexpected unblocked waiting");
    check(same(eu.waiting, O::sub(opportunity.at, root3)), "bounded upper did not wait exactly until common evidence");
    check(O::cmp(zu.stopped_at, zl.stopped_at) < 0, "zero-error upper should arrive first");
    check(eu.completed == opportunity.releases, "completion disagrees with strict release control");
    if (opportunity.releases) {
        check(same(eu.stopped_at, O::add(opportunity.at, O::mul(rat(3), root3))),
              "bounded upper arrival differs from actual wait plus controller durations");
        check(O::cmp(eu.observed_lower, rat(61, 20)) > 0, "completed upper lacks strict evidence");
        check((O::cmp(eu.stopped_at, el.stopped_at) < 0) == same(opportunity.at, rat(5, 2)),
              "expected timing intervention did not restore or reverse path ranking");
    } else {
        check(same(eu.stopped_at, opportunity.at) && O::cmp(eu.observed_lower, rat(61, 20)) <= 0,
              "insufficient/equal evidence was not censored at its sole opportunity");
    }
    std::cout << "{\"event\":\"opportunity_summary\",\"opportunity\":\"" << opportunity.name
              << "\",\"zero_error_preferred\":\"upper\",\"bounded_upper_complete\":"
              << (eu.completed ? "true" : "false") << ",\"bounded_error_completed_path_comparison\":\""
              << (!eu.completed ? "not_comparable_upper_unfinished" :
                  O::cmp(eu.stopped_at, el.stopped_at) < 0 ? "upper_earlier" : "lower_earlier")
              << "\"}\n";
}
void run() {
    group({"early_2", rat(2), rat(2), false});
    group({"equal_threshold", O::sqrt(rat(61, 10)), rat(61, 20), false});
    group({"crossed_5_over_2", rat(5, 2), rat(25, 8), true});
    group({"late_4", rat(4), O::sub(O::mul(rat(24), O::sqrt(rat(2))), rat(28)), true});
    std::cout << "{\"event\":\"summary\",\"status\":\"passed\",\"checks\":" << checks
              << ",\"named_opportunities\":4,\"paired_routes\":16,"
              << "\"scope\":\"finite_common_timing_intervention_not_learning_or_full_cost\"}\n";
}
} // namespace
int main() {
    try { run(); return 0; }
    catch (const std::exception& e) { std::cerr << "timing precheck failed after " << checks << " checks: " << e.what() << '\n'; return 1; }
}

