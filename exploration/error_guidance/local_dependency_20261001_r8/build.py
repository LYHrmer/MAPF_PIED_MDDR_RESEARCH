from pathlib import Path
import json,subprocess,time,shlex,hashlib
HERE=Path(__file__).resolve().parent;MAIN=Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence');OUT=MAIN/HERE.name
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def run(name,cmd):
 d=HERE/'build_receipts'/name;d.mkdir(parents=True,exist_ok=True);s=time.monotonic()
 p=subprocess.run(['rtk','proxy',*map(str,cmd)],capture_output=True,text=True)
 (d/'stdout.log').write_text(p.stdout);(d/'stderr.log').write_text(p.stderr);(d/'receipt.json').write_text(json.dumps({'command':list(map(str,cmd)),'exit':p.returncode,'wall':time.monotonic()-s},indent=2));print(name,p.returncode,flush=True);assert p.returncode==0,p.stderr[-500:]
run('configure',['cmake','-S',OUT/'lsmart_successor/server','-B',OUT/'server_build','-DCMAKE_BUILD_TYPE=Release','-DCMAKE_INSTALL_PREFIX=/home/lyh/.local','-DCMAKE_CXX_FLAGS=-I/home/lyh/.local/include','-DCMAKE_EXE_LINKER_FLAGS=-L/home/lyh/.local/lib -Wl,-rpath,/home/lyh/.local/lib'])
run('server',['cmake','--build',OUT/'server_build','-j','3'])
B=MAIN/'published_guidance_comparison_20260930_r4/build_hm';flags=(B/'CMakeFiles/py_driver.dir/flags.make').read_text();defs=shlex.split(next(x.split('=',1)[1] for x in flags.splitlines() if x.startswith('CXX_DEFINES')));incs=shlex.split(next(x.split('=',1)[1] for x in flags.splitlines() if x.startswith('CXX_INCLUDES')))
objects=sorted(p for p in (B/'CMakeFiles/py_driver.dir').rglob('*.o') if p.name not in ['py_driver.cpp.o','driver.cpp.o'])
for policy in ['official','candidate']:
 obs=objects if policy=='official' else [p for p in objects if p.name!='search.cpp.o']+[MAIN/'execution_residual_20261001_r7/search_overlay.o']
 run(policy,['c++','-O3','-DNDEBUG','-std=c++17','-flto',*defs,*incs,HERE/(policy+'_bridge.cpp'),*obs,'-lboost_program_options','-lboost_system','-lboost_log_setup','-lboost_log','-lboost_filesystem','-lboost_chrono','-lboost_regex','-lboost_thread','-lboost_atomic','-pthread','-o',OUT/('bridge_'+policy)])
pins={str(p):sha(p) for p in [OUT/'server_build/ExecutionManager',OUT/'bridge_official',OUT/'bridge_candidate',MAIN/'published_continuous_execution_20261001_r6c/client_build/controllers/footbot_diffusion/libfootbot_diffusion.so',MAIN/'published_continuous_execution_20261001_r6c/client_build/loop_functions/trajectory_loop_functions/libtrajectory_loop_functions.so',*objects,MAIN/'execution_residual_20261001_r7/search_overlay.o']}
(HERE/'binary_manifest.json').write_text(json.dumps(pins,indent=2)+'\n')
