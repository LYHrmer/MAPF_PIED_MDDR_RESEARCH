from pathlib import Path
import json,tempfile,copy
import runner,audit_all
P=runner.HERE
def first(rows,event,predicate=lambda r:True):return next(r for r in rows if r['event']==event and predicate(r))
def main():
 reg=json.loads((P/'REGISTRATION.json').read_text());worlds={w['name']:w for w in reg['worlds']};receipts=[json.loads(p.read_text()) for p in (P/'runs').glob('*.receipt.json')];valid=[e for e in receipts if e['error'] is None]
 probe=next(e for e in valid if e['policy'].startswith('probe_') and e['summary']['queries']);paced=next(e for e in valid if e['policy']=='paced_condition');random=next(e for e in valid if e['world'].startswith('random-') and e['policy']=='WAIT');cases=[]
 def add(name,e,mutate):cases.append((name,e,mutate))
 def future(rs,ps):first(rs,'planner_request')['goals'][0]['id']+=1
 def features(rs,ps):first(rs,'actor_decision')['candidates'][0]['features'][10]='999'
 def missing(rs,ps):first(rs,'actor_decision')['candidates'].pop()
 def budget(rs,ps):first(rs,'actor_decision')['remaining_capacity']+=1
 def certificate(rs,ps):first(rs,'certified_POSITION_committed')['certified_lower']['lower']+=100000
 def dependency(rs,ps):first(rs,'official_move_committed')['dependency_departure_started']='m-999-0'
 def service(rs,ps):first(rs,'task_service')['goal'][0]+=1
 def pace(rs,ps):
  spent=0
  for r in rs:
   if r['event']=='actor_decision':
    allowance=min(16,4*(1+int(r['at']['lower']//32000000)))
    if spent>=allowance and spent<16 and allowance<16 and not r['selected'] and any(float(__import__('fractions').Fraction(c['score']))>0 for c in r['candidates']):r['selected']=r['candidates'][0]['move'];return
    spent+=bool(r['selected'])
  raise AssertionError('no exhausted pacing gate found')
 def obstacle(rs,ps):
  w=worlds[random['world']]
  for z in ps:
   for i,at in enumerate(z['request']['starts']):
    x,y=at%w['cols'],at//w['cols']
    for a,(dx,dy) in enumerate([(1,0),(0,1),(-1,0),(0,-1)]):
     if 0<=x+dx<w['cols'] and 0<=y+dy<w['rows'] and w['layout'][y+dy][x+dx]=='@':z['result']['actions'][i]=a;return
  raise AssertionError('no adjacent obstacle')
 for name,func in [('future_head',future),('history_feature',features),('missing_candidate',missing),('capacity',budget),('certificate',certificate),('dependency',dependency),('true_service',service)]:add(name,probe,func)
 add('pacing_gate',paced,pace);add('obstacle',random,obstacle);results=[]
 with tempfile.TemporaryDirectory(prefix='query-r8-neg-') as td:
  for name,e,mutate in cases:
   rs=[json.loads(x) for x in Path(e['raw']).read_text().splitlines()];ps=[json.loads(x) for x in Path(e['planner']).read_text().splitlines()];mutate(rs,ps);fake=copy.deepcopy(e)
   for key,data in [('raw',rs),('planner',ps)]:
    p=Path(td)/(name+'.'+key+'.jsonl');p.write_text(''.join(json.dumps(r)+'\n' for r in data));fake[key]=str(p);fake[key+'_sha256']=runner.sha(p)
   try:audit_all.check(fake,worlds[e['world']])
   except AssertionError as exc:results.append(dict(case=name,rejected=True,reason=str(exc)))
   else:raise AssertionError('negative control accepted '+name)
 runner.write(P/'NEGATIVE_CONTROLS.json',dict(passed=True,cases=results));print(json.dumps(results,indent=2),flush=True)
if __name__=='__main__':main()
