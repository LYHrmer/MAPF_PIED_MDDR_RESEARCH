"""Software fixtures: actual transformed author methods, fake clocks/graph/search.

No author Instance, MAPF benchmark, scientific search or prior DEV replay.
"""
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from address_budget import adapt, function_span
from test_address_recovery import sources
import test_address_loop_guard as loop_contract

HERE=Path(__file__).resolve().parent


def loop_fixture(source):
    old=loop_contract.LOOP_ANCHOR
    if 'address_budget::below_repair_cap(iteration_stats.size(),num_of_iterations)' in source:
        loop_contract.LOOP_ANCHOR=old.replace('iteration_stats.size() <= num_of_iterations',
            'address_budget::below_repair_cap(iteration_stats.size(),num_of_iterations)')
    try:return loop_contract.fixture(source)
    finally:loop_contract.LOOP_ANCHOR=old


def method(source,signature):
    a,b=function_span(source,signature);return source[a:b]


COMMON=r'''
#include "address_budget_support.h"
#include <cassert>
#include <iostream>
#include <map>
#include <queue>
#include <list>
#include <set>
#include <tuple>
using namespace std;
double tick=0,cputick=0,increment=0;
double fake_wall(){tick+=increment;return tick;}
double fake_cpu(){return cputick;}
void setup(double stop=100) {
    address_budget::state()=address_budget::State{};
    auto& s=address_budget::state();s.wall=fake_wall;s.cpu=fake_cpu;
    s.configured=true;s.wall_stop=stop;s.cpu_limit=10;s.cpu_reserve=1;
    tick=0;cputick=0;increment=0;
}
struct PathEntry { int location;PathEntry(int x):location(x){};PathEntry():location(0){}; };
using Path=vector<PathEntry>;
'''


def pp_fixture(source):
    return COMMON+r'''
using fsec=chrono::duration<double>;
struct Time {static fsec now(){return fsec(0);}};
int calls=0,expire_call=0;
struct Planner {
    int start_location=0;vector<int>my_heuristic{0};
    template<class T>Path findPath(const T&) {
      ++calls;++address_budget::state().sipp_calls;address_budget::state().last_sipp_end="FOUND";
      if(calls==expire_call)tick=100;
      if(expire_call==-2&&calls==2){address_budget::state().last_sipp_end="FOCAL_DRAINED_EMPTY";return {};}
      if(expire_call==-4)return {{start_location},{start_location},{start_location+1},{start_location+2}};
      return {{start_location},{start_location+1},{start_location+2}};
    }
};
struct Agent {int id;Path path;Planner* path_planner;};
struct FakeTable {
    map<int,Path> paths;
    void insertPath(int a,const Path&p){assert(!paths.count(a));paths[a]=p;}
    void deletePath(int a,const Path&p){assert(paths.count(a));assert(paths[a].size()==p.size());paths.erase(a);}
};
struct ConstraintTable {ConstraintTable(int,int,FakeTable*){}};
struct Graph {
    int map_size=15,num_of_rows=3,num_of_cols=5;
    bool isObstacle(int)const{return false;}
    vector<int>getStarts()const{return {0,5,10};}
    vector<int>getGoals()const{return {2,7,12};}
};
struct LNS {
    enum{RANDOMWALK,DESTROY_COUNT,CANONICAL,BERNOULIE,NORMAL,INTERSECTION};
    int screen=0,destroy_strategy=RANDOMWALK,algo=BERNOULIE,current_index=-1,sum_of_costs=9,num_of_failures=0;
    vector<int>*q_values=nullptr,*frequency=nullptr;vector<double>*location_q_values=nullptr,*location_frequency=nullptr;
    vector<int>alpha,beta,location_alpha,location_beta;vector<double>mu,sigma2,location_mu,location_sigma2;
    vector<int>iteration_stats{1};double runtime=0,time_limit=100,replan_time_limit=100;fsec start_time{0};
    struct {vector<int>agents{0,1,2};vector<Path>old_paths;int old_sum_of_costs=9,sum_of_costs=0;}neighbor;
    Graph instance;FakeTable path_table;vector<Planner>planners;vector<Agent>agents;
    LNS(){planners.resize(3);for(int i=0;i<3;++i){planners[i].start_location=i*5;Path p{{i*5},{i*5},{i*5+1},{i*5+2}};agents.push_back({i,p,&planners[i]});neighbor.old_paths.push_back(p);}}
    bool runPP();
};
'''+method(source,'bool LNS::runPP()')+r'''
int main(int argc,char**argv){
    setup();expire_call=atoi(argv[1]);LNS test;
    if(argc>3)address_budget::configure_trace(argv[3]);
    auto original=test.neighbor.old_paths;
    bool accepted=test.runPP();
    if(expire_call){assert(!accepted);assert(test.neighbor.sum_of_costs==9);assert(address_budget::state().rollbacks==1);
      for(int a=0;a<3;++a){assert(test.agents[a].path.size()==4);assert(test.path_table.paths.at(a).size()==4);}}
    else {assert(accepted);assert(test.neighbor.sum_of_costs==6);assert(test.path_table.paths.size()==3);}
    auto& s=address_adapter::state();s.initial_soc=9;s.initial_validated=true;s.total_seconds=5;s.receipt_file=argv[2];
    address_adapter::check_final(test.agents,test.instance,test.neighbor.sum_of_costs);
    cout<<calls<<" "<<accepted<<" FULL_FINAL_OUTPUT\n";
    return address_budget::finish();
}
'''


def seed_fixture(source):
    return COMMON+r'''
vector<int> sampled;
namespace boost { namespace random {
template<class T=double>struct beta_distribution {
    int id;beta_distribution(int alpha,int):id(alpha-100){}
    template<class RNG> double operator()(RNG& gen){sampled.push_back(id);return double(gen())/RNG::max();}
};}}
struct Planner {int start_location=0;vector<int>my_heuristic{1};};
struct Agent {int id;Path path{{0},{1}};Planner* path_planner;
    int getNumOfDelays()const{return int(path.size())-1-path_planner->my_heuristic[path_planner->start_location];}};
struct AgentComparator {bool operator()(const pair<int,int>&a,const pair<int,int>&b)const{return a.first<b.first;}};
struct LNS {
    vector<Planner> planners=vector<Planner>(9);vector<Agent>agents;
    vector<int>alpha,beta,counts=vector<int>(9,0);vector<int>*frequency=&counts;
    int k=9,current_index=-1,neighbor_size=8,screen=0;
    struct {vector<int>agents;}neighbor;
    LNS(){for(int i=0;i<9;++i){agents.push_back({i,{{0},{1}},&planners[i]});alpha.push_back(100+i);beta.push_back(1);}}
    int bernoulie();int wrapper(){return bernoulie();}
    bool generateNeighborByRandomWalk(int);
    void randomWalk(int,int,int,set<int>&members,int,int){members.insert(0);}
    vector<int>expected(bool filter)const{
        priority_queue<pair<int,int>,vector<pair<int,int>>,AgentComparator>q;
        for(const auto&a:agents)q.push({a.getNumOfDelays(),a.id});
        vector<int>ids;for(int i=0;i<k&&!q.empty();++i){if(!filter||q.top().first>0)ids.push_back(q.top().second);q.pop();}return ids;
    }
};
'''+method(source,'int LNS::bernoulie()')+'\n'+method(source,'bool LNS::generateNeighborByRandomWalk(')+r'''
int main(int argc,char**argv){
    setup();LNS x;const string mode=argv[1];
    address_adapter::state().seeds.seed(123);srand(123);
    if(mode=="off"){
        x.agents[1].path={{0},{0},{1}};x.agents[3].path={{0},{0},{1}};
        for(int j=0;j<4;++j){sampled.clear();const int chosen=x.bernoulie();assert(sampled==x.expected(false));cout<<chosen<<",";}
        cout<<address_adapter::next_seed()<<","<<rand()<<"\n";return 0;
    }
    address_budget::configure_seed_admission("positive_delay");
    if(mode=="zero"){
        assert(x.bernoulie()==-1);assert(sampled.empty());
        const auto&c=address_budget::state().seed_admission;
        assert(c.empty_eligible_calls==1&&c.static_soc_lower_bound_reached&&c.filtered_zero_candidates==9);
        assert(!address_budget::state().global_deadline&&c.deadline_calls==0);return 0;
    }
    if(mode=="deadline"){
        increment=1;address_budget::state().wall_stop=4;
        assert(x.bernoulie()==-1);const auto&c=address_budget::state().seed_admission;
        assert(c.empty_eligible_calls==0&&!c.static_soc_lower_bound_reached&&c.deadline_calls==1);
        assert(address_budget::state().global_deadline&&address_budget::state().deadline_resource=="WALL");return 0;
    }
    if(mode=="full_group"){
        x.neighbor_size=9;assert(x.generateNeighborByRandomWalk(0));
        assert(x.neighbor.agents.size()==9&&address_budget::state().seed_admission.selection_calls==0);return 0;
    }
    x.agents[1].path={{0},{0},{1}};
    if(mode=="member"){
        assert(x.generateNeighborByRandomWalk(0));assert(x.neighbor.agents==vector<int>({0,1}));
        assert(x.agents[0].getNumOfDelays()==0);return 0;
    }
    if(mode=="invalid"){
        x.planners[0].my_heuristic[0]=2;bool caught=false;
        try{x.bernoulie();}catch(const runtime_error&){caught=true;}
        assert(caught&&!address_budget::state().seed_admission.static_soc_lower_bound_reached);return 0;
    }
    assert(mode=="updates");
    assert(x.bernoulie()==1&&sampled==vector<int>{1});
    sampled.clear();x.agents[3].path={{0},{0},{1}};x.agents[5].path={{0},{0},{1}};
    x.bernoulie();assert(sampled==x.expected(true));
    sampled.clear();x.agents[1].path={{0},{1}}; // accepted incumbent removes eligibility
    x.bernoulie();assert(sampled==x.expected(true));assert(find(sampled.begin(),sampled.end(),1)==sampled.end());
    sampled.clear();x.agents[1].path={{0},{0},{1}}; // rolled-back incumbent restores eligibility
    x.bernoulie();assert(sampled==x.expected(true));assert(find(sampled.begin(),sampled.end(),1)!=sampled.end());
}
'''


def sipp_fixture(source,reservation_source):
    return COMMON+r'''
using Interval=tuple<int,int,bool>;
struct ConstraintTable {
    int length_min=0,length_max=1000;
    int getHoldingTime(int,int)const{return 0;}
    int getLastCollisionTimestep(int)const{return -1;}
    int getFutureNumOfCollisions(int,int)const{return 0;}
};
struct ReservationTable {
    const ConstraintTable&constraint_table;map<int,list<Interval>>sit;
    ReservationTable(const ConstraintTable&c,int):constraint_table(c){}
    void insert2SIT(int,int,int);
    Interval get_first_safe_interval(int x){
        if(x==99){for(int i=0;i<100;++i)sit[x].push_back({i,i+1,false});insert2SIT(x,99,100);}
        return {0,1000,false};
    }
    vector<tuple<int,int,int,bool,bool>>get_safe_intervals(int,int,int t,int){return {{1000,t,999,false,false}};}
    bool find_safe_interval(Interval&,int,int){return false;}
};
struct SIPPNode {
    int location,timestep,h_val,num_of_conflicts,high_expansion,high_generation;bool in_openlist=true,is_goal=false,wait_at_goal=false;
    SIPPNode(int l,int t,int h,void*,int,int high,int exp,bool,int conflicts):location(l),timestep(t),h_val(h),num_of_conflicts(conflicts),high_expansion(exp),high_generation(high){}
    int getFVal()const{return timestep+h_val;}
};
struct FakeGraph {list<int>getNeighbors(int l){return l<40?list<int>{l+1}:list<int>{};}};
struct SIPP {
    int start_location=0,goal_location=100,num_expanded=0,released=0;
    vector<int>my_heuristic=vector<int>(200,0);FakeGraph instance;
    struct Queue{vector<SIPPNode*>v;bool empty(){return v.empty();}auto top(){return v.back();}void pop(){v.pop_back();}}focal_list;
    vector<SIPPNode*>owned;
    void reset(){}
    void pushNodeToFocal(SIPPNode*p){owned.push_back(p);focal_list.v.push_back(p);}
    bool dominanceCheck(SIPPNode*){return true;}
    void updatePath(SIPPNode*p,Path&path){path={{p->location}};}
    void releaseNodes(){for(auto*p:owned)delete p;owned.clear();focal_list.v.clear();++released;}
    Path findPath(const ConstraintTable&);
};
'''+method(reservation_source,'void ReservationTable::insert2SIT(')+'\n'+method(source,'Path SIPP::findPath(const ConstraintTable& constraint_table)')+r'''
int main(int argc,char**argv){
    setup(20);increment=1;SIPP s;if(atoi(argv[1]))s.start_location=99;
    ConstraintTable c;auto p=s.findPath(c);
    assert(p.empty());assert(s.owned.empty());assert(s.released==1);
    cout<<s.num_expanded<<" "<<address_budget::state().last_sipp_end<<" "<<address_budget::state().sipp_deadlines<<"\n";
}
'''


class BudgetContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base=sources();cls.guarded=dict(cls.base,**adapt(cls.base));cls.tmp=tempfile.TemporaryDirectory();cls.root=Path(cls.tmp.name)

    @classmethod
    def tearDownClass(cls):cls.tmp.cleanup()

    def compile(self,name,code):
        src=self.root/(name+'.cpp');exe=src.with_suffix('');src.write_text(code)
        result=subprocess.run(['rtk','proxy','g++','-std=c++14','-O0','-I',str(HERE),str(src),'-o',str(exe)],capture_output=True,text=True,timeout=30)
        self.assertEqual(result.returncode,0,result.stderr);return exe

    def execute(self,exe,*args):
        result=subprocess.run(['rtk','proxy',str(exe),*map(str,args)],capture_output=True,text=True,timeout=5)
        self.assertEqual(result.returncode,0,result.stderr)
        return result.stdout.strip().splitlines()[-1] if result.stdout.strip() else ''

    def test_positive_slack_failed_groups_stop_before_iteration_cap(self):
        for variant,files in (('red',self.base),('green',self.guarded)):
            code=loop_fixture(files['src/LNS.cpp'].decode())
            code=code.replace('struct Agent { vector<Vertex> path; Planner* path_planner; };',
                'struct Agent { vector<Vertex> path; Planner* path_planner; int getNumOfDelays() const {return int(path.size())-1-path_planner->my_heuristic[path_planner->start_location];} };')
            code=code.replace('#include "address_adapter_support.h"','#include "address_budget_support.h"\ndouble ticks=0;double stepclock(){return ++ticks;}double zerocpu(){return 0;}')
            code=code.replace('agents.insert((a+1)%9);','/* never generates another agent */')
            code=code.replace('    if(!test.run_fixture())','    address_budget::state().configured=true;address_budget::state().wall=stepclock;address_budget::state().cpu=zerocpu;address_budget::state().wall_stop=30;address_budget::state().cpu_limit=10;address_budget::state().cpu_reserve=1;\n    if(!test.run_fixture())')
            exe=self.compile('groups_'+variant,code)
            raw=self.execute(exe,self.root/('groups_'+variant+'.json'),'slack').split()
            generated,repairs,stats,tick=map(int,raw[:4]);self.assertEqual((repairs,stats),(0,1))
            if variant=='red':self.assertEqual(generated,100)
            else:self.assertLess(generated,100);self.assertGreater(generated,0)

    def test_seed_admission_exact_order_updates_and_zero_neighbor_membership(self):
        exe=self.compile('seed_admission',seed_fixture(self.guarded['src/LNS.cpp'].decode()))
        for mode in ('zero','deadline','full_group','member','invalid','updates'):
            self.execute(exe,mode)

    def test_seed_admission_default_preserves_selection_and_rng_stream(self):
        outputs=[]
        for name,files in (('original',self.base),('current',self.guarded)):
            outputs.append(self.execute(self.compile('seed_default_'+name,
                seed_fixture(files['src/LNS.cpp'].decode())),'off'))
        self.assertEqual(outputs[0],outputs[1])

    def test_effort_mode_and_termination_contracts(self):
        code=COMMON+r'''
int main(){
 using namespace address_budget;setup();
 configure_effort("fixed_repairs",16);assert(below_repair_cap(16,16));assert(!below_repair_cap(17,16));
 record_loop_exit(17,16);assert(state().termination=="REPAIR_CAP");
 setup();configure_effort("total_budget",0);assert(below_repair_cap(1000000,0));
 ::tick=100;assert(expired("GROUP"));record_loop_exit(20,0);
 assert(state().termination=="GLOBAL_DEADLINE"&&state().deadline_resource=="WALL");
 setup();cputick=9;assert(expired("CPU"));assert(state().deadline_resource=="CPU");
 setup();::tick=100;cputick=9;assert(expired("BOTH"));assert(state().deadline_resource=="WALL_AND_CPU");
 setup();configure_effort("total_budget",0);mark_static_soc_lower_bound();record_loop_exit(1,0);
 assert(state().termination=="STATIC_SOC_BOUND");
 for(auto invalid:vector<pair<string,int>>{{"fixed_repairs",0},{"total_budget",1},{"other",1}}){
    bool caught=false;try{configure_effort(invalid.first,invalid.second);}catch(const runtime_error&){caught=true;}assert(caught);
 }
}
'''
        self.execute(self.compile('effort_modes',code))

    def test_seed_eligibility_reads_actual_acceptance_and_rollback_paths(self):
        code=pp_fixture(self.guarded['src/LNS.cpp'].decode())
        code=code.replace('vector<int>my_heuristic{0};','vector<int>my_heuristic=vector<int>(15,2);')
        code=code.replace('    bool accepted=test.runPP();','''    address_budget::configure_seed_admission("positive_delay");
    for(const auto&a:test.agents)address_budget::check_seed_delay(a,1);
    bool accepted=test.runPP();
    for(const auto&a:test.agents)address_budget::check_seed_delay(a,accepted?0:1);
    assert(address_budget::state().seed_admission.agents_checked==6);''')
        exe=self.compile('seed_transaction',code)
        for expiry in (0,2,-2,-4):
            receipt=self.root/('seed_transaction_'+str(expiry)+'.json');self.execute(exe,expiry,receipt)
            row=json.loads(receipt.read_text());self.assertTrue(row['initial_and_final_validated'])
            self.assertEqual(row['repair_attempts'],1)
            self.assertEqual(row['seed_admission']['agents_checked'],6)

    def test_actual_loop_total_budget_has_no_iteration_cap_and_zero_bound_stops(self):
        code=loop_fixture(self.guarded['src/LNS.cpp'].decode())
        code=code.replace('#include "address_adapter_support.h"','#include "address_budget_support.h"')
        code=code.replace('struct Agent { vector<Vertex> path; Planner* path_planner; };',
            'struct Agent { vector<Vertex> path; Planner* path_planner; int getNumOfDelays() const {return int(path.size())-1-path_planner->my_heuristic[path_planner->start_location];} };')
        code=code.replace('    if(!test.run_fixture())','''    address_budget::configure_effort("total_budget",0);
    address_budget::state().cpu_limit=10;address_budget::state().cpu_reserve=1;
    address_budget::configure_seed_admission("positive_delay");test.num_of_iterations=0;
    if(!test.run_fixture())''')
        code=code.replace('int code=address_adapter::finish();','int code=address_budget::finish();')
        exe=self.compile('actual_total_budget',code)
        for slack in (False,True):
            receipt=self.root/('actual_total_'+str(slack)+'.json')
            raw=self.execute(exe,receipt,*(['slack'] if slack else [])).split()
            # A total-budget run with num_of_iterations=0 still performs one
            # useful fixture repair; both paths stop at the complete SOC bound.
            self.assertEqual(int(raw[1]),int(slack))
            value=json.loads(receipt.read_text());self.assertIsNone(value['repair_cap'])
            self.assertEqual(value['effort_mode'],'total_budget')
            self.assertEqual(value['termination'],'STATIC_SOC_BOUND')
            self.assertTrue(value['static_soc_lower_bound_reached'])
            self.assertTrue(value['initial_and_final_validated'])

    def test_actual_sipp_and_safe_interval_interrupt_classified_deadline(self):
        for variant,files in (('red',self.base),('green',self.guarded)):
            exe=self.compile('sipp_'+variant,sipp_fixture(files['src/SIPP.cpp'].decode(),files['src/ReservationTable.cpp'].decode()))
            expanded,stop,count=self.execute(exe,0).split()
            if variant=='red':self.assertEqual(int(expanded),41);self.assertEqual(int(count),0)
            else:self.assertLess(int(expanded),41);self.assertEqual((stop,count),('DEADLINE','1'))
            if variant=='green':
                expanded,stop,count=self.execute(exe,1).split();self.assertEqual((expanded,stop,count),('0','DEADLINE','1'))

    def test_partial_and_last_found_deadline_roll_back_and_final_output(self):
        exe=self.compile('pp',pp_fixture(self.guarded['src/LNS.cpp'].decode()))
        for expiry in (0,2,3):
            receipt=self.root/('pp'+str(expiry)+'.json');self.execute(exe,expiry,receipt)
            value=json.loads(receipt.read_text());self.assertTrue(value['initial_and_final_validated'])
            self.assertEqual(value['final_soc'],9 if expiry else 6)
            self.assertEqual(value['rollbacks'],int(bool(expiry)))

    def test_trace_uses_real_call_position_and_preserves_no_diagnosis(self):
        from run_address_adapter import verify_attempt_trace
        exe=self.compile('trace_pp',pp_fixture(self.guarded['src/LNS.cpp'].decode()))
        for mode,stop,position,site in ((0,'FOUND',-1,'COMPLETE'),(2,'DEADLINE',1,'RETURN'),
                                       (-2,'FOCAL_DRAINED_EMPTY',1,'RETURN'),(-4,'COST_STOP',2,'COST_BOUND')):
            receipt=self.root/('trace_receipt'+str(mode)+'.json');trace=self.root/('trace'+str(mode)+'.jsonl')
            self.execute(exe,mode,receipt,trace)
            row=json.loads(trace.read_text());native=json.loads(receipt.read_text())
            verify_attempt_trace(trace.read_bytes(),native,3)
            self.assertEqual(row['primary_stop'],stop);self.assertEqual(row['failed_position_zero_based'],position)
            self.assertEqual(row['failure_site'],site)
            self.assertEqual(row['failed_agent'],-1 if position<0 else row['order'][position])
            self.assertFalse(row['blockers_checked']);self.assertFalse(row['recoverability_established'])
            self.assertEqual(row['primary_calls'],len(row['primary_returns']))
            self.assertEqual(row['primary_calls'],native['sipp_calls'])
            self.assertTrue(native['attempt_trace_enabled']);self.assertEqual(native['attempt_trace_rows'],1)
            for metric in ('wall','cpu'):
                self.assertEqual(row['cost']['primary_search_'+metric+'_ns'],
                    sum(x[metric+'_ns'] for x in row['primary_returns']))

    def test_first_observed_deadlines_keep_local_global_and_last_distinct(self):
        code=COMMON+r'''
int main(){
    setup();address_budget::configure_cost_diagnostics(1);
    {address_budget::RepairScope repair(1);
     tick=2;assert(address_budget::expired("SEARCH_RETURN"));
     const auto first=address_budget::state().event_deadlines.first;
     assert(first.stage=="SEARCH_RETURN"&&first.local_wall&&!first.global_cpu&&!first.global_wall);
     cputick=9;assert(address_budget::expired("VALIDATION_ENTRY"));
     auto&s=address_budget::state();
     assert(s.event_deadlines.first.stage=="SEARCH_RETURN");
     assert(s.event_deadlines.global.stage=="VALIDATION_ENTRY"&&s.event_deadlines.global.global_cpu);
     assert(s.last_stage=="VALIDATION_ENTRY");
     assert(address_budget::expired("ACCEPT"));
     assert(s.event_deadlines.first.stage=="SEARCH_RETURN"&&s.event_deadlines.global.stage=="VALIDATION_ENTRY");
     assert(s.last_stage=="ACCEPT");}
    setup();address_budget::configure_cost_diagnostics(1);cputick=9;
    assert(address_budget::expired("CPU_ONLY"));
    assert(address_budget::state().repair_deadline); // Historical latch, NOT local-wall evidence.
    assert(!address_budget::state().event_deadlines.local.seen);
    assert(address_budget::state().event_deadlines.first.resource=="CPU");
    setup();tick=100;assert(address_budget::expired("OFF"));
    assert(!address_budget::state().run_deadlines.first.seen);
}
'''
        exe=self.compile('first_deadline',code)
        subprocess.run([str(exe)],check=True,timeout=5)

    def test_absolute_cpu_and_deadline_node_ownership(self):
        code=COMMON+r'''
struct Node{static int alive;Node(){++alive;}~Node(){--alive;}};int Node::alive=0;
int main(){setup(100);tick=0;cputick=9;
  assert(address_budget::expired("CPU"));assert(address_budget::state().global_deadline);
  setup();auto*n=new Node;bool caught=false;
  try{address_budget::owned_dominance(n,[]()->bool{throw address_budget::Deadline{};});}
  catch(const address_budget::Deadline&){caught=true;}assert(caught&&Node::alive==0);
  setup();{address_budget::RepairScope scope(1);tick=2;assert(address_budget::expired("LOCAL"));}
  assert(!address_budget::expired("NEXT"));assert(address_budget::state().repair_deadlines==1);
}
'''
        exe=self.compile('clock',code);self.execute(exe)

    def test_phase_profile_exclusive_scopes_return_and_deadline_unwind(self):
        code=COMMON+r'''
int main(){
    using namespace address_budget;
    setup();configure_profile(1);::tick=1;
    { PhaseScope outer(Phase::PREPROCESS);::tick=2;
      {PhaseScope child(Phase::TOPK);::tick=4;}
      ::tick=5;outer.set(Phase::BETA);::tick=8;
      [](){PhaseScope early(Phase::WALK);::tick=10;return;}();
      ::tick=11;
    }
    ::tick=12;profile_finish();auto& p=state().profile;
    const auto cost=[&](Phase phase){return p.phases[static_cast<size_t>(phase)].wall_ns;};
    assert(p.window_ns==12000000000LL);
    assert(cost(Phase::DRIVER_OTHER)==2000000000LL);
    assert(cost(Phase::PREPROCESS)==2000000000LL);
    assert(cost(Phase::TOPK)==2000000000LL);
    assert(cost(Phase::BETA)==4000000000LL);
    assert(cost(Phase::WALK)==2000000000LL);
    long long sum=0;for(auto c:p.phases)sum+=c.wall_ns;assert(sum==p.window_ns);
    cout<<"{";write_profile(cout);cout<<"}\n";
    setup();configure_profile(1);::tick=1;
    try{PhaseScope scope(Phase::REPAIR);::tick=3;throw Deadline{};}catch(const Deadline&){}
    ::tick=5;profile_finish();assert(state().profile.window_ns==5000000000LL);
    assert(state().profile.phases[static_cast<size_t>(Phase::REPAIR)].wall_ns==2000000000LL);
    assert(state().profile.phases[static_cast<size_t>(Phase::DRIVER_OTHER)].wall_ns==3000000000LL);
}
'''
        exe=self.compile('profile_scopes',code)
        # write_profile appends a comma because it is embedded in a receipt.
        raw=self.execute(exe).replace('{,','{',1)
        row=json.loads(raw)['phase_profile']
        self.assertEqual(row['window_wall_ns'],row['accounted_wall_ns'])
        self.assertEqual(row['residual_wall_ns'],0)
        self.assertEqual(sum(v['wall_ns'] for v in row['phases'].values()),row['window_wall_ns'])

    def test_phase_profile_off_has_no_extra_clock_or_rng_side_effect(self):
        code=COMMON+r'''
int wall_calls=0,cpu_calls=0;
double counted_wall(){++wall_calls;return 0;}
double counted_cpu(){++cpu_calls;return 0;}
int main(){
    using namespace address_budget;
    setup();state().wall=counted_wall;state().cpu=counted_cpu;
    srand(7);const auto expected=rand();srand(7);
    configure_profile(0);
    {PhaseScope outer(Phase::PREPROCESS);outer.set(Phase::TOPK);{PhaseScope child(Phase::REPAIR);}}
    profile_finish();std::ostringstream text;write_profile(text);
    assert(text.str().empty()&&wall_calls==0&&cpu_calls==0&&rand()==expected);
    assert(!expired("OFF"));assert(wall_calls==1&&cpu_calls==1);
    assert(state().profile.expired_calls==0);
    bool rejected=false;try{configure_profile(2);}catch(const std::runtime_error&){rejected=true;}
    assert(rejected&&wall_calls==1&&cpu_calls==1);
}
'''
        self.execute(self.compile('profile_off',code))

    def test_expired_profile_sampling_exact_boundaries_without_extra_cpu_calls(self):
        code=COMMON+r'''
int wall_calls=0,cpu_calls=0;
double counted_wall(){return double(++wall_calls)/1000000;}
double counted_cpu(){++cpu_calls;return 0;}
int main(){
    using namespace address_budget;
    setup();state().wall=counted_wall;state().cpu=counted_cpu;configure_profile(1);
    for(int i=0;i<1023;++i)assert(!expired("SAMPLED"));
    assert(state().profile.expired_samples==0);
    assert(!expired("SAMPLED"));assert(state().profile.expired_samples==1);
    for(int i=1024;i<2050;++i)assert(!expired("SAMPLED"));
    profile_finish();const auto& p=state().profile;
    assert(p.expired_calls==2050&&p.expired_samples==2);
    assert(wall_calls==2056&&cpu_calls==2050);
    const auto& c=p.phases[static_cast<size_t>(Phase::DRIVER_OTHER)];
    assert(c.expired_calls==2050&&c.expired_samples==2);
    assert(c.expired_sampled_wall_ns==p.expired_sampled_wall_ns&&p.expired_sampled_wall_ns>0);
    cout<<"{";write_profile(cout);cout<<"}\n";
}
'''
        row=json.loads(self.execute(self.compile('profile_sampling',code)).replace('{,','{',1))['phase_profile']
        sample=row['expired_sampling']
        self.assertEqual(sample['samples'],sample['calls']//sample['stride'])
        self.assertFalse(sample['extrapolated'])
        self.assertEqual(row['residual_wall_ns'],0)
        from run_address_adapter import verify_phase_profile
        verify_phase_profile({'phase_profile': row, 'inner_wall_before_receipt_s': .01,
                              'group_calls': 0, 'attempt_trace_rows': 0}, {'phase_profile': True})

    def test_profile_generated_anchors_preserve_rng_and_reward(self):
        old=self.base['src/LNS.cpp'].decode();new=self.guarded['src/LNS.cpp'].decode()
        driver=self.guarded['src/driver.cpp'].decode()
        self.assertIn('("phaseProfile", po::value<int>()->default_value(0)',driver)
        self.assertLess(driver.index('configure_profile('),driver.index('Instance instance('))
        self.assertLess(driver.index('budget_preprocess.stop();'),driver.index('bool succ = lns.run();'))
        self.assertIn('Phase::FINAL_CHECK_OUTPUT',driver)
        seed=method(new,'int LNS::bernoulie()')
        self.assertLess(seed.index('Phase::TOPK'),seed.index('std::mt19937 gen(rd());'))
        self.assertLess(seed.index('queue.pop();'),seed.index('Phase::BETA'))
        self.assertLess(seed.index('Phase::BETA'),seed.index('beta_dist(alpha[i], beta[i])'))
        for signature in ('int LNS::bernoulie()','void LNS::randomWalk(',
                          'bool LNS::generateNeighborByRandomWalk(','bool LNS::runPP()'):
            before,after=method(old,signature),method(new,signature)
            # Inserted timers/counters do not add/remove random draws or reorder them.
            import re
            random_lines=lambda src:[line.strip() for line in src.splitlines()
                if re.search(r'\brand\(|\brd\(\)|beta_dist\(gen\)|random_shuffle',line)]
            self.assertEqual(random_lines(before),random_lines(after))
        self.assertIn('a = i;',method(new,'bool LNS::generateNeighborByRandomWalk('))

    def test_profile_actual_group_outcomes_on_fake_graph_and_seed(self):
        for mode in ('formed','no_seed','too_small','deadline'):
            code=loop_fixture(self.guarded['src/LNS.cpp'].decode())
            code=code.replace('#include "address_adapter_support.h"',
                '#include "address_budget_support.h"\ndouble ticks=0;double stepclock(){ticks+=0.001;return ticks;}double zerocpu(){return 0;}')
            code=code.replace('struct Agent { vector<Vertex> path; Planner* path_planner; };',
                'struct Agent { vector<Vertex> path; Planner* path_planner; int getNumOfDelays() const {return int(path.size())-1-path_planner->my_heuristic[path_planner->start_location];} };')
            code=code.replace('int wrapper() { ++generated; return 0; }',
                'int wrapper() { ++generated; if(address_budget::state().profile.active)++address_budget::state().profile.seed_calls; return '+('-1' if mode=='no_seed' else '0')+'; }')
            if mode=='too_small':code=code.replace('agents.insert((a+1)%9);','/* fake graph has no blocker */')
            stop='0.003' if mode=='deadline' else '100'
            code=code.replace('    if(!test.run_fixture())',
                '    auto& budget=address_budget::state();budget.configured=true;budget.wall=stepclock;budget.cpu=zerocpu;budget.wall_stop='+stop+';budget.cpu_limit=10;budget.cpu_reserve=1;address_budget::configure_profile(1);\n    if(!test.run_fixture())')
            code=code.replace('int code=address_adapter::finish();','int code=address_budget::finish();')
            receipt=self.root/('profile_groups_'+mode+'.json')
            self.execute(self.compile('profile_groups_'+mode,code),receipt,'slack')
            native=json.loads(receipt.read_text());profile=native['phase_profile'];counts=profile['counters']
            outcomes=('groups_formed','groups_no_seed','groups_too_small','groups_deadline')
            self.assertEqual(sum(counts[k] for k in outcomes),counts['group_calls'])
            self.assertEqual(counts['group_calls'],native['group_calls'])
            key={'formed':'groups_formed','no_seed':'groups_no_seed','too_small':'groups_too_small','deadline':'groups_deadline'}[mode]
            self.assertGreater(counts[key],0)
            for other in set(outcomes)-{key}:self.assertEqual(counts[other],0)
            self.assertEqual(profile['residual_wall_ns'],0)
            self.assertEqual(counts['seed_zero_delay_selected'],0)
            self.assertLessEqual(counts['seed_positive_delay_selected'],counts['seed_calls'])

    def test_overlay_preserves_author_reward_and_complete_rollback(self):
        old=self.base['src/LNS.cpp'].decode();new=self.guarded['src/LNS.cpp'].decode()
        marker='     if ((destroy_strategy == RANDOMWALK || destroy_strategy == DESTROY_COUNT) && (algo != CANONICAL))'
        reward=old.split(marker)[1].split('    if (remaining_agents == 0')[0]
        self.assertIn(marker+reward,new)
        rollback=old.split('        auto p2 = shuffled_agents.begin();')[1].split('        return false;')[0]
        self.assertIn('        auto p2 = shuffled_agents.begin();'+rollback,new)
        with self.assertRaises(ValueError):adapt(self.guarded)

    def test_actual_heuristic_checkpoint_preserves_prevalidated_fallback(self):
        code=COMMON+r'''
#include <boost/heap/pairing_heap.hpp>
const int MAX_TIMESTEP=10000;
struct Graph {
    int map_size=100,num_of_rows=1,num_of_cols=100;
    vector<int> getNeighbors(int x)const{return x<99?vector<int>{x+1}:vector<int>{};}
    bool isObstacle(int)const{return false;}
    vector<int>getStarts()const{return {0};}vector<int>getGoals()const{return {1};}
    int getRowCoordinate(int)const{return 0;}int getColCoordinate(int x)const{return x;}
};
struct SingleAgentSolver{Graph instance;int goal_location=0;vector<int>my_heuristic;void compute_heuristics();};
'''+method(self.guarded['src/SingleAgentSolver.cpp'].decode(),'void SingleAgentSolver::compute_heuristics()')+r'''
int main(int argc,char**argv){
 setup(8);increment=1;Graph graph;
 auto& a=address_adapter::state();a.total_seconds=5;a.initial_file=argv[1];a.receipt_file=argv[3];
 auto initial=address_budget::prevalidate(graph,1);bool caught=false;
 address_budget::state().preprocessing=true;
 try{SingleAgentSolver solver;solver.compute_heuristics();}
 catch(const address_budget::Deadline&){caught=true;address_budget::state().preprocessing=false;
   address_budget::output_initial(initial,graph,argv[2]);}
 assert(caught);return address_budget::finish();
}
'''
        exe=self.compile('preprocessing',code)
        initial=self.root/'initial.txt';initial.write_text('1\n2 0 1\n')
        output=self.root/'initial_output.txt';receipt=self.root/'initial_receipt.json'
        self.execute(exe,initial,output,receipt)
        self.assertEqual(output.read_text(),'Agent 0:(0,0)->(0,1)->\n')
        value=json.loads(receipt.read_text());self.assertTrue(value['preprocessing_fallback'])
        self.assertTrue(value['initial_and_final_validated']);self.assertEqual(value['final_soc'],1)


class RewardContracts(unittest.TestCase):
    """Actual reward-overlay PP body with the existing fake planner/clock.

    These cases do not construct an author Instance or invoke SIPP.
    """
    @classmethod
    def setUpClass(cls):
        from address_reward import adapt as reward_adapt
        cls.base=sources();cls.base.update(adapt(cls.base))
        cls.changed=reward_adapt(cls.base)
        cls.tmp=tempfile.TemporaryDirectory();cls.root=Path(cls.tmp.name)
        for name,raw in dict(cls.base,**cls.changed).items():
            if name.startswith('inc/address_'):
                (cls.root/Path(name).name).write_bytes(raw)

    @classmethod
    def tearDownClass(cls):cls.tmp.cleanup()

    def compile(self,name,code):
        src=self.root/(name+'.cpp');exe=src.with_suffix('');src.write_text(code)
        result=subprocess.run(['rtk','proxy','g++','-std=c++14','-O0','-I',str(self.root),
                               str(src),'-o',str(exe)],capture_output=True,text=True,timeout=30)
        self.assertEqual(result.returncode,0,result.stderr);return exe

    def execute(self,exe,*args):
        result=subprocess.run(['rtk','proxy',str(exe),*map(str,args)],capture_output=True,text=True,timeout=5)
        self.assertEqual(result.returncode,0,result.stderr)
        return result

    def test_execution_observations_configuration_fails_closed(self):
        code=COMMON+r'''
#include "address_reward_support.h"
int main(int argc,char**argv){
    setup();int mode=atoi(argv[1]);
    if(mode!=1)address_budget::configure_cost_diagnostics(1);
    if(mode==2)address_budget::configure_trace(argv[3]);
    bool refused=false;
    try {address_reward::configure(mode==3?"cumulative":"author",0,1,argv[2],"all",
        mode==4?"unknown":mode==5?"search_then_admission":"legacy",mode==5?0:1);}
    catch(const runtime_error&){refused=true;}
    assert(refused==(mode!=0));return 0;
}
'''
        exe=self.compile('execution_configuration',code)
        for mode in range(6):
            self.execute(exe,mode,self.root/('config_reward'+str(mode)),self.root/('config_attempt'+str(mode)))

    def test_actual_pp_separates_candidate_commit_failure_and_deadline(self):
        code=pp_fixture(self.changed['src/LNS.cpp'].decode())
        code=code.replace('      if(expire_call==-4)', '''      if(expire_call==-5&&calls==3){Path p(6,PathEntry{start_location});p.push_back({start_location+1});p.push_back({start_location+2});return p;}
      if(expire_call==-6&&calls==3)return {{start_location},{start_location+1},{start_location}};
      if(expire_call==-4)''')
        code=code.replace('    bool accepted=test.runPP();', '''    address_reward::configure("cumulative",0,3,argv[3]);
    test.alpha.assign(3,1);test.beta.assign(3,1);
    address_reward::SelectionScope selection(9);address_reward::bind_seed(0);
    bool accepted=false;
    try{accepted=test.runPP();}catch(const runtime_error&){
        assert(expire_call==-6);assert(!address_reward::state().active);
        for(int a=0;a<3;++a)assert(test.path_table.paths.at(a).size()==4);
        assert(test.alpha[0]==1&&test.beta[0]==1);return 0;
    }
    assert(test.alpha[0]==(expire_call?1:2));
    assert(test.beta[0]==((expire_call<0)?2:1));''')
        # argv[3] is the new event trace, not the older per-repair trace.
        code=code.replace('    if(argc>3)address_budget::configure_trace(argv[3]);','')
        exe=self.compile('reward_pp',code)
        for mode in (0,1,3,-2,-4,-5,-6):
            receipt=self.root/('reward_native'+str(mode)+'.json')
            trace=self.root/('reward_pp'+str(mode)+'.jsonl')
            self.execute(exe,mode,receipt,trace)
            rows=[json.loads(line) for line in trace.read_text().splitlines()]
            self.assertEqual(len(rows),1)
            row=rows[0];self.assertEqual(row['selection_id'],1)
            self.assertEqual(row['repair_attempt_id'],1)
            self.assertEqual(row['committed_gain'],3 if mode==0 else 0)
            self.assertEqual(row['candidate_reward'],{0:3,-4:0,-5:-2}.get(mode))
            self.assertEqual(row['censored'],mode in (1,3))
            if row['censored']:
                self.assertTrue(row['global_deadline'] or row['local_deadline'])
                self.assertNotEqual(row['deadline_stage'],'NONE')
            self.assertEqual(row['memory_eligible'],mode not in (1,3,-6))
            if mode!=-6:
                native=json.loads(receipt.read_text())
                self.assertTrue(native['initial_and_final_validated'])
                self.assertEqual(native['reward_contract']['selections'],native['reward_contract']['settlements'])

    def test_cost_diagnostics_actual_pp_deadline_unwind_and_external_validation(self):
        from reward_analysis import verify_reward_trace
        code=pp_fixture(self.changed['src/LNS.cpp'].decode())
        code=code.replace('double fake_cpu(){return cputick;}',
                          'double fake_cpu(){cputick+=0.000001;return cputick;}')
        code=code.replace('bool isObstacle(int)const{return false;}',
                          'bool isObstacle(int)const{if(expire_call==-7)tick=100;return false;}')
        code=code.replace('vector<int>getStarts()const{return {0,5,10};}',
                          'vector<int>getStarts()const{if(expire_call==-8)tick=100;return {0,5,10};}')
        code=code.replace('    if(argc>3)address_budget::configure_trace(argv[3]);','')
        code=code.replace('    bool accepted=test.runPP();', '''    increment=0.000001;
    address_budget::configure_cost_diagnostics(1);
    address_reward::configure("cumulative",0,3,argv[3]);
    address_budget::state().group_calls=1; // Fixture enters runPP directly, bypassing group wrapper.
    test.alpha.assign(3,1);test.beta.assign(3,1);
    address_reward::SelectionScope selection(9);address_reward::bind_seed(0);
    address_reward::seed_pool_completed(3);
    bool accepted=test.runPP();''')
        exe=self.compile('reward_cost_pp',code)
        for mode in (0,1,3,-2,-4,-7,-8):
            native_path=self.root/('cost_native'+str(mode)+'.json')
            trace=self.root/('cost_pp'+str(mode)+'.jsonl')
            self.execute(exe,mode,native_path,trace)
            native=json.loads(native_path.read_text())
            raw=trace.read_bytes();row=json.loads(raw);d=row['cost_diagnostics']
            verify_reward_trace(raw,native,dict(reward_memory='cumulative',reward_window=0),3,True)
            self.assertEqual(d['eligible_topk_candidates'],3)
            self.assertTrue(d['seed_pool_completed'])
            self.assertGreater(d['post_search_through_settlement_wall_ns'],0)
            self.assertGreater(d['post_search_through_settlement_cpu_ns'],0)
            if mode in (0,3,-4,-7,-8):
                self.assertGreater(d['candidate_validation_wall_ns'],0)
                self.assertGreater(d['candidate_validation_cpu_ns'],0)
            else:
                self.assertEqual(d['candidate_validation_wall_ns'],0)
            if mode in (1,3):
                self.assertEqual(d['first_observed_deadline']['stage'],'SIPP_RETURN')
            if mode in (-7,-8):
                self.assertEqual(d['validation_result'],'DEADLINE')
                self.assertEqual(d['first_observed_deadline']['stage'],
                                 'REWARD_VALIDATION_MAP' if mode==-7 else 'REWARD_VALIDATION_JOINT')
                self.assertFalse(row['candidate_validated'])
                self.assertEqual(row['committed_gain'],0)
            # No double billing or fabricated complete pool can pass the validator.
            for key,value in (('post_search_other_wall_ns',d['post_search_other_wall_ns']+1),
                              ('eligible_topk_candidates',None)):
                bad=dict(row,cost_diagnostics=dict(d,**{key:value}))
                with self.assertRaises(ValueError):
                    verify_reward_trace((json.dumps(bad)+'\n').encode(),native,
                                        dict(reward_memory='cumulative',reward_window=0),3,True)

    def test_cost_diagnostic_completed_seed_pool_and_interrupted_pool_unknown(self):
        from reward_analysis import verify_event_cost
        code=seed_fixture(self.changed['src/LNS.cpp'].decode()).split('int main(int argc,char**argv){')[0]+r'''
int main(int argc,char**argv){
    setup(1000);address_budget::configure_cost_diagnostics(1);
    address_budget::configure_seed_admission("positive_delay");
    address_reward::configure("cumulative",0,9,argv[2]);LNS x;
    x.agents[1].path={{0},{0},{1}};x.agents[3].path={{0},{0},{1}};
    if(string(argv[1])=="deadline"){increment=1;address_budget::state().wall_stop=4;}
    address_reward::SelectionScope selection(11);
    x.bernoulie();address_reward::no_repair("GROUP_TOO_SMALL",x.alpha,x.beta);
}
'''
        exe=self.compile('reward_seed_pool',code)
        for mode in ('complete','deadline'):
            trace=self.root/('cost_seed_'+mode+'.jsonl');self.execute(exe,mode,trace)
            row=json.loads(trace.read_bytes());d=verify_event_cost(row)
            self.assertEqual(d['seed_pool_completed'],mode=='complete')
            self.assertEqual(d['eligible_topk_candidates'],2 if mode=='complete' else None)
            if mode=='deadline':self.assertEqual(d['first_observed_deadline']['stage'],'GROUP_SEED')

    def test_acceptance_gate_actual_pp_keeps_author_update_rollback_and_final_check(self):
        from reward_analysis import verify_reward_trace
        code=pp_fixture(self.changed['src/LNS.cpp'].decode())
        code=code.replace('int calls=0,expire_call=0;', 'int calls=0,expire_call=0,materializations=0;')
        code=code.replace('bool isObstacle(int)const{return false;}',
                          'bool isObstacle(int)const{++materializations;return false;}')
        code=code.replace('      if(expire_call==-4)', '''      if(expire_call==-5&&calls==3){Path p(6,PathEntry{start_location});p.push_back({start_location+1});p.push_back({start_location+2});return p;}
      if(expire_call==-6&&calls==3)return {{start_location},{start_location+1},{start_location}};
      if(expire_call==-4)''')
        code=code.replace('    if(argc>3)address_budget::configure_trace(argv[3]);','')
        code=code.replace('    bool accepted=test.runPP();', '''    increment=0.000001;
    address_budget::configure_cost_diagnostics(1);
    address_reward::configure("author",0,3,argv[3],argv[4]);
    address_budget::state().group_calls=1;
    vector<int> q(3,9),freq(3,1);test.q_values=&q;test.frequency=&freq;test.current_index=0;
    test.alpha.assign(3,1);test.beta.assign(3,1);
    address_reward::SelectionScope selection(9);address_reward::bind_seed(0);address_reward::seed_pool_completed(3);
    bool accepted=false,invalid=false;
    try{accepted=test.runPP();}catch(const runtime_error&){invalid=true;assert(expire_call==-6);}
    assert(!address_reward::state().active);
    assert(test.alpha[0]==((expire_call==-4||expire_call==-5)?1:2));
    assert(test.beta[0]==((expire_call==-4||expire_call==-5)?2:1));
    bool duplicate=false;try{address_reward::settle(false,9,"DUPLICATE",test.alpha,test.beta);}
    catch(const runtime_error&){duplicate=true;}assert(duplicate);
    const bool gate=string(argv[4])=="acceptance_eligible";
    if(gate&&(expire_call==-4||expire_call==-5))assert(materializations==0);
    if(!gate&&(expire_call==-4||expire_call==-5))assert(materializations==15);
    if(invalid){for(int a=0;a<3;++a)assert(test.path_table.paths.at(a).size()==4);return 0;}
''')
        exe=self.compile('acceptance_gate_pp',code)
        for policy in ('all','acceptance_eligible'):
            for mode in (0,-4,-5,-2,1,3,-6):
                with self.subTest(policy=policy,mode=mode):
                    native_path=self.root/f'gate_native_{policy}_{mode}.json'
                    trace=self.root/f'gate_pp_{policy}_{mode}.jsonl'
                    self.execute(exe,mode,native_path,trace,policy)
                    raw=trace.read_bytes();row=json.loads(raw)
                    self.assertEqual(row['committed_gain'],3 if mode==0 else 0)
                    if mode==-6:
                        self.assertEqual(row['outcome'],'INVALID_CANDIDATE')
                        self.assertFalse(row['candidate_validated'])
                        continue
                    native=json.loads(native_path.read_text())
                    self.assertTrue(native['initial_and_final_validated'])
                    summary=verify_reward_trace(raw,native,dict(reward_memory='author',reward_window=0,
                        candidate_validation_policy=policy),3,True)
                    self.assertEqual(summary['selections'],1)
                    if policy=='all':
                        self.assertNotIn('candidate_validation_policy',row)
                        self.assertEqual(row['candidate_reward'],{0:3,-4:0,-5:-2}.get(mode))
                    else:
                        p=row['candidate_validation_policy'];d=row['cost_diagnostics']
                        skipped=mode in (-4,-5)
                        self.assertEqual(p['result']=='SKIPPED_ACCEPTANCE_INELIGIBLE',skipped)
                        if skipped:
                            self.assertIsNone(row['candidate_reward']);self.assertIsNone(row['candidate_subset_soc'])
                            self.assertFalse(row['candidate_validated']);self.assertEqual(p['remaining_agents'],1)
                            self.assertEqual(d['candidate_materialization_wall_ns'],0)
                            self.assertEqual(d['candidate_joint_check_wall_ns'],0)
                            self.assertEqual(row['bernoulli_reward'],0)
                            bad=dict(row,candidate_validation_policy=dict(p,remaining_agents=0,
                                fresh_cost_sum_unvalidated=row['old_subset_soc'],skip_reason='COST_EXCEEDS_OLD'))
                            with self.assertRaises(ValueError):
                                verify_reward_trace((json.dumps(bad)+'\n').encode(),native,
                                    dict(reward_memory='author',reward_window=0,candidate_validation_policy=policy),3,True)
                        if mode==3:
                            self.assertEqual(p['result'],'DEADLINE')
                            self.assertEqual(d['first_observed_deadline']['stage'],'SIPP_RETURN')

    def test_shared_budget_actual_pp_closes_search_before_global_admission(self):
        from reward_analysis import verify_reward_trace
        code=pp_fixture(self.changed['src/LNS.cpp'].decode()).split('int main(int argc,char**argv){')[0]
        code=code.replace('      if(calls==expire_call)tick=100;',
                          '      if(expire_call==4&&calls==3)tick=2;')
        code=code.replace('bool isObstacle(int)const{return false;}', '''bool isObstacle(int)const{
            if(expire_call==1)tick=2;
            if(expire_call==2)tick=100;
            if(expire_call==3)cputick=9;
            return false;
        }''')
        # Place the fake crossing exactly between the old snapshot and the
        # existing PRIMARY_DONE checkpoint, not in a replacement search loop.
        code=code.replace('    budget_attempt.primary_done(remaining_agents,int(p-shuffled_agents.begin()));',
            '    if(expire_call==5)tick=2;\n    budget_attempt.primary_done(remaining_agents,int(p-shuffled_agents.begin()));')
        code=code.replace('    if (address_reward::admissible() && !address_budget::expired("ACCEPT")',
            '    if(expire_call==6)tick=100;\n    if (address_reward::admissible() && !address_budget::expired("ACCEPT")')
        code+=r'''
int main(int argc,char**argv){
    setup();expire_call=atoi(argv[1]);LNS test;test.replan_time_limit=1;
    address_budget::configure_cost_diagnostics(1);
    address_reward::configure("author",0,3,argv[3],argv[4],argv[5],1);
    address_budget::state().group_calls=1;
    vector<int> q(3,9),freq(3,1);test.q_values=&q;test.frequency=&freq;test.current_index=0;
    test.alpha.assign(3,1);test.beta.assign(3,1);
    address_adapter::Paths initial;
    for(const auto& a:test.agents){initial.emplace_back();for(const auto& x:a.path)initial.back().push_back(x.location);}
    address_reward::initialize_plan_identity(initial);
    address_reward::SelectionScope selection(9);address_reward::bind_seed(0);address_reward::seed_pool_completed(3);
    const bool accepted=test.runPP();
    const bool expected=expire_call==0||(expire_call==1&&string(argv[5])=="search_then_admission");
    assert(accepted==expected);assert(test.neighbor.sum_of_costs==(expected?6:9));
    assert(test.alpha[0]==(expire_call==-4?1:2));assert(test.beta[0]==(expire_call==-4?2:1));
    auto& a=address_adapter::state();a.initial_soc=9;a.initial_validated=true;a.total_seconds=5;a.receipt_file=argv[2];
    address_adapter::check_final(test.agents,test.instance,test.neighbor.sum_of_costs);
    assert(a.final_validated);return address_budget::finish();
}
'''
        exe=self.compile('shared_budget_pp',code)
        initial=[[s,s,s+1,s+2] for s in (0,5,10)]
        for contract in ('legacy','search_then_admission'):
            for policy in ('all','acceptance_eligible'):
                for mode in (0,1,2,3,4,5,6,-4,-2):
                    with self.subTest(contract=contract,policy=policy,mode=mode):
                        native_path=self.root/f'common_native_{contract}_{policy}_{mode}.json'
                        trace=self.root/f'common_pp_{contract}_{policy}_{mode}.jsonl'
                        self.execute(exe,mode,native_path,trace,policy,contract)
                        row=json.loads(trace.read_bytes());native=json.loads(native_path.read_bytes())
                        accepted=mode==0 or (mode==1 and contract=='search_then_admission')
                        final=[[s,s+1,s+2] for s in (0,5,10)] if accepted else initial
                        job=dict(reward_memory='author',reward_window=0,candidate_validation_policy=policy,
                                 repair_budget_contract=contract)
                        verify_reward_trace(trace.read_bytes(),native,job,3,True,initial,final)
                        self.assertEqual(row['accepted'],accepted)
                        o=row['execution_observations'];search=o['search_return']
                        self.assertEqual(search['local_scope_released'],contract=='search_then_admission')
                        self.assertEqual(o['author_update']['positive_predicate'],mode!=-4)
                        if contract=='search_then_admission' and mode in (4,5):
                            self.assertTrue(search['search_censored'])
                            self.assertTrue(row['local_deadline'])
                            self.assertFalse(row['candidate_validated'])
                            self.assertEqual(row['cost_diagnostics']['validation_result'],'SEARCH_CENSORED')
                        if mode==6:
                            self.assertTrue(row['candidate_validated'])
                            self.assertTrue(row['global_deadline'])
                            self.assertEqual(o['plan_identity']['revision_after'],0)
                        # A signed time margin is an observation, not an excuse
                        # to erase an actual expiry or fabricate a posterior.
                        bad=json.loads(trace.read_bytes())
                        bad['execution_observations']['author_update']['alpha_after']+=1
                        with self.assertRaises(ValueError):
                            verify_reward_trace((json.dumps(bad)+'\n').encode(),native,job,3,True,initial,final)
                        with self.assertRaises(ValueError):
                            verify_reward_trace(trace.read_bytes(),native,job,3,True)

    def test_acceptance_gate_uses_nonstrict_original_cost_condition(self):
        code=COMMON+r'''
struct Agent {Path path;};
struct Graph {
    int map_size=3,num_of_rows=1,num_of_cols=3;
    bool isObstacle(int)const{return false;}
    vector<int>getStarts()const{return {0};}vector<int>getGoals()const{return {2};}
};
int main(int argc,char**argv){
    setup();address_reward::configure("author",0,1,argv[1],"acceptance_eligible");
    address_budget::state().attempts=1;
    vector<int>alpha(1,1),beta(1,1);vector<Agent>agents{{{{0},{1},{2}}}};Graph graph;
    address_reward::SelectionScope selection(2);address_reward::bind_seed(0);
    address_reward::group(1,2);address_reward::found(2);
    address_reward::inspect_candidate(agents,graph,0);
    assert(address_reward::admissible());assert(address_reward::pending().candidate==2);
    address_reward::settle(true,2,"FOUND",alpha,beta);
}
'''
        trace=self.root/'gate_equal_acceptance_condition.jsonl'
        self.execute(self.compile('gate_equal_condition',code),trace)
        row=json.loads(trace.read_bytes())
        self.assertTrue(row['candidate_validated']);self.assertTrue(row['accepted'])
        self.assertEqual(row['candidate_reward'],0)
        self.assertEqual(row['candidate_validation_policy']['result'],'VALIDATED')

    def test_shared_memory_rule_empty_groups_censoring_and_exactly_once(self):
        code=COMMON+r'''
int main(int argc,char**argv){
    setup();string mode=argv[1];int width=atoi(argv[2]);
    address_reward::configure(mode,width,2,argv[3]);
    vector<int> alpha(2,1),beta(2,1);
    for(bool win:{true,false,false,true}){
        address_reward::SelectionScope selection(10);address_reward::bind_seed(0);
        if(win){address_reward::group(1,5);auto&e=address_reward::pending();
            e.candidate=4;e.candidate_valid=true;address_reward::settle(true,4,"FOUND",alpha,beta);}
        else address_reward::no_repair("GROUP_TOO_SMALL",alpha,beta);
        bool duplicate=false;try{address_reward::no_repair("DUPLICATE",alpha,beta);}
        catch(const runtime_error&){duplicate=true;}assert(duplicate);
    }
    auto expected_a=alpha,expected_b=beta;
    {address_reward::SelectionScope selection(9);address_reward::bind_seed(0);
     address_budget::state().global_deadline=true;address_reward::no_repair("DEADLINE",alpha,beta);}
    assert(alpha==expected_a&&beta==expected_b);
    address_budget::state().global_deadline=false;
    {address_reward::SelectionScope selection(9);address_reward::no_repair("NO_SEED",alpha,beta);}
    assert(alpha==expected_a&&beta==expected_b);
    assert(address_reward::state().started==6&&address_reward::state().settled==6);
    assert(address_reward::state().arms[0].completed==4&&address_reward::state().arms[0].censored==1);
    assert(address_reward::state().arms[1].completed==0);
    if(mode=="window"&&width==2)assert(alpha[0]==2&&beta[0]==2);
    else if(mode=="author")assert(alpha[0]==1&&beta[0]==1);
    else assert(alpha[0]==3&&beta[0]==3);
    // An unclosed selection is an error event, never an implicit reward zero.
    {address_reward::SelectionScope incomplete(9);}
    assert(address_reward::state().errors==1);
    bool rejected=false;try{ostringstream out;address_reward::summary(out);}catch(const runtime_error&){rejected=true;}
    assert(rejected);
}
'''
        exe=self.compile('reward_memory',code)
        outputs={}
        for mode,width in (('cumulative',0),('window',2),('window',4),('author',0)):
            path=self.root/(mode+str(width)+'.jsonl');self.execute(exe,mode,width,path)
            outputs[mode,width]=[json.loads(line) for line in path.read_text().splitlines()]
        # Memory alone changes retained counts; event rewards and costs match.
        self.assertEqual(outputs['cumulative',0],outputs['window',4])
        self.assertEqual(outputs['cumulative',0],outputs['window',2])
        self.assertIsNone(outputs['window',2][-1]['committed_gain'])

    def test_overlay_connections_preserve_old_build_and_reject_duplicate(self):
        from address_reward import adapt as reward_adapt
        with self.assertRaises(ValueError):reward_adapt(dict(self.base,**self.changed))
        old=method(self.base['src/LNS.cpp'].decode(),'bool LNS::runPP()')
        new=method(self.changed['src/LNS.cpp'].decode(),'bool LNS::runPP()')
        marker='     if ((destroy_strategy == RANDOMWALK || destroy_strategy == DESTROY_COUNT) && (algo != CANONICAL))'
        original=old[old.index(marker):old.index('    if (!address_budget::expired("ACCEPT")')]
        self.assertIn('if(address_reward::author()) {\n'+original,new)
        run=method(self.changed['src/LNS.cpp'].decode(),'bool LNS::run()')
        self.assertEqual(run.count('SelectionScope reward_selection'),1)
        self.assertEqual(run.count('address_reward::no_repair'),2)
        self.assertEqual(new.count('address_reward::settle('),2)
        self.assertLess(new.index('budget_attempt.end_rollback()'),new.index('address_reward::settle(false'))
        self.assertNotIn('address_reward',self.base['src/LNS.cpp'].decode())

    def test_actual_outer_loop_settles_failed_group_and_formed_deadline(self):
        code=loop_fixture(self.changed['src/LNS.cpp'].decode())
        code=COMMON+code.replace('#include "address_adapter_support.h"','')
        # Existing fixture declarations use different path/clock types.
        code=code.replace('struct PathEntry { int location;PathEntry(int x):location(x){};PathEntry():location(0){}; };\nusing Path=vector<PathEntry>;','')
        code=code.replace('struct Agent { vector<Vertex> path; Planner* path_planner; };',
            'struct Agent { vector<Vertex> path; Planner* path_planner; int getNumOfDelays()const{return int(path.size())-1-path_planner->my_heuristic[path_planner->start_location];} };')
        code=code.replace('    int wrapper() { ++generated; return 0; }',
            '    vector<int> alpha=vector<int>(9,1),beta=vector<int>(9,1);\n    int wrapper() { ++generated; address_reward::bind_seed(0); return 0; }')
        code=code.replace('    srand(0); LNS test(argc>2);', '''    setup(1);increment=.01;
    address_reward::configure("cumulative",0,9,argv[2]);
    srand(0); LNS test(true);''')
        # Exercise actual failed-construct control flow; graph yields no neighbor.
        code=code.replace('++calls; agents.insert((a+1)%9);','++calls;')
        code=code.replace('int code=address_adapter::finish();','int code=address_budget::finish();')
        exe=self.compile('reward_loop_no_group',code)
        receipt=self.root/'loop_no_group.json';trace=self.root/'loop_no_group.jsonl'
        self.execute(exe,receipt,trace)
        rows=[json.loads(line) for line in trace.read_text().splitlines()]
        self.assertTrue(rows)
        self.assertEqual([r['selection_id'] for r in rows],list(range(1,len(rows)+1)))
        self.assertTrue(all(r['committed_gain']==0 for r in rows))
        self.assertTrue(all(r['outcome'] in ('NO_GROUP','CENSORED') for r in rows))
        self.assertEqual(json.loads(receipt.read_text())['reward_contract']['settlements'],len(rows))
        # Formed group crosses the global cutoff immediately after generation;
        # the real outer admission branch must settle before break, with no PP.
        formed=code.replace('++calls;', '++calls; agents.insert((a+1)%9);')
        formed=formed.replace('        if(address_budget::expired("GROUP")) {\n            address_reward::no_repair',
            '        ::tick=100;\n        if(address_budget::expired("GROUP")) {\n            address_reward::no_repair')
        formed=formed.replace('setup(1);increment=.01;', 'setup(100);increment=0;')
        exe=self.compile('reward_loop_formed_deadline',formed)
        receipt=self.root/'loop_formed.json';trace=self.root/'loop_formed.jsonl';self.execute(exe,receipt,trace)
        row=json.loads(trace.read_text())
        self.assertEqual(row['outcome'],'CENSORED');self.assertEqual(row['stop'],'GROUP_ADMISSION_DEADLINE')
        self.assertFalse(row['memory_eligible']);self.assertEqual(row['fresh_paths'],0)


if __name__=='__main__':unittest.main()
