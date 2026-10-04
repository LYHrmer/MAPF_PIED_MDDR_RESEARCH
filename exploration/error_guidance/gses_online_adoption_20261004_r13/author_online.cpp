// New research input/output adapter. All upstream Graph/Astar sources unchanged.
#include <chrono>
#include <fstream>
#include <stdexcept>
#include "Algorithm/Astar.h"
#include "Algorithm/graph_algo.h"
#include "group/group.h"
#include "nlohmann/json.hpp"
using json=nlohmann::json;
json export_graph(const std::shared_ptr<Graph>& g) {
 if (!g->is_fixed()) throw std::runtime_error("nonfixed candidate");
 json j={{"paths",*g->paths},{"current",*g->curr_states},{"offsets",*g->accum_state_cnts_begin}};
 for (auto entry:std::vector<std::pair<std::string,std::shared_ptr<Subgraph>>>{{"type1",g->type1_edges},{"type2",g->non_switchable_type2_edges}}) {
  j[entry.first]=json::array();
  for(int u=0;u<g->get_num_states();u++) for(int v:entry.second->get_out_neighbor_global_ids(u))
   j[entry.first].push_back({u,v,g->edge_manager->get_edge(u,v).cost});
 }
 return j;
}
int main(int argc,char** argv) {
 if(argc!=4) throw std::runtime_error("author_online PUBLIC_INPUT METHOD OUTPUT");
 std::ifstream in(argv[1]);json input=json::parse(in);const auto& j=input.at("solver_graph");
 std::string method=argv[2];bool improved=method=="Improved_GSES";
 if(!improved && method!="GSES") throw std::runtime_error("method");
 auto paths=std::make_shared<Paths>(j.at("paths").get<Paths>());
 auto graph=std::make_shared<Graph>(paths,j.at("current").get<std::vector<int>>());
 graph->edge_manager=std::make_shared<EdgeManager>();
 graph->type1_edges=std::make_shared<Subgraph>(graph->get_num_agents(),graph->accum_state_cnts_begin,graph->state_cnts,graph->global_state_id_to_agent_state_ids);
 graph->non_switchable_type2_edges=std::make_shared<Subgraph>(graph->get_num_agents(),graph->accum_state_cnts_begin,graph->state_cnts,graph->global_state_id_to_agent_state_ids);
 for(const auto& key: {"type1","type2"}) for(const auto& e:j.at(key)) {
  int u=e[0],v=e[1];COST_TYPE w=e[2];auto a=graph->get_agent_state_id(u),b=graph->get_agent_state_id(v);
  (std::string(key)=="type1"?graph->type1_edges:graph->non_switchable_type2_edges)->insert_edge(a.first,a.second,b.first,b.second);
  graph->edge_manager->add_edge(u,v,w);
  if(std::string(key)=="type2") graph->edge_manager->add_edge(v+1,u-1,w);
 }
 if(export_graph(graph)!=j) throw std::runtime_error("author input roundtrip mismatch");
 auto grouping_start=std::chrono::steady_clock::now();std::shared_ptr<GroupManager> groups(nullptr);
 if(improved) {auto sw=graph->copy();sw->make_switchable();groups=std::make_shared<GroupManager>(sw,*sw->curr_states,"all");}
 auto grouping_us=std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::steady_clock::now()-grouping_start).count();
 auto solver=std::make_shared<Astar>(16,true,improved?"largest_diff":"default",improved?"wcg_greedy":"zero",true,improved,1.0,1.0,-1,groups,10);
 auto start=std::chrono::steady_clock::now();auto candidate=solver->solve(graph);
 auto micros=std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::steady_clock::now()-start).count();
 bool in_budget=micros<16000000;
 json out={{"method",method},{"status",in_budget?"Succ":"Timeout"},{"search_elapsed_us",micros},{"grouping_us",grouping_us},{"input_graph",export_graph(graph)},{"selected_graph",export_graph(in_budget?candidate:graph)}};
 out["stats"]=json::object();solver->write_stats(out["stats"]);
 std::ofstream sink(argv[3]);sink<<out.dump()<<'\n';if(!sink) throw std::runtime_error("write failed");
}
