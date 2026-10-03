"""Offline diagnostic of actual persistent-action lifetimes and conserved count budget."""
from fractions import Fraction as Q
import json
import runner,verify_matched_tail as matched
P=runner.HERE
def mid(row):return Q(row['at']['lower']+row['at']['upper'],2000000)
def main():
 episodes=[json.loads(p.read_text()) for p in (P/'runs').glob('*.receipt.json')];em={(e['world'],e['policy']):e for e in episodes};result=[];concurrent=[]
 for e in episodes:
  rs=matched.rows(e);concurrent.append(max((len(x['skip_state']) for x in rs if x['event']=='public_candidate_visibility'),default=0))
  for idx,install in [(i,x) for i,x in enumerate(rs) if x['event']=='public_SKIP_installed']:
   move=install['id'];agent=int(move.split('-')[1]);pair=[agent,move];decision=next(x for x in reversed(rs[:idx]) if x['event']=='actor_decision');assert decision['selected_kind']=='SKIP' and decision['selected']==move
   ended=next((x for x in rs[idx:] if x['event']=='public_END_delivered' and x['move']==move),None);physical=next((x for x in rs if x['event']=='physical_original_END' and x['id']==move),None);clear=next((x for x in rs[idx:] if x['event']=='public_SKIP_cleared_normal_END' and x['id']==move),None)
   assert (clear is None)==(ended is None)
   if clear:assert clear['at']==ended['at'] and mid(clear)>mid(physical) and rs.index(clear)==rs.index(ended)+1
   through=rs[idx:rs.index(clear) if clear else len(rs)]
   offered=[x for x in through if x['event']=='public_candidate_visibility'];raw=[x for x in offered if pair in x['raw_candidates']];assert all(pair in x['skip_state'] and pair not in x['visible_candidates'] for x in offered)
   assert not any(x['event']=='certified_POSITION_committed' and x['move']==move for x in rs)
   later=[c[1] for x in rs[(rs.index(clear)+1 if clear else len(rs)):] if x['event']=='public_candidate_visibility' for c in x['visible_candidates'] if c[0]==agent and int(c[1].split('-')[2])>int(move.split('-')[2])]
   base=matched.rows(em[e['world'],'condition']);baseline_queries={x['move'] for x in base if x['event']=='certified_POSITION_committed'};actual=[x for x in rs if x['event']=='certified_POSITION_committed'];extra=[x['move'] for x in actual if x['move'] not in baseline_queries]
   result.append(dict(world=e['world'],policy=e['policy'],agent=agent,move=move,opportunity=decision['opportunity'],installed=install['at'],physical_END=physical['at'] if physical else None,accepted_END=ended['at'] if ended else None,cleared=clear['at'] if clear else None,lifetime=str(mid(clear)-mid(install)) if clear else None,raw_reappearances=len(raw),visibility_events_while_skipped=len(offered),same_agent_later_visible_occurrences=sorted(set(later)),remaining_immediately_after=decision['remaining_capacity'],remaining_at_clear=(16-sum(x['event']=='certified_POSITION_committed' for x in rs[:rs.index(clear)])) if clear else None,first_later_query=next((dict(move=x['move'],at=x['at']) for x in rs[idx:] if x['event']=='certified_POSITION_committed'),None),same_occurrence_query_count=0,total_queries=len(actual),baseline_queries=len(baseline_queries),queries_of_new_occurrences=extra,fewer_total_queries_than_condition=e['summary']['queries']<em[e['world'],'condition']['summary']['queries']))
 runner.write(P/'SKIP_LIFETIMES.json',dict(passed=True,max_simultaneous_skip_bindings=max(concurrent),episodes_with_two_simultaneous_skips=sum(n>=2 for n in concurrent),installed=len(result),cleared_at_accepted_END=sum(r['cleared'] is not None for r in result),raw_reappearances=sum(r['raw_reappearances'] for r in result),with_later_same_agent_visible=sum(bool(r['same_agent_later_visible_occurrences']) for r in result),with_new_queried_occurrences=sum(bool(r['queries_of_new_occurrences']) for r in result),episodes=result));print('verified persistent SKIP lifetimes',len(result))
if __name__=='__main__':main()
