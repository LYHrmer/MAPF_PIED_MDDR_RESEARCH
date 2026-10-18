"""Shared cooperative deadline overlay. Source transformation only, no search.

Apply after common initial adapter + loop guard, before optional recovery overlay.
Frozen older overlays/manifests remain reproducible at their recorded commits.
"""
from pathlib import Path
import re
from address_adapter import replace_exact

HERE = Path(__file__).resolve().parent


def function_span(source, signature):
    start=source.index(signature);opening=source.index('{',start);depth=1
    for i in range(opening+1,len(source)):
        depth+=(source[i]=='{')-(source[i]=='}')
        if not depth:return start,i+1
    raise ValueError('unterminated source method '+signature)


def edit_function(source,signature,edit):
    a,b=function_span(source,signature)
    return source[:a]+edit(source[a:b])+source[b:]


def loop_checkpoints(source,statement):
    """Insert only in existing braced loop bodies in fixed verified sources."""
    points=[]
    for match in re.finditer(r'\b(?:for|while)\s*\(',source):
        opening=source.index('(',match.start());depth=1;i=opening+1
        while depth:
            depth+=(source[i]=='(')-(source[i]==')');i+=1
        while i<len(source) and source[i].isspace():i+=1
        if i<len(source) and source[i]=='{':points.append(i+1)
    for i in reversed(points):source=source[:i]+'\n        '+statement+source[i:]
    return source


def adapt(files):
    driver=files['src/driver.cpp'].decode('utf-8-sig')
    if '#include "address_adapter_support.h"' not in driver or 'inc/address_budget_support.h' in files:
        raise ValueError('budget requires common initial adapter; no duplicate overlay')
    driver='#include "address_budget_support.h"\n'+driver
    driver=replace_exact(driver,'("help", "produce help message")','''("help", "produce help message")
        ("cpuLimit", po::value<double>()->required(), "absolute process CPU hard-limit contract in seconds")
        ("cpuReserve", po::value<double>()->required(), "CPU seconds reserved for rollback/final checks/output")
        ("attemptTrace", po::value<string>()->default_value(""), "optional new common primary-attempt JSONL")''')
    driver=replace_exact(driver,'    srand(config.seed);','''    srand(config.seed);
    address_budget::configure(vm["cpuLimit"].as<double>(),vm["cpuReserve"].as<double>());
    address_budget::configure_trace(vm["attemptTrace"].as<string>());''')
    driver=replace_exact(driver,'        LNS lns(instance, time_limit,','''        const auto budget_initial=address_budget::prevalidate(instance,size_t(n));
        try {
        address_budget::state().preprocessing=true;
        address_budget::checkpoint("PREPROCESSING");
        LNS lns(instance, time_limit,''')
    driver=replace_exact(driver,'        bool succ = lns.run();','''        address_budget::state().preprocessing=false;
        bool succ = lns.run();''')
    driver=replace_exact(driver,'            lns.writeIterStatsToFile(vm["stats"].as<string>());','''            lns.writeIterStatsToFile(vm["stats"].as<string>());
        } catch(const address_budget::Deadline&) {
            if(!address_budget::state().preprocessing)throw;
            address_budget::state().preprocessing=false;
            address_budget::output_initial(budget_initial,instance,vm["outputPaths"].as<string>());
        }''')
    driver=replace_exact(driver,'return address_adapter::finish();','return address_budget::finish();')

    lns=files['src/LNS.cpp'].decode()
    lns='#include "address_budget_support.h"\n'+lns
    lns=replace_exact(lns,'        agents.emplace_back(instance, i, use_sipp);','''    {
        address_budget::checkpoint("PREPROCESSING");
        agents.emplace_back(instance, i, use_sipp);
    }''')
    anchor='    while (runtime < time_limit && iteration_stats.size() <= num_of_iterations)\n    {\n'
    lns=replace_exact(lns,anchor,anchor+'        if(address_budget::expired("GROUP"))break;\n')
    lns=replace_exact(lns,'        // store the neighbor information','''        if(address_budget::expired("GROUP"))break;
        // store the neighbor information''')
    def group(src):
        src=src.replace('{\n','{\n    ++address_budget::state().group_calls;\n    if(address_budget::expired("GROUP"))return false;\n',1)
        src=loop_checkpoints(src,'if(address_budget::expired("GROUP"))return false;')
        return src
    lns=edit_function(lns,'bool LNS::generateNeighborByRandomWalk(',group)
    lns=edit_function(lns,'void LNS::randomWalk(',lambda s:loop_checkpoints(s,'if(address_budget::expired("GROUP_WALK"))return;'))
    lns=edit_function(lns,'int LNS::bernoulie()',lambda s:loop_checkpoints(s,'if(address_budget::expired("GROUP_SEED"))return -1;'))
    def repair(src):
        src=src.replace('{\n','{\n    address_budget::AttemptTrace budget_attempt(neighbor.old_sum_of_costs);\n',1)
        src=replace_exact(src,'    std::random_shuffle(shuffled_agents.begin(), shuffled_agents.end());',
            '    std::random_shuffle(shuffled_agents.begin(), shuffled_agents.end());\n    budget_attempt.order=shuffled_agents;')
        src=replace_exact(src,'    auto time = Time::now();','''    auto time = Time::now();
    address_budget::RepairScope budget_repair(T);''')
        src=replace_exact(src,'    while (p != shuffled_agents.end() && ((fsec)(Time::now() - time)).count() < T)',
            '    while (p != shuffled_agents.end() && !address_budget::expired("REPAIR"))')
        src=replace_exact(src,'        agents[id].path = agents[id].path_planner->findPath(constraint_table);','''        agents[id].path = agents[id].path_planner->findPath(constraint_table);
        budget_attempt.returned(id,int(p-shuffled_agents.begin()),agents[id].path.empty(),
            agents[id].path.empty()?-1:int(agents[id].path.size())-1);
        if(address_budget::expired("SIPP_RETURN"))break;''')
        src=replace_exact(src,'        agents[id].path = agents[id].path_planner->findPath(constraint_table);',
            '        budget_attempt.before_call();\n        agents[id].path = agents[id].path_planner->findPath(constraint_table);')
        src=replace_exact(src,'        if (neighbor.sum_of_costs >= neighbor.old_sum_of_costs)\n            break;',
            '        if (neighbor.sum_of_costs >= neighbor.old_sum_of_costs) {\n            budget_attempt.primary_stop="COST_STOP";budget_attempt.failure_site="COST_BOUND";\n            break;\n        }')
        reward='     if ((destroy_strategy == RANDOMWALK || destroy_strategy == DESTROY_COUNT) && (algo != CANONICAL))'
        src=replace_exact(src,reward,
            '    budget_attempt.primary_done(remaining_agents,int(p-shuffled_agents.begin()));\n'+reward)
        # Reject even a complete FOUND whose final return consumes the deadline.
        src=replace_exact(src,'    if (remaining_agents == 0 && neighbor.sum_of_costs <= neighbor.old_sum_of_costs',
                          '    if (!address_budget::expired("ACCEPT") && remaining_agents == 0 && neighbor.sum_of_costs <= neighbor.old_sum_of_costs')
        src=replace_exact(src,'    else // stick to old paths\n    {','''    else // stick to old paths
    {
        budget_attempt.begin_rollback();
        ++address_budget::state().rollbacks;''')
        src=replace_exact(src,'        return true;',
            '        budget_attempt.finish(true,neighbor.sum_of_costs);\n        return true;')
        src=replace_exact(src,'        return false;',
            '        budget_attempt.end_rollback();\n        budget_attempt.finish(false,neighbor.sum_of_costs);\n        return false;')
        return src
    lns=edit_function(lns,'bool LNS::runPP()',repair)

    sipp=files['src/SIPP.cpp'].decode()
    sipp='#include "address_budget_support.h"\n'+sipp
    def search(src):
        src=src.replace('{\n','{\n    address_budget::SearchScope budget_search;\n    try {\n',1)
        src=replace_exact(src,'    reset();','    reset();\n    address_budget::checkpoint("SIPP_SETUP");')
        src=loop_checkpoints(src,'address_budget::checkpoint("SIPP_EXPANSION");')
        for var in ('goal','next'):
            src=src.replace('if (dominanceCheck('+var+'))',
                'if (address_budget::owned_dominance('+var+',[&](){return dominanceCheck('+var+');}))')
        src=replace_exact(src,'    releaseNodes();\n','''    address_budget::checkpoint("SIPP_RETURN");
    address_budget::state().last_sipp_end=path.empty()?"FOCAL_DRAINED_EMPTY":"FOUND";
    releaseNodes();
''')
        # Initial safe-interval failure is not exhausted search.
        if 'address_recovery::NativeEnd::START_BLOCKED' not in src:
            src=replace_exact(src,'    if (get<0>(interval) > 0)\n        return path;','''    if (get<0>(interval) > 0) {
        address_budget::state().last_sipp_end="START_BLOCKED";
        return path;
    }''')
        else:
            src=replace_exact(src,'address_recovery::native_end()=address_recovery::NativeEnd::START_BLOCKED;',
                'address_budget::state().last_sipp_end="START_BLOCKED";\n        address_recovery::native_end()=address_recovery::NativeEnd::START_BLOCKED;')
        return src[:-1]+'''    } catch(const address_budget::Deadline&) {
        // No checkpoint during node release, rollback, complete validation or output.
        releaseNodes();
        ++address_budget::state().sipp_deadlines;
        address_budget::state().last_sipp_end="DEADLINE";
        return Path{};
    }
}'''
    sipp=edit_function(sipp,'Path SIPP::findPath(const ConstraintTable& constraint_table)',search)
    for signature in ('void SIPP::updatePath(', 'bool SIPP::dominanceCheck('):
        sipp=edit_function(sipp,signature,lambda s:loop_checkpoints(s,'address_budget::search_checkpoint("SIPP_HELPER");'))
    single=files['src/SingleAgentSolver.cpp'].decode()
    single='#include "address_budget_support.h"\n'+single
    single=edit_function(single,'void SingleAgentSolver::compute_heuristics()',
        lambda s:loop_checkpoints(s,'if(address_budget::state().preprocessing)address_budget::checkpoint("HEURISTIC");'))
    changed={'src/driver.cpp':driver.encode(),'src/LNS.cpp':lns.encode(),'src/SIPP.cpp':sipp.encode(),
        'src/SingleAgentSolver.cpp':single.encode(),
        'inc/address_budget_support.h':(HERE/'address_budget_support.h').read_bytes()}
    adapter=files['inc/address_adapter_support.h'].decode()
    adapter='#include <functional>\n'+adapter
    adapter=replace_exact(adapter,'const std::vector<int>& goals) {',
        'const std::vector<int>& goals, const std::function<void()>& cancel=std::function<void()>()) {')
    adapter=edit_function(adapter,'inline int validate(',lambda s:loop_checkpoints(s,'if(cancel)cancel();'))
    changed['inc/address_adapter_support.h']=adapter.encode()
    for name in ('src/ReservationTable.cpp','src/PathTable.cpp'):
        raw=files[name].decode()
        if name=='src/PathTable.cpp':
            raw=replace_exact(raw,'    while (rst > earliest_timestep and table[location][rst - 1] == NO_AGENT)\n        rst--;',
                '    while (rst > earliest_timestep and table[location][rst - 1] == NO_AGENT)\n    {\n        rst--;\n    }')
        changed[name]=('#include "address_budget_support.h"\n'+loop_checkpoints(raw,
            'address_budget::search_checkpoint("SIPP_RESERVATIONS");')).encode()
    return changed
