"""Strict END-only actor replay. No current-phase source truth is passed into choose."""
from collections import Counter,defaultdict
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

HERE=Path(__file__).resolve().parent
ROOT=Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH')
QUERY=HERE.parent.parent
ALLOWED={'run_id','tick','agent','heading','original_END','received','full_cap_uninterrupted','length'}

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def bound(v):return F(v['lower'],v['denominator']),F(v['upper'],v['denominator'])

def decode_END_only(observation):
    assert set(observation)==ALLOWED,'non-END or private field in actor observation'
    assert observation['full_cap_uninterrupted'] and observation['length']==1,'unsupported END inverse domain'
    lo,hi=bound(observation['original_END']);assert hi<F(5,4) or lo>F(5,4),'END duration cannot identify profile class'
    return int(hi<F(5,4))

def choose_END_only(pairs,model,history,run_id,tick):
    # Deliberately no regime, private eta, physics/controller or current END argument.
    arms={}
    for arm in ['WAIT','global_bin','direction_bin','categorical_supervised','analytic_direction','lag2','RR']:
        candidates=[]
        for p in pairs:
            h=p['source_heading'];a=p['source_agent'];prior=history.get(a,[])
            for obs in prior:
                assert obs['run_id']==run_id and obs['tick']<tick
                assert bound(obs['received'])[1]+4*obs['tick']<4*tick,'current or future END arrived too late'
                decode_END_only(obs)
            if arm=='WAIT':prob=F(0)
            elif arm=='RR':prob=F(1)
            elif arm=='global_bin':prob=model['global']
            elif arm in ['direction_bin','categorical_supervised']:prob=model['direction'][h]
            elif arm=='analytic_direction':prob=F(1,10) if h in ['NO','SO'] else F(9,10)
            elif arm=='lag2':prob=F(decode_END_only(prior[-2])) if len(prior)>=2 else model['global']
            else:raise AssertionError(arm)
            candidates.append({'pair':p['pair'],'p_release':str(prob),'terminal':p['terminal'],'score':str(prob if p['terminal'] else 0),
                'heading':h,'history_row_ids':[f'{o["run_id"]}:{o["tick"]}:{o["agent"]}' for o in prior] if arm=='lag2' else []})
        positive=[c for c in candidates if F(c['score'])>0]
        selected=min(positive,key=lambda c:(-F(c['score']),c['pair']))['pair'] if positive else None
        arms[arm]={'selected_pair':selected,'query_capacity':1,'candidates':candidates,'uses_current_truth':False}
    return arms

def qualification():
    pins=json.loads((QUERY/'legal_and_sources.json').read_text())
    result={'status':'failed','purpose':'original full-cap profile inverse qualification, not test fitting','commands':[]}
    with tempfile.TemporaryDirectory(prefix='query_END_only_') as td:
        tmp=Path(td)
        for rel,s in pins.items():assert sha(ROOT/rel)==s;(tmp/Path(rel).name).write_bytes((ROOT/rel).read_bytes())
        sdk=ROOT/'third_party/host_sdk/usr';library=ROOT/'third_party/flint_host_config';binary=tmp/'native'
        cmd=['rtk','proxy','g++-11','-std=c++14','-O2','-Wall','-Wextra','-Werror','-pedantic','-fno-elide-constructors',
             '-I',str(tmp),'-isystem',str(sdk/'include'),'-isystem',str(library/'src'),str(HERE/'native_semantic_20260930_r2.cpp'),
             '-L',str(library),'-L',str(sdk/'lib/x86_64-linux-gnu'),f'-Wl,-rpath,{library}','-lflint','-lmpfr','-lgmp','-o',str(binary)]
        for argv,limit in [(cmd,120)]:
            p=subprocess.run(argv,capture_output=True,text=True,timeout=limit)
            result['commands'].append({'argv':argv,'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr,'timeout_seconds':limit})
            assert p.returncode==0
        inp=tmp/'qualification.txt';inp.write_text('M 0 0 0 1 0 -1\nM 1 0 1 1 1 0\nM 2 0 2 1 2 1\n')
        argv=['rtk','proxy',str(binary),str(inp)];p=subprocess.run(argv,capture_output=True,text=True,timeout=60)
        result['commands'].append({'argv':argv,'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr,'timeout_seconds':60})
        assert p.returncode==0;events=[json.loads(s) for s in p.stdout.splitlines() if s.startswith('{')]
        profiles=[]
        for e in events:
            if e['event']!='source_original_END_delivered':continue
            observation={'run_id':'qualification','tick':0,'agent':e['agent'],'heading':'EA',
                'original_END':e['original_END'],'received':e['received'],'full_cap_uninterrupted':True,'length':1}
            label=decode_END_only(observation);qlo,qhi=bound(e['at_query_progress'])
            assert (qlo>F(13,20) if label else qhi<=F(13,20))
            profiles.append({'public_eta':[-1,0,1][e['agent']],'public_END':e['original_END'],'END_only_class':label,
                             'offline_progress_validation':e['at_query_progress']})
        assert [p['END_only_class'] for p in profiles]==[0,0,1]
        result.update(status='passed',native_binary_sha256=sha(binary),native_source_sha256=sha(HERE/'native_semantic_20260930_r2.cpp'),profiles=profiles)
    with (HERE/'end_only_qualification_20260930_r2.json').open('x') as f:json.dump(result,f,indent=2)
    return result

def rejected(fn):
    try:fn()
    except AssertionError:return True
    return False

def run():
    qualification()
    receipt=json.loads((HERE/'receipt_20260930_r2.json').read_text());public=json.loads((HERE/'public_source_20260930_r2.json').read_text())
    assert receipt['status']=='passed';training=[];model=None;rows=[];observations=0;comparisons=0;actor_inputs=[]
    for run in receipt['runs']:
        history=defaultdict(list);run_phases=[]
        for phase in run['phases']:
            tick=phase['tick'];pairs=public['phases'][tick]['pairs']
            choices=choose_END_only(pairs,model,history,run['run_id'],tick) if model else {}
            assert choices==phase['choices'];comparisons+=len(choices)
            run_phases.append({'tick':tick,'choices':choices,'END_observations_before_choice':sum(map(len,history.values()))})
            # Deliver native END records only AFTER choosing this phase.
            c=receipt['commands'][phase['command_index']]
            events=[json.loads(s) for s in c['stdout'].splitlines() if s.startswith('{')]
            heading={m['agent']:m['heading'] for m in public['phases'][tick]['moves']}
            for e in events:
                if e['event']!='source_original_END_delivered':continue
                obs={'run_id':run['run_id'],'tick':tick,'agent':e['agent'],'heading':heading[e['agent']],
                     'original_END':e['original_END'],'received':e['received'],
                     'full_cap_uninterrupted':e['full_cap_uninterrupted'],'length':e['length']}
                label=decode_END_only(obs);history[e['agent']].append(obs);actor_inputs.append(obs);observations+=1
                if run['split']=='train':training.append((obs['heading'],label))
        if run['run_id']=='train_2207':
            counts=defaultdict(Counter);all_count=Counter()
            for h,label in training:counts[h][label]+=1;all_count[label]+=1
            model={'direction':{h:F(c[1]+1,sum(c.values())+2) for h,c in counts.items()},
                   'global':F(all_count[1]+1,sum(all_count.values())+2)}
            assert {h:str(v) for h,v in model['direction'].items()}==receipt['frozen_models']['direction']
            assert str(model['global'])==receipt['frozen_models']['global']
        rows.append({'run_id':run['run_id'],'split':run['split'],'phases':run_phases})
    example=actor_inputs[0];private=dict(example,at_query_progress={'lower':0,'upper':0,'denominator':1})
    current=dict(example,tick=3,run_id='negative')
    badhistory={public['pairs'][0]['source_agent']:[current]}
    negative={'private_progress_rejected':rejected(lambda:decode_END_only(private)),
              'current_or_future_END_as_past_history_rejected':rejected(lambda:choose_END_only([public['pairs'][0]],model,badhistory,'negative',3)),
              'unsupported_interrupted_motion_rejected':rejected(lambda:decode_END_only(dict(example,full_cap_uninterrupted=False)))}
    assert all(negative.values()) and observations==10746 and comparisons==560
    out={'status':'passed','kind':'offline causal actor replay over all actually executed native potential outcomes',
         'native_rerun':False,'original_native_receipt_sha256':sha(HERE/'receipt_20260930_r2.json'),
         'contract_sha256':sha(HERE/'END_ONLY_REPLAY_CONTRACT_20260930_r2.md'),'decoded_END_only_observations':observations,
         'actor_choice_comparisons':comparisons,'all_model_probabilities_scores_histories_choices_identical':True,
         'private_fields_enter_END_only_actor':False,'test_ENDs_used_for_fit':False,'negative_controls':negative,
         'actor_observation_schema':sorted(ALLOWED),'actor_observations':actor_inputs,'runs':rows}
    with (HERE/'end_only_replay_20260930_r2.json').open('x') as f:json.dump(out,f,indent=2)
    print(json.dumps({k:v for k,v in out.items() if k not in ['actor_observations','runs']},indent=2))

if __name__=='__main__':run()
