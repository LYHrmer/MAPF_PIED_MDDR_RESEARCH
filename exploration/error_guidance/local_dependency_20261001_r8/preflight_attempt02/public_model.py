from public_model_parent import *
class PublicHistory(PublicHistory):
 def accept(self,e):
  allowed={'view':{'kind','tick','sequence','view'},'proposal':{'kind','tick','sequence','proposal'},'admit':{'kind','tick','sequence','robot','actions'},'end':{'kind','tick','sequence','robot','node','accepted'}}
  assert set(e)==allowed[e['kind']] and e['sequence']>self.last_sequence
  self.last_sequence=e['sequence'];self.projected.append(e);k=e['kind']
  if k=='view':self.last_view=e['view']
  elif k=='proposal':
   self.pid=pid=e['proposal']['proposal_id'];inst=self.last_view['mapf_instance']
   for a,path in enumerate(e['proposal']['plan']):
    ori=inst['starts'][a]['orientation']
    for step,(s,t) in enumerate(zip(path,path[1:])):
     delta=(t[0]-s[0],t[1]-s[1])
     if delta==(0,0):continue
     d={(0,1):0,(1,0):1,(0,-1):2,(-1,0):3}[delta];turns=turn_count(ori,d);ori=d
     self.moves[(pid,a,step)]={'proposal_id':pid,'agent':a,'logical_step':step,'direction':d,'turns':turns,'proposal_tick':e['tick'],'start':[s[1],s[0]],'goal':[t[1],t[0]],'features':feature(self.rows,a,d,turns),'history_cutoff_sequence':e['sequence'],'duration':None,'final_node':None}
  elif k=='admit':
   a=int(e['robot'])
   for c in e['actions']:
    if c[3]!='M':continue
    matches=[r for key,r in self.moves.items() if key[:2]==(self.pid,a) and r['final_node'] is None and c[5]==r['goal']]
    if matches:
     r=min(matches,key=lambda x:x['logical_step']);r['final_node']=c[1];self.node_moves[(a,c[1])]=r
  elif k=='end':
   r=self.node_moves.get((int(e['robot']),e['node']))
   if r:
    assert e['accepted'] and r['duration'] is None
    r['duration']=e['tick']-r['proposal_tick'];r['end_tick']=e['tick'];r['end_sequence']=e['sequence']
    assert r['duration']>0 and r['end_sequence']>r['history_cutoff_sequence'];self.rows.append(dict(r))
