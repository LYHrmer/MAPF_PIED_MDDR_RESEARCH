"""Plot root-recomputed paired outcomes; never choose a subset by performance."""
from pathlib import Path
import json

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent


def main():
    data = json.loads((HERE / 'ROOT_COMPLETE_AUDIT.json').read_text())
    assert data['passed'] and len(data['rows']) == 60
    rows = data['rows']
    assert all(r['error'] is None for r in rows)
    worlds = list(dict.fromkeys(r['world'] for r in rows))
    comparisons = [('WAIT', 'WAIT', '#707070'),
                   ('RR', 'Unpaced RR', '#319065'),
                   ('paced_condition', 'Paced condition rule', '#2579a8'),
                   ('paced_ridge_nohistory', 'Ridge without history', '#bf6534')]
    y = np.arange(len(worlds))
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 6.5), sharey=True)
    plt.rcParams['pdf.fonttype'] = 42
    for k, (reference, label, color) in enumerate(comparisons):
        pairs = []
        for world in worlds:
            group = {r['policy']: r for r in rows if r['world'] == world}
            model, baseline = group['paced_ridge_history'], group[reference]
            pairs.append(dict(task_delta=model['served'] - baseline['served'],
                              query_delta=model['queries'] - baseline['queries']))
        offset = (k - 1.5) * 0.18
        for ax, metric in zip(axes, ('task_delta', 'query_delta')):
            ax.scatter([p[metric] for p in pairs], y + offset,
                       color=color, s=35, label=label, zorder=3)
    labels = []
    for world in worlds:
        row = next(r for r in rows if r['world'] == world)
        labels.append(f"{'Empty' if row['map'].startswith('empty') else 'Random'} "
                      f"{row['seed']} / {'SHIFT' if row['shift'] else 'IID'} / N{row['N']}")
    axes[0].set_yticks(y, labels, fontsize=9)
    axes[0].invert_yaxis()
    axes[0].set_xlabel('Completed tasks: history ridge minus reference')
    axes[1].set_xlabel('Queries: history ridge minus reference')
    axes[0].set_title('A  Primary task outcome', loc='left', fontsize=12)
    axes[1].set_title('B  Query use (capacity 16)', loc='left', fontsize=12)
    scale_start = next(i for i, world in enumerate(worlds)
                       if next(r for r in rows if r['world'] == world)['split'] == 'scale')
    for ax in axes:
        ax.axvline(0, color='#333333', linewidth=0.8)
        ax.axhline(scale_start - 0.5, color='#888888', linewidth=0.8, linestyle='--')
        ax.grid(axis='x', color='#e2e2e2', zorder=0)
        ax.spines[['top', 'right']].set_visible(False)
    handles, legend_labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, legend_labels, loc='lower center', ncol=2,
               bbox_to_anchor=(0.58, 0.06), frameon=False, fontsize=9)
    fig.suptitle('R8 frozen held-out query policies: all 10 paired worlds', fontsize=14)
    fig.text(0.02, 0.02,
             'Dots compare the same world. IID / SHIFT share a task family; they are not independent replicates.\n'
             'Below dashed line: N32 after input-guard correction. Internal ablations; fewer queries alone do not imply improvement.',
             fontsize=8, color='#444444')
    fig.tight_layout(rect=(0, 0.14, 1, 0.94))
    for suffix in ('svg', 'pdf', 'png'):
        fig.savefig(HERE / f'root_heldout_results.{suffix}', dpi=200)
    (HERE / 'ROOT_FIGURE_CAPTION.md').write_text(
        '# R8完整留出配对图\n\n'
        '![全部测试与规模迁移配对](root_heldout_results.png)\n\n'
        '数据来自root逐事件重算的`ROOT_COMPLETE_AUDIT.json`，包含60个完成臂、10个world。'
        'N32原12臂因输入上限拒绝，完整保留在`ROOT_HELDOUT_AUDIT.json`；图中N32使用只修复输入上限的事后兼容后继，未改场景或模型。'
        '每行分别比较有历史ridge与WAIT、普通RR、相同分时预算条件规则、无历史ridge；横轴为有历史模型减对照。'
        '左图正值表示完成更多任务，右图表示多用或少用查询，二者不可互相替代。'
        '同地图/任务种子的IID与SHIFT属于同family；虚线下为N32冻结迁移，不与N16合并估计总体效应。'
        '这些策略属于内部机制消融，图中没有声称击败外部发表算法。\n\n'
        '由`plot_heldout_results.py`生成可编辑SVG、PDF及PNG，未筛选有利world。\n',
        encoding='utf-8')
    print('Wrote SVG, PDF, PNG and complete-world caption.')


if __name__ == '__main__':
    main()
