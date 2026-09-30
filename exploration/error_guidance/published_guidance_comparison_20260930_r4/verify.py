"""Independent method/config/archive verification, without new evaluations."""
import hashlib
import json
from pathlib import Path
import tarfile

HERE=Path(__file__).resolve().parent
MAIN=Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence')
RAW=MAIN/'published_guidance_comparison_20260930_r4'
OLD=MAIN/'onlineggo_training_20260930_r3_attempt02'
R3=HERE.parent/'onlineggo_training_20260930_r3'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    f=read(HERE/'freeze.json');assert f['holdout_seeds']==[930101,930103,930107]
    for path,digest in f['pins'].items():assert sha(Path(path))==digest,path
    cfg=read(HERE/'build.json')
    original=read(MAIN/'onlineggo_neural_r0_20260930_r2/configure_01/receipt.json')['argv']
    new=cfg['configure']['argv']
    assert len(new)==len(original)
    diffs=[(a,b) for a,b in zip(original,new) if a!=b]
    assert len(diffs)==2 and diffs[0][1]==str(RAW/'build_hm') and diffs[1]==('-DOBJECTIVE=4','-DOBJECTIVE=3')
    oldflags=(MAIN/'onlineggo_neural_r0_20260930_r2/build_nn/CMakeFiles/py_driver.dir/flags.make').read_text()
    assert oldflags.replace('-DOBJECTIVE=4','-DOBJECTIVE=3')==cfg['flags']
    assert sha(next((RAW/'build_hm').glob('py_driver*.so')))==cfg['module_sha256']
    prior=read(R3/'training_02/holdout.json');newrows=read(HERE/'results.json')
    rows=[]
    for row in newrows:
        p=RAW/row['raw_label'];job=read(p/'job.json')
        match=next(r for r in prior if r['policy']=='initial' and r['seed']==row['seed'])
        oldjob=read(OLD/match['raw_label']/'job.json')
        a=dict(job['kwargs']);b=dict(oldjob['kwargs'])
        del a['save_path'];del b['save_path'];assert a==b
        assert job['config']==oldjob['config'] and job['map_sha256']==oldjob['map_sha256']
        result=read(p/'job.result.json');trace=read(p/'trace.json')
        assert row['throughput']==result['result']['throughput']==trace['numTaskFinished']/1000
        assert sha(p/'job.json')==row['job_sha256'] and sha(p/'job.result.json')==row['result_sha256']
        rec=read(RAW/(row['raw_label']+'_process')/'receipt.json')
        assert rec['returncode']==0 and not rec['timed_out']
        rows.append({'seed':row['seed'],'completed':trace['numTaskFinished'],'throughput':row['throughput']})
    assert [r['seed'] for r in rows]==f['holdout_seeds']
    manifest=read(HERE/'archive_manifest.json');archive=HERE/'native_evidence.tar.gz'
    assert sha(archive)==manifest['archive_sha256']
    with tarfile.open(archive,'r:gz') as tf:
        for row in manifest['entries']:
            data=tf.extractfile(row['path']).read()
            assert len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256']
    audit=read(HERE/'audit.json');assert audit['passed']
    assert sum(r['actions_replayed'] for r in audit['new_full_trajectory_audits'].values())==2400000
    for r in audit['task_stream_agreement']:assert r['same_starts'] and r['same_initial_task_goals']
    summary=read(HERE/'summary.json')
    for policy in ['initial','trained','hm_GPIBT']:
        mean=sum(r['throughput'] for r in prior+newrows if r['policy']==policy)/3
        assert abs(mean-summary['means'][policy])<1e-12
    out={'passed':True,'new_native_runs':rows,'only_compile_objective_and_build_directory_changed':True,
         'same_author_kwargs_except_save_path':True,'frozen_inputs_unchanged':True,
         'archive_files_verified':len(manifest['entries']),'full_trajectory_audit_actions':2400000,
         'fully_paired_future_tasks':False,'verifier_sha256':sha(Path(__file__))}
    (HERE/'independent_verification.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out))
if __name__=='__main__':main()
