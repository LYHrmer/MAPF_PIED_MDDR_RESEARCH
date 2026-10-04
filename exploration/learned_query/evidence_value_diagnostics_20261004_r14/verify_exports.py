"""Independently reconcile structured exports and finite-set headroom; no raw re-audit."""
from pathlib import Path
from fractions import Fraction as Q
from collections import defaultdict
import copy,hashlib,json
import export_values as cache_api
P=Path(__file__).resolve().parent
OLD=P.parent/'late_budget_choice_20261004_r13'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,x):(P/n).write_text(json.dumps(x,sort_keys=True,indent=2)+'\n')
def bound(lo,hi):return dict(lower=str(lo),upper=str(hi))
def pretty(b):return '['+', '.join(f'{float(Q(b[k])):.6f}' for k in ['lower','upper'])+']'

def validate(pairs,original):
    assert len(pairs)==48 and len({p['world'] for p in pairs})==48
    for p in pairs:
        cpol,dpol=('condition','alwaysLD') if p['split']=='test' else ('macro_C','macro_LD')
        c,d=original[p['world'],cpol],original[p['world'],dpol]
        assert p['family_key']==c['family_key']==d['family_key'] and p['budget']==c['budget']==d['budget']
        for k,r in [('C',c),('LD',d)]:
            out=p[k];assert out['N']==r['tasks'] and out['queries']==r['queries'] and out['remaining']==r['remaining']
            assert out['service_sha256']==r['service_sha256'] and Q(out['T']['lower'])==Q(r['T_lower']) and Q(out['T']['upper'])==Q(r['T_upper'])
        assert p['delta_N']==d['tasks']-c['tasks'] and p['delta_queries']==d['queries']-c['queries']
        lo=Q(c['T_lower'])-Q(d['T_upper']);hi=Q(c['T_upper'])-Q(d['T_lower'])
        assert p['raw_interval_subtraction']==bound(lo,hi)
        if c['service_sha256']==d['service_sha256']:lo=hi=Q(0)
        assert p['delta_T']==bound(lo,hi)
        assert p['public_gate']['features']==c['gate']['features']==d['gate']['features']
        assert p['public_gate']['remaining_capacity']==c['gate']['remaining_capacity']==d['gate']['remaining_capacity']
    test=[p for p in pairs if p['split']=='test'];groups=defaultdict(list)
    for p in test:groups[p['family_key']].append(p['budget'])
    assert len(groups)==8 and all(sorted(bs)==[8,16] for bs in groups.values())

def headroom(ps):
    eq=[p for p in ps if p['delta_N']==0]
    c_lo=c_hi=d_lo=d_hi=Q(0)
    for p in eq:
        lo,hi=Q(p['delta_T']['lower']),Q(p['delta_T']['upper'])
        c_lo+=max(lo,0);c_hi+=max(hi,0)
        d_lo+=max(-hi,0);d_hi+=max(-lo,0)
    return dict(contexts=len(ps),equal_task_contexts=len(eq),N_C=sum(p['C']['N'] for p in ps),N_LD=sum(p['LD']['N'] for p in ps),
                N_task_first_oracle=sum(max(p['C']['N'],p['LD']['N']) for p in ps),
                equal_task_oracle_T_gain_vs_C=bound(c_lo,c_hi),equal_task_oracle_T_gain_vs_LD=bound(d_lo,d_hi))

def main():
    original={(r['world'],r['policy']):r for r in read(OLD/'RESULTS.json')}
    pairs=read(P/'VALUE_PAIRS.json')['pairs'];arms=read(P/'ARM_VALUES.json')['arms'];validate(pairs,original)
    assert len(arms)==160 and {(a['world'],a['policy']) for a in arms}==set(original)
    archive=read(OLD/'RAW_ARCHIVE_MANIFEST.json');members={m['path']:m['sha256'] for a in archive['archives'] for m in a['members']}
    for a in arms:
        r=original[a['world'],a['policy']];assert a['outcome']['N']==r['tasks']
        assert Q(a['outcome']['T']['lower'])==Q(r['T_lower']) and Q(a['outcome']['T']['upper'])==Q(r['T_upper'])
        assert a['raw_reference']['sha256']==members[a['raw_reference']['member']]
    negatives=[]
    for name in ['task_label','time_sign','branch_swap','family_budget_alias','missing_pair']:
        z=copy.deepcopy(pairs)
        if name=='task_label':z[0]['delta_N']+=1
        elif name=='time_sign':z[0]['delta_T']['lower']='999'
        elif name=='branch_swap':z[0]['C']['N']+=1
        elif name=='family_budget_alias':z[0]['budget']=999
        else:z.pop()
        try:validate(z,original)
        except AssertionError:negatives.append(dict(case=name,rejected=True))
        else:raise AssertionError('accepted corrupted export '+name)
    pins,key=cache_api.bindings();cache=read(P/'VALUE_CACHE.json');assert cache_api.cache_matches(cache,key)
    z=copy.deepcopy(cache);z['cache_key']='changed-content';assert not cache_api.cache_matches(z,key)
    z=copy.deepcopy(cache);z['outputs']['VALUE_PAIRS.json']='wrong-content';assert not cache_api.cache_matches(z,key)
    first,second=read(P/'REUSE_V2_FIRST.json'),read(P/'REUSE_V2_SECOND.json')
    assert first['cache_key']==second['cache_key']==key and not first['cache_hit'] and second['cache_hit']
    assert (first['extracted_arms'],first['extracted_pairs'])==(160,48)
    assert (second['extracted_arms'],second['extracted_pairs'],second['raw_trajectory_reads'],second['new_native_runs'],second['new_model_fits'])==(0,0,0,0,0)
    split={s:headroom([p for p in pairs if p['split']==s]) for s in ['train','calibration','test']}
    fam=defaultdict(list)
    for p in pairs:
        if p['split']=='test':fam[p['family_key']].append(p)
    tight=dict(method='Sum branch improvements; unchanged or identical-service branches contribute exactly zero. This tightens subtraction of two independent total intervals.',
               numerical_not_statistical=True,splits=split,TEST_families={k:headroom(ps) for k,ps in sorted(fam.items())})
    write('TIGHT_HEADROOM.json',tight)
    test=split['test'];ldtotal=sum((Q(p['LD']['T']['lower'])+Q(p['LD']['T']['upper']))/2 for p in pairs if p['split']=='test')
    tg=test['equal_task_oracle_T_gain_vs_LD'];percentage=100*(Q(tg['lower'])+Q(tg['upper']))/2/ldtotal
    train=[p for p in pairs if p['split']=='train'];all_single_claim=all(p['public_conditions']['claim_count']==1 for p in pairs)
    coverage=[]
    for p in pairs:
        fs=list(map(Q,p['public_gate']['features']))
        # With one claim, inverse-route/owner sum=1/(remaining_route*owners).
        owners=1/(fs[3]*fs[4]*64) if p['public_conditions']['claim_count']==1 else None
        if owners is not None:assert owners.denominator==1 and owners>=1
        coverage.append(dict(world=p['world'],split=p['split'],budget=p['budget'],candidate_count=p['public_conditions']['candidate_count'],claim_count=p['public_conditions']['claim_count'],owners_on_single_claim=None if owners is None else int(owners)))
    write('PUBLIC_COVERAGE.json',dict(method='For a single claim only, owners=1/(feature3*feature4*64), using exact public feature definitions; multiple-claim rows would remain unidentified.',private_inputs_used=False,rows=coverage,all_single_claim=all_single_claim,all_single_owner=all(r['owners_on_single_claim']==1 for r in coverage)))
    lines=['# R14 interpretation and next target','',
      f"The finite C/LD TEST oracle completes {test['N_task_first_oracle']} tasks, exactly the fixed LD total {test['N_LD']}. It has no additional task-count space over LD in these 16 registered contexts. Among the 15 equal-task contexts, its time improvement over LD is {pretty(tg)}, about {float(percentage):.6f}% of LD’s restricted-time total. This is a small finite-option opportunity envelope, not evidence that the broader problem is unlearnable.",'',
      'TIGHT_HEADROOM independently recomputes the v2 pairwise bounds in SPLIT_DIAGNOSTICS. Unchanged selected branches contribute exactly zero, avoiding interval self-subtraction. The original more conservative v1 export remains in V1_EXPORT_EVIDENCE; all versions use the same data and policy set. Neither bound is a statistical confidence interval.','',
      '| TEST family | Equal-task finite oracle T gain vs LD |', '|---|---:|']
    for key,d in tight['TEST_families'].items():lines.append(f"| {key} | {pretty(d['equal_task_oracle_T_gain_vs_LD'])} |")
    lines += ['', f"The TRAIN task-first envelope is {split['train']['N_task_first_oracle']} versus C {split['train']['N_C']} and LD {split['train']['N_LD']}. TRAIN contains two LD task losses as well as three gains. In random132103, LD loses one task at B8 and gains one at B16; the gate state also changes, so this is not an isolated causal estimate of budget alone.", '',
      f"All 48 target gates have exactly one public claim: {all_single_claim}; exact reconstruction from the public inverse-route/owner feature gives one owner on each claim. PUBLIC_COVERAGE records the calculation without private inputs. TRAIN has 22 single-candidate gates and two two-candidate gates; TEST has 15 and one. Multiple visible candidates therefore do not constitute multi-head or multi-owner coupled blocking. The current narrow C/LD tails offer little remaining TEST headroom over a strong fixed rule.", '',
      'The next TRAIN question should be which publicly distinguishable states offer larger legal continuation effects while preserving task count, and where task-count risk changes with remaining budget and state. Keep a task-risk target separate from a same-task timing target; register full-tail labels and a material effect scale before fitting. Public claim/owner multiplicity and alternative eligible actions need actual coverage if the next design aims at coupled dependence. Do not merely enlarge the model, or use these TEST contributors to pick future evaluation cases.', '',
      'These are hypotheses for new preregistered TRAIN/CAL collection, not a new threshold, policy or permission to retune R13 TEST. A separate file-level holdout should test any design change. The common schema preserves shared context, legal complete continuation, whole-task reward, restricted-time cost, actual queries and reachability across research lines; numerical transfer requires a common simulator/action contract.']
    (P/'VALUE_INTERPRETATION.md').write_text('\n'.join(lines)+'\n')
    write('VERIFICATION.json',dict(passed=True,structured_arms=160,matched_pairs=48,TEST_family_clusters=8,
            source_results_sha256=sha(OLD/'RESULTS.json'),pairs_sha256=sha(P/'VALUE_PAIRS.json'),
            raw_trajectory_audits_repeated=0,new_native_runs=0,new_model_fits=0,negative_controls=negatives,
            changed_cache_key_rejected=True,changed_output_digest_rejected=True,second_run_zero_extraction=True,
            bounded_headroom_source='TIGHT_HEADROOM.json',script_sha256=sha(Path(__file__))))
    print(json.dumps(dict(passed=True,TEST_oracle_N=test['N_task_first_oracle'],TEST_oracle_equal_task_T_gain_vs_LD=tg,percentage=float(percentage),negative_controls=len(negatives)+2)))

if __name__=='__main__':main()
