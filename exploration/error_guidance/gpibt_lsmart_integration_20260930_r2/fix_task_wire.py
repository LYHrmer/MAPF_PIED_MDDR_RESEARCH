"""Retain first-pair identities, repair the observed native RPC task_id omission."""
from pathlib import Path
import hashlib, json, shutil, subprocess, time, difflib

HERE=Path(__file__).resolve().parent
OUT=Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence/gpibt_lsmart_integration_20260930_r2')
SRC=OUT/'lsmart_successor'
retain=OUT/'retained_first_pair';retain.mkdir(exist_ok=False)
for name in ('binary_manifest.json','source_manifest.json','lsmart_integration_r2.patch','audit.json'):
    shutil.copy2(HERE/name,HERE/('first_pair_'+name))
for name in json.loads((HERE/'source_manifest.json').read_text()):
    dst=HERE/'first_pair_source_snapshot'/name;dst.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(SRC/name,dst)
old_binary=OUT/'server_build/ExecutionManager'
shutil.copy2(old_binary,retain/'ExecutionManager')
oldsha=hashlib.sha256(old_binary.read_bytes()).hexdigest()
require=json.loads((HERE/'binary_manifest.json').read_text())[str(old_binary)]
assert oldsha==require
(HERE/'first_pair_retained_binary.json').write_text(json.dumps({'original_path':str(old_binary),'retained_path':str(retain/'ExecutionManager'),'sha256':oldsha},indent=2)+'\n')
path=SRC/'server/src/ADG.cpp';old=path.read_text()
(HERE/'first_pair_source_snapshot/server/src/ADG.cpp').write_text(old)
needle='''        int task_id;
        if (action.task_ptr == nullptr) {
            task_id = -1;
        } else {
            task_id = action.task_ptr->id;
        }'''
assert old.count(needle)==1
new=old.replace(needle,'''        // Integration correction: task_ptr is never populated by this parser.
        // Preserve the existing native task identity on the RPC wire.
        int task_id = action.task_id;''',1)
path.write_text(new)
(HERE/'task_wire_fix.patch').write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/server/src/ADG.cpp',tofile='b/server/src/ADG.cpp')))
pins=json.loads((HERE/'source_manifest.json').read_text())
pins['server/src/ADG.cpp']={'previous':hashlib.sha256(old.encode()).hexdigest(),'successor':hashlib.sha256(new.encode()).hexdigest()}
(HERE/'source_manifest.json').write_text(json.dumps(pins,indent=2)+'\n')
receipt_dir=HERE/'build_receipts/build_server_retry01';receipt_dir.mkdir(exist_ok=False)
args=['rtk','proxy','timeout','--kill-after=5s','120s','cmake','--build',str(OUT/'server_build'),'-j','4']
start=time.monotonic()
with (receipt_dir/'stdout.log').open('w') as o,(receipt_dir/'stderr.log').open('w') as e:
    p=subprocess.run(args,stdout=o,stderr=e)
(receipt_dir/'receipt.json').write_text(json.dumps({'argv':args,'exit_code':p.returncode,'wall_seconds':time.monotonic()-start},indent=2)+'\n')
assert p.returncode==0
ids=json.loads((HERE/'binary_manifest.json').read_text())
ids[str(old_binary)]=hashlib.sha256(old_binary.read_bytes()).hexdigest()
(HERE/'binary_manifest.json').write_text(json.dumps(ids,indent=2)+'\n')
print(json.dumps({'status':'TASK_WIRE_FIXED_FOR_PRESPECIFIED_RETRY01','old_server_sha256':oldsha,'new_server_sha256':ids[str(old_binary)],'official_planner_unchanged':True},indent=2))
