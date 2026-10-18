"""Repackage THREE preselected existing R18 plans; no path search or simulation."""
import hashlib
import json
from pathlib import Path

from address_backend import GridProblem

HERE = Path(__file__).resolve().parent
ROOT = Path('/home/lyh/MAPF_LMAPF_ERROR_GUIDANCE_EXPLORE/exploration/error_guidance/sadg_benchmark_20261005_r18/data')
CASES = ('maze-32-32-2__s01__n08', 'random-32-32-10__s01__n08',
         'warehouse-10-20-10-2-1__s01__n08')
ORDERS = [[0, 1, 2, 3], [3, 2, 1, 0], [4, 5, 6, 7], [7, 6, 5, 4]]
RUNTIME = ('pp_repair.py', 'address_backend.py', 'address_sipp_bridge.cpp',
           'run_repair_dev.py', 'build_receipt.json')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def prepare_case(name):
    folder = ROOT / 'cases' / name
    source = {}
    def read(path, expected=None):
        raw = path.read_bytes()
        digest = sha(raw)
        if expected is not None and expected != digest:
            raise ValueError('changed original evidence: ' + str(path))
        source[str(path.relative_to(ROOT))] = {'sha256': digest, 'bytes': len(raw)}
        return raw
    provenance = json.loads(read(folder / 'INPUT_PROVENANCE.json'))
    plan = json.loads(read(folder / 'plan.json'))
    validation = json.loads(read(folder / 'validation.json'))
    receipt = json.loads(read(folder / 'receipt.json'))
    read(folder / 'input.yaml', provenance['ecbs_input_sha256'])
    read(folder / 'solution.yaml', receipt['raw_solution_sha256'])
    grid = read(ROOT / provenance['map_path'], provenance['map_sha256']).decode().splitlines()
    scenarios = read(ROOT / provenance['scenario_path'], provenance['scenario_sha256']).decode().splitlines()[1:]
    rows, cols = provenance['height'], provenance['width']
    if grid[:4] != ['type octile', 'height '+str(rows), 'width '+str(cols), 'map']:
        raise ValueError('unexpected MovingAI header')
    grid = grid[4:]
    if len(grid) != rows or any(len(row) != cols or set(row)-set('.GS@OTW') for row in grid):
        raise ValueError('map shape/symbol mismatch')
    blocked = [r*cols+c for r, row in enumerate(grid) for c, value in enumerate(row) if value not in '.GS']
    if plan['case_id'] != name or plan['status'] != 'valid' or not validation['valid']:
        raise ValueError('original task lacks a validated initial plan')
    paths, endpoints = {}, {}
    for i, agent in enumerate(provenance['agents']):
        if agent['name'] != 'agent'+str(i):
            raise ValueError('nonstandard source robot IDs')
        row = scenarios[provenance['scenario_rows_1_based'][i]-1].split()
        if list(map(int, row[4:8])) != agent['start'] + agent['goal']:
            raise ValueError('scenario endpoints differ from source plan')
        sx, sy = agent['start']; gx, gy = agent['goal']
        endpoints[i] = (sy*cols+sx, gy*cols+gx)
        states = plan['solution']['schedule'][agent['name']]
        if [state['t'] for state in states] != list(range(len(states))):
            raise ValueError('source clock is not consecutive integer grid time')
        paths[i] = [state['y']*cols+state['x'] for state in states]
    problem = GridProblem(rows, cols, blocked, endpoints)
    problem.validate(paths)  # Validate existing paths; never solve for a new one.
    if sum(len(p)-1 for p in paths.values()) != validation['sum_of_costs']:
        raise ValueError('projection changed the original cost')
    return {'id': name, 'rows': rows, 'cols': cols, 'blocked': blocked,
            'paths': paths, 'endpoints': endpoints, 'orders': ORDERS, 'seed': 0,
            'source_root': str(ROOT), 'source_files': source,
            'old_split': plan['split'], 'current_split': 'DEV_REUSED_NOT_HELD_OUT',
            'physical_resolution': 'NOT_USED_DISCRETE_GRID_ONLY'}


def main():
    if (HERE / 'results' / 'repair_dev_v1').exists():
        raise ValueError('an attempt exists; preserve its inputs and manifest, do not regenerate')
    folder = HERE / 'config'
    folder.mkdir(exist_ok=True)
    bundle = {'scope': 'EXISTING_PLAN_REPACK_NO_NEW_SOLVER', 'selection': 's01 n08 for each of three registered families; fixed before new solver outcomes',
              'generator_sha256': sha(Path(__file__).read_bytes()), 'cases': [prepare_case(name) for name in CASES]}
    raw = (json.dumps(bundle, sort_keys=True, separators=(',', ':'))+'\n').encode()
    input_path = folder / 'repair_dev_inputs.json'
    input_path.write_bytes(raw)
    jobs = []
    for i, name in enumerate(CASES):
        policies = ['ORIGINAL_PREFIX', 'REMAINING_BOUND']
        if i % 2:
            policies.reverse()
        for policy in policies:
            jobs.append({'id': name+'__'+policy.lower(), 'case': name, 'policy': policy})
    manifest = {'schema': 'repair_dev_v1', 'batch_id': 'repair_dev_v1', 'authorization': 'PENDING_USER',
                'input_file': input_path.name, 'input_sha256': sha(raw),
                'binary': '.native_build_checked/address_sipp_bridge',
                'code_sha256': {name: sha((HERE/name).read_bytes()) for name in RUNTIME},
                'limits': {'case_wall_s': 15, 'algorithm_wall_s': 10, 'worker_cpu_s': 10,
                           'native_cpu_s': 10, 'per_process_as_mib': 512, 'search_calls': 16},
                'retry': 0, 'jobs': jobs}
    mraw = (json.dumps(manifest, sort_keys=True, indent=2)+'\n').encode()
    (folder/'repair_dev_manifest.json').write_bytes(mraw)
    print(json.dumps({'input_sha256': sha(raw), 'input_bytes': len(raw),
                      'manifest_sha256': sha(mraw), 'cases': len(CASES), 'jobs': len(jobs),
                      'scope': bundle['scope']}))


if __name__ == '__main__':
    main()
