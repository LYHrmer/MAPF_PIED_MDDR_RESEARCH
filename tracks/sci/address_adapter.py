"""Exact, fail-closed build overlay for the pinned author-recommended ADDRESS.

No solver is invoked by this module. The pristine author checkout is immutable.
"""
import hashlib
from pathlib import Path

HERE = Path(__file__).resolve().parent


def replace_exact(text, old, new, count=1):
    if text.count(old) != count:
        raise ValueError('author adapter anchor changed: '+repr(old[:70]))
    return text.replace(old, new)


def adapt(files):
    """Return changed source bytes only; author reward/search bodies are retained."""
    driver = files['src/driver.cpp'].decode('utf-8-sig')
    driver = '#include "address_adapter_support.h"\n'+driver
    driver = replace_exact(driver, 'int main(int argc, char** argv)\n{',
        'int main(int argc, char** argv)\n{\n    address_adapter::state().entry = address_adapter::Clock::now();')
    driver = replace_exact(driver, '("help", "produce help message")', '''("help", "produce help message")
        ("initialPaths", po::value<string>()->required(), "adapter common complete initial paths")
        ("adapterReceipt", po::value<string>()->required(), "new adapter receipt path")
        ("finalReserve", po::value<double>()->required(), "seconds reserved for final checks/output")''')
    driver = replace_exact(driver, '\tsrand((int)time(0));', '''    // Restrict to the author's README recommended single-destroy ADDRESS.
    // Keep its fixed 8-agent neighborhood and top-K Bernoulli seed selection.
    if (vm["solver"].as<string>() != "LNS" || vm["replanAlgo"].as<string>() != "PP"
        || vm["destroyStrategy"].as<string>() != "RandomWalk"
        || vm["algorithm"].as<string>() != "bernoulie" || !vm["sipp"].as<bool>()
        || vm["b"].as<string>() != "canonical" || vm["neighborSize"].as<int>() != 8
        || vm["agentNum"].as<int>() < 8 || vm["maxIterations"].as<int>() <= 0
        || vm["k"].as<int>() <= 0 || vm["k"].as<int>() > vm["agentNum"].as<int>()
        || vm["seed"].as<int>() < 0 || !vm.count("outputPaths")
        || !std::isfinite(vm["cutoffTime"].as<double>())
        || !std::isfinite(vm["finalReserve"].as<double>())
        || vm["finalReserve"].as<double>() <= 0
        || vm["cutoffTime"].as<double>() <= vm["finalReserve"].as<double>())
        throw std::runtime_error("adapter: unsupported configuration");
    for (const auto* name : {"map", "agents", "initialPaths"})
        if (!std::ifstream(vm[name].as<string>()))
            throw std::runtime_error("adapter: missing required input");
    for (const auto* name : {"outputPaths", "adapterReceipt"})
        if (std::ifstream(vm[name].as<string>()))
            throw std::runtime_error("adapter: refusing output overwrite");
    auto& config = address_adapter::state();
    config.initial_file = vm["initialPaths"].as<string>();
    config.receipt_file = vm["adapterReceipt"].as<string>();
    config.total_seconds = vm["cutoffTime"].as<double>();
    config.final_reserve = vm["finalReserve"].as<double>();
    config.seed = unsigned(vm["seed"].as<int>());
    config.seeds.seed(config.seed);
    srand(config.seed);''')
    driver = replace_exact(driver, '            lns.validateSolution();', '''            lns.validateSolution();
            address_adapter::check_final(lns.agents, instance, lns.sum_of_costs);''')
    driver = replace_exact(driver, '\treturn 0;\n', '\treturn address_adapter::finish();\n')
    lns = files['src/LNS.cpp'].decode()
    lns = '#include "address_adapter_support.h"\n'+lns
    lns = replace_exact(lns, '    q_values = new std::vector<int>(num_agent, INT_MAX-1);',
        '    generator.seed(address_adapter::next_seed());\n    q_values = new std::vector<int>(num_agent, INT_MAX-1);')
    lns = replace_exact(lns, 'std::mt19937 rng(std::random_device{}());',
        'std::mt19937 rng(address_adapter::next_seed());', count=10)
    lns = replace_exact(lns, 'std::random_device rd;',
        'auto rd = [](){ return address_adapter::next_seed(); };', count=4)
    lns = replace_exact(lns, '    start_time = Time::now();\n    bool succ = getInitialSolution();', '''    start_time = Time::now();
    time_limit = std::max(0.0, address_adapter::remaining()-address_adapter::state().final_reserve);
    replan_time_limit = time_limit / 100; // preserve original per-repair ratio
    bool succ = getInitialSolution();''')
    lns = replace_exact(lns, 'bool LNS::getInitialSolution()\n{', '''bool LNS::getInitialSolution()
{
    if (!address_adapter::state().initial_file.empty()) {
        const auto check_start = address_adapter::Clock::now();
        const auto paths = address_adapter::read_initial(agents.size());
        const int cost = address_adapter::check(paths, instance);
        path_table.reset();
        neighbor.agents.resize(agents.size());
        for (size_t i = 0; i < agents.size(); ++i) {
            neighbor.agents[i] = int(i);
            agents[i].path.clear();
            for (int loc : paths[i]) agents[i].path.emplace_back(loc);
            path_table.insertPath(agents[i].id, agents[i].path);
        }
        neighbor.old_sum_of_costs = MAX_COST;
        neighbor.sum_of_costs = initial_sum_of_costs = sum_of_costs = cost;
        address_adapter::state().initial_soc = cost;
        address_adapter::state().initial_validated = true;
        address_adapter::state().initial_check_seconds =
            std::chrono::duration<double>(address_adapter::Clock::now()-check_start).count();
        return true;
    }''')
    instance = files['src/Instance.cpp'].decode()
    instance = replace_exact(instance, 'generateRandomAgents(warehouse_width);\n\t\t\tsaveNathan();',
        'throw std::runtime_error("adapter: refusing generated replacement agents");')
    return {'src/driver.cpp': driver.encode(), 'src/LNS.cpp': lns.encode(),
            'src/Instance.cpp': instance.encode(),
            'inc/address_adapter_support.h': (HERE/'address_adapter_support.h').read_bytes()}


def materialize(root, output, pins):
    """Copy only the 86 pinned build inputs (<2 MiB), preserving the full license."""
    files = {name: (root/name).read_bytes() for name in pins}
    changed = adapt(files)
    all_files = dict(files, **changed)
    output.mkdir(exist_ok=False)
    for name, raw in all_files.items():
        target = output/name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
    return {name: {'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}
            for name, raw in changed.items()}
