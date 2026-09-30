"""Independent official-neural-interface and actual task/action audit."""
from pathlib import Path
import copy
import hashlib
import importlib.util
import json
import tempfile

HERE=Path(__file__).resolve().parent
LOCAL=Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence/onlineggo_neural_r0_20260930_r2')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def need(condition, message):
    if not condition:
        raise ValueError(message)


def load_module(name, path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def integer_file(path):
    values=list(map(int,Path(path).read_text().split()))
    need(values[0]==len(values)-1,'author integer-file count mismatch')
    return values[1:]


def run():
    # After archival, verify all immutable raw rather than rerunning native.
    root=HERE/'raw' if (HERE/'raw').exists() else LOCAL
    for label in ('configure_01','build_01','invalid_shape_01',
                  'untrained_initial_mean_01','invalid_shape_02','untrained_initial_mean_02'):
        r=json.loads((root/label/'receipt.json').read_text())
        need(r['elapsed_seconds']<=r['limit_seconds']+5,'stage exceeded bounded time')
        for stream in ('stdout','stderr'):
            need(sha(root/label/(stream+'.log'))==r[stream+'_sha256'],'receipt/log hash mismatch')
    need(json.loads((root/'build_01/receipt.json').read_text())['exit_code']==0,'neural module not built')
    need(json.loads((root/'untrained_initial_mean_02/receipt.json').read_text())['exit_code']==0,'valid diagnostic did not complete')
    invalid=json.loads((root/'invalid_shape_02/receipt.json').read_text())
    need(invalid['exit_code']==1,'official invalid shape was not rejected')
    need('should be 560, but receive 559' in (root/'invalid_shape_02/stdout.log').read_text(),
         'not the official shape rejection')
    for label in ('invalid_shape_01','untrained_initial_mean_01'):
        need(json.loads((root/label/'receipt.json').read_text())['exit_code']==1,'initial missing-input failure lost')
        need('Failed to load' in (root/label/'stderr.log').read_text(),'initial failure mislabeled')
    identity=json.loads((root/'binary_identity.json').read_text())
    need('-DOBJECTIVE=4' in identity['flags'] and '-DMAPFT' not in identity['flags'],'wrong algorithm compile mode')
    job=json.loads((root/'untrained_initial_mean_02_job.json').read_text())
    need(job['trained'] is False,'diagnostic mislabeled trained')
    need(json.loads(job['kwargs']['network_params'])==[5.0]*560,'diagnostic weights changed')
    for path,digest in job['input_sha256'].items():
        need(sha(path)==digest,'author input changed')
    config_path=Path(job['kwargs']['all_json_path'])
    config=json.loads(config_path.read_text())
    need(config['teamSize']==10 and config['numTasksReveal']==1,'fixed input settings changed')
    lines=(config_path.parent/config['mapFile']).read_text().splitlines()
    grid=lines[4:]
    need(len(grid)==int(lines[1].split()[1]),'map height mismatch')
    need(all(len(x)==int(lines[2].split()[1]) for x in grid),'map width mismatch')
    starts=integer_file(config_path.parent/config['agentFile'])
    tasks=integer_file(config_path.parent/config['taskFile'])
    data=json.loads((root/'untrained_initial_mean_02_trace.json').read_text())
    validator=load_module('external_validator',HERE.parent/'external_baseline_pilot_20260929/validator.py')
    replay=validator.validate(grid,starts,tasks,data,10,horizon=100)
    parsed=json.loads((root/'untrained_initial_mean_02_job_result.json').read_text())
    need(abs(parsed['throughput']-replay['completed_tasks']/100)<1e-12,'summary/actual task mismatch')
    need(identity['source_unchanged'],'author algorithm changes not disclosed')
    preflight=load_module('neural_preflight',HERE/'preflight.py')
    rejected=[]
    # This tests source/weights identity handling, not a policy benchmark.
    with tempfile.TemporaryDirectory(prefix='onlineggo_weight_identity_') as directory:
        directory=Path(directory)
        weights=directory/'weights.json'
        provenance=directory/'provenance.json'
        def expect_reject(label,params,meta=None):
            weights.write_text(json.dumps({'params':params}))
            provenance.write_text(json.dumps(meta or {}))
            try:
                preflight.check_weights(weights,provenance)
            except (ValueError,FileNotFoundError,TypeError):
                rejected.append(label)
            else:
                raise ValueError('bad checkpoint accepted: '+label)
        expect_reject('wrong shape',[5.0]*559)
        expect_reject('boolean parameter',[True]+[5.0]*559)
        expect_reject('nonfinite parameter',[float('nan')]+[5.0]*559)
        expect_reject('missing lineage',[5.0]*560)
        meta={'source_url':'https://github.com/zanghz21/OnlineGGO',
              'source_commit':preflight.COMMIT,'training_config_sha256':'x',
              'training_log_sha256':'x','weights_sha256':'wrong',
              'training_run_ids':['train01'],'heldout_run_ids':['test01']}
        expect_reject('wrong weights hash',[5.0]*560,meta)
        weights.write_text(json.dumps({'params':[5.0]*560}))
        meta['weights_sha256']=sha(weights)
        meta['heldout_run_ids']=['train01']
        expect_reject('overlapping train/test',[5.0]*560,meta)
        meta['heldout_run_ids']=['test01'];meta['source_commit']='wrong'
        expect_reject('wrong author version',[5.0]*560,meta)
        try:
            preflight.check_weights(directory/'absent.json',provenance)
        except FileNotFoundError:
            rejected.append('missing weights has no fallback')
        else:
            raise ValueError('missing weights did not fail closed')
    return {'status':'passed','scope':'official OBJ4 evaluator and untrained diagnostic only',
            'trained_policy_qualified':False,'continuous_error_experiment':False,
            'priority_RNG_deterministic':False,'official_parameter_count':560,
            'wrong_dimension_rejected_by_official_module':True,
            'checkpoint_identity_negative_controls_rejected':rejected,
            'independent_actual_action_and_task_replay':replay,
            'build_seconds':json.loads((root/'build_01/receipt.json').read_text())['elapsed_seconds'],
            'source_commit':preflight.COMMIT,'module_sha256':identity['sha256'],
            'prior_missing_input_failures_retained':True,
            'raw_sha256':{str(p.relative_to(root)):sha(p) for p in root.rglob('*')
                          if p.is_file() and 'build_nn' not in p.parts}}


if __name__=='__main__':
    result=run()
    import sys
    target=Path(sys.argv[1]) if len(sys.argv)>1 else HERE/'audit.json'
    with target.open('x') as out:
        json.dump(result,out,indent=2);out.write('\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('raw_sha256','independent_actual_action_and_task_replay')}))
