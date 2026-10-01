"""Compare frozen physical starts/obstacles to the actual parser/controller coordinates.

This runs the real replay auditor's endpoint predicate before native execution.
The author controller reads ADG (col,row) as physical (-row,-col), while
flipped_coord=true returns the corresponding (row,col) planner state.
"""
from pathlib import Path
import json
import sys
import xml.etree.ElementTree as ET
from mapping_replay import endpoint_error

HERE = Path(__file__).resolve().parent
errors = []
checks = 0
for folder in sorted((HERE / 'inputs').iterdir()):
    environment = json.loads((folder / 'environment.json').read_text())
    layout = json.loads((folder / 'map.json').read_text())['layout']
    for team in (8, 16):
        config = ET.parse(folder / f'experiment_n{team}.argos').getroot()
        arena = config.find('arena')
        for robot in arena.findall('foot-bot'):
            owner = int(robot.attrib['id'])
            row, col = divmod(environment['starts'][owner], 32)
            x, y, _ = map(float, robot.find('body').attrib['position'].split(','))
            checks += 1
            error = endpoint_error({'x': x, 'y': y}, [col, row])
            if error > 1e-10:
                errors.append({'map': folder.name, 'N': team, 'robot': owner, 'intended_row_col': [row, col], 'physical_xy': [x, y], 'initial_replay_endpoint_error_m': error, 'author_initial_view_location': int(-x) * 32 + int(-y), 'intended_location': row * 32 + col})
        boxes = {box.attrib['id']: box for box in arena.findall('box')}
        for row, cells in enumerate(layout):
            for col, cell in enumerate(cells):
                if cell != '@':
                    continue
                checks += 1
                box = boxes[f'obstacle_{row}_{col}']
                x, y, _ = map(float, box.find('body').attrib['position'].split(','))
                if (x, y) != (-row, -col):
                    errors.append({'map': folder.name, 'N': team, 'obstacle': [row, col], 'physical_xy': [x, y], 'expected_xy': [-row, -col]})
result = {'passed': not errors, 'checks': checks, 'error_count': len(errors), 'errors': errors, 'mapping': 'planner(row,col) -> ADG(col,row) -> physical(x,y)=(-row,-col)', 'scope': 'input/parser coordinate contract; not a native run or continuous safety test'}
print(json.dumps(result, indent=2))
raise SystemExit(bool(errors))
