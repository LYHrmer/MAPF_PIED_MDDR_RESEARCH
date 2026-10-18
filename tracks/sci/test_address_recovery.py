"""Native recovery software contracts only; never constructs a solver/Instance."""
from pathlib import Path
import subprocess
import tempfile
import unittest
import json

from address_adapter import adapt as base_adapt
from address_loop_guard import adapt as loop_adapt
from address_recovery import adapt
from address_budget import adapt as budget_adapt
from build_address_full import source_identity

HERE=Path(__file__).resolve().parent
AUTHOR=Path('/home/lyh/.cache/mapf_research/address-b3d35c4')


def sources():
    pins=source_identity(AUTHOR)
    files={name:(AUTHOR/name).read_bytes() for name in pins}
    files.update(base_adapt(files));files.update(loop_adapt(files))
    return files


class RecoveryContract(unittest.TestCase):
    def test_overlay_preserves_primary_reward_and_rollback(self):
        files=sources();files.update(budget_adapt(files));changed=adapt(files)
        original=sources()['src/LNS.cpp'].decode();new=changed['src/LNS.cpp'].decode()
        marker='     if ((destroy_strategy == RANDOMWALK || destroy_strategy == DESTROY_COUNT) && (algo != CANONICAL))'
        reward=original.split(marker)[1].split('    if (remaining_agents == 0')[0]
        self.assertIn(marker+reward,new)
        rollback=original.split('        auto p2 = shuffled_agents.begin();')[1].split('        return false;')[0]
        self.assertIn('        auto p2 = shuffled_agents.begin();'+rollback,new)
        self.assertIn('FOCAL_DRAINED_EMPTY',files['src/SIPP.cpp'].decode())
        self.assertNotIn('length_max =',files['src/SIPP.cpp'].decode())
        with self.assertRaises(ValueError):
            adapt({**files,'src/driver.cpp':b'int main(){}'})

    def test_native_fake_callback_mechanism(self):
        code=r'''
#include "address_recovery_support.h"
#include "address_adapter_support.h"
#include <cassert>
using namespace address_recovery;
long long fake_now=0;double fake_cpu=0;
double wall(){return double(fake_now);}double cpu(){return fake_cpu;}
void reset(){fake_now=0;fake_cpu=0;auto& b=address_budget::state();b=address_budget::State{};b.configured=true;b.wall=wall;b.cpu=cpu;b.wall_stop=1000;b.cpu_limit=10;b.cpu_reserve=1;}
int main() {
    reset();
    Context c;
    c.incumbent={{15,15,15,16,17},{0,0,0,1,2},{10,10,10,11},{4,3,2,7,12}};
    c.primary={{15,16,17},{0,1,2},{10,11},{}};
    c.order={0,1,2,3};c.failed_position=3;c.old_group_cost=15;c.primary_calls=4;
    c.stop=Stop::FOCAL_DRAINED_EMPTY;
    Paths good={{15,16,17},{0,0,0,1,2},{10,11},{4,3,2,7,12}};
    auto validate=[&](const Paths& p,bool complete) {
        address_adapter::Paths chosen;std::vector<int> starts,goals;
        for(size_t a=0;a<p.size();++a) {
            if(p[a].empty()) {if(complete)throw std::runtime_error("incomplete");continue;}
            chosen.push_back(p[a]);starts.push_back(c.incumbent[a].front());goals.push_back(c.incumbent[a].back());
        }
        if(!chosen.empty()) address_adapter::validate(chosen,4,5,std::vector<bool>(20,false),starts,goals);
    };
    long long& now=fake_now;int calls=0;std::mt19937 rng(4);
    auto clock=[&](){return now;};
    auto search=[&](int a,const Paths& partial){++calls;return Reply{Stop::FOUND,good[a]};};
    auto anchor=recover(c,Policy::ANCHOR,8,rng,search,validate,clock);
    assert(anchor.accepted && calls==2 && anchor.trace.kept==1 && anchor.trace.tail==2);
    assert(anchor.paths==good && anchor.order==std::vector<int>({0,3,1,2}));
    assert(anchor.trace.blocking_prefix_agents==std::vector<int>({1}));
    assert(c.primary[1]==std::vector<int>({0,1,2})); // input transaction untouched
    calls=0;auto abandoned=recover(c,Policy::ABANDON,8,rng,search,validate,clock);
    assert(!abandoned.accepted && calls==0 && abandoned.trace.decision=="ABANDON_NO_DIAGNOSIS");
    calls=0;auto random=recover(c,Policy::RANDOM,8,rng,search,validate,clock);
    assert(random.accepted && calls==4 && random.paths==good);
    assert(random.trace.partial_checks>=abandoned.trace.partial_checks);
    calls=0;assert(!recover(c,Policy::ANCHOR,1,rng,search,validate,clock).accepted && calls==0);
    for(auto stop:{Stop::UNKNOWN,Stop::DEADLINE,Stop::COST_STOP,Stop::EMPTY_UNCLASSIFIED,Stop::START_BLOCKED}) {
        c.stop=stop;calls=0;assert(!recover(c,Policy::ANCHOR,8,rng,search,validate,clock).accepted && calls==0);
    }
    c.stop=Stop::FOCAL_DRAINED_EMPTY;
    auto late=[&](int a,const Paths& p){++calls;now=1001;return Reply{Stop::FOUND,good[a]};};
    calls=0;auto late_result=recover(c,Policy::ANCHOR,8,rng,late,validate,clock);
    assert(!late_result.accepted && calls==1 && late_result.trace.decision=="DEADLINE");
    reset();
    auto prep_expired=[&](int a,const Paths& p){now=1001;return Reply{Stop::DEADLINE,{},false};};
    auto prep_result=recover(c,Policy::ANCHOR,8,rng,prep_expired,validate,clock);
    assert(!prep_result.accepted && prep_result.trace.extra_requests==1 && prep_result.trace.extra_calls==0);
    reset();
    auto empty=[&](int a,const Paths& p){return Reply{Stop::FOCAL_DRAINED_EMPTY,{}};};
    assert(!recover(c,Policy::ANCHOR,8,rng,empty,validate,clock).accepted);
    assert(classify(true,true,NativeEnd::FOCAL_DRAINED_EMPTY)==Stop::DEADLINE);
    assert(classify(false,true,NativeEnd::FOUND)==Stop::DEADLINE);
    assert(classify(true,false,NativeEnd::UNKNOWN)==Stop::EMPTY_UNCLASSIFIED);
    assert(conflict({0,1},{4,3,2,1})); // late goal occupancy
    assert(conflict({0,1},{1,0})); // opposing edge
    assert(!conflict({0,1},{4,3}));
    reset();auto malformed=c;malformed.old_group_cost=16;bool threw=false;
    try {recover(malformed,Policy::ANCHOR,8,rng,search,validate,clock);}
    catch(const std::runtime_error&){threw=true;}assert(threw);
}
'''
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);(root/'contract.cpp').write_text(code)
            subprocess.run(['g++','-std=c++14','-O0','-I',str(HERE),str(root/'contract.cpp'),
                            '-o',str(root/'contract')],check=True,capture_output=True,timeout=30)
            subprocess.run([str(root/'contract')],check=True,capture_output=True,timeout=5)

    def test_real_overlay_translation_units_compile_without_execution(self):
        files=sources();files.update(budget_adapt(files));files.update(adapt(files))
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            for name,raw in files.items():
                target=root/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
            includes=['-I'+str(root/'inc'),'-I'+str(root/'inc/CBS'),'-I'+str(root/'inc/PIBT'),'-I/usr/include/eigen3']
            for name in ('src/LNS.cpp','src/SIPP.cpp','src/driver.cpp'):
                result=subprocess.run(['g++','-std=c++14','-fsyntax-only',*includes,str(root/name)],
                                      capture_output=True,text=True,timeout=30)
                self.assertEqual(result.returncode,0,result.stderr)

    def test_actual_runpp_private_commit_reverse_swap_and_abandon(self):
        from test_address_budget import pp_fixture
        files=sources();files.update(budget_adapt(files));files.update(adapt(files))
        code=pp_fixture(files['src/LNS.cpp'].decode())
        code='#include "address_recovery_support.h"\n'+code
        begin=code.index('struct Planner {');end=code.index('struct Agent {',begin)
        code=code[:begin]+r'''
vector<vector<int>> oldpaths{{15,15,15,16,17},{0,0,0,1,2},{10,10,10,11},{4,3,2,7,12}};
vector<vector<int>> primary{{15,16,17},{0,1,2},{10,11},{}};
vector<vector<int>> good{{15,16,17},{0,0,0,1,2},{10,11},{4,3,2,7,12}};
int swap_expiry=0,swaps=0,fixture_mode=0,inserts=0;
struct Planner {
 int start_location=0,id=0;vector<int>my_heuristic{0};
 template<class T>Path findPath(const T&){++calls;++address_budget::state().sipp_calls;
   const auto& selected=calls<=4?primary[id]:good[id];Path p;for(int x:selected)p.emplace_back(x);
   address_budget::state().last_sipp_end=p.empty()?"FOCAL_DRAINED_EMPTY":"FOUND";return p;}
};
'''+code[end:]
        code=code.replace('    map<int,Path> paths;',r'''
    struct Store:map<int,Path>{void swap(Store&other){map<int,Path>::swap(other);if(swap_expiry&&swaps++==0)tick=100;}};
    Store table;Store&paths=table;vector<int>goals;int makespan=0;
    explicit FakeTable(int=0){}
''')
        code=code.replace('struct ConstraintTable {','using PathTable=FakeTable;\nstruct ConstraintTable {')
        code=code.replace('paths[a]=p;',r'''paths[a]=p;if(address_budget::state().recovery_active){++inserts;
          if((fixture_mode==3&&inserts==2)||(fixture_mode==4&&inserts==7)){tick=100;address_budget::checkpoint("FIXTURE_TABLE");}}''')
        code=code.replace('map_size=15,num_of_rows=3,num_of_cols=5','map_size=20,num_of_rows=4,num_of_cols=5')
        code=code.replace('return {0,5,10};','return {15,0,10,4};').replace('return {2,7,12};','return {17,2,11,12};')
        code=code.replace('sum_of_costs=9','sum_of_costs=15').replace('old_sum_of_costs=9','old_sum_of_costs=15')
        code=code.replace('vector<int>agents{0,1,2}','vector<int>agents{0,1,2,3}')
        start=code.index('    LNS(){');end=code.index('    bool runPP();',start)
        code=code[:start]+r'''
    LNS(){planners.resize(4);for(int i=0;i<4;++i){planners[i].id=i;planners[i].start_location=oldpaths[i][0];Path p;for(int x:oldpaths[i])p.emplace_back(x);agents.push_back({i,p,&planners[i]});neighbor.old_paths.push_back(p);}}
'''+code[end:]
        # The software fixture fixes the order; native ADDRESS keeps its RNG unchanged.
        code=code.replace('std::random_shuffle(shuffled_agents.begin(), shuffled_agents.end());','/* fixed fixture order */')
        code=code.replace('    if (!address_budget::expired("ACCEPT")',
            '    if(fixture_mode==5)tick=100; // fake clock advances after completed recovery swap\n    if (!address_budget::expired("ACCEPT")')
        code=code.replace('[](){address_budget::checkpoint("RECOVERY_VALIDATE");}',
            '[&](){if(fixture_mode==6 && complete && calls==6)cputick=9;address_budget::checkpoint("RECOVERY_VALIDATE");}')
        code=code.replace('    const auto recovery_hook_begin=address_budget::tick();',
            '    const auto recovery_hook_begin=address_budget::tick();\n    if(fixture_mode==7)cputick=9;')
        code=code[:code.index('int main(int argc,char**argv)')]+r'''
int main(int argc,char**argv){
 setup();int mode=atoi(argv[1]);fixture_mode=mode;swap_expiry=mode==2;
 address_budget::configure_trace(argv[3]);address_recovery::configure(mode==1?"abandon":"anchor",8,0,argv[4]);
 LNS test;bool accepted=test.runPP();assert(accepted==(mode==0));
 assert(test.neighbor.sum_of_costs==(mode==0?11:15));assert(test.path_table.paths.size()==4);
 if(mode!=0)for(int a=0;a<4;++a){assert(test.agents[a].path.size()==oldpaths[a].size());for(size_t i=0;i<oldpaths[a].size();++i)assert(test.agents[a].path[i].location==oldpaths[a][i]);}
 auto&s=address_adapter::state();s.initial_soc=15;s.initial_validated=true;s.total_seconds=5;s.receipt_file=argv[2];
 address_adapter::check_final(test.agents,test.instance,test.neighbor.sum_of_costs);return address_budget::finish();
}
'''
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            for path in ('inc/address_adapter_support.h','inc/address_budget_support.h','inc/address_recovery_support.h'):
                (root/Path(path).name).write_bytes(files[path])
            (root/'fixture.cpp').write_text(code)
            built=subprocess.run(['rtk','proxy','g++','-std=c++14','-O0','-I'+str(root),str(root/'fixture.cpp'),'-o',str(root/'fixture')],capture_output=True,text=True,timeout=30)
            self.assertEqual(built.returncode,0,built.stderr)
            for mode in (0,1,2,3,4,5,6,7):
                receipt=root/('receipt'+str(mode)+'.json');trace=root/('attempt'+str(mode)+'.jsonl');detail=root/('detail'+str(mode)+'.jsonl')
                run=subprocess.run(['rtk','proxy',str(root/'fixture'),str(mode),str(receipt),str(trace),str(detail)],capture_output=True,text=True,timeout=5)
                self.assertEqual(run.returncode,0,'mode='+str(mode)+' '+run.stderr)
                row=json.loads(trace.read_text());value=json.loads(detail.read_text())
                self.assertEqual(row['primary_stop'],'FOCAL_DRAINED_EMPTY');self.assertEqual(row['failed_agent'],3)
                self.assertEqual(row['primary_calls'],4);self.assertEqual(row['accepted'],mode==0)
                self.assertEqual(value['snapshot_complete'],mode not in (1,7))
                if mode==1:self.assertEqual((value['full_checks'],value['pair_checks'],value['extra_calls']),(0,0,0))
                if mode==0:self.assertTrue(value['final_check_complete']);self.assertEqual(value['extra_calls'],2)
                if mode==2:self.assertEqual(value['decision'],'DEADLINE');self.assertEqual(value['deadline_phase'],'RECOVERY_COMMIT')
                if mode in (3,4):self.assertEqual(value['decision'],'DEADLINE')
                if mode==5:self.assertEqual(value['decision'],'COMMIT_REJECTED')
                if mode==6:
                    self.assertEqual(value['decision'],'DEADLINE');self.assertFalse(value['final_check_complete'])
                    self.assertLess(value['checks_completed'],value['full_checks']+value['partial_checks'])
                if mode==7:self.assertEqual((value['full_checks'],value['pair_checks'],value['extra_calls']),(0,0,0))


if __name__=='__main__': unittest.main()
