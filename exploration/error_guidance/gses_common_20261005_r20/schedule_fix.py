#!/usr/bin/env python3
"""Explicit correction of invalid nominal path timestamps before any Astar ran."""
import argparse,copy,json
from pathlib import Path
import phase1

ROOT=Path(__file__).resolve().parent
DEST=ROOT/'valid_nominal_schedule'


def register():
    old=json.loads((ROOT/'PHASE1_REGISTRATION.json').read_text())
    if (DEST/'PHASE1_REGISTRATION.json').exists():raise RuntimeError('already registered')
    reg=copy.deepcopy(old);reg.update(registered_utc=phase1.now(),amendment='All four original invocations stopped at Graph constructor because both paths reached crossing at nominal t2. B nominal path timestamps are shifted +4; all coordinates, weights, choices and objectives unchanged. Original failures retained; no outcome-driven case selection.',
        supersedes_only_input_validity=False,original_registration_sha256=phase1.sha(ROOT/'PHASE1_REGISTRATION.json'),
        original_program_invocations=4,original_Astar_calls=0,new_native_call_cap=4,
        source_pins={str(Path('..')/n):phase1.sha(ROOT/n) for n in ['phase1.py','fraction_oracle.py','schedule_fix.py','QUALIFICATION.md']})
    reg['inputs']=[]
    for entry in old['inputs']:
        spec=json.loads(Path(entry['path']).read_text());spec['id']+='_valid_schedule'
        for waypoint in spec['solver_graph']['paths'][1]:waypoint[1]+=4
        spec['nominal_schedule_correction']='B timestamp +4 only; unchanged crossing order A then B'
        # Verify the construct_graph rejection cause is removed before calling.
        seen={}
        for aid,path in enumerate(spec['solver_graph']['paths']):
            for loc,t in path:
                key=(tuple(loc),t);assert key not in seen or seen[key]==aid;seen[key]=aid
        out=DEST/'inputs'/(spec['id']+'.json');phase1.write(out,spec)
        reg['inputs'].append(dict(id=spec['id'],path=str(out),sha256=phase1.sha(out)))
    phase1.write(DEST/'PHASE1_REGISTRATION.json',reg)
    print('registered corrected inputs',phase1.sha(DEST/'PHASE1_REGISTRATION.json'))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=['register','run']);args=parser.parse_args()
    if args.command=='register':register()
    else:phase1.HERE=DEST;phase1.run()
