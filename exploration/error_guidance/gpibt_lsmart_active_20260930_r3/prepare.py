"""Clone the frozen task-wire-corrected parent; only active intervention/observation changes."""
from pathlib import Path
import difflib, hashlib, json, shutil

HERE=Path(__file__).resolve().parent
PRIOR=HERE.parent/'gpibt_lsmart_integration_20260930_r2'
PARENT=Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence/gpibt_lsmart_integration_20260930_r2')
OUT=PARENT.with_name('gpibt_lsmart_active_20260930_r3')
SRC=OUT/'lsmart_successor'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not OUT.exists(), 'new native successor already exists'
old={str(p.relative_to(PRIOR)):sha(p) for p in sorted(PRIOR.rglob('*')) if p.is_file() and '__pycache__' not in p.parts}
for p,h in json.loads((PRIOR/'artifact_manifest.json').read_text()).items():assert sha(PRIOR/p)==h,p
(HERE/'previous_archive_manifest.json').write_text(json.dumps(old,indent=2)+'\n')
for part in ('server','client'):
    shutil.copytree(PARENT/'lsmart_successor'/part,SRC/part,ignore=shutil.ignore_patterns('build','externalDependencies','__pycache__'))
(SRC/'client/externalDependencies').symlink_to(PARENT/'lsmart_successor/client/externalDependencies',target_is_directory=True)
for name in ('map.json','GPIBT_LICENSE.txt','LSMART_LICENSE.txt','gpibt_bridge.cpp'):
    shutil.copy2(PRIOR/name,HERE/name)
shutil.copy2(PRIOR/'audit.py',HERE/'parent_mapping_audit.py')
shutil.copy2(PARENT/'gpibt_bridge',OUT/'gpibt_bridge')
(OUT/'server_build').mkdir()
shutil.copy2(PARENT/'server_build/ExecutionManager',OUT/'server_build/ExecutionManager')
parent_sources={str(p.relative_to(SRC)):sha(p) for p in sorted(SRC.rglob('*')) if p.is_file() and 'externalDependencies' not in p.parts}
changes={}
def edit(name,old,new):
    p=SRC/name;s=p.read_text();changes.setdefault(name,s)
    assert s.count(old)==1,(name,old[:100],s.count(old))
    p.write_text(s.replace(old,new,1))

header='client/controllers/footbot_diffusion/footbot_diffusion.h'
edit(header,'private:\n    Real pidLinear(Real error);','''private:
    // Observe the actual arguments sent to the actuator; native control laws
    // and every original argument expression remain unchanged.
    void integrationSetWheels(Real left, Real right) const {
        integration_left_command=left; integration_right_command=right;
        m_pcWheels->SetLinearVelocity(left,right);
    }
    Real pidLinear(Real error);''')
edit(header,'    int count = 0;','''    int count = 0;
    mutable Real integration_left_command = 0.0;
    mutable Real integration_right_command = 0.0;
    int integration_trigger_tick = -1;
    bool integration_resumed = false;''')
cpp='client/controllers/footbot_diffusion/footbot_diffusion.cpp'
p=SRC/cpp;before=p.read_text();changes[cpp]=before
assert before.count('m_pcWheels->SetLinearVelocity(')==6
p.write_text(before.replace('m_pcWheels->SetLinearVelocity(','integrationSetWheels('))
edit(cpp,'    Real left_v, right_v;\n    CVector3 currPos', '    const int integration_step_tick=count;\n    Real left_v, right_v;\n    CVector3 currPos')
edit(cpp,'                << ",\\"previous_zero_command\\":" << (previous_zero_command?"true":"false")','''                << ",\\"previous_zero_command\\":" << (previous_zero_command?"true":"false")
                << ",\\"previous_wheel_left_cm_s\\":" << integration_left_command
                << ",\\"previous_wheel_right_cm_s\\":" << integration_right_command''')
edit(cpp,'    auto controlTrace = [&](const char* phase, const Action &current, bool paused) {','''    const char* pause=std::getenv("INTEGRATION_PAUSE");
    const bool integration_pause=pause && std::string(pause)=="1";
    auto controlTrace = [&](const char* phase, const Action &current, bool paused) {''')
edit(cpp,'            {"target_x",current.x},{"target_y",current.y},{"paused",paused},{"queue_size",q.size()}};','''            {"target_x",current.x},{"target_y",current.y},{"paused",paused},{"queue_size",q.size()},
            {"controller_tick",integration_step_tick},{"trigger_tick",integration_trigger_tick},
            {"mode",integration_pause?"pause":"nominal"},{"displacement_m",displacement},
            {"issued_left_cm_s",integration_left_command},{"issued_right_cm_s",integration_right_command}};''')
edit(cpp,'''    const char* pause=std::getenv("INTEGRATION_PAUSE");
    if (pause && std::string(pause)=="1" && robot_id=="0" && count>=30 && count<50) {
        const Action current=q.empty()?a:q.front();
        controlTrace("pause",current,true);
        integrationSetWheels(0.0f,0.0f);
        previous_zero_command=true;
        ++count; ++step_count_;
        return;
    }''','''    if (robot_id=="0" && integration_trigger_tick<0 && !q.empty() &&
        q.front().type==Action::MOVE && !q.front().nodeIDS.empty() &&
        (integration_left_command!=0.0 || integration_right_command!=0.0) && displacement>1e-6) {
        integration_trigger_tick=count;
        controlTrace("active_trigger",q.front(),false);
    }
    if (integration_pause && robot_id=="0" && integration_trigger_tick>=0 &&
        count>=integration_trigger_tick && count<integration_trigger_tick+20) {
        const Action current=q.front();
        integrationSetWheels(0.0f,0.0f);
        previous_zero_command=true;
        controlTrace("pause",current,true);
        controlTrace("wheel_command",current,true);
        ++count; ++step_count_;
        return;
    }
    if (integration_pause && robot_id=="0" && integration_trigger_tick>=0 &&
        count==integration_trigger_tick+20 && !integration_resumed) {
        integration_resumed=true;
        controlTrace("active_resume",q.front(),false);
    }''')
edit(cpp,'    previous_zero_command = (a.type == Action::STOP || a.type == Action::STATION);','''    previous_zero_command = (a.type == Action::STOP || a.type == Action::STATION);
    controlTrace("wheel_command",q.empty()?Action{}:q.front(),false);''')
patch=[];manifest={}
for name,old in changes.items():
    new=(SRC/name).read_text()
    patch.extend(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/'+name,tofile='b/'+name))
    manifest[name]={'previous':hashlib.sha256(old.encode()).hexdigest(),'successor':sha(SRC/name)}
    snap=HERE/'source_snapshot'/name;snap.parent.mkdir(parents=True,exist_ok=True);snap.write_text(new)
(HERE/'active_move_r3.patch').write_text(''.join(patch))
(HERE/'source_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
(HERE/'native_source_tree_manifest.json').write_text(json.dumps({'parent':parent_sources,'successor':{name:sha(SRC/name) for name in parent_sources}},indent=2)+'\n')
(HERE/'preflight_identity.json').write_text(json.dumps({'protocol_sha256':sha(HERE/'PROTOCOL.md'),'prepare_sha256':sha(HERE/'prepare.py'),'direct_parent_artifact_manifest_sha256':sha(PRIOR/'artifact_manifest.json'),'fixed_rule':'first_agent0_front_MOVE_unACK_prior_actual_nonzero_wheels_displacement_gt_1e-6','pause_duration_ticks':20,'horizon_ticks':200,'seed':42,'copied_server_sha256':sha(OUT/'server_build/ExecutionManager'),'copied_bridge_sha256':sha(OUT/'gpibt_bridge')},indent=2)+'\n')
print(SRC)
