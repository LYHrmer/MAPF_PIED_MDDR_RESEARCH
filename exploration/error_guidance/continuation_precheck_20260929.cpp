// Finite preregistered two-task geometry-waiting comparison.
#define main preserved_mismatch_precheck_entry
#include "mismatch_precheck.cpp"
#undef main
#include <set>
#include <array>
#include <algorithm>
#include "continuation_world_20260929.hpp"
namespace continuation {
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


using Plan = std::array<std::vector<G>, 2>;
const char* plan_name(unsigned n) { return std::array<const char*,4>{{"UU","UL","LU","LL"}}.at(n); }
Plan make_plan(unsigned n, const R& error) {
    Plan p;
    for (unsigned task=0; task<2; ++task) {
        const bool upper = task == 0 ? n < 2 : n % 2 == 0;
        const long y = upper ? 1 : -2;
        const long x0 = task == 0 ? 0 : 4, x1 = task == 0 ? 4 : 6;
        const std::string id = "task-"+std::to_string(task+1)+(upper ? "-U-" : "-L-");
        p[task].push_back(geometry(id+"1", {rat(x0),rat(0)}, {rat(x0),rat(y)}, error));
        p[task].push_back(geometry(id+"2", {rat(x0),rat(y)}, {rat(x1),rat(y)}, error));
        p[task].push_back(geometry(id+"3", {rat(x1),rat(y)}, {rat(x1),rat(0)}, error));
    }
    return p;
}
struct Forecast {
    R motion=rat(0), wait=rat(0), arrival=rat(0), first=rat(0);
    unsigned completed=0;
};
Forecast analytic_forecast(const Plan& plan, const P::View& view, const Opportunity& opportunity,
                           const DurationPrior& duration, bool public_end_delivery) {
    const auto& state=view.structure();
    const auto& blocker=*state.actions.at("blocker")->input;
    check(state.actions.size()==1 && state.demands.empty() && same(blocker.q,rat(0)),
          "forecast must receive initial committed state");
    Forecast result;
    for (const auto& task:plan) for (const auto& edge:task)
        result.motion=O::add(result.motion,duration.duration(edge.length()));
    const R lower=O::sub(nominal_blocker_progress(blocker,opportunity.at),*blocker.epsilon);
    const R end_receipt=O::add(nominal_duration(blocker.geometry.length()),rat(1,4));
    const auto terminal=blocker.geometry.n_mask(blocker.geometry.length(),blocker.geometry.length());
    for (const auto& task:plan) {
        for (const auto& edge:task) {
            std::vector<std::string> conflict;
            const auto desired=edge.n_mask(rat(0),edge.length());
            for (const auto& cell:desired.mask()) {
                const auto it=state.owners.find(cell);
                if (it!=state.owners.end() && it->second.agent!="requester") {
                    check(it->second.action=="blocker" && it->second.geometric,
                          "unsupported foreign public owner in forecast");
                    conflict.push_back(cell);
                }
            }
            if (!conflict.empty()) {
                const auto threshold=pie_query_geometry::extract<O>(blocker.geometry,blocker.q,blocker.b,conflict);
                bool endpoint_conflict=false;
                for (const auto& cell:conflict)
                    if (std::find(terminal.mask().begin(),terminal.mask().end(),cell)!=terminal.mask().end()) endpoint_conflict=true;
                const bool position_releases=threshold.crossed_by(lower);
                const bool end_releases=public_end_delivery && !endpoint_conflict;
                std::cout << "{\"event\":\"forecast_owner_relation\",\"move\":\"" << edge.binding().move_occurrence
                          << "\",\"threshold\":\"" << rational_text(threshold.physical_exit)
                          << "\",\"position_releases\":" << (position_releases?"true":"false")
                          << ",\"native_END_releases\":" << (end_releases?"true":"false") << "}\n";
                if (!position_releases && !end_releases) return result;
                const R release=position_releases ? opportunity.at : end_receipt;
                if (O::cmp(result.arrival,release)<0) {
                    result.wait=O::add(result.wait,O::sub(release,result.arrival));
                    result.arrival=release;
                }
            }
            result.arrival=O::add(result.arrival,duration.duration(edge.length()));
        }
        ++result.completed;
        if (result.completed==1) result.first=result.arrival;
    }
    return result;
}
bool forecast_better(const Forecast& a,const Forecast& b) {
    if (a.completed!=b.completed) return a.completed>b.completed;
    return O::cmp(a.completed==2?a.arrival:a.first,b.completed==2?b.arrival:b.first)<0;
}
struct Actual {
    Result result;
    unsigned tasks;
    R first, second;
    bool end_delivered;
};
Actual execute_plan(const Plan& plan,const R& error,const R& private_eta,const Opportunity& opportunity,
                    bool end_delivery,unsigned candidate,const std::string& expected_signature) {
    std::cout << "{\"event\":\"candidate_execution_begin\",\"plan\":\"" << plan_name(candidate) << "\"}\n";
    TaskWorld world(error,plan[0].front(),opportunity,Authorization::OriginalPrefix,private_eta,end_delivery);
    check(public_signature(world.public_view())==expected_signature, "candidate initial public state differs");
    unsigned completed=0;
    R first=rat(0),second=rat(0);
    bool all=true;
    for (const auto& task:plan) {
        for (const auto& edge:task) if (!world.edge(edge)) { all=false; break; }
        if (!all) break;
        ++completed;
        const R ended=world.result(true).stopped_at;
        if (completed==1) first=ended; else second=ended;
        std::cout << "{\"event\":\"task_completed_and_next_activated\",\"task\":" << completed
                  << ",\"at\":"; interval(ended);
        std::cout << ",\"original_endpoint_and_stationary_owner_verified\":true}\n";
    }
    if (!all) world.hold_censored_until(rat(24));
    const Result actual=world.result(all);
    check(actual.observations==1 && same(actual.stopped_at,O::add(actual.moving,actual.waiting)),
          "clock decomposition or common query count mismatch");
    check(actual.edges==actual.cap_grants && actual.edges==actual.run_commands,
          "original MOVE lifecycle counts mismatch");
    if (all) check(actual.edges==6 && O::cmp(actual.stopped_at,rat(24))<0,
                   "completed pair outside fixed horizon or missing original moves");
    std::cout << "{\"event\":\"candidate_result\",\"plan\":\"" << plan_name(candidate)
              << "\",\"completed_tasks\":" << completed << ",\"task1_completed_at\":";
    if (completed>=1) interval(first); else std::cout << "null";
    std::cout << ",\"task2_completed_at\":";
    if (completed==2) interval(second); else std::cout << "null";
    std::cout << ",\"task2_flow_time_from_activation\":";
    if (completed==2) interval(O::sub(second,first)); else std::cout << "null";
    std::cout << ",\"sum_task_flow_times\":";
    if (completed==2) interval(second); else std::cout << "null";
    std::cout << ",\"sum_task_completion_times\":";
    if (completed==2) interval(O::add(first,second)); else std::cout << "null";
    std::cout << ",\"movement\":"; interval(actual.moving);
    std::cout << ",\"owner_evidence_wait\":"; interval(actual.waiting);
    std::cout << ",\"stopped_at\":"; interval(actual.stopped_at);
    std::cout << ",\"fixed_horizon\":24,\"completed_original_MOVEs\":" << actual.edges
              << ",\"position_commits\":" << actual.observations
              << ",\"native_blocker_END_delivered\":" << (world.end_delivered()?"true":"false")
              << ",\"censored\":" << (all?"false":"true") << "}\n";
    return {actual,completed,first,second,world.end_delivered()};
}
bool actual_better(const Actual& a,const Actual& b) {
    if (a.tasks!=b.tasks) return a.tasks>b.tasks;
    return O::cmp(a.tasks==2?a.second:a.first,b.tasks==2?b.second:b.first)<0;
}
void run_instance(unsigned error_case,long private_eta,unsigned opportunity_case,bool end_delivery) {
    const R error=error_case?rat(1,5):rat(0);
    const Opportunity opportunity=opportunity_case ? Opportunity{"late_4",rat(4)} : Opportunity{"early_5_over_2",rat(5,2)};
    const std::string id="z"+std::to_string(error_case)+"-eta"+std::to_string(private_eta)+"-obs"+
                         std::to_string(opportunity_case)+"-end"+std::to_string(end_delivery);
    std::cout << "{\"event\":\"instance\",\"id\":\"" << id << "\",\"data_status\":\"synthetic_native_mechanism\","
              << "\"error_half_width\":\"" << rational_text(error) << "\",\"private_eta_offline_label\":" << private_eta
              << ",\"observation_at\":\"" << rational_text(opportunity.at)
              << "\",\"native_END_delivery_enabled\":" << (end_delivery?"true":"false") << "}\n";
    const std::vector<DeliveredEnd> history={
        historical_task(id+"-history-1",rat(1),rat(0),rat(private_eta)),
        historical_task(id+"-history-2",rat(2),rat(4),rat(private_eta))};
    const DurationPrior duration=calibrate(history);
    const std::array<Plan,4> plans={{make_plan(0,error),make_plan(1,error),make_plan(2,error),make_plan(3,error)}};
    TaskWorld public_world(error,plans[0][0].front(),opportunity,Authorization::OriginalPrefix,rat(private_eta),end_delivery);
    const auto view=public_world.public_view();
    const std::string signature=public_signature(view);
    std::array<Forecast,4> forecasts;
    unsigned motion=0,strong=0;
    for (unsigned i=0;i<4;++i) {
        forecasts[i]=analytic_forecast(plans[i],view,opportunity,duration,end_delivery);
        if (O::cmp(forecasts[i].motion,forecasts[motion].motion)<0) motion=i;
        if (forecast_better(forecasts[i],forecasts[strong])) strong=i;
        std::cout << "{\"event\":\"frozen_forecast\",\"plan\":\"" << plan_name(i)
                  << "\",\"completed_tasks\":" << forecasts[i].completed << ",\"total_motion\":";
        interval(forecasts[i].motion);
        std::cout << ",\"arrival\":";
        if (forecasts[i].completed==2) interval(forecasts[i].arrival); else std::cout << "null";
        std::cout << ",\"owner_wait_until_block_or_completion\":"; interval(forecasts[i].wait);
        std::cout << "}\n";
    }
    check(public_world.public_view().same_identity(view),"forecast mutated public state");
    std::cout << "{\"event\":\"selection_before_any_evaluation\",\"motion_plan\":\"" << plan_name(motion)
              << "\",\"analytic_plan\":\"" << plan_name(strong)
              << "\",\"public_signature\":\"" << signature
              << "\",\"alpha\":"; interval(duration.alpha);
    std::cout << ",\"legal_history_rows\":2,\"decision_global_time\":10,\"private_eta_feature\":false,"
              << "\"future_END_truth_feature\":false,\"offline_counterfactual_feature\":false}\n";
    // Freeze both policies first; execute analytic selected plan before offline alternatives.
    std::vector<unsigned> order{strong};
    for (unsigned i=0;i<4;++i) if (i!=strong) order.push_back(i);
    std::vector<std::unique_ptr<Actual>> actual(4);
    for (const unsigned i:order) actual[i].reset(new Actual(execute_plan(plans[i],error,rat(private_eta),opportunity,end_delivery,i,signature)));
    unsigned best=0;
    for (unsigned i=0;i<4;++i) if (actual_better(*actual[i],*actual[best])) best=i;
    for (unsigned i=0;i<4;++i) {
        std::cout << "{\"event\":\"forecast_residual\",\"plan\":\"" << plan_name(i)
                  << "\",\"actual_minus_predicted_completed_tasks\":"
                  << static_cast<int>(actual[i]->tasks)-static_cast<int>(forecasts[i].completed)
                  << ",\"task2_arrival_actual_minus_predicted\":";
        if (actual[i]->tasks==2 && forecasts[i].completed==2) interval(O::sub(actual[i]->second,forecasts[i].arrival));
        else std::cout << "null";
        std::cout << "}\n";
    }
    std::cout << "{\"event\":\"comparison\",\"motion_plan\":\"" << plan_name(motion)
              << "\",\"analytic_plan\":\"" << plan_name(strong) << "\",\"offline_best_of_four\":\"" << plan_name(best)
              << "\",\"motion_completed_tasks\":" << actual[motion]->tasks
              << ",\"analytic_completed_tasks\":" << actual[strong]->tasks
              << ",\"analytic_completion_gap_to_best\":" << actual[best]->tasks-actual[strong]->tasks
              << ",\"analytic_task2_time_gap_to_best\":";
    if (actual[strong]->tasks==2 && actual[best]->tasks==2) interval(O::sub(actual[strong]->second,actual[best]->second));
    else std::cout << "null";
    std::cout << ",\"task2_time_gain_over_motion\":";
    if (actual[motion]->tasks==2 && actual[strong]->tasks==2) interval(O::sub(actual[motion]->second,actual[strong]->second));
    else std::cout << "null";
    std::cout << "}\n";
    std::cout << "{\"event\":\"summary\",\"status\":\"passed\",\"checks\":" << checks
              << ",\"instance_id\":\"" << id << "\",\"actual_plan_executions\":4,\"historical_single_MOVE_tasks\":2,"
              << "\"learning_advantage_claim\":false,\"full_cost_measured\":false,\"production_AUTH_verified\":false}\n";
}
} // namespace continuation
int main(int argc,char** argv) {
    try {
        check(argc==5,"expected error_case private_eta opportunity_case end_delivery");
        const int z=std::stoi(argv[1]),eta=std::stoi(argv[2]),op=std::stoi(argv[3]),end=std::stoi(argv[4]);
        check((z==0||z==1) && (eta==-1||eta==1) && (op==0||op==1) && (end==0||end==1),
              "outside preregistered finite instance table");
        continuation::run_instance(z,eta,op,end==1); return 0;
    } catch (const std::exception& e) {
        std::cerr << "continuation failed after " << checks << " checks: " << e.what() << '\n'; return 1;
    }
}
