"""Create an isolated successor with additional causal evidence, no control-law edits."""
from pathlib import Path
import shutil, difflib, hashlib, json

HERE = Path(__file__).resolve().parent
PRIOR = HERE.parent / 'gpibt_lsmart_integration_20260930'
PREVIOUS_NATIVE = Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence/gpibt_lsmart_integration_20260930')
OUT = PREVIOUS_NATIVE.with_name(PREVIOUS_NATIVE.name + '_r2')
SRC = OUT / 'lsmart_successor'
assert not SRC.exists(), 'isolated successor already exists'
previous = {str(p.relative_to(PRIOR)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(PRIOR.rglob('*')) if p.is_file()}
(HERE / 'previous_archive_manifest.json').write_text(json.dumps(previous, indent=2) + '\n')
for part in ('server', 'client'):
    shutil.copytree(PREVIOUS_NATIVE/'lsmart_successor'/part, SRC/part,
                    ignore=shutil.ignore_patterns('build', 'externalDependencies', '__pycache__'))
(SRC/'client/externalDependencies').symlink_to(PREVIOUS_NATIVE/'lsmart_successor/client/externalDependencies', target_is_directory=True)
for name in ('map.json', 'GPIBT_LICENSE.txt', 'LSMART_LICENSE.txt', 'gpibt_bridge.cpp'):
    shutil.copy2(PRIOR/name, HERE/name)
shutil.copy2(PREVIOUS_NATIVE/'gpibt_bridge', OUT/'gpibt_bridge')
changes = {}
def edit(name, old, new):
    p = SRC/name
    original = p.read_text()
    changes.setdefault(name, original)
    assert original.count(old) == 1, (name, old[:80], original.count(old))
    p.write_text(original.replace(old, new, 1))

# Server observes evidence only. Native completion remains in the native ADG.
edit('server/inc/ADG.h', '    bool isTaskNode(int robot_id, int node_id);', '''    bool isTaskNode(int robot_id, int node_id);
    int integrationTaskID(int agent_id, int node_id) {
        return graph[agent_id][node_id].action.task_id;
    }''')
edit('server/src/ExecutionManager.cpp', '    bool task=adg->isTaskNode(agent_id,node_ID);', '''    bool task=adg->isTaskNode(agent_id,node_ID);
    int task_id=adg->integrationTaskID(agent_id,node_ID);''')
edit('server/src/ExecutionManager.cpp', '{"goal",goal},{"task",task},{"accepted",status_update}', '{"goal",goal},{"task",task},{"task_id",task_id},{"accepted",status_update}')
edit('server/src/ExecutionManager.cpp', '    set<int> new_finished_tasks = this->adg->updateFinishedTasks();', '''    set<int> new_finished_tasks = this->adg->updateFinishedTasks();
    trace({{"kind","task_bookkeeping"},{"new_finished_tasks",new_finished_tasks}});''')
edit('server/src/ExecutionManager.cpp', '    this->adg->addMAPFPlan(actions);', '''    json parsed=json::array();
    for(const auto &plan:actions) {
        json agent=json::array();
        for(const auto &action:plan) agent.push_back({{"type",string(1,action.type)},
            {"start",action.start},{"goal",action.goal},{"orientation",action.orientation},
            {"task_id",action.task_id}});
        parsed.push_back(agent);
    }
    trace({{"kind","parsed"},{"proposal_id",new_plan_json.at("proposal_id")},{"actions",parsed}});
    this->adg->addMAPFPlan(actions);''')
edit('server/src/server.cpp', '    srv.bind("snapshot", []() {', '''    srv.bind("control_observe", [](string robot, string control) {
        lock_guard<mutex> guard(rpc_api::globalMutex);
        rpc_api::em->trace({{"kind","control"},{"robot",robot},{"control",json::parse(control)}});
    });
    srv.bind("snapshot", []() {''')
edit('server/src/ExecutionManager.cpp', '    this->curr_tick++;', '''    this->curr_tick++;
    if(simulationFinished()) trace({{"kind","horizon"},{"snapshot",snapshot()}});''')

# Capture actual controller queue before causal ACK, including native20 timer.
controller='client/controllers/footbot_diffusion/footbot_diffusion.cpp'
edit(controller, '#include "footbot_diffusion.h"', '#include "footbot_diffusion.h"\n#include "utils/json.hpp"')
edit(controller, '                << ",\\"queue_size\\":" << q.size()', '''                << ",\\"queue_size\\":" << q.size()
                << ",\\"previous_zero_command\\":" << (previous_zero_command?"true":"false")
                << ",\\"displacement_m\\":" << displacement''')
edit(controller, '    client->call("observe",robot_id,observation.str());', '''    client->call("observe",robot_id,observation.str());
    auto controlTrace = [&](const char* phase, const Action &current, bool paused) {
        nlohmann::json detail={{"phase",phase},{"type",static_cast<int>(current.type)},
            {"nodes",current.nodeIDS},{"task_id",current.task_id},{"timer",current.timer},
            {"target_x",current.x},{"target_y",current.y},{"paused",paused},{"queue_size",q.size()}};
        client->call("control_observe",robot_id,detail.dump());
    };''')
edit(controller, '        m_pcWheels->SetLinearVelocity(0.0f,0.0f);', '''        const Action current=q.empty()?a:q.front();
        controlTrace("pause",current,true);
        m_pcWheels->SetLinearVelocity(0.0f,0.0f);''')
edit(controller, '        a = q.front();\n        CVector3 targetPos = CVector3(a.x, a.y, 0.0f);', '''        a = q.front();
        controlTrace("front",a,false);
        CVector3 targetPos = CVector3(a.x, a.y, 0.0f);''')
edit(controller, '        q.front().timer--;', '''        controlTrace("service_decrement",q.front(),false);
        q.front().timer--;''')

patch=[]
manifest={}
for name, old in changes.items():
    new=(SRC/name).read_text()
    patch.extend(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/'+name,tofile='b/'+name))
    manifest[name]={'previous':hashlib.sha256(old.encode()).hexdigest(),'successor':hashlib.sha256(new.encode()).hexdigest()}
(HERE/'lsmart_integration_r2.patch').write_text(''.join(patch))
(HERE/'source_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(SRC)
