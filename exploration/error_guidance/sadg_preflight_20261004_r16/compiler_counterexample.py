#!/usr/bin/env python3
"""Actual original compiler and isolated patch on a valid two-agent MAPF plan."""
import importlib.util
import json
import sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('r16_core',HERE/'run_preflight.py');c=importlib.util.module_from_spec(sp);sp.loader.exec_module(c)
solution={'schedule':{
    'agent0':[dict(x=0,y=0,t=0),dict(x=1,y=0,t=1),dict(x=2,y=0,t=2)],
    'agent1':[dict(x=0,y=-2,t=0),dict(x=0,y=-1,t=1),dict(x=0,y=0,t=2),dict(x=0,y=1,t=3)]}}
dim={'dimensions':{'resolution':2,'x_offset':0,'y_offset':0}}
original=c.compile_sadg(c.Plan(solution,dim),c.LOG)
sys.path.insert(0,str(HERE/'isolated_patch'))
sp=importlib.util.spec_from_file_location('r16_compiler',HERE/'isolated_patch/compiler.py');patch=importlib.util.module_from_spec(sp);sp.loader.exec_module(patch)
patched=patch.compile_sadg(c.Plan(solution,dim),c.LOG)
a=c.snapshot(original,5);b=c.snapshot(patched,5)
assert a['groups'][0]['dependencies'][0]['reverse']==['v_1_2','v_0_1']
assert b['groups'][0]['dependencies'][0]['reverse'] is None
assert a['groups'][0]['switchable'] and not b['groups'][0]['switchable']
c.dump(HERE/'COMPILER_COUNTEREXAMPLE.json',dict(solution=solution,dimensions=dim,original=a,patched=b,
    expected='A starts at shared vertex; its first move has no predecessor; reverse must be unavailable.',
    actual_optimizer_calls=0,pass_regression=True))
print('Original k=0 wraps to last action; isolated patch makes reverse unavailable. 0 optimizer calls.')
