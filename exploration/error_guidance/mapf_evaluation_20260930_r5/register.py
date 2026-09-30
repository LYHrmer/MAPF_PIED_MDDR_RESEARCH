"""Register official benchmark archives and validate graph/scenario compatibility."""
from collections import deque
from datetime import datetime, timezone
import hashlib,json,shutil,zipfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
DOWNLOAD=Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence/mapf_benchmark_materials_20260930_r5')
NAMES={'empty-32-32':1024,'random-32-32-10':922,'maze-32-32-2':666,'room-32-32-4':682}
def digest(data): return hashlib.sha256(data).hexdigest()
def components(grid):
    h,w=len(grid),len(grid[0]); labels={}; sizes=[]
    for y in range(h):
        for x in range(w):
            if grid[y][x] in '@T' or (x,y) in labels: continue
            tag=len(sizes); labels[x,y]=tag; todo=deque([(x,y)]); size=0
            while todo:
                a,b=todo.popleft(); size+=1
                for c,d in [(a+1,b),(a-1,b),(a,b+1),(a,b-1)]:
                    if 0<=c<w and 0<=d<h and grid[d][c] not in '@T' and (c,d) not in labels:
                        labels[c,d]=tag; todo.append((c,d))
            sizes.append(size)
    return labels,sizes
def main():
    assert not (HERE/'registry.json').exists(), 'Do not overwrite registered inputs'
    original=HERE/'original_archives'; original.mkdir()
    archives={}
    names=['mapf-map.zip']+[n+'.map-scen-random.zip' for n in NAMES]
    for name in names:
        p=DOWNLOAD/name; data=p.read_bytes()
        with zipfile.ZipFile(p) as z: assert z.testzip() is None
        shutil.copyfile(p,original/name)
        archives[name]={'url':'https://movingai.com/benchmarks/mapf/'+name,'sha256':digest(data),'bytes':len(data)}
    results={}
    with zipfile.ZipFile(original/'mapf-map.zip') as maps:
        for name,expected_free in NAMES.items():
            map_bytes=maps.read(name+'.map'); lines=map_bytes.decode().splitlines()
            assert lines[:4]==['type octile','height 32','width 32','map']
            grid=lines[4:]; assert len(grid)==32 and all(len(row)==32 for row in grid)
            labels,sizes=components(grid); assert sum(sizes)==expected_free
            scenarios=[]
            with zipfile.ZipFile(original/(name+'.map-scen-random.zip')) as z:
                names=[s for s in z.namelist() if s.endswith('.scen')]; assert len(names)==25
                for index in range(1,26):
                    member='scen-random/'+name+f'-random-{index}.scen'
                    content=z.read(member); rows=content.decode().splitlines(); assert rows[0]=='version 1'
                    pairs=[]
                    for raw in rows[1:]:
                        parts=raw.split(); assert len(parts)==9 and parts[1]==name+'.map'
                        assert [int(parts[2]),int(parts[3])]==[32,32]
                        sx,sy,gx,gy=map(int,parts[4:8]); start=(sx,sy); goal=(gx,gy)
                        assert start in labels and goal in labels and labels[start]==labels[goal]
                        pairs.append((start,goal))
                    assert len(pairs)>=256
                    for n in [32,64,128,256]:
                        assert len({s for s,g in pairs[:n]})==n
                        assert len({g for s,g in pairs[:n]})==n
                    scenarios.append({'scenario':index,'archive_member':member,'sha256':digest(content),
                                      'pairs':len(pairs),'all_pairs_reachable_four_connected':True,
                                      'valid_unique_start_goal_prefixes':[32,64,128,256]})
            results[name]={'map_sha256':digest(map_bytes),'width':32,'height':32,'free_cells':expected_free,
                           'connected_component_sizes':sizes,
                           'density_by_agent_count':{str(n):n/expected_free for n in [32,64,128,256]},
                           'scenario_count':25,'scenarios':scenarios}
    out={'status':'MATERIALS_VALIDATED_NOT_EXPERIMENTS_RUN','registered_utc':datetime.now(timezone.utc).isoformat(),
         'source':'https://movingai.com/benchmarks/mapf/index.html',
         'license_source':'https://movingai.com/benchmarks/','license':'Open Data Commons Attribution License',
         'maps':results,'archives':archives,'agent_counts':[32,64,128,256],
         'reserved_test_scenarios_per_map':list(range(1,26)),
         'future_training_must_exclude_these_exact_scenarios':True,
         'past_map_exposure_not_audited_no_map_generalization_claim':True,
         'material_instances_per_algorithm_and_condition':400,
         'local_four_robot_and_two_robot_pilots_are_not_standard_benchmark_results':True,
         'lifelong_followup_task_generator_still_requires_frozen_common_adapter':True,
         'verifier_sha256':digest(Path(__file__).read_bytes())}
    (HERE/'registry.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'maps':len(results),'scenarios':100,'scaling_instances':400,
                      'all_coordinate_reachability_prefix_checks_passed':True,'new_benchmark_native_runs':0}))
if __name__=='__main__':main()
