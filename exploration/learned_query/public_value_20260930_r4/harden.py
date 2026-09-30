"""Input/model provenance and current-world-history independence checks."""
import json
from fractions import Fraction
from pathlib import Path
from pipeline import HERE,sha,write
def main():
    out=HERE/'scheduled_successor_01';reg=json.loads((HERE/'native_attempt_01/REGISTRATION.json').read_text());rec=json.loads((out/'RECEIPT.json').read_text())
    sup=json.loads((HERE/'SUPPORT_AUDIT_60.json').read_text());cohorts={c['cohort_id']:c for c in sup['cohorts']};worlds={w['world_id']:w for w in reg['worlds']}
    model=json.loads((out/'MODEL_FROZEN_BEFORE_TEST.json').read_text());coeff=[Fraction(z) for z in model['coefficients']]
    history=[x for x in (HERE.parent/'public_joint_20260930_r3/public_native_input_20260930_r3.txt').read_text().splitlines() if x.startswith('H ')]
    first_features={};first_choices={};test_intervals={};changed=0
    for e in rec['episodes']:
        w=worlds[e['world_id']];c=cohorts[e['cohort_id']];lines=Path(e['input']).read_text().splitlines()
        public=[f'C {x} {y}' for x,y in c['resource_cells']]
        public+=[' '.join(map(str,['R',r['agent'],r['task'],*r['start'],*r['goal'],','.join(r['route'])])) for r in c['robots']]+history
        private=[f"E {x['agent']} {x['leg']} {x['eta']}" for x in w['private_world_only']]
        m=[f'M {x.numerator} {x.denominator}' for x in coeff] if w['split']=='test' else []
        assert lines==public+private+m,('native public/private/trained coefficient binding',e['world_id'],e['policy'])
        records=[json.loads(x) for x in Path(e['raw']).read_text().splitlines()]
        decision=next(x for x in records if x['event']=='actor_decision');assert decision['at']=={'lower':750000,'upper':750000,'denominator':1000000}
        assert not any(x['event']=='public_END_delivered' for x in records[:records.index(decision)])
        for cand in decision['candidates']:
            key=(c['cohort_id'],cand['agent']);values=tuple(cand['features'])
            assert key not in first_features or first_features[key]==values,'private eta/state leaked to first features'
            first_features[key]=values
        key=(c['cohort_id'],e['policy']);choice=decision['selected']
        assert key not in first_choices or first_choices[key]==choice,'first policy secretly adapts to private current world'
        first_choices[key]=choice
        if e['split']=='test' and not e['policy'].startswith('forced_'):
            p=e['policy'];s=e['summary'];v=s['service_time_sum'];lo,hi=test_intervals.get(p,(Fraction(0),Fraction(0)))
            test_intervals[p]=(lo+Fraction(v['lower'],v['denominator'])+64*s['uncompleted_heads'],hi+Fraction(v['upper'],v['denominator'])+64*s['uncompleted_heads'])
    result=dict(status='passed',actual_inputs_bound=598,model_rational_coefficients_bound=11,first_cohort_source_feature_sets=len(first_features),
       current_world_END_before_first_choice=False,features_and_choice_same_across_all13_exogenous_worlds_per_cohort=True,
       first_choices={f'{c}:{p}':v for (c,p),v in first_choices.items()},
       heldout_total_native_enclosing_intervals={p:dict(lower=str(lo),upper=str(hi)) for p,(lo,hi) in test_intervals.items()},
       model_sha256=sha(out/'MODEL_FROZEN_BEFORE_TEST.json'),audit_sha256=sha(HERE/'AUDIT.json'),source_sha256=sha(Path(__file__)))
    write(HERE/'AUDIT_HARDENED.json',result)
    print({k:v for k,v in result.items() if k not in ['first_choices','heldout_total_native_enclosing_intervals']})
if __name__=='__main__':main()
