"""Independent TRAIN tree reconstruction and full CAL semantic-alias audit.

No candidate module import, no simulation/solver, no TEST traces or labels.
Only writes QUERY_CAL_MODEL_INDEPENDENT.json beside this script.
"""
from collections import Counter
from fractions import Fraction as F
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
QUERY = Path('/home/lyh/MAPF_PIED_MDDR_LEARNING_EXPLORE/exploration/learned_query')
NEW = QUERY/'stop_value_20261004_r16'
OLD = QUERY/'late_budget_choice_20261004_r13'
PINS = {}
RAW_READ = set()


def sha(path):
    path=Path(path)
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):h.update(block)
    return h.hexdigest()


def read(path):
    path=Path(path);PINS[str(path)]=sha(path)
    return json.loads(path.read_text())


def iv(x):return F(x['lower'],x['denominator']),F(x['upper'],x['denominator'])
def digest(rows):
    h=hashlib.sha256()
    for row in rows:h.update((json.dumps(row,sort_keys=True,separators=(',',':'))+'\n').encode())
    return h.hexdigest()


def receipt(world,policy,base):
    assert world['split'] in ('train','cal','calibration'), 'old TEST excluded'
    path=base/'runs'/(world['name']+'__'+policy+'.receipt.json')
    r=read(path)
    assert r['world']==world['name'] and r['capacity']==world['budget'] and r['policy']==policy
    assert r['error'] is None
    for field in ['raw','input','planner']:
        assert 'test_' not in Path(r[field]).name and '_test_' not in Path(r[field]).name
        actual=sha(r[field]);assert actual==r[field+'_sha256']
        PINS[r[field]]=actual
    return r


def iterraw(r):
    RAW_READ.add(r['raw'])
    with Path(r['raw']).open() as stream:
        for line in stream:yield json.loads(line)


def legal_gate(gate,actor):
    assert actor['event']=='actor_decision' and actor['at']==gate['at']
    assert actor['opportunity']==gate['opportunity']
    assert actor['END_only_known']>=2
    assert all(actor[k] is False for k in ('private_progress_input','regime_input','future_head_input'))
    assert gate['feature_schema']=='late_target10_v1'
    candidates=actor['candidates'];assert candidates
    priorities=[]
    for c in candidates:
        f=list(map(F,c['features']));assert len(f)==24
        assert f[20]==F(actor['remaining_capacity'],16)
        assert f[22]==f[20]*f[19] and f[23]==f[20]*(1-f[21])
        assert F(c['probability'])==f[10]
        assert all(x['remaining_route_items']>0 and x['owners']>0 for x in c['claims'])
        inverse=sum((F(1,x['remaining_route_items']*x['owners']) for x in c['claims']),F(0))
        priorities.append((-F(c['probability'])*inverse,c['agent'],c['move'],c,inverse))
    _,_,_,target,inverse=min(priorities,key=lambda x:x[:3])
    assert (target['agent'],target['move'])==(gate['target_agent'],gate['target_move'])
    f=list(map(F,target['features']))
    expected=[f[10],f[0],f[18],inverse,F(min(x['remaining_route_items'] for x in target['claims']),64),
              F(len(target['claims']),15),F(len(candidates)-1,15),F(actor['remaining_capacity'],16),1-f[21],f[10]*inverse]
    assert list(map(F,gate['features']))==expected
    assert gate['spent']==gate['initial_capacity']//2 and gate['remaining_capacity']>0
    return {'target':target['move'],'candidate_count':len(candidates),'features':list(map(str,expected)),
            'target_selection_reconstructed':True,'public_input_flags_only':True}


def outcome(world,r):
    fifo={a['agent']:a['tasks'] for a in world['robots']}
    counts=Counter();services={};queries=0;position_count=0;gate=None;gate_check=None;pending=False;summary=None
    native_stop=(r['policy']=='macro_STOP');after_end=0
    for row in iterraw(r):
        kind=row['event']
        if pending:
            gate_check=legal_gate(gate,row);pending=False
        if kind=='macro_choice':
            assert gate is None;gate=row;pending=True
        elif kind=='task_service':
            agent=row['agent'];task=fifo[agent][counts[agent]]
            assert row['task']==task['task'] and row['goal']==task['goal']
            assert row['original_endpoint_at_rest'] and row['physical_footprint_inside_service_square']
            assert (agent,row['task']) not in services
            services[agent,row['task']]=iv(row['at']);counts[agent]+=1
        elif kind=='actor_decision':
            assert all(row[k] is False for k in ('private_progress_input','regime_input','future_head_input'))
            queries+=int(row['selected_kind']=='QUERY')
            if native_stop and gate:
                assert row['macro']=='STOP' and row['decision_mode']=='WAIT'
                assert row['selected_kind']=='WAIT' and row['selected']==''
        elif kind=='certified_POSITION_committed':
            position_count+=1
            assert not (native_stop and gate), 'POSITION after STOP'
        elif kind=='public_SKIP_installed':
            assert not native_stop, 'SKIP in STOP arm'
        elif kind=='public_END_delivered':after_end+=int(gate is not None)
        elif kind=='joint_summary':
            assert summary is None;summary=row
    assert summary and summary['status']=='passed' and not summary['deadlock']
    assert iv(summary['last_clock'])==(F(world['horizon']),)*2
    assert not summary['production_COST']
    assert queries==position_count==summary['queries']<=world['budget']
    assert len(services)==summary['served']
    if native_stop:assert queries==world['budget']//2 and gate['selected_option']=='STOP' and after_end>0
    restricted=[F(0),F(0)]
    for agent,tasks in fifo.items():
        for task in tasks[:4]:
            at=services.get((agent,task['task']),(F(world['horizon']),)*2)
            restricted[0]+=at[0];restricted[1]+=at[1]
    return {'world':world['name'],'tasks':len(services),'queries':queries,'T_lower':str(restricted[0]),'T_upper':str(restricted[1]),
            'gate':gate,'gate_check':gate_check,'raw_sha256':r['raw_sha256']}


def assert_outcome(actual,reported):
    for k in ['tasks','queries','T_lower','T_upper','raw_sha256']:assert actual[k]==reported[k],(actual['world'],k)


def reconstruct_tree(rows):
    # Independent weighted variance formula, retaining prescribed enumeration ties.
    material=Counter()
    data=[]
    for row in rows:
        dt=row['delta_tasks'];low,high=F(row['T_gain_lower']),F(row['T_gain_upper'])
        label='STOP' if dt>0 or dt==0 and low>=1 else 'C' if dt<0 or dt==0 and high<=-1 else 'neutral'
        material[label]+=1
        if row['gate'] is not None:data.append((list(map(F,row['gate']['features'])),F(dt),(low+high)/2))
    assert material['STOP'] and material['C'] and len(data)>=8
    def leaf(indices):
        n=len(indices);task=sum((data[i][1] for i in indices),F(0))/n
        timing=sum((data[i][2] for i in indices),F(0))/n
        y=[data[i][1]+data[i][2]/16385 for i in indices]
        variance=(sum((z*z for z in y),F(0))-sum(y,F(0))**2/n)/2
        return {'tasks':str(task),'time_gain':str(timing),'n':n,'weight':str(F(n,2))},variance
    ids=list(range(len(data)));root,root_loss=leaf(ids);best=root_loss;tree={'leaf':root};splits=0
    for j in range(10):
        xs=sorted({x[0][j] for x in data})
        for i in range(len(xs)-1):
            threshold=(xs[i]+xs[i+1])/2
            left=[k for k in ids if data[k][0][j]<=threshold];right=[k for k in ids if data[k][0][j]>threshold]
            if min(len(left),len(right))<4:continue
            splits+=1;l,ll=leaf(left);r,rr=leaf(right)
            if ll+rr<best:
                best=ll+rr;tree={'feature':j,'threshold':str(threshold),'left':l,'right':r}
    return {'activated':True,'preferences':dict(material),'tree':tree,'root_loss':str(root_loss),'loss':str(best),
            'training_gated_rows':len(data),'enumerated_valid_splits':splits}


def choose(model,gate):
    if gate is None or not model['activated']:return 'C',None
    tree=model['tree']
    leaf=tree.get('leaf') or tree['left' if F(gate['features'][tree['feature']])<=F(tree['threshold']) else 'right']
    pick='STOP' if F(leaf['tasks'])>0 or F(leaf['tasks'])==0 and F(leaf['time_gain'])>=1 else 'C'
    return pick,leaf


def alias_check(source,target,claim,source_world,target_world):
    excluded={'actor_decision','macro_choice','joint_summary'}
    assert {k:v for k,v in source_world.items() if k not in ('name','budget')}=={k:v for k,v in target_world.items() if k not in ('name','budget')}
    assert Path(source['input']).read_bytes()==Path(target['input']).read_bytes()
    target_prefix=[];target_positions=[];target_gate=None;target_actor=None
    iterator=iterraw(target)
    for row in iterator:
        if row['event']=='macro_choice':
            target_gate=row;target_actor=next(iterator);break
        if row['event'] not in excluded:target_prefix.append(row)
        if row['event']=='certified_POSITION_committed':target_positions.append(row)
    assert target_gate and target_gate['spent']==8 and target_gate['remaining_capacity']==8
    legal_gate(target_gate,target_actor)
    assert len(target_positions)==8
    source_prefix=[];source_positions=[];source_actor=None;after=Counter();at_gate=False
    for row in iterraw(source):
        kind=row['event']
        if not at_gate and kind not in excluded:
            source_prefix.append(row)
            if len(source_prefix)==len(target_prefix):at_gate=True
        elif at_gate:after[kind]+=1
        if kind=='certified_POSITION_committed':source_positions.append(row)
        if at_gate and kind=='actor_decision':
            if source_actor is None:source_actor=row
            assert row['remaining_capacity']==0 and row['selected_kind']=='WAIT' and row['selected']==''
    assert source_prefix==target_prefix
    assert source_positions==target_positions and len(source_positions)==8
    assert after['certified_POSITION_committed']==after['public_SKIP_installed']==0
    assert source_actor is not None
    stable_keys=['at','opportunity','trigger','RR_cursor','END_only_known','END_unknown',
                 'private_progress_input','regime_input','future_head_input']
    assert all(source_actor[k]==target_actor[k] for k in stable_keys)
    assert all(source_actor[k] is False for k in ('private_progress_input','regime_input','future_head_input'))
    assert len(source_actor['candidates'])==len(target_actor['candidates'])
    for a,b in zip(source_actor['candidates'],target_actor['candidates']):
        assert all(a[k]==b[k] for k in ['agent','move','heading','public_launch','probability','claims'])
        assert len(a['features'])==len(b['features'])==24
        assert all(a['features'][j]==b['features'][j] for j in range(24) if j not in (20,22,23))
        for actor,candidate in [(source_actor,a),(target_actor,b)]:
            f=list(map(F,candidate['features']))
            assert f[20]==F(actor['remaining_capacity'],16)
            assert f[22]==f[20]*f[19] and f[23]==f[20]*(1-f[21])
    actual={'physical_public_prefix_sha256':digest(target_prefix),'prefix_records':len(target_prefix),
            'first8_position_sha256':digest(target_positions),'source_gate_actor_sha256':digest([source_actor]),
            'target_gate_actor_sha256':digest([target_actor])}
    for k,v in actual.items():assert claim[k]==v,k
    assert claim['source_raw_sha256']==source['raw_sha256'] and claim['target_gate_raw_sha256']==target['raw_sha256']
    assert claim['gate']==target_gate
    assert claim['after_gate_source_events']==dict(after)
    return dict(actual,source_world=source_world['name'],target_world=target_world['name'],
                exact_input_equal=True,first8_complete_POSITION_records_equal=True,nonbudget_candidate_features_equal=True,
                all_budget_feature_exceptions_recomputed=True,no_source_QUERY_SKIP_after_gate=True,
                semantic_alias_only=True,native_STOP=False)


def total(rows):
    return {'contexts':len(rows),'tasks':sum(x['tasks'] for x in rows),'queries':sum(x['queries'] for x in rows),
            'T_lower':str(sum((F(x['T_lower']) for x in rows),F(0))),'T_upper':str(sum((F(x['T_upper']) for x in rows),F(0)))}


def main():
    registration=read(NEW/'REGISTRATION.json');model=read(NEW/'MODEL_FROZEN.json')
    train_pairs=read(NEW/'TRAIN_PAIRS.json');cal_pairs=read(NEW/'CAL_PAIRS.json')
    selection=read(NEW/'CAL_SELECTIONS.json');alias=read(NEW/'CAL_ALIAS_REGISTRATION.json')
    train_start=read(NEW/'TRAIN_START.json');cal_start=read(NEW/'CAL_START.json')
    assert len(train_pairs)==len(registration['train_worlds'])==24
    assert len(cal_pairs)==len(registration['cal_worlds'])==6
    assert model['training_pairs_sha256']==sha(NEW/'TRAIN_PAIRS.json')
    assert model['learn_source_sha256']==registration['frozen']['learn.py']==sha(NEW/'learn.py')
    for name,h in registration['frozen'].items():assert sha(NEW/name)==h
    assert train_start['registration_sha256']==sha(NEW/'REGISTRATION.json')
    assert alias['original_registration_sha256']==sha(NEW/'REGISTRATION.json')
    assert alias['alias_source_sha256']==sha(NEW/'cal_alias.py')
    assert alias['amendment_sha256']==sha(NEW/'CAL_ALIAS_AMENDMENT.md')
    assert alias['train_equivalence_sha256']==sha(NEW/'BUDGET_ALIAS_OBSERVATION.json')
    assert model['frozen_unix_ns']<alias['frozen_unix_ns']<cal_start['started_unix_ns']
    assert alias['model_frozen_sha256']==selection['model_sha256']==sha(NEW/'MODEL_FROZEN.json')
    assert cal_start['alias_registration_sha256']==sha(NEW/'CAL_ALIAS_REGISTRATION.json')
    assert registration['frozen_unix_ns']<train_start['started_unix_ns']<model['frozen_unix_ns']
    # The four changes are inside policy selection/allow-list; all World3 code is unchanged.
    old_source=(OLD/'joint_history_native.cpp').read_text();new_source=(NEW/'joint_history_native.cpp').read_text()
    replacements=[('options={"C","LD"}','options={"C",policy=="macro_STOP"?"STOP":"LD"}'),
                  ('policy=="alwaysLD"||policy=="macro_LD")selected_option=1','policy=="alwaysLD"||policy=="macro_LD"||policy=="macro_STOP")selected_option=1'),
                  ('scoring_policy=macro_name=="W"?"WAIT":"condition"','scoring_policy=(macro_name=="W"||macro_name=="STOP")?"WAIT":"condition"'),
                  ('p=="macro_C"||p=="macro_LD"','p=="macro_C"||p=="macro_STOP"||p=="macro_LD"')]
    transformed=old_source
    for before,after in replacements:
        assert transformed.count(before)==1;transformed=transformed.replace(before,after)
    assert transformed==new_source
    assert 'if(selected.empty())return;' in new_source
    PINS[str(OLD/'joint_history_native.cpp')]=sha(OLD/'joint_history_native.cpp')
    PINS[str(NEW/'joint_history_native.cpp')]=sha(NEW/'joint_history_native.cpp')
    worlds={w['name']:w for w in registration['train_worlds']+registration['cal_worlds']}
    train_audit=[];recomputed_train=[];train_receipts=[]
    for row in train_pairs:
        w=worlds[row['world']];assert w['split']=='train'
        cr=receipt(w,'macro_C',OLD);sr=receipt(w,'macro_STOP',NEW)
        train_receipts.append(sr)
        assert registration['frozen_unix_ns']<sr['started_unix_ns']<sr['finished_unix_ns']<model['frozen_unix_ns']
        assert cr['input_sha256']==sr['input_sha256']
        co=outcome(w,cr);so=outcome(w,sr);assert_outcome(co,row['C']);assert_outcome(so,row['STOP'])
        assert co['gate']==row['gate']
        low=F(co['T_lower'])-F(so['T_upper']);high=F(co['T_upper'])-F(so['T_lower']);delta=so['tasks']-co['tasks']
        assert (delta,str(low),str(high),co['queries']-so['queries'])==(row['delta_tasks'],row['T_gain_lower'],row['T_gain_upper'],row['queries_saved'])
        recomputed_train.append(dict(world=w['name'],gate=co['gate'],delta_tasks=delta,T_gain_lower=str(low),T_gain_upper=str(high)))
        train_audit.append({'world':w['name'],'labels_from_raw_verified':True,'gate_features_reconstructed':True})
    independent_model=reconstruct_tree(recomputed_train)
    for k in ['activated','preferences','tree','root_loss','loss','training_gated_rows']:assert independent_model[k]==model[k],k
    assert [r['world'] for r in train_pairs]==model['training_worlds']
    assert model['max_depth']==1 and model['min_leaf_rows']==4 and model['schema']=='late_target10_v1'
    by_world={};alias_results=[];native_cal=[]
    for row in cal_pairs:
        w=worlds[row['world']];assert w['split'] in ('cal','calibration')
        cr=receipt(w,'macro_C',OLD);co=outcome(w,cr);assert_outcome(co,row['C']);assert co['gate']==row['gate']
        if w['budget']==8:
            sr=receipt(w,'macro_STOP',NEW);native_cal.append(sr)
            assert sr['model_frozen_sha256']==sha(NEW/'MODEL_FROZEN.json')
            assert cal_start['started_unix_ns']<sr['started_unix_ns']<sr['finished_unix_ns']
            assert sr['input_sha256']==cr['input_sha256']
            so=outcome(w,sr);assert not row['STOP'].get('semantic_alias')
        else:
            claim=next(x for x in alias['checks'] if x['target_world']==w['name'])
            sw=worlds[claim['source_world']];assert sw['budget']==8
            source=receipt(sw,'macro_C',OLD);so=outcome(sw,source)
            check=alias_check(source,cr,claim,sw,w);alias_results.append(check)
            assert not (NEW/'runs'/(w['name']+'__macro_STOP.receipt.json')).exists()
            assert row['STOP']['policy']=='macro_STOP_semantic_alias'
            provenance=row['STOP']['semantic_alias']
            assert provenance['source_world']==sw['name'] and provenance['source_policy']=='macro_C' and provenance['source_budget']==8
            assert provenance['source_raw_sha256']==source['raw_sha256']
            assert provenance['target_gate_raw_sha256']==cr['raw_sha256']
            assert provenance['alias_registration_sha256']==sha(NEW/'CAL_ALIAS_REGISTRATION.json')
            assert claim['source_receipt_sha256']==sha(OLD/'runs'/(sw['name']+'__macro_C.receipt.json'))
            assert claim['target_gate_receipt_sha256']==sha(OLD/'runs'/(w['name']+'__macro_C.receipt.json'))
            ap=OLD/'audits'/(sw['name']+'__macro_C.receipt.audit.json')
            assert sha(ap)==claim['source_audit_sha256'] and read(ap)['status']=='passed'
        assert_outcome(so,row['STOP'])
        assert row['delta_tasks']==so['tasks']-co['tasks']
        assert F(row['T_gain_lower'])==F(co['T_lower'])-F(so['T_upper'])
        assert F(row['T_gain_upper'])==F(co['T_upper'])-F(so['T_lower'])
        by_world[w['name']]={'C':co,'STOP':so,'gate':co['gate'],'alias':w['budget']==16}
    decisions=[];chosen=[]
    for row in selection['selections']:
        rs=by_world[row['world']];pick,leaf=choose(independent_model,rs['gate']);actual=rs[pick]
        assert pick==row['selected'] and actual['raw_sha256']==row['selected_raw_sha256']
        assert row['selected_is_semantic_alias']==(rs['alias'] and pick=='STOP')
        chosen.append(actual)
        decisions.append({'world':row['world'],'choice':pick,'feature_8':rs['gate']['features'][8],
                          'leaf_prediction':leaf,'selected_raw_sha256':actual['raw_sha256'],
                          'selected_is_semantic_alias':row['selected_is_semantic_alias']})
    assert len(decisions)==len(by_world)==6 and len(native_cal)==len(alias_results)==3
    totals={'fixed_C':total([x['C'] for x in by_world.values()]),'fixed_STOP':total([x['STOP'] for x in by_world.values()]),'tree':total(chosen)}
    for name,reported in [('fixed_C','fixed_C'),('fixed_STOP','fixed_STOP'),('tree','total')]:
        for k,v in totals[name].items():assert selection[reported][k]==v,(name,k)
    c,s,t=totals['fixed_C'],totals['fixed_STOP'],totals['tree']
    dominates=s['tasks']>=t['tasks'] and s['queries']<=t['queries'] and F(s['T_upper'])<F(t['T_lower'])
    assert dominates and (c['tasks'],c['queries'],s['tasks'],s['queries'],t['tasks'],t['queries'])==(237,72,238,36,238,52)
    result={'passed':True,'auditor':'main evidence implementer cross-review, independent implementation, not blind',
            'candidate_learn_imported':False,'simulation_calls':0,'old_TEST_traces_or_labels_read':0,
            'TRAIN_rows_rebuilt_from_raw':len(train_audit),'CAL_contexts':6,'CAL_independent_families':3,
            'CAL_new_native_STOP':3,'CAL_STOP_semantic_aliases':3,'aliases_are_native_STOP':False,
            'unique_raw_files_read':len(RAW_READ),'model_reconstruction':independent_model,'training_checks':train_audit,
            'freeze_order':{'source_registration':registration['frozen_unix_ns'],'TRAIN_start':train_start['started_unix_ns'],
                            'last_TRAIN_native_finish':max(r['finished_unix_ns'] for r in train_receipts),'model_freeze':model['frozen_unix_ns'],
                            'CAL_alias_qualification_freeze':alias['frozen_unix_ns'],'CAL_start':cal_start['started_unix_ns'],
                            'first_new_CAL_native_start':min(r['started_unix_ns'] for r in native_cal),
                            'source_before_TRAIN_model_before_new_CAL':True,
                            'limit':'Old cached C CAL traces pre-existed R16; not a claim that model preceded their original creation. Exact model reconstruction uses TRAIN only.'},
            'native_source_delta_exactly_four_policy_changes':True,'alias_checks':alias_results,'CAL_selections_recomputed':decisions,
            'totals':totals,'fixed_STOP_strictly_dominates_tree_on_tasks_queries_restricted_T':dominates,
            'tree_extra_queries_vs_STOP':t['queries']-s['queries'],
            'tree_restricted_T_excess_interval':[str(F(t['T_lower'])-F(s['T_upper'])),str(F(t['T_upper'])-F(s['T_lower']))],
            'scope':'Restricted T sums each agent fixed first four FIFO completion times, missing=H128; not flow time or unrestricted task sum. Three families with paired budgets, exploratory CAL only. Query count is not production COST. Alias is finite frozen-source semantics, not universal cache identity.',
            'source_and_receipt_pins':PINS,'script_sha256':sha(__file__)}
    (HERE/'QUERY_CAL_MODEL_INDEPENDENT.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['passed','TRAIN_rows_rebuilt_from_raw','CAL_new_native_STOP','CAL_STOP_semantic_aliases','unique_raw_files_read','totals','fixed_STOP_strictly_dominates_tree_on_tasks_queries_restricted_T','tree_extra_queries_vs_STOP','tree_restricted_T_excess_interval']},indent=2))


if __name__=='__main__':main()
