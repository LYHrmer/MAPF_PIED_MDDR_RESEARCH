"""Finite-budget orchestration of the author's unchanged CMA-ES components."""
from concurrent.futures import ThreadPoolExecutor, as_completed
import importlib.metadata
import json
import pickle
import subprocess
import time
import numpy as np
from common import HERE, RAW, CMAES, UPSTREAM, MODULE, MAP, sha, write_json, load_source, evaluate

def main():
    run = HERE / 'training'
    run.mkdir(exist_ok=False)
    started = time.monotonic()
    sources = ['env_search/archives/grid_archive.py', 'env_search/emitters/opt/_cma_es.py',
               'env_search/emitters/evolution_strategy_emitter.py', 'env_search/schedulers/scheduler.py',
               'env_search/manager.py', 'env_search/traffic_mapf/config.py',
               'env_search/traffic_mapf/module.py', 'env_search/traffic_mapf/traffic_mapf_manager.py',
               'config/traffic_mapf/base.gin', 'config/traffic_mapf/sortation_small.gin']
    # Manager is in a different filename in this revision; locate explicitly.
    sources = [s if (CMAES/s).exists() else 'env_search/traffic_mapf/traffic_mapf_manager.py' for s in sources]
    missing = [s for s in sources if not (CMAES/s).exists()]
    if missing:
        raise FileNotFoundError(missing)
    freeze = {'protocol_sha256': sha(HERE/'TRAINING_PROTOCOL.md'),
              'code_sha256': {n:sha(HERE/n) for n in ['train.py','common.py','native_worker.py']},
              'official_sources': {s:sha(CMAES/s) for s in sources},
              'module_sha256':sha(MODULE), 'map_sha256':sha(MAP),
              'versions':{n:importlib.metadata.version(n) for n in ['numpy','numba','ribs','gin-config']},
              'upstream_head':subprocess.check_output(['rtk','proxy','git','-C',str(UPSTREAM),'rev-parse','HEAD'],text=True).strip(),
              'training_budget_candidates':200,'native_training_evaluations':400,
              'holdout_seeds':[930101,930103,930107]}
    write_json(run/'freeze.json', freeze)
    A = load_source('r3_archive','env_search/archives/grid_archive.py').GridArchive
    C = load_source('r3_cma','env_search/emitters/opt/_cma_es.py').CMAEvolutionStrategy
    E = load_source('r3_emitter','env_search/emitters/evolution_strategy_emitter.py').EvolutionStrategyEmitter
    S = load_source('r3_scheduler','env_search/schedulers/scheduler.py').Scheduler
    rng=np.random.default_rng(930031)
    seed_max=int(np.iinfo(np.int32).max/2)
    archive_seed=int(rng.integers(seed_max,endpoint=True))
    emitter_seeds=rng.integers(seed_max,size=5,endpoint=True)
    archive=A(solution_dim=560,dims=[15,100],ranges=[[5,20],[9,14]],seed=archive_seed,dtype=np.float32)
    emitters=[E(archive,x0=np.full(560,5.),sigma0=5,ranker='obj',es=C,
                selection_rule='mu',restart_rule='basic',bounds=[(.1,100)]*560,
                batch_size=20,seed=int(seed)) for seed in emitter_seeds]
    scheduler=S(archive,emitters)
    write_json(run/'optimizer_seeds.json',{'manager':930031,'archive':archive_seed,'emitters':emitter_seeds.tolist()})
    all_train_seeds=set()
    summaries=[]
    for generation in range(2):
        archive.new_history_gen()
        solutions, parents=scheduler.ask()
        assert solutions.shape==(100,560) and parents is None and np.isfinite(solutions).all()
        seeds=rng.integers(seed_max,size=(100,2),endpoint=True)
        all_train_seeds.update(map(int,seeds.flat))
        assert not all_train_seeds.intersection(freeze['holdout_seeds'])
        write_json(run/f'generation_{generation}_candidates.json',{
            'solutions':solutions.tolist(),'seeds':seeds.tolist(),
            'out_of_bounds_components':int(((solutions<.1)|(solutions>100)).sum()),
            'min_weight':float(solutions.min()),'max_weight':float(solutions.max())})
        results=[[None,None] for _ in range(100)]
        count=0
        with ThreadPoolExecutor(max_workers=12) as pool:
            futures={pool.submit(evaluate,f'g{generation}_c{i:03d}_r{r}',solutions[i].tolist(),int(seeds[i,r])):(i,r)
                     for i in range(100) for r in range(2)}
            for future in as_completed(futures):
                i,r=futures[future]
                results[i][r]=future.result()
                count+=1
                if count%20==0:
                    print(json.dumps({'generation':generation,'native_done':count,'elapsed_seconds':round(time.monotonic()-started,1)}),flush=True)
        objectives=np.array([np.mean([x['result']['throughput'] for x in pair]) for pair in results])
        assert np.isfinite(objectives).all()
        records=[{'candidate':i,'objective':float(objectives[i]),'replicas':[
            {k:v for k,v in row.items() if k!='result'}|{'throughput':row['result']['throughput']}
            for row in pair]} for i,pair in enumerate(results)]
        write_json(run/f'generation_{generation}_results.json',records)
        scheduler.tell(objectives,np.zeros((100,2)))
        snapshot={'generation':generation,'mean_objective':float(objectives.mean()),
                  'max_objective':float(objectives.max()),
                  'best_archive_objective':float(archive.best_elite().objective),
                  'emitters':[{'itrs':int(e._itrs),'restarts':int(e._restarts),
                               'sigma':float(e._opt.sigma),'current_eval':int(e._opt.current_eval)} for e in emitters]}
        summaries.append(snapshot)
        write_json(run/f'generation_{generation}_after_tell.json',snapshot)
        (RAW/f'optimizer_after_g{generation}.pickle').write_bytes(pickle.dumps(scheduler))
        print(json.dumps(snapshot),flush=True)
    elite=archive.best_elite()
    selected={'trained':True,'training_scope':'finite_budget_official_components',
              'full_author_R0':False,'parameters':elite.solution.tolist(),
              'selected_training_objective':float(elite.objective),
              'training_candidates':200,'training_native_runs':400,
              'protocol_sha256':freeze['protocol_sha256']}
    write_json(run/'trained_checkpoint.json',selected)
    selected_sha=sha(run/'trained_checkpoint.json')
    holdout=[]
    with ThreadPoolExecutor(max_workers=6) as pool:
        futures={pool.submit(evaluate,f'holdout_{label}_{seed}',weights,seed,save_trace=True):(label,seed)
                 for label,weights in [('initial',[5.]*560),('trained',selected['parameters'])]
                 for seed in freeze['holdout_seeds']}
        for future in as_completed(futures):
            label,seed=futures[future]
            row=future.result()
            holdout.append({'policy':label,'seed':seed,'throughput':row['result']['throughput'],
                            'raw_label':row['label'],'job_sha256':row['job_sha256'],
                            'result_sha256':row['result_sha256'],'wall_seconds':row['wall_seconds']})
    holdout.sort(key=lambda x:(x['seed'],x['policy']))
    write_json(run/'holdout.json',holdout)
    means={label:float(np.mean([r['throughput'] for r in holdout if r['policy']==label]))
           for label in ['initial','trained']}
    write_json(run/'summary.json',{'completed':True,'generations':summaries,
        'trained_checkpoint_sha256':selected_sha,'holdout_means':means,
        'holdout_difference':means['trained']-means['initial'],
        'wall_seconds':time.monotonic()-started,'full_author_R0':False,
        'our_error_learning_method':False,'statistical_significance_claim':False})
    print(json.dumps({'completed':True,'holdout_means':means}),flush=True)

if __name__=='__main__':
    main()
