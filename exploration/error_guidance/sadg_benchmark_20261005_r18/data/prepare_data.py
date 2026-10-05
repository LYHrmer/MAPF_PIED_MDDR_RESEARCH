"""Prepare frozen official inputs. Does not invoke any path solver."""
from pathlib import Path
import datetime as dt
import hashlib
import io
import json
import shutil
import subprocess
import urllib.request
import zipfile
import yaml

ROOT = Path(__file__).resolve().parent
AUTHOR = Path('/home/lyh/.cache/mapf_research/sadg-controller-c2626d9')
LIB = AUTHOR/'third_party/libmultirobotplanning/external/libMultiRobotPlanning'
BIN = Path('/home/lyh/.cache/mapf_research/sadg-ecbs-build/ecbs')
MAPS = ['random-32-32-10', 'maze-32-32-2', 'warehouse-10-20-10-2-1']
BASE = 'https://movingai.com/benchmarks/mapf/'

def now(): return dt.datetime.now(dt.timezone.utc).isoformat()
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p, v): Path(p).write_text(json.dumps(v, indent=2, sort_keys=True)+'\n')
def git(p,*args): return subprocess.check_output(['rtk','proxy','git',*args],cwd=p,text=True).strip()

def main():
    ROOT.mkdir(parents=True,exist_ok=True)
    assert not any((ROOT/'cases').glob('*/receipt.json')), 'solver attempts already exist: prepared inputs are frozen'
    cases = [dict(case_id=f'{m}__s{s:02d}__n{n:02d}',map_name=m,scenario_id=s,
                  split='train' if s<3 else 'calibration' if s==3 else 'test',num_agents=n)
             for m in MAPS for s in range(1,6) for n in (8,16,32)]
    registration = dict(registered_utc=now(),cases=cases,
        selection='three fixed official map families; random scenario IDs 1..5; first N rows, unchanged order',
        scenario_id_note='official file index, not a rerun random seed',
        planner=dict(executable=str(BIN),sha256=sha(BIN),suboptimality=1.5,
                     wall_timeout_seconds=30,workers=1,goal_hold=True,address_space_bytes=4*1024**3),
        no_outcome_selection=True,no_replacement=True,no_retry=True,
        r16_difference='R16 fixture used w=1.0; all R18 instances use uniform w=1.5 before any solving',
        rationale='share a bounded-suboptimal author-produced initial schedule across all execution arms; do not make optimal initial MAPF the comparison bottleneck',
        limits_note='30-second wall cap includes wrapper startup; 4-GiB address cap bounds resource use and any failure is retained',
        output_api='cases/<case_id>/plan.json; status valid/timeout/planner_failure/invalid; solution=null for failure',
        coordinate_convention='MovingAI x=column,y=row; author plan parser maps to world (2*y,-2*x), an isometry',
        existing_reuse_audit=dict(
            r16='official fixture has four agents on a different input; not identical',
            gses='published PBS paths use random60/warehouse110/Paris120/lak41 and a different planner; not identical',
            previous_continuous='same random map/scenario files exist; trajectories use a different controller/planner and are not author ECBS paths',
            solver_reuse_count=0))
    if (ROOT/'REGISTERED_MATRIX.json').exists():
        original=json.loads((ROOT/'REGISTERED_MATRIX.json').read_text())
        assert original['cases']==cases and original['planner']==registration['planner']
        registration=original  # Retrieval retries may resume, but registration is never rewritten.
    else:
        dump(ROOT/'REGISTERED_MATRIX.json',registration)
    print('REGISTERED',len(cases),sha(ROOT/'REGISTERED_MATRIX.json'),flush=True)

    planner_dir=ROOT/'planner';planner_dir.mkdir(exist_ok=True)
    pins={}
    for name,folder,expected in [('sadg_controller',AUTHOR,'c2626d996121a9d6c128844a167b917db24418ac'),
                                 ('libMultiRobotPlanning',LIB,'4c75fa20c435c440d8b6bd6dc81668ddc7296ba0')]:
        assert git(folder,'rev-parse','HEAD')==expected
        assert not git(folder,'status','--porcelain'), 'author checkout modified'
        tracked=git(folder,'ls-files').splitlines()
        files={f:sha(folder/f) for f in tracked if (folder/f).is_file()}
        archive=planner_dir/(name+'.tar')
        with archive.open('wb') as out:
            subprocess.run(['rtk','proxy','git','archive','HEAD'],cwd=folder,stdout=out,check=True)
        pins[name]=dict(source_path=str(folder),upstream=git(folder,'remote','get-url','origin'),
            commit=expected,tracked_status='',tracked_file_sha256=files,archive_sha256=sha(archive))
    shutil.copy2(BIN,planner_dir/'ecbs')
    pins['binary']=dict(original_path=str(BIN),local_path=str(planner_dir/'ecbs'),sha256=sha(BIN),
                        rebuilt=False,unmodified=True)
    pins['registered_matrix_sha256']=sha(ROOT/'REGISTERED_MATRIX.json')
    pins['created_utc']=now()
    dump(ROOT/'AUTHOR_PIN.json',pins)

    downloads=ROOT/'downloads';downloads.mkdir(exist_ok=True)
    sources=ROOT/'sources';sources.mkdir(exist_ok=True)
    receipts=json.loads((ROOT/'DOWNLOAD_RECEIPTS.json').read_text()) if (ROOT/'DOWNLOAD_RECEIPTS.json').exists() else []
    for filename in ['index.html']+[m+s for m in MAPS for s in ('.map.zip','.map-scen-random.zip')]:
        url=BASE+filename
        existing=next((r for r in receipts if r['url']==url),None)
        if existing:
            assert sha(ROOT/existing['path'])==existing['sha256']
            for item in existing.get('extracted',[]):assert sha(ROOT/item['path'])==item['sha256']
            print('REUSE_FETCH',filename,flush=True)
            continue
        started=now()
        with urllib.request.urlopen(url,timeout=45) as response:
            payload=response.read();meta=dict(url=url,final_url=response.url,status=response.status,
                headers=dict(response.headers),started_utc=started,completed_utc=now())
        dest=downloads/filename;dest.write_bytes(payload)
        meta.update(path=str(dest.relative_to(ROOT)),sha256=sha(dest),bytes=len(payload))
        receipts.append(meta);dump(ROOT/'DOWNLOAD_RECEIPTS.json',receipts)
        if filename.endswith('.zip'):
            z=zipfile.ZipFile(io.BytesIO(payload))
            for member in z.namelist():
                basename=Path(member).name
                if basename in [m+'.map' for m in MAPS] or basename in [f'{m}-random-{s}.scen' for m in MAPS for s in range(1,6)]:
                    out=sources/basename;out.write_bytes(z.read(member))
                    meta.setdefault('extracted',[]).append(dict(member=member,path=str(out.relative_to(ROOT)),sha256=sha(out)))
            dump(ROOT/'DOWNLOAD_RECEIPTS.json',receipts)
        print('FETCHED',filename,len(payload),flush=True)

    inputs=[]
    for c in cases:
        m=c['map_name'];mp=sources/(m+'.map');sc=sources/f'{m}-random-{c["scenario_id"]}.scen'
        lines=mp.read_text().splitlines();height=int(lines[1].split()[1]);width=int(lines[2].split()[1]);grid=lines[4:]
        assert lines[0]=='type octile' and lines[3]=='map' and len(grid)==height and all(len(r)==width for r in grid)
        assert set(''.join(grid)) <= set('.@TGSOW'), 'unexpected MovingAI terrain'
        # Selected official maps use . floor, @ out-of-bounds, and T tree obstacles.
        assert set(''.join(grid)) <= set('.@T'), set(''.join(grid))
        obstacles=[[x,y] for y,row in enumerate(grid) for x,ch in enumerate(row) if ch!='.']
        scenlines=sc.read_text().splitlines();assert scenlines[0]=='version 1'
        rows=[line.split() for line in scenlines[1:] if line.strip()]
        agents=[]
        for i,row in enumerate(rows[:c['num_agents']]):
            assert row[1]==m+'.map' and int(row[2])==width and int(row[3])==height
            sx,sy,gx,gy=map(int,row[4:8]);assert grid[sy][sx]=='.' and grid[gy][gx]=='.'
            agents.append(dict(name=f'agent{i}',start=[sx,sy],goal=[gx,gy]))
        assert len(agents)==c['num_agents']
        assert len({tuple(a['start']) for a in agents})==len(agents)
        assert len({tuple(a['goal']) for a in agents})==len(agents)
        folder=ROOT/'cases'/c['case_id'];folder.mkdir(parents=True,exist_ok=True)
        inp=dict(map=dict(dimensions=[width,height],obstacles=obstacles),agents=agents)
        (folder/'input.yaml').write_text(yaml.safe_dump(inp,sort_keys=False))
        info={**c,'width':width,'height':height,'free_cells':width*height-len(obstacles),
              'map_path':str(mp.relative_to(ROOT)),'map_sha256':sha(mp),
              'scenario_path':str(sc.relative_to(ROOT)),'scenario_sha256':sha(sc),
              'scenario_rows_1_based':list(range(1,c['num_agents']+1)),
              'ecbs_input_path':str((folder/'input.yaml').relative_to(ROOT)),
              'ecbs_input_sha256':sha(folder/'input.yaml'),
              'official_map_url':BASE+m+'.map.zip','official_scenario_url':BASE+m+'.map-scen-random.zip',
              'agents':agents}
        dump(folder/'INPUT_PROVENANCE.json',info);inputs.append(info)
    # Hash-match reusable local copies to the official download, without trusting old provenance.
    legacy=[Path('/home/lyh/MAPF_LMAPF_ERROR_GUIDANCE_EXPLORE/exploration/error_guidance/published_continuous_execution_20261001_r6/inputs/random-32-32-10'),
            Path('/home/lyh/MAPF_PIED_MDDR_LEARNING_EXPLORE/exploration/learned_query/late_budget_choice_20261004_r13/inputs')]
    reuse=[]
    for folder in legacy:
        for p in folder.glob('random-32-32-10*'):
            if p.is_file() and (sources/p.name).exists():
                reuse.append(dict(existing_path=str(p),new_path=str(sources/p.name),sha256=sha(p),official_exact_match=sha(p)==sha(sources/p.name)))
    dump(ROOT/'LOCAL_INPUT_REUSE_AUDIT.json',reuse)
    dump(ROOT/'INPUT_MANIFEST.json',dict(created_utc=now(),registration_sha256=sha(ROOT/'REGISTERED_MATRIX.json'),cases=inputs))
    print('READY',len(inputs),flush=True)

if __name__=='__main__': main()
