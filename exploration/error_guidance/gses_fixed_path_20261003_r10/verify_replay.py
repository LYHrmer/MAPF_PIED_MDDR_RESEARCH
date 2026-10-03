"""Independent synchronous TPG replay; never use recorded next states as actions."""
from pathlib import Path
import copy
import gzip
import hashlib
import json

ROOT=Path(__file__).resolve().parent


def replay(run):
    g=run['graph']
    paths=g['paths']
    n=len(paths)
    counts=[len(p) for p in paths]
    offsets=[]
    ids=[]
    for a,p in enumerate(paths):
        offsets.append(len(ids))
        ids.extend((a,s) for s in range(len(p)))
        for (u,_),(v,_) in zip(p,p[1:]):
            assert sum(abs(x-y) for x,y in zip(u,v))==1, 'non-grid or repeated-location state'
    assert offsets==g['offsets']
    state=list(g['current'])
    assert len(state)==n and all(0<=s<counts[a] for a,s in enumerate(state))
    initial=list(state)
    incoming=[[] for _ in ids]
    weights={}
    for kind in ['type1','type2']:
        assert len({tuple(e[:2]) for e in g[kind]})==len(g[kind]), 'duplicate edge'
        for u,v,w in g[kind]:
            assert 0<=u<len(ids) and 0<=v<len(ids)
            assert w>=1 and int(w)==w, 'non-integer cost outside original simulator contract'
            incoming[v].append(ids[u])
            if kind=='type1':
                a,s=ids[u]
                assert ids[v]==(a,s+1)
                assert s>=initial[a], 'unpruned type1'
                if s!=initial[a]:
                    assert w==1, 'future weighted primitive unsupported by author simulator'
                weights[(u,v)]=int(w)
            else:
                assert ids[u][0]!=ids[v][0] and w==1
    expected={(offsets[a]+s,offsets[a]+s+1) for a in range(n) for s in range(initial[a],counts[a]-1)}
    assert set(weights)==expected
    delay=[weights[(offsets[a]+s,offsets[a]+s+1)]-1 if s<counts[a]-1 else 0 for a,s in enumerate(state)]
    trajectory=[[p[s][0]] for p,s in zip(paths,state)]
    states=[state.copy()]
    ticks=cost=0
    while any(s<counts[a]-1 for a,s in enumerate(state)):
        assert ticks<1000000,'deadlock'
        old=state.copy()
        oldpos=[tuple(paths[a][s][0]) for a,s in enumerate(old)]
        assert len(set(oldpos))==n,'vertex collision'
        for a,s in enumerate(old):
            if s==counts[a]-1:
                continue
            cost+=1
            if delay[a]==0 and all(old[b]>=q for b,q in incoming[offsets[a]+s+1]):
                state[a]+=1
            if delay[a]>0:
                delay[a]-=1
            trajectory[a].append(paths[a][state[a]][0])
        newpos=[tuple(paths[a][s][0]) for a,s in enumerate(state)]
        assert len(set(newpos))==n,'vertex collision'
        previous_owner={p:a for a,p in enumerate(oldpos)}
        assert all(p not in previous_owner or previous_owner[p]==a for a,p in enumerate(newpos)), 'following collision'
        ticks+=1
        states.append(state.copy())
        if old==state and not any(delay):
            # The last delay decrement may legitimately create a move on the next tick.
            assert any(s<counts[a]-1 and all(state[b]>=q for b,q in incoming[offsets[a]+s+1]) for a,s in enumerate(state)), 'dependency deadlock'
    assert states==run['states'],'state time series mismatch'
    assert trajectory==run['paths'],'native trajectory mismatch'
    assert ticks==run['ticks'],'tick mismatch'
    assert cost==run['cost']==sum(len(p)-1 for p in trajectory),'sum of costs mismatch'
    assert run['native_simulate_matches_step_trace'] is True
    return {'cost':cost,'ticks':ticks,'agents':n,'state_observations':len(states)*n,
            'type1_edges':len(g['type1']),'type2_edges':len(g['type2'])}


def check_reversals(a,b):
    assert a['paths']==b['paths'] and a['current']==b['current'] and a['type1']==b['type1']
    def pair(edge):
        u,v,w=edge
        assert w==1
        return min((u,v),(v+1,u-1))
    assert sorted(map(pair,a['type2']))==sorted(map(pair,b['type2'])), 'unmatched type2 dependency'
    return len(set(map(tuple,a['type2']))-set(map(tuple,b['type2'])))


def main():
    results=json.loads((ROOT/'RESULTS_attempt01.json').read_text())
    old=json.loads((ROOT.parent/'gses_author_preflight_20261003_r9/RESULTS.json').read_text())
    old={(r['case'],r['method']):r['stats'] for r in old}
    checks=[]
    first=None
    for row in results:
        raw=ROOT/row['raw']
        assert hashlib.sha256(raw.read_bytes()).hexdigest()==row['raw_sha256']
        unpacked=gzip.decompress(raw.read_bytes())
        assert hashlib.sha256(unpacked).hexdigest()==row['uncompressed_sha256']
        data=json.loads(unpacked)
        audits={k:replay(data[k]) for k in ['original','selected']}
        reversals=check_reversals(data['original']['graph'],data['selected']['graph'])
        reference=old[(row['case'],row['method'])]
        assert reference['original_cost']==data['original']['cost']
        assert reference['cost']==data['selected']['cost']
        assert reference['status']==data['status']
        if data['status']=='Timeout':
            assert data['original']==data['selected'], 'timeout did not execute original graph'
        checks.append({'case':row['case'],'method':row['method'],'status':data['status'],
                       'r9_original_cli_status_and_cost_match':True,'reversed_dependencies':reversals,**audits})
        if first is None:
            first=data['original']
    negative=[]
    for name in ['state','cost','trajectory','future_weight']:
        bad=copy.deepcopy(first)
        if name=='state':
            bad['states'][-1][0]-=1
        elif name=='cost':
            bad['cost']+=1
        elif name=='trajectory':
            bad['paths'][0][-1][0]+=1
        else:
            for e in bad['graph']['type1']:
                if all(e[0]!=o+s for o,s in zip(bad['graph']['offsets'],bad['graph']['current'])):
                    e[2]=2
                    break
            else:
                raise AssertionError('no future edge for control')
        try:
            replay(bad)
        except AssertionError as e:
            negative.append({'mutation':name,'rejected':True,'reason':str(e)})
        else:
            raise AssertionError('negative control accepted: '+name)
    result={'verdict':'PASS','runs':len(checks),'replays':2*len(checks),'checks':checks,'negative_controls':negative}
    (ROOT/'INDEPENDENT_REPLAY.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'verdict':'PASS','runs':len(checks),'replays':2*len(checks),'negative_controls':len(negative)}))


if __name__=='__main__':
    main()
