"""Independent exact public gate aggregation and complete-macro interpreter."""
from fractions import Fraction as F
from decimal import Decimal as D
OPTIONS=['C','W','E','L','ED','LD']
def choice(c,e):
 assert not getattr(c,'macro_name','') and not c.asked and c.decisions==0,'macro selection must happen exactly once before any query'
 assert set(e)=={'event','at','policy','opportunity','initial_capacity','features','learned','margin_infinite','margin','scores','selected_option','inference_calls','inference_ns'}
 assert e['policy']==c.policy and e['opportunity']==1 and e['initial_capacity']==c.capacity
 c.opps.update(key for key,m in c.moves.items() if abs(m['launch']+D('.75')-c.clock)<D('1e-60'))
 actual=c.candidates();assert actual
 remaining=F(c.capacity,16);time=F(int(c.clock/D(8)*D(1000000)),16000000)
 fs=[r['features']+[remaining,time,remaining*r['features'][19],remaining*(1-time)] for r in actual]
 mean=[sum((f[j] for f in fs),F(0))/len(fs) for j in range(24)]+[F(len(actual),c.N)]
 assert list(map(F,e['features']))==mean,'public 25-dimensional gate means'
 learned=c.policy in ['full','nohistory','nobudget','tasks_only'];infinite=False;margin=F(0);scores=[dict(option=o,tasks=F(0),time=F(0),total=F(0)) for o in OPTIONS];selected=0
 if c.policy=='WAIT':selected=1
 elif c.policy.startswith('macro_'):selected=OPTIONS.index(c.policy[6:])
 elif c.policy=='budget_lookup':
  value=c.coefficients['budget_lookup_'+str(c.capacity)];assert len(value)==1 and value[0].denominator==1 and 0<=value[0]<6;selected=int(value[0])
 elif learned:
  threshold=c.coefficients['shared_margin'];assert len(threshold)==2 and threshold[0] in [0,1];infinite=bool(threshold[0]);margin=threshold[1];variant='full' if c.policy=='tasks_only' else c.policy
  masked=set(range(10,18)) if c.policy=='nohistory' else {20,22,23} if c.policy=='nobudget' else set()
  for k,option in enumerate(OPTIONS[1:],1):
   for head in ['tasks','time']:
    if head=='time' and c.policy=='tasks_only':continue
    coef=c.coefficients[variant+'_'+option+'_'+head];assert len(coef)==26
    scores[k][head]=coef[0]+sum((w*x for j,(w,x) in enumerate(zip(coef[1:],mean)) if j not in masked),F(0))
   scores[k]['total']=scores[k]['tasks']+scores[k]['time']
  qualified=[k for k in range(1,6) if not infinite and scores[k]['total']>margin]
  selected=min(qualified,key=lambda k:(-scores[k]['total'],k)) if qualified else 0
 else:assert c.policy=='condition'
 for r,expected in zip(e['scores'],scores):assert r['option']==expected['option'] and all(F(r[key])==expected[key] for key in ['tasks','time','total']),'exact frozen macro scores'
 assert len(e['scores'])==6 and e['selected_option']==OPTIONS[selected],'macro score/margin/fixed-order tie'
 assert e['learned']==learned and e['margin_infinite']==infinite and F(e['margin'])==margin
 assert e['inference_calls']==int(learned) and isinstance(e['inference_ns'],int) and e['inference_ns']>=0
 c.macro_name=OPTIONS[selected];c.initial_capacity=c.capacity;c.gate_features=mean
def decision(c,e,actual,remaining):
 assert e['macro']==c.macro_name and e['initial_capacity']==c.initial_capacity
 mode='WAIT' if c.macro_name=='W' else 'condition';index=0;eligible=[]
 early=c.macro_name in ['E','ED'];late=c.macro_name in ['L','LD'];twice=c.macro_name in ['ED','LD']
 first=(early or late) and c.pair_stage==0 and remaining>0 and (early or c.capacity-remaining>=c.capacity//2)
 second=twice and c.pair_stage==1 and remaining>0
 if first or second:
  choices=[x for x in actual if first or (x['agent'],x['move'])!=(c.anchor_agent,c.anchor_move)]
  if second:eligible=[x['move'] for x in choices]
  if choices:
   def rank(x):return (-c.survival_probability(x['agent'],c.clock-x['launch'])*sum((F(1,cl['remaining_route_items']*cl['owners']) for cl in x['claims']),F(0)),x['agent'],x['move'])
   target=min(choices,key=rank);mode='force_SKIP'+str(target['agent']);index=1 if first else 2;c.pair_stage=index
   if first:c.anchor_agent=target['agent'];c.anchor_move=target['move'];c.anchor_tasks={x['task'] for x in target['claims']}
 assert e['intervention_index']==index and e['pair_stage']==c.pair_stage,'macro first/second stage'
 assert e['anchor_agent']==c.anchor_agent and e['anchor_move']==c.anchor_move and e['anchor_tasks']==sorted(c.anchor_tasks),'full macro anchor binding'
 assert e['second_eligible']==eligible and e['head_lineage_count']==len(c.public_head_parent),'earliest public distinct-trigger candidate set'
 assert e['decision_mode']==mode,'fixed shared complete-macro tail'
 return mode
