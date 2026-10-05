"""Independent R20 R0 consumption proof from existing CAS; no engine import."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import gzip
import json
import hashlib
import math
from datetime import datetime,timezone
from independent_math import evaluate_position,evaluate_end

HERE=Path(__file__).resolve().parent
ROOT=Path('/home/lyh/MAPF_LMAPF_ERROR_GUIDANCE_EXPLORE/exploration/error_guidance/sadg_fusion_20261005_r20')


def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()


def main():
    model=json.loads((HERE/'MODEL.json').read_text());end=json.loads((HERE/'PINNED_END_MODEL.json').read_text())
    checked=[];position_records=0;consumed=0;max_delta=0.;dependencies={}
    def get(ref):
        assert ref['schema']=='r19-cas-ref-v1'
        expected=f"objects/{ref['sha256'][:2]}/{ref['sha256']}.json.gz";assert ref['path']==expected
        path=ROOT/'r0/evidence'/ref['path'];raw=gzip.decompress(path.read_bytes())
        assert len(raw)==ref['raw_bytes'] and hashlib.sha256(raw).hexdigest()==ref['sha256']
        value=json.loads(raw);assert digest(value)==ref['sha256']
        dependencies[str(path)]=hashlib.sha256(path.read_bytes()).hexdigest();return value
    for arm in ['linear','joint']:
        path=ROOT/'r0'/arm/'episode.json';ep=json.loads(path.read_text())
        assert ep['schema']=='r20-sadg-position-episode-v1' and ep['success'] and ep['status']=='completed'
        assert ep['query_count']==5 and ep['dense_unbudgeted_reference'] and ep['query_budget']==1
        assert abs(ep['makespan']-2.1)<1e-8
        records=get(ep['prediction_evidence_ref']);starts={(e['agent'],e['vertex']):e['time'] for e in ep['events'] if e['kind']=='START'}
        ends={(e['agent'],e['vertex']):e['time'] for e in ep['events'] if e['kind']=='END'}
        assert get(ep['predictor_model_ref'])==end
        if arm=='joint':assert get(ep['position_model_ref'])==model
        for key,r in records.items():
            assert digest(r)==key
            context=r['context'];n=context['nominal_duration'];t=r['time'];uid=r['vertex'];aid=r['agent']
            h=[x for x in ep['delivered_end_history'][aid] if x['delivered']<=t+1e-9]
            public=[{k:x[k] for k in ['nominal_duration','duration','start','end','delivered']} for x in h]
            assert public==context['completed_history']
            if context['status']=='IN_PROGRESS':assert abs(context['elapsed']-(t-starts[(aid,uid)]))<1e-8 and ends[(aid,uid)]>t-1e-8
            else:assert context['elapsed']==0
            original=evaluate_end(end,public,n,context['elapsed'],'learned')
            assert abs(original-r['predictor_output']['remaining_time'])<1e-7
            assert r['future_duration_ratio']==r['predictor_output']['future_duration_ratio']
            if r['provider']!='position_capture_conditional':continue
            position_records+=1;pc=r['position_predictor_input'];q=ep['queries'][r['delivered_position']['query_id']]
            assert q['vertex']==uid and q['agent']==aid and q['delivered_at']<=t+1e-9 and q['delivery_status']=='accepted'
            assert pc['completed_history']==[{k:x[k] for k in ['nominal_duration','duration','start','end','delivered']} for x in h if x['delivered']<=q['captured']+1e-9]
            assert abs(pc['position']['captured_elapsed']-(q['captured']-starts[(aid,uid)]))<1e-8
            assert abs(pc['position']['age']-(t-q['captured']))<1e-8
            assert abs(pc['position']['delivered_age']-(q['delivered_at']-q['captured']))<1e-8 and pc['position']['progress']==q['progress']
            expected=evaluate_position(pc,model)['remaining_time'];delta=abs(expected-r['remaining_time']);max_delta=max(max_delta,delta)
            assert delta<1e-7 and abs(expected-r['position_predictor_output']['remaining_time'])<1e-7
            assert abs(r['encoded_duration']*(1-r['encoded_progress'])-expected)<1e-7
        for solve in ep['solves']:
            split=get(solve['before_ref']);top=get(split['topology']);states=get(split['vertex_state'])
            vertices={v['uid']:(v,s) for v,s in zip(top['vertices'],states)}
            for aid,key in solve['prediction_keys'].items():
                r=records[key]
                if r['provider']!='position_capture_conditional':continue
                _,state=vertices[r['vertex']]
                assert state[0]=='IN_PROGRESS' and abs(state[1]-r['encoded_duration'])<1e-8 and abs(state[2]-r['encoded_progress'])<1e-8
                assert abs(state[1]*(1-state[2])-r['remaining_time'])<1e-8 and abs(r['time']-solve['time'])<1e-8
                consumed+=1
        checked.append(dict(arm=arm,episode_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),queries=ep['query_count'],
            new_author_calls=ep['new_author_calls'],complete=True,engine_sha256=ep['engine_sha256']))
    a=json.loads((ROOT/'r0/linear/episode.json').read_text());b=json.loads((ROOT/'r0/joint/episode.json').read_text())
    assert a['events']==b['events'] and a['segments']==b['segments']
    report=dict(schema='r20-independent-r0-position-consumption-v1',passed=True,verified_utc=datetime.now(timezone.utc).isoformat(),
        checked=checked,position_records=position_records,actual_optimizer_consumptions=consumed,max_math_difference=max_delta,
        cas_objects=len(dependencies),cas_dependency_sha256=dependencies,engine_or_predictor_imported=False,new_solver_or_physical_calls=0,
        retained_first_attempt='Original mechanical attempt failed a mistaken dense-query-count assertion after a complete linear run; root retained it and registered correction.',
        dense_reference='Five paid captures exceed the configured budget intentionally in DensePositionPolicy; this R0 is not evidence of scientific policy budget compliance.',
        scope='One-action mechanical integration only; actual inputs, public timing, future ratio preservation and optimizer residual checked; no scheduling-effect claim.')
    (HERE/'R0_INDEPENDENT_REVIEW.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='cas_dependency_sha256'},indent=2))


if __name__=='__main__':main()
