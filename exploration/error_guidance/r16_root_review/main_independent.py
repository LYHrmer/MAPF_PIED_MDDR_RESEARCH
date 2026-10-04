"""Independent exact rectangle/age checks on the real archived main-line body.

No candidate module imports, native reruns or access to live capabilities.
"""
from fractions import Fraction as F
from pathlib import Path
import hashlib
import json

HERE=Path(__file__).resolve().parent
MAIN=Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH')
BASE=MAIN/'implementation_binding_evidence/evidence_execution_contract_20261004_r16'
OLD=MAIN/'implementation_binding_evidence/position_search_bridge_20261004_r14'


def load(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def q(x):return F(int(x['numerator']),int(x['denominator']))
def dyadic(x):return F(int(x['mantissa']))*F(2)**int(x['exponent'])


def extent(piece,axis):
    values=[q(point[axis]) for point in piece]
    return min(values),max(values)


def main():
    binding=load(BASE/'EXECUTION_BINDING.json')
    native=load(BASE/'NATIVE_RESULT.json')
    body=load(OLD/'POSITION.json')
    observation=load(BASE/'CONSUMED_CONSTRAINTS.json')
    assert binding['domain']==body['domain'] and binding['request']==body['record']['request']
    assert binding['body_sha256']==body['body_sha256']==sha(OLD/'POSITION.body')
    for p,h in binding['source_pins'].items():assert sha(p)==h,p
    receipt=load(BASE/'commands/native/receipt.json')
    assert receipt['exit_code']==0
    stdout=BASE/'commands/native/stdout.log'
    assert receipt['stdout_sha256']==sha(stdout)
    assert json.loads(stdout.read_text())==native
    geometry=binding['source_geometry']; control=binding['controller']
    u,v=[q(x) for x in geometry['u']],[q(x) for x in geometry['v']]
    L=q(geometry['length'])
    assert u==[F(1),F(0)] and v==[F(13),F(0)] and L==12
    footprint=geometry['footprint'];assert len(footprint)==1
    fx0,fx1=extent(footprint[0],0);fy0,fy1=extent(footprint[0],1)
    error=geometry['error_box'];ex0,ey0=map(q,error['lower']);ex1,ey1=map(q,error['upper'])
    assert (fx0,fx1,fy0,fy1)==(-F(1,20),F(1,20),-F(1,20),F(1,20))
    assert (ex0,ex1,ey0,ey1)==(-F(1,20),F(1,20),-F(1,20),F(1,20))
    intervals={}
    for resource in geometry['resources']:
        assert len(resource['pieces'])==1
        piece=resource['pieces'][0]
        x0,x1=extent(piece,0);y0,y1=extent(piece,1)
        if u[1]+fy1+ey1 < y0 or u[1]+fy0+ey0 > y1:
            hit=[]
        else:
            lo=max(F(0),x0-u[0]-fx1-ex1)
            hi=min(L,x1-u[0]-fx0-ex0)
            hit=[(lo,hi)] if lo<=hi else []
        intervals[resource['key']]=hit
    for key,hit in intervals.items():
        assert hit==[tuple(map(q,z)) for z in native['front_cell_progress_intervals'][key]],key
    def mask(progress):
        return sorted(k for k,ranges in intervals.items() if any(a<=L and progress<=b for a,b in ranges))
    record=body['record'];lo,hi=dyadic(record['lower']),dyadic(record['upper'])
    captured,delivered=q(record['captured']),q(body['delivered'])
    now=q(observation['now']);age=now-captured
    assert (lo,hi,captured,delivered,now)==(F(2),F(2),F(2),F(4),F(4))
    assert q(control['a_hi'])==6 and control['monotone_progress'] is True
    vmax=q(control['speed_upper']);assert vmax**2>=2*q(control['a_hi'])*L
    upper=min(L,hi+age*vmax)
    assert (q(observation['progress_lower']),q(observation['progress_upper']))==(lo,upper)==(F(2),F(12))
    assert (q(observation['remaining_distance_lower']),q(observation['remaining_distance_upper']))==(L-upper,L-lo)
    assert native['front_mask_before']==mask(F(0)) and native['front_mask_after']==mask(lo)
    assert native['closed_contact_mask']==mask(F(3,5))
    assert native['strictly_passed_mask']==mask(F(600001,1000000))
    assert 'cell-1' in mask(F(3,5)) and 'cell-1' not in mask(F(600001,1000000))
    demand=['cell-0','cell-1'];assert native['demand_cells']==demand
    assert native['intersection_before']==sorted(set(mask(F(0)))&set(demand))==['cell-1']
    assert native['intersection_after']==sorted(set(mask(lo))&set(demand))==[]
    for k in ('ARRIVE','resource_release','advance_current','executed'):assert native[k] is False
    assert native['eta_point'] is None and native['completion_delay_upper'] is None
    assert q(native['current_q_unchanged'])==0 and q(native['cap_unchanged'])==12
    old_rows=[json.loads(s) for s in (OLD/'commands/native/stdout.log').read_text().splitlines() if s.startswith('{')]
    rear=[r for r in old_rows if r['event']=='R8_original_rear_cap_RUN']
    assert len(rear)==1 and rear[0]['tick']==6 and rear[0]['front_closed'] is True
    assert rear[0]['cause']=='paid_POSITION'
    costs=[r for r in old_rows if r['event']=='closed_segment']
    assert sum(r['actual'] for r in costs)==344352218
    output=dict(passed=True,intervals_reconstructed=len(intervals),
                body_sha256=body['body_sha256'],current_progress_bounds=['2','12'],
                remaining_distance_bounds=['0','10'],changed_geometric_intersection=['cell-1',[]],
                closed_boundary_retained=True,original_actual_rear_RUN=rear[0],
                new_physical_execution=False,production_COST_replayed=344352218,
                cost_attribution='original total, not new run or POSITION marginal cost',
                pins={str(p):sha(p) for p in [BASE/'EXECUTION_BINDING.json',BASE/'CONSUMED_CONSTRAINTS.json',
                    BASE/'NATIVE_RESULT.json',BASE/'commands/native/receipt.json',OLD/'POSITION.body']})
    (HERE/'MAIN_INDEPENDENT.json').write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps({k:v for k,v in output.items() if k!='pins'},indent=2))


if __name__=='__main__':main()
