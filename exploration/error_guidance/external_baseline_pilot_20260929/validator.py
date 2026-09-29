"""Standalone independent trajectory + author roundrobin task replay."""
import collections,math
class InvalidTrace(Exception):pass
def need(c,m):
 if not c:raise InvalidTrace(m)
def validate(grid,start_ids,task_source,data,expected_agents,horizon=450):
 h,w=len(grid),len(grid[0]);n=expected_agents
 starts=[tuple(p[:2]) for p in data['start']]
 need(starts==[divmod(x,w) for x in start_ids[:n]],'start differs from author input')
 actions=[p.split(',') for p in data['actualPaths']]
 need(len(actions)==n and all(len(p)==horizon for p in actions),'incomplete action matrix')
 directions={'R':(0,1),'D':(1,0),'L':(0,-1),'U':(-1,0),'W':(0,0)}
 def check_state(state,t):
  need(len(set(state))==n,f'vertex conflict t={t}')
  for a,(r,c) in enumerate(state):
   need(0<=r<h and 0<=c<w,f'out of bounds a={a} t={t}')
   need(grid[r][c] not in '@T',f'obstacle a={a} t={t}')
 positions=starts[:];check_state(positions,0);events=[[] for _ in range(n)];pending=[None]*n;counter=[0]*n;tasks=[];stream=[];flow=[];curve=[0];assign_time={}
 def assign(a,t):
  location=task_source[(counter[a]*n+a)%len(task_source)];goal=divmod(location,w);tid=len(tasks)
  need(0<=goal[0]<h and 0<=goal[1]<w and grid[goal[0]][goal[1]] not in '@T','bad source goal')
  tasks.append([tid,*goal]);pending[a]=(tid,goal);counter[a]+=1;assign_time[tid]=t;events[a].append([tid,t,'assigned']);stream.append((t,'assigned',a,tid))
 for a in range(n):assign(a,0)
 for t in range(1,horizon+1):
  nxt=[]
  for a,(r,c) in enumerate(positions):
   symbol=actions[a][t-1];need(symbol in directions,f'unknown action {symbol}')
   dr,dc=directions[symbol];p=(r+dr,c+dc);need(abs(dr)+abs(dc)<=1,'nonadjacent transition');nxt.append(p)
  check_state(nxt,t)
  edges={}
  for a,(old,new) in enumerate(zip(positions,nxt)):
   need((new,old) not in edges,f'reverse edge conflict t={t} a={a}')
   edges[(old,new)]=a
  positions=nxt
  for a,position in enumerate(positions):
   tid,goal=pending[a]
   if position==goal:
    flow.append(t-assign_time[tid]);events[a].append([tid,t,'finished']);stream.append((t,'finished',a,tid));pending[a]=None
  for a in range(n):
   if pending[a] is None:assign(a,t)
  curve.append(len(flow))
 need(data['events']==events,'task events disagree with actual positions')
 need(data['tasks']==tasks,'task list disagrees with original roundrobin source')
 need(data['numTaskFinished']==len(flow),'completion total mismatch')
 need(len(data['plannerTimes'])==horizon,'planning times incomplete')
 censored=[horizon-assign_time[item[0]] for item in pending if item is not None]
 ordered=sorted(flow);p95=ordered[math.ceil(.95*len(ordered))-1] if ordered else None
 return {'status':'passed','agents':n,'horizon':horizon,'actions_replayed':n*horizon,'positions_checked':n*(horizon+1),'joint_state_checks':horizon+1,'directed_edge_lookup_checks':n*horizon,'boundary_obstacle_adjacency_vertex_reverse_edge_violations':0,'completed_tasks':len(flow),'assigned_tasks':len(tasks),'pending_tasks':len(censored),'completed_task_flow_sum':sum(flow),'completed_task_flow_mean':sum(flow)/len(flow) if flow else None,'completed_task_flow_p95_nearest_rank':p95,'pending_restricted_flow_sum':sum(censored),'all_assigned_restricted_flow_sum':sum(flow)+sum(censored),'cumulative_completed_tasks':curve,'action_counts':dict(collections.Counter(x for p in actions for x in p)),'event_stream':stream,'upstream_AllValid_or_errors_used':False}
