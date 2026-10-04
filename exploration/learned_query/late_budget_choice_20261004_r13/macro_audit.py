"""Independent public late-gate target features and fixed C/LD interpreter."""
from fractions import Fraction as F
from decimal import Decimal as D
OPTIONS=['C','LD']
def rank(c,x):return (-c.survival_probability(x['agent'],c.clock-x['launch'])*sum((F(1,cl['remaining_route_items']*cl['owners']) for cl in x['claims']),F(0)),x['agent'],x['move'])
def choice(c,e):
 assert not c.macro_name and c.policy!='WAIT','late macro selected more than once or WAIT gate'
 assert set(e)=={'event','at','policy','opportunity','initial_capacity','remaining_capacity','spent','target_agent','target_move','feature_schema','features','learned','margin_infinite','margin','scores','selected_option','inference_calls','inference_ns'}
 remaining=c.capacity-len(c.asked)
 assert remaining>0 and len(c.asked)>=c.capacity//2,'gate before half budget or without remaining budget'
 assert e['policy']==c.policy and e['opportunity']==c.decisions+1 and e['initial_capacity']==c.capacity
 assert e['remaining_capacity']==remaining and e['spent']==len(c.asked) and e['feature_schema']=='late_target10_v1'
 c.opps.update(key for key,m in c.moves.items() if abs(m['launch']+D('.75')-c.clock)<D('1e-60'))
 actual=c.candidates();assert actual;target=min(actual,key=lambda x:rank(c,x));assert (e['target_agent'],e['target_move'])==(target['agent'],target['move']),'late gate exact condition-rank target'
 inverse=sum((F(1,cl['remaining_route_items']*cl['owners']) for cl in target['claims']),F(0));p=target['features'][10];time=F(int(c.clock/D(8)*D(1000000)),16000000)
 features=[p,target['features'][0],target['features'][18],inverse,F(min(cl['remaining_route_items'] for cl in target['claims']),64),F(len(target['claims']),15),F(len(actual)-1,15),F(remaining,16),1-time,p*inverse]
 assert list(map(F,e['features']))==features,'independent ten public late target features'
 learned=c.policy in ['full','no_history_prob'];infinite=False;margin=F(0);scores=[dict(option=o,tasks=F(0),time=F(0),total=F(0)) for o in OPTIONS];selected=0
 if c.policy in ['alwaysLD','macro_LD']:selected=1
 elif c.policy=='budget_lookup':
  value=c.coefficients['budget_lookup_'+str(c.capacity)];assert len(value)==1 and value[0] in [0,1];selected=int(value[0])
 elif learned:
  threshold=c.coefficients['shared_margin'];assert len(threshold)==2 and threshold[0] in [0,1];infinite=bool(threshold[0]);margin=threshold[1];masked={0,9} if c.policy=='no_history_prob' else set()
  for head in ['tasks','time']:
   coef=c.coefficients[c.policy+'_LD_'+head];assert len(coef)==11
   scores[1][head]=coef[0]+sum((w*x for j,(w,x) in enumerate(zip(coef[1:],features)) if j not in masked),F(0))
  scores[1]['total']=scores[1]['tasks']+scores[1]['time'];selected=int(not infinite and scores[1]['total']>margin)
 else:assert c.policy in ['condition','macro_C']
 assert len(e['scores'])==2
 for row,expected in zip(e['scores'],scores):assert row['option']==expected['option'] and all(F(row[key])==expected[key] for key in ['tasks','time','total']),'exact frozen late scores'
 assert e['selected_option']==OPTIONS[selected] and e['learned']==learned and e['margin_infinite']==infinite and F(e['margin'])==margin,'late score/margin C tie'
 assert e['inference_calls']==int(learned) and isinstance(e['inference_ns'],int) and e['inference_ns']>=0
 c.macro_name=OPTIONS[selected];c.gate_features=features

def decision(c,e,actual,remaining):
 if c.policy=='WAIT':c.macro_name='W'
 elif not c.macro_name:assert not (remaining>0 and len(c.asked)>=c.capacity//2),'missing earliest qualifying late gate'
 assert e['macro']==c.macro_name and e['initial_capacity']==c.capacity,'pre-gate C metadata or selected complete tail'
 mode='WAIT' if c.macro_name=='W' else 'condition';index=0;eligible=[]
 first=c.macro_name=='LD' and c.pair_stage==0 and remaining>0;second=c.macro_name=='LD' and c.pair_stage==1 and remaining>0
 if first or second:
  choices=[x for x in actual if first or (x['agent'],x['move'])!=(c.anchor_agent,c.anchor_move)]
  if second:eligible=[x['move'] for x in choices]
  if choices:
   target=min(choices,key=lambda x:rank(c,x));mode='force_SKIP'+str(target['agent']);index=1 if first else 2;c.pair_stage=index
   if first:c.anchor_agent=target['agent'];c.anchor_move=target['move'];c.anchor_tasks={x['task'] for x in target['claims']}
 assert e['intervention_index']==index and e['pair_stage']==c.pair_stage,'late macro first/second stage'
 assert e['anchor_agent']==c.anchor_agent and e['anchor_move']==c.anchor_move and e['anchor_tasks']==sorted(c.anchor_tasks),'complete occurrence anchor binding'
 assert e['second_eligible']==eligible and e['head_lineage_count']==len(c.public_head_parent),'earliest distinct public second trigger'
 assert e['decision_mode']==mode,'condition prefix and fixed full-tail macro'
 return mode
