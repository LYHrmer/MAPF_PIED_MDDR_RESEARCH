from pathlib import Path
import json,tarfile,hashlib
H=Path(__file__).resolve().parent;M=Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence');O=M/H.name;A=H/'source_archives';A.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
groups={'lsmart_successor':sorted(p for p in (O/'lsmart_successor').rglob('*') if p.is_file()),'native_binaries':[O/'server_build/ExecutionManager',O/'bridge_official',O/'bridge_candidate',M/'execution_residual_20261001_r7/search_overlay.o',M/'published_continuous_execution_20261001_r6c/client_build/controllers/footbot_diffusion/libfootbot_diffusion.so',M/'published_continuous_execution_20261001_r6c/client_build/loop_functions/trajectory_loop_functions/libtrajectory_loop_functions.so']};result={}
for name,files in groups.items():
 dst=A/(name+'.tar.gz');members={str(p.relative_to(M)):{'sha256':sha(p),'bytes':p.stat().st_size} for p in files}
 with tarfile.open(dst,'w:gz',compresslevel=6) as t:
  for p in files:t.add(p,arcname=str(p.relative_to(M)),recursive=False)
 with tarfile.open(dst,'r:gz') as t:
  check={m.name:{'sha256':hashlib.sha256(t.extractfile(m).read()).hexdigest(),'bytes':m.size} for m in t.getmembers() if m.isfile()}
 assert check==members;result[name]={'path':str(dst.relative_to(H)),'sha256':sha(dst),'bytes':dst.stat().st_size,'members':members}
(H/'source_archive_manifest.json').write_text(json.dumps({'all_member_sha256_verified':True,'archives':result},indent=2)+'\n');print('source archives verified')
