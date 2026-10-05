#!/usr/bin/env python3
"""Audit finished R18 logs and TRAIN value/model evidence without engine imports.

Only TRAIN receipts are read by default. --splits CAL TEST requires an existing
frozen-model receipt, and verifies the frozen-model hash before opening episodes.
No experiment, solver, callback, fitting code from the study is imported.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import sys
sys.dont_write_bytecode=True
from audit_episode import Auditor, canon, close, feature_vector, score, read


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def evidence_fingerprint(root, episode, receipt, raw, memo):
    """Bind cached verification to external graphs/models/code, not just JSON.

    Completed receipts make these inputs immutable by contract. File hashes are
    nevertheless recomputed once per file per invocation; stat changes invalidate
    that invocation's memo. Missing dependencies change the fingerprint too.
    """
    paths={episode,episode.parent/'RUN_RECEIPT.json',root/receipt['spec']['case']['case_path'],root/'EXPERIMENT_REGISTRATION.json'}
    paths.update(root/name for name in receipt['spec']['source_pins'])
    paths.update(Path(name) for name in raw.get('source_hashes',{}) if name.startswith('/'))
    if receipt['spec']['arm']=='learned_query':paths.update([root/'MODEL_FROZEN.json',root/'MODEL_FREEZE_RECEIPT.json'])
    for s in raw.get('solves',[]):
        base=episode.parent/'solves'/f"{s['gate_index']:05d}"
        paths.update(base/name for name in ('receipt.json','before.json','after.json'))
        local=base/'model.json.gz'
        if local.exists():paths.add(local)
        for key in ('cache_source','cached_model_file'):
            if s.get(key):paths.add(Path(s[key]))
    hashed={}
    for path in sorted(paths):
        if not path.is_file():hashed[str(path)]=None;continue
        stat=path.stat();key=(str(path),stat.st_size,stat.st_mtime_ns)
        if key not in memo:memo[key]=sha(path)
        hashed[str(path)]=memo[key]
    return canon(hashed),len(hashed)


def save(path, obj):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    Path(path).write_text(json.dumps(obj,indent=2,sort_keys=True,allow_nan=False)+'\n')


def physical_prefix(e, t):
    result=[]
    for s in e['segments']:
        if s['t0']>=t:continue
        row=dict(s)
        if s['t1']>t:
            fraction=(t-s['t0'])/(s['t1']-s['t0'])
            row['p1']=[a+fraction*(b-a) for a,b in zip(s['p0'],s['p1'])];row['t1']=t
        result.append(row)
    return result


def prefix(e, g):
    gate=next(x for x in e['gates'] if x['gate_index']==g);t=gate['capture_time']
    return {'events':[x for x in e['events'] if x['time']<=t],
        'gates':[x for x in e['gates'] if x['gate_index']<g],
        'snapshot':gate['public_snapshot'],'segments':physical_prefix(e,t),
        'prior_queries':[x for x in e['queries'] if x['captured']<t]}


def deep_close(a,b):
    if isinstance(a,dict) and isinstance(b,dict):return set(a)==set(b) and all(deep_close(a[k],b[k]) for k in a)
    if isinstance(a,list) and isinstance(b,list):return len(a)==len(b) and all(deep_close(x,y) for x,y in zip(a,b))
    if isinstance(a,(float,int)) and isinstance(b,(float,int)):return close(a,b,1e-9)
    return a==b


def audit_learning(root):
    errors=[];checks=0;stats={}
    def check(ok,name,detail=None):
        nonlocal checks
        checks+=1
        if not ok:errors.append({'check':name,'detail':detail})
    pairs_path=root/'training/PAIRS.json';labels_path=root/'training/LABELS.json'
    if not pairs_path.exists():return {'passed':True,'checks':0,'errors':[],'status':'not_yet_collected'}
    # Collection snapshots are atomic but may advance independently. A label's
    # parent pair must be present; trailing unlabelled pairs are legal in progress.
    labels=read(labels_path);pairs=read(pairs_path);evidence={p['pair_id']:p for p in pairs}
    check(len(evidence)==len(pairs),'unique_pair_ids')
    check(len({r['pair_id'] for r in labels})==len(labels),'unique_training_rows')
    cases={x['case_id']:x for x in read(root/'EXPERIMENT_REGISTRATION.json')['cases']}
    labels_by_id={r['pair_id']:r for r in labels}
    for p in pairs:
        pid=p['pair_id'];g=p['gate_index']
        a_path=root/p['noquery_episode'];b_path=root/p['query_episode'];a=read(a_path);b=read(b_path)
        check([sha(a_path),sha(b_path)]==p['episode_sha256'],'pair_raw_hash:'+pid)
        check(g in (1,3) and p['split']=='TRAIN','registered_training_gate_split:'+pid)
        check(a['benchmark']['split']==b['benchmark']['split']=='TRAIN','raw_split:'+pid)
        check(a['benchmark']['family']==b['benchmark']['family']==p['family'],'group_identity:'+pid)
        check(a['case_id']==b['case_id'],'matched_case:'+pid)
        c=cases[a['case_id']]
        check(c['family']==p['family'] and c['split']=='TRAIN','registered_family:'+pid)
        check(a['geometry_binding']==b['geometry_binding'] and a['initial_graph']==b['initial_graph'],'same_input_graph:'+pid)
        check(a['private_truth']['seed']==b['private_truth']['seed'] and a['private_truth']['disturbance']==b['private_truth']['disturbance'],'same_private_world:'+pid)
        for key in set(a['private_truth']['action_profiles'])&set(b['private_truth']['action_profiles']):
            check(a['private_truth']['action_profiles'][key]==b['private_truth']['action_profiles'][key],'same_occurrence_disturbance:'+pid)
        config_a={k:v for k,v in a['config'].items() if k!='output_dir'};config_b={k:v for k,v in b['config'].items() if k!='output_dir'}
        check(config_a==config_b,'same_budget_clock_horizon:'+pid)
        check(deep_close(prefix(a,g),prefix(b,g)),'complete_physical_public_prefix:'+pid)
        ga=next(x for x in a['gates'] if x['gate_index']==g);gb=next(x for x in b['gates'] if x['gate_index']==g)
        snap=ga['public_snapshot'];check(snap==gb['public_snapshot']==p['public_snapshot'],'paired_public_snapshot:'+pid)
        candidates=[x for x in snap['agents'] if x['query_eligible']]
        target=sorted(candidates,key=(lambda x:(-score(x),x['agent_id'])) if g==1 else (lambda x:(-x['downstream_nominal'],x['agent_id'])))[0]
        check(target['agent_id']==p['target_agent'],'preregistered_target:'+pid)
        check(ga['selected']==[] and gb['selected']==[p['target_agent']],'actual_intervention:'+pid)
        check(a['benchmark']['arm']==b['benchmark']['arm']=='history_rule','same_history_continuation:'+pid)
        check(set(map(int,a['benchmark']['probe']))<={g} and set(map(int,b['benchmark']['probe']))<={g},'single_probe_only:'+pid)
        check(p['query_count_difference']==b['query_count']-a['query_count'],'complete_query_difference:'+pid)
        check(p['completed_difference']==b['completed_agents']-a['completed_agents'],'complete_tasks_difference:'+pid)
        legal=all(x['status'] in ('completed','truncated') and x['collision_audit']['passed'] for x in (a,b))
        check(legal==p['eligible_label'],'label_legality:'+pid)
        if pid in labels_by_id:
            row=labels_by_id[pid]
            check(legal and row['split']=='TRAIN' and row['family']==p['family'],'row_legal_TRAIN:'+pid)
            check(canon(p)==row['pair_evidence_sha256'],'row_parent_evidence_hash:'+pid)
            expected=feature_vector(snap,target)
            check(all(close(x,y,1e-12) for x,y in zip(expected,row['features'])) and len(row['features'])==22,'independent_22_features:'+pid)
            check(close(row['value'],a['restricted_sum_completion']-b['restricted_sum_completion'],1e-12),'full_episode_value:'+pid)
    stats.update(pairs=len(pairs),labels=len(labels),families=len({r['family'] for r in labels}))
    model_path=root/'MODEL_FROZEN.json'
    if model_path.exists():
        import numpy as np
        final=read(model_path);selection=read(root/'training/GROUPED_MODEL_SELECTION.json')
        complete=read(root/'training/COLLECTION_COMPLETE.json')
        check(complete['labels_sha256']==canon(labels),'collection_labels_frozen')
        check(complete['pairs_sha256']==canon(pairs),'collection_pairs_frozen')
        check(final['rows_sha256']==canon(labels),'model_rows_frozen')
        check(final['query_threshold']==1e-8,'threshold_preregistered')
        families=sorted({r['family'] for r in labels});check(selection['families']==families,'selection_family_set')
        def verify_fit(model,rows,tag):
            xx=np.array([r['features'] for r in rows]);yy=np.array([r['value'] for r in rows]);nn=len(rows)
            counts={f:sum(r['family']==f for r in rows) for f in {r['family'] for r in rows}}
            weights=np.array([1/counts[r['family']] for r in rows]);weights*=nn/sum(weights)
            mu=(xx*weights[:,None]).sum(axis=0)/sum(weights)
            std=np.sqrt(((xx-mu)**2*weights[:,None]).sum(axis=0)/sum(weights));std[std<1e-10]=1
            check(np.allclose(mu,model['mean'],rtol=1e-11,atol=1e-11),tag+':fold_only_mean')
            check(np.allclose(std,model['scale'],rtol=1e-11,atol=1e-11),tag+':fold_only_scale')
            check(model['fitted_families']==sorted(counts) and model['fitted_rows']==nn,tag+':fit_membership')
            design=np.column_stack([np.ones(nn),(xx-mu)/std]);beta=np.array([model['intercept']]+model['coef'])
            grad=design.T@(weights*(design@beta-yy));grad[1:]+=model['alpha']*beta[1:]
            residual=float(np.max(np.abs(grad)))
            check(residual<1e-6,tag+':independent_normal_equation',residual)
            return residual
        residuals=[verify_fit(final,labels,'final')];scores=[]
        check([x['alpha'] for x in selection['candidates']]==[1.,10.,100.],'registered_alpha_grid')
        for candidate in selection['candidates']:
            check(sorted(f['held_family'] for f in candidate['folds'])==families,'each_family_once')
            mses=[]
            for fold in candidate['folds']:
                held=fold['held_family'];train=[r for r in labels if r['family']!=held];test=[r for r in labels if r['family']==held]
                check(held not in fold['trained_families'] and set(fold['trained_families'])==set(families)-{held},'family_isolation:'+held)
                check(fold['pair_ids']==[r['pair_id'] for r in test],'fold_membership:'+held)
                m=fold['model'];check(m['alpha']==candidate['alpha'],'fold_alpha')
                residuals.append(verify_fit(m,train,f'fold:{held}:{m["alpha"]}'))
                pred=m['intercept']+((np.array([r['features'] for r in test])-m['mean'])/m['scale'])@np.array(m['coef'])
                check(np.allclose(pred,fold['predictions'],rtol=1e-10,atol=1e-10),'fold_predictions')
                mse=float(np.mean((pred-np.array([r['value'] for r in test]))**2));mses.append(mse)
                check(close(mse,fold['mse'],1e-10),'fold_MSE')
            mean=sum(mses)/len(mses);check(close(mean,candidate['family_mean_mse'],1e-10),'family_mean_MSE');scores.append((mean,candidate['alpha']))
        selected=min(scores)[1];check(final['alpha']==selection['selected_alpha']==selected,'TRAIN_only_alpha_selection')
        stats.update(model_fits_verified=len(residuals),max_normal_equation_residual=max(residuals),selected_alpha=selected)
    return {'passed':not errors,'checks':checks,'errors':errors,'stats':stats,'engine_or_policy_imported':False,'new_scientific_episodes':0}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parent.parent)
    parser.add_argument('--splits',nargs='+',choices=['TRAIN','CAL','TEST'],default=['TRAIN'])
    parser.add_argument('--learning-only',action='store_true');args=parser.parse_args();root=args.root
    if any(s!='TRAIN' for s in args.splits):
        frozen=read(root/'MODEL_FREEZE_RECEIPT.json')
        assert frozen['model_sha256']==sha(root/'MODEL_FROZEN.json'),'freeze required before accessing CAL/TEST'
    review=root/'review';reports=[];auditor_hash=sha(Path(__file__).with_name('audit_episode.py'));file_memo={}
    if not args.learning_only:
        for split in args.splits:
            for receipt_path in sorted((root/'episodes'/split).glob('*/*/RUN_RECEIPT.json')):
                receipt=read(receipt_path);spec=receipt['spec'];episode=receipt_path.parent/'episode.json'
                raw=read(episode)
                fingerprint,evidence_files=evidence_fingerprint(root,episode,receipt,raw,file_memo)
                target=review/'episodes'/split/receipt_path.parent.parent.name/(receipt_path.parent.name+'.json')
                cached=read(target) if target.exists() else None
                if cached and cached.get('auditor_sha256')==auditor_hash and cached['episode_sha256']==sha(episode) and cached.get('evidence_fingerprint')==fingerprint:result=cached
                else:
                    if raw['schema']=='r18-constructor-failure':
                        result={'passed':receipt['episode_sha256']==sha(episode) and not raw['success'],'episode':str(episode),
                            'episode_sha256':sha(episode),'checks':2,'errors':[],'recorded_status':raw['status'],'stats':{},
                            'limitation':'Constructor failure retained; no physical trajectory existed to audit.'}
                    else:
                        result=Auditor(episode,root/spec['case']['case_path'],spec['arm'],
                            root/'MODEL_FROZEN.json' if spec['arm']=='learned_query' else None).run()
                    result.update(auditor_sha256=auditor_hash,evidence_fingerprint=fingerprint,evidence_files=evidence_files);save(target,result)
                reports.append({'episode':str(episode.relative_to(root)),'audit':str(target.relative_to(root)),
                    'passed':result['passed'],'checks':result['checks'],'errors':result['errors'],'episode_sha256':result['episode_sha256']})
    learning=audit_learning(root);save(review/'LEARNING_AUDIT.json',learning)
    report={'schema':'r18-independent-completed-artifacts-v1','audited_utc':datetime.now(timezone.utc).isoformat(),
        'requested_splits':args.splits,'passed':learning['passed'] and all(r['passed'] for r in reports),
        'new_scientific_episodes':0,'engine_or_policy_imported':False,'completed_receipts_audited':len(reports),
        'checks':learning['checks']+sum(r['checks'] for r in reports),'learning':learning,'episodes':reports}
    save(review/('LEARNING_ONLY_AUDIT.json' if args.learning_only else 'COMPLETED_ARTIFACTS_AUDIT.json'),report)
    print(json.dumps({k:report[k] for k in ['passed','requested_splits','completed_receipts_audited','checks']}))
    if not report['passed']:print(json.dumps({'learning_errors':learning['errors'],'episode_errors':[r for r in reports if not r['passed']]}))
    raise SystemExit(0 if report['passed'] else 1)


if __name__=='__main__':main()
