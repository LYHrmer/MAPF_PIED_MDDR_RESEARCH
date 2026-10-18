"""Actual author loop/walk methods on fake graph/table; never an author solver.

The C++ executable is a temporary software fixture, not an ADDRESS build. Its
clock is deterministic and a successful repair is a stub. No MAPF task is run.
"""
import os
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from address_adapter import adapt
from address_loop_guard import apply_loop_guard, LOOP_ANCHOR, GUARD
from build_address_full import source_identity


def function(source, signature):
    start = source.index(signature)
    opening = source.index('{', start)
    depth = 1
    for index in range(opening+1, len(source)):
        depth += (source[index] == '{') - (source[index] == '}')
        if depth == 0:
            return source[start:index+1]
    raise ValueError('unterminated fixed-source method')


def fixture(source):
    walk = function(source, 'void LNS::randomWalk(')
    generate = function(source, 'bool LNS::generateNeighborByRandomWalk(')
    opening = source.index(LOOP_ANCHOR)
    # The real loop condition, time update, dispatch and false/continue path.
    loop = source[opening:source.index('        // store the neighbor information', opening)]
    run = function(source, 'bool LNS::run()')
    postlude = run[run.index('    average_group_size ='):-1]
    return r'''
#include "address_adapter_support.h"
#include <algorithm>
#include <cassert>
#include <chrono>
#include <cstdlib>
#include <iostream>
#include <set>
#include <vector>
using namespace std;
using fsec = chrono::duration<double>;
struct Time { static int tick; static fsec now() { return fsec(++tick); } }; int Time::tick=0;
struct Vertex { int location; };
struct Planner { vector<int> my_heuristic; int start_location; };
struct Agent { vector<Vertex> path; Planner* path_planner; };
struct FakeGraph {
    int map_size=18,num_of_rows=9,num_of_cols=2;
    vector<int> getNeighbors(int v) const { return {v^1}; }
    bool isObstacle(int) const { return false; }
    vector<int> getStarts() const { return {0,2,4,6,8,10,12,14,16}; }
    vector<int> getGoals() const { return {1,3,5,7,9,11,13,15,17}; }
};
struct FakeTable {
    int calls=0;
    void getConflictingAgents(int a,set<int>& agents,int,int,int) { ++calls; agents.insert((a+1)%9); }
};
struct LNS {
    enum { RANDOMWALK, INTERSECTION, RANDOMAGENTS, DESTROY_COUNT };
    vector<Planner> planners; vector<Agent> agents;
    struct { vector<int> agents; } neighbor;
    FakeGraph instance; FakeTable path_table;
    int neighbor_size=8, screen=0, generated=0, repairs=0;
    int destroy_strategy=RANDOMWALK, num_of_iterations=2, sum_of_costs=9, sum_of_distances=9;
    int initial_sum_of_costs=9, num_of_failures=0; double average_group_size=0;
    bool ALNS=false; double runtime=0, time_limit=100; fsec start_time{0};
    struct Stat { int num_of_agents; }; vector<Stat> iteration_stats{{9}};
    LNS(bool slack) {
        planners.resize(9);
        for(int a=0;a<9;++a) {
            planners[a].my_heuristic.assign(18,1000);
            planners[a].my_heuristic[2*a]=1; planners[a].my_heuristic[2*a+1]=0;
            planners[a].start_location=2*a;
            agents.push_back({{{2*a},{2*a+1}},&planners[a]});
        }
        if(slack) { agents[0].path={Vertex{0},Vertex{0},Vertex{1}}; ++sum_of_costs; }
        initial_sum_of_costs=sum_of_costs;
    }
    int wrapper() { ++generated; return 0; }
    int bernoulie() { return wrapper(); }
    void chooseDestroyHeuristicbyALNS() {}
    bool generateNeighborByIntersection() { return false; }
    void validateSolution() {}
    const char* getSolverName() const { return "fixture"; }
    bool generateNeighborByRandomWalk(int);
    void randomWalk(int,int,int,set<int>&,int,int);
    bool run_fixture() {
        bool succ=true; int searchSuccess=0;
''' + loop + r'''
        // Replace only the actual solver call/accepted-iteration body at this seam.
        ++repairs; agents[0].path={Vertex{0},Vertex{1}}; sum_of_costs=sum_of_distances;
        iteration_stats.push_back({int(neighbor.agents.size())});
    }
''' + postlude + r'''
    }
};
''' + generate + '\n' + walk + r'''
int main(int argc,char**argv) {
    srand(0); LNS test(argc>2);
    address_adapter::Paths initial;
    for(const auto& a:test.agents) { initial.emplace_back(); for(auto p:a.path) initial.back().push_back(p.location); }
    auto& state=address_adapter::state(); state.total_seconds=5; state.receipt_file=argv[1];
    state.initial_soc=address_adapter::check(initial,test.instance); state.initial_validated=true;
    if(!test.run_fixture()) return 91;
    // Actual adapter final validator and receipt writer, on declared software paths.
    address_adapter::check_final(test.agents,test.instance,test.sum_of_costs);
    int code=address_adapter::finish();
    cout << test.generated << " " << test.repairs << " " << test.iteration_stats.size()
         << " " << Time::tick << " FINAL_CHECK_AND_OUTPUT_REACHED\n";
    return code;
}
'''


class LoopGuardContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = Path(os.environ.get('ADDRESS_AUTHOR_ROOT', '/home/lyh/.cache/mapf_research/address-b3d35c4'))
        pins = source_identity(root)
        original = {name: (root/name).read_bytes() for name in pins}
        cls.base = dict(original, **adapt(original))
        cls.guarded = dict(cls.base, **apply_loop_guard(cls.base))
        cls.directory = tempfile.TemporaryDirectory()
        cls.executables = {}
        for name, files in (('base', cls.base), ('guarded', cls.guarded)):
            cpp = Path(cls.directory.name)/(name+'.cpp')
            exe = cpp.with_suffix('')
            cpp.write_text(fixture(files['src/LNS.cpp'].decode()))
            compiled = subprocess.run(['rtk','proxy','g++','-std=c++14','-O0','-I',str(Path(__file__).parent),
                                       str(cpp),'-o',str(exe)],
                                      capture_output=True, timeout=30)
            if compiled.returncode:
                raise RuntimeError(compiled.stderr.decode())
            cls.executables[name] = exe

    @classmethod
    def tearDownClass(cls):
        cls.directory.cleanup()

    def run_fixture(self, name, slack=False):
        receipt = Path(self.directory.name)/(name+str(slack)+'.json')
        command = ['rtk','proxy',str(self.executables[name]),str(receipt)]+(['slack'] if slack else [])
        raw = subprocess.run(command, capture_output=True, check=True, timeout=5).stdout.decode().splitlines()[-1].split()
        self.assertTrue(json.loads(receipt.read_text())['initial_and_final_validated'])
        self.assertEqual(raw[-1], 'FINAL_CHECK_AND_OUTPUT_REACHED')
        return tuple(map(int,raw[:-1]))

    def test_zero_slack_stops_before_failed_generation(self):
        base = self.run_fixture('base')
        self.assertEqual(base, (100,0,1,100))
        # Red on the real bug: maxIterations=2 never advances despite 100 proposals.
        self.assertEqual(self.run_fixture('guarded'), (0,0,1,0))

    def test_positive_slack_is_not_skipped_and_later_root_bound_stops(self):
        self.assertEqual(self.run_fixture('guarded', slack=True), (1,1,2,1))

    def test_patch_is_only_root_guard_and_rejects_wrong_or_duplicate_input(self):
        old, new = self.base['src/LNS.cpp'], self.guarded['src/LNS.cpp']
        self.assertEqual(new, old.replace(LOOP_ANCHOR.encode(), (LOOP_ANCHOR+GUARD).encode(), 1))
        self.assertEqual(function(old.decode(), 'bool LNS::runPP()'),
                         function(new.decode(), 'bool LNS::runPP()'))
        for bad in ({'src/LNS.cpp': old.replace(LOOP_ANCHOR.encode(), b'changed')},
                    {'src/LNS.cpp': old.replace(b'#include "address_adapter_support.h"', b'')},
                    self.guarded):
            with self.assertRaises(ValueError):
                apply_loop_guard(bad)


if __name__ == '__main__':
    unittest.main()
