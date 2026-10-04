"""Reuse frozen R13 complete-tail values; no simulator, model fit or raw extraction."""
from pathlib import Path
from fractions import Fraction as F
from collections import Counter, defaultdict
import argparse, csv, hashlib, json, time

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / 'late_budget_choice_20261004_r13'
INPUTS = ['REGISTRATION.json', 'RESULTS.json', 'TRAIN_CAL_LABELS.json',
          'RAW_ARCHIVE_MANIFEST.json', 'AUDIT_ALL.json', 'DEPLOYMENT_AUDIT.json',
          'ROOT_MACRO_AUDIT.json', 'MENTOR_MODEL_AUDIT.json',
          'OFFLINE_REPLAY_RECEIPT.json', 'MODELS_FROZEN_BEFORE_TEST.json']
OUTPUTS = ['ARM_VALUES.json', 'VALUE_PAIRS.json', 'VALUE_PAIRS.csv',
           'SPLIT_DIAGNOSTICS.json', 'TEST_FAMILY_DIAGNOSTICS.json',
           'PUBLIC_CONDITION_DIAGNOSTICS.json', 'REPORT.md', 'HANDOFF.md']

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p): return json.loads(p.read_text())
def canonical(d): return json.dumps(d, sort_keys=True, separators=(',', ':')).encode()
def write(name, d): (HERE/name).write_text(json.dumps(d, sort_keys=True, indent=2)+'\n')
def rational(x): return str(F(x))
def add(xs): return sum(map(F, xs), F(0))
def interval(lo, hi): return {'lower': str(lo), 'upper': str(hi)}
def pretty(d): return '['+', '.join(f'{float(F(d[k])):.6f}' for k in ('lower','upper'))+']'

def bindings():
    freeze = load(SOURCE/'FROZEN_MANIFEST.json')['frozen_files']
    pins = {}
    for name in INPUTS:
        digest = sha(SOURCE/name)
        assert digest == freeze[name]['sha256'], ('source changed', name)
        pins[name] = digest
    pins['FROZEN_MANIFEST.json'] = sha(SOURCE/'FROZEN_MANIFEST.json')
    for name in ['export_values.py', 'CONTRACT.md', 'COMMON_VALUE_SCHEMA.json']:
        pins['R14/'+name] = sha(HERE/name)
    return pins, hashlib.sha256(canonical(pins)).hexdigest()

def cache_matches(cache, key):
    return (cache.get('cache_key') == key and set(cache.get('outputs',{})) == set(OUTPUTS)
            and all((HERE/n).is_file() and sha(HERE/n)==d for n,d in cache['outputs'].items()))

def tail_outcome(r):
    return dict(N=r['tasks'], T=interval(r['T_lower'],r['T_upper']),
                queries=r['queries'], remaining=r['remaining'],
                service_sha256=r['service_sha256'],
                requested_interventions=r['requested_interventions'],
                actual_interventions=r['actual_interventions'],
                unreached_reason=r['unreached_observation'])

def select_envelope(pair):
    c,d=pair['C'],pair['LD']
    if c['N']!=d['N']:
        x=c if c['N']>d['N'] else d
        return x['N'], F(x['T']['lower']), F(x['T']['upper'])
    return c['N'], min(F(c['T']['lower']),F(d['T']['lower'])), min(F(c['T']['upper']),F(d['T']['upper']))

def aggregate(pairs):
    families=defaultdict(list)
    for p in pairs: families[p['family_key']].append(p)
    base={k:dict(N=sum(p[k]['N'] for p in pairs),queries=sum(p[k]['queries'] for p in pairs),
                 T=interval(add(p[k]['T']['lower'] for p in pairs), add(p[k]['T']['upper'] for p in pairs))) for k in ['C','LD']}
    envelopes=[select_envelope(p) for p in pairs]
    oracle=dict(N=sum(x[0] for x in envelopes), T=interval(sum((x[1] for x in envelopes),F(0)),sum((x[2] for x in envelopes),F(0))))
    eq=[p for p in pairs if p['delta_N']==0]
    eq_gain={}
    for option in ['C','LD']:
        # Same selected branch contributes exactly zero; preserve covariance.
        # max is monotone, including any numerically unresolved alternative.
        lo=hi=F(0)
        for p in eq:
            l,u=map(F,[p['delta_T']['lower'],p['delta_T']['upper']])
            if option=='LD':l,u=-u,-l
            lo+=max(l,F(0));hi+=max(u,F(0))
        eq_gain[option]=interval(lo,hi)
    # A single shared option for both budgets in each family cannot exploit within-family budget differences.
    family_shared_N=sum(max(sum(p[k]['N'] for p in ps) for k in ['C','LD']) for ps in families.values())
    budget_groups=defaultdict(list)
    for p in pairs:budget_groups[p['budget']].append(p)
    per_budget_fixed_N=sum(max(sum(p[k]['N'] for p in ps) for k in ['C','LD']) for ps in budget_groups.values())
    return dict(contexts=len(pairs),registered_families=len(families),fixed_complete_tails=base,
                task_signs=dict(Counter(p['task_relation'] for p in pairs)),
                task_time_conflicts=[p['world'] for p in pairs if p['task_time_conflict']],
                same_task_contexts=len(eq),same_task_time_signs=dict(Counter(p['time_relation'] for p in eq)),
                same_task_service_equal=sum(p['service_records_equal'] for p in eq),
                same_task_finite_oracle_time_gain_vs_fixed=eq_gain,
                finite_task_first_oracle=oracle,
                finite_task_first_oracle_N_gain_vs_fixed={k:oracle['N']-base[k]['N'] for k in base},
                diagnostic_family_shared_option_oracle_N=family_shared_N,
                diagnostic_per_budget_fixed_option_oracle_N=per_budget_fixed_N,
                oracle_not_deployable=True)

def extract(pins):
    rs=load(SOURCE/'RESULTS.json'); reg=load(SOURCE/'REGISTRATION.json')
    assert len(rs)==160 and len(reg['worlds'])==48 and not any(r['error'] for r in rs)
    archive=load(SOURCE/'RAW_ARCHIVE_MANIFEST.json')
    rawrefs={m['path']:dict(member=m['path'],sha256=m['sha256'],archive=a['path'],archive_sha256=a['sha256'])
             for a in archive['archives'] for m in a['members'] if m['path'].endswith('.jsonl') and not m['path'].endswith('.planner.jsonl')}
    assert len(rawrefs)==160
    arms=[]; by={}
    for r in sorted(rs,key=lambda r:(r['world'],r['policy'])):
        gate=r['gate'];rawname='runs/'+r['world']+'__'+r['policy']+'.jsonl'
        a=dict(world=r['world'],family_key=r['family_key'],split=r['split'],budget=r['budget'],policy=r['policy'],
               provenance={k:r[k] for k in ['map','seed','scenario','offset']},
               public_gate=None if gate is None else {k:gate[k] for k in ['at','opportunity','initial_capacity','spent','remaining_capacity','feature_schema','features']},
               gate_identity=None if gate is None else dict(agent=gate['target_agent'],occurrence=gate['target_move']),
               outcome=tail_outcome(r),actual_option=r['selected_option'],planned_option=r['planned_option'],
               query_occurrences=r['query_occurrences'],interventions=r['interventions'],raw_reference=rawrefs[rawname])
        assert a['outcome']['queries']+a['outcome']['remaining']==a['budget']
        arms.append(a);by[r['world'],r['policy']]=a
    pairs=[]
    for w in sorted(reg['worlds'],key=lambda w:w['name']):
        cp,dp=('condition','alwaysLD') if w['split']=='test' else ('macro_C','macro_LD')
        c,d=by[w['name'],cp],by[w['name'],dp]
        assert c['public_gate']==d['public_gate'] and c['gate_identity']==d['gate_identity']
        co,do=c['outcome'],d['outcome'];dn=do['N']-co['N'];same=co['service_sha256']==do['service_sha256']
        rawlo=F(co['T']['lower'])-F(do['T']['upper']);rawhi=F(co['T']['upper'])-F(do['T']['lower'])
        # Identical exact service records imply zero difference, avoiding interval self-subtraction noise.
        lo,hi=(F(0),F(0)) if same else (rawlo,rawhi)
        trel='LD_faster' if lo>0 else 'C_faster' if hi<0 else 'identical_service' if same else 'numerically_unresolved'
        gate=c['public_gate'];features=None if gate is None else gate['features']
        conditions=None if features is None else dict(candidate_count=int(F(features[6])*15+1),claim_count=int(F(features[5])*15),
                remaining_at_gate=gate['remaining_capacity'],spent_at_gate=gate['spent'],history_p=features[0],prior_p=features[1],
                inverse_route_owner_claim_sum=features[3],min_blocked_remaining_route_over64=features[4],remaining_horizon=features[8])
        cq={x['move'] for x in c['query_occurrences']};dq={x['move'] for x in d['query_occurrences']}
        p=dict(world=w['name'],family_key=c['family_key'],split=c['split'],budget=c['budget'],provenance=c['provenance'],
               public_gate=gate,public_conditions=conditions,gate_identity_provenance=c['gate_identity'],C=co,LD=do,
               delta_N=dn,delta_T=interval(lo,hi),raw_interval_subtraction=interval(rawlo,rawhi),
               delta_queries=do['queries']-co['queries'],service_records_equal=same,
               task_relation='LD_more_tasks' if dn>0 else 'C_more_tasks' if dn<0 else 'equal_tasks',
               time_relation=trel,task_time_conflict=(dn>0 and hi<0) or (dn<0 and lo>0),
               query_identity_difference=dict(C_only=sorted(cq-dq),LD_only=sorted(dq-cq)),
               branch_sources={'C':c['raw_reference'],'LD':d['raw_reference']},
               prefix_evidence_sha256=pins['DEPLOYMENT_AUDIT.json'],root_audit_sha256=pins['ROOT_MACRO_AUDIT.json'])
        pairs.append(p)
    assert Counter(p['split'] for p in pairs)==Counter(train=24,calibration=8,test=16)
    labels={(r['world'],r['option']):r for r in load(SOURCE/'TRAIN_CAL_LABELS.json')}
    for p in pairs:
        if p['split']!='test':
            old=labels[p['world'],'LD']
            assert F(old['task_target'])==p['delta_N'] and old['features']==p['public_gate']['features']
            assert F(old['T_gain_lower'])==F(p['raw_interval_subtraction']['lower']) and F(old['T_gain_upper'])==F(p['raw_interval_subtraction']['upper'])
    return arms,pairs

def produce(pins):
    arms,pairs=extract(pins);write('ARM_VALUES.json',dict(schema='complete_public_continuation_value_v1',arms=arms))
    write('VALUE_PAIRS.json',dict(schema='complete_public_continuation_value_v1',pairs=pairs))
    fields=['world','family_key','split','budget','delta_N','delta_T_lower','delta_T_upper','delta_queries','task_relation','time_relation','task_time_conflict','service_records_equal','candidate_count','claim_count']
    with (HERE/'VALUE_PAIRS.csv').open('w',newline='') as f:
        out=csv.DictWriter(f,fieldnames=fields);out.writeheader()
        for p in pairs:
            row={k:p[k] for k in fields if k in p};row.update(delta_T_lower=p['delta_T']['lower'],delta_T_upper=p['delta_T']['upper'])
            row.update({k:None if p['public_conditions'] is None else p['public_conditions'][k] for k in ['candidate_count','claim_count']});out.writerow(row)
    splits={s:aggregate([p for p in pairs if p['split']==s]) for s in ['train','calibration','test']}
    write('SPLIT_DIAGNOSTICS.json',splits)
    grouped=defaultdict(list)
    for p in pairs:
        if p['split']=='test':grouped[p['family_key']].append(p)
    families=[]
    for key,ps in sorted(grouped.items()):
        assert sorted(p['budget'] for p in ps)==[8,16]
        families.append(dict(family_key=key,paired_budgets=[8,16],worlds=[p['world'] for p in ps],
                             budget_task_labels={str(p['budget']):p['delta_N'] for p in ps},
                             budget_time_relations={str(p['budget']):p['time_relation'] for p in ps},values=aggregate(ps)))
    write('TEST_FAMILY_DIAGNOSTICS.json',dict(registered_families=8,independent_budget_samples=False,source_scenario_files=2,families=families))
    strata=[]
    for split in ['train','calibration','test']:
        for field in ['budget','candidate_count','claim_count']:
            groups=defaultdict(list)
            for p in pairs:
                if p['split']==split:
                    val=p['budget'] if field=='budget' else None if p['public_conditions'] is None else p['public_conditions'][field]
                    groups[str(val)].append(p)
            for value,ps in sorted(groups.items()):strata.append(dict(split=split,public_field=field,value=value,values=aggregate(ps)))
    write('PUBLIC_CONDITION_DIAGNOSTICS.json',dict(descriptive_only=True,no_threshold_search=True,strata=strata))
    report(pairs,splits,families)
    return len(arms),len(pairs)

def report(pairs,splits,families):
    test=splits['test'];lines=['# R14: reusable complete-tail evidence value diagnostics','',
      'This analysis reuses all 160 frozen R13 arms and exports 48 matched C/LD complete-tail pairs. It performs no new native run, fit, threshold selection or raw trajectory audit. All exported raw references retain their archive/member content hashes.','',
      'The 16 TEST contexts are eight registered row-block/error-seed families, each run with B8 and B16. They come from two scenario-2 files on two maps. Budget repetitions are paired, not independent observations; no file-level or unseen-map generalization is established.','',
      '| Split | C tasks | LD tasks | Task-first finite oracle | Oracle gain vs C / LD | LD more / equal / fewer task contexts |',
      '|---|---:|---:|---:|---:|---:|']
    for s,d in splits.items():
        z=d['task_signs'];lines.append(f"| {s} | {d['fixed_complete_tails']['C']['N']} | {d['fixed_complete_tails']['LD']['N']} | {d['finite_task_first_oracle']['N']} | {d['finite_task_first_oracle_N_gain_vs_fixed']['C']} / {d['finite_task_first_oracle_N_gain_vs_fixed']['LD']} | {z.get('LD_more_tasks',0)} / {z.get('equal_tasks',0)} / {z.get('C_more_tasks',0)} |")
    lines+=['','The oracle knows both completed outcomes. It only bounds choices within the two registered tails at the registered gate; it is not a deployable baseline or the globally best MAPF policy. Its label must never become an input feature or tune this TEST.','',
      '| Split: equal-task subset only | Contexts | LD faster / C faster / identical / unresolved | Finite oracle time gain vs C | Finite oracle time gain vs LD |',
      '|---|---:|---:|---:|---:|']
    for s,d in splits.items():
        z=d['same_task_time_signs'];g=d['same_task_finite_oracle_time_gain_vs_fixed'];lines.append(f"| {s} | {d['same_task_contexts']} | {z.get('LD_faster',0)} / {z.get('C_faster',0)} / {z.get('identical_service',0)} / {z.get('numerically_unresolved',0)} | {pretty(g['C'])} | {pretty(g['LD'])} |")
    lines += ['', 'Time is the fixed first-four-tasks-per-agent restricted sum through H128, with unfinished tasks assigned128; task count covers the whole FIFO. Rational bounds are numerical enclosures, not statistical confidence intervals. Identical service hashes tighten a pair difference to exactly zero. Equal-task time-space excludes every context whose task counts differ, so faster timing cannot hide a lost task.','',
      '| Registered TEST family (both budgets) | C / LD tasks | Task-first oracle tasks | Equal-task oracle T gain vs LD | B8 / B16 LD task labels |',
      '|---|---:|---:|---:|---|']
    for f in families:
        d=f['values'];lines.append(f"| {f['family_key']} | {d['fixed_complete_tails']['C']['N']} / {d['fixed_complete_tails']['LD']['N']} | {d['finite_task_first_oracle']['N']} | {pretty(d['same_task_finite_oracle_time_gain_vs_fixed']['LD'])} | {f['budget_task_labels']['8']} / {f['budget_task_labels']['16']} |")
    conflicts=[p for p in pairs if p['task_time_conflict']]
    lines+=['','Task/time conflicts are retained: '+('; '.join(p['world']+f" (LD ΔN={p['delta_N']:+d}, ΔT={pretty(p['delta_T'])})" for p in conflicts) or 'none')+'.','',
      'The reusable learning target is the value of a complete continuation from a common public prefix. Keep whole-task risk and equal-task time value as distinct targets/evaluation strata. Public budget, candidate multiplicity, claim structure and time remaining are available conditioning variables; their descriptive tables are not a fitted threshold rule. A future TRAIN design should collect both task-safe timing reversals and task-risk examples at matched budget/state conditions, retain ties and negative cases, and evaluate against fixed LD and C. More parameters alone do not create missing causal action-space coverage.','',
      'The shared interface in COMMON_VALUE_SCHEMA.json is context → complete option → task/time/query outcome plus paired value. It can align query and graph/search experiments only after their legal action, budget and full-tail contracts are separately specified. It does not equate the third line’s actions with C/LD or transfer these numerical labels to another simulator.','',
      'This round fits no model and uses no TEST result to select a new policy. Future research remains within the user’s continuing authorization; proposed training changes require new preregistered TRAIN/CAL and separate file-level TEST. Cache receipts record extraction and a second content-verified reuse. The original v1 evidence and receipts are preserved; v2 sums nonnegative pairwise oracle gains so unchanged branches contribute exactly zero. Source and export hashes are in VALUE_CACHE.json.']
    (HERE/'REPORT.md').write_text('\n'.join(lines)+'\n')
    (HERE/'HANDOFF.md').write_text('# R14 query handoff\n\nRun `rtk proxy python3 export_values.py --run-name <new-name>` in this directory. No native executable or model trainer is called. Read REPORT.md, VALUE_PAIRS.json/CSV, SPLIT_DIAGNOSTICS.json, TEST_FAMILY_DIAGNOSTICS.json and COMMON_VALUE_SCHEMA.json. ARM_VALUES preserves all 160 controls; 48 matched pairs retain public-gate/outcome/provenance separation. INPUT hashes bind frozen R13; cached deterministic outputs are verified before reuse. Root owns entry documentation and publication. R13 and all earlier frozen files are unchanged.\n')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--run-name',required=True);args=ap.parse_args()
    assert args.run_name.replace('_','').isalnum()
    receipt=HERE/('REUSE_'+args.run_name+'.json');assert not receipt.exists(),'receipt must not be overwritten'
    start=time.time_ns();pins,key=bindings();cache_path=HERE/'VALUE_CACHE.json'
    hit=cache_path.exists() and cache_matches(load(cache_path),key)
    if hit: arms=pairs=0
    else:
        assert not cache_path.exists(),'changed input/output: preserve old extraction in another isolated directory'
        arms,pairs=produce(pins)
        write('VALUE_CACHE.json',dict(cache_key=key,source_directory=str(SOURCE),pins=pins,
                outputs={n:sha(HERE/n) for n in OUTPUTS},extracted_arms=arms,extracted_pairs=pairs))
    write(receipt.name,dict(passed=True,cache_hit=hit,cache_key=key,started_unix_ns=start,finished_unix_ns=time.time_ns(),
                extracted_arms=arms,extracted_pairs=pairs,raw_trajectory_reads=0,new_native_runs=0,new_model_fits=0,
                source_frozen_manifest_sha256=pins['FROZEN_MANIFEST.json'],cache_manifest_sha256=sha(cache_path)))
    print(json.dumps(dict(cache_hit=hit,extracted_arms=arms,extracted_pairs=pairs,new_native_runs=0,raw_reads=0)))

if __name__=='__main__':main()
