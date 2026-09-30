"""Frozen 48-case native runner: 120 s compile / 60 s each, receipts never overwritten."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
from budget_task_audit_20260930 import audit_events

HERE=Path(__file__).resolve().parent
FIXTURE=HERE/'budget_task_fixture_20260930.cpp'

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def now():
    return datetime.now(timezone.utc).isoformat()

def command(argv, timeout):
    row=dict(argv=argv,timeout_seconds=timeout,started_utc=now(),exit_code=None,stdout='',stderr='',timed_out=False)
    try:
        result=subprocess.run(argv,text=True,capture_output=True,timeout=timeout)
        row.update(exit_code=result.returncode,stdout=result.stdout,stderr=result.stderr)
    except subprocess.TimeoutExpired as error:
        decode=lambda x:x.decode(errors='replace') if isinstance(x,bytes) else x or ''
        row.update(timed_out=True,stdout=decode(error.stdout),stderr=decode(error.stderr))
    except OSError as error:
        row['error']=str(error)
    row['finished_utc']=now()
    return row

def run(root, output):
    report=dict(status='failed_or_incomplete',started_utc=now(),source_root=str(root),commands=[],instances=[],
                contract_sha256=sha(HERE/'BUDGET_TASK_CONTRACT_20260930.md'),predeclared_native_cases=48,
                episodes_per_case=8,production_AUTH=False,full_paid_cost=False,concurrency=1)
    protected={p.name:sha(p) for p in HERE.iterdir() if p.is_file() and not p.name.lower().startswith('budget_task_')}
    pins=json.loads((HERE/'legal_and_sources.json').read_text())
    report.update(protected_sha256=protected,source_header_sha256=pins,
                  new_sources={p.name:dict(sha256=sha(p),source=p.read_text()) for p in
                      (FIXTURE,Path(__file__),HERE/'budget_task_audit_20260930.py')})
    with output.open('x',encoding='utf-8') as stream:
        def persist():
            stream.seek(0);json.dump(report,stream,indent=2);stream.truncate();stream.flush()
        try:
            require_sources(root,pins)
            old=(HERE/'objective_task_fixture.cpp').read_text();new=FIXTURE.read_text()
            for begin,end in [('unsigned completion_value(', 'std::string choose_probe('),
                              ('struct DeliveredDuration {','void task_comparison(')]:
                frozen=old[old.index(begin):old.index(end)]
                if new[new.index(begin):new.index(begin)+len(frozen)]!=frozen:
                    raise ValueError('frozen model/history/completion predictor changed')
            with tempfile.TemporaryDirectory(prefix='mapf_budget_task_') as directory:
                build=Path(directory)
                for rel in pins:
                    (build/Path(rel).name).write_bytes((root/rel).read_bytes())
                library=root/'third_party/flint_host_config';sdk=root/'third_party/host_sdk/usr';binary=build/'budget_task'
                argv=['rtk','proxy','g++-11','-std=c++14','-O2','-Wall','-Wextra','-Werror','-pedantic',
                      '-fno-elide-constructors','-I',str(build),'-isystem',str(sdk/'include'),'-isystem',str(library/'src'),
                      str(FIXTURE),'-L',str(library),'-L',str(sdk/'lib/x86_64-linux-gnu'),
                      f'-Wl,-rpath,{library}','-lflint','-lmpfr','-lgmp','-o',str(binary)]
                print('strict compile starting',flush=True)
                record=command(argv,120);report['commands'].append(record);persist()
                if record['exit_code']!=0: raise RuntimeError('strict compile failed')
                report['binary_sha256']=sha(binary)
                for index in range(48):
                    print(f'case {index}/47 starting',flush=True)
                    record=command(['rtk','proxy',str(binary),str(index)],60)
                    report['commands'].append(record);persist()
                    if record['exit_code']!=0: raise RuntimeError(f'native case {index} failed')
                    events=[json.loads(line) for line in record['stdout'].splitlines() if line.strip()]
                    result=audit_events(events,index);report['instances'].append(result);persist()
                    print(f'case {index}/47 passed: {result["checks"]} native checks',flush=True)
            require_sources(root,pins)
            if protected!={name:sha(HERE/name) for name in protected}: raise ValueError('protected old file changed')
            report['status']='passed'
        except Exception as error:
            report['error']=f'{type(error).__name__}: {error}'
        finally:
            report['finished_utc']=now();persist()
    print(json.dumps(dict(status=report['status'],cases=len(report['instances']),error=report.get('error'),output=str(output))),flush=True)
    return report['status']=='passed'

def require_sources(root,pins):
    if len(pins)!=9:raise ValueError('expected nine source pins')
    for rel,expected in pins.items():
        if Path(rel).is_absolute() or '..' in Path(rel).parts or sha(root/rel)!=expected:
            raise ValueError(f'source pin differs: {rel}')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--source-root',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    raise SystemExit(0 if run(args.source_root.resolve(),args.output.resolve()) else 1)
