#include <fstream>
#include "simulation/new_simulator.h"
#include "graph/generate_graph.h"
#include "nlohmann/json.hpp"
using json=nlohmann::json;
int main(int argc,char**argv){
    if(argc!=2)return 2;
    json result=json::array();
    for(int mode=0;mode<3;++mode){
        auto paths=std::make_shared<Paths>();
        paths->push_back(Path{{{0,0},0},{{1,0},1},{{2,0},2}});
        auto g=construct_graph(paths,false);
        if(mode==1)g->delay(0,0,2);
        if(mode==2)g->delay(0,1,2);
        NewSimulator sim;
        int cost=sim.simulate(g);
        json weights=json::array();float sum=0;
        for(int i=0;i<2;++i){float w=g->edge_manager->get_edge(i,i+1).cost;weights.push_back(w);sum+=w;}
        result.push_back({{"case",mode==0?"unit":mode==1?"current_delay":"future_weight"},
                          {"type1_weights",weights},{"weighted_path_sum",sum},
                          {"native_cost",cost},{"native_ticks",sim.step_ctr},
                          {"terminated",sim.terminated()},{"paths",sim.paths}});
    }
    std::ofstream out(argv[1]);out<<result.dump(2)<<'\n';
}
