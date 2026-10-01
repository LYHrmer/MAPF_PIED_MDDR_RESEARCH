from pathlib import Path
import hashlib,json,shlex,subprocess,time,difflib
HERE=Path(__file__).resolve().parent;MAIN=Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence');OUT=MAIN/HERE.name
PARENT=HERE.parent/'published_continuous_execution_20261001_r6c';BUILD=MAIN/'published_guidance_comparison_20260930_r4/build_hm'
BASE=MAIN/'baseline_selection_20260929/OnlineGGO/Guided-PIBT/guided-pibt'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
 search=(BASE/'traffic_mapf/search.cpp').read_text()
 changed=search.replace('namespace TrafficMAPF{','namespace TrafficMAPF{\nextern double r7_edge_penalty(int search_start, int destination);',1)
 needle='            s_node temp_node(next,cost,h,op_flow, depth);'
 assert changed.count(needle)==1
 changed=changed.replace(needle,'            cost += r7_edge_penalty(start, next);\n'+needle)
 (HERE/'search_overlay.cpp').write_text(changed)
 (HERE/'search_overlay.patch').write_text(''.join(difflib.unified_diff(search.splitlines(True),changed.splitlines(True),fromfile='official/search.cpp',tofile='R7/search_overlay.cpp')))
 bridge=(PARENT/'official_bridge.cpp').read_text()
 helper='''
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
'''
 bridge=bridge.replace('using json=nlohmann::json;','using json=nlohmann::json;\n'+helper)
 needle='  auto p_before=planner.p;'
 assert bridge.count(needle)==1
 bridge=bridge.replace(needle,'  TrafficMAPF::r7_starts.clear();for(auto &s:ins.at("starts"))TrafficMAPF::r7_starts.push_back(s.at("location"));\n  TrafficMAPF::r7_costs=req.at("edge_costs").get<std::vector<std::vector<double>>>();TrafficMAPF::r7_calls=0;TrafficMAPF::r7_nonzero=0;\n'+needle)
 bridge=bridge.replace('  r["rand_seed"]=', '  r["r7_edge_cost_calls"]=TrafficMAPF::r7_calls;r["r7_nonzero_edge_cost_calls"]=TrafficMAPF::r7_nonzero;\n  r["rand_seed"]=')
 (HERE/'candidate_bridge.cpp').write_text(bridge)
 flags=(BUILD/'CMakeFiles/py_driver.dir/flags.make').read_text()
 defs=shlex.split(next(x.split('=',1)[1] for x in flags.splitlines() if x.startswith('CXX_DEFINES')))
 incs=shlex.split(next(x.split('=',1)[1] for x in flags.splitlines() if x.startswith('CXX_INCLUDES')))
 objects=sorted(p for p in (BUILD/'CMakeFiles/py_driver.dir').rglob('*.o') if p.name not in ['py_driver.cpp.o','driver.cpp.o','search.cpp.o'])
 receipts=[]
 cmds=[['c++','-O3','-DNDEBUG','-std=c++17','-flto',*defs,*incs,'-c',str(HERE/'search_overlay.cpp'),'-o',str(OUT/'search_overlay.o')],
       ['c++','-O3','-DNDEBUG','-std=c++17','-flto',*defs,*incs,str(HERE/'candidate_bridge.cpp'),str(OUT/'search_overlay.o'),*map(str,objects),'-lboost_program_options','-lboost_system','-lboost_log_setup','-lboost_log','-lboost_filesystem','-lboost_chrono','-lboost_regex','-lboost_thread','-lboost_atomic','-pthread','-o',str(OUT/'bridge_candidate')]]
 for i,cmd in enumerate(cmds):
  start=time.monotonic();p=subprocess.run(['rtk','proxy',*cmd],capture_output=True,text=True)
  (HERE/f'build_{i}.stdout').write_text(p.stdout);(HERE/f'build_{i}.stderr').write_text(p.stderr)
  receipts.append({'argv':cmd,'exit_code':p.returncode,'wall_seconds':time.monotonic()-start})
  (HERE/'build_receipts.json').write_text(json.dumps(receipts,indent=2)+'\n')
  assert p.returncode==0,p.stderr
 (HERE/'candidate_identity.json').write_text(json.dumps({'base_search':str(BASE/'traffic_mapf/search.cpp'),'base_search_sha256':sha(BASE/'traffic_mapf/search.cpp'),'overlay_sha256':sha(HERE/'search_overlay.cpp'),'bridge_source_sha256':sha(HERE/'candidate_bridge.cpp'),'binary':str(OUT/'bridge_candidate'),'binary_sha256':sha(OUT/'bridge_candidate'),'retained_original_objects':{str(p):sha(p) for p in objects},'replaced_object':'traffic_mapf/search.cpp.o'},indent=2)+'\n')
 print('candidate built')
if __name__=='__main__':main()
