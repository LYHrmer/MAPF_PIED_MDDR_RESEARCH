"""Native recovery software contracts only; never constructs a solver/Instance."""
from pathlib import Path
import subprocess
import tempfile
import unittest

from address_adapter import adapt as base_adapt
from address_loop_guard import adapt as loop_adapt
from address_recovery import adapt
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
        files=sources();changed=adapt(files)
        original=files['src/LNS.cpp'].decode();new=changed['src/LNS.cpp'].decode()
        marker='     if ((destroy_strategy == RANDOMWALK || destroy_strategy == DESTROY_COUNT) && (algo != CANONICAL))'
        reward=original.split(marker)[1].split('    if (remaining_agents == 0')[0]
        self.assertIn(marker+reward,new)
        rollback=original.split('        auto p2 = shuffled_agents.begin();')[1].split('        return false;')[0]
        self.assertIn('        auto p2 = shuffled_agents.begin();'+rollback,new)
        self.assertIn('FOCAL_DRAINED_EMPTY',changed['src/SIPP.cpp'].decode())
        self.assertNotIn('length_max =',changed['src/SIPP.cpp'].decode())
        with self.assertRaises(ValueError):
            adapt({**files,'src/driver.cpp':b'int main(){}'})

    def test_native_fake_callback_mechanism(self):
        code=r'''
#include "address_recovery_support.h"
#include "address_adapter_support.h"
#include <cassert>
using namespace address_recovery;
int main() {
    Context c;
    c.incumbent={{15,15,15,16,17},{0,0,0,1,2},{10,10,10,11},{4,3,2,7,12}};
    c.primary={{15,16,17},{0,1,2},{10,11},{}};
    c.order={0,1,2,3};c.failed_position=3;c.old_group_cost=15;c.primary_calls=4;
    c.stop=Stop::FOCAL_DRAINED_EMPTY;c.deadline_ns=1000;
    Paths good={{15,16,17},{0,0,0,1,2},{10,11},{4,3,2,7,12}};
    auto validate=[&](const Paths& p,bool complete) {
        address_adapter::Paths chosen;std::vector<int> starts,goals;
        for(size_t a=0;a<p.size();++a) {
            if(p[a].empty()) {if(complete)throw std::runtime_error("incomplete");continue;}
            chosen.push_back(p[a]);starts.push_back(c.incumbent[a].front());goals.push_back(c.incumbent[a].back());
        }
        if(!chosen.empty()) address_adapter::validate(chosen,4,5,std::vector<bool>(20,false),starts,goals);
    };
    long long now=0;int calls=0;std::mt19937 rng(4);
    auto clock=[&](){return now;};
    auto search=[&](int a,const Paths& partial){++calls;return Reply{Stop::FOUND,good[a]};};
    auto anchor=recover(c,Policy::ANCHOR,8,rng,search,validate,clock);
    assert(anchor.accepted && calls==2 && anchor.trace.kept==1 && anchor.trace.tail==2);
    assert(anchor.paths==good && anchor.order==std::vector<int>({0,3,1,2}));
    assert(anchor.trace.blocking_prefix_agents==std::vector<int>({1}));
    assert(c.primary[1]==std::vector<int>({0,1,2})); // input transaction untouched
    calls=0;auto abandoned=recover(c,Policy::ABANDON,8,rng,search,validate,clock);
    assert(!abandoned.accepted && calls==0 && abandoned.trace.decision=="ABANDON");
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
    now=0;
    auto prep_expired=[&](int a,const Paths& p){now=1001;return Reply{Stop::DEADLINE,{},false};};
    auto prep_result=recover(c,Policy::ANCHOR,8,rng,prep_expired,validate,clock);
    assert(!prep_result.accepted && prep_result.trace.extra_requests==1 && prep_result.trace.extra_calls==0);
    now=0;
    auto empty=[&](int a,const Paths& p){return Reply{Stop::FOCAL_DRAINED_EMPTY,{}};};
    assert(!recover(c,Policy::ANCHOR,8,rng,empty,validate,clock).accepted);
    assert(classify(true,true,NativeEnd::FOCAL_DRAINED_EMPTY)==Stop::DEADLINE);
    assert(classify(false,true,NativeEnd::FOUND)==Stop::DEADLINE);
    assert(classify(true,false,NativeEnd::UNKNOWN)==Stop::EMPTY_UNCLASSIFIED);
    assert(conflict({0,1},{4,3,2,1})); // late goal occupancy
    assert(conflict({0,1},{1,0})); // opposing edge
    assert(!conflict({0,1},{4,3}));
    auto malformed=c;malformed.old_group_cost=16;bool threw=false;
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
        files=sources();files.update(adapt(files))
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            for name,raw in files.items():
                target=root/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
            includes=['-I'+str(root/'inc'),'-I'+str(root/'inc/CBS'),'-I'+str(root/'inc/PIBT'),'-I/usr/include/eigen3']
            for name in ('src/LNS.cpp','src/SIPP.cpp','src/driver.cpp'):
                result=subprocess.run(['g++','-std=c++14','-fsyntax-only',*includes,str(root/name)],
                                      capture_output=True,text=True,timeout=30)
                self.assertEqual(result.returncode,0,result.stderr)


if __name__=='__main__': unittest.main()
