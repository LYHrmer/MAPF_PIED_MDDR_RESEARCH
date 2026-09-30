"""Isolated controller-condition successor; preserve parent/official search objects."""
from pathlib import Path
import difflib,json,shutil
from common import HERE,NATIVE,sha,write
PRIOR=HERE.parent/'gpibt_lsmart_active_20260930_r3'
PN=NATIVE.with_name('gpibt_lsmart_active_20260930_r3');SRC=NATIVE/'lsmart_successor'
assert not NATIVE.exists()
old={str(p.relative_to(PRIOR)):sha(p) for p in PRIOR.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
for name,h in json.loads((PRIOR/'artifact_manifest.json').read_text()).items():assert sha(PRIOR/name)==h
write(HERE/'parent_archive_manifest.json',old)
for part in ('server','client'):
    shutil.copytree(PN/'lsmart_successor'/part,SRC/part,ignore=shutil.ignore_patterns('build','externalDependencies','__pycache__'))
(SRC/'client/externalDependencies').symlink_to(PN/'lsmart_successor/client/externalDependencies',target_is_directory=True)
for name in ('map.json','GPIBT_LICENSE.txt','LSMART_LICENSE.txt'):shutil.copy2(PRIOR/name,HERE/name)
(NATIVE/'server_build').mkdir();shutil.copy2(PN/'server_build/ExecutionManager',NATIVE/'server_build/ExecutionManager')
before={str(p.relative_to(SRC)):sha(p) for p in SRC.rglob('*') if p.is_file() and 'externalDependencies' not in p.parts}
names=['client/controllers/footbot_diffusion/footbot_diffusion.h','client/controllers/footbot_diffusion/footbot_diffusion.cpp']
old_text={n:(SRC/n).read_text() for n in names}
def edit(n,old,new):
 p=SRC/n;s=p.read_text();assert s.count(old)==1,(n,old[:80],s.count(old));p.write_text(s.replace(old,new))
h,c=names
edit(h,'        integration_left_command=left; integration_right_command=right;\n        m_pcWheels->SetLinearVelocity(left,right);','''        const char* raw=std::getenv("R4_CONDITION");
        const std::string condition=raw?raw:"nominal";
        Real factor=1.0;
        if(robot_id=="0") {
            if(condition=="slow065") factor=0.65;
            if(condition=="slow085") factor=0.85;
            if(condition=="axis" && integration_current_axis==0) factor=0.65;
            if(condition=="unknown_shift" && integration_trigger_tick>=0) factor=0.55;
        }
        integration_left_command=left*factor; integration_right_command=right*factor;
        m_pcWheels->SetLinearVelocity(integration_left_command,integration_right_command);''')
edit(h,'    int integration_trigger_tick = -1;','    mutable int integration_current_axis = -1;\n    map<int,int> integration_node_axes;\n    int integration_trigger_tick = -1;')
edit(c,'        if (action1 == "M") {\n            deque<int> prev_ids;','        if (action1 == "M") {\n            integration_node_axes[nodeID]=(x!=start_x?0:1);\n            deque<int> prev_ids;')
edit(c,'    if (a.type == Action::MOVE) {\n        CVector3 targetPos', '    integration_current_axis = a.type==Action::MOVE ? integration_node_axes.at(a.nodeIDS.front()) : -1;\n    if (a.type == Action::MOVE) {\n        CVector3 targetPos')
manifest={};patch=[]
for n in names:
 p=SRC/n;new=p.read_text();manifest[n]={'parent':before[n],'successor':sha(p)}
 patch.extend(difflib.unified_diff(old_text[n].splitlines(True),new.splitlines(True),fromfile='a/'+n,tofile='b/'+n))
 snap=HERE/'source_snapshot'/n;snap.parent.mkdir(parents=True,exist_ok=True);snap.write_text(new)
(HERE/'controller_condition.patch').write_text(''.join(patch));write(HERE/'source_manifest.json',manifest)
write(HERE/'native_source_tree_manifest.json',{'parent':before,'successor':{n:sha(SRC/n) for n in before}})
protocol=sha(HERE/'PROTOCOL.md');runs=[]
for split,seeds,conditions,policies in [('train',[42,43,44],['nominal','slow065','slow085','axis'],['zero']),('cal',[51],['nominal','slow065','slow085','axis'],['zero']),('test',[61],['nominal','slow065','slow085','axis','unknown_pause','unknown_shift'],['zero','analytic','history','learned'])]:
 for seed in seeds:
  for condition in conditions:
   for policy in policies:runs.append({'id':f'{split}_s{seed}_{condition}_{policy}','split':split,'seed':seed,'condition':condition,'policy':policy,'horizon_ticks':400})
assert len(runs)==40
write(HERE/'runs.json',{'protocol_sha256':protocol,'runs':runs})
write(HERE/'preflight_identity.json',{'protocol_sha256':protocol,'runs_sha256':sha(HERE/'runs.json'),'parent_manifest_sha256':sha(PRIOR/'artifact_manifest.json'),'parent_server_sha256':sha(NATIVE/'server_build/ExecutionManager')})
print(SRC)
