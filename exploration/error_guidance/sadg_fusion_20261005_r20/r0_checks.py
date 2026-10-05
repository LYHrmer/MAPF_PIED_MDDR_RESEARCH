"""New position-fusion interface qualification; no standard-scene test access."""
from pathlib import Path
from dataclasses import replace
import copy
import importlib.util
import json
import math
import sys

from engine import Simulator, EngineConfig, DensePositionPolicy, file_sha, write_json

HERE=Path(__file__).resolve().parent
OUT=HERE/'r0'
CASE=dict(case_id='r20_new_position_pause_1p1',solution={'schedule':{'agent0':[dict(x=0,y=0,t=0),dict(x=1,y=0,t=1)]}})

def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec);sys.modules[name]=mod;spec.loader.exec_module(mod);return mod

def main():
    assert not (OUT/'REGISTRATION.json').exists(), 'retain each qualification attempt'
    from run_study import prepare_model,prepare_position_model
    prepare_model();prepare_position_model()
    write_json(OUT/'REGISTRATION.json',dict(scope='new mechanical position-fusion qualification',
        scientific_episodes=0,author_call_cap=12,case=CASE,
        disturbance=dict(kind='bounded_pause',affected_fraction=1.,pause_probability=1.,pause_duration=1.1,pause_fraction=.35),
        sources={n:file_sha(HERE/n) for n in ('engine.py','r0_checks.py','solver_adapter.py','evidence.py','structural.py','PUBLIC_SCHEMA.json','model/MODEL.json','model/predictor.py','position_model/MODEL.json','position_model/predictor.py')}))
    cfg=EngineConfig(solve_period=.4,query_latency=.1,query_budget=1,max_queries_per_gate=1,
        max_time=5.,evidence_dir=str(OUT/'evidence'),cache_dir=str(OUT/'cache'))
    end=module('r20_r0_end',HERE/'model/predictor.py').DurationPredictor(HERE/'model/MODEL.json','learned')
    module('end_predictor',HERE/'position_model/end_predictor.py')
    joint=module('r20_r0_position',HERE/'position_model/predictor.py').PositionPredictor(HERE/'position_model/MODEL.json')
    calls=[]
    class Spy:
        model={'scope':'mechanical spy'}
        def __call__(self,context):
            calls.append(copy.deepcopy(context));return dict(remaining_time=2.3,metadata={'mechanical_only':True})
    sim=Simulator(CASE,predictor=end,position_predictor=Spy(),config=cfg)
    sim.now=5.;sim._estimate('agent0');assert not calls # dependency WAIT is not elapsed motion
    sim.now=0.;sim._dispatch();sim.now=.5
    baseline=sim._estimate('agent0');assert not calls
    vertex=sim.agents['agent0']['vertex'];uid=vertex.get_shorthand()
    sim.latest['agent0']=dict(vertex='other_occurrence',captured=.3,delivered_at=.4,progress=.35,query_id=0)
    assert sim._estimate('agent0')['remaining']==baseline['remaining'] and not calls
    sim.latest['agent0']['vertex']=uid
    new=sim._estimate('agent0');assert new['remaining']==2.3 and len(calls)==1
    assert new['future_ratio']==baseline['future_ratio']
    context=calls[-1];assert set(context)=={'status','occurrence_id','nominal_duration','elapsed','completed_history','position'}
    assert context['position']['captured_elapsed']==.3 and abs(context['position']['age']-.2)<1e-12
    assert abs(context['position']['delivered_age']-.1)<1e-12
    sim._update_predictor();assert abs(vertex.get_expected_completion_time()*(1-vertex.get_progress())-2.3)<1e-12
    actual=joint(context);assert actual['remaining_time']>=0 and math.isfinite(actual['remaining_time'])
    # Undelivered POSITION must be rejected before model invocation.
    sim.latest['agent0']['delivered_at']=.6
    try:sim._estimate('agent0')
    except RuntimeError:pass
    else:raise AssertionError('undelivered position was consumed')
    negative=0
    for field,value in [('occurrence_id','wrong'),('age',-.1),('delivered_age',.3),('progress',1.2),('captured_elapsed',.4)]:
        bad=copy.deepcopy(context);bad['position'][field]=value
        try:joint(bad)
        except ValueError:negative+=1
        else:raise AssertionError('invalid position context accepted: '+field)
    outcomes=[]
    disturbance=dict(kind='bounded_pause',affected_fraction=1.,pause_probability=1.,pause_duration=1.1,pause_fraction=.35)
    for name,predictor in [('linear',None),('joint',joint)]:
        run=Simulator(CASE,disturbance,19,predictor=end,position_predictor=predictor,
            config=replace(cfg,output_dir=str(OUT/name))).run(DensePositionPolicy())
        assert run['success'] and run['query_count']==1 and abs(run['makespan']-2.1)<1e-7
        outcomes.append(run)
    assert outcomes[0]['events']==outcomes[1]['events']
    assert sum(x['new_author_calls'] for x in outcomes)<=12
    store=Simulator(CASE,predictor=end,config=cfg).store
    predictions=store.get(outcomes[1]['prediction_evidence_ref'])
    records=[r for r in predictions.values() if r['provider']=='position_capture_conditional']
    assert records and all(r['position_predictor_input']['position']['age']>=.1-1e-8 for r in records)
    report=dict(passed=True,scientific_episodes=0,new_author_calls=sum(x['new_author_calls'] for x in outcomes),
        negative_controls=negative+1,position_predictions=len(records),checks=[
            'STAGED_wait_excluded','missing_position_END_fallback','stale_occurrence_END_fallback',
            'current_position_passed_with_full_age','future_ratio_unchanged','encoded_residual_exact',
            'undelivered_position_rejected','invalid_contexts_rejected','two_complete_native_arms',
            'one_actual_query_per_arm','identical_single_action_physics','capture_survival_deployed'],
        registration_sha256=file_sha(OUT/'REGISTRATION.json'))
    write_json(OUT/'VALIDATION.json',report);print(json.dumps(report,indent=2))

if __name__=='__main__':main()
