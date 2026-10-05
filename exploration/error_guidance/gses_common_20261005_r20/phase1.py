#!/usr/bin/env python3
"""Four preregistered new inputs, existing original-author ELF, no source edits."""
from pathlib import Path
from datetime import datetime,timezone
from fractions import Fraction as F
import argparse,hashlib,json,subprocess,time
from fraction_oracle import enumerate_legal,objective

HERE=Path(__file__).resolve().parent
R13=HERE.parent/'gses_online_adoption_20261004_r13'
VENDOR=Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence/gses_author_preflight_20261003_r9/vendor/STPG')


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def write(path,value):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')
def now():return datetime.now(timezone.utc).isoformat()


def graph(weights,cross=1):
    paths=[[[[i-2,0],i] for i in range(5)],[[[0,i-2],i] for i in range(5)],[[[10+i,10],i] for i in range(5)]]
    edges=[[5*a+i,5*a+i+1,w] for a,row in enumerate(weights) for i,w in enumerate(row)]
    # A leaves the shared resource (state3) before B enters (state2).
    # B's final state releases C's final state; this is fixed by the author
    # last-state rule and represents a downstream dependency, not a map case.
    return dict(paths=paths,current=[0,0,0],offsets=[0,5,10],type1=edges,type2=[[3,7,cross],[9,14,1]])


def register():
    regpath=HERE/'PHASE1_REGISTRATION.json'
    if regpath.exists():raise RuntimeError('registration already exists; no overwrite')
    old=json.loads((R13/'REGISTRATION.json').read_text());binary=Path(old['binary'])
    assert sha(binary)==old['binary_sha256']
    files=json.loads((R13/'AUTHOR_SOURCE.json').read_text())['files']
    for name,value in files.items():assert sha(VENDOR/name)==value['sha256']
    rows=[
        ('p01_unit_edges_current_delay',[[5,1,1,1],[1,1,1,1],[1,1,1,1]],1,'Native unit type2 with integer current delay'),
        ('p02_future_integer_duration',[[1,4,1,1],[1,1,1,1],[1,1,1,1]],1,'Future type1 weight changes; independent graph objective, not original simulator'),
        ('p03_fractional_type1_counterexample',[[.875,.0625,.0625,.0625],[1.1875,.0625,.0625,.0625],[.125,.125,.125,.125]],1,'Binary-exact fractional current/future durations; downstream dependency may expose unit-gap test'),
        ('p04_nonunit_type2_counterexample',[[1,1,1,1],[3,1,1,1],[1,1,1,1]],8,'Integer type1 but type2 separation8; test original >=0/+1 unit semantics')]
    inputs=[]
    for name,weights,cross,purpose in rows:
        g=graph(weights,cross);spec=dict(id=name,purpose=purpose,solver_graph=g,reversible_edges=[g['type2'][0]],scope='new deterministic graph mechanism; no heldout-performance claim')
        file=HERE/'inputs'/(name+'.json');write(file,spec);inputs.append(dict(id=name,path=str(file),sha256=sha(file)))
    reg=dict(registered_utc=now(),phase=1,author_commit=old['author_commit'],binary=str(binary),binary_sha256=sha(binary),
        author_source={name:value['sha256'] for name,value in files.items()},author_source_root=str(VENDOR),
        adapter_sha256=sha(R13/'author_online.cpp'),source_pins={n:sha(HERE/n) for n in ['phase1.py','fraction_oracle.py','QUALIFICATION.md']},
        new_native_call_cap=4,method='Improved_GSES',solver_seconds=16,host_seconds=20,seed=10,
        inputs=inputs,predeclared_acceptance='Full original output graph DAG and Fraction objective equals minimum over native legal orientations; preserve all failures and mismatches',
        second_phase='At most8 additional calls only after separate input registration; no changes to old sources')
    write(regpath,reg);print('registered',sha(regpath))


def run():
    reg=json.loads((HERE/'PHASE1_REGISTRATION.json').read_text());assert sha(reg['binary'])==reg['binary_sha256']
    for name,value in reg['source_pins'].items():assert sha(HERE/name)==value
    results=[]
    for entry in reg['inputs']:
        assert sha(entry['path'])==entry['sha256'];spec=json.loads(Path(entry['path']).read_text());out=HERE/'calls'/entry['id']
        if out.exists():raise RuntimeError('refuse repeat/unfinished input '+entry['id'])
        out.mkdir(parents=True);write(out/'STARTED.json',dict(started_utc=now(),input_sha256=entry['sha256']))
        command=['rtk','proxy',reg['binary'],entry['path'],reg['method'],str(out/'author_reply.json')]
        started=time.monotonic();error=None
        try:
            completed=subprocess.run(command,capture_output=True,text=True,timeout=reg['host_seconds']);rc=completed.returncode;stdout=completed.stdout;stderr=completed.stderr
        except subprocess.TimeoutExpired as exc:
            rc=None;error='HostTimeout';stdout=exc.stdout or '';stderr=exc.stderr or ''
            if isinstance(stdout,bytes):stdout=stdout.decode(errors='replace')
            if isinstance(stderr,bytes):stderr=stderr.decode(errors='replace')
        (out/'stdout.txt').write_text(stdout);(out/'stderr.txt').write_text(stderr)
        receipt=dict(command=command,returncode=rc,error=error,elapsed_seconds=time.monotonic()-started,finished_utc=now(),input_sha256=entry['sha256'],binary_sha256=reg['binary_sha256'])
        write(out/'receipt.json',receipt)
        oracle=enumerate_legal(spec);row=dict(id=entry['id'],receipt=receipt,oracle=oracle)
        if (out/'author_reply.json').exists():
            reply=json.loads((out/'author_reply.json').read_text());g=reply['selected_graph'];check=objective(g)
            row.update(author_status=reply['status'],author_output_sha256=sha(out/'author_reply.json'),actual_graph_objective=check,
                matches_optimum=check['feasible'] and F(check['sum_completion'])==F(oracle['optimum']),
                legal_choice=any(sorted(g['type2'])==sorted(c['type2']) for c in oracle['candidates']),
                unchanged_type1=g['type1']==spec['solver_graph']['type1'],selected_type2=g['type2'])
        else:row.update(author_status=error or 'AuthorError',matches_optimum=False)
        write(out/'FRACTION_AUDIT.json',row);results.append(row)
        print(entry['id'],row['author_status'],row.get('actual_graph_objective',{}).get('sum_completion'),'oracle',oracle['optimum'],'match',row['matches_optimum'],flush=True)
    write(HERE/'PHASE1_RESULTS.json',dict(registration_sha256=sha(HERE/'PHASE1_REGISTRATION.json'),new_native_calls=len(results),results=results))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=['register','run']);a=p.parse_args()
    register() if a.command=='register' else run()
