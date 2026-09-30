"""Read-only exact interval audit of all declared capacity decisions and task events."""
from fractions import Fraction
from objective_task_recovery_audit import candidate_forecast, exact_time


def require(value, message):
    if not value:
        raise ValueError(message)


def audit_block(block, models):
    begin, result = block[0], block[-1]
    capacity, ab, ct = begin['capacity'], begin['ab_tail'], begin['c_tail']
    policy = begin['policy']
    scored = policy in ('current_cohort_flow_pair', 'nominal_completion_pair_window6')
    launches, queries, data, candidates, context = {}, [], None, [], None
    expected_action, decisions, active_terms, candidate_count = None, 0, 0, 0
    for event in block:
        kind = event['event']
        if kind == 'original_move_started' and decisions < 2 and scored:
            launches[event['id']] = exact_time(event['at'])
        elif kind == 'budget_context':
            context = event
            require(event['capacity'] == capacity and event['used'] == len(queries)
                    and event['remaining'] == capacity-len(queries), 'capacity accounting')
        elif kind == 'cohort_input':
            require(scored and data is None and expected_action is None, 'input order')
            data, candidates = event, []
            require(data['alpha'] == models[begin['predictor']], 'frozen predictor changed')
            opportunities = ['5/2', '11/4'] if decisions == 0 else ['11/4']
            require(data['opportunities'] == opportunities and data['at'] == opportunities[0], 'opportunities changed')
            require(data['eligible_actions'] == [a for a in 'ABC' if a not in queries], 'eligible query history')
            require([t['task'] for t in data['tasks']] == ['D1-task1','D2-task1','D3-task1'], 'future/missing tasks')
            for task in data['tasks']:
                key = task['demand']
                tail = ct if key == 'D3' else ab
                require(list(map(Fraction,task['lengths'])) == [Fraction(4 if key=='D3' else 6)]+([Fraction(1)] if tail else []), 'public task route')
                require(task['assigned_at'] == '0', 'assignment leaked')
                require(task['active'] == (key in launches), 'active differs from public grant')
                require(Fraction(task['launched']) == launches.get(key, Fraction(0)), 'launch time differs')
                required = [] if task['active'] else [a for a in ('C' if key=='D3' else 'AB') if a not in queries]
                require([r['action'] for r in task['relations']] == required, 'committed relation differs')
                active_terms += int(task['active'])
        elif kind == 'cohort_candidate':
            require(data is not None, 'candidate without input')
            expected = candidate_forecast(data, event['sequence'])
            require({k:v for k,v in event.items() if k!='event'} == expected, 'exact forecast differs')
            require(sum(bool(a) for a in event['sequence']) <= context['remaining'], 'infeasible capacity candidate')
            candidates.append(expected)
            candidate_count += 1
        elif kind == 'budget_candidate_score':
            require(candidates and 'window_count' not in candidates[-1], 'window score order')
            expected = sum(term['feasible'] and not task['active']
                           and Fraction(term['predicted_service_at']) <= Fraction(data['at'])+6
                           for task,term in zip(data['tasks'],candidates[-1]['terms']))
            require(event['window_count'] == expected, 'window completion score differs')
            candidates[-1]['window_count'] = expected
        elif kind == 'cohort_choice':
            keys = ['']+data['eligible_actions']
            sequences = ([[a] for a in keys] if len(data['opportunities'])==1 else
                         [[a,b] for a in keys for b in keys if not a or a!=b])
            sequences = [s for s in sequences if sum(bool(a) for a in s) <= context['remaining']]
            require([c['sequence'] for c in candidates] == sequences, 'incomplete candidate enumeration')
            feasible = [c for c in candidates if c['feasible']]
            def score(c):
                primary = Fraction(c['flow']) if policy=='current_cohort_flow_pair' else -c['window_count']
                return primary, sum(bool(a) for a in c['sequence'])
            winner = min(feasible,key=score)
            require(event['sequence']==winner['sequence'] and event['flow']==winner['flow']
                    and event['window_count']==winner['window_count']
                    and event['diagnostic_query_count']==sum(bool(a) for a in winner['sequence']), 'winner/tie differs')
            expected_action=winner['sequence'][0]
            data=None
            decisions+=1
        elif kind in ('query_selected','no_query'):
            action=event['id'] if kind=='query_selected' else ''
            if scored:
                require(expected_action is not None and action==expected_action, 'executed action differs')
                expected_action=None
            if action:
                require(action not in queries and len(queries)<capacity, 'duplicate/over-capacity query')
                queries.append(action)
    require(data is None and expected_action is None and decisions==(2 if scored else 0), 'unfinished decisions')
    services=[e for e in block if e['event']=='task_service']
    moves=[e for e in block if e['event']=='original_move_started']
    ends=[e for e in block if e['event']=='native_end_ownership_handoff']
    require(len(services)==9 and len({e['task'] for e in services})==9, 'nine distinct services missing')
    require(len(moves)==9+2*ab+ct and len({e['id'] for e in moves})==len(moves), 'MOVE count differs')
    require({e['id'] for e in moves}.issubset({e['id'] for e in ends}), 'requester native END missing')
    require(result['queries']==queries, 'query result differs')
    flow=sum(exact_time(e['at'])-exact_time(e['assigned_at']) for e in services)
    require(flow==result['task_flow_sum'], 'all-task flow differs')
    curve=[sum(exact_time(e['at'])<=t for e in services) for t in result['service_times']]
    require(curve==result['completed_tasks'], 'completion curve differs')
    require(max(exact_time(e['at']) for e in services)==result['last_task_service'], 'last service differs')
    first=[e for e in services if e['task'].endswith('-task1')]
    return dict(run_id=begin['run_id'],policy=policy,predictor=begin['predictor'],capacity=capacity,
                ab_tail=ab,c_tail=ct,queries=queries,query_count=len(queries),
                cohort_flow=int(sum(exact_time(e['at']) for e in first)),task_flow_sum=int(flow),
                cohort_service={e['task']:int(exact_time(e['at'])) for e in first},
                curve=curve,last_service=result['last_task_service'],moves=len(moves),tasks=len(services),
                audited_decisions=decisions,active_input_terms=active_terms,audited_candidates=candidate_count)


def audit_events(events,index):
    condition=events[0]
    require(condition['event']=='condition' and condition['capacity']==index%3
            and condition['ab_tail']==(index//12)//2 and condition['c_tail']==(index//12)%2, 'instance factor mismatch')
    histories=[e for e in events if e['event']=='historical_native_END_delivered']
    require(len(histories)==6 and len({e['run_id'] for e in histories})==6
            and all(Fraction(e['received']['upper'],e['received']['denominator'])<32 for e in histories), 'training history mismatch')
    models={e['predictor']:e['alpha'] for e in events if e['event']=='frozen_predictor'}
    require(len(models)==6, 'frozen predictor set changed')
    blocks,block=[],None
    for event in events:
        if event['event']=='policy_begin':
            require(block is None,'unfinished episode')
            block=[event]
        elif block is not None:
            block.append(event)
            if event['event']=='policy_result':
                blocks.append(audit_block(block,models));block=None
    require(len(blocks)==8 and block is None,'declared eight episodes missing')
    require(events[-1]['event']=='summary' and events[-1]['status']=='passed','native summary missing')
    require(all(events[-1][k] is False for k in ('production_AUTH','full_paid_cost','independent_learning_advantage_claim','lifelong_performance_claim')),'claim boundary changed')
    return dict(index=index,condition=condition['id'],checks=events[-1]['checks'],results=blocks)
