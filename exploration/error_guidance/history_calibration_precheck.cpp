// New historical-calibration successor; mismatch sources/receipts stay unchanged.
// Reuse only this branch's self-written native mechanism implementation.
#define main preserved_mismatch_precheck_entry
#include "mismatch_precheck.cpp"
#undef main
#include <set>

namespace historical_calibration {
struct DeliveredEnd {
    std::string run_id, move_id;
    R length, started_global, ended_global, received_global;
};
struct DurationPrior {
    R alpha;
    R duration(const R& length) const { return O::sqrt(O::mul(alpha, length)); }
};
R evaluation_origin() { return rat(10); }

DeliveredEnd historical_task(const std::string& run_id, const R& length,
                             const R& global_origin, const R& private_eta) {
    // Independent completed one-MOVE history episode. Native World checks real
    // geometry, ordinary grant, cap installation/RUN, original closed END and
    // endpoint ownership. It is not a production AUTH/service certificate.
    const std::string move = run_id + "-move";
    const G g = geometry(move, {rat(0), rat(0)}, {length, rat(0)}, rat(1, 5));
    const Opportunity unused_query{"historical_no_query_before_completion", rat(4)};
    World world(rat(1, 5), g, unused_query, Authorization::OriginalPrefix, private_eta);
    check(world.edge(g), "historical original MOVE did not complete");
    const Result done = world.result(true);
    check(done.edges == 1 && done.cap_grants == 1 && done.run_commands == 1 &&
          done.observations == 0 && same(done.waiting, rat(0)),
          "historical label was not an uninterrupted original MOVE completion");
    const R end = O::add(global_origin, done.stopped_at);
    const R received = O::add(end, rat(1, 4));
    check(O::cmp(received, evaluation_origin()) < 0, "historical END not delivered before evaluation");
    const auto endpoint = g.n_mask(g.length(), g.length());
    for (const auto& cell : endpoint.mask()) {
        const auto& owner = world.public_view().structure().owners.at(cell);
        check(owner.agent == "requester" && owner.action.empty() && !owner.geometric,
              "historical END delivery lacks retained endpoint residence");
    }
    // Native delivery is a declared 1/4-time receipt event after verified END.
    // The receiver exports only this immutable payload; no private eta/World.
    DeliveredEnd row{run_id, move, length, global_origin, end, received};
    std::cout << "{\"event\":\"historical_native_END_delivered\",\"run_id\":\"" << run_id
              << "\",\"move_id\":\"" << move << "\",\"length\":\"" << rational_text(length)
              << "\",\"started_global\":"; interval(row.started_global);
    std::cout << ",\"ended_global\":"; interval(row.ended_global);
    std::cout << ",\"received_global\":"; interval(row.received_global);
    std::cout << ",\"evaluation_origin_global\":\"10\",\"endpoint_resident_retained\":true,"
              << "\"completed_single_move_history_task\":true,\"profile\":\"requester_native_profile\"}\n";
    return row;
}
DurationPrior calibrate(const std::vector<DeliveredEnd>& rows) {
    check(rows.size() == 2, "finite history calibration needs exactly two delivered tasks");
    std::set<std::string> ids;
    R numerator = rat(0), denominator = rat(0);
    for (const auto& row : rows) {
        check(ids.insert(row.run_id).second && O::cmp(row.length, rat(0)) > 0 &&
              O::cmp(row.ended_global, row.started_global) > 0 &&
              O::cmp(row.received_global, row.ended_global) > 0 &&
              O::cmp(row.received_global, evaluation_origin()) < 0,
              "invalid, duplicate or future historical END label");
        const R duration = O::sub(row.ended_global, row.started_global);
        numerator = O::add(numerator, O::mul(row.length, O::mul(duration, duration)));
        denominator = O::add(denominator, O::mul(row.length, row.length));
    }
    // Closed-form one-parameter least squares, zero intercept: D^2 = alpha L.
    // This uses only previously received END durations and public MOVE lengths.
    const DurationPrior model{O::div(numerator, denominator)};
    check(O::cmp(model.alpha, rat(0)) > 0, "nonpositive historical duration model");
    const auto& last = rows.back();
    const R last_duration = O::sub(last.ended_global, last.started_global);
    const R last_alpha = O::div(O::mul(last_duration, last_duration), last.length);
    // Same stationary artificial condition makes this equal to last-END
    // analytic scaling. No independent learned-over-analytic advantage is claimed.
    check(same(model.alpha, last_alpha), "two historical scale estimates disagree");
    std::cout << "{\"event\":\"historical_calibration\",\"received_rows\":2,\"alpha\":";
    interval(model.alpha);
    std::cout << ",\"last_END_alpha\":"; interval(last_alpha);
    std::cout << ",\"same_as_last_END_scaling\":true,\"private_eta_input\":false}\n";
    return model;
}

Prediction calibrated_predict(const std::vector<G>& route, const P::View& public_view,
                   const Opportunity& opportunity, const DurationPrior& model) {
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
        const R duration = model.duration(g.length());
        movement = O::add(movement, duration);
        arrival = O::add(arrival, duration);
    }
    return {movement, waiting, arrival, forecast, available};
}

Decision calibrated_choose(const std::vector<G>& upper, const std::vector<G>& lower,
                           const P::View& view, const Opportunity& opportunity,
                           const DurationPrior& model) {
    const Prediction pu = calibrated_predict(upper, view, opportunity, model);
    const Prediction pl = calibrated_predict(lower, view, opportunity, model);
    check(pu.available && pl.available, "fixed calibrated case has unavailable certificate prior");
    return {pu, pl, O::cmp(pu.arrival, pl.arrival) <= 0, O::cmp(pu.motion, pl.motion) <= 0};
}
void evaluation(const Condition& condition, const Opportunity& opportunity,
                const std::vector<DeliveredEnd>& history, const DurationPrior& model) {
    const auto upper = route(true), lower = route(false);
    const std::string run_id = std::string("calibrated-evaluation-") + condition.name + '-' + opportunity.name;
    for (const auto& row : history) check(row.run_id != run_id, "evaluation episode in its own history");
    World selected_world(rat(1, 5), upper.front(), opportunity,
                         Authorization::OriginalPrefix, condition.actual_requester_eta);
    const auto view = selected_world.public_view();
    const std::string signature = public_signature(view);
    const Decision frozen = choose(upper, lower, view, opportunity);
    const Decision calibrated = calibrated_choose(upper, lower, view, opportunity, model);
    check(selected_world.public_view().same_identity(view), "calibration mutated committed geometry/knowledge");
    check(same(frozen.upper.certificate_lower, calibrated.upper.certificate_lower) &&
          same(frozen.lower.certificate_lower, calibrated.lower.certificate_lower),
          "requester history changed the blocker certificate prior");

    // Both decisions are recorded before either evaluation trajectory. Condition
    // is an offline label only; selectors receive public state and history alpha.
    std::cout << "{\"event\":\"historical_selection_before_execution\",\"run_id\":\"" << run_id
              << "\",\"condition\":\"" << condition.name << "\",\"opportunity\":\""
              << opportunity.name << "\",\"decision_local_time\":\"0\",\"decision_global_time\":\"10\","
              << "\"legal_delivered_history_rows\":2,\"frozen_selected\":\""
              << (frozen.waiting_upper ? "upper" : "lower") << "\",\"calibrated_selected\":\""
              << (calibrated.waiting_upper ? "upper" : "lower") << "\",\"alpha\":";
    interval(model.alpha);
    std::cout << ",\"frozen_upper_prediction\":"; prediction_json(frozen.upper);
    std::cout << ",\"frozen_lower_prediction\":"; prediction_json(frozen.lower);
    std::cout << ",\"calibrated_upper_prediction\":"; prediction_json(calibrated.upper);
    std::cout << ",\"calibrated_lower_prediction\":"; prediction_json(calibrated.lower);
    std::cout << "}\n";

    const bool selected_upper = calibrated.waiting_upper;
    const Result selected = execute(selected_world, selected_upper ? upper : lower, selected_upper,
                                    condition, opportunity, "selected_by_delivered_END_calibration");
    World other_world(rat(1, 5), upper.front(), opportunity,
                      Authorization::OriginalPrefix, condition.actual_requester_eta);
    check(public_signature(other_world.public_view()) == signature, "paired initial public state changed");
    const Result other = execute(other_world, selected_upper ? lower : upper, !selected_upper,
                                 condition, opportunity, "offline_other_route");
    const Result actual_upper = selected_upper ? selected : other;
    const Result actual_lower = selected_upper ? other : selected;
    if (actual_upper.completed && actual_lower.completed) {
        const Result old_selected = frozen.waiting_upper ? actual_upper : actual_lower;
        const R best = O::cmp(actual_upper.stopped_at, actual_lower.stopped_at) <= 0 ?
                       actual_upper.stopped_at : actual_lower.stopped_at;
        std::cout << "{\"event\":\"historical_calibration_comparison\",\"condition\":\""
                  << condition.name << "\",\"opportunity\":\"" << opportunity.name
                  << "\",\"frozen_selected\":\"" << (frozen.waiting_upper ? "upper" : "lower")
                  << "\",\"calibrated_selected\":\"" << (selected_upper ? "upper" : "lower")
                  << "\",\"frozen_actual_arrival\":"; interval(old_selected.stopped_at);
        std::cout << ",\"calibrated_actual_arrival\":"; interval(selected.stopped_at);
        std::cout << ",\"calibrated_arrival_improvement\":";
        interval(O::sub(old_selected.stopped_at, selected.stopped_at));
        std::cout << ",\"frozen_selection_loss\":"; interval(O::sub(old_selected.stopped_at, best));
        std::cout << ",\"calibrated_selection_loss\":"; interval(O::sub(selected.stopped_at, best));
        std::cout << ",\"frozen_upper_actual_minus_prior\":";
        interval(O::sub(actual_upper.stopped_at, frozen.upper.arrival));
        std::cout << ",\"calibrated_upper_actual_minus_prior\":";
        interval(O::sub(actual_upper.stopped_at, calibrated.upper.arrival));
        std::cout << ",\"frozen_lower_actual_minus_prior\":";
        interval(O::sub(actual_lower.stopped_at, frozen.lower.arrival));
        std::cout << ",\"calibrated_lower_actual_minus_prior\":";
        interval(O::sub(actual_lower.stopped_at, calibrated.lower.arrival));
        std::cout << ",\"candidate_reference_count\":2,\"evaluation_original_MOVEs\":6,"
                  << "\"evaluation_observations\":2}\n";
    } else {
        std::cout << "{\"event\":\"historical_calibration_comparison_censored\",\"run_id\":\""
                  << run_id << "\",\"loss\":null}\n";
    }
    // No assertion requires improvement, a predetermined selected path, or a
    // zero prediction error. Negative improvements remain reportable outcomes.
}
void run() {
    for (const long eta : {-1L, 1L}) {
        const Condition condition{eta == -1 ? "matched_eta_minus_one" : "mismatch_eta_plus_one", rat(eta)};
        // The latent physical condition persists across these independent prior
        // runs and subsequent evaluations. This stationarity is a stated premise,
        // not inferred from the current evaluation's private dynamics.
        const std::vector<DeliveredEnd> rows = {
            historical_task(std::string(condition.name) + "-history-task-1", rat(1), rat(0), condition.actual_requester_eta),
            historical_task(std::string(condition.name) + "-history-task-2", rat(2), rat(4), condition.actual_requester_eta)
        };
        const DurationPrior model = calibrate(rows);
        evaluation(condition, {"crossed_5_over_2", rat(5, 2)}, rows, model);
        evaluation(condition, {"late_4", rat(4)}, rows, model);
    }
    std::cout << "{\"event\":\"summary\",\"status\":\"passed\",\"checks\":" << checks
              << ",\"named_opportunities\":2,\"named_private_conditions\":2,"
              << "\"actual_route_executions\":8,\"historical_single_MOVE_tasks\":4,"
              << "\"calibration\":\"one_scale_from_two_delivered_ENDs_equals_last_END\","
              << "\"scope\":\"native_historical_calibration_not_learning_advantage_or_full_cost\"}\n";
}
} // namespace historical_calibration
int main() {
    try { historical_calibration::run(); return 0; }
    catch (const std::exception& e) {
        std::cerr << "history calibration precheck failed after " << checks << " checks: " << e.what() << '\n';
        return 1;
    }
}
