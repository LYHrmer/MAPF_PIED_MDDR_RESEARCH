"""Independent full source, split, native closed-world causal replay and true fit audit."""
from collections import Counter,deque
from copy import deepcopy
from fractions import Fraction
import hashlib,json
from pathlib import Path
import numpy as np
from audit_joint_replay import Replay,HERE,ROOT,bind_source,sha,require
def write(p,o):
    with p.open('x') as f:json.dump(o,f,indent=2);f.write('\n')
def main():
    out=HERE/'scheduled_successor_01';reg=json.loads((HERE/'native_attempt_01/REGISTRATION.json').read_text());rec=json.loads((out/'RECEIPT.json').read_text())
    sup=json.loads((HERE/'SUPPORT_AUDIT_60.json').read_text());model=json.loads((out/'MODEL_FROZEN_BEFORE_TEST.json').read_text())
    require(rec['complete'] and rec['all_native_passed'] and len(rec['episodes'])==598,'complete registered native sequence')
    require(all(sha(HERE/p)==h for p,h in reg['frozen'].items()),'frozen pre-run code/contract/input identity')
    d=json.loads((HERE/'author_60.json').read_text());paths=[p.split(',') for p in d['actualPaths']];D={'EA':(1,0),'WE':(-1,0),'NO':(0,-1),'SO':(0,1),'W':(0,0)}
    pre=json.loads((ROOT/'implementation_binding_evidence/baseline_selection_20260929/pied_preflight.json').read_text())
    base=ROOT/'implementation_binding_evidence/baseline_selection_20260929/PIED-full';rel='lifelong_benchmark/random/maps/random-32-32-20.map';mp=base/rel
    require(sha(mp)==pre['manifest'][rel]['sha256'],'source original map');grid=mp.read_text().splitlines()[4:]
    positions=[[(c,r) for r,c,_ in d['start']]]
    for tick in range(60):
        before=positions[-1];after=[(x+D[paths[a][tick]][0],y+D[paths[a][tick]][1]) for a,(x,y) in enumerate(before)]
        require(len(set(after))==100,'full source vertex conflict')
        require(all(grid[y][x]=='.' for x,y in after),'full source obstacle/support')
        require(not any(before[a]==after[b] and before[b]==after[a] and before[a]!=after[a] for a in range(100) for b in range(a+1,100)),'full source edge swap')
        positions.append(after)
    goals={tid:(c,r) for tid,r,c in d['tasks']};services=0
    for a,events in enumerate(d['events']):
        q=deque()
        for tid,t,k in events:
            if k=='assigned':q.append(tid)
            else:
                require(k=='finished' and q.popleft()==tid and positions[t][a]==goals[tid],'official source FIFO task service');services+=1
    require(services==d['numTaskFinished']==206,'source reported tasks recomputed')
    generation=json.loads((HERE/'SOURCE_REGISTRATION_20260930_r4.json').read_text());receipt=json.loads((HERE/'author_60.receipt.json').read_text())
    require(generation['command']==receipt['command'] and receipt['returncode']==0,'actual official source generation command')
    require(sha(Path(generation['binary']))==generation['binary_sha256'] and sha(Path(generation['configuration']))==generation['configuration_sha256'],'original official input/runner unchanged')
    cohorts={c['cohort_id']:c for c in sup['cohorts']};used=set();split={}
    for i,c in enumerate(cohorts.values()):
        require(c['split']==['train','train','train','calibration','test'][i%5],'predeclared whole-cohort split')
        tasks={r['task'] for r in c['robots']};require(not tasks&used and not tasks&{14,22,99,118},'cohort task overlap/R3 leakage');used|=tasks
        require(max(len(r['route']) for r in c['robots'])<=16,'fixed finite head support');bind_source(c);split.setdefault(c['split'],[]).append(c['cohort_id'])
    require({k:len(v) for k,v in split.items()}=={'train':8,'calibration':2,'test':2} and len(used)==48,'support groups and split')
    worlds={w['world_id']:w for w in reg['worlds']};training=json.loads((HERE.parent/'public_joint_20260930_r3/public_training_END_20260930_r3.json').read_text())
    coefficients=[Fraction(z) for z in model['coefficients']];audits=[];records_by={};episode_by={}
    for e in rec['episodes']:
        w=worlds[e['world_id']];c=cohorts[w['cohort_id']]
        require(e['split']==w['split']==c['split'],'whole-world/cohort identity')
        require(sha(Path(e['raw']))==e['raw_sha256'] and sha(Path(e['input']))==e['input_sha256'],'actual native raw/input binding')
        expected=[];sources=w['sources'];k=w['case']
        for r in c['robots']:
            for leg,h in enumerate(r['route']):
                eta=0
                if 'corner' in k and leg==0 and r['agent'] in sources:eta=k['corner'][sources.index(r['agent'])]
                elif 'seed' in k and h!='W':
                    word=hashlib.sha256(f"{k['seed']}:{c['cohort_id']}:{r['agent']}:{leg}".encode()).digest()[:8]
                    preferred=-1 if h in ['NO','SO'] else 1;eta=preferred if int.from_bytes(word,'big')%10<9 else -preferred
                expected.append(dict(agent=r['agent'],leg=leg,heading=h,eta=eta))
        require(expected==w['private_world_only'],'fixed exogenous full-world inputs')
        records=[json.loads(x) for x in Path(e['raw']).read_text().splitlines()]
        actor=Replay(c,w,e['policy'],e['capacity'],training);actor.coefficients=coefficients
        obj=actor.run(records);require(all(x['at']['upper']<=750000 for x in records if x['event']=='actor_decision'),'first opportunity only; no future adaptive query')
        obj.update(world_id=w['world_id'],cohort_id=c['cohort_id'],split=c['split'],policy=e['policy'],capacity=e['capacity'],raw_sha256=e['raw_sha256'])
        audits.append(obj);key=(w['world_id'],e['policy']);require(key not in episode_by,'duplicate native arm');episode_by[key]=obj;records_by[key]=records
    require(len(worlds)==156,'13 complete worlds per cohort')
    for w in worlds.values():
        policies={'WAIT'}|{'forced_'+str(a) for a in w['sources']}
        if w['split']=='test':policies|={'RR','probability','task_rank','structural','ridge'}
        require({p for wid,p in episode_by if wid==w['world_id']}==policies,'complete registered whole-world arm set')
    labels=json.loads((out/'ALL_COUNTERFACTUAL_LABELS.json').read_text());require(len(labels)==312,'all source action counterfactual labels')
    for r in labels:
        wait=episode_by[(r['world_id'],'WAIT')];act=episode_by[(r['world_id'],'forced_'+str(r['source']))]
        exact_gain=float(wait['restricted_flow_sum'])-float(act['restricted_flow_sum'])
        require(abs(float(Fraction(r['target_flow_gain']))-exact_gain)<=1.00001e-6,'independent actual task marginal label')
        require(r['extra_heads']==act['served']-wait['served'],'true marginal task completion label')
        decision=next(x for x in records_by[(r['world_id'],'forced_'+str(r['source']))] if x['event']=='actor_decision')
        cand=next(x for x in decision['candidates'] if x['agent']==r['source']);require(cand['features']==r['features'],'label features public before actual query')
    train=[r for r in labels if r['split']=='train'];X=np.array([[1]+[float(Fraction(z)) for z in r['features']] for r in train]);y=np.array([float(Fraction(r['target_flow_gain'])) for r in train])
    penalty=np.eye(11);penalty[0,0]=0;fit=np.linalg.solve(X.T@X+penalty,X.T@y)
    require(model['train_rows']==208 and model['train_cohorts']==split['train'] and not model['used_test_for_fit'] and not model['used_calibration_for_fit'],'true train-only fit contract')
    require([Fraction(str(round(float(z),9))) for z in fit]==coefficients,'independently refit exported true ridge coefficients')
    require(sha(out/'MODEL_FROZEN_BEFORE_TEST.json')==rec['model_sha256'],'frozen trained model binding')
    controls=[];example=next(e for e in rec['episodes'] if e['policy']=='ridge' and any(x['event']=='task_service' for x in records_by[(e['world_id'],'ridge')]));w=worlds[example['world_id']];c=cohorts[w['cohort_id']];original=records_by[(w['world_id'],'ridge')]
    bad=deepcopy(original);next(x for x in bad if x['event']=='actor_decision')['eta']=1
    bad2=deepcopy(original);next(x for x in bad2 if x['event']=='actor_decision')['candidates'][0]['features'][6]='1'
    bad3=deepcopy(original);next(x for x in bad3 if x['event']=='task_service')['task']=999
    bad4=deepcopy(original);next(x for x in bad4 if x['event']=='actor_decision')['candidates'][0]['score']='999999'
    for name,records in [('private actor feature',bad),('forged public graph feature',bad2),('future/wrong task service',bad3),('untrained wrong coefficient score',bad4),('native truncation',original[:-1])]:
        a=Replay(c,w,'ridge',1,training);a.coefficients=coefficients
        try:a.run(records)
        except AssertionError as ex:controls.append(dict(name=name,rejected=True,reason=str(ex)))
        else:raise AssertionError('negative escaped '+name)
    parent=HERE.parent/'public_joint_20260930_r3';pm=json.loads((parent/'FROZEN_MANIFEST_20260930_r3.json').read_text())
    require(all(sha(parent/p)==h['sha256'] for p,h in pm['frozen_files'].items()),'154 frozen R3 files changed')
    require(all(sha(ROOT/p)==h for p,h in reg['production_headers'].items()),'9 production headers changed')
    result=dict(status='passed',native_episodes=len(audits),worlds=156,cohorts=12,split_cohorts=split,task_disjoint_heads=48,original_source_actions=6000,
       original_source_tasks=services,native_MOVEs=sum(a['original_MOVEs'] for a in audits),normal_END_feedback=sum(a['END_feedback'] for a in audits),
       actual_queries=sum(a['queries'] for a in audits),world_frames=sum(a['frames'] for a in audits),true_train_only_refit=True,trained_model_sha256=rec['model_sha256'],
       mutations=controls,episodes=audits,source_maps=1,formal_external_comparison=False,production_COST=False,R3_154_and_production_9_unchanged=True)
    write(HERE/'AUDIT.json',result);print({k:v for k,v in result.items() if k not in ['episodes','mutations']})
if __name__=='__main__':main()
