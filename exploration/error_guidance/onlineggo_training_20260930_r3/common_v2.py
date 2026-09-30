"""Local orchestration; optimizer and kwargs method are loaded from pinned upstream."""
import ast
from dataclasses import asdict
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
MAIN = Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence')
UPSTREAM = MAIN / 'baseline_selection_20260929/OnlineGGO'
CMAES = UPSTREAM / 'CMAES'
RAW = MAIN / 'onlineggo_training_20260930_r3_attempt02'
MODULE = next((MAIN / 'onlineggo_neural_r0_20260930_r2/build_nn').glob('py_driver*.so'))
MAP = UPSTREAM / 'Guided-PIBT/guided-pibt/benchmark-lifelong/maps/sortation_small_kiva.map'

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')

def load_source(name, relative):
    spec = importlib.util.spec_from_file_location(name, CMAES / relative)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

def official_config_and_kwargs(weights):
    # Execute the author's dataclass defaults and the exact gen_sim_kwargs AST.
    # This avoids importing unrelated Dask/RHCR/offline environments.
    cfg_mod = sys.modules.get('r3_official_config') or load_source(
        'r3_official_config', 'env_search/traffic_mapf/config.py')
    cfg = cfg_mod.TrafficMAPFConfig(map_path=str(MAP), num_agents=800, simu_time=1000)
    source = CMAES / 'env_search/traffic_mapf/module.py'
    tree = ast.parse(source.read_text())
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'TrafficMAPFModule')
    fn = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == 'gen_sim_kwargs')
    scope = {'json': json}
    exec(compile(ast.Module(body=[fn], type_ignores=[]), str(source), 'exec'), scope)
    return asdict(cfg), scope['gen_sim_kwargs'](SimpleNamespace(config=cfg), weights)

TEMPLATE_CONFIG, TEMPLATE_KWARGS = official_config_and_kwargs([5.0]*560)

def evaluate(label, weights, seed, *, save_trace=False, timeout=120):
    raw = RAW / label
    raw.mkdir(parents=True, exist_ok=False)
    config = dict(TEMPLATE_CONFIG)
    kwargs = dict(TEMPLATE_KWARGS)
    kwargs['network_params'] = json.dumps(weights)
    kwargs['seed'] = int(seed)
    if save_trace:
        kwargs['save_path'] = str(raw / 'trace.json')
    job = {'label': label, 'module_path': str(MODULE), 'module_sha256': sha(MODULE),
           'map_sha256': sha(MAP), 'config': config, 'kwargs': kwargs}
    path = raw / 'job.json'
    write_json(path, job)
    env = os.environ.copy()
    env.update(OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1')
    start = time.monotonic()
    with (raw / 'stdout.log').open('w') as out, (raw / 'stderr.log').open('w') as err:
        try:
            result = subprocess.run(['rtk', 'proxy', sys.executable, str(HERE / 'native_worker.py'), str(path)],
                                    cwd=raw, env=env, stdout=out, stderr=err, timeout=timeout)
            status = {'returncode': result.returncode, 'timed_out': False}
        except subprocess.TimeoutExpired:
            status = {'returncode': None, 'timed_out': True}
    status.update(label=label, seed=int(seed), wall_seconds=time.monotonic()-start,
                  job_sha256=sha(path))
    result_path = path.with_suffix('.result.json')
    if result_path.exists():
        status.update(json.loads(result_path.read_text()))
        status['result_sha256'] = sha(result_path)
    write_json(raw / 'receipt.json', status)
    if status['returncode'] != 0 or 'result' not in status:
        raise RuntimeError(f'Native evaluation failed; retained at {raw}')
    return status

if __name__ == '__main__':
    RAW.mkdir(parents=True, exist_ok=True)
    result = evaluate('runtime_probe_800_1000', [5.0]*560, 719, save_trace=True)
    print(json.dumps({k: v for k, v in result.items() if k != 'result'} |
                     {'throughput': result['result']['throughput']}, indent=2))
