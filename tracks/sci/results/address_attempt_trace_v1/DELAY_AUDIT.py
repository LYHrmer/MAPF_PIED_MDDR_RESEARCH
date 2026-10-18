"""Offline graph labels and source deductions from frozen ADDRESS evidence.

No imports of project solver code; no author Instance/SIPP/group calls. Reads
frozen files only, checks their hashes, and writes one result under /tmp.
"""
from collections import Counter, deque
from pathlib import Path
import hashlib
import json
import math
import re

SCI = Path('/home/lyh/MAPF_SCI_RESEARCH/tracks/sci')
BATCH = SCI / 'results/address_attempt_trace_v1'
OVERLAY = SCI.parent.parent / '.address_attempt_trace_build/source_overlay'
AUTHOR = Path('/home/lyh/.cache/mapf_research/address-b3d35c4')
OUTPUT = Path('/tmp/mapf_nonrepair_delay_audit.json')
RECEIPT_SHA = '308e5a65e98270b6049336dff0c50da88bbbf137755fc2875a9203d91d5a8632'
MANIFEST_SHA = 'edf8516ab73919c0fedc0542c407c5775f8601383259f69ead6949146f43c2f3'
BUILD_SHA = 'f88c0112ad5b531ad498f7721453ca663b0609f18867d7295db7cf86d8315a28'
JOBS = ('random-32-32-10__s01__n32__attempt_trace',
        'maze-32-32-2__s01__n32__attempt_trace')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def checked_json(path, expected):
    assert sha(path) == expected, str(path)
    return json.loads(path.read_text())


def artifact(path, pin):
    assert path.stat().st_size == pin['bytes'], str(path)
    assert sha(path) == pin['sha256'], str(path)


def method(source, start, end):
    return source[source.index(start):source.index(end, source.index(start))]


def inspect_case(job):
    folder = BATCH / job
    lines = (folder/'map.txt').read_text().splitlines()
    rows, cols = map(int, lines[0].split(','))
    assert len(lines) == rows + 1 and all(len(x) == cols for x in lines[1:])
    grid = ''.join(lines[1:])

    def neighbors(loc):
        r, c = divmod(loc, cols)
        return [rr*cols+cc for rr, cc in ((r, c+1), (r, c-1), (r+1, c), (r-1, c))
                if 0 <= rr < rows and 0 <= cc < cols and grid[rr*cols+cc] == '.']

    raw = (folder/'initial.txt').read_text().splitlines()
    initial = []
    for line in raw[1:]:
        values = list(map(int, line.split()))
        assert values[0] == len(values)-1
        initial.append(values[1:])
    assert int(raw[0]) == len(initial) == 32
    result = json.loads((folder/'result.json').read_text())
    receipt = json.loads((folder/'receipt.json').read_text())
    native = json.loads((folder/'native_receipt.json').read_text())
    assert result['status'] == receipt['status'] == 'COMPLETE'
    assert result['final_validated'] and native['initial_and_final_validated']
    assert receipt['job']['id'] == job and receipt['job']['top_k'] == 32
    cmd = result['native_command']
    for opt, value in (('--agentNum', '32'), ('--k', '32'),
                       ('--algorithm', 'bernoulie'), ('--destroyStrategy', 'RandomWalk'),
                       ('--replanAlgo', 'PP'), ('--neighborSize', '8'),
                       ('--screen', '0'), ('--seed', '0')):
        assert cmd[cmd.index(opt)+1] == value, (job, opt)
    final = [result['final_paths'][str(i)] for i in range(32)]
    parsed = []
    for a, line in enumerate((folder/'final.paths').read_text().splitlines()):
        assert line.startswith('Agent '+str(a)+':')
        parsed.append([int(r)*cols+int(c) for r, c in re.findall(r'\((\d+),(\d+)\)->', line)])
    assert parsed == final
    item = {'case': job, 'input_sha256': {n: sha(folder/n) for n in
            ('map.txt', 'initial.txt', 'final.paths', 'result.json', 'attempts.jsonl')}, 'agents': []}
    for a, (before, after) in enumerate(zip(initial, final)):
        assert before[0] == after[0] and before[-1] == after[-1]
        # Graph BFS computes labels only; it neither plans MAPF paths nor calls
        # the author solver, random walk, repair, or a scientific-run entrypoint.
        distance = {before[-1]: 0}
        queue = deque([before[-1]])
        while queue:
            loc = queue.popleft()
            for nb in neighbors(loc):
                if nb not in distance:
                    distance[nb] = distance[loc]+1
                    queue.append(nb)
        entry = {'agent': a, 'static_distance': distance[before[0]],
                 'initial_cost': len(before)-1, 'final_cost': len(after)-1,
                 'path_changed': before != after}
        for name, path in (('initial', before), ('final', after)):
            cost = len(path)-1
            delay = cost-distance[path[0]]
            entry[name+'_delay'] = delay
            assert delay >= 0
            assert all(0 <= x < rows*cols and grid[x] == '.' for x in path)
            for x, y in zip(path, path[1:]):
                assert x == y or y in neighbors(x)
            candidates = [(t, x, nb) for t, x in enumerate(path)
                          for nb in neighbors(x)+[x] if t+1+distance[nb] < cost]
            entry[name+'_strict_start_candidates'] = len(candidates)
            if delay == 0:
                assert all(t+distance[x] == cost for t, x in enumerate(path))
                assert not candidates
        item['agents'].append(entry)
    for name in ('initial', 'final'):
        item[name+'_summary'] = {
            'soc': sum(e[name+'_cost'] for e in item['agents']),
            'static_sum': sum(e['static_distance'] for e in item['agents']),
            'delay_histogram': dict(sorted(Counter(e[name+'_delay'] for e in item['agents']).items())),
            'delayed_agents': [e['agent'] for e in item['agents'] if e[name+'_delay'] > 0]}
    assert item['initial_summary']['soc'] == result['initial_soc'] == native['initial_soc']
    assert item['final_summary']['soc'] == result['final_soc'] == native['final_soc']
    item['changed_agents'] = [e['agent'] for e in item['agents'] if e['path_changed']]
    return item


def main():
    manifest = checked_json(SCI/'config/address_attempt_trace_v1_manifest.json', MANIFEST_SHA)
    batch = checked_json(BATCH/'RUN_RECEIPT.json', RECEIPT_SHA)
    build = checked_json(SCI/'budget_trace_build_receipt.json', BUILD_SHA)
    assert tuple(j['id'] for j in manifest['jobs']) == JOBS
    assert tuple(j['job'] for j in batch['jobs']) == JOBS
    assert batch['counts'] == {'COMPLETE': 2, 'FAILED_OR_INCOMPLETE': 0, 'NOT_RUN_AFTER_BATCH_STOP': 0}
    for name, pin in batch['artifacts'].items():
        artifact(BATCH/name, pin)
    for job in JOBS:
        receipt = json.loads((BATCH/job/'receipt.json').read_text())
        for name, pin in receipt['artifacts'].items():
            artifact(BATCH/job/name, pin)
    # Pin actual source used for the frozen binary, not current editable modules.
    for name in ('src/LNS.cpp', 'src/Instance.cpp', 'inc/BasicLNS.h'):
        artifact(AUTHOR/name, build['author_files'][name])
    pinned_sources = {}
    for name in ('src/LNS.cpp', 'src/driver.cpp', 'inc/address_adapter_support.h'):
        pin = build['extension_sources']['address_budget'][name]
        artifact(OVERLAY/name, pin)
        pinned_sources[name] = pin['sha256']
    lns = (OVERLAY/'src/LNS.cpp').read_text()
    driver = (OVERLAY/'src/driver.cpp').read_text()
    support = (OVERLAY/'inc/address_adapter_support.h').read_text()
    constructor = method(lns, 'LNS::LNS(', 'bool LNS::run()')
    assert 'alpha = std::vector<int>(num_agent, 1);' in constructor
    assert 'beta = std::vector<int>(num_agent, 1);' in constructor
    assert 'algorithm == "bernoulie"' in constructor and 'algo = BERNOULIE;' in constructor
    assert 'config.seeds.seed(config.seed);' in driver and 'srand(config.seed);' in driver
    assert 'inline unsigned next_seed() { return state().seeds(); }' in support
    bernoulli = method(lns, 'int LNS::bernoulie()', 'int LNS::normal()')
    assert 'auto rd = [](){ return address_adapter::next_seed(); };' in bernoulli
    assert 'std::mt19937 gen(rd());' in bernoulli
    assert 'beta_dist(alpha[i], beta[i])' in bernoulli
    assert bernoulli.count('frequency') == 1 and '(*frequency)[best_agent]++;' in bernoulli
    assert bernoulli.index('(*frequency)[best_agent]++') > bernoulli.index('beta_dist(gen)')
    assert 'current_index = best_agent;' in bernoulli
    group = method(lns, 'bool LNS::generateNeighborByRandomWalk(', 'int LNS::wrapper()')
    assert 'a = i;' in group and 'if (neighbors_set.size() < 2)' in group
    assert 'alpha[' not in group and 'beta[' not in group
    run = method(lns, 'bool LNS::run()', 'bool LNS::getInitialSolution()')
    assert 'if(!succ)\n            continue;' in run
    repair = method(lns, 'bool LNS::runPP()', 'bool LNS::runPPS()')
    assert '(neighbor.old_sum_of_costs - neighbor.sum_of_costs) > 0 ? 1 : -1' in repair
    assert 'alpha[current_index]++;' in repair and 'beta[current_index]++;' in repair
    source_facts = {
        'overlay_sha256': pinned_sources,
        'initial_alpha_beta': [1, 1],
        'frequency_only_incremented_after_selection_not_read_by_bernoulli': True,
        'bernoulli_generator_seed_source': 'deterministic address_adapter::next_seed(); global seeds seeded once with CLI seed=0',
        'group_failure_beta_update': False,
        'author_set_index_as_agent_id_preserved': True,
        'line_anchors': {needle: [i for i, line in enumerate(lns.splitlines(), 1) if needle in line]
                         for needle in ('alpha = std::vector<int>', 'beta = std::vector<int>',
                                        'a = i;', 'int LNS::bernoulie()', '(*frequency)[best_agent]++;',
                                        't + 1 + next_h_val < upperbound', 'beta[current_index]++;')}}
    cases = [inspect_case(job) for job in JOBS]
    random_case = cases[0]
    assert random_case['initial_summary']['delayed_agents'] == [19]
    assert not random_case['changed_agents']
    assert random_case['agents'][0]['initial_delay'] == 0
    attempts = [json.loads(line) for line in (BATCH/JOBS[0]/'attempts.jsonl').read_text().splitlines()]
    assert len(attempts) == 5
    for attempt in attempts:
        assert attempt['primary_stop'] == 'COST_STOP' and not attempt['accepted']
        assert len(attempt['primary_returns']) == attempt['group_size']
        assert all(r['stop'] == 'FOUND' and not r['empty'] for r in attempt['primary_returns'])
        assert sum(r['path_cost'] for r in attempt['primary_returns']) >= attempt['old_group_cost']
    denominator = math.comb(31+6, 6)
    out = {'scope': 'OFFLINE_BFS_LABELS_ON_FROZEN_PATHS_NO_AUTHOR_SEARCH',
           'status': 'PASS', 'script_sha256': sha(Path(__file__)),
           'manifest_sha256': MANIFEST_SHA, 'batch_receipt_sha256': RECEIPT_SHA,
           'build_receipt_sha256': BUILD_SHA, 'batch_artifacts_verified': len(batch['artifacts']),
           'fixed_job_order': list(JOBS), 'source_facts': source_facts, 'cases': cases,
           'random_source_deduction': {
               'classification': 'SOURCE_AND_FROZEN_PATH_DEDUCTION_NOT_OBSERVED_SEED_LOG',
               'only_possible_group_seed': 19,
               'scope_condition': 'All unchanged zero-delay seed paths cannot take a strict-shortening first step; preserved a=i switches their singleton continuation to agent0, also zero-delay here.',
               'deduced_five_repair_seeds': [19]*5,
               'deduced_after_five_cost_stops_alpha_beta_agent19': [1, 6],
               'other_31_alpha_beta': [1, 1],
               'ideal_independent_beta_win_probability': {'formula': 'E[X^31]=1/binom(37,6), X~Beta(1,6)',
                                                        'numerator': 1, 'denominator': denominator,
                                                        'value': 1/denominator},
               'limitation': 'Analytic sampling-model probability, not measured seed frequency, timing attribution, finite-PRNG guarantee, or performance result.'},
           'proof': 'For a legal unit-edge path of shortest length L=h(s), t+h(x_t)=L. Consistent graph distance gives h(x_t)<=1+h(y), hence t+1+h(y)>=L for every neighbor including wait. No strict-shortening first step exists.',
           'scientific_runs_executed': 0}
    OUTPUT.write_text(json.dumps(out, indent=2)+'\n')
    print(json.dumps({'status': out['status'], 'batch_artifacts_verified': out['batch_artifacts_verified'],
                      'output': str(OUTPUT), 'fixed_job_order': list(JOBS),
                      'cases': [{k: c[k] for k in ('case', 'initial_summary', 'final_summary', 'changed_agents')}
                                for c in cases]}, indent=2))


if __name__ == '__main__':
    main()
