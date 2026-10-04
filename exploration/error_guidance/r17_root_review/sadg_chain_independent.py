"""Independent input, exact reuse, LP and continuous suffix checks; no episodes."""
import importlib.util
import hashlib
import json
from fractions import Fraction as Q
from pathlib import Path
import suffix_independent as physical

HERE = Path(__file__).resolve().parent
BASE = HERE.parent / 'sadg_history_shift_20261004_r17'
load, sha = physical.load, physical.sha
def canonical_hash(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',', ':')).encode()).hexdigest()
spec = importlib.util.spec_from_file_location('old_root_model_audit', HERE.parent/'r16_root_review/sadg_independent.py')
model_audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(model_audit)


def main():
    public = load(BASE/'public.json')
    decision = Q(public['decision_time'])
    assert decision == Q(3,4)
    duration = {}
    for agent in ('agent0', 'agent1'):
        records = [r for r in public['completed_history'] if r['agent'] == agent]
        assert all(Q(r['delivered']) <= decision and Q(r['end']) <= Q(r['delivered']) for r in records)
        rate = sum((Q(r['length']) for r in records), Q(0)) / sum((Q(r['end'])-Q(r['start']) for r in records), Q(0))
        duration[agent] = Q(public['action_length']) / rate
    assert duration == {'agent0':Q(1), 'agent1':Q(1)}
    rows, reused_models, suffixes, new_lp = [], [], {}, []
    for row in load(BASE/'RESULTS.json')['rows']:
        name = row['name']; case = BASE/'cases'/name
        world = load(BASE/'worlds'/(row['scene']+'.json'))
        inp = load(BASE/'inputs'/(name+'.json'))
        assert inp['prediction']['public_sha256'] == canonical_hash(public)
        assert inp['duration_model'] == {a:float(d) for a,d in duration.items()}
        progress = {a: min(Q(1),(decision-Q(t))/duration[a]) for a,t in public['current_start'].items()}
        prefix = world['A_prefix_segments']
        def truth(at):
            return sum((max(Q(0), min(at,Q(s['end']))-Q(s['start']))*Q(s['rate']) for s in prefix),Q(0))
        actual = {'agent0':truth(decision), 'agent1':Q(1,2)}
        rates = {'agent0':Q(world['suffix_rate']), 'agent1':Q(world['agent_B_rate'])}
        if row['arm'] != 'public_history':
            capture_path = BASE/'captures'/(name+'.json'); cap=load(capture_path)
            assert cap['source_kind'] == 'simulated_position_capture_not_production_AUTH'
            assert cap['world_binding'] == world['world_binding'] == public['world_binding']
            captured,delivered = Q(cap['captured']),Q(cap['delivered'])
            assert 0 <= captured <= delivered == decision
            assert Q(cap['progress']) == truth(captured)
            assert all(Q(s['end']) <= captured for s in cap['observed_prefix'])
            age = decision-captured
            assert age == (Q(0) if row['arm']=='position_age0' else Q(1,4))
            progress['agent0'] = min(Q(1),Q(cap['progress'])+age/duration['agent0'])
            projection=inp['prediction']['projection']
            assert Q(projection['lower']) == Q(cap['progress'])
            assert Q(projection['upper']) == min(Q(1),Q(cap['progress'])+age*Q(public['max_progress_rate']))
            assert Q(projection['lower']) <= actual['agent0'] <= Q(projection['upper'])
            assert not projection['safety_authority'] and not projection['finite_completion_upper']
            assert inp['prediction']['evidence_sha256'] == canonical_hash({k:v for k,v in cap.items() if k != 'observed_prefix'})
        assert inp['progress'] == {a:float(p) for a,p in progress.items()}
        before,after=load(case/'graph_before.json'),load(case/'graph_after.json')
        for vertex in before['vertices']:
            assert vertex['nominal_duration'] == float(duration[vertex['agent']])
            if vertex['status']=='IN_PROGRESS':
                assert vertex['index']==1 and vertex['progress']==float(progress[vertex['agent']])
        result=load(case/'result.json')
        registration = next(r for r in load(BASE/'REGISTRATION.json')['cases'] if r['name']==name)
        assert registration['input_sha256'] == sha(BASE/'inputs'/(name+'.json'))
        if result.get('reused_from'):
            source=BASE.parent/result['reused_from']
            assert result['input_sha256'] == load(source/'result.json')['input_sha256']
            assert load(source/'graph_before.json') == before
            assert load(source/'graph_after.json') == after
            assert sha(source/'result.json') == result['reuse_source_result_sha256']
            prior = next(r for r in load(HERE.parent/'r16_root_review/SADG_INDEPENDENT.json')['cases'] if r['case']==source.name)
            assert all(sha(source/f)==h for f,h in prior['source_hashes'].items())
            reused_models.append(name)
        else:
            assert result['input_sha256'] == sha(BASE/'inputs'/(name+'.json'))
            new_lp.append(model_audit.verify_case(case))
        rec=load(case/'suffix_receipt.json'); key=rec['execution_key']
        if key not in suffixes:
            suffixes[key]=physical.audit(name,actual,rates)
        else:
            assert rec['source_sha256']==suffixes[key]['suffix_sha256']
        checked=suffixes[key]
        assert Q(checked['sum_completion']) == Q(str(row['sum_completion_time']))
        assert Q(checked['makespan']) == Q(str(row['makespan']))
        assert Q(str(row['A_true_progress']))==actual['agent0']
        assert Q(str(row['A_true_remaining']))==(1-actual['agent0'])/rates['agent0']
        rows.append({'name':name,'input_sha256':sha(BASE/'inputs'/(name+'.json')),'case_result_sha256':sha(case/'result.json'),'sum_completion':checked['sum_completion'],'makespan':checked['makespan']})
    assert len(rows)==9 and len(new_lp)==1 and len(suffixes)==5 and len(reused_models)==8
    result={'passed':True,'rows':rows,'new_model_checks':new_lp,'reused_old_model_checks':reused_models,'unique_suffixes':suffixes,'new_author_calls':0,'new_execution_episodes':0,'scope':'Frozen synthetic two-agent histories, real author input and exact point-trajectory reconstruction; not LMAPF or paid sensing.'}
    (HERE/'SADG_CHAIN_INDEPENDENT.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'passed':True,'cases':len(rows),'new_independent_LPs':sum(len(x['assignments']) for x in new_lp),'unique_suffixes':len(suffixes)}))


if __name__ == '__main__':
    main()
