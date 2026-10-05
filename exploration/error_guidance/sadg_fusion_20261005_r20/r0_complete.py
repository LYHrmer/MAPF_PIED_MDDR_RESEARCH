"""Complete R0 using its original dense-query reference; do not rerun linear."""
from dataclasses import replace
import json
import math
from pathlib import Path

from r0_checks import HERE,OUT,CASE,module
from engine import Simulator,EngineConfig,DensePositionPolicy,file_sha,write_json

def main():
    assert not (OUT/'CORRECTION_REGISTRATION.json').exists()
    linear=json.loads((OUT/'linear/episode.json').read_text())
    assert linear['success'] and linear['query_count']==5 and abs(linear['makespan']-2.1)<1e-8
    assert not (OUT/'joint/episode.json').exists()
    write_json(OUT/'CORRECTION_REGISTRATION.json',dict(
        reason='Initial R0 assertion incorrectly expected DensePositionPolicy to obey budget; this inherited diagnostic policy intentionally queries every active gate. No science policy uses it.',
        retained_first_attempt=True,reused_linear_sha256=file_sha(OUT/'linear/episode.json'),
        action='retain five-query reference and run joint once with identical dense policy; do not rerun linear',
        original_native_calls=linear['new_author_calls'],total_author_call_cap=12,
        source_sha256=file_sha(__file__),engine_sha256=file_sha(HERE/'engine.py'),
        unchanged_position_model_sha256=file_sha(HERE/'position_model/MODEL.json')))
    cfg=EngineConfig(**linear['config']);cfg=replace(cfg,output_dir=str(OUT/'joint'))
    end=module('r20_r0_end',HERE/'model/predictor.py').DurationPredictor(HERE/'model/MODEL.json','learned')
    module('end_predictor',HERE/'position_model/end_predictor.py')
    joint=module('r20_r0_position',HERE/'position_model/predictor.py').PositionPredictor(HERE/'position_model/MODEL.json')
    run=Simulator(CASE,linear['private_truth']['disturbance'],linear['private_truth']['seed'],
        predictor=end,position_predictor=joint,config=cfg).run(DensePositionPolicy())
    assert run['success'] and run['query_count']==5 and abs(run['makespan']-2.1)<1e-8
    assert linear['events']==run['events'] and linear['segments']==run['segments']
    calls=linear['new_author_calls']+run['new_author_calls'];assert calls<=12
    store=Simulator(CASE,predictor=end,config=cfg).store
    records=[r for r in store.get(run['prediction_evidence_ref']).values() if r['provider']=='position_capture_conditional']
    assert records and all(r['position_predictor_input']['position']['age']>=.1-1e-8 for r in records)
    report=dict(passed=True,scientific_episodes=0,new_author_calls=calls,
        reused_physical_episodes=1,new_corrective_physical_episodes=1,
        correction_registration_sha256=file_sha(OUT/'CORRECTION_REGISTRATION.json'),
        first_attempt_scope='mechanical interface checks completed through the successful linear run; failed only the mistaken dense-query-count assertion',
        negative_controls_preceding_first_failure=6,position_predictions=len(records),
        checks=['STAGED/missing/stale END fallback','public capture-age context','unchanged future ratio',
            'encoded residual','undelivered and invalid contexts rejected','two complete native arms',
            'five dense-reference queries each','same physical event and segment trace','joint predictor actually deployed'],
        dense_reference_exceeds_budget_intentionally=True,
        science_policies='structural and noquery obey caps independently audited against snapshots')
    write_json(OUT/'VALIDATION.json',report);print(json.dumps(report,indent=2))

if __name__=='__main__':main()
