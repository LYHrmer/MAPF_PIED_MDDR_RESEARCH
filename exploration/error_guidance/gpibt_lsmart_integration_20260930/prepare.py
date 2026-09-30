"""Create isolated LSMART successor; never modify old source/build evidence."""
from pathlib import Path
import shutil, difflib, json
OLD=Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence/baseline_selection_20260929')
OUT=Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence/gpibt_lsmart_integration_20260930')
HERE=Path(__file__).resolve().parent
SRC=OUT/'lsmart_successor'
assert not SRC.exists()
for part in ['server','client']:
    shutil.copytree(OLD/'lsmart_compat'/part,SRC/part,ignore=shutil.ignore_patterns('build','externalDependencies','__pycache__'))
(SRC/'client/externalDependencies').symlink_to(OLD/'lsmart_compat/client/externalDependencies',target_is_directory=True)
changes={}
def edit(name,old,new):
    p=SRC/name
    s=p.read_text()
    changes.setdefault(name,s)
    assert old in s, (name,old[:80])
    p.write_text(s.replace(old,new,1))

# Each event records actual causal server order. Planner snapshots exclude future truth.
edit('server/inc/ExecutionManager.h','private:\n    // Setup the heuristic table', '''public:
    json delivered_observations = json::object();
    void trace(json record);
    bool jointSettled();
    json snapshot();
private:
    // Setup the heuristic table''')
edit('server/src/ExecutionManager.cpp','#include "ExecutionManager.h"','''#include "ExecutionManager.h"
#include <cstdlib>
void ExecutionManager::trace(json record) {
    static std::ofstream out(std::getenv("INTEGRATION_TRACE"));
    static unsigned long long sequence = 0;
    record["sequence"] = sequence++;
    record["tick"] = getCurrSimStep();
    out << record.dump() << std::endl;
}
bool ExecutionManager::jointSettled() {
    if (!isADGInitialized()) return false;
    if (plannerNeverInvoked()) return true;
    for(int a=0; a<numRobots; ++a) {
        if(adg->getNumUnfinishedActions(a) != 0) return false;
        const auto id=adg->robotIDToStartIndex.at(a);
        if(!delivered_observations.contains(id)) return false;
        const auto o=delivered_observations.at(id);
        if(!o.at("idle").get<bool>() || o.at("tick").get<int>() < getCurrSimStep()-1) return false;
    }
    return true;
}
json ExecutionManager::snapshot() {
    json r={{"tick",getCurrSimStep()},{"observations",delivered_observations},{"joint_settled",jointSettled()}};
    r["unfinished"]=json::array();
    for(int a=0;a<numRobots;++a) r["unfinished"].push_back(adg->getNumUnfinishedActions(a));
    return r;
}
''')
edit('server/src/ExecutionManager.cpp','void ExecutionManager::freezeSimulationIfNecessary() {','''void ExecutionManager::freezeSimulationIfNecessary() {
    if (planner_invoke_policy == "joint_settled") {
        if (jointSettled() && !simulationFinished()) freeze_simulation = true;
        return;
    }''')
edit('server/src/ExecutionManager.cpp','bool ExecutionManager::invokePlanner() {','''bool ExecutionManager::invokePlanner() {
    if (planner_invoke_policy == "joint_settled") {
        if (!freeze_simulation || planner_running || !jointSettled() || simulationFinished()) return false;
        if (plannerNeverInvoked()) start_time=std::chrono::steady_clock::now();
        prev_invoke_planner_tick=getCurrSimStep();
        planner_running=true;
        planner_invoke_ticks.push_back(getCurrSimStep());
        trace({{"kind","invoke"},{"snapshot",snapshot()}});
        return true;
    }''')
edit('server/src/ExecutionManager.cpp','    return result_message.dump();\n}\n\n// Add a new MAPF plan','''    trace({{"kind","view"},{"view",result_message},{"snapshot",snapshot()}});
    return result_message.dump();
}

// Add a new MAPF plan''')
edit('server/src/ExecutionManager.cpp','    json new_plan_json = json::parse(new_plan_json_str);','''    json new_plan_json = json::parse(new_plan_json_str);
    trace({{"kind","proposal"},{"proposal",new_plan_json}});''')
edit('server/src/ExecutionManager.cpp','    bool status_update = this->adg->updateFinishedNode(agent_id, node_ID);','''    auto goal = adg->getActionGoal(agent_id,node_ID);
    bool task=adg->isTaskNode(agent_id,node_ID);
    bool status_update = this->adg->updateFinishedNode(agent_id, node_ID);
    trace({{"kind","end"},{"robot",robot_id_str},{"agent",agent_id},{"node",node_ID},
           {"goal",goal},{"task",task},{"accepted",status_update},{"observation",delivered_observations.value(robot_id_str,json())}});''')
edit('server/src/ExecutionManager.cpp','    return this->adg->getPlan(Robot_ID);','''    auto actions=this->adg->getPlan(Robot_ID);
    if(!actions.empty()) trace({{"kind","admit"},{"robot",RobotID},{"agent",Robot_ID},{"actions",actions}});
    return actions;''')
edit('server/src/server.cpp','    srv.bind("receive_update", &rpc_api::actionFinished);','''    srv.bind("observe", [](string robot, string observation) {
        lock_guard<mutex> guard(rpc_api::globalMutex);
        auto o=json::parse(observation);
        o["tick"]=rpc_api::em->getCurrSimStep();
        rpc_api::em->delivered_observations[robot]=o;
        rpc_api::em->trace({{"kind","observation"},{"robot",robot},{"observation",o}});
    });
    srv.bind("snapshot", []() {
        lock_guard<mutex> guard(rpc_api::globalMutex);
        return rpc_api::em->snapshot().dump();
    });
    srv.bind("receive_update", &rpc_api::actionFinished);''')

# Client observation precedes normal controller acknowledgement. Pause is one
# exogenous physical-time interval; it is not transmitted to the planner.
edit('client/controllers/footbot_diffusion/footbot_diffusion.h','    int count = 0;','    int count = 0;\n    bool previous_zero_command = true;\n    CVector3 previous_observed_position;\n    bool have_previous_observation = false;')
edit('client/controllers/footbot_diffusion/footbot_diffusion.cpp','    CVector3 currPos = m_pcPosSens->GetReading().Position;','''    CVector3 currPos = m_pcPosSens->GetReading().Position;
    const double displacement = have_previous_observation ? (currPos - previous_observed_position).Length() : 0.0;
    previous_observed_position = currPos;
    have_previous_observation = true;
    std::ostringstream observation;
    observation << std::setprecision(17) << "{\\"x\\":" << currPos.GetX()
                << ",\\"y\\":" << currPos.GetY() << ",\\"angle\\":" << currAngle
                << ",\\"speed_cm_s\\":" << prevVelocity_
                << ",\\"queue_size\\":" << q.size()
                << ",\\"idle\\":" << ((q.empty() && previous_zero_command && displacement <= 1e-6)?"true":"false") << "}";
    client->call("observe",robot_id,observation.str());
    const char* pause=std::getenv("INTEGRATION_PAUSE");
    if (pause && std::string(pause)=="1" && robot_id=="0" && count>=30 && count<50) {
        m_pcWheels->SetLinearVelocity(0.0f,0.0f);
        previous_zero_command=true;
        ++count; ++step_count_;
        return;
    }''')
edit('client/controllers/footbot_diffusion/footbot_diffusion.cpp','    auto end = std::chrono::high_resolution_clock::now();\n    std::chrono::duration<double, milli> exec_duration_ms','''    previous_zero_command = (a.type == Action::STOP || a.type == Action::STATION);
    auto end = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double, milli> exec_duration_ms''')
patch=[]
for name,original in changes.items():
    patch.extend(difflib.unified_diff(original.splitlines(True),(SRC/name).read_text().splitlines(True),fromfile='a/'+name,tofile='b/'+name))
(HERE/'lsmart_integration.patch').write_text(''.join(patch))
shutil.copy2(OLD/'lsmart_compat/maps/front_fig_5x5.json',HERE/'map.json')
shutil.copy2(OLD/'lsmart_compat/LICENSE.txt',HERE/'LSMART_LICENSE.txt')
shutil.copy2(OLD/'gpibt_seeded_trace_successor/LICENCE.txt',HERE/'GPIBT_LICENSE.txt')
print(SRC)
