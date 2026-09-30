"""Bounded builds in ignored isolated native tree; no old build is mutated."""
from pathlib import Path
import subprocess, time, json, hashlib, shutil

HERE=Path(__file__).resolve().parent
OUT=Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence/gpibt_lsmart_integration_20260930_r2')
PRIOR=OUT.with_name('gpibt_lsmart_integration_20260930')
SRC=OUT/'lsmart_successor'
def run(name,args):
    d=HERE/'build_receipts'/name
    d.mkdir(parents=True,exist_ok=False)
    start=time.monotonic()
    with (d/'stdout.log').open('w') as o,(d/'stderr.log').open('w') as e:
        p=subprocess.run(['rtk','proxy','timeout','--kill-after=5s','120s',*map(str,args)],stdout=o,stderr=e)
    (d/'receipt.json').write_text(json.dumps({'argv':list(map(str,args)),'exit_code':p.returncode,'wall_seconds':time.monotonic()-start},indent=2)+'\n')
    print(name,p.returncode,flush=True)
    if p.returncode:raise SystemExit(p.returncode)

run('configure_server',['cmake','-S',SRC/'server','-B',OUT/'server_build','-DCMAKE_BUILD_TYPE=Release','-DCMAKE_CXX_FLAGS=-I/home/lyh/.local/include','-DCMAKE_EXE_LINKER_FLAGS=-L/home/lyh/.local/lib -Wl,-rpath,/home/lyh/.local/lib'])
run('build_server',['cmake','--build',OUT/'server_build','-j','4'])
run('configure_client',['cmake','-S',SRC/'client','-B',OUT/'client_build','-DCMAKE_BUILD_TYPE=Release','-DARGoS_DIR=/home/lyh/.local/share/argos3/cmake','-DCMAKE_INSTALL_PREFIX=/home/lyh/.local'])
run('build_client',['cmake','--build',OUT/'client_build','-j','4'])
files=[OUT/'gpibt_bridge',OUT/'server_build/ExecutionManager',OUT/'client_build/controllers/footbot_diffusion/libfootbot_diffusion.so',OUT/'client_build/loop_functions/trajectory_loop_functions/libtrajectory_loop_functions.so']
identities={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
prior=json.loads((HERE.parent/'gpibt_lsmart_integration_20260930/binary_manifest.json').read_text())
assert identities[str(OUT/'gpibt_bridge')]==prior[str(PRIOR/'gpibt_bridge')]
identities.update({p:h for p,h in prior.items() if p.endswith('.o')})
for p,h in identities.items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h,p
(HERE/'binary_manifest.json').write_text(json.dumps(identities,indent=2)+'\n')
