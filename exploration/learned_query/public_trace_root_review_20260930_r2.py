"""Root review: public END causality, raw outcomes and immutable artifact binding."""
from collections import Counter, defaultdict
from fractions import Fraction as F
import hashlib
import importlib
import json
import argparse
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
PACKAGE = HERE / 'public_trace_20260930_r2'
SEMANTIC = PACKAGE / 'semantic_successor_20260930_r2'
sys.dont_write_bytecode = True
sys.path.insert(0, str(SEMANTIC))
base = importlib.import_module('audit_20260930_r2')
hard = importlib.import_module('hardened_audit_20260930_r2')
actor = importlib.import_module('end_only_replay_20260930_r2')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bounds(value):
    return F(value['lower'], value['denominator']), F(value['upper'], value['denominator'])


def main():
    receipt = json.loads((SEMANTIC / 'receipt_20260930_r2.json').read_text())
    public = json.loads((SEMANTIC / 'public_source_20260930_r2.json').read_text())
    clean = json.loads((SEMANTIC / 'end_only_replay_20260930_r2.json').read_text())
    archive = HERE / 'public_trace_author_archive_20260930_r2'
    if archive.exists():
        archived = json.loads((archive / 'manifest.json').read_text())
        for relative, identity in archived['files'].items():
            assert sha(archive / relative) == identity['sha256']
        public['origin'] = str(archive / 'original_run/result.json')
        public['map_path'] = str(archive / 'author_inputs/lifelong_benchmark/random/maps/random-32-32-20.map')
    assert public['source_commit'] == '74cfba3c81a0c165c2e7044dea6fd4dee8ddf415'
    assert public['source_sha256'] == '67c10baa0faa4b10200591982d970368c6f8292e87959a47b8f7d0d832849b10'
    assert sha(Path(public['map_path'])) == public['map_sha256']
    hard.validate_author_bindings(public)
    assert hard.validate_native_inputs(receipt, public) == 4260
    recomputed = base.audit(receipt, public)
    assert recomputed == json.loads((SEMANTIC / 'audit_20260930_r2.json').read_text())
    assert sha(SEMANTIC / 'receipt_20260930_r2.json') == clean['original_native_receipt_sha256']
    assert clean['native_rerun'] is False and clean['private_fields_enter_END_only_actor'] is False
    counts = defaultdict(Counter)
    total = Counter()
    model = None
    feedback = comparisons = history_checks = 0
    examples = []
    for run in receipt['runs']:
        history = defaultdict(list)
        for phase in run['phases']:
            tick = phase['tick']
            pairs = public['phases'][tick]['pairs']
            assert sum(p['terminal'] for p in pairs) <= 1
            if model is not None:
                actual = actor.choose_END_only(pairs, model, history, run['run_id'], tick)
                assert actual == phase['choices']
                for arm, choice in actual.items():
                    expected = []
                    for pair in pairs:
                        prior = history[pair['source_agent']]
                        for obs in prior:
                            assert obs['tick'] < tick and bounds(obs['received'])[1] + 4 * obs['tick'] < 4 * tick
                            assert set(obs) == actor.ALLOWED
                            history_checks += 1
                        h = pair['source_heading']
                        if arm == 'WAIT': probability = F(0)
                        elif arm == 'RR': probability = F(1)
                        elif arm == 'global_bin': probability = model['global']
                        elif arm in ('direction_bin', 'categorical_supervised'): probability = model['direction'][h]
                        elif arm == 'analytic_direction': probability = F(1, 10) if h in ('NO', 'SO') else F(9, 10)
                        elif arm == 'lag2': probability = F(bounds(prior[-2]['original_END'])[1] < F(5, 4)) if len(prior) >= 2 else model['global']
                        else: raise AssertionError(arm)
                        if pair['terminal'] and probability > 0: expected.append((probability, pair['pair']))
                    selected = min(expected, key=lambda p: (-p[0], p[1]))[1] if expected else None
                    assert choice['selected_pair'] == selected
                comparisons += len(actual)
            command = receipt['commands'][phase['command_index']]
            events = [json.loads(s) for s in command['stdout'].splitlines() if s.startswith('{')]
            headings = {m['agent']: m['heading'] for m in public['phases'][tick]['moves']}
            for event in events:
                if event['event'] != 'source_original_END_delivered': continue
                lo, hi = bounds(event['original_END'])
                assert hi < F(5, 4) or lo > F(5, 4)
                label = int(hi < F(5, 4))
                qlo, qhi = bounds(event['at_query_progress'])
                assert (qlo > F(13, 20)) if label else (qhi <= F(13, 20))
                obs = {k: event[k] for k in ['original_END', 'received', 'full_cap_uninterrupted', 'length']}
                obs.update(run_id=run['run_id'], tick=tick, agent=event['agent'], heading=headings[event['agent']])
                assert actor.decode_END_only(obs) == label
                history[event['agent']].append(obs)
                examples.append(obs)
                feedback += 1
                if run['split'] == 'train':
                    counts[obs['heading']][label] += 1
                    total[label] += 1
        if run['run_id'] == 'train_2207':
            model = {'direction': {h: F(c[1] + 1, sum(c.values()) + 2) for h, c in counts.items()},
                     'global': F(total[1] + 1, sum(total.values()) + 2)}
    assert examples == clean['actor_observations'] and feedback == 10746 and comparisons == 560
    assert sum(total.values()) == 3582
    negatives = {}
    example = examples[0]
    for name, observation in {
        'private_field': dict(example, at_query_progress=0),
        'threshold_straddle': dict(example, original_END={'lower': 124, 'upper': 126, 'denominator': 100}),
        'unsupported_length': dict(example, length=2),
        'interrupted_move': dict(example, full_cap_uninterrupted=False),
    }.items():
        try: actor.decode_END_only(observation)
        except AssertionError: negatives[name] = True
        else: negatives[name] = False
    assert all(negatives.values())
    manifest = {str(p.relative_to(PACKAGE)): {'bytes': p.stat().st_size, 'sha256': sha(p)}
                for p in sorted(PACKAGE.rglob('*')) if p.is_file() and '__pycache__' not in p.parts}
    out = {'status': 'passed', 'kind': 'root independent saved-evidence replay; no new physics run',
           'frozen_package_files': len(manifest), 'package_manifest': manifest,
           'source_counts': public['source_counts'], 'source_sha256': public['source_sha256'],
           'actual_native_checks': recomputed['native_checks'], 'actual_pair_episodes': 4260,
           'actual_terminal_endpoint_potentials': 96, 'public_END_feedback_verified': feedback,
           'END_only_choices_verified': comparisons, 'past_END_causal_checks': history_checks,
           'extra_actual_decoder_negative_controls': negatives,
           'maximum_terminal_candidates_per_phase': 1, 'trained_feedback_rows': 3582,
           'independent_learning_advantage': False, 'full_100_robot_execution': False,
           'published_baseline_comparison': False, 'production_complete_query': False}
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=HERE / 'public_trace_root_review_20260930_r2.json')
    target = parser.parse_args().output
    with target.open('x') as f: json.dump(out, f, indent=2); f.write('\n')
    print(json.dumps({k: v for k, v in out.items() if k != 'package_manifest'}, indent=2))


if __name__ == '__main__':
    main()
