#!/usr/bin/env python3
"""In-memory corruption checks; no scientific execution or raw-file mutation."""
import json
from pathlib import Path
import sys
sys.dont_write_bytecode=True
from audit_episode import Auditor

ROOT=Path(__file__).resolve().parent.parent
EP=ROOT/'engine_smoke/standard_train8/episode.json'
CASE=ROOT/'data/cases/random-32-32-10__s01__n08/plan.json'


def main():
    reports=[]
    for name in ('budget','private_feature','history','capture','trajectory_gap','declared_success'):
        a=Auditor(EP,CASE,'dense_position');a.events_and_outcomes()
        # Mutate only the auditor's newly loaded memory, preserving all raw files.
        if name=='budget':a.e['query_count']+=1
        elif name=='private_feature':a.e['gates'][0]['public_snapshot']['future_speed']=.2
        elif name=='history':a.e['gates'][0]['public_snapshot']['agents'][0]['history_ratio']+=.5
        elif name=='capture':a.e['queries'][0]['progress']+=.1
        elif name=='trajectory_gap':a.e['segments'][0]['t0']+=.01
        elif name=='declared_success':
            # Engine's collision flag is kept; actual path now occupies another
            # agent's initial point for its first segment.
            seg=a.e['segments'][0];other=next(v for k,v in a.e['initial_positions'].items() if k!=seg['agent'])
            seg['p0']=list(other);seg['p1']=list(other)
        a.graph_adoptions();a.trajectory();a.public_and_queries()
        checks=[x['check'] for x in a.errors]
        expected={'budget':'total_queries','private_feature':'public_top_level_allowlist',
            'history':'public_history_ratio:','capture':'captured_physical_progress',
            'trajectory_gap':'full_time_coverage:','declared_success':'success_requires_collision_free'}[name]
        passed=any(c.startswith(expected) for c in checks)
        reports.append({'mutation':name,'detected_by_required_check':passed,'checks':checks[:12]})
    result={'passed':all(r['detected_by_required_check'] for r in reports),'in_memory_only':True,
        'native_or_solver_calls':0,'raw_files_modified':False,'negative_cases':reports}
    (ROOT/'review/VERIFIER_SELFCHECK.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result));assert result['passed']


if __name__=='__main__':main()
