from pathlib import Path
import hashlib
import json
import subprocess
import time

P=Path(__file__).resolve().parent
RAW=Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence/gses_fixed_path_20261003_r10')
V=RAW/'archive_rebuild/STPG'
pins=json.loads((P/'SOURCE_BINDINGS_01.json').read_text())
assert all(hashlib.sha256((V/k).read_bytes()).hexdigest()==v['sha256'] for k,v in pins['files'].items())
sources=['src/Algorithm/Astar.cpp','src/Algorithm/graph_algo.cpp','src/Algorithm/heuristic.cpp',
         'src/graph/graph.cpp','src/graph/generate_graph.cpp','src/util/Timer.cpp']
command=['rtk','proxy','g++','-std=c++17','-O3','-DNDEBUG','-I'+str(V/'inc'),str(P/'probe_duration_contract.cpp')]+[str(V/s) for s in sources]+['-o',str(RAW/'probe_duration_contract')]
folder=P/'mechanical';folder.mkdir(exist_ok=False)
registration={'cases':['unit','current_delay','future_weight'],'author_source_unchanged':True,
              'inputs':{f:hashlib.sha256((P/f).read_bytes()).hexdigest() for f in ['MECHANICAL_PROTOCOL.md','probe_duration_contract.cpp','run_contract_probe.py']}}
(folder/'REGISTRATION.json').write_text(json.dumps(registration,indent=2)+'\n')
records=[]
for name,cmd in [('build',command),('run',['rtk','proxy',str(RAW/'probe_duration_contract'),str(folder/'RESULTS.json')])]:
    started=time.monotonic()
    with (folder/(name+'.stdout')).open('w') as out,(folder/(name+'.stderr')).open('w') as err:
        proc=subprocess.run(cmd,stdout=out,stderr=err,timeout=300)
    records.append({'step':name,'command':cmd,'returncode':proc.returncode,'wall_seconds':time.monotonic()-started})
    (folder/'RECEIPTS.json').write_text(json.dumps(records,indent=2)+'\n')
    assert proc.returncode==0
data=json.loads((folder/'RESULTS.json').read_text())
assert all(r['terminated'] and sum(len(p)-1 for p in r['paths'])==r['native_cost']==r['native_ticks'] for r in data)
assert [r['native_cost'] for r in data]==[2,4,2]
assert [r['weighted_path_sum'] for r in data]==[2,4,4]
print(json.dumps({'native_costs':[r['native_cost'] for r in data],'graph_weight_sums':[r['weighted_path_sum'] for r in data],'future_weights_not_executed':True}))
