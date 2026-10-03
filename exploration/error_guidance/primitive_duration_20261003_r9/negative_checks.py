from pathlib import Path
import json,copy
import audit,mapping_replay as mapping
H=Path(__file__).resolve().parent;O=Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence')/H.name
s=next(x for x in json.loads((H/'runs.json').read_text())['runs'] if x['condition']=='unknown_pause' and x['execution']=='local');d=O/'runs'/s['id'];es=[json.loads(x) for x in (d/'events.jsonl').open()];ds=[json.loads(x) for x in (d/'decisions.jsonl').open()];layout=json.loads((H/'inputs'/s['input_id']/'map.json').read_text())['layout'];res={}
def reject(name,fn):
 try:fn()
 except (AssertionError,ValueError,KeyError):res[name]='rejected';return
 raise AssertionError(name+' accepted')
missing=[e for e in es if not(e['kind']=='end' and e['robot']=='0' and e['node']==1)];reject('removed_original_predecessor_END',lambda:audit.dependencies(missing,'local'))
reject('local_events_misclaimed_global',lambda:audit.dependencies(es,'global'))
filtered=[]
for e in es:
 if e['kind']=='control' and e['control']['phase'] not in ('front','service_decrement','pause'):continue
 filtered.append(dict(e,sequence=len(filtered)))
def replay(ev,de):mapping.check(ev,de,True,True,layout,4,300)
bad=copy.deepcopy(ds);bad[0]['calls'][1]['request']['mapf_instance']['goals'][0][0]['id']+=100000;reject('future_head_in_second_plan',lambda:replay(filtered,bad))
bad=copy.deepcopy(ds);bad[0]['calls'][1]['request']['mapf_instance']['starts'][0]['location']+=1;reject('forged_frontier',lambda:replay(filtered,bad))
bad=copy.deepcopy(filtered);e=next(e for e in bad if e['kind']=='end');e['goal'][0]+=1;reject('forged_normal_END_endpoint',lambda:replay(bad,ds))
bad=copy.deepcopy(filtered);e=next(e for e in bad if e['kind']=='control' and e['control']['phase']=='service_decrement');e['control']['timer']-=1;reject('shortened_STATION_dwell',lambda:replay(bad,ds))
bad=copy.deepcopy(filtered);e=next(e for e in bad if e['kind']=='parsed');e['actions'][0].append(dict(e['actions'][0][-1]));reject('duplicated_STATION_node',lambda:replay(bad,ds))
(H/'negative_checks.json').write_text(json.dumps({'all_rejected':True,'cases':res},indent=2)+'\n');print(res)
