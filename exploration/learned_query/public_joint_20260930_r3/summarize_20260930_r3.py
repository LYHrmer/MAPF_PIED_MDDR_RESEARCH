"""Publish all registered results and PUBLIC structural diagnostics; no policy edits."""
import csv,json
from decimal import Decimal
from pathlib import Path
HERE=Path(__file__).resolve().parent
def main():
    audit=json.loads((HERE/'AUDIT_20260930_r3.json').read_text());sup=json.loads((HERE/'support_20260930_r3.json').read_text())
    episodes=audit['episodes'];lookup={(e['condition'],e['policy'],e['capacity']):e for e in episodes}
    names=list(dict.fromkeys(e['condition'] for e in episodes));rows=[]
    for e in episodes:
        wait=lookup[(e['condition'],'WAIT',0)]
        rows.append({k:e[k] for k in ['condition','policy','capacity','served','queries','deadlock','restricted_flow_sum']}|
          dict(extra_heads_vs_WAIT=e['served']-wait['served'],restricted_flow_gain_vs_WAIT=str(Decimal(wait['restricted_flow_sum'])-Decimal(e['restricted_flow_sum']))))
    with (HERE/'JOINT_ALL_RESULTS_20260930_r3.csv').open('x') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    features=[];byagent={r['agent']:r for r in sup['robots']}
    for src,requester in sup['initial_follow_pairs']:
        r=byagent[requester];path=set(map(tuple,r['route_points']));others=[a for a in byagent if a!=requester]
        intersections={str(a):[list(p) for p in sorted(path&set(map(tuple,byagent[a]['route_points'])))] for a in others}
        terminal_intrusions=[dict(agent=a,current_head=byagent[a]['task'],terminal=byagent[a]['goal'],
          requester_first_path_index=next(i for i,p in enumerate(r['route_points']) if p==byagent[a]['goal']))
          for a in others if tuple(byagent[a]['goal']) in path]
        features.append(dict(source=src,requester=requester,current_head=r['task'],remaining_public_route_items=len(r['route']),
          other_public_head_path_intersections=intersections,other_current_head_terminals_in_requester_path=terminal_intrusions,
          uses_future_tasks=False,uses_private_eta_or_progress=False))
    obj=dict(all_registered_episodes=rows,public_structural_features=features,features_used_to_change_policy=False,
       diagnostic_only_after_registered_run=True,one_source_trace_cannot_support_map_generalization=True)
    with (HERE/'JOINT_RESULTS_AND_FEATURES_20260930_r3.json').open('x') as f:json.dump(obj,f,indent=2);f.write('\n')
    labels=[('WAIT',0),('RR',1),('task_rank',1),('task_trigger',1),('RR',2),('task_rank',2)]
    print('| 条件 | WAIT B0 | RR B1 | 方向排序 B1 | 触发 B1 | RR B2 | 方向排序 B2 |')
    print('|---|---:|---:|---:|---:|---:|---:|')
    for n in names:
        values=[]
        for p,b in labels:
            e=lookup[(n,p,b)];values.append(f"{e['served']}/4 · q{e['queries']} · {Decimal(e['restricted_flow_sum']):.6f}")
        print('| '+n+' | '+' | '.join(values)+' |')
    print(json.dumps(features,indent=2))
if __name__=='__main__':main()
