// Finite prefix/full-MOVE x public motion/nominal waiting successor.
// Original 73 section 5 permits partial INITIAL caps only through GROUP_ADMIT.
// This two-agent domain has one UNGRANTED request and no request-cycle group.
// It exercises the exact ordinary branch; it does not implement general GROUP_ADMIT.
// Actual admission uses PositionCommit; predicted waiting never releases an owner.
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
enum class Authorization { OriginalPrefix, FullMove };
enum class Cost { MotionOnly, NominalWaiting };
const char* name(Authorization a) { return a == Authorization::OriginalPrefix ? "original_prefix_ordinary" : "full_move"; }
const char* name(Cost c) { return c == Cost::MotionOnly ? "motion_only" : "nominal_waiting"; }
struct Opportunity { const char* name; R at; };
struct Result {
    R stopped_at, waiting, observed_lower;
    unsigned observations, edges, grant_attempts, cap_grants, run_commands, prefix_no_group_checks;
    bool completed;
};

// Public, declared prior. The coefficients and eta=-1 are not inferred from
// a future controller snapshot. Matching the realized eta in this artificial
// run makes the prediction exact here, but is not an eta-robust guarantee.
R nominal_duration(const R& length) { return O::sqrt(O::mul(rat(3), length)); }
R nominal_blocker_progress(const I::Action& a, const R& elapsed) {
    check(O::cmp(elapsed, rat(0)) >= 0 && same(a.b, a.geometry.length()),
          "nominal model requires a publicly granted full cap and nonnegative elapsed");
    const R ell = a.geometry.length();
    const R launch_end = O::sqrt(O::div(O::mul(rat(4), ell), rat(3)));
    const R end = nominal_duration(ell);
    if (O::cmp(elapsed, launch_end) <= 0) return O::div(O::mul(elapsed, elapsed), rat(2));
    if (O::cmp(elapsed, end) >= 0) return ell;
    const R remaining = O::sub(end, elapsed);
    return O::sub(ell, O::mul(remaining, remaining));
}
struct Prediction { R motion, wait, arrival, certificate_lower; bool available; };
Prediction predict(const std::vector<G>& route, const P::View& public_view,
                   const Opportunity& opportunity) {
    const auto& state = public_view.structure();
    const auto& blocker = *state.actions.at("blocker")->input;
    check(state.actions.size() == 1 && state.demands.empty() && same(blocker.q, rat(0)),
          "route selection must use the common initial committed state");
    check(bool(blocker.epsilon), "prediction lacks a public source precision");
    // Public native RUN schedule says blocker launched at time zero. This
    // declared schedule/model is a prior, not remote START or motion truth.
    const R nominal_s = nominal_blocker_progress(blocker, opportunity.at);
    const R precision_lower = O::sub(nominal_s, *blocker.epsilon);
    const R forecast = O::cmp(precision_lower, blocker.q) > 0 ? precision_lower : blocker.q;
    R arrival = rat(0), movement = rat(0), waiting = rat(0);
    bool available = true;
    for (const auto& g : route) {
        std::vector<std::string> conflict;
        const auto full = g.n_mask(rat(0), g.length());
        for (const auto& cell : full.mask()) {
            const auto found = state.owners.find(cell);
            if (found == state.owners.end() || found->second.agent == "requester") continue;
            check(found->second.action == "blocker" && found->second.geometric,
                  "nominal forecast has an unsupported foreign responsibility");
            conflict.push_back(cell);
        }
        if (!conflict.empty()) {
            const auto threshold = pie_query_geometry::extract<O>(
                blocker.geometry, blocker.q, blocker.b, conflict);
            // Existing known q would eliminate these owners already. Their
            // first modeled future release is the one public observation.
            if (!threshold.crossed_by(forecast)) available = false;
            else if (O::cmp(arrival, opportunity.at) < 0) {
                waiting = O::add(waiting, O::sub(opportunity.at, arrival));
                arrival = opportunity.at;
            }
            std::cout << "{\"event\":\"public_prediction_relation\",\"move\":\""
                      << g.binding().move_occurrence << "\",\"owner\":\"blocker\",\"threshold\":\""
                      << rational_text(threshold.physical_exit) << "\",\"nominal_release\":"
                      << (threshold.crossed_by(forecast) ? "true" : "false") << "}\n";
        }
        const R duration = nominal_duration(g.length());
        movement = O::add(movement, duration);
        arrival = O::add(arrival, duration);
    }
    return {movement, waiting, arrival, forecast, available};
}
void prediction_json(const Prediction& p) {
    std::cout << "{\"motion\":"; interval(p.motion);
    std::cout << ",\"waiting_prior\":"; interval(p.wait);
    std::cout << ",\"arrival_prior\":";
    if (p.available) interval(p.arrival); else std::cout << "null";
    std::cout << ",\"certificate_lower_prior\":"; interval(p.certificate_lower);
    std::cout << ",\"conditional_prior_available\":" << (p.available ? "true" : "false") << '}';
}

class World {
    G blocker_;
    Controller blocker_motion_;
    std::unique_ptr<P> position_;
    R now_ = rat(0), waiting_ = rat(0), observed_lower_ = rat(0);
    R opportunity_;
    std::string opportunity_name_;
    Authorization authorization_;
    unsigned serial_ = 0, observations_ = 0, edges_ = 0;
    unsigned grant_attempts_ = 0, cap_grants_ = 0, run_commands_ = 0, prefix_no_group_checks_ = 0;
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
    bool attempt(const std::string& demand) {
        ++grant_attempts_;
        const auto view = position_->view();
        const auto& state = view.structure();
        // A domain check, not a fabricated GROUP_ADMIT implementation. Every
        // current request is enumerated; neither future route steps nor the
        // already GRANTED blocker can be an UNGRANTED group vertex.
        if (authorization_ == Authorization::OriginalPrefix) {
            check(state.demands.size() == 1 && state.demands.count(demand) == 1 &&
                  state.demands.at(demand)->input->requester_action.empty() &&
                  state.demands.at(demand)->input->agent == "requester",
                  "outside exact one-UNGRANTED-request prefix branch");
            check(state.actions.size() == 1 && state.actions.count("blocker") == 1 &&
                  state.actions.at("blocker")->input->agent != "requester",
                  "prefix audit cannot treat a GRANTED blocker as an ungranted group member");
            // Original group graph uses intersections with ANOTHER request's
            // initial resident. One vertex has no such edge or cyclic SCC.
            ++prefix_no_group_checks_;
            std::cout << "{\"event\":\"prefix_no_certified_group\",\"demand\":\""
                      << demand << "\",\"ungranted_vertices\":1,\"cross_request_edges\":0,"
                      << "\"cyclic_components\":0,\"granted_blocker_excluded\":true}\n";
        }
        return ready(demand);
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
        std::cout << "{\"event\":\"actual_position_committed\",\"at\":"; interval(opportunity_);
        std::cout << ",\"lower\":"; interval(observed_lower_);
        std::cout << ",\"endpoint_retained\":true}\n";
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
    World(const R& error, const G& first, const Opportunity& opportunity, Authorization authorization)
        : blocker_(geometry("blocker", {rat(2), rat(3, 2)}, {rat(8), rat(3, 2)}, error)),
          blocker_motion_({rat(1), rat(2), rat(6), rat(1)}, blocker_.length(), rat(0),
                          rat(0), rat(-1), "blocker"), opportunity_(opportunity.at),
          opportunity_name_(opportunity.name), authorization_(authorization) {
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
        check(blocker_motion_.install_cap(rat(0), blocker_.length()),
              "blocker failed to install the already committed full grant");
        check(blocker_motion_.run(rat(0)), "blocker public native RUN did not start");
    }
    P::View public_view() const { return position_->view(); }
    bool edge(const G& g) {
        const std::string move = g.binding().move_occurrence;
        resident(g);
        const auto desired = g.n_mask(rat(0), g.length());
        auto request = delta();
        request.structure.demands.emplace(move, std::make_shared<const I::Demand>(
            I::Demand{"requester", "", desired.mask(), now_, true}));
        commit(request);
        if (!attempt(move)) {
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
            const bool released = attempt(move);
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
        // Real cumulative-cap installation follows the center's committed grant.
        Controller c({rat(1), rat(2), rat(6), rat(1)}, g.length(), now_,
                     rat(0), rat(-1), move);
        check(same(position_->view().structure().actions.at(move)->input->b, g.length()) &&
              same(c.snapshot().cap(), rat(0)), "cap installed before committed grant");
        check(c.install_cap(now_, g.length()), "initial cumulative cap failed to install");
        ++cap_grants_;
        check(same(c.snapshot().state().s, rat(0)) && same(c.snapshot().state().v, rat(0)),
              "cap installation moved the reference state");
        check(c.run(now_), "native RUN failed after committed full-cap grant");
        ++run_commands_;
        std::cout << "{\"event\":\"requester_full_cap_installed\",\"move\":\""
                  << move << "\",\"at\":"; interval(now_);
        std::cout << ",\"from\":\"0\",\"to\":\"" << rational_text(g.length())
                  << "\",\"original_move_unchanged\":true}\n";
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
        std::cout << "{\"event\":\"original_move_end\",\"move\":\"" << move
                  << "\",\"at\":"; interval(now_);
        std::cout << ",\"endpoint_resident_retained\":true}\n";
        return true;
    }
    Result result(bool complete) const {
        return {now_, waiting_, observed_lower_, observations_, edges_, grant_attempts_,
                cap_grants_, run_commands_, prefix_no_group_checks_, complete};
    }
};

std::vector<G> route(bool upper) {
    const long y = upper ? 1 : -2;
    const std::string prefix = upper ? "upper-" : "lower-";
    const R error = rat(1, 5);
    std::vector<G> result;
    result.push_back(geometry(prefix + "1", {rat(0), rat(0)}, {rat(0), rat(y)}, error));
    result.push_back(geometry(prefix + "2", {rat(0), rat(y)}, {rat(4), rat(y)}, error));
    result.push_back(geometry(prefix + "3", {rat(4), rat(y)}, {rat(4), rat(0)}, error));
    return result;
}
struct CellResult { Result actual; bool upper; Prediction predicted; };
CellResult cell(const Opportunity& opportunity, Authorization authorization, Cost cost) {
    const auto upper = route(true), lower = route(false);
    check(upper.front().n_mask(rat(0), rat(0)).mask() == lower.front().n_mask(rat(0), rat(0)).mask(),
          "candidate routes do not share the initial footprint");
    World world(rat(1, 5), upper.front(), opportunity, authorization);
    // Frozen PUBLIC state only. Neither predict nor the selection expression
    // receives a World/Controller/snapshot of actual private motion.
    const auto public_at_zero = world.public_view();
    const Prediction pu = predict(upper, public_at_zero, opportunity);
    const Prediction pl = predict(lower, public_at_zero, opportunity);
    check(pu.available && pl.available, "finite comparison requires both stated priors available");
    const R upper_score = cost == Cost::MotionOnly ? pu.motion : pu.arrival;
    const R lower_score = cost == Cost::MotionOnly ? pl.motion : pl.arrival;
    const bool choose_upper = O::cmp(upper_score, lower_score) <= 0;
    const Prediction selected_prediction = choose_upper ? pu : pl;
    check(world.public_view().same_identity(public_at_zero),
          "route prediction mutated committed knowledge");
    std::cout << "{\"event\":\"selection_before_execution\",\"opportunity\":\""
              << opportunity.name << "\",\"authorization\":\"" << name(authorization)
              << "\",\"cost\":\"" << name(cost) << "\",\"selected\":\""
              << (choose_upper ? "upper" : "lower") << "\",\"decision_time\":\"0\","
              << "\"committed_blocker_q\":\"0\",\"upper_prediction\":";
    prediction_json(pu); std::cout << ",\"lower_prediction\":"; prediction_json(pl);
    std::cout << "}\n";
    bool complete = true;
    const auto& selected = choose_upper ? upper : lower;
    for (const auto& g : selected) if (!world.edge(g)) { complete = false; break; }
    const Result actual = world.result(complete);
    check(complete && actual.edges == 3 && actual.observations == 1,
          "selected route failed to complete exactly three original MOVEs with one observation");
    check(actual.cap_grants == 3 && actual.run_commands == 3,
          "unexpected requester grant/install/RUN count");
    check(actual.grant_attempts == (choose_upper ? 4u : 3u),
          "unexpected full initial-cap attempt count");
    check(actual.prefix_no_group_checks ==
          (authorization == Authorization::OriginalPrefix ? actual.grant_attempts : 0u),
          "original-prefix branch did not audit each initial admission attempt");
    // Independent expectations appear only AFTER real execution; these values
    // were not inputs to route selection, source certificates or admission.
    const R expected_sample = same(opportunity.at, rat(5, 2)) ? rat(25, 8) :
        O::sub(O::mul(rat(24), O::sqrt(rat(2))), rat(28));
    check(same(actual.observed_lower, expected_sample), "actual blocker sample regression");
    const R expected_arrival = choose_upper ?
        O::add(opportunity.at, O::mul(rat(3), O::sqrt(rat(3)))) :
        O::mul(rat(2), O::add(O::sqrt(rat(3)), O::sqrt(rat(6))));
    check(same(actual.stopped_at, expected_arrival), "actual closed-controller arrival regression");
    check(same(actual.stopped_at, selected_prediction.arrival) &&
          same(actual.waiting, selected_prediction.wait),
          "nominal prediction residual is nonzero in the matching artificial realization");
    std::cout << "{\"event\":\"factorial_cell\",\"opportunity\":\"" << opportunity.name
              << "\",\"authorization\":\"" << name(authorization) << "\",\"cost\":\""
              << name(cost) << "\",\"selected\":\"" << (choose_upper ? "upper" : "lower")
              << "\",\"arrival\":"; interval(actual.stopped_at);
    std::cout << ",\"waiting\":"; interval(actual.waiting);
    std::cout << ",\"observed_lower\":"; interval(actual.observed_lower);
    std::cout << ",\"completed_original_moves\":" << actual.edges
              << ",\"committed_observations\":" << actual.observations
              << ",\"full_initial_cap_attempts\":" << actual.grant_attempts
              << ",\"requester_cap_installs\":" << actual.cap_grants
              << ",\"requester_run_commands\":" << actual.run_commands
              << ",\"blocker_cap_installs\":1,\"blocker_run_commands\":1"
              << ",\"partial_initial_caps\":0,\"cap_extensions\":0,\"group_admissions\":0"
              << ",\"prefix_no_group_checks\":" << actual.prefix_no_group_checks
              << ",\"native_ends\":3,\"prediction_arrival_error\":\"0\"}\n";
    return {actual, choose_upper, selected_prediction};
}
void group(const Opportunity& opportunity) {
    const CellResult pm = cell(opportunity, Authorization::OriginalPrefix, Cost::MotionOnly);
    const CellResult pw = cell(opportunity, Authorization::OriginalPrefix, Cost::NominalWaiting);
    const CellResult fm = cell(opportunity, Authorization::FullMove, Cost::MotionOnly);
    const CellResult fw = cell(opportunity, Authorization::FullMove, Cost::NominalWaiting);
    check(pm.upper == fm.upper && pw.upper == fw.upper &&
          same(pm.actual.stopped_at, fm.actual.stopped_at) &&
          same(pw.actual.stopped_at, fw.actual.stopped_at) &&
          same(pm.actual.waiting, fm.actual.waiting) && same(pw.actual.waiting, fw.actual.waiting),
          "authorization comparison changed this ordinary full-initial-cap domain");
    check(pm.upper && fm.upper, "base movement cost did not choose the shorter upper route");
    check(pw.upper == same(opportunity.at, rat(5, 2)),
          "public nominal waiting rule did not make the expected ex-ante choice");
    const R gain = O::sub(pm.actual.stopped_at, pw.actual.stopped_at);
    check(O::cmp(gain, rat(0)) >= 0, "nominal waiting did not match this finite prediction");
    std::cout << "{\"event\":\"factorial_summary\",\"opportunity\":\"" << opportunity.name
              << "\",\"authorization_trajectories_equal\":true,\"waiting_rule_arrival_reduction\":";
    interval(gain); std::cout << "}\n";
}
void run() {
    group({"crossed_5_over_2", rat(5, 2)});
    group({"late_4", rat(4)});
    std::cout << "{\"event\":\"summary\",\"status\":\"passed\",\"checks\":" << checks
              << ",\"named_opportunities\":2,\"factorial_cells\":8,"
              << "\"scope\":\"ordinary_prefix_contract_x_public_nominal_waiting_not_general_group_or_learning\"}\n";
}
} // namespace
int main() {
    try { run(); return 0; }
    catch (const std::exception& e) {
        std::cerr << "prefix precheck failed after " << checks << " checks: " << e.what() << '\n';
        return 1;
    }
}
