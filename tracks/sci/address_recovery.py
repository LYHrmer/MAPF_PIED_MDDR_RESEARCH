"""Optional native overlay AFTER frozen address_adapter.adapt (and loop guard).

Never modifies the frozen adapter, runner, author tree, or authorized manifest.
This module transforms source only; it cannot invoke an Instance or search.

All three modes share recovery diagnostics for a mechanism comparison. Their
abandon mode is NOT the strong end-to-end ADDRESS cost baseline: compare also
the separate loop_guard-only binary, whose runPP has no forced diagnostics.
Recovery SIPP calls consume the author's global rand stream; equal initial
seeds do not imply equal later neighborhood proposals across policies.
"""
from pathlib import Path
from address_adapter import replace_exact

HERE = Path(__file__).resolve().parent

HOOK = r'''
    // The primary attempt's author reward block ABOVE is kept byte-for-byte.
    // Recovery gets no additional seed-bandit update. No recursion is possible.
    address_recovery::Context recovery_context;
    recovery_context.order = shuffled_agents;
    recovery_context.failed_position = size_t(p-shuffled_agents.begin());
    recovery_context.old_group_cost = neighbor.old_sum_of_costs;
    recovery_context.primary_calls = recovery_primary_calls;
    recovery_context.stop = recovery_stop;
    recovery_context.deadline_ns = recovery_deadline_ns;
    recovery_context.incumbent.resize(agents.size());
    recovery_context.primary.resize(agents.size());
    if (neighbor.old_paths.size()!=neighbor.agents.size())
        throw std::runtime_error("recovery requires a complete incumbent group snapshot");
    for (size_t a=0;a<agents.size();++a)
        for (const auto& step:agents[a].path) recovery_context.incumbent[a].push_back(step.location);
    for (size_t i=0;i<neighbor.agents.size();++i) {
        const int a=neighbor.agents[i];recovery_context.incumbent[a].clear();
        for (const auto& step:neighbor.old_paths[i]) recovery_context.incumbent[a].push_back(step.location);
    }
    for (auto q=shuffled_agents.begin();q!=p;++q)
        for (const auto& step:agents[*q].path) recovery_context.primary[*q].push_back(step.location);
    auto recovery_validate = [&](const address_recovery::Paths& paths,bool complete) {
        address_adapter::Paths chosen;
        std::vector<int> starts,goals;
        auto all_starts=instance.getStarts();auto all_goals=instance.getGoals();
        for (size_t a=0;a<paths.size();++a) {
            if (paths[a].empty()) {
                if (complete) throw std::runtime_error("incomplete recovery joint plan");
                continue;
            }
            chosen.push_back(paths[a]);starts.push_back(all_starts[a]);goals.push_back(all_goals[a]);
        }
        if (chosen.empty()) return;
        std::vector<bool> blocked(instance.map_size);
        for (int i=0;i<instance.map_size;++i) blocked[i]=instance.isObstacle(i);
        address_adapter::validate(chosen,instance.num_of_rows,instance.num_of_cols,blocked,starts,goals);
    };
    auto recovery_search = [&](int id,const address_recovery::Paths& partial) {
        // Rebuild a private reservation table; primary agents/path_table remain
        // unchanged until complete recovery validation succeeds. This cost counts.
        PathTable temporary_table(instance.map_size);
        for (size_t a=0;a<partial.size();++a) if (!partial[a].empty()) {
            Path path;for (int loc:partial[a]) path.emplace_back(loc);
            temporary_table.insertPath(int(a),path);
        }
        ConstraintTable temporary_constraints(instance.num_of_cols,instance.map_size,&temporary_table);
        if (address_recovery::now_ns()>=recovery_deadline_ns)
            return address_recovery::Reply{address_recovery::Stop::DEADLINE,{},false};
        const auto path=agents[id].path_planner->findPath(temporary_constraints);
        const auto stop=address_recovery::classify(path.empty(),
            address_recovery::now_ns()>=recovery_deadline_ns,address_recovery::native_end());
        std::vector<int> result;for (const auto& step:path) result.push_back(step.location);
        return address_recovery::Reply{stop,result};
    };
    auto recovery_result=address_recovery::recover(recovery_context,
        address_recovery::settings().policy,address_recovery::settings().max_calls,
        address_recovery::settings().rng,recovery_search,recovery_validate);
    if (remaining_agents==0 && address_recovery::now_ns()<recovery_deadline_ns) {
        // All modes also check a primary complete candidate, under the same
        // deadline; a final FOUND returned after T may NOT be accepted.
        address_recovery::Paths complete(agents.size());
        for (size_t a=0;a<agents.size();++a)
            for (const auto& step:agents[a].path) complete[a].push_back(step.location);
        const auto check_begin=address_recovery::now_ns();
        recovery_validate(complete,true);++recovery_result.trace.full_checks;
        recovery_result.trace.validation_ns+=address_recovery::now_ns()-check_begin;
    }
    if (recovery_result.accepted && address_recovery::now_ns()<recovery_deadline_ns) {
        for (auto q=shuffled_agents.begin();q!=p;++q)
            path_table.deletePath(*q,agents[*q].path);
        neighbor.sum_of_costs=0;
        for (int a:neighbor.agents) {
            agents[a].path.clear();
            for (int loc:recovery_result.paths[a]) agents[a].path.emplace_back(loc);
            path_table.insertPath(a,agents[a].path);
            neighbor.sum_of_costs+=int(agents[a].path.size())-1;
        }
        shuffled_agents=recovery_result.order;
        p=shuffled_agents.end();remaining_agents=0;
    }
'''


def adapt(files):
    """Input must contain the merged common-initial adapter; return changed files.

    A loop-guard overlay may precede this one. No fallback cap is inferred from
    historical EMPTY_CAPPED jobs: the author call uses length_max=MAX_TIMESTEP.
    """
    driver = files['src/driver.cpp'].decode('utf-8-sig')
    if '#include "address_adapter_support.h"' not in driver:
        raise ValueError('apply common-initial address_adapter first')
    driver = '#include "address_recovery_support.h"\n'+driver
    driver = replace_exact(driver, '("help", "produce help message")', '''("help", "produce help message")
        ("recoveryPolicy", po::value<string>()->default_value("abandon"), "abandon/random/anchor; optional bounded recovery")
        ("recoveryCalls", po::value<int>()->default_value(8), "at most 8 extra requests, once per failed attempt")
        ("recoveryTrace", po::value<string>()->required(), "new per-attempt diagnostic JSONL")''')
    driver = replace_exact(driver, '    srand(config.seed);', '''    srand(config.seed);
    address_recovery::configure(vm["recoveryPolicy"].as<string>(),vm["recoveryCalls"].as<int>(),
        config.seed,vm["recoveryTrace"].as<string>());''')
    sipp = files['src/SIPP.cpp'].decode()
    begin=sipp.index('Path SIPP::findPath(const ConstraintTable& constraint_table)')
    end=sipp.index('Path SIPP::findOptimalPath(',begin)
    find=sipp[begin:end]
    find=replace_exact(find,'    reset();','    address_recovery::native_end()=address_recovery::NativeEnd::UNKNOWN;\n    reset();')
    find=replace_exact(find,'    if (get<0>(interval) > 0)\n        return path;', '''    if (get<0>(interval) > 0) {
        address_recovery::native_end()=address_recovery::NativeEnd::START_BLOCKED;
        return path;
    }''')
    find=replace_exact(find,'    releaseNodes();\n    return path;', '''    releaseNodes();
    // A return-site diagnostic, not an independent completeness guarantee.
    address_recovery::native_end()=path.empty() ? address_recovery::NativeEnd::FOCAL_DRAINED_EMPTY
                                              : address_recovery::NativeEnd::FOUND;
    return path;''')
    sipp='#include "address_recovery_support.h"\n'+sipp[:begin]+find+sipp[end:]
    lns=files['src/LNS.cpp'].decode()
    begin=lns.index('bool LNS::runPP()')
    end=lns.index('bool LNS::runPPS()',begin)
    run=lns[begin:end]
    run=replace_exact(run,'    auto shuffled_agents = neighbor.agents;',
        '    const auto recovery_attempt_begin_ns=address_recovery::now_ns();\n    auto shuffled_agents = neighbor.agents;')
    run=replace_exact(run,'    auto time = Time::now();', '''    auto time = Time::now();
    const auto recovery_now_ns=address_recovery::now_ns();
    const double repair_remaining=T-((fsec)(Time::now()-time)).count();
    const auto recovery_deadline_ns=recovery_now_ns+static_cast<long long>(
        std::max(0.0,std::min(repair_remaining,address_adapter::remaining()))*1e9);
    auto recovery_stop=address_recovery::Stop::UNKNOWN;
    int recovery_primary_calls=0;''')
    run=replace_exact(run,'        agents[id].path = agents[id].path_planner->findPath(constraint_table);\n        if (agents[id].path.empty()) break;', '''        ++recovery_primary_calls;
        agents[id].path = agents[id].path_planner->findPath(constraint_table);
        recovery_stop=address_recovery::classify(agents[id].path.empty(),
            address_recovery::now_ns()>=recovery_deadline_ns,address_recovery::native_end());
        if (agents[id].path.empty()) break;''')
    run=replace_exact(run,'''        if (neighbor.sum_of_costs >= neighbor.old_sum_of_costs)
            break;''','''        if (neighbor.sum_of_costs >= neighbor.old_sum_of_costs) {
            if (recovery_stop!=address_recovery::Stop::DEADLINE)
                recovery_stop=address_recovery::Stop::COST_STOP;
            break;
        }''')
    reward_start='     if ((destroy_strategy == RANDOMWALK || destroy_strategy == DESTROY_COUNT) && (algo != CANONICAL)){'
    run=replace_exact(run,reward_start,'''    if (address_recovery::now_ns()>=recovery_deadline_ns)
        recovery_stop=address_recovery::Stop::DEADLINE;
'''+reward_start)
    accept='    if (remaining_agents == 0 && neighbor.sum_of_costs <= neighbor.old_sum_of_costs) // accept new paths'
    run=replace_exact(run,accept,HOOK+'''    if (remaining_agents == 0 && neighbor.sum_of_costs <= neighbor.old_sum_of_costs
        && address_recovery::now_ns()<recovery_deadline_ns) // complete, validated, on-time acceptance''')
    run=replace_exact(run,'        return true;', '''        recovery_result.trace.decision=recovery_result.accepted ? "RECOVERY_ACCEPTED" : "PRIMARY_ACCEPTED";
        address_recovery::emit(recovery_result.trace,recovery_stop,true);
        return true;''')
    run=replace_exact(run,'        return false;', '''        if (address_recovery::now_ns()>=recovery_deadline_ns)
            recovery_result.trace.decision="DEADLINE_REJECTED";
        address_recovery::emit(recovery_result.trace,recovery_stop,false);
        return false;''')
    run=run.replace('        address_recovery::emit(',
        '        recovery_result.trace.final_group_cost=neighbor.sum_of_costs;\n        recovery_result.trace.attempt_wall_before_trace_ns=address_recovery::now_ns()-recovery_attempt_begin_ns;\n        address_recovery::emit(')
    # Preserve the exact author reward block, including its pre-rollback update.
    original=files['src/LNS.cpp'].decode()[begin:end]
    reward=original[original.index(reward_start):original.index(accept)]
    if reward not in run:
        raise ValueError('author reward block changed')
    lns='#include "address_recovery_support.h"\n'+lns[:begin]+run+lns[end:]
    return {'src/driver.cpp':driver.encode(),'src/LNS.cpp':lns.encode(),'src/SIPP.cpp':sipp.encode(),
            'inc/address_recovery_support.h':(HERE/'address_recovery_support.h').read_bytes()}
