"""Offline verification of this portable artifact; no solver invocation."""
import argparse, copy, hashlib, json, re
from pathlib import Path
from validator import validate, InvalidTrace
from harness import ints, log_events

def selfcheck():
    valid = {'start': [[0,0],[0,2]], 'actualPaths': ['R','W'],
             'events': [[[0,0,'assigned'],[0,1,'finished'],[2,1,'assigned']],
                        [[1,0,'assigned'],[1,1,'finished'],[3,1,'assigned']]],
             'tasks': [[0,0,1],[1,0,2],[2,0,1],[3,0,2]],
             'numTaskFinished': 2, 'plannerTimes': [0.1]}
    assert validate(['...'], [0,2], [1,2], valid, 2, 1)['completed_tasks'] == 2
    mutations = []
    v=copy.deepcopy(valid); v['actualPaths']=['R','L']
    mutations.append(('vertex', ['...'], [0,2], [1,2], v))
    v=copy.deepcopy(valid); v['start']=[[0,0],[0,1]]; v['actualPaths']=['R','L']
    mutations.append(('reverse edge', ['..'], [0,1], [1,0], v))
    v=copy.deepcopy(valid); v['actualPaths']=['U','W']
    mutations.append(('out of bounds', ['...'], [0,2], [1,2], v))
    v=copy.deepcopy(valid)
    mutations.append(('obstacle', ['.@.'], [0,2], [0,2], v))
    v=copy.deepcopy(valid); v['actualPaths']=['X','W']
    mutations.append(('unknown action', ['...'], [0,2], [1,2], v))
    v=copy.deepcopy(valid); v['events'][0][1][1]=0
    mutations.append(('task events', ['...'], [0,2], [1,2], v))
    v=copy.deepcopy(valid); v['actualPaths']=['R,R','W']
    mutations.append(('incomplete action matrix', ['...'], [0,2], [1,2], v))
    rejected=[]
    for expected,grid,starts,tasks,v in mutations:
        try: validate(grid,starts,tasks,v,2,1)
        except InvalidTrace as error:
            assert expected in str(error), (expected,str(error))
            rejected.append(expected)
        else: raise AssertionError('negative control not rejected: '+expected)
    return {'positive_control':True,'negative_controls_rejected':rejected}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parent)
    root=parser.parse_args().root.resolve(); src=root/'author_inputs'; runs=root/'runs'
    archive=root/'archive_manifest.json'
    if archive.exists():
        for name,expected in json.loads(archive.read_text())['file_sha256'].items():
            assert hashlib.sha256((root/name).read_bytes()).hexdigest()==expected,name
    manifest=json.loads((runs/'manifest.json').read_text())
    for name,expected in manifest['author_input_sha256'].items():
        assert hashlib.sha256((src/name).read_bytes()).hexdigest()==expected,name
    grid=(src/'maps/sortation_small.map').read_text().splitlines()[4:]
    starts=ints(src/'agents/sortation_small_0_200.agents')
    tasks=ints(src/'tasks/sortation_small_0.task')
    rows=[]
    for case,filename,n,seed in manifest['fixed_cases']:
        d=runs/case; known=json.loads((d/'verification.json').read_text())
        for name,expected in known['artifact_sha256'].items():
            assert hashlib.sha256((d/name).read_bytes()).hexdigest()==expected,(case,name)
        data=json.loads((d/'result.json').read_text())
        actual=validate(grid,starts,tasks,data,n,manifest['horizon'])
        assert actual.pop('event_stream')==log_events(d/'event_log.txt')
        for key,value in actual.items(): assert value==known[key],(case,key)
        actual_seed=re.findall(r'^---priority-initialization-seed,(\d+)$',(d/'stdout.log').read_text(),re.M)
        assert actual_seed==[str(seed)]
        rows.append(dict(case=case,**{k:actual[k] for k in ['agents','horizon','completed_tasks','assigned_tasks','pending_tasks','actions_replayed','positions_checked']}))
    print(json.dumps({'status':'passed','validator_selfcheck':selfcheck(),'cases':rows,
                      'total_actions':sum(x['actions_replayed'] for x in rows),
                      'total_positions':sum(x['positions_checked'] for x in rows),
                      'native_runs_started':0},indent=2))

if __name__=='__main__': main()
