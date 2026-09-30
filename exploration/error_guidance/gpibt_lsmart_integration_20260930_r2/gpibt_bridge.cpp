#include <MAPFPlanner.h>
#include <iostream>
using json=nlohmann::json;
int main() {
    // Official logging goes to stderr; stdout is the request/response channel.
    auto* response=std::cout.rdbuf();
    std::cout.rdbuf(std::cerr.rdbuf());
    MAPFPlanner planner;
    std::string line;
    bool initialized=false;
    int step=0;
    while(std::getline(std::cin,line)) {
        auto req=json::parse(line);
        auto* e=planner.env;
        const auto& instance=req.at("mapf_instance");
        if(!initialized) {
            e->rows=req.at("rows"); e->cols=req.at("cols");
            e->map=req.at("map").get<std::vector<int>>();
            e->num_of_agents=instance.at("starts").size();
            e->map_name="front_fig_5x5";
            e->curr_states.resize(e->num_of_agents);
            e->goal_locations.resize(e->num_of_agents);
        }
        e->curr_timestep=step;
        for(int a=0;a<e->num_of_agents;++a) {
            e->curr_states[a]=State(instance.at("starts")[a].at("location"),step,0);
            e->goal_locations[a]={{instance.at("goals")[a][0].at("location"),step}};
        }
        if(!initialized) {
            planner.initialize(10);
            // Tiny-instance support: author's public group-size parameter.
            // flow.cpp loops group_size entries even if N is smaller.
            planner.trajLNS.group_size=2;
            initialized=true;
        }
        std::vector<Action> actions;
        auto begin=std::chrono::steady_clock::now();
        planner.plan(10,actions);
        auto us=std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::steady_clock::now()-begin).count();
        json r={{"actions",actions},{"step",step++},{"planner_us",us}};
        std::ostream out(response); out << r.dump() << std::endl;
    }
}
