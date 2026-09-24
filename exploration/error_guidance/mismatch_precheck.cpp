// Finite frozen-prior mismatch successor: only requester actual eta changes.
// The public nominal predictor is copied byte-for-byte from prefix_precheck.cpp.
// Same footprint/Z, owners, blocker, observations and original ordinary grant rule.
// The selected route is fixed before either actual paired trajectory is executed.
// Offline counterfactual results and private eta never enter the selector.
#include "pie_geometry_flint.hpp"
#include "pie_position_commit.hpp"
#include "pie_reference_controller.hpp"
#include <iostream>
#include <memory>
#include <sstream>
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
    check(O::cmp(value, rat(-64)) >= 0 && O::cmp(value, rat(64)) < 0, "display interval out of finite range");
    long lo = -64 * scale, hi = 64 * scale;
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
    R moving;
    std::vector<R> move_durations;
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
    R requester_eta_, moving_ = rat(0);
    std::vector<R> move_durations_;
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
    World(const R& error, const G& first, const Opportunity& opportunity, Authorization authorization,
          const R& requester_eta)
        : blocker_(geometry("blocker", {rat(2), rat(3, 2)}, {rat(8), rat(3, 2)}, error)),
          blocker_motion_({rat(1), rat(2), rat(6), rat(1)}, blocker_.length(), rat(0),
                          rat(0), rat(-1), "blocker"), opportunity_(opportunity.at),
          opportunity_name_(opportunity.name), authorization_(authorization), requester_eta_(requester_eta) {
        check(O::cmp(requester_eta_, rat(-1)) >= 0 && O::cmp(requester_eta_, rat(1)) <= 0,
              "requester eta outside the unchanged delta=1 domain");
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
        const R entered_at = now_;
        Controller c({rat(1), rat(2), rat(6), rat(1)}, g.length(), now_,
                     rat(0), requester_eta_, move);
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
                  same(c.snapshot().cap(), g.length()) && same(c.snapshot().eta(), requester_eta_),
                  "edge changed original MOVE, installed cap or the fixed private eta");
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
        const R duration = O::sub(now_, entered_at);
        move_durations_.push_back(duration);
        moving_ = O::add(moving_, duration);
        std::cout << "{\"event\":\"original_move_end\",\"move\":\"" << move
                  << "\",\"at\":"; interval(now_);
        std::cout << ",\"endpoint_resident_retained\":true}\n";
        return true;
    }
    Result result(bool complete) const {
        return {now_, waiting_, observed_lower_, observations_, edges_, grant_attempts_,
                cap_grants_, run_commands_, prefix_no_group_checks_, complete, moving_, move_durations_};
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
struct Condition { const char* name; R actual_requester_eta; };

// This signature contains only public committed facts. Geometry definitions,
// route vertices, source precision and nominal model are constant across all
// cases; exact owner/action content is checked across the hidden conditions.
std::string public_signature(const P::View& view) {
    const auto& state = view.structure();
    std::ostringstream out;
    out << "view=" << state.view_id << ";demands=" << state.demands.size() << ';';
    for (const auto& item : state.actions) {
        const auto& a = *item.second->input;
        out << "a=" << item.first << ',' << a.agent << ',' << a.source << ',' << a.profile
            << ',' << a.geometry.binding().move_occurrence << ',' << rational_text(a.geometry.length())
            << ',' << rational_text(a.q) << ',' << rational_text(a.b) << ','
            << rational_text(*a.epsilon) << ',' << a.eligible << ';';
    }
    for (const auto& item : state.owners) {
        const auto& o = item.second;
        out << "o=" << item.first << ',' << o.responsibility << ',' << o.agent
            << ',' << o.action << ',' << o.geometric << ';';
    }
    return out.str();
}
struct Decision { Prediction upper, lower; bool waiting_upper, motion_upper; };
Decision choose(const std::vector<G>& upper, const std::vector<G>& lower,
                const P::View& committed, const Opportunity& opportunity) {
    // This function cannot see Condition, World or a Controller.
    const Prediction pu = predict(upper, committed, opportunity);
    const Prediction pl = predict(lower, committed, opportunity);
    check(pu.available && pl.available, "fixed named cases need the same available nominal priors");
    return {pu, pl, O::cmp(pu.arrival, pl.arrival) <= 0, O::cmp(pu.motion, pl.motion) <= 0};
}
void print_decision(const Decision& d, const Opportunity& o, const Condition& condition,
                    const std::string& signature) {
    // condition.name is an OFFLINE logging label, not supplied to choose().
    std::cout << "{\"event\":\"selection_before_either_execution\",\"condition\":\""
              << condition.name << "\",\"opportunity\":\"" << o.name
              << "\",\"decision_time\":\"0\",\"nominal_requester_eta\":\"-1\","
              << "\"public_input_signature\":\"" << signature
              << "\",\"legal_completed_requester_history_count\":0,"
              << "\"waiting_selected\":\"" << (d.waiting_upper ? "upper" : "lower")
              << "\",\"motion_selected\":\"" << (d.motion_upper ? "upper" : "lower")
              << "\",\"upper_prediction\":";
    prediction_json(d.upper); std::cout << ",\"lower_prediction\":"; prediction_json(d.lower);
    std::cout << "}\n";
}
Result execute(World& world, const std::vector<G>& path, bool upper,
               const Condition& condition, const Opportunity& opportunity,
               const char* role) {
    bool complete = true;
    for (const auto& edge : path) if (!world.edge(edge)) { complete = false; break; }
    const Result actual = world.result(complete);
    check(actual.observations == 1, "paired route did not receive the one common observation");
    if (complete) {
        check(actual.edges == 3 && actual.cap_grants == 3 && actual.run_commands == 3,
              "completed route lacks three actual original MOVE lifecycles");
        check(actual.prefix_no_group_checks == actual.grant_attempts &&
              actual.grant_attempts == (upper ? 4u : 3u),
              "ordinary-prefix admission attempt count changed");
        check(same(actual.stopped_at, O::add(actual.moving, actual.waiting)),
              "actual clock does not equal native motion plus waiting");
        check(actual.move_durations.size() == 3, "missing actual MOVE durations");
    }
    // Expected blocker truth is checked after this execution; never an input to
    // the frozen prior, the selected path, or the native certificate source.
    const R expected_sample = same(opportunity.at, rat(5, 2)) ? rat(25, 8) :
        O::sub(O::mul(rat(24), O::sqrt(rat(2))), rat(28));
    check(same(actual.observed_lower, expected_sample), "unchanged blocker sample regressed");
    std::cout << "{\"event\":\"paired_route_result\",\"condition\":\"" << condition.name
              << "\",\"private_requester_eta\":\"" << rational_text(condition.actual_requester_eta)
              << "\",\"opportunity\":\"" << opportunity.name << "\",\"path\":\""
              << (upper ? "upper" : "lower") << "\",\"execution_role\":\"" << role
              << "\",\"authorization\":\"" << name(Authorization::OriginalPrefix)
              << "\",\"completed\":" << (complete ? "true" : "false") << ",\"arrival\":";
    if (complete) interval(actual.stopped_at); else std::cout << "null";
    std::cout << ",\"stopped_at\":"; interval(actual.stopped_at);
    std::cout << ",\"waiting\":"; interval(actual.waiting);
    std::cout << ",\"moving\":"; interval(actual.moving);
    std::cout << ",\"move_durations\":[";
    for (std::size_t i = 0; i < actual.move_durations.size(); ++i) {
        if (i) std::cout << ',';
        interval(actual.move_durations[i]);
    }
    std::cout << "],\"completed_original_moves\":" << actual.edges
              << ",\"committed_observations\":" << actual.observations
              << ",\"full_initial_cap_attempts\":" << actual.grant_attempts
              << ",\"requester_cap_installs\":" << actual.cap_grants
              << ",\"requester_run_commands\":" << actual.run_commands
              << ",\"blocker_cap_installs\":1,\"blocker_run_commands\":1,"
              << "\"partial_initial_caps\":0,\"cap_extensions\":0,\"group_admissions\":0}\n";
    return actual;
}
struct Pair {
    Decision decision;
    Result upper, lower;
    std::string signature;
};
Pair paired_case(const Condition& condition, const Opportunity& opportunity) {
    const auto upper = route(true), lower = route(false);
    check(upper.front().n_mask(rat(0), rat(0)).mask() == lower.front().n_mask(rat(0), rat(0)).mask(),
          "candidate routes do not share the same initial requester footprint");
    World selected_world(rat(1, 5), upper.front(), opportunity,
                         Authorization::OriginalPrefix, condition.actual_requester_eta);
    const auto initial = selected_world.public_view();
    const std::string signature = public_signature(initial);
    const Decision decision = choose(upper, lower, initial, opportunity);
    check(selected_world.public_view().same_identity(initial),
          "prediction changed the committed public state");
    print_decision(decision, opportunity, condition, signature);

    // The nominal-waiting choice is actually executed first. The second route
    // is an independent offline counterfactual, never a query for the selector.
    const auto& selected_path = decision.waiting_upper ? upper : lower;
    const Result selected = execute(selected_world, selected_path, decision.waiting_upper,
                                    condition, opportunity, "selected_by_frozen_waiting");
    World alternative_world(rat(1, 5), upper.front(), opportunity,
                            Authorization::OriginalPrefix, condition.actual_requester_eta);
    check(public_signature(alternative_world.public_view()) == signature,
          "offline counterfactual did not rebuild the same initial public state");
    const auto& alternative_path = decision.waiting_upper ? lower : upper;
    const Result alternative = execute(alternative_world, alternative_path, !decision.waiting_upper,
                                       condition, opportunity, "offline_other_route");
    const Result actual_upper = decision.waiting_upper ? selected : alternative;
    const Result actual_lower = decision.waiting_upper ? alternative : selected;
    if (actual_upper.completed && actual_lower.completed) {
        const bool upper_best = O::cmp(actual_upper.stopped_at, actual_lower.stopped_at) <= 0;
        const R best = upper_best ? actual_upper.stopped_at : actual_lower.stopped_at;
        const Result motion_selected = decision.motion_upper ? actual_upper : actual_lower;
        const R selection_loss = O::sub(selected.stopped_at, best);
        const R motion_loss = O::sub(motion_selected.stopped_at, best);
        // Loss is defined against this finite two-route reference, not a global
        // oracle. Gain and prediction errors may have either sign.
        check(O::cmp(selection_loss, rat(0)) >= 0 && O::cmp(motion_loss, rat(0)) >= 0,
              "finite reference minimum is inconsistent");
        std::cout << "{\"event\":\"mismatch_comparison\",\"condition\":\"" << condition.name
                  << "\",\"opportunity\":\"" << opportunity.name
                  << "\",\"offline_best_of_two\":\"" << (upper_best ? "upper" : "lower")
                  << "\",\"waiting_selected\":\"" << (decision.waiting_upper ? "upper" : "lower")
                  << "\",\"motion_selected\":\"" << (decision.motion_upper ? "upper" : "lower")
                  << "\",\"waiting_selection_loss\":"; interval(selection_loss);
        std::cout << ",\"motion_selection_loss\":"; interval(motion_loss);
        std::cout << ",\"waiting_gain_over_motion\":";
        interval(O::sub(motion_selected.stopped_at, selected.stopped_at));
        std::cout << ",\"upper_arrival_actual_minus_prior\":";
        interval(O::sub(actual_upper.stopped_at, decision.upper.arrival));
        std::cout << ",\"lower_arrival_actual_minus_prior\":";
        interval(O::sub(actual_lower.stopped_at, decision.lower.arrival));
        std::cout << ",\"upper_wait_actual_minus_prior\":";
        interval(O::sub(actual_upper.waiting, decision.upper.wait));
        std::cout << ",\"lower_wait_actual_minus_prior\":";
        interval(O::sub(actual_lower.waiting, decision.lower.wait));
        std::cout << ",\"waiting_policy\":\"" << name(Cost::NominalWaiting)
                  << "\",\"motion_policy\":\"" << name(Cost::MotionOnly)
                  << "\",\"legal_completed_requester_history_count\":0}\n";
    } else {
        std::cout << "{\"event\":\"mismatch_comparison_censored\",\"condition\":\""
                  << condition.name << "\",\"opportunity\":\"" << opportunity.name
                  << "\",\"arrival_loss\":null,\"reason\":\"a_paired_route_unfinished\"}\n";
    }
    return {decision, actual_upper, actual_lower, signature};
}
void verify_analytic_motion_after_execution(const Pair& pair, const R& scale,
                                             const Opportunity& opportunity) {
    // Independent check only after BOTH actual trajectories. It never supplies
    // Controller durations, certificates, public priors, or path decisions.
    if (!pair.upper.completed || !pair.lower.completed) return;
    const R root2 = O::sqrt(rat(2));
    check(same(pair.upper.move_durations[0], scale) &&
          same(pair.upper.move_durations[1], O::mul(rat(2), scale)) &&
          same(pair.upper.move_durations[2], scale), "upper real MOVE durations disagree with independent derivation");
    check(same(pair.lower.move_durations[0], O::mul(root2, scale)) &&
          same(pair.lower.move_durations[1], O::mul(rat(2), scale)) &&
          same(pair.lower.move_durations[2], O::mul(root2, scale)),
          "lower real MOVE durations disagree with independent derivation");
    check(same(pair.upper.stopped_at, O::add(opportunity.at, O::mul(rat(3), scale))) &&
          same(pair.lower.stopped_at, O::mul(O::mul(rat(2), O::add(rat(1), root2)), scale)),
          "actual paired arrival disagrees with independent motion derivation");
}
void group(const Opportunity& opportunity) {
    const Pair matched = paired_case({"matched_eta_minus_one", rat(-1)}, opportunity);
    const Pair mismatch = paired_case({"mismatch_eta_plus_one", rat(1)}, opportunity);
    check(matched.signature == mismatch.signature &&
          matched.decision.waiting_upper == mismatch.decision.waiting_upper &&
          matched.decision.motion_upper == mismatch.decision.motion_upper &&
          same(matched.decision.upper.arrival, mismatch.decision.upper.arrival) &&
          same(matched.decision.lower.arrival, mismatch.decision.lower.arrival),
          "hidden requester eta changed the public input or frozen decision");

    verify_analytic_motion_after_execution(matched, O::sqrt(rat(3)), opportunity);
    const R fast_scale = O::div(O::sub(rat(3), O::div(rat(1), O::sqrt(rat(3)))), O::sqrt(rat(5)));
    verify_analytic_motion_after_execution(mismatch, fast_scale, opportunity);
    std::cout << "{\"event\":\"information_boundary\",\"opportunity\":\"" << opportunity.name
              << "\",\"same_public_inputs_across_private_conditions\":true,"
              << "\"same_frozen_decision\":true,\"legal_requester_history_at_decision\":0,"
              << "\"private_eta_exposed_to_predictor\":false,\"exact_instance_inference_supported\":false}\n";
}
void run() {
    group({"crossed_5_over_2", rat(5, 2)});
    group({"late_4", rat(4)});
    std::cout << "{\"event\":\"summary\",\"status\":\"passed\",\"checks\":" << checks
              << ",\"named_opportunities\":2,\"named_private_conditions\":2,\"actual_route_executions\":8,"
              << "\"scope\":\"frozen_public_prior_private_requester_mismatch_not_learning_or_full_cost\"}\n";
}
} // namespace
int main() {
    try { run(); return 0; }
    catch (const std::exception& e) {
        std::cerr << "mismatch precheck failed after " << checks << " checks: " << e.what() << '\n';
        return 1;
    }
}
