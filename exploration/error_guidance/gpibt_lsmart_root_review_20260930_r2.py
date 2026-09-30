"""Root review: immutable evidence plus an independent physical-service replay."""
from pathlib import Path
import collections
import hashlib
import importlib.util
import json
import math

HERE=Path(__file__).resolve().parent
ROOT=HERE/'gpibt_lsmart_integration_20260930_r2'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def need(condition, message):
    if not condition:
        raise ValueError(message)


def run():
    checks=[]
    manifest=json.loads((ROOT/'artifact_manifest.json').read_text())
    for name,digest in manifest.items():
        need(sha(ROOT/name)==digest,'archive bytes changed: '+name)
    checks.append('all archived bytes equal frozen manifest')
    identities=json.loads((ROOT/'binary_manifest.json').read_text())
    for path,digest in identities.items():
        need(sha(path)==digest,'runtime identity changed: '+path)
    checks.append('current official objects and final execution binaries')
    old_ids=json.loads((ROOT/'first_pair_binary_manifest.json').read_text())
    changed=[p for p in identities if identities[p]!=old_ids[p]]
    need(len(changed)==1 and Path(changed[0]).name=='ExecutionManager','unexpected planner/controller binary change')
    checks.append('wire correction changes only ExecutionManager identity')
    spec=importlib.util.spec_from_file_location('r2_execution_audit',ROOT/'audit.py')
    auditor=importlib.util.module_from_spec(spec);spec.loader.exec_module(auditor)
    recorded=json.loads((ROOT/'audit.json').read_text())
    results={}
    for trial in ('nominal','pause','nominal_retry01','pause_retry01'):
        path=ROOT/'attempts'/trial
        receipt=json.loads((path/'receipt.json').read_text())
        for name,digest in receipt['files'].items():
            need(sha(path/name)==digest,'native receipt bytes changed: '+trial+'/'+name)
        need(receipt['error'] is None,'native run did not complete: '+trial)
        need(all(x['before_cleanup']==0 for x in receipt['processes'][:2]),'server/simulator did not exit normally')
        need(receipt['fixed_horizon_ticks']==200 and receipt['seed']==42,'fixed contract changed')
        events=[json.loads(x) for x in (path/'events.jsonl').read_text().splitlines()]
        decisions=[json.loads(x) for x in (path/'decisions.jsonl').read_text().splitlines()]
        if not trial.endswith('retry01'):
            try:
                auditor.check(events,decisions,trial.startswith('pause'))
            except ValueError as error:
                need(str(error)=='admit_not_native_proposal_decomposition','wrong first-pair failure')
            else:
                raise ValueError('original omitted task wire was silently accepted')
            results[trial]={'native_complete':True,'strict_audit':False,'failure':'task wire omitted'}
            continue
        actual=auditor.check(events,decisions,trial.startswith('pause'))
        for key,value in actual.items():
            need(recorded['trials'][trial][key]==json.loads(json.dumps(value)),
                 'audit replay differs: '+trial+'/'+key)
        need(all(x['rejected'] for x in recorded['trials'][trial]['negative_checks'].values()),'negative not rejected')
        observations=collections.defaultdict(dict)
        admits={};service_ends=[];public_tasks={};prefix=[];bookkeeping=[]
        for e in events:
            if e['kind']=='observation':
                observations[e['robot']][e['tick']]=e['observation']
            elif e['kind']=='view':
                for agent,goals in enumerate(e['view']['mapf_instance']['goals']):
                    for goal in goals:
                        identity=(agent,goal['location'])
                        need(goal['id'] not in public_tasks or public_tasks[goal['id']]==identity,'public task changed')
                        if goal['id'] not in public_tasks:
                            prefix.append([goal['id'],*identity])
                        public_tasks[goal['id']]=identity
            elif e['kind']=='admit':
                for command in e['actions']:
                    admits[(command[0],command[1])]=command
            elif e['kind']=='end' and e['task']:
                service_ends.append(e)
            elif e['kind']=='task_bookkeeping':
                bookkeeping.extend((tid,e['tick']) for tid in e['new_finished_tasks'])
        need(len(service_ends)==1,'unexpected number of real task services')
        end=service_ends[0];robot=end['robot'];tid=end['task_id'];command=admits[(robot,end['node'])]
        need(command[3]=='S' and command[6]==tid==1,'task identity not carried end to end')
        need(public_tasks[tid]==(int(robot),7),'task service owner/goal mismatch')
        decrements=[e for e in events if e['kind']=='control' and e['robot']==robot
                    and e['control']['nodes'] and e['control']['nodes'][0]==end['node']
                    and e['control']['phase']=='service_decrement']
        need([e['control']['timer'] for e in decrements]==list(range(20,0,-1)),'not all real timer decrements')
        need([e['tick'] for e in decrements]==list(range(end['tick']-20,end['tick'])),'timer is not 20 consecutive control ticks')
        errors=[]
        for tick in range(end['tick']-20,end['tick']+1):
            o=observations[robot][tick]
            # task location 7 on width 5 => physical x=-row=-1, y=-col=-2
            errors.append(math.hypot(o['x']+1,o['y']+2))
        need(max(errors)<.03,'real service residence left native tolerance')
        need(len(bookkeeping)==1 and bookkeeping[0][0]==tid,'task bookkeeping missing or duplicated')
        need(bookkeeping[0][1]>end['tick'],'task counted before physical service END')
        need(any(e['kind']=='horizon' and e['tick']==200 for e in events),'no real fixed horizon')
        pause=[e for e in events if e['kind']=='control' and e['control']['phase']=='pause']
        need([e['tick'] for e in pause]==(list(range(30,50)) if trial.startswith('pause') else []),'pause contract changed')
        need(all(e['control']['nodes']==[] and e['control']['queue_size']==0 for e in pause),'pause interpretation changed')
        results[trial]={'native_complete':True,'strict_audit':True,'actual_pose_samples':actual['observation_count'],
                        'official_plan_calls':len(decisions),'task_services':len(service_ends),'service_tick':end['tick'],
                        'independent_residence_samples':len(errors),'independent_max_service_error_m':max(errors),
                        'actual_public_task_prefix':prefix,'pending_at_horizon':actual['horizon_unfinished_nodes'],
                        'latest_delivered_pose_tick':actual['latest_terminal_pose_tick'],'active_move_pause':False,
                        'negative_controls':len(recorded['trials'][trial]['negative_checks'])}
    need(results['nominal_retry01']['actual_public_task_prefix']==results['pause_retry01']['actual_public_task_prefix'],
         'actual prefixes are not paired in these two runs')
    return {'status':'passed','checks':checks,'archived_files_verified':len(manifest),
            'binary_and_objects_verified':len(identities),'trials':results,
            'scope':'two support trials plus independently replayed physical service; not a performance comparison',
            'continuous_footprint_safety_established':False,'active_move_disturbance_established':False,
            'trained_policy_baseline_qualified':False,'frozen_manifest_sha256':sha(ROOT/'artifact_manifest.json')}


if __name__=='__main__':
    result=run()
    target=HERE/'gpibt_lsmart_root_review_20260930_r2.json'
    with target.open('x') as out:
        json.dump(result,out,indent=2);out.write('\n')
    print(json.dumps(result,indent=2))
