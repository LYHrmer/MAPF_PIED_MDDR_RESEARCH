"""Build TEST-only paired summaries and a figure from independently audited raw results."""
from collections import Counter, defaultdict
from fractions import Fraction as F
from pathlib import Path
import hashlib
import json
import statistics

P = Path(__file__).resolve().parent
POLICIES = ['WAIT', 'condition', 'budget_lookup', 'full', 'nohistory', 'nobudget', 'tasks_only']


def difference(row, base):
    low = F(base['time_low']) - F(row['time_high'])
    high = F(base['time_high']) - F(row['time_low'])
    tasks = row['tasks'] - base['tasks']
    return {'tasks': tasks, 'time_saved_lower': str(low), 'time_saved_upper': str(high),
            'queries_saved': base['queries'] - row['queries'],
            'J_gain_lower': str(tasks + low / 16385), 'J_gain_upper': str(tasks + high / 16385),
            'robust_J_gain': tasks + low / 16385 > 0,
            'same_all_task_service_records': row['service_sha256'] == base['service_sha256'],
            'same_query_occurrence_set': row['queried_occurrences_sha256'] == base['queried_occurrences_sha256']}


def main():
    source = P / 'ROOT_MACRO_AUDIT.json'
    audit = json.loads(source.read_text())
    assert audit['passed'] and not audit['partial'] and audit['observed_runs'] == 152
    rows = [r for r in audit['rows'] if r['split'] == 'test']
    assert len(rows) == 56
    worlds = defaultdict(dict)
    for r in rows:
        worlds[r['world']][r['policy']] = r
    assert len(worlds) == 8 and all(set(v) == set(POLICIES) for v in worlds.values())
    ordered = sorted(worlds, key=lambda w: (worlds[w]['condition']['family'], worlds[w]['condition']['budget']))
    paired, families = [], defaultdict(list)
    for w in ordered:
        for policy in POLICIES:
            r = worlds[w][policy]
            item = {k: r[k] for k in ['world', 'family', 'budget', 'policy', 'macro', 'tasks', 'queries', 'time_low', 'time_high']}
            for baseline in ['condition', 'WAIT', 'budget_lookup']:
                item['vs_' + baseline] = difference(r, worlds[w][baseline])
            paired.append(item)
            families[r['family'], policy].append(item)
    family_effects = []
    for (family, policy), group in sorted(families.items()):
        assert len(group) == 2 and {r['budget'] for r in group} == {8, 16}
        result = {'family': family, 'policy': policy}
        for baseline in ['condition', 'WAIT', 'budget_lookup']:
            ds = [r['vs_' + baseline] for r in group]
            result['vs_' + baseline] = {
                'mean_task_gain': str(F(sum(d['tasks'] for d in ds), 2)),
                'mean_time_saved_lower': str(sum((F(d['time_saved_lower']) for d in ds), F(0)) / 2),
                'mean_time_saved_upper': str(sum((F(d['time_saved_upper']) for d in ds), F(0)) / 2),
                'mean_queries_saved': str(F(sum(d['queries_saved'] for d in ds), 2))}
        family_effects.append(result)
    totals = []
    for budget in [8, 16, 'both']:
        for policy in POLICIES:
            selected = [r for r in rows if r['policy'] == policy and (budget == 'both' or r['budget'] == budget)]
            ns = [r['gate']['inference_ns'] for r in selected if r['gate'] and r['gate']['learned']]
            totals.append({'budget': budget, 'policy': policy, 'runs': len(selected),
                           'tasks': sum(r['tasks'] for r in selected), 'queries': sum(r['queries'] for r in selected),
                           'time_lower': str(sum((F(r['time_low']) for r in selected), F(0))),
                           'time_upper': str(sum((F(r['time_high']) for r in selected), F(0))),
                           'chosen_macros': dict(Counter(r['macro'] or 'NO_GATE' for r in selected)),
                           'inference_calls': len(ns), 'scoring_ns_median': statistics.median(ns) if ns else None,
                           'skip_interventions_reached': sum(len(r['interventions']) for r in selected)})
    report = {'passed': True, 'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
              'TEST_only': True, 'independent_families': 4, 'paired_budget_settings': 8,
              'totals': totals, 'paired': paired, 'family_effects': family_effects,
              'scope': 'Descriptive four-family heldout pilot; budgets repeat each family. Positive time saving is condition minus method. Query counts are not production compute costs. Inference timing is scoring only, excluding feature construction.'}
    (P / 'ROOT_TEST_RESULTS.json').write_text(json.dumps(report, indent=2) + '\n')
    draw(worlds, ordered, report)
    print(json.dumps([r for r in totals if r['budget'] == 'both'], indent=2), flush=True)


def draw(worlds, ordered, report):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
    methods = ['WAIT', 'budget_lookup', 'full', 'nohistory', 'nobudget', 'tasks_only']
    labels = ['WAIT', 'Budget lookup', 'Full model', 'No history', 'No budget', 'Task head only']
    values = [[], [], []]
    annotations = [[], [], []]
    row_labels = []
    for w in ordered:
        base = worlds[w]['condition']
        family = base['family']
        seed = family.rsplit('_', 1)[-1]
        row_labels.append(('Empty' if family.startswith('empty') else 'Random') + ' ' + seed + ' / B' + str(base['budget']))
        line = [[], [], []]
        text = [[], [], []]
        for policy in methods:
            d = difference(worlds[w][policy], base)
            lo, hi = F(d['time_saved_lower']), F(d['time_saved_upper'])
            time_uncertain = lo <= 0 <= hi
            numbers = [d['tasks'], 0 if time_uncertain else float((lo + hi) / 2), d['queries_saved']]
            for j, number in enumerate(numbers):
                line[j].append(number)
                text[j].append('≈0' if j == 1 and time_uncertain else f'{number:+.2f}' if j == 1 else f'{number:+d}')
        for j in range(3):
            values[j].append(line[j]); annotations[j].append(text[j])
    fig, axes = plt.subplots(1, 3, figsize=(13.4, 5.7), gridspec_kw={'wspace': .32})
    titles = ['(a) Completed tasks\nmethod − condition', '(b) Restricted completion sum\ncondition − method', '(c) Queries saved\ncondition − method']
    for j, ax in enumerate(axes):
        data = np.array(values[j]); limit = max(1., float(np.abs(data).max()))
        im = ax.imshow(data, cmap='RdBu', vmin=-limit, vmax=limit, aspect='auto')
        ax.set_xticks(range(6), labels, rotation=42, ha='right', fontsize=8)
        ax.set_yticks(range(8), row_labels if j == 0 else [''] * 8, fontsize=8)
        ax.set_title(titles[j], fontsize=10, pad=12)
        for i in range(8):
            for k in range(6):
                ax.text(k, i, annotations[j][i][k], ha='center', va='center', fontsize=8,
                        color='white' if abs(data[i, k]) > .62 * limit else '#18222c')
        for line in [1.5, 3.5, 5.5]:
            ax.axhline(line, color='white', linewidth=1.6)
        ax.tick_params(length=0)
        cb = fig.colorbar(im, ax=ax, orientation='horizontal', pad=.28, fraction=.04)
        cb.ax.tick_params(labelsize=8)
    fig.subplots_adjust(left=.145, right=.985, top=.83, bottom=.25)
    fig.suptitle('R12 frozen TEST: four independent families, two paired budgets', fontsize=13, y=.96)
    fig.text(.5, .06, 'Read task outcomes first. ≈0 denotes an interval containing zero; query counts are not production compute costs.',
             ha='center', fontsize=8)
    out = P / 'figures'; out.mkdir(exist_ok=True)
    paths = []
    for ext in ['png', 'pdf', 'svg']:
        target = out / ('r12_test_comparison.' + ext)
        fig.savefig(target, dpi=600 if ext == 'png' else 180, bbox_inches='tight')
        paths.append(target)
    fig.savefig(out / 'preview.png', dpi=120, bbox_inches='tight')
    plt.close(fig)
    manifest = {'data_sha256': hashlib.sha256((P / 'ROOT_TEST_RESULTS.json').read_bytes()).hexdigest(),
                'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                'files': {p.name: {'bytes': p.stat().st_size, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in paths + [out / 'preview.png']}}
    (out / 'MANIFEST.json').write_text(json.dumps(manifest, indent=2) + '\n')


if __name__ == '__main__':
    main()
