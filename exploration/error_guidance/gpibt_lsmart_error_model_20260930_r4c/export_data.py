"""Separate causal delivered inputs and full original-MOVE supervision, whole-run split."""
from common import HERE,sha,events,public_steps,features,predict,write
import json,math
def export(runid):
 dst=HERE/'attempts'/runid;es=events(dst/'events.jsonl');ds=events(dst/'decisions.jsonl')
 spec=json.loads((dst/'receipt.json').read_text())['run_spec'];steps=public_steps(es);rows=[];labels=[]
 dispatch={};pid=None
 for e in es:
  if e['kind']=='proposal':pid=e['proposal']['proposal_id']
  elif e['kind']=='admit' and e['actions']:dispatch.setdefault((pid,e['robot']),e['tick'])
 for s in steps:
  d=ds[s['proposal_id']];ctx=d['forecast']['context'];x=features(ctx,s['agent'],s['axis'])
  key=f"{runid}:p{s['proposal_id']}:a{s['agent']}"
  rows.append({'key':key,'split':spec['split'],'run_id':runid,'proposal_id':s['proposal_id'],'agent':s['agent'],'axis':s['axis'],
               'freeze_sequence':ctx['freeze_sequence'],'features':x,'context':ctx,'visibility':'delivered_public_commands_END_only'})
  labels.append({'key':key,'visibility':'offline_supervision_only','original_start_xy_m':s['start'],'original_goal_xy_m':s['goal'],'original_length_m':s['length'],
                 'first_nonzero_command_tick':s['first_command_tick'],'final_native_MOVE_node':s['final_node'],'normal_full_MOVE_END_tick':s['end_tick'],
                 'duration_ticks':s['duration'],'right_censored':s['duration'] is None,'horizon_ticks':800,
                 'proposal_received_tick':s['proposal_tick'],'first_native_dispatch_tick':dispatch.get((s['proposal_id'],s['agent'])),
                 'proposal_to_whole_MOVE_END_ticks':s['end_tick']-s['proposal_tick'] if s['end_tick'] is not None else None,
                 'first_dispatch_to_whole_MOVE_END_ticks':s['end_tick']-dispatch[(s['proposal_id'],s['agent'])] if s['end_tick'] is not None and (s['proposal_id'],s['agent']) in dispatch else None,
                 'proposal_to_first_nonzero_MOVE_gap_ticks':s['first_command_tick']-s['proposal_tick'] if s['first_command_tick'] is not None else None})
 out=HERE/'datasets'/runid;out.mkdir(parents=True,exist_ok=False)
 for name,data in [('delivered_context.jsonl',rows),('offline_original_MOVE_targets.jsonl',labels)]:
  (out/name).write_text(''.join(json.dumps(r,sort_keys=True,allow_nan=False)+'\n' for r in data))
 # Per-tick remaining labels refer to the same full-step final node; not half-ACK.
 by={(s['proposal_id'],s['agent']):s for s in steps};pid=None;active=[];target=[]
 for e in es:
  if e['kind']=='proposal':pid=e['proposal']['proposal_id']
  if e['kind']!='control' or e['control']['phase']!='wheel_command' or (pid,e['robot']) not in by:continue
  s=by[(pid,e['robot'])];c=e['control'];t=e['tick'];seen_first=s['first_command_tick'] is not None and s['first_command_tick']<=t
  d=ds[pid];x=features(d['forecast']['context'],e['robot'],s['axis']);elapsed=t-s['first_command_tick'] if seen_first else 0
  key=f'{runid}:s{e["sequence"]}'
  active.append({'key':key,'run_id':runid,'split':spec['split'],'agent':e['robot'],'tick':t,'freeze_sequence':e['sequence'],
    'features':x,'elapsed_from_delivered_first_MOVE_command_ticks':elapsed,'first_command_already_delivered':seen_first,
    'issued_left_cm_s':c['issued_left_cm_s'],'issued_right_cm_s':c['issued_right_cm_s'],'active_nodes':c['nodes'],
    'information_scope':'step_start_public_history_plus_already_delivered_current_commands','used_by_active_planner':False})
  target.append({'key':key,'visibility':'offline_supervision_only','normal_full_MOVE_END_tick':s['end_tick'],
    'remaining_ticks':max(0,s['end_tick']-t) if s['end_tick'] is not None else None,'END_already_delivered':bool(s['end_sequence'] is not None and s['end_sequence']<e['sequence']),
    'right_censored':s['end_tick'] is None,'original_start_xy_m':s['start'],'original_goal_xy_m':s['goal'],'final_native_MOVE_node':s['final_node']})
 for name,data in [('active_delivered_context.jsonl',active),('offline_remaining_targets.jsonl',target)]:
  (out/name).write_text(''.join(json.dumps(r,sort_keys=True,allow_nan=False)+'\n' for r in data))
 write(out/'manifest.json',{'run_spec':spec,'raw_sha256':sha(dst/'events.jsonl'),'decision_sha256':sha(dst/'decisions.jsonl'),
  'files':{p.name:sha(p) for p in out.iterdir() if p.is_file()},'original_steps':len(rows),'uncensored_steps':sum(l['duration_ticks'] is not None for l in labels),'active_context_rows':len(active)})
 return rows,labels
if __name__=='__main__':
 import sys
 for name in sys.argv[1:]:
  rows,labels=export(name);print(name,len(rows),sum(l['duration_ticks'] is not None for l in labels))
