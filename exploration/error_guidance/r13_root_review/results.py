"""Descriptive paired effects, retaining every registered adopted continuation."""
from fractions import Fraction as F
from pathlib import Path
import csv, json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

P = Path(__file__).resolve().parent
SOURCE = P.parent / 'gses_online_adoption_20261004_r13'
rows = json.loads((SOURCE / 'RESULTS.json').read_text())
control = {r['spec']['id']: r for r in rows if r['method'] == 'original'}
out = []
for r in rows:
    if r['method'] == 'original': continue
    base = control[r['spec']['id']]
    out.append({'id': r['id'], 'case': r['spec']['case'], 'at': r['spec']['at'],
                'profile': r['spec']['profile'], 'method': r['method'],
                'sum_gain': str(F(base['sum_completion_time']) - F(r['sum_completion_time'])),
                'makespan_gain': str(F(base['makespan']) - F(r['makespan'])),
                'author_search_us': r['author_search_us'], 'changed': r['changed']})
assert len(out) == 24
with (P / 'PAIRED_EFFECTS.csv').open('w') as f:
    w = csv.DictWriter(f, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
summary = {'passed': True, 'comparisons': 24, 'source_instances': 2, 'contexts': 12,
           'sum_better': sum(F(r['sum_gain']) > 0 for r in out),
           'sum_worse': sum(F(r['sum_gain']) < 0 for r in out),
           'makespan_better': sum(F(r['makespan_gain']) > 0 for r in out),
           'makespan_worse': sum(F(r['makespan_gain']) < 0 for r in out),
           'makespan_equal': sum(F(r['makespan_gain']) == 0 for r in out),
           'sum_gain_range': [str(min(F(r['sum_gain']) for r in out)), str(max(F(r['sum_gain']) for r in out))],
           'rows': out}
(P / 'ROOT_PAIRED_RESULTS.json').write_text(json.dumps(summary, indent=2) + '\n')
fig, axes = plt.subplots(1, 2, figsize=(12, 5), gridspec_kw={'wspace': .35})
for ax, case, title in zip(axes, sorted({r['case'] for r in out}), ['Random map · 60 agents', 'Warehouse · 110 agents']):
    group = [r for r in out if r['case'] == case]
    for method, marker, color in [('GSES', 'o', '#246B8E'), ('Improved_GSES', '^', '#B86432')]:
        items = [r for r in group if r['method'] == method]
        ax.scatter([float(F(r['sum_gain'])) for r in items], [float(F(r['makespan_gain'])) for r in items],
                   marker=marker, color=color, s=70, label=method.replace('_', ' '), alpha=.8)
    ax.axvline(0, color='.55', linewidth=.8); ax.axhline(0, color='.55', linewidth=.8)
    ax.set_title(title); ax.set_xlabel('Completion-sum gain (original − adopted)')
    ax.set_ylabel('Makespan gain (original − adopted)')
    ax.grid(alpha=.15); ax.legend(fontsize=8)
    ax.spines[['top', 'right']].set_visible(False)
fig.suptitle('Legal online adoption changes execution, with objective trade-offs', fontsize=13)
fig.text(.5, .015, 'Two source instances × two checkpoints × three profiles × two author solvers; descriptive only. Overlapping points retained.',
         ha='center', fontsize=8)
fig.subplots_adjust(bottom=.16, top=.84)
for suffix in ['pdf', 'svg', 'png']: fig.savefig(P / ('r13_adoption_tradeoff.' + suffix), dpi=180)
(P / 'FIGURE_CAPTION.md').write_text('Each point is a registered adopted continuation compared with the identical checkpoint continued under the original graph. Positive values are improvements. All 24 comparisons are retained, including overlapping points. The 12 contexts derive from only two source instances; no inferential confidence intervals or independent-sample success rate are implied. Solver host time is recorded separately and is not inserted as physical delay. Raw fractions are in PAIRED_EFFECTS.csv.\n')
print(json.dumps({k:v for k,v in summary.items() if k != 'rows'}))
