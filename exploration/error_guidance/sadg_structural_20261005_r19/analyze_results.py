"""Read-only paired analysis after the complete registered matrix is available."""
from pathlib import Path
from collections import defaultdict, Counter
import json
import random
import statistics
import hashlib

HERE=Path(__file__).resolve().parent
def read(p): return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,x):Path(p).write_text(json.dumps(x,indent=2,sort_keys=True,allow_nan=False)+'\n')
def mean(xs):return statistics.mean(xs) if xs else None

def main():
    summary=read(HERE/'SUMMARY.json');reg=read(HERE/'EXPERIMENT_REGISTRATION.json')
    rows=summary['rows'];assert not summary['missing'] and len(rows)==reg['planned_rows']
    expected={(c['case_id'],d,a) for c in reg['cases'] for d in reg['disturbances']
        for a in (reg['scale_extension_arms'] if c['num_agents']==64 else reg['arms'])}
    assert len(expected)==len(rows) and {(r['case_id'],r['disturbance'],r['arm']) for r in rows}==expected
    groups=defaultdict(list)
    for r in rows:groups[(r['stratum'],r['arm'])].append(r)
    aggregates=[]
    for (stratum,arm),rr in sorted(groups.items()):
        active=[r for r in rr if r['restricted_sum_completion'] is not None]
        aggregates.append(dict(stratum=stratum,arm=arm,registered_worlds=len(rr),executed_worlds=len(active),
            completed_worlds=sum(r['success'] for r in rr),initial_failures=len(rr)-len(active),
            completed_agents=sum(r['completed_agents'] for r in rr),
            sum_completion=sum(r['restricted_sum_completion'] for r in active),
            query_count=sum(r['query_count'] for r in rr),
            new_native_calls=sum(r.get('solver_calls',0) for r in rr),
            solve_rejections=sum(r.get('solve_failures',0) for r in rr)))
    pairs=[]
    contrasts=[('learned_no_query','history_no_query'),('ewma_no_query','history_no_query'),
        ('learned_no_query','ewma_no_query'),('history_structural','history_no_query'),
        ('learned_structural','learned_no_query'),('ewma_structural','ewma_no_query'),
        ('learned_structural','history_structural'),('learned_structural','ewma_structural'),
        ('history_structural','history_rule'),('learned_structural','fixed_update')]
    index={(r['stratum'],r['case_id'],r['disturbance'],r['arm']):r for r in rows}
    for stratum in ('core','scale_extension'):
        for method,control in contrasts:
            paired=[]
            for row in rows:
                if row['stratum']!=stratum or row['arm']!=method:continue
                ref=index.get((stratum,row['case_id'],row['disturbance'],control))
                if not ref or row['restricted_sum_completion'] is None or ref['restricted_sum_completion'] is None:continue
                delta=row['restricted_sum_completion']-ref['restricted_sum_completion']
                paired.append(dict(case_id=row['case_id'],disturbance=row['disturbance'],family=row['family'],
                    delta=delta,relative_percent=100*delta/ref['restricted_sum_completion'],
                    query_delta=row['query_count']-ref['query_count']))
            if not paired: continue
            families=defaultdict(list)
            for p in paired:families[p['family']].append(p['relative_percent'])
            fm={k:mean(v) for k,v in families.items()}; values=list(fm.values())
            rng=random.Random(1905);boot=sorted(mean(rng.choices(values,k=len(values))) for _ in range(20000))
            pairs.append(dict(stratum=stratum,method=method,control=control,worlds=len(paired),families=len(fm),
                better=sum(p['delta'] < -1e-7 for p in paired),worse=sum(p['delta'] > 1e-7 for p in paired),
                tie=sum(abs(p['delta'])<=1e-7 for p in paired),total_delta=sum(p['delta'] for p in paired),
                query_delta=sum(p['query_delta'] for p in paired),mean_family_relative_percent=mean(values),
                exploratory_family_bootstrap_95=[boot[499],boot[19499]],family_means=fm,paired=paired))
    result=dict(schema='r19-paired-analysis-v1',summary_sha256=sha(HERE/'SUMMARY.json'),
        registration_sha256=sha(HERE/'EXPERIMENT_REGISTRATION.json'),aggregates=aggregates,contrasts=pairs,
        conventions='negative completion delta favors method; initial MAPF failures counted separately, never imputed as observed execution',
        inference='small family count; exploratory intervals; scale extension reported independently',
        code_sha256=sha(__file__))
    save(HERE/'ANALYSIS.json',result)
    lines=['# R19 完整执行结果表','',
        '负的完成时间差表示前一方法更快。所有对照共用冻结作者 SADG 核心；预测器/查询规则属于内部因子，不是额外发表算法。', '',
        '| 层 | 方法 | 完成/登记世界 | 初始规划失败 | 总完成时间 | 查询 |',
        '|---|---|---:|---:|---:|---:|']
    for a in aggregates:lines.append(f'| {a["stratum"]} | {a["arm"]} | {a["completed_worlds"]}/{a["registered_worlds"]} | {a["initial_failures"]} | {a["sum_completion"]:.6f} | {a["query_count"]} |')
    lines+=['','| 层 | 方法 − 对照 | 好/差/同 | 总时间差 | 查询差 | 族均相对差 | 探索性95%区间 |',
        '|---|---|---:|---:|---:|---:|---|']
    for p in pairs:
        lo,hi=p['exploratory_family_bootstrap_95']
        lines.append(f'| {p["stratum"]} | {p["method"]} − {p["control"]} | {p["better"]}/{p["worse"]}/{p["tie"]} | {p["total_delta"]:.6f} | {p["query_delta"]} | {p["mean_family_relative_percent"]:.5f}% | [{lo:.5f}%, {hi:.5f}%] |')
    lines+=['','核心 6 个地图×场景族；扩规模可执行结果仅 2 族，另 1 族初始规划超时。区间不能替代更大样本独立确认。','']
    (HERE/'RESULT_TABLES.md').write_text('\n'.join(lines))
    print(json.dumps(dict(rows=len(rows),aggregate_rows=len(aggregates),contrasts=len(pairs))))

if __name__=='__main__':main()
