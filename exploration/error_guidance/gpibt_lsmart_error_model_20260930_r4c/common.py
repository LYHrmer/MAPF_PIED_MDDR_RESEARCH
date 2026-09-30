"""Shared causal forecast interface. No private observation fields are read here."""
from pathlib import Path
import hashlib,json,math,statistics
HERE=Path(__file__).resolve().parent
NATIVE=Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence/gpibt_lsmart_error_model_20260930_r4c')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(path,value):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    Path(path).write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')
def events(path):return [json.loads(x) for x in Path(path).read_text().splitlines() if x]
def public_steps(es):
    """Construct original grid steps from delivered proposal/admit/command/END only."""
    steps={};nodes={};pid=None
    for e in es:
        k=e['kind']
        if k=='proposal':
            pid=e['proposal']['proposal_id']
            for a,p in enumerate(e['proposal']['plan']):
                start=[-p[0][0],-p[0][1]];goal=[-p[1][0],-p[1][1]]
                steps[(pid,str(a))]={'proposal_id':pid,'agent':str(a),'proposal_tick':e['tick'],'start':start,'goal':goal,
                    'axis':int(start[1]!=goal[1]),'length':math.dist(start,goal),'first_command_tick':None,
                    'final_node':None,'end_tick':None,'end_sequence':None,'command_speeds':[],'zero_command_ticks':[]}
        elif k=='admit':
            for a in e['actions']:
                if a[3]=='M':
                    s=steps[(pid,e['robot'])];nodes[(e['robot'],a[1])]=(pid,e['robot'])
                    if [-a[5][1],-a[5][0]]==s['goal']:s['final_node']=a[1]
        elif k=='control' and e['control']['phase']=='wheel_command' and pid is not None:
            c=e['control'];s=steps[(pid,e['robot'])]
            if c['type']==0 and s['length']>0:
                speed=(abs(c['issued_left_cm_s'])+abs(c['issued_right_cm_s']))/2
                if speed>0:
                    if s['first_command_tick'] is None:s['first_command_tick']=e['tick']
                    s['command_speeds'].append(speed)
                else:s['zero_command_ticks'].append(e['tick'])
        elif k=='end' and (e['robot'],e['node']) in nodes:
            s=steps[nodes[(e['robot'],e['node'])]]
            if e['node']==s['final_node']:
                s['end_tick']=e['tick'];s['end_sequence']=e['sequence']
    out=[]
    for s in steps.values():
        if s['length']==0:continue
        s['duration']=s['end_tick']-s['first_command_tick'] if s['end_tick'] is not None and s['first_command_tick'] is not None else None
        out.append(s)
    return out
def context(es):
    completed=[]
    for s in public_steps(es):
        if s['duration'] is not None:
            completed.append({k:s[k] for k in ('proposal_id','agent','axis','length','first_command_tick','end_tick','end_sequence','duration')}|
                {'max_command_cm_s':max(s['command_speeds'],default=0),'mean_command_cm_s':statistics.mean(s['command_speeds']) if s['command_speeds'] else 0,
                 'past_zero_command_ticks':len(s['zero_command_ticks'])})
    return {'freeze_sequence':es[-1]['sequence'] if es else -1,'completed_steps':completed}
def analytic(v=200.,distance=100.,accel=200.):
    v=max(10.,float(v));ramp=v*v/accel
    secs=2*math.sqrt(distance/accel) if distance<=ramp else 2*v/accel+(distance-ramp)/v
    return math.ceil(10*secs)+10
FEATURES=['analytic_ticks','agent_median','axis_median','last_duration','max_command_cm_s','mean_command_cm_s','same_last_axis','history_count','axis']
def features(ctx,agent,axis):
    hs=[s for s in ctx['completed_steps'] if s['agent']==str(agent)][-6:]
    matched=[s for s in hs if s['axis']==axis][-3:]
    base=analytic(hs[-1]['max_command_cm_s'] if hs else 200)
    am=statistics.median([s['duration'] for s in hs[-3:]]) if hs else base
    xm=statistics.median([s['duration'] for s in matched]) if matched else am
    last=hs[-1] if hs else None
    return [base,am,xm,last['duration'] if last else base,last['max_command_cm_s'] if last else 200,
            last['mean_command_cm_s'] if last else 100,int(bool(last and last['axis']==axis)),len(hs),axis]
def predict(x,policy,model=None):
    if policy in ('zero','analytic','fixed_agent0','fixed_agent1'):y=x[0]
    elif policy=='history':y=x[2]
    else:
        y=x[0]+model['intercept']+sum(c*(v-m)/s for c,v,m,s in zip(model['coefficients'],x,model['mean'],model['scale']))
    return min(120.,max(5.,float(y)))
def axes(view,agent,layout):
    inst=view['mapf_instance'];s=inst['starts'][agent]['location'];g=inst['goals'][agent][0]['location']
    if s==g:return []
    dist={g:0};todo=[g]
    for cell in todo:
        for d in [1,5,-1,-5]:
            t=cell+d
            if 0<=t<25 and abs(t//5-cell//5)+abs(t%5-cell%5)==1 and layout[t//5][t%5]!='@' and t not in dist:
                dist[t]=dist[cell]+1;todo.append(t)
    best=[]
    for d in [1,5,-1,-5]:
        t=s+d
        if 0<=t<25 and abs(t//5-s//5)+abs(t%5-s%5)==1 and layout[t//5][t%5]!='@' and dist.get(t,100)<dist.get(s,100):best.append(int(d in (1,-1)))
    assert best,'no public goal-decreasing neighbor'
    return sorted(set(best))
def forecast(ctx,view,layout,policy,model,amplitude):
    predicted=[];fs=[]
    for a in range(2):
        aa=axes(view,a,layout);rows=[features(ctx,a,axis) for axis in aa]
        fs.append([{'axis':axis,'features':row,'predicted_ticks':predict(row,policy,model)} for axis,row in zip(aa,rows)])
        predicted.append(statistics.mean([r['predicted_ticks'] for r in fs[-1]]) if rows else 20.)
    mean=statistics.mean(predicted)
    bias=([1.,-1.] if policy=='fixed_agent0' else [-1.,1.]) if policy.startswith('fixed_agent') else ([0.,0.] if policy=='zero' or abs(predicted[0]-predicted[1])<1.0 else ([amplitude,-amplitude] if predicted[0]>predicted[1] else [-amplitude,amplitude]))
    return {'policy':policy,'amplitude':amplitude,'predicted_ticks':predicted,'bias':bias,'axis_features':fs,'context':ctx}
