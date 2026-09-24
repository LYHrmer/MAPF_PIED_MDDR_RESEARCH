// Successor of the frozen artificial AND witness. Reuse its geometry/source
// helpers verbatim; its old entry point remains compiled but is never run.
#define main preserved_legal_and_entry
#include "legal_and_fixture.cpp"
#undef main
#include <set>

namespace {
enum class Decision { OriginalSrdc, OriginalRR, UnitForecastGreedy, UnitForecastPair };
const char* name(Decision d) {
    switch (d) {
    case Decision::OriginalSrdc: return "original_srdc_unpriced";
    case Decision::OriginalRR: return "original_rr";
    case Decision::UnitForecastGreedy: return "unit_forecast_one_step";
    case Decision::UnitForecastPair: return "unit_forecast_two_step";
    }
    throw std::logic_error("unknown decision");
}
void display_interval(const R& value) {
    const long scale = 1000000;
    check(O::cmp(value, rat(0)) >= 0 && O::cmp(value, rat(32)) < 0, "display range");
    long lo = 0, hi = 32 * scale;
    while (hi - lo > 1) {
        const long mid = lo + (hi - lo) / 2;
        if (O::cmp(rat(mid, scale), value) <= 0) lo = mid; else hi = mid;
    }
    std::cout << "{\"lower\":" << lo << ",\"upper\":"
              << (same(value, rat(lo, scale)) ? lo : hi) << ",\"denominator\":" << scale << '}';
}
std::unique_ptr<P> initial_for(Decision decision) {
    const auto original = initial();
    const auto physical = original->view();
    S scheduler("selector-empty", rat(0), decision == Decision::OriginalRR ?
                pie_query::QueryPolicy::RoundRobin : pie_query::QueryPolicy::Srdc);
    S::Delta copy{{"selector-empty", "selector-initial", {}, {}, {}}, rat(0), {}, {}};
    for (const auto& item : physical.structure().actions) copy.structure.actions.emplace(item.first, item.second->input);
    for (const auto& item : physical.structure().owners)
        copy.structure.owners.emplace(item.first, std::make_shared<const I::Owner>(item.second));
    for (const auto& item : physical.structure().demands) copy.structure.demands.emplace(item.first, item.second->input);
    auto prepared = scheduler.prepare(copy); scheduler.commit(std::move(prepared));
    pie_query::Map<P::SnapshotIds> ids;
    for (const auto& item : copy.structure.actions) ids.emplace(item.first, P::SnapshotIds{
        item.first + "-selector-seed", item.first + "-selector-current", "", ""});
    return std::unique_ptr<P>(new P(scheduler, ids));
}

// Diagnostic forecast: each eligible action's next lower is estimated as
// b-epsilon using COMMITTED fields only. This is an optimistic unit-success
// assumption, not a guaranteed bound, learned predictor or physical truth.
// Both new decision rules use exactly this same forecast and unit demand value.
bool forecast_clears(const I::State& state, const I::Relation& relation,
                     const std::set<std::string>& selected) {
    if (!relation.retirable || !relation.threshold || !selected.count(relation.action)) return false;
    const auto& a = *state.actions.at(relation.action)->input;
    return a.eligible && a.epsilon && O::cmp(O::sub(a.b, *a.epsilon), *relation.threshold) > 0;
}
unsigned predicted_admissions(const I::State& state, const std::set<std::string>& selected) {
    unsigned count = 0;
    for (const auto& item : state.demands) {
        const auto& d = *item.second;
        if (!d.input->non_owner_eligible || d.relations.empty()) continue;
        bool all = true;
        for (const auto& r : d.relations) if (!forecast_clears(state, r, selected)) all = false;
        if (all) ++count;
    }
    return count;
}
R predicted_partial(const I::State& state, const std::string& key) {
    R sum = rat(0);
    for (const auto& item : state.demands) {
        const auto& d = *item.second;
        if (!d.input->non_owner_eligible || d.relations.empty()) continue;
        for (const auto& r : d.relations)
            if (forecast_clears(state, r, {key}))
                sum = O::add(sum, rat(1, static_cast<unsigned long>(d.relations.size())));
    }
    return sum;
}
std::string diagnostic_choose(const P::View& view, Decision rule, unsigned remaining) {
    const auto& state = view.structure();
    std::vector<std::string> candidates;
    for (const auto& a : state.actions) if (a.second->input->eligible) candidates.push_back(a.first);
    check(!candidates.empty(), "no diagnostic candidate");
    if (rule == Decision::UnitForecastPair && remaining == 2 && candidates.size() >= 2) {
        unsigned best = 0; std::string chosen;
        for (const auto& a : candidates) for (const auto& b : candidates) {
            if (a == b) continue;
            const unsigned value = predicted_admissions(state, {a, b});
            // Remaining ties keep the first lexicographic ordered pair.
            if (chosen.empty() || value > best) { chosen = a; best = value; }
        }
        return chosen;
    }
    unsigned best_a = 0; R best_p = rat(0); std::string chosen;
    for (const auto& a : candidates) {
        const unsigned admissions = predicted_admissions(state, {a});
        const R partial = predicted_partial(state, a);
        if (chosen.empty() || admissions > best_a ||
            (admissions == best_a && O::cmp(partial, best_p) > 0)) {
            chosen = a; best_a = admissions; best_p = partial;
        }
    }
    return chosen;
}

struct Flight {
    std::string key;
    R started;
    Controller controller;
    std::shared_ptr<const R> completed;
};
struct Outcome {
    std::vector<std::string> order;
    std::vector<Flight> flights;
    unsigned by_five, by_six, by_seven;
};
bool physically_ready(const P::View& view, const I::Demand& d) {
    if (!d.non_owner_eligible) return false;
    for (const auto& cell : d.resources) {
        const auto found = view.structure().owners.find(cell);
        if (found != view.structure().owners.end() && found->second.agent != d.agent) return false;
    }
    return true;
}
void admit_and_start(P& p, const R& at, std::vector<Flight>& flights) {
    for (const std::string key : {"D1", "D2", "D3"}) {
        const auto before = p.view();
        const auto found = before.structure().demands.find(key);
        if (found == before.structure().demands.end() || !physically_ready(before, *found->second->input)) continue;
        G g = requester(key);
        const auto resident = g.n_mask(rat(0), rat(0));
        for (const auto& cell : resident.mask()) {
            const auto& own = before.structure().owners.at(cell);
            check(own.agent == "agent-" + key && own.action.empty() && !own.geometric,
                  "requester did not retain waiting residency");
        }
        S::Delta grant{{before.structure().view_id, "start-" + key, {}, {}, {}}, at, {}, {}};
        auto a = std::make_shared<I::Action>(*action("agent-" + key, g));
        a->eligible = false; // This finite two-query protocol observes blockers only.
        grant.structure.actions.emplace(key, std::move(a));
        const auto full = g.n_mask(rat(0), g.length());
        for (const auto& cell : full.mask()) {
            const auto owner = before.structure().owners.find(cell);
            check(owner == before.structure().owners.end() || owner->second.agent == "agent-" + key,
                  "immediate admission conflicts with a foreign owner");
            grant.structure.owners.emplace(cell, std::make_shared<const I::Owner>(I::Owner{key, "agent-" + key, key, true}));
        }
        grant.structure.demands.emplace(key, nullptr);
        auto prepared = p.prepare_admitted_update(grant, {{key, {key + "-started-seed", key + "-started-current", "", ""}}});
        p.commit(std::move(prepared));
        Controller c({rat(1), rat(2), rat(6), rat(1)}, g.length(), at, g.length(), rat(-1), key);
        check(c.run(at), "admitted requester failed to launch immediately");
        flights.push_back({key, at, std::move(c), nullptr});
        std::cout << "{\"event\":\"start\",\"move\":\"" << key << "\",\"at\":\"" << exact(at) << "\"}\n";
    }
}
void advance_all(std::vector<Controller>& blockers, std::vector<Flight>& flights, const R& at) {
    for (auto& b : blockers) b.advance_to(at);
    for (auto& f : flights) {
        f.controller.advance_to(at);
        if (f.controller.snapshot().closed() && !f.completed) {
            const auto witness = f.controller.snapshot();
            check(same(witness.state().s, witness.length()) && same(witness.state().v, rat(0)),
                  "completion is not original endpoint at rest");
            check(witness.move_id() == f.key && same(witness.cap(), witness.length()), "completion changed original MOVE");
            f.completed = std::make_shared<const R>(at);
            std::cout << "{\"event\":\"original_move_completed\",\"move\":\"" << f.key << "\",\"at\":";
            display_interval(at); std::cout << "}\n";
        }
    }
}
unsigned completed_by(const std::vector<Flight>& flights, const R& time) {
    unsigned count = 0;
    for (const auto& f : flights) if (f.completed && O::cmp(*f.completed, time) <= 0) ++count;
    return count;
}
Outcome execute(Decision rule) {
    auto held = initial_for(rule); P& p = *held;
    std::vector<Controller> blockers{controller("A"), controller("B"), controller("C")};
    std::vector<Flight> flights;
    std::vector<std::string> order;
    std::cout << "{\"event\":\"policy_begin\",\"policy\":\"" << name(rule) << "\"}\n";
    for (unsigned step = 0; step < 2; ++step) {
        const R at = step == 0 ? rat(5, 2) : rat(11, 4);
        advance_all(blockers, flights, at);
        const auto before = p.view();
        std::string key;
        if (rule == Decision::OriginalSrdc || rule == Decision::OriginalRR) {
            const auto choice = p.choose(at);
            check(choice.kind() == pie_query::ChoiceKind::RoundRobin && choice.score(), "unpriced original did not use RR");
            key = choice.score()->action;
            check(p.view().same_identity(before), "choose changed committed state");
            auto published = p.prepare_query_publication(choice, {choice.view(), key, choice.score()->source,
                "artificial-native-publication-not-AUTH", choice.generation(), at});
            p.commit(std::move(published));
        } else {
            key = diagnostic_choose(before, rule, 2 - step);
            check(p.view().same_identity(before), "forecast or lookahead changed committed state");
        }
        check(key == "A" || key == "B" || key == "C", "selected a non-blocker");
        check(std::find(order.begin(), order.end(), key) == order.end(), "repeated observation in at-most-once protocol");
        std::cout << "{\"event\":\"selection\",\"step\":" << step + 1 << ",\"action\":\"" << key
                  << "\",\"at\":\"" << exact(at) << "\",\"kind\":\""
                  << ((rule == Decision::OriginalSrdc || rule == Decision::OriginalRR) ? "actual_rr_choice" : "diagnostic_unit_forecast") << "\"}\n";
        // Only AFTER selection can the private witness enter the admitted
        // certificate path. Nothing in either selector sees the controller.
        query(p, blockers.at(static_cast<unsigned>(key[0] - 'A')), at, std::string(name(rule)) + "-" + key);
        order.push_back(key);
        S::Delta observed{{p.view().structure().view_id, "observed-" + key, {}, {}, {}}, at, {}, {}};
        auto action_copy = std::make_shared<I::Action>(*p.view().structure().actions.at(key)->input);
        action_copy->eligible = false;
        observed.structure.actions.emplace(key, std::move(action_copy));
        auto updated = p.prepare_admitted_update(observed, {}); p.commit(std::move(updated));
        for (const auto& b : blockers) {
            const std::string id = b.snapshot().move_id();
            if (std::find(order.begin(), order.end(), id) == order.end())
                check(same(p.view().structure().actions.at(id)->input->q, rat(0)), "unobserved truth leaked into q");
        }
        admit_and_start(p, at, flights);
    }
    // Advance by ACTUAL autonomous boundaries, so recorded completion times
    // are not coarse sampling times or formula-filled arrival labels.
    for (unsigned event = 0; event < 32; ++event) {
        std::shared_ptr<const R> next;
        auto consider = [&](const Controller& c) {
            const auto s = c.snapshot();
            if (s.closed()) return;
            const R boundary = O::add(s.segment_start(), s.segment().duration());
            if (!next || O::cmp(boundary, *next) < 0) next = std::make_shared<const R>(boundary);
        };
        for (const auto& b : blockers) consider(b);
        for (const auto& f : flights) consider(f.controller);
        if (!next) break;
        advance_all(blockers, flights, *next);
    }
    for (const auto& b : blockers) check(b.snapshot().closed(), "blocker did not reach its original endpoint");
    for (const auto& f : flights) {
        check(bool(f.completed), "started requester failed to complete");
        const G g = requester(f.key);
        const R expected = O::add(f.started, O::sqrt(O::mul(rat(3), g.length())));
        check(same(*f.completed, expected), "controller duration differs from independent check");
        const auto endpoint = g.n_mask(g.length(), g.length());
        for (const auto& cell : endpoint.mask())
            check(p.view().structure().owners.at(cell).action == f.key, "completion removed endpoint responsibility");
    }
    for (const auto& item : p.view().structure().demands) {
        const G g = requester(item.first);
        const auto residence = g.n_mask(rat(0), rat(0));
        for (const auto& cell : residence.mask())
            check(p.view().structure().owners.at(cell).agent == item.second->input->agent,
                  "unadmitted requester lost residency");
    }
    const unsigned five = completed_by(flights, rat(5));
    const unsigned six = completed_by(flights, rat(6));
    const unsigned seven = completed_by(flights, rat(7));
    const bool greedy = rule == Decision::UnitForecastGreedy;
    check(order == (greedy ? std::vector<std::string>{"C", "A"} : std::vector<std::string>{"A", "B"}), "unexpected actual choice sequence");
    check(flights.size() == (greedy ? 1u : 2u), "unexpected immediate admissions");
    check(five == 0 && six == (greedy ? 1u : 0u) && seven == (greedy ? 1u : 2u), "finite completion ordering did not match expected horizon reversal");
    for (const auto& f : flights) check(same(f.started, greedy ? rat(5, 2) : rat(11, 4)), "early-ready work was delayed");
    std::cout << "{\"event\":\"policy_result\",\"policy\":\"" << name(rule)
              << "\",\"order\":[\"" << order[0] << "\",\"" << order[1]
              << "\"],\"started\":" << flights.size()
              << ",\"completed_by_5\":" << five << ",\"completed_by_6\":" << six
              << ",\"completed_by_7\":" << seven << "}\n";
    return {std::move(order), std::move(flights), five, six, seven};
}
void run_execution_comparison() {
    const auto sr = execute(Decision::OriginalSrdc);
    const auto rr = execute(Decision::OriginalRR);
    const auto one = execute(Decision::UnitForecastGreedy);
    const auto two = execute(Decision::UnitForecastPair);
    check(sr.order == rr.order && rr.order == two.order, "fixture falsely claims lookahead beats original selectors");
    check(one.by_six > two.by_six && one.by_seven < two.by_seven, "completion advantage was made horizon-independent");
    std::cout << "{\"event\":\"summary\",\"status\":\"passed\",\"checks\":" << checks
              << ",\"production_auth\":false,\"paid_cost\":false,\"task_service\":false,\"learning\":false}\n";
}
} // namespace
int main() {
    try { run_execution_comparison(); return 0; }
    catch (const std::exception& e) { std::cerr << "decision execution failed after " << checks << " checks: " << e.what() << '\n'; return 1; }
}
