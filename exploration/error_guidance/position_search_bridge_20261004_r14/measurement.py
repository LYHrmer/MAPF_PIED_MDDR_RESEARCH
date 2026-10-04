"""Trusted local simulation measurement boundary; never a main guest certificate."""
from fractions import Fraction as F
from bridge import Executor,DOMAIN,digest

def issue(snapshot,checkpoint_sha,request):
 engine=Executor.restore(snapshot);assert request['domain']==DOMAIN and F(request['captured_at'])==engine.t
 a=request['agent'];r=engine.ag[a];assert 'active' in r
 s,t,o,d=r['active'];assert request['from_state']==s and request['to_state']==t and request['origin']==list(o) and request['destination']==list(d)
 at=engine.t
 pieces=[v for v in engine.segments if v['agent']==a and F(v['t0'])<=at<=F(v['t1'])]
 assert pieces,'no current measurement segment';v=pieces[-1]
 t0,t1=F(v['t0']),F(v['t1']);p0,p1=list(map(F,v['p0'])),list(map(F,v['p1']))
 fraction=(at-t0)/(t1-t0) if t1>t0 else F(0)
 point=[x+fraction*(y-x) for x,y in zip(p0,p1)]
 alpha=sum((x-F(u))*(F(w)-F(u)) for x,u,w in zip(point,o,d))
 body={'domain':DOMAIN,'source':'synthetic_position_measurement','request':request,
       'captured_at':str(at),'delivered_at':str(at),'position':list(map(str,point)),
       'progress_lower':str(alpha),'progress_upper':str(alpha),'request_count':1,'production_cost':None}
 receipt={'source':'synthetic_position_measurement','checkpoint_sha256':checkpoint_sha,
          'request_sha256':digest(request),'body_sha256':digest(body),'production_cost':None,
          'scope':'trusted local issue receipt, not cryptographic or production guest authentication'}
 return body,receipt
