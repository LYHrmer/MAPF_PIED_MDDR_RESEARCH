// Program-local artificial component inputs, not a production/AUTH query.
// No files, seeds, research workloads, guest, controller or world are read/run.
#include "component_snapshot.hpp"
#include <iostream>
#include <memory>
#include <stdexcept>
#include <string>
#include <utility>

namespace {
namespace Export = pie_learning_component;
using O = Export::Ops;
using R = Export::Real;
using P = Export::Position;
using S = Export::Scheduler;
using I = Export::Index;
using G = P::Geometry;
unsigned checks = 0;
const std::string run_id = "synthetic-component-run";

void check(bool yes, const char* reason) {
    ++checks;
    if (!yes) throw std::runtime_error(reason);
}
R rat(long numerator, unsigned long denominator = 1) {
    struct Integers {
        fmpz_t n, d;
        Integers() { fmpz_init(n); fmpz_init(d); }
        ~Integers() { fmpz_clear(n); fmpz_clear(d); }
        Integers(const Integers&) = delete;
        Integers& operator=(const Integers&) = delete;
    } values;
    fmpz_set_si(values.n, numerator); fmpz_set_ui(values.d, denominator);
    return R::from_rational(values.n, values.d);
}
G::Piece segment(const R& left, const R& right) {
    return {{left, rat(0)}, {right, rat(0)}};
}
G geometry(const std::string& move, long offset, const std::string& prefix) {
    return G(G::Input{{"component-v1", "exact-flint", "fixture-plane", "unit", move},
        {rat(offset), rat(0)}, {rat(offset + 1), rat(0)}, {{{rat(0), rat(0)}}},
        {{rat(0), rat(0)}, {rat(0), rat(0)}},
        {{prefix + "end", {segment(rat(10 * offset + 9, 10), rat(offset + 1))}},
         {prefix + "pending", {segment(rat(offset), rat(5 * offset + 3, 5))}},
         {prefix + "short", {segment(rat(offset), rat(10 * offset + 3, 10))}}}}, true);
}
void add_action(S::Delta& delta, const std::string& move, const std::string& agent,
                const std::string& profile, long offset, const std::string& prefix,
                const std::shared_ptr<const R>& precision) {
    G g = geometry(move, offset, prefix);
    delta.structure.actions.emplace(move, std::make_shared<const I::Action>(
        I::Action{agent, "fixture-position-source", profile, g, rat(0), rat(1), precision, true}));
    const auto initial_mask = g.g_init(rat(1), "initial-mask-" + move);
    for (const auto& resource : initial_mask.mask())
        delta.structure.owners.emplace(resource, std::make_shared<const I::Owner>(
            I::Owner{move, agent, move, true}));
}
S initial() {
    S scheduler("empty", rat(0));
    S::Delta delta{{"empty", "initial", {}, {}, {}}, rat(0), {}, {}};
    add_action(delta, "move-A", "agent-A", "precision-profile", 0, "a-",
               std::make_shared<const R>(rat(1, 10)));
    add_action(delta, "move-U", "agent-U", "unknown-precision", 2, "u-", nullptr);
    delta.structure.owners.emplace("resident-r1", std::make_shared<const I::Owner>(
        I::Owner{"resident-one", "agent-R1", "", false}));
    delta.structure.owners.emplace("resident-r2", std::make_shared<const I::Owner>(
        I::Owner{"resident-two", "agent-R2", "", false}));
    delta.structure.demands.emplace("demand-single", std::make_shared<const I::Demand>(
        I::Demand{"requester-B", "", {"a-pending"}, rat(0), true}));
    delta.structure.demands.emplace("demand-and", std::make_shared<const I::Demand>(
        I::Demand{"requester-C", "", {"a-pending", "resident-r1", "resident-r2"}, rat(0), true}));
    delta.structure.demands.emplace("demand-unknown", std::make_shared<const I::Demand>(
        I::Demand{"requester-D", "", {"u-pending"}, rat(0), true}));
    auto prepared = scheduler.prepare(delta);
    scheduler.commit(std::move(prepared));
    return scheduler;
}
struct Certificate {
    S::Evidence evidence;
    const G::Binding& binding() const { return evidence.binding; }
    const R& lower_bound() const { return evidence.lower; }
    const R& captured_at() const { return evidence.captured; }
    const R& delivered_at() const { return evidence.delivered; }
    const S::Evidence* precision_evidence() const { return &evidence; }
};
Certificate certificate(const P::View& view, const R& lower, long time, const std::string& key) {
    const auto& a = *view.structure().actions.at("move-A")->input;
    const std::string provenance = "fixture \"certificate\"\\path\nnot-AUTH\t\001";
    return {{"move-A", a.source, key, provenance, a.geometry.binding(),
             rat(time), rat(time), lower, *a.epsilon, a.b}};
}
struct Guard {
    bool operator()(const I::Demand&, const P::OwnerMap&, const R&) const { return true; }
};
std::string stable(const P::View& view, long now) {
    return Export::snapshot_json(view, rat(now), run_id, "same-export-identity");
}
void emit(const P::View& view, long now, const std::string& id) {
    std::cout << Export::snapshot_json(view, rat(now), run_id, id) << '\n';
    if (!std::cout) throw std::runtime_error("component stdout failed");
}
const char* choice_name(pie_query::ChoiceKind kind) {
    switch (kind) {
        case pie_query::ChoiceKind::PositiveScore: return "PositiveScore";
        case pie_query::ChoiceKind::RoundRobin: return "RoundRobin";
        case pie_query::ChoiceKind::NoEligible: return "NoEligible";
        case pie_query::ChoiceKind::BlockerCount: return "BlockerCount";
    }
    throw std::invalid_argument("unknown fixture choice kind");
}

void run() {
    const S seed = initial();
    P position(seed, {{"move-A", {"seed-A", "current-A", "", ""}},
                      {"move-U", {"seed-U", "current-U", "", ""}}});
    Guard guard;
    const auto original = position.view();
    const std::string initial_bytes = stable(original, 0);
    check(original.export_history("move-A") == nullptr, "initial history unexpectedly exists");
    check(original.export_receipt("precision-profile") == nullptr, "initial receipt unexpectedly exists");
    check(original.structure().demands.at("demand-and")->relations.size() == 3,
          "nonquery owner relations were lost");
    emit(original, 0, "initial");

    auto first = position.prepare_position(certificate(original, rat(1, 5), 1, "capture-1"),
        P::PublicationIds{rat(1), "position-one", "progress-one", ""}, guard);
    check(position.view().same_identity(original), "first prepare leaked a root");
    check(stable(position.view(), 0) == initial_bytes, "first prepare leaked exported fields");
    emit(position.view(), 0, "position1_prepared");
    position.commit(std::move(first));
    const auto first_view = position.view();
    const std::string first_bytes = stable(first_view, 1);
    check(!first_view.same_identity(original), "first commit retained the old root");
    check(O::cmp(first_view.structure().actions.at("move-A")->input->q, rat(1, 5)) == 0,
          "first commit did not publish q");
    check(first_view.export_history("move-A") && first_view.export_history("move-A")->size() == 1,
          "first commit did not publish precision history");
    check(stable(original, 0) == initial_bytes, "first commit mutated the pinned initial view");
    emit(first_view, 1, "position1_committed");

    auto second = position.prepare_position(certificate(first_view, rat(2, 5), 2, "capture-2"),
        P::PublicationIds{rat(2), "position-two", "progress-two", ""}, guard);
    check(stable(position.view(), 1) == first_bytes, "second prepare leaked exported fields");
    emit(position.view(), 1, "position2_prepared");
    position.commit(std::move(second));
    const auto second_view = position.view();
    const std::string second_bytes = stable(second_view, 2);
    check(O::cmp(second_view.structure().actions.at("move-A")->input->q, rat(2, 5)) == 0,
          "second commit did not publish q");
    check(second_view.export_history("move-A") && second_view.export_history("move-A")->size() == 2,
          "second commit did not retain two distinct captures");
    check(!second_view.structure().owners.count("a-short") &&
          first_view.structure().owners.count("a-short"),
          "q/history commit failed to retire the crossed owner atomically");
    check(O::cmp(second_view.export_history("move-A")->front().lower,
                 second_view.structure().actions.at("move-A")->input->q) == 0,
          "committed q/history disagree");
    check(stable(first_view, 1) == first_bytes, "second commit mutated pinned history");
    const auto unpriced_choice = position.choose(rat(2));
    check(unpriced_choice.kind() == pie_query::ChoiceKind::RoundRobin,
          "missing actual quote did not use original fallback");
    emit(second_view, 2, "position2_committed");

    const auto& a = *second_view.structure().actions.at("move-A")->input;
    S::Receipt artificial{a.profile, a.source, "synthetic-receipt", "fixture-only-not-B1",
        a.epsilon, rat(0), rat(1), rat(2), rat(3), rat(2)};
    S::Delta price{{second_view.structure().view_id, "receipt-installed", {}, {}, {}},
                   rat(3), {}, {artificial}};
    auto receipt_pending = position.prepare_admitted_update(price, {});
    check(position.view().export_receipt(a.profile) == nullptr, "receipt prepare leaked a quote");
    check(stable(position.view(), 2) == second_bytes, "receipt prepare leaked exported fields");
    emit(position.view(), 2, "receipt_prepared");
    position.commit(std::move(receipt_pending));
    const auto rational_view = position.view();
    check(rational_view.export_receipt(a.profile) != nullptr, "receipt commit did not install quote");
    check(second_view.export_receipt(a.profile) == nullptr, "receipt commit mutated old view");
    check(stable(second_view, 2) == second_bytes, "receipt commit changed retained history");
    check(stable(original, 0) == initial_bytes, "later commits changed the initial view");
    emit(original, 0, "old_view_retained");

    const auto reference = position.choose(rat(3));
    check(reference.kind() == pie_query::ChoiceKind::PositiveScore && reference.score() &&
          reference.score()->prediction && reference.score()->cost_delay,
          "rational reference has no scored C++ candidate");
    check(reference.score()->action == "move-A", "unexpected component candidate");
    check(rational_view.structure().demands.at("demand-and")->relations.size() == 3,
          "commits dropped a nonquery relation");
    emit(rational_view, 3, "rational_ready");

    const R irrational = O::div(O::sqrt(rat(2)), rat(2));
    check(!O::is_rational(irrational), "nonrational fixture is accidentally rational");
    auto unsupported = position.prepare_position(certificate(rational_view, irrational, 4, "capture-irrational"),
        P::PublicationIds{rat(4), "nonrational-committed", "progress-irrational", ""}, guard);
    position.commit(std::move(unsupported));
    check(O::cmp(position.view().structure().actions.at("move-A")->input->q, irrational) == 0,
          "nonrational q was not committed");
    const std::string encoded = Export::snapshot_json(position.view(), rat(4), run_id,
                                                     "non_rational_committed");
    check(encoded.find("\"unsupported\":\"non_rational\"") != std::string::npos,
          "nonrational value was approximated or silently omitted");
    check(O::cmp(rational_view.structure().actions.at("move-A")->input->q, rat(2, 5)) == 0,
          "nonrational commit mutated rational reference view");
    std::cout << encoded << '\n';
    if (!std::cout) throw std::runtime_error("component stdout failed");

    const auto& score = *reference.score();
    std::cerr << "{\"component_checks\":" << checks << ",\"reference\":{"
              << "\"snapshot_id\":\"rational_ready\",\"first_action\":";
    Export::json_string(std::cerr, score.action);
    std::cerr << ",\"predicted_lower\":"; Export::exact_number(std::cerr, score.prediction->lower);
    std::cerr << ",\"denominator\":"; Export::exact_number(std::cerr, *score.cost_delay);
    std::cerr << ",\"admission\":"; Export::exact_number(std::cerr, score.admission);
    std::cerr << ",\"partial\":"; Export::exact_number(std::cerr, score.partial);
    std::cerr << ",\"owner_counts\":{";
    bool comma = false;
    for (const auto& item : rational_view.structure().demands) {
        if (comma) std::cerr << ',';
        comma = true;
        Export::json_string(std::cerr, item.first);
        std::cerr << ':' << item.second->relations.size();
    }
    std::cerr << "},\"weights\":{";
    comma = false;
    for (const auto& item : rational_view.structure().demands) {
        if (comma) std::cerr << ',';
        comma = true;
        Export::json_string(std::cerr, item.first);
        std::cerr << ':' << Export::demand_weight(rational_view, *item.second->input);
    }
    std::cerr << "}},\"unpriced\":{\"snapshot_id\":\"position2_committed\",\"choice_kind\":";
    Export::json_string(std::cerr, choice_name(unpriced_choice.kind()));
    std::cerr << "}}\n";
}
} // namespace

int main() {
    try { run(); return 0; }
    catch (const std::exception& error) {
        std::cerr << "{\"error\":";
        Export::json_string(std::cerr, error.what());
        std::cerr << ",\"component_checks\":" << checks << "}\n";
        return 1;
    }
}
