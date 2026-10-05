"""Register and extract R20 fresh official scenarios using verified existing downloads."""
from pathlib import Path
import datetime as dt
import hashlib
import json
import os
import shutil
import zipfile
import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE / 'data'
OLD = HERE.parent / 'sadg_benchmark_20261005_r18/data'
MAPS = ['random-32-32-10', 'maze-32-32-2', 'warehouse-10-20-10-2-1']

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p, obj):
    p = Path(p); p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2, sort_keys=True)+'\n')

def main():
    ROOT.mkdir(parents=True, exist_ok=True)
    assert not (ROOT/'REGISTERED_MATRIX.json').exists(), 'preparation already registered; do not overwrite'
    oldreg = json.loads((OLD/'REGISTERED_MATRIX.json').read_text())
    cases = [dict(case_id=f'{m}__s{s:02d}__n{n:02d}', map_name=m,
        scenario_id=s, num_agents=n, split='test',
        stratum='core')
        for m in MAPS for s in (8,9) for n in (32,)]
    reg = dict(registered_utc=dt.datetime.now(dt.timezone.utc).isoformat(), cases=cases,
        planner=oldreg['planner'], no_retry=True, no_replacement=True,
        selection='Official map scenario files 8/9; first32 rows unchanged',
        old_registration_sha256=sha(OLD/'REGISTERED_MATRIX.json'),
        decision_sha256=sha(HERE/'THREE_ROUTE_DECISION.md'))
    dump(ROOT/'REGISTERED_MATRIX.json', reg)  # Before extraction/planning, immutable.
    (ROOT/'planner').mkdir(exist_ok=True)
    binary = ROOT/'planner/ecbs'
    binary.symlink_to(os.path.relpath(OLD/'planner/ecbs', binary.parent))
    assert sha(binary)==reg['planner']['sha256']
    dump(ROOT/'AUTHOR_PIN.json', dict(parent_path=str(OLD/'AUTHOR_PIN.json'),
        parent_sha256=sha(OLD/'AUTHOR_PIN.json'),
        author_commit='c2626d996121a9d6c128844a167b917db24418ac',
        ecbs_commit='4c75fa20c435c440d8b6bd6dc81668ddc7296ba0',
        binary_sha256=sha(binary), unchanged_binary=True,
        registration_sha256=sha(ROOT/'REGISTERED_MATRIX.json')))
    receipts=json.loads((OLD/'DOWNLOAD_RECEIPTS.json').read_text())
    sources=ROOT/'sources'; sources.mkdir(exist_ok=True)
    extraction=[]
    for m in MAPS:
        for suffix in ('.map.zip', '.map-scen-random.zip'):
            archive=OLD/'downloads'/(m+suffix)
            receipt=next(r for r in receipts if r['path']=='downloads/'+archive.name)
            assert sha(archive)==receipt['sha256']
            with zipfile.ZipFile(archive) as z:
                for member in z.namelist():
                    name=Path(member).name
                    if name not in [m+'.map',f'{m}-random-8.scen',f'{m}-random-9.scen']: continue
                    target=sources/name; target.write_bytes(z.read(member))
                    extraction.append(dict(path=str(target.relative_to(ROOT)),sha256=sha(target),
                        source_archive=str(archive),archive_sha256=sha(archive),member=member,
                        original_receipt=receipt))
    dump(ROOT/'EXTRACTION_RECEIPTS.json',extraction)
    inputs=[]
    for c in cases:
        m=c['map_name']; mp=sources/(m+'.map'); sc=sources/f'{m}-random-{c["scenario_id"]}.scen'
        lines=mp.read_text().splitlines(); h=int(lines[1].split()[1]); w=int(lines[2].split()[1]); grid=lines[4:]
        assert lines[0]=='type octile' and lines[3]=='map' and len(grid)==h
        assert all(len(row)==w for row in grid) and set(''.join(grid))<=set('.@T')
        obstacles=[[x,y] for y,row in enumerate(grid) for x,v in enumerate(row) if v!='.']
        rows=[line.split() for line in sc.read_text().splitlines()[1:] if line.strip()]
        agents=[]
        for i,row in enumerate(rows[:c['num_agents']]):
            assert row[1]==m+'.map' and int(row[2])==w and int(row[3])==h
            sx,sy,gx,gy=map(int,row[4:8]); assert grid[sy][sx]=='.' and grid[gy][gx]=='.'
            agents.append(dict(name=f'agent{i}',start=[sx,sy],goal=[gx,gy]))
        assert len(agents)==c['num_agents']
        assert len({tuple(a['start']) for a in agents})==len(agents)
        assert len({tuple(a['goal']) for a in agents})==len(agents)
        folder=ROOT/'cases'/c['case_id']; folder.mkdir(parents=True)
        (folder/'input.yaml').write_text(yaml.safe_dump(dict(map=dict(dimensions=[w,h],obstacles=obstacles),agents=agents),sort_keys=False))
        info=dict(**c,width=w,height=h,free_cells=w*h-len(obstacles),
            map_path=str(mp.relative_to(ROOT)),map_sha256=sha(mp),
            scenario_path=str(sc.relative_to(ROOT)),scenario_sha256=sha(sc),
            scenario_rows_1_based=list(range(1,c['num_agents']+1)),
            ecbs_input_path=str((folder/'input.yaml').relative_to(ROOT)),ecbs_input_sha256=sha(folder/'input.yaml'),
            official_map_url='https://movingai.com/benchmarks/mapf/'+m+'.map.zip',
            official_scenario_url='https://movingai.com/benchmarks/mapf/'+m+'.map-scen-random.zip',agents=agents)
        dump(folder/'INPUT_PROVENANCE.json',info); inputs.append(info)
    dump(ROOT/'INPUT_MANIFEST.json',dict(cases=inputs,registration_sha256=sha(ROOT/'REGISTERED_MATRIX.json')))
    shutil.copy2(OLD/'validate_paths.py',ROOT/'validate_paths.py')
    runner=(OLD/'run_paths.py').read_text().replace('registered_count=45','registered_count=6')
    (ROOT/'run_paths.py').write_text(runner)
    dump(ROOT/'PREPARATION_RECEIPT.json',dict(script_sha256=sha(__file__),
        inherited_runner_sha256=sha(OLD/'run_paths.py'),runner_sha256=sha(ROOT/'run_paths.py'),
        inherited_checker_sha256=sha(ROOT/'validate_paths.py'), new_case_count=len(cases),
        network_fetches=0, previous_science_repeated=0))
    print(json.dumps(dict(registered=len(cases),registration_sha256=sha(ROOT/'REGISTERED_MATRIX.json'))))

if __name__=='__main__': main()
