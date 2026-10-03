"""Publish a compact author-source/input/receipt capsule, excluding build trees."""
from pathlib import Path
import csv
import hashlib
import io
import json
import shutil
import subprocess
import tarfile

H = Path(__file__).resolve().parent
V = H/'vendor/STPG'
P = Path('/home/lyh/MAPF_LMAPF_ERROR_GUIDANCE_EXPLORE/exploration/error_guidance/gses_author_preflight_20261003_r9')
P.mkdir(parents=True, exist_ok=False)
reg=json.loads((H/'REGISTERED_CASES.json').read_text())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
for name in ['REGISTERED_CASES.json','EXECUTION_LIMITS.json','DEPENDENCY_PACKAGES.json','RESULTS.json','run_registered.py','run_step.py','package_preflight.py']:
    shutil.copy2(H/name,P/name)
shutil.copytree(H/'commands',P/'commands')
for c in reg['cases']:
    for k in ['path','situation_file']:
        dest=P/'inputs'/c[k];dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(V/c[k],dest)
files=[]
for directory in ['inc','src']:
    files.extend(p for p in (V/directory).rglob('*') if p.is_file())
files.extend(V/p for p in ['CMakeLists.txt','README.md','LICENSE','.gitmodules','compile.sh','simulate.sh','script/run_exps.py'])
with tarfile.open(P/'author_core_source.tar.gz','w:gz') as archive:
    for p in sorted(files): archive.add(p,arcname=str(p.relative_to(V)),recursive=False)
source={str(p.relative_to(V)):sha(p) for p in sorted(files)}
def git(*args):
    return subprocess.check_output(['rtk','proxy','git',*args],cwd=V,text=True).strip()
assert git('rev-parse','HEAD')==reg['author_commit']
assert not git('diff','--name-only')
provenance={'upstream':'https://github.com/DiligentPanda/STPG','paper':'https://ojs.aaai.org/index.php/AAAI/article/view/34487',
 'commit':reg['author_commit'],'submodules':git('submodule','status','--recursive').splitlines(),
 'author_tracked_source_modified':False,'binary_sha256':sha(V/'build/simulate'),
 'core_source_members':source,'source_archive_sha256':sha(P/'author_core_source.tar.gz'),
 'submodule_source_included':False,'note':'PBS and pybind11 obtained at pinned author submodule commits when rebuilding; native binary and private system dependency sysroot omitted.'}
(P/'PROVENANCE.json').write_text(json.dumps(provenance,indent=2)+'\n')
shutil.copy2(V/'LICENSE',P/'AUTHOR_LICENSE.txt')
rows=[]
for r in json.loads((P/'RESULTS.json').read_text()):
    s=r['stats'];folder=P/'commands'/(r['case']+'__'+r['method']);output=(folder/'stdout.log').read_text()
    assert r['returncode']==0 and s['status'] in ['Succ','Timeout']
    assert all(x not in output for x in ['bug: all stucked','collision detected'])
    assert s['cost']<=s['original_cost']
    rows.append({'map':r['case'],'agents':r['agents'],'method':r['method'],'status':s['status'],
        'original_cost':s['original_cost'],'cost':s['cost'],'search_seconds':s['search_time']/1e6,
        'reported_total_seconds':s['total_time']/1e6,'grouping_seconds':s['grouping_time']/1e6,
        'elapsed_seconds':r['elapsed_seconds'],'explored_nodes':s['explored_node']})
with (P/'summary.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
out={'passed':True,'registered_runs':8,'matched_input_pairs':4,'original_source_delta':0,
 'binary_sha256':provenance['binary_sha256'],'returncode_zero':8,
 'status_counts':{m:{s:sum(r['method']==m and r['status']==s for r in rows) for s in ['Succ','Timeout']} for m in reg['methods']},
 'stdout_stuck_or_collision_markers':0,'limitations':['author discrete simulator internal checks only; independent trajectory replay not available because single-situation CLI does not emit requested paths',
 'four deterministic cases selected before outcome, no statistical performance claim',
 'native author costs and source models do not match current continuous FIFO execution task']}
(P/'ROOT_AUTHOR_AUDIT.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
