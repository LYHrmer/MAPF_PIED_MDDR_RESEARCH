"""Software contracts only: no author Instance or SIPP/search construction."""
import os
from pathlib import Path
import subprocess
import tempfile
import time
import unittest
from unittest.mock import patch

from address_adapter import adapt, replace_exact
from build_address_full import AUTHOR, build, source_identity
from run_address_adapter import load, parse_paths, worker
from run_repair_dev import unpack


class AdapterContracts(unittest.TestCase):
    def test_materialization_failure_retains_build_receipt(self):
        import json
        for error in (ValueError('anchor mismatch'), FileNotFoundError('missing header'),
                      OSError('overlay write failed')):
            with self.subTest(error=type(error).__name__), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                with patch('build_address_full.source_identity', return_value={}), \
                     patch('address_adapter.materialize', side_effect=error):
                    with self.assertRaises(type(error)):
                        build(root/'fake-author', root/'new-build', adapter=True)
                receipt = json.loads((root/'new-build/build_receipt.json').read_bytes())
                self.assertEqual(receipt['status'], 'FAILED')
                self.assertIn(str(error), receipt['error'])
                self.assertEqual(receipt['stages'], [])

    def test_load_binds_receipt_status_author_and_binary(self):
        import hashlib, json
        def sha(raw):
            return hashlib.sha256(raw).hexdigest()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            names = ['run_address_adapter.py', 'run_repair_dev.py', 'address_backend.py', 'pp_repair.py']
            for name in names:
                (root/name).write_text('# fixture only\n')
            binary_raw = b'fixture binary bytes; never executed'
            (root/'binary').write_bytes(binary_raw)
            inputs = b'{"cases": []}'
            (root/'inputs.json').write_bytes(inputs)
            good = {'status': 'COMPILED_HELP_ONLY',
                    'scope': 'ADDRESS_COMMON_INITIAL_ADAPTER_COMPILE_AND_HELP_ONLY',
                    'author_commit': AUTHOR, 'author_unchanged': True,
                    'solver_instance_constructed': False, 'scientific_search_executed': False,
                    'binary_sha256': sha(binary_raw)}
            config = {'schema': 'address_common_initial_dev_v1', 'authorization': 'PENDING_USER',
                      'binary': 'binary', 'binary_sha256': sha(binary_raw), 'input_file': 'inputs.json',
                      'input_sha256': sha(inputs), 'retry': 0, 'batch_id': 'fixture', 'jobs': [],
                      'limits': {'total_wall_s': 15, 'worker_cpu_s': 10, 'native_cpu_s': 10,
                                 'per_process_as_mib': 512, 'external_final_reserve_s': .5,
                                 'inner_final_reserve_s': .25}}
            def inspect(receipt):
                (root/'adapter_build_receipt.json').write_text(json.dumps(receipt))
                config['code_sha256'] = {name: sha((root/name).read_bytes())
                                        for name in names+['adapter_build_receipt.json']}
                raw = json.dumps(config).encode()
                (root/'manifest.json').write_bytes(raw)
                with patch('run_address_adapter.HERE', root):
                    return load(root/'manifest.json', sha(raw))
            self.assertEqual(inspect(good)[2], root/'binary')
            for key, bad in [('status', 'FAILED'), ('scope', 'PRISTINE_FULL_ADDRESS_COMPILE_AND_HELP_ONLY'),
                             ('author_commit', '0'*40), ('binary_sha256', '0'*64),
                             ('author_unchanged', False)]:
                with self.subTest(key=key), self.assertRaisesRegex(ValueError, 'build receipt'):
                    inspect(dict(good, **{key: bad}))

    def test_fail_closed_patch_anchor(self):
        with self.assertRaises(ValueError):
            replace_exact('a a', 'a', 'b')

    def test_author_reward_and_acceptance_bodies_unchanged(self):
        root = Path(os.environ.get('ADDRESS_AUTHOR_ROOT', '/home/lyh/.cache/mapf_research/address-b3d35c4'))
        pins = source_identity(root)
        files = {name: (root/name).read_bytes() for name in pins}
        changed = adapt(files)
        old, new = files['src/LNS.cpp'], changed['src/LNS.cpp']
        def body(raw):
            return raw.split(b'bool LNS::runPP()')[1].split(b'bool LNS::runPPS()')[0]
        self.assertEqual(body(old), body(new))
        self.assertNotIn('src/BasicLNS.cpp', changed)
        self.assertNotIn(b'std::random_device', new)
        self.assertIn(b'this->neighbor_size = 8;', new)
        self.assertIn(b'neighbor.sum_of_costs = initial_sum_of_costs = sum_of_costs = cost;', new)

    def test_cpp_geometry_and_seed_contracts_without_solver(self):
        source = r'''
#include "address_adapter_support.h"
#include <cassert>
using namespace address_adapter;
void invalid(Paths p, std::vector<int> s, std::vector<int> g) {
    bool threw=false;
    try { validate(p, 2, 3, std::vector<bool>(6, false), s, g); }
    catch (const std::runtime_error&) { threw=true; }
    assert(threw);
}
int main() {
    assert(validate({{0,1,2},{3,4,5}},2,3,std::vector<bool>(6,false),{0,3},{2,5})==4);
    invalid({{0,1},{2,1}}, {0,2}, {1,1}); // vertex
    invalid({{0,1},{1,0}}, {0,1}, {1,0}); // opposing edge
    invalid({{0,1},{5,4,1,2}}, {0,5}, {1,2}); // stationary terminal hit
    invalid({{2,3},{4,5}}, {2,4}, {3,5}); // row wrap
    invalid({{0,1},{3,4}}, {1,3}, {1,4}); // endpoint
    state().seeds.seed(41); const auto a=next_seed(), b=next_seed();
    state().seeds.seed(41); assert(a==next_seed() && b==next_seed());
}
'''
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root/'contract.cpp').write_text(source)
            subprocess.run(['g++', '-std=c++14', '-O0', '-I', str(Path(__file__).parent),
                            str(root/'contract.cpp'), '-o', str(root/'contract')], check=True,
                           capture_output=True, timeout=30)
            subprocess.run([str(root/'contract')], check=True, capture_output=True, timeout=5)

    def test_external_worker_fake_child_and_final_validation(self):
        # Eight stationary paths are software fixtures; the child only writes
        # known bytes and never imports/constructs an author Instance or solver.
        case = {'id': 'fixture', 'rows': 2, 'cols': 4, 'blocked': [],
                'paths': {str(i): [i] for i in range(8)},
                'endpoints': {str(i): [i, i] for i in range(8)}, 'orders': []}
        config = {'manifest_sha256': 'fixture', 'limits': {'external_final_reserve_s': .1,
            'inner_final_reserve_s': .1, 'native_cpu_s': 2, 'per_process_as_mib': 128}}
        job = {'seed': 1, 'iterations': 1, 'top_k': 4}
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            script = folder/'fake.py'
            script.write_text('''from pathlib import Path
import json, sys
root=Path(sys.argv[1])
(root/'final.paths').write_text(''.join(f'Agent {i}:({i//4},{i%4})->\\n' for i in range(8)))
(root/'native_receipt.json').write_text(json.dumps({'initial_and_final_validated':True,
    'seed':1, 'initial_soc':0, 'final_soc':0}))
''')
            import sys
            factory = lambda *args: [sys.executable, '-B', str(script), str(folder)]
            self.assertTrue(worker(config, case, job, None, folder, time.monotonic_ns()+3_000_000_000, factory))
            import json
            result = json.loads((folder/'result.json').read_bytes())
            self.assertEqual(result['final_soc'], 0)
            self.assertTrue(result['final_validated'])
        problem, _ = unpack(case)
        malformed = ''.join(f'Agent {i}:(0,0)->\n' for i in range(8)).encode()
        with self.assertRaises(ValueError):
            parse_paths(malformed, problem)

    def test_failed_fake_child_retains_result(self):
        case = {'id': 'fixture', 'rows': 2, 'cols': 4, 'blocked': [],
                'paths': {str(i): [i] for i in range(8)},
                'endpoints': {str(i): [i, i] for i in range(8)}, 'orders': []}
        config = {'manifest_sha256': 'fixture', 'limits': {'external_final_reserve_s': .1,
            'inner_final_reserve_s': .1, 'native_cpu_s': 2, 'per_process_as_mib': 128}}
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            import sys, json
            factory = lambda *args: [sys.executable, '-B', '-c', 'raise SystemExit(7)']
            self.assertFalse(worker(config, case, {'seed': 1, 'iterations': 1, 'top_k': 4},
                None, folder, time.monotonic_ns()+3_000_000_000, factory))
            result = json.loads((folder/'result.json').read_bytes())
            self.assertEqual(result['status'], 'FAILED')
            self.assertIn('exited 7', result['reason'])
            self.assertTrue((folder/'initial.txt').exists())


if __name__ == '__main__':
    unittest.main()
