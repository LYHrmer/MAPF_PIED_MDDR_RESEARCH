"""Root checks actual accepted task ENDs and first action divergences.

Reads saved native logs without importing experiment code. Matched-task times
are descriptive diagnostics, not a replacement for completed-task counts.
"""
from pathlib import Path
from collections import Counter
import hashlib
import json

HERE = Path(__file__).resolve().parent
RAW = Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence')/HERE.name


def main():
    groups = {}
    for spec in json.loads((HERE/'runs.json').read_text())['runs']:
        if spec['split'] != 'test':
            continue
        root = RAW/'runs'/spec['id']
        receipt = json.loads((root/'receipt.json').read_text())
        assert receipt['error'] is None and receipt['true_horizon_tick'] == 4000
        tasks = {}
        with (root/'events.jsonl').open() as stream:
            for line in stream:
                if '"kind":"end"' not in line:
                    continue
                row = json.loads(line)
                if not row['task']:
                    continue
                assert row['accepted'] and row['task_id'] >= 0
                key = (int(row['robot']), row['task_id'])
                assert key not in tasks
                tasks[key] = row['tick']
        decisions = [json.loads(line) for line in (root/'decisions.jsonl').open()]
        assert len(decisions) == receipt['decisions']
        key = (spec['map'], spec['condition'])
        groups.setdefault(key, {})[spec['policy']] = (tasks, decisions)
    totals = Counter(); comparisons = []
    for key, policies in sorted(groups.items()):
        assert set(policies) == {'hm_GPIBT','trained','history','learned'}
        for policy, (tasks, _) in policies.items():
            totals[policy] += len(tasks)
        ht, hd = policies['history']; lt, ld = policies['learned']
        diverge = None
        for i, (h,l) in enumerate(zip(hd,ld)):
            if h['result']['actions'] != l['result']['actions']:
                assert h['view'] == l['view'] and h['snapshot'] == l['snapshot']
                for earlier_h, earlier_l in zip(hd[:i],ld[:i]):
                    assert earlier_h['view'] == earlier_l['view'] and earlier_h['snapshot'] == earlier_l['snapshot']
                    assert earlier_h['result']['actions'] == earlier_l['result']['actions']
                diverge = dict(decision=i, tick=h['snapshot']['tick'], identical_public_and_physical_prefix=True)
                break
        common = set(ht)&set(lt)
        diffs = [lt[t]-ht[t] for t in common]
        comparisons.append(dict(map=key[0], condition=key[1], counts={p:len(t) for p,(t,_) in policies.items()},
                                first_action_divergence=diverge, matched_tasks=len(common),
                                learned_earlier=sum(d<0 for d in diffs), learned_equal=sum(d==0 for d in diffs), learned_later=sum(d>0 for d in diffs),
                                learned_minus_history_matched_tick_sum=sum(diffs),
                                only_history_tasks=len(set(ht)-set(lt)), only_learned_tasks=len(set(lt)-set(ht))))
    result = dict(status='PASS', scope='Root independent accepted native task END counts and same-prefix actual action divergence; timing sum conditional on matched tasks',
                  script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), totals=dict(totals), comparisons=comparisons)
    (HERE/'ROOT_TEST_AUDIT.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))


if __name__=='__main__':
    main()
