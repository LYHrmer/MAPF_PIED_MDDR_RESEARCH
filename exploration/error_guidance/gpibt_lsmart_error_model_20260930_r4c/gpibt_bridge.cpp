#include <MAPFPlanner.h>
#include <iostream>
using json=nlohmann::json;
int main(){
    auto* response=std::cout.rdbuf();std::cout.rdbuf(std::cerr.rdbuf());
    MAPFPlanner planner;std::string line;bool initialized=false;int step=0;
    while(std::getline(std::cin,line)){
        auto req=json::parse(line);auto* e=planner.env;const auto& ins=req.at("mapf_instance");
        if(!initialized){e->rows=req.at("rows");e->cols=req.at("cols");e->map=req.at("map").get<std::vector<int>>();e->num_of_agents=ins.at("starts").size();e->map_name="front_fig_5x5";e->curr_states.resize(e->num_of_agents);e->goal_locations.resize(e->num_of_agents);}
        e->curr_timestep=step;
        for(int a=0;a<e->num_of_agents;++a){e->curr_states[a]=State(ins.at("starts")[a].at("location"),step,0);e->goal_locations[a]={{ins.at("goals")[a][0].at("location"),step}};}
        if(!initialized){planner.initialize(10);planner.trajLNS.group_size=2;initialized=true;}
        const auto bias=req.at("priority_bias").get<std::vector<double>>();
        if(bias.size()!=2)throw std::runtime_error("invalid bias length");
        const auto before=planner.p,copy_before=planner.p_copy;
        std::vector<double> effective_base(2);
        for(int a=0;a<2;++a){
            if(!std::isfinite(bias[a])||std::abs(bias[a])>2.00000001)throw std::runtime_error("invalid bounded bias");
            effective_base[a]=e->goal_locations[a][0].first!=planner.trajLNS.tasks[a]?copy_before[a]:before[a]+1;
            planner.p[a]+=bias[a];planner.p_copy[a]+=bias[a];
        }
        std::vector<Action> actions;auto begin=std::chrono::steady_clock::now();planner.plan(10,actions);
        auto us=std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::steady_clock::now()-begin).count();
        const auto applied=planner.p;const auto order=planner.ids;
        for(int a=0;a<2;++a){planner.p[a]-=bias[a];planner.p_copy[a]-=bias[a];}
        json r={{"actions",actions},{"step",step++},{"planner_us",us},{"priority_adapter",{{"bias",bias},{"p_before",before},{"p_copy_before",copy_before},{"effective_base",effective_base},{"effective_applied",applied},{"search_order",order},{"p_after_restore",planner.p},{"p_copy_after_restore",planner.p_copy}}}};
        std::ostream out(response);out<<r.dump()<<std::endl;
    }
}
