"""Fixed public R3 contention fixture; prove adapter can change actual official actions."""
import os,json,subprocess
from common import HERE,NATIVE,sha,write
parent=HERE.parent/'gpibt_lsmart_active_20260930_r3/attempts/nominal/decisions.jsonl'
d=json.loads(parent.read_text().splitlines()[0]);req=d['request'];out={}
for name,bias in [('zero',[0.,0.]),('agent0',[2.,-2.]),('agent1',[-2.,2.])]:
 request=req|{'priority_bias':bias};env=os.environ.copy();env['GPIBT_R0_SEED']='42'
 p=subprocess.run(['rtk','proxy',str(NATIVE/'gpibt_bridge')],input=json.dumps(request)+'\n',text=True,capture_output=True,env=env,timeout=20)
 assert p.returncode==0,p.stderr
 result=json.loads(p.stdout);out[name]={'request':request,'result':result,'stderr':p.stderr}
assert len({tuple(v['result']['actions']) for v in out.values()})>1,'priority adapter did not change joint actions'
write(HERE/'interface_probe.json',{'status':'PASSED_REAL_OFFICIAL_ACTION_INFLUENCE','fixture_source_sha256':sha(parent),'bridge_sha256':sha(NATIVE/'gpibt_bridge'),'cases':out,'not_a_trajectory_run':True})
print(json.dumps({k:{'actions':v['result']['actions'],'order':v['result']['priority_adapter']['search_order']} for k,v in out.items()},indent=2))
