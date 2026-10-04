#!/usr/bin/env python3
"""Same-history duration input adapter; original unmodified author optimizer."""
import argparse
import importlib.util
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('r16_core',HERE/'run_preflight.py')
c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
author_compile=c.compile_sadg


def duration_adapter(plan,logger):
    graph=author_compile(plan,logger)
    for i,v in enumerate(graph.vertices_by_agent['agent0']):
        if i>=1:v.expected_completion_time*=1.25
    return graph


def register():
    base=json.loads((HERE/'inputs/mini_public_history.json').read_text())
    models=[]
    for name,p in [('mini_public_history_rate',.6),('mini_measured_history_rate',.25)]:
        obj=dict(base,name=name,progress={'agent0':p,'agent1':.5},
            duration_adapter='history_rate_on_all_uncompleted_A_vertices',
            unfinished_duration_scale={'agent0':1.25,'agent1':1.0},
            duration_adapter_sha256=c.sha(__file__),core_optimizer_unchanged=True)
        c.dump(HERE/'inputs'/f'{name}.json',obj);models.append(obj)
    c.dump(HERE/'HISTORY_RATE_REGISTRATION.json',dict(new_unique_calls=2,cumulative_upper_bound=12,
        input_hashes={x['name']:c.key(x) for x in models},author_cap_seconds=60,
        public_history_only=True,coefficients_fitted=False,physical_suffix_runs_if_existing_graph=0))


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('action',choices=['register','solve']);ap.add_argument('--case');args=ap.parse_args()
    if args.action=='register':register()
    else:
        c.compile_sadg=duration_adapter
        c.solve(args.case)
