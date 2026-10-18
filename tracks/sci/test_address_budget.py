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
from test_address_loop_guard import fixture as loop_fixture

HERE=Path(__file__).resolve().parent


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


if __name__=='__main__':unittest.main()
