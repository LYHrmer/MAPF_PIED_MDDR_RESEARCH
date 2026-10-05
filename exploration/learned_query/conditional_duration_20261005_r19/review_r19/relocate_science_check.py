"""Run the CLI on a dependency-only relocated copy of one scientific receipt."""
import sys
sys.dont_write_bytecode=True
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
from audit_episode import ROOT,BUNDLE

HERE=Path(__file__).resolve().parent
relative=Path('random-32-32-10__s06__n16__stable/learned_no_query')
proof=json.loads((HERE/'episodes'/relative.parent/(relative.name+'.json')).read_text())
oldrepo=ROOT.parents[2];oldauthor=Path('/home/lyh/.cache/mapf_research/sadg-controller-c2626d9')
with tempfile.TemporaryDirectory(prefix='r19-science-relocation-') as directory:
    temp=Path(directory);repo=temp/'repo';root=repo/ROOT.relative_to(oldrepo)
    store=temp/'cas';bundle=root/'model';review=root/'review'
    mappings={str(ROOT/'evidence_store'):store,str(HERE):review,str(BUNDLE):bundle,
              str(oldauthor):temp/'author',str(oldrepo):repo}
    def translate(original):
        for prefix,destination in sorted(mappings.items(),key=lambda x:-len(x[0])):
            try:return destination/original.relative_to(prefix)
            except ValueError:pass
        raise ValueError('Unmapped dependency '+str(original))
    paths={Path(p) for p in proof['dependencies']}
    paths.update({ROOT/'episodes'/relative/'episode.json',HERE/'audit_episode.py',HERE/'physical_math.py',HERE/'BASE_PROVENANCE.json'})
    for original in paths:
        destination=translate(original);destination.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(original,destination)
    output=temp/'audit.json'
    command=['rtk','proxy','python3',str(review/'audit_episode.py'),'--episode',str(root/'episodes'/relative/'episode.json'),
        '--root',str(root),'--store',str(store),'--bundle',str(bundle),
        '--path-map',str(oldrepo)+'='+str(repo),'--path-map',str(oldauthor)+'='+str(temp/'author'),
        '--path-map',str(BUNDLE)+'='+str(bundle),'--output',str(output)]
    completed=subprocess.run(command,text=True,capture_output=True)
    report=json.loads(output.read_text())
    assert completed.returncode==0 and report['passed'],(completed.stderr,report['errors'])
    result=dict(passed=True,checks=report['checks'],episode_sha256=report['episode_sha256'],
        copied_dependency_files=len(paths),new_solver_calls=0,new_scientific_episodes=0,
        relocated=['review code','scientific root','CAS store','model bundle','R18/R16 source references','author source checkout'],
        receipt_content_unchanged=True,cli_executed=True,
        command_with_ephemeral_paths=command,
        minimum_bundle_files=['MODEL.json','predictor.py','MODEL_FREEZE.json'],
        optional_bundle_schema='PUBLIC_SCHEMA.json is documentation; the root R19 query PUBLIC_SCHEMA.json remains a source-pinned dependency.')
(HERE/'SCIENCE_RELOCATION_CHECK.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='command_with_ephemeral_paths'}))
