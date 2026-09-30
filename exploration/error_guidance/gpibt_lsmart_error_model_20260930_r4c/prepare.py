from pathlib import Path
import json,hashlib,shutil,difflib
HERE=Path(__file__).resolve().parent;P=HERE.parent/'gpibt_lsmart_error_model_20260930_r4b';R=P.with_name('gpibt_lsmart_error_model_20260930_r4')
N=Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence/gpibt_lsmart_error_model_20260930_r4c');PN=N.with_name('gpibt_lsmart_error_model_20260930_r4')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):Path(p).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
assert not N.exists();parent=json.loads((P/'artifact_manifest.json').read_text())
for n,h in parent.items():assert sha(P/n)==h,n
write(HERE/'parent_archive_manifest.json',parent|{'artifact_manifest.json':sha(P/'artifact_manifest.json')})
N.mkdir();(N/'lsmart_successor').mkdir();shutil.copytree(PN/'lsmart_successor/server',N/'lsmart_successor/server')
(N/'lsmart_successor/client').symlink_to(PN/'lsmart_successor/client',target_is_directory=True)
for n in ['gpibt_bridge','client_build']:(N/n).symlink_to(PN/n,target_is_directory=n!='gpibt_bridge')
for n in ['trained_model.json','map.json','GPIBT_LICENSE.txt','LSMART_LICENSE.txt','gpibt_bridge.cpp','mapping_replay.py','export_data.py','audit.py']:shutil.copy2(P/n,HERE/n)
s=(P/'common.py').read_text().replace("gpibt_lsmart_error_model_20260930_r4b')","gpibt_lsmart_error_model_20260930_r4c')")
s=s.replace("if policy in ('zero','analytic'):","if policy in ('zero','analytic','fixed_agent0','fixed_agent1'):")
a="    bias=[0.,0.] if policy=='zero' or abs(predicted[0]-predicted[1])<1.0 else ([amplitude,-amplitude] if predicted[0]>predicted[1] else [-amplitude,amplitude])"
b="    bias=([1.,-1.] if policy=='fixed_agent0' else [-1.,1.]) if policy.startswith('fixed_agent') else ([0.,0.] if policy=='zero' or abs(predicted[0]-predicted[1])<1.0 else ([amplitude,-amplitude] if predicted[0]>predicted[1] else [-amplitude,amplitude]))"
assert s.count(a)==1;(HERE/'common.py').write_text(s.replace(a,b))
s=(P/'run_trial.py').read_text().replace("gpibt_lsmart_error_model_20260930_r4b')","gpibt_lsmart_error_model_20260930_r4c')").replace('port=9471','port=9481').replace('GPIBT_R0_SEED=str(seed)',"GPIBT_R0_SEED='42'").replace('400','800')
s=s.replace("'--task_assigner_type=one_goal']","'--task_assigner_type=one_goal',f'--task_file={HERE}/tasks.txt']")
s=s.replace("'calibration_rank_probe.json'","'tasks.txt','fifo_task.patch'")
(HERE/'run_trial.py').write_text(s)
runs=[{'id':f'test_s62_{c}_{pol}','split':'test','seed':62,'planner_initialization_seed':42,'condition':c,'policy':pol,'horizon_ticks':800} for c in ['nominal','slow065','slow085','axis','unknown_pause','unknown_shift'] for pol in ['zero','analytic','history','learned','fixed_agent0','fixed_agent1']]
write(HERE/'runs.json',{'protocol_sha256':sha(HERE/'PROTOCOL.md'),'runs':runs})
tasks=[[5,0]+[21,0]*32,[15,10]+[7,10]*32]
(HERE/'tasks.txt').write_text('2\n'+'\n'.join(';'.join(f'{g},-1,0,0' for g in gs) for gs in tasks)+'\n')
write(HERE/'task_environment.json',{'agent_goal_lists':tasks,'policy_may_read_future_lists':False,'task_file_sha256':sha(HERE/'tasks.txt'),'fixed_horizon':800})
file='server/src/task_assigners/OneGoalTaskAssigner.cpp';f=N/'lsmart_successor'/file;old=f.read_text();needle='    int next_goal;\n'
new='''    int next_goal;
    // Explicit task-file FIFO environment adapter. The controller/planner
    // receives only the currently revealed goal via the unchanged view API.
    if (!random_task) {
        if(tasks.at(agent_id).empty()) throw std::runtime_error("FIFO task file exhausted");
        next_goal=tasks.at(agent_id).front().location;
        tasks.at(agent_id).pop_front();
        return next_goal;
    }
'''
assert old.count(needle)==1;f.write_text(old.replace(needle,new))
(HERE/'fifo_task.patch').write_text(''.join(difflib.unified_diff(old.splitlines(True),f.read_text().splitlines(True),fromfile='a/'+file,tofile='b/'+file)))
snap=HERE/'source_snapshot'/file;snap.parent.mkdir(parents=True);snap.write_text(f.read_text())
write(HERE/'source_manifest.json',{file:{'parent':hashlib.sha256(old.encode()).hexdigest(),'successor':sha(f)}})
write(HERE/'native_source_tree_manifest.json',{'server_sources':{str(p.relative_to(N/'lsmart_successor')):sha(p) for p in (N/'lsmart_successor/server').rglob('*') if p.is_file()},'unchanged_client_native_root':str(PN/'lsmart_successor/client')})
write(HERE/'preflight_identity.json',{'protocol_sha256':sha(HERE/'PROTOCOL.md'),'runs_sha256':sha(HERE/'runs.json'),'parent_manifest_sha256':sha(P/'artifact_manifest.json')})
write(HERE/'model_freeze.json',{'files':{n:sha(HERE/n) for n in ['trained_model.json','common.py','export_data.py','PROTOCOL.md','tasks.txt','task_environment.json']},'amplitude':1.,'test_runs_started':False,'model_training_unchanged':True,'parent_model_sha256':sha(R/'trained_model.json')})
# Horizon is a new declared environment parameter; audit/export logic remains otherwise identical.
for name in ['mapping_replay.py','audit.py','export_data.py']:
 f=HERE/name;s=f.read_text().replace('400','800').replace('==800','==1600') if name=='audit.py' else f.read_text().replace('400','800');f.write_text(s)
# export source SHA is bound after the declared horizon adaptation.
v=json.loads((HERE/'model_freeze.json').read_text());v['files']['export_data.py']=sha(HERE/'export_data.py');write(HERE/'model_freeze.json',v)
print(N)
