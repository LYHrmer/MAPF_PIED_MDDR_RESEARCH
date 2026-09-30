"""Build and qualify the official neural evaluator without fabricating weights."""
from pathlib import Path
import argparse
import datetime
import hashlib
import importlib.util
import json
import math
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
DEFAULT = Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence')
COMMIT = 'ff6d830e2fd5bf85ccbb72eaec0fb8df1cf1c256'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_new(path, value):
    with Path(path).open('x') as out:
        json.dump(value, out, indent=2, allow_nan=False)
        out.write('\n')


def stage(root, name, argv, cwd, limit):
    dest = root / name
    dest.mkdir()
    command = ['rtk', 'proxy', 'timeout', '--kill-after=5s', str(limit)+'s', *argv]
    started = time.monotonic()
    with (dest/'stdout.log').open('wb') as stdout, (dest/'stderr.log').open('wb') as stderr:
        run = subprocess.run(command, cwd=cwd, stdout=stdout, stderr=stderr, check=False)
    receipt = {'argv': command, 'cwd': str(cwd), 'exit_code': run.returncode,
               'elapsed_seconds': time.monotonic()-started, 'limit_seconds': limit,
               'finished_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
               'stdout_sha256': sha(dest/'stdout.log'), 'stderr_sha256': sha(dest/'stderr.log')}
    write_new(dest/'receipt.json', receipt)
    print(json.dumps({'stage':name, **receipt}), flush=True)
    return receipt


def check_weights(path, provenance_path):
    data = json.loads(Path(path).read_text())
    params = data.get('params')
    if not isinstance(params, list) or len(params) != 560:
        raise ValueError('quad/flow/win_r2/output4 requires exactly 560 params')
    if not all(type(x) in (int,float) and math.isfinite(x) for x in params):
        raise ValueError('all params must be finite numbers, excluding booleans')
    provenance = json.loads(Path(provenance_path).read_text())
    for field in ('source_url', 'source_commit', 'training_config_sha256',
                  'training_log_sha256', 'weights_sha256', 'training_run_ids',
                  'heldout_run_ids'):
        if not provenance.get(field):
            raise ValueError('missing provenance: '+field)
    if provenance['source_commit'] != COMMIT or provenance['weights_sha256'] != sha(path):
        raise ValueError('weights or source lineage mismatch')
    if set(provenance['training_run_ids']) & set(provenance['heldout_run_ids']):
        raise ValueError('training/evaluation run leakage')
    return params, provenance


def build(args):
    source = args.evidence/'baseline_selection_20260929/OnlineGGO'
    root = args.evidence/'onlineggo_neural_r0_20260930_r2'
    root.mkdir()
    head = subprocess.check_output(['rtk','proxy','git','-C',str(source),'rev-parse','HEAD'], text=True).strip()
    if head != COMMIT:
        raise ValueError('unexpected author commit')
    status = subprocess.check_output(['rtk','proxy','git','-C',str(source),'status','--porcelain','--untracked-files=no'],text=True)
    if status.strip():
        raise ValueError('author source is modified')
    files = subprocess.check_output(['rtk','proxy','git','-C',str(source),'ls-files'],text=True).splitlines()
    identity = {'source_root':str(source), 'commit':head,
                'tracked_sha256':{x:sha(source/x) for x in files if (source/x).is_file()},
                'submodules':subprocess.check_output(['rtk','proxy','git','-C',str(source),'submodule','status','--recursive'],text=True),
                'official_checkpoint_files':[x for x in files if 'optimal_update_model' in x or x.endswith(('.pt','.pth','.pkl'))],
                'scientific_trained_policy_qualified':False}
    write_new(root/'source_identity.json',identity)
    src = source/'Guided-PIBT/guided-pibt'
    builddir = root/'build_nn'
    command=['cmake','-S',str(src),'-B',str(builddir),'-DDEV=OFF','-DSWAP=ON',
             '-DGUIDANCE=ON','-DGUIDANCE_LNS=OFF','-DFLOW_GUIDANCE=OFF',
             '-DINIT_PP=ON','-DRELAX=100','-DOBJECTIVE=4','-DFOCAL_SEARCH=OFF',
             '-DCMAKE_BUILD_TYPE=Release','-DEIGEN3_INCLUDE_DIR=/usr/include/eigen3',
             '-DMINIDNN_DIR='+str(source/'third_party/MiniDNN/include')]
    if stage(root,'configure_01',command,source,120)['exit_code']:
        raise RuntimeError('configure failed; receipt retained')
    if stage(root,'build_01',['cmake','--build',str(builddir),'--target','py_driver','-j','4'],source,120)['exit_code']:
        raise RuntimeError('build failed; receipt retained')
    module, = builddir.glob('py_driver*.so')
    flags=(builddir/'CMakeFiles/py_driver.dir/flags.make').read_text()
    if '-DOBJECTIVE=4' not in flags or '-DMAPFT' in flags:
        raise ValueError('neural/nonrotation compile flags mismatch')
    current={x:sha(source/x) for x in identity['tracked_sha256']}
    if current != identity['tracked_sha256']:
        raise ValueError('author source changed during build')
    write_new(root/'binary_identity.json',{'path':str(module),'sha256':sha(module),'flags':flags,
                                         'source_unchanged':True,'trained_policy_qualified':False})


def smoke(args):
    source=args.evidence/'baseline_selection_20260929/OnlineGGO'
    root=args.evidence/'onlineggo_neural_r0_20260930_r2'
    module, = (root/'build_nn').glob('py_driver*.so')
    identity=json.loads((root/'binary_identity.json').read_text())
    if sha(module) != identity['sha256']:
        raise ValueError('module identity changed')
    config=HERE.parent/'external_baseline_pilot_20260929/author_inputs/visualizer_example_sts.json'
    config_data=json.loads(config.read_text())
    if config_data['teamSize'] != 10 or config_data['numTasksReveal'] != 1:
        raise ValueError('fixed diagnostic input mismatch')
    for field in ('mapFile','agentFile','taskFile'):
        if not (config.parent/config_data[field]).is_file():
            raise ValueError('missing author input: '+field)
    for name,count in [('invalid_shape_02',559),('untrained_initial_mean_02',560)]:
        job={'module_path':str(module),'label':name,'trained':False,
             'input_sha256':{str(p):sha(p) for p in [config,*[config.parent/config_data[k] for k in ('mapFile','agentFile','taskFile')]]},
             'kwargs':{'gen_tasks':False,'all_json_path':str(config),'simu_time':100,
                       'net_type':'quad','net_input_type':'flow','win_r':2,
                       'output_size':4,'has_map':False,'has_path':False,'has_previous':False,
                       'use_all_flow':True,'use_cached_nn':True,'learn_obst_flow':False,
                       'network_params':json.dumps([5.0]*count),
                       'save_path':str(root/(name+'_trace.json'))}}
        path=root/(name+'_job.json')
        write_new(path,job)
        stage(root,name,[sys.executable,str(Path(__file__).resolve()),'native','--job',str(path)],source,60)


def native(args):
    job=json.loads(args.job.read_text())
    spec=importlib.util.spec_from_file_location('py_driver',job['module_path'])
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    data=json.loads(module.run(**job['kwargs']))
    write_new(args.job.with_name(args.job.stem+'_result.json'),data)
    print(json.dumps({'label':job['label'],'trained':job['trained'],'result_keys':list(data)}))


def evaluate(args):
    # Providing lineage metadata never automatically certifies a trained policy.
    if args.weights is None or args.provenance is None or args.job is None:
        raise ValueError('explicit weights, provenance and fresh job output required; no fallback')
    params, provenance=check_weights(args.weights,args.provenance)
    root=args.evidence/'onlineggo_neural_r0_20260930_r2'
    identity=json.loads((root/'binary_identity.json').read_text())
    module=Path(identity['path'])
    if sha(module) != identity['sha256']:
        raise ValueError('neural module identity changed')
    prior=json.loads((root/'untrained_initial_mean_02_job.json').read_text())
    kwargs=dict(prior['kwargs'])
    kwargs['network_params']=json.dumps(params)
    kwargs['save_path']=str(args.job.with_name(args.job.stem+'_trace.json'))
    job={'module_path':str(module),'label':'provided_weights_support_input',
         'trained':None,'trained_policy_qualification':'requires independent config/log audit',
         'provenance':provenance,'weights_sha256':sha(args.weights),
         'input_sha256':prior['input_sha256'],'kwargs':kwargs}
    for path,digest in job['input_sha256'].items():
        if sha(path)!=digest:
            raise ValueError('fixed author support input changed')
    write_new(args.job,job)
    receipt_root=args.job.parent/(args.job.stem+'_run')
    receipt_root.mkdir()
    receipt=stage(receipt_root,'native_01',[sys.executable,str(Path(__file__).resolve()),
                  'native','--job',str(args.job)],args.job.parent,60)
    if receipt['exit_code']:
        raise RuntimeError('provided-weights evaluation failed; retained, no fallback')


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('mode',choices=['build','smoke','native','check-weights','evaluate'])
    parser.add_argument('--evidence',type=Path,default=DEFAULT)
    parser.add_argument('--job',type=Path)
    parser.add_argument('--weights',type=Path)
    parser.add_argument('--provenance',type=Path)
    args=parser.parse_args()
    if args.mode=='check-weights':
        params, provenance=check_weights(args.weights,args.provenance)
        print(json.dumps({'schema_passed':True,'params':len(params),
                          'scope':'provided lineage metadata checked; logs/config still require independent verification'}))
    else:
        globals()[args.mode](args)
