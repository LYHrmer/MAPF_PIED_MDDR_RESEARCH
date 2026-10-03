// Research adapter, not a modification of the upstream search/execution algorithm.
#include <chrono>
#include <fstream>
#include <stdexcept>
#include "Algorithm/Astar.h"
#include "graph/generate_graph.h"
#include "simulation/new_simulator.h"
#include "nlohmann/json.hpp"
using json = nlohmann::json;

json export_graph(const std::shared_ptr<Graph>& g) {
    if (!g->is_fixed()) throw std::runtime_error("export requires fixed graph");
    json j;
    j["paths"] = *g->paths;
    j["current"] = *g->curr_states;
    j["offsets"] = *g->accum_state_cnts_begin;
    for (const auto& entry : std::vector<std::pair<std::string,std::shared_ptr<Subgraph>>>{
             {"type1",g->type1_edges},{"type2",g->non_switchable_type2_edges}}) {
        j[entry.first] = json::array();
        for (int u=0; u<g->get_num_states(); ++u)
            for (int v : entry.second->get_out_neighbor_global_ids(u))
                j[entry.first].push_back({u,v,g->edge_manager->get_edge(u,v).cost});
    }
    return j;
}

json execute_export(const std::shared_ptr<Graph>& g) {
    // A fresh simulator avoids the upstream resize-retains-old-paths behaviour.
    NewSimulator native;
    const int native_cost = native.simulate(g);
    if (!native.terminated()) throw std::runtime_error("native simulation stuck");
    NewSimulator traced;
    traced.reset(g, *g->curr_states);
    traced.step_ctr=0;
    traced.total_delays=0;
    json states=json::array();
    auto snapshot = [&]() {
        std::vector<int> ids;
        for (const auto& a : traced.agent_states) ids.push_back(a.state_id);
        states.push_back(ids);
    };
    snapshot();
    int cost=0;
    while (!traced.terminated()) {
        if (traced.all_stucked()) throw std::runtime_error("trace stuck");
        cost += traced.step();
        ++traced.step_ctr;
        if (traced.step_ctr > 1000000) throw std::runtime_error("trace horizon exceeded");
        snapshot();
    }
    if (cost!=native_cost || traced.paths!=native.paths)
        throw std::runtime_error("step trace differs from original simulate API");
    return {{"graph",export_graph(g)}, {"states",states}, {"paths",native.paths},
            {"cost",native_cost}, {"ticks",traced.step_ctr},
            {"native_simulate_matches_step_trace",true}};
}

int main(int argc, char** argv) {
    if (argc!=5) throw std::runtime_error("export_author PATH SITUATION METHOD OUTPUT");
    const std::string method(argv[3]);
    if (method!="GSES" && method!="Improved_GSES") throw std::runtime_error("unknown method");
    const bool improved=method=="Improved_GSES";
    auto graph=construct_graph(argv[1]);
    std::ifstream input(argv[2]);
    const json situation=json::parse(input);
    const auto states=situation.at("states").get<std::vector<int>>();
    const auto delays=situation.at("delay_steps").get<std::vector<int>>();
    if (states.size()!=size_t(graph->get_num_agents()) || states.size()!=delays.size())
        throw std::runtime_error("situation size mismatch");
    std::shared_ptr<GroupManager> groups(nullptr);
    auto t=std::chrono::steady_clock::now();
    if (improved) {
        auto sw=graph->copy();
        sw->make_switchable();
        groups=std::make_shared<GroupManager>(sw,*sw->curr_states,"all");
    }
    const auto group_us=std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::steady_clock::now()-t).count();
    graph->update_curr_states(states);
    graph->delay(std::vector<COST_TYPE>(delays.begin(),delays.end()));
    json output;
    output["original"]=execute_export(graph);
    auto solver=std::make_shared<Astar>(16,true,improved?"largest_diff":"default",
        improved?"wcg_greedy":"zero",true,improved,1.0,1.0,-1,groups,10);
    t=std::chrono::steady_clock::now();
    const auto candidate=solver->solve(graph);
    const auto elapsed=std::chrono::steady_clock::now()-t;
    const bool accepted=std::chrono::duration_cast<std::chrono::seconds>(elapsed).count()<16;
    output["selected"]=execute_export(accepted?candidate:graph);
    output["status"]=accepted?"Succ":"Timeout";
    output["method"]=method;
    output["search_elapsed_us"]=std::chrono::duration_cast<std::chrono::microseconds>(elapsed).count();
    output["grouping_us"]=group_us;
    output["stats"]=json::object();
    solver->write_stats(output["stats"]);
    std::ofstream out(argv[4]);
    out<<output.dump()<<'\n';
    if (!out) throw std::runtime_error("output write failed");
}
