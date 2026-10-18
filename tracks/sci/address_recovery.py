"""Optional recovery AFTER the common wall/CPU/repair-budget overlay.

Source transformation only. Native calls and return positions are recorded by
address_budget; this extension adds bounded diagnostics and a private candidate.
"""
from pathlib import Path
from address_adapter import replace_exact
from address_budget import edit_function

HERE=Path(__file__).resolve().parent

HOOK=r"""
    // The author primary reward above is unchanged. Recovery has no extra reward.
    address_recovery::Context recovery_context;
    address_recovery::Result recovery_result;
    auto& recovery_trace=recovery_result.trace;
    recovery_trace.attempt_id=budget_attempt.id;
    recovery_trace.original_order=budget_attempt.order;
    recovery_trace.primary_calls=budget_attempt.calls;
    recovery_trace.failed_position=budget_attempt.failed_position;
    recovery_trace.failed_agent=budget_attempt.failed_agent;
    recovery_trace.old_group_cost=neighbor.old_sum_of_costs;
    address_recovery::Stop recovery_stop=address_recovery::from_name(budget_attempt.primary_stop);
    const auto recovery_hook_begin=address_budget::tick();
    try {
        address_budget::RecoveryScope recovery_scope;
        address_budget::checkpoint("RECOVERY_ENTRY");
        if(address_recovery::settings().policy==address_recovery::Policy::ABANDON) {
            recovery_trace.decision="ABANDON_NO_DIAGNOSIS";
        } else if(recovery_stop!=address_recovery::Stop::FOCAL_DRAINED_EMPTY) {
            recovery_trace.decision="INELIGIBLE_STOP";
        } else if(budget_attempt.failed_position<0 ||
                  2*(size_t(budget_attempt.failed_position)+1)<=shuffled_agents.size()) {
            recovery_trace.decision="NOT_LATE";
        } else {
            {
                address_recovery::Charge context_cost(recovery_trace.context_ns,recovery_trace.context_cpu_ns);
                recovery_context.order=budget_attempt.order;
                recovery_context.failed_position=size_t(budget_attempt.failed_position);
                recovery_context.old_group_cost=neighbor.old_sum_of_costs;
                recovery_context.primary_calls=budget_attempt.calls;
                recovery_context.stop=recovery_stop;
                recovery_context.incumbent.resize(agents.size());
                recovery_context.primary.resize(agents.size());
                if(neighbor.old_paths.size()!=neighbor.agents.size())throw std::runtime_error("incomplete recovery incumbent");
                for(size_t a=0;a<agents.size();++a)for(const auto& step:agents[a].path) {
                    address_budget::checkpoint("RECOVERY_CONTEXT");
                    recovery_context.incumbent[a].push_back(step.location);
                }
                for(size_t i=0;i<neighbor.agents.size();++i) {
                    int a=neighbor.agents[i];recovery_context.incumbent[a].clear();
                    for(const auto& step:neighbor.old_paths[i]) {
                        address_budget::checkpoint("RECOVERY_CONTEXT");
                        recovery_context.incumbent[a].push_back(step.location);
                    }
                }
                for(auto q=shuffled_agents.begin();q!=p;++q)for(const auto& step:agents[*q].path) {
                    address_budget::checkpoint("RECOVERY_CONTEXT");
                    recovery_context.primary[*q].push_back(step.location);
                }
                address_budget::checkpoint("RECOVERY_CONTEXT");
                recovery_trace.snapshot_complete=true;
            }
            auto validate=[&](const address_recovery::Paths& paths,bool complete) {
                address_adapter::Paths chosen;std::vector<int> starts,goals;
                const auto all_starts=instance.getStarts(),all_goals=instance.getGoals();
                for(size_t a=0;a<paths.size();++a) {
                    address_budget::checkpoint("RECOVERY_VALIDATE_PREPARE");
                    if(paths[a].empty()) {if(complete)throw std::runtime_error("incomplete recovery plan");continue;}
                    chosen.emplace_back();
                    for(int loc:paths[a]) {address_budget::checkpoint("RECOVERY_VALIDATE_PREPARE");chosen.back().push_back(loc);}
                    starts.push_back(all_starts[a]);goals.push_back(all_goals[a]);
                }
                std::vector<bool> blocked(instance.map_size);
                for(int i=0;i<instance.map_size;++i) {
                    address_budget::checkpoint("RECOVERY_VALIDATE_PREPARE");blocked[i]=instance.isObstacle(i);
                }
                if(!chosen.empty())address_adapter::validate(chosen,instance.num_of_rows,instance.num_of_cols,
                    blocked,starts,goals,[](){address_budget::checkpoint("RECOVERY_VALIDATE");});
                address_budget::checkpoint("RECOVERY_VALIDATE");
            };
            auto search=[&](int id,const address_recovery::Paths& partial) {
                address_recovery::Reply reply{address_recovery::Stop::UNKNOWN,{},false};
                try {
                    address_recovery::Charge prepare(reply.reservation_ns,reply.reservation_cpu_ns);
                    address_budget::checkpoint("RECOVERY_RESERVATIONS");
                    PathTable private_table(instance.map_size);
                    {
                        for(size_t a=0;a<partial.size();++a)if(!partial[a].empty()) {
                            address_budget::checkpoint("RECOVERY_RESERVATIONS");Path path;
                            for(int loc:partial[a]) {address_budget::checkpoint("RECOVERY_RESERVATIONS");path.emplace_back(loc);}
                            private_table.insertPath(int(a),path);
                        }
                        address_budget::checkpoint("RECOVERY_RESERVATIONS");
                    }
                    ConstraintTable constraints(instance.num_of_cols,instance.map_size,&private_table);
                    address_budget::checkpoint("RECOVERY_SEARCH");
                    prepare.finish();
                    Path path;
                    {
                        address_recovery::Charge search_cost(reply.search_ns,reply.search_cpu_ns);
                        reply.search_executed=true;path=agents[id].path_planner->findPath(constraints);
                    }
                    reply.stop=address_recovery::from_name(address_budget::expired("RECOVERY_SEARCH_RETURN")?
                        "DEADLINE":(path.empty()?address_budget::state().last_sipp_end:"FOUND"));
                    for(const auto& step:path) {
                        address_budget::checkpoint("RECOVERY_SEARCH_RETURN");reply.path.push_back(step.location);
                    }
                }catch(const address_budget::Deadline&) {reply.stop=address_recovery::Stop::DEADLINE;reply.path.clear();}
                return reply;
            };
            const auto context_ns=recovery_trace.context_ns,context_cpu_ns=recovery_trace.context_cpu_ns;
            recovery_result=address_recovery::recover(recovery_context,address_recovery::settings().policy,
                address_recovery::settings().max_calls,address_recovery::settings().rng,search,validate);
            recovery_trace.attempt_id=budget_attempt.id;recovery_trace.snapshot_complete=true;
            recovery_trace.context_ns=context_ns;recovery_trace.context_cpu_ns=context_cpu_ns;
            if(recovery_result.accepted) {
                // Build the ENTIRE replacement privately. All copies/table insertion
                // can stop before touching the live primary transaction.
                address_recovery::Charge prepare(recovery_trace.commit_prepare_ns,recovery_trace.commit_prepare_cpu_ns);
                address_budget::checkpoint("RECOVERY_COMMIT_PREPARE");
                std::vector<Path> prepared(agents.size());PathTable prepared_table(instance.map_size);
                std::vector<int> prepared_order=recovery_result.order;
                int prepared_cost=0;
                {
                    for(size_t a=0;a<agents.size();++a) {
                        for(int loc:recovery_result.paths[a]) {
                            address_budget::checkpoint("RECOVERY_COMMIT_PREPARE");prepared[a].emplace_back(loc);
                        }
                        prepared_table.insertPath(int(a),prepared[a]);
                    }
                    for(int a:neighbor.agents)prepared_cost+=int(prepared[a].size())-1;
                    if(!recovery_trace.final_check_complete||prepared_cost>=neighbor.old_sum_of_costs)
                        throw std::runtime_error("unvalidated or nonimproving recovery commit");
                }
                address_budget::checkpoint("RECOVERY_COMMIT");
                prepare.finish();
                {
                    address_recovery::Charge commit(recovery_trace.commit_ns,recovery_trace.commit_cpu_ns);
                    for(int a:neighbor.agents)agents[a].path.swap(prepared[a]);
                    path_table.table.swap(prepared_table.table);path_table.goals.swap(prepared_table.goals);
                    std::swap(path_table.makespan,prepared_table.makespan);
                    if(address_budget::expired("RECOVERY_COMMIT")) {
                        // Finite nonallocating reverse swap, then ordinary author rollback.
                        for(int a:neighbor.agents)agents[a].path.swap(prepared[a]);
                        path_table.table.swap(prepared_table.table);path_table.goals.swap(prepared_table.goals);
                        std::swap(path_table.makespan,prepared_table.makespan);
                        throw address_budget::Deadline{};
                    }
                    shuffled_agents.swap(prepared_order);p=shuffled_agents.end();remaining_agents=0;
                    neighbor.sum_of_costs=prepared_cost;
                }
            }
        }
    }catch(const address_budget::Deadline&) {
        recovery_result.accepted=false;recovery_trace.decision="DEADLINE";
        recovery_trace.deadline_phase=address_budget::state().last_stage;
    }
    const auto recovery_hook_end=address_budget::tick();
    recovery_trace.hook_wall_ns=address_budget::difference(recovery_hook_end.wall,recovery_hook_begin.wall);
    recovery_trace.hook_cpu_ns=address_budget::difference(recovery_hook_end.cpu,recovery_hook_begin.cpu);
    budget_attempt.recovery_decision=recovery_trace.decision;
"""


def adapt(files):
    driver=files['src/driver.cpp'].decode('utf-8-sig')
    lns=files['src/LNS.cpp'].decode()
    if 'address_budget::RepairScope budget_repair(T);' not in lns or '#include "address_budget_support.h"' not in driver:
        raise ValueError('recovery requires common budget overlay first')
    if 'address_recovery::Context' in lns:raise ValueError('duplicate recovery overlay')
    driver='#include "address_recovery_support.h"\n'+driver
    driver=replace_exact(driver,'("help", "produce help message")','''("help", "produce help message")
        ("recoveryPolicy", po::value<string>()->default_value("abandon"), "abandon/random/anchor; optional bounded recovery")
        ("recoveryCalls", po::value<int>()->default_value(8), "at most 8 extra requests, once per failed attempt")
        ("recoveryTrace", po::value<string>()->required(), "new per-attempt recovery-detail JSONL")''')
    driver=replace_exact(driver,'    address_budget::configure_trace(vm["attemptTrace"].as<string>());','''    address_budget::configure_trace(vm["attemptTrace"].as<string>());
    if(vm["attemptTrace"].as<string>().empty())throw std::runtime_error("recovery requires common attemptTrace");
    address_recovery::configure(vm["recoveryPolicy"].as<string>(),vm["recoveryCalls"].as<int>(),
        config.seed,vm["recoveryTrace"].as<string>());''')
    def recovery(src):
        accept='    if (!address_budget::expired("ACCEPT") && remaining_agents == 0 && neighbor.sum_of_costs <= neighbor.old_sum_of_costs) // accept new paths'
        src=replace_exact(src,accept,HOOK+accept)
        for accepted in ('true','false'):
            marker='        budget_attempt.finish('+accepted+',neighbor.sum_of_costs);'
            src=replace_exact(src,marker,
                '        recovery_trace.final_group_cost=neighbor.sum_of_costs;\n'
                '        if(!'+accepted+' && recovery_result.accepted)recovery_trace.decision="COMMIT_REJECTED";\n'
                '        budget_attempt.recovery_decision=recovery_trace.decision;\n'
                '        budget_attempt.blockers_checked=recovery_trace.blockers_checked;\n'
                '        budget_attempt.recoverability_established='+accepted+' && recovery_result.accepted;\n'+marker+'\n'
                '        recovery_trace.attempt_wall_before_trace_ns=address_budget::difference(address_budget::tick().wall,budget_attempt.begin.wall);\n'
                '        address_recovery::emit(recovery_trace,recovery_stop,'+accepted+',recovery_context);')
        return src
    lns='#include "address_recovery_support.h"\n'+edit_function(lns,'bool LNS::runPP()',recovery)
    return {'src/driver.cpp':driver.encode(),'src/LNS.cpp':lns.encode(),
            'inc/address_recovery_support.h':(HERE/'address_recovery_support.h').read_bytes()}
