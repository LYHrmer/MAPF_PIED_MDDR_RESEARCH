"""Explicit optional reward adaptation after the shared budget overlay.

The frozen author/budget variants are untouched. Source transformation only.
"""
from pathlib import Path
from address_adapter import replace_exact
from address_budget import edit_function

HERE = Path(__file__).resolve().parent


def adapt(files):
    if 'inc/address_budget_support.h' not in files or 'inc/address_reward_support.h' in files:
        raise ValueError('reward requires budget overlay exactly once')
    driver = '#include "address_reward_support.h"\n' + files['src/driver.cpp'].decode()
    driver = replace_exact(driver, '("help", "produce help message")', '''("help", "produce help message")
        ("rewardMemory", po::value<string>()->required(), "author audit or committed Bernoulli cumulative/window")
        ("rewardWindow", po::value<int>()->required(), "positive for window; zero for author/cumulative")
        ("candidateValidation", po::value<string>()->default_value("all"), "all or acceptance_eligible (author mode only)")
        ("repairBudgetContract", po::value<string>()->default_value("legacy"), "legacy transaction cap or search_then_admission")
        ("executionObservations", po::value<int>()->default_value(0), "explicit matched budget/posterior/order/plan observations (0 or 1)")
        ("rewardTrace", po::value<string>()->required(), "new per-selection reward JSONL")''')
    driver = replace_exact(driver, '    address_budget::configure_trace(vm["attemptTrace"].as<string>());', '''    address_budget::configure_trace(vm["attemptTrace"].as<string>());
    address_reward::configure(vm["rewardMemory"].as<string>(),vm["rewardWindow"].as<int>(),
        vm["agentNum"].as<int>(),vm["rewardTrace"].as<string>(),vm["candidateValidation"].as<string>(),
        vm["repairBudgetContract"].as<string>(),vm["executionObservations"].as<int>());''')
    driver = replace_exact(driver, '        const auto budget_initial=address_budget::prevalidate(instance,size_t(n));',
        '        const auto budget_initial=address_budget::prevalidate(instance,size_t(n));\n        address_reward::initialize_plan_identity(budget_initial);')
    lns = '#include "address_reward_support.h"\n' + files['src/LNS.cpp'].decode()

    def run(src):
        src = replace_exact(src, '        switch (destroy_strategy)',
            '        address_reward::SelectionScope reward_selection(sum_of_costs);\n        switch (destroy_strategy)')
        src = replace_exact(src, '        if(!succ) {', '''        if(!succ) {
            address_reward::no_repair("GROUP_NOT_FORMED",alpha,beta);''')
        src = replace_exact(src, '        if(address_budget::expired("GROUP"))break;\n        address_budget::PhaseScope budget_neighbor_prepare', '''        if(address_budget::expired("GROUP")) {
            address_reward::no_repair("GROUP_ADMISSION_DEADLINE",alpha,beta);break;
        }
        address_budget::PhaseScope budget_neighbor_prepare''')
        return src
    lns = edit_function(lns, 'bool LNS::run()', run)
    lns = edit_function(lns, 'int LNS::bernoulie()', lambda src: replace_exact(src,
        '    return best_agent;', '    address_reward::bind_seed(best_agent);\n    return best_agent;'))
    lns = edit_function(lns, 'int LNS::bernoulie()', lambda src: replace_exact(src,
        '    if(address_budget::positive_seed_admission()) {',
        '    address_reward::seed_pool_completed(int(topAgents.size()));\n    if(address_budget::positive_seed_admission()) {'))

    def repair(src):
        src = replace_exact(src, '    budget_attempt.primary_done(remaining_agents,int(p-shuffled_agents.begin()));',
            '''    const auto reward_raw_search_stop=budget_attempt.primary_stop;
    if(!address_reward::common_budget())address_reward::search_returned(reward_raw_search_stop,remaining_agents);
    budget_attempt.primary_done(remaining_agents,int(p-shuffled_agents.begin()));
    if(address_reward::common_budget())address_reward::search_returned(reward_raw_search_stop,remaining_agents);
    address_reward::enter_admission();''')
        src = replace_exact(src, '    auto shuffled_agents = neighbor.agents;', '''    address_reward::group(int(neighbor.agents.size()),neighbor.old_sum_of_costs);
    address_reward::observe_group(neighbor.agents);
    auto shuffled_agents = neighbor.agents;''')
        src = replace_exact(src, '    budget_attempt.order=shuffled_agents;',
            '    budget_attempt.order=shuffled_agents;\n    address_reward::observe_order(shuffled_agents);')
        src = replace_exact(src, '        budget_attempt.returned(id,', '''        if(!agents[id].path.empty())address_reward::found(int(agents[id].path.size())-1);
        budget_attempt.returned(id,''')
        marker = '     if ((destroy_strategy == RANDOMWALK || destroy_strategy == DESTROY_COUNT) && (algo != CANONICAL))'
        end = '    if (!address_budget::expired("ACCEPT") && remaining_agents == 0'
        a, b = src.index(marker), src.index(end)
        original_reward = src[a:b]
        src = src[:a] + '''    address_reward::inspect_candidate(agents,instance,remaining_agents);
    address_reward::author_before(current_index,neighbor.old_sum_of_costs,neighbor.sum_of_costs,alpha,beta,
        address_reward::author() && current_index!=-1 && algo!=CANONICAL &&
        (destroy_strategy==RANDOMWALK||destroy_strategy==DESTROY_COUNT) &&
        (algo==BERNOULIE||destroy_strategy==DESTROY_COUNT));
    if(address_reward::author()) {
''' + original_reward + '    }\n    address_reward::author_after(alpha,beta);\n' + src[b:]
        src = replace_exact(src, end,
            '    if (address_reward::admissible() && !address_budget::expired("ACCEPT") && remaining_agents == 0')
        src = replace_exact(src, '        budget_attempt.finish(true,neighbor.sum_of_costs);', '''        budget_attempt.finish(true,neighbor.sum_of_costs);
        address_reward::settle(true,neighbor.sum_of_costs,budget_attempt.primary_stop,alpha,beta);''')
        src = replace_exact(src, '        budget_attempt.finish(false,neighbor.sum_of_costs);', '''        budget_attempt.finish(false,neighbor.sum_of_costs);
        address_reward::settle(false,neighbor.sum_of_costs,budget_attempt.primary_stop,alpha,beta);''')
        return src
    lns = edit_function(lns, 'bool LNS::runPP()', repair)
    # Forward-declare summary to allow either header include order. Include
    # the definition after the complete budget namespace.
    budget = files['inc/address_budget_support.h'].decode()
    budget = replace_exact(budget, 'inline int finish() {', '''} // namespace address_budget
namespace address_reward { inline void summary(std::ostream&); }
namespace address_budget {
inline int finish() {''')
    budget = replace_exact(budget, '    write_profile(receipt);write_seed_admission(receipt);receipt<<"}\\n";',
        '    address_reward::summary(receipt);\n    write_profile(receipt);write_seed_admission(receipt);receipt<<"}\\n";')
    budget = replace_exact(budget, 'AUTHOR_ATTEMPT_UPDATE_BEFORE_ROLLBACK',
        'SEE_REWARD_CONTRACT_AUTHOR_OR_COMMITTED')
    budget += '\n#include "address_reward_support.h"\n'
    return {'src/driver.cpp': driver.encode(), 'src/LNS.cpp': lns.encode(),
            'inc/address_budget_support.h': budget.encode(),
            'inc/address_reward_support.h': (HERE/'address_reward_support.h').read_bytes()}
