#include <MAPFPlanner.h>
#include <fstream>
#include <iostream>
#include <random>
#include <numeric>
#include <cstdlib>
using json=nlohmann::json;

namespace TrafficMAPF {
std::vector<int> r7_starts;
std::vector<std::vector<double>> r7_costs;
unsigned long long r7_calls=0, r7_nonzero=0;
double r7_edge_penalty(int search_start,int destination) {
 ++r7_calls;
 auto it=std::find(r7_starts.begin(),r7_starts.end(),search_start);
 if(it==r7_starts.end()) throw std::runtime_error("R7 search start not a public current start");
 double value=r7_costs.at(it-r7_starts.begin()).at(destination);
 if(!std::isfinite(value)||value<0) throw std::runtime_error("invalid nonnegative duration cost");
 r7_nonzero+=(value>0);return value;
}
}

// Pure observation wrapper; every value is produced by the unchanged official
// QuadraticNetwork object, including its original rounding and clipping.
struct CountedNetwork:TrafficMAPF::Network {
 std::shared_ptr<TrafficMAPF::Network> original;unsigned long long calls=0;
 explicit CountedNetwork(std::shared_ptr<TrafficMAPF::Network> n):original(n){params_num=n->params_num;params=n->get_params();}
 std::vector<double> forward(std::vector<double>& x,std::vector<double>& m) override{++calls;return original->forward(x,m);}
 double forward(int d,std::vector<double>& x,std::vector<double>& m) override{++calls;return original->forward(d,x,m);}
 void set_params(std::vector<double> x) override{original->set_params(x);params=x;}
};
int main(int argc,char** argv){
 if(argc!=2)throw std::runtime_error("network config path required");
 json cfg;std::ifstream input(argv[1]);input>>cfg;
 auto& c=TrafficMAPF::network_config;
 c.WIN_R=cfg.at("win_r");c.has_map=cfg.at("has_map");c.has_path=cfg.at("has_path");c.has_previous=cfg.at("has_previous");c.use_all_flow=cfg.at("use_all_flow");c.use_cached_nn=cfg.at("use_cached_nn");c.use_rotate_input=cfg.at("rotate_input");c.output_size=cfg.at("output_size");c.hidden_size=cfg.at("hidden_size");c.input_type=cfg.at("net_input_type");c.default_obst_flow=cfg.at("default_obst_flow");c.learn_obst_flow=cfg.at("learn_obst_flow");
 auto* response=std::cout.rdbuf();std::cout.rdbuf(std::cerr.rdbuf());
 MAPFPlanner planner;planner.set_network_type(cfg.at("net_type"));planner.set_network_params(cfg.at("parameters").get<std::vector<double>>());
 auto counted=std::make_shared<CountedNetwork>(planner.network_ptr);planner.network_ptr=counted;
 std::srand(cfg.at("initial_priority_seed").get<unsigned>());
 std::string line;bool initialized=false;int step=0;std::vector<int> initial_ids,last_task_ids,reveal_steps,previous_locations;
 std::vector<std::vector<std::pair<int,int>>> completed_transitions;
 while(std::getline(std::cin,line)){
  auto req=json::parse(line);auto* e=planner.env;const auto& ins=req.at("mapf_instance");
  if(!initialized){e->rows=req.at("rows");e->cols=req.at("cols");e->map=req.at("map").get<std::vector<int>>();e->num_of_agents=ins.at("starts").size();e->map_name=req.at("map_name");e->file_storage_path="";e->curr_states.resize(e->num_of_agents);e->goal_locations.resize(e->num_of_agents);e->past_traffic_interval=cfg.at("past_traffic_interval");last_task_ids.assign(e->num_of_agents,-1);reveal_steps.resize(e->num_of_agents);previous_locations.assign(e->num_of_agents,-1);completed_transitions.resize(e->num_of_agents);}
  e->curr_timestep=step;e->goal_loc_arr.assign(e->map.size(),0);e->reset_hist_edge_usage();
  // R8 input states are explicitly planned frontier, never physical END.
  // OBJ3 and input_type=flow do not consume hist_edge_usage. Keep it empty.
  if(c.input_type!="flow" || OBJECTIVE!=3) throw std::runtime_error("R8 audited only OBJ3 flow");
  for(int a=0;a<e->num_of_agents;++a){int location=ins.at("starts")[a].at("location");e->curr_states[a]=State(location,step,0);int goal=ins.at("goals")[a][0].at("location"),task_id=ins.at("goals")[a][0].at("id");if(task_id!=last_task_ids[a]){last_task_ids[a]=task_id;reveal_steps[a]=step;}e->goal_locations[a]={{goal,reveal_steps[a]}};++e->goal_loc_arr[goal];}
  if(!initialized){planner.initialize(10);std::iota(planner.ids.begin(),planner.ids.end(),0);std::shuffle(planner.ids.begin(),planner.ids.end(),std::mt19937(cfg.at("initial_priority_seed").get<unsigned>()));for(int i=0;i<e->num_of_agents;++i)planner.p[planner.ids[i]]=double(e->num_of_agents-i)/(e->num_of_agents+1.0);planner.p_copy=planner.p;initial_ids=planner.ids;initialized=true;}
  TrafficMAPF::r7_starts.clear();for(auto &s:ins.at("starts"))TrafficMAPF::r7_starts.push_back(s.at("location"));
  TrafficMAPF::r7_costs=req.at("edge_costs").get<std::vector<std::vector<double>>>();TrafficMAPF::r7_calls=0;TrafficMAPF::r7_nonzero=0;
  auto p_before=planner.p;auto copy_before=planner.p_copy;std::vector<Action> actions;auto begin=std::chrono::steady_clock::now();auto calls_before=counted->calls;planner.plan(10,actions);
  json r={{"actions",actions},{"step",step++},{"objective",OBJECTIVE},{"initial_priority_seed",cfg.at("initial_priority_seed")},{"initial_ids",initial_ids},{"parameter_count",planner.network_ptr->params_num},{"network_parameters",planner.network_ptr->get_params()},{"network_forward_calls",counted->calls-calls_before},{"network_forward_calls_cumulative",counted->calls},{"search_order",planner.ids},{"p_before",p_before},{"p_copy_before",copy_before},{"p_after",planner.p},{"p_copy_after",planner.p_copy},{"planner_us",std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::steady_clock::now()-begin).count()}};
  r["r7_edge_cost_calls"]=TrafficMAPF::r7_calls;r["r7_nonzero_edge_cost_calls"]=TrafficMAPF::r7_nonzero;
  r["rand_seed"]=cfg.at("initial_priority_seed");r["goal_reveal_plan_steps"]=reveal_steps;
  std::ostream out(response);out<<r.dump()<<std::endl;
 }
}
