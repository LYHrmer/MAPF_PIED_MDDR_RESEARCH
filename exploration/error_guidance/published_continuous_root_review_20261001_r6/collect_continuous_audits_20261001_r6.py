"""Parallel read-only audit after each finalized R6c receipt; never runs planners."""
from concurrent.futures import ProcessPoolExecutor, wait, FIRST_COMPLETED
import importlib.util
import json
from pathlib import Path
import sys
import time

HERE = Path('/home/lyh/MAPF_LMAPF_ERROR_GUIDANCE_EXPLORE/exploration/error_guidance/published_continuous_execution_20261001_r6c')
RAW = Path(__file__).resolve().parent / HERE.name / 'runs'
sys.path.insert(0, str(HERE))
import audit

def work(spec):
    try:
        result = audit.check(spec)
    except Exception as error:
        result = {'passed': False, 'error': str(error), 'exception': type(error).__name__}
    geometry = None
    if result['passed']:
        path = Path(__file__).with_name('verify_physical_clearance_20261001_r6.py')
        module_spec = importlib.util.spec_from_file_location('clearance', path)
        module = importlib.util.module_from_spec(module_spec)
        module_spec.loader.exec_module(module)
        geometry = module.audit(RAW / spec['id'], .095036758)
    return spec['id'], result, geometry

def main():
    specs = json.loads((HERE/'runs.json').read_text())['runs']
    out, clearance, submitted, pending = {}, {}, set(), {}
    result_path = Path(__file__).with_name('CONTINUOUS_EXECUTION_ROOT_20261001_R6.json')
    with ProcessPoolExecutor(max_workers=4) as pool:
        while len(out) != len(specs):
            for spec in specs:
                if spec['id'] not in submitted and (RAW/spec['id']/'receipt.json').exists():
                    pending[pool.submit(work, spec)] = spec['id']
                    submitted.add(spec['id'])
            done, _ = wait(pending, timeout=2, return_when=FIRST_COMPLETED) if pending else (set(), set())
            for future in done:
                name, result, geometry = future.result()
                out[name] = result
                if geometry is not None:
                    clearance[name] = geometry
                del pending[future]
                result_path.write_text(json.dumps({'runs': out, 'clearance': clearance,
                    'all_available_passed': all(v['passed'] for v in out.values()),
                    'frozen_auditor_sha256': audit.sha(HERE/'audit.py'),
                    'independent_clearance_verifier_sha256': audit.sha(Path(__file__).with_name('verify_physical_clearance_20261001_r6.py'))}, indent=2)+'\n')
                print(json.dumps({'run': name, 'passed': result['passed'], 'error': result.get('error'),
                                  'tasks': result.get('task_services'), 'audited': len(out)}), flush=True)
            if not pending:
                time.sleep(2)
    print('All 24 frozen audits and independent sampled geometry checks completed.', flush=True)

if __name__ == '__main__':
    main()
