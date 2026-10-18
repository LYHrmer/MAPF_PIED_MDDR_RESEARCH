"""Read-only audit of frozen motion artifacts; never imports a solver/constructor."""
import hashlib
import itertools
import json
import math
from pathlib import Path
from fractions import Fraction
import subprocess

ROOT = Path('/home/lyh/MAPF_THESIS_RESEARCH')
HERE = ROOT / 'tracks/thesis'
BATCH = HERE / 'results/nominal_motion_v1'
SHA = 'b0a49406a094955d2499c829e6b0dfce539188ec08f34576abb203b482c086bd'
def digest(raw): return hashlib.sha256(raw).hexdigest()
def close(a,b): assert math.isclose(a,b,rel_tol=1e-10,abs_tol=1e-7),(a,b)
def read(p): return json.loads(p.read_bytes())
assert digest((BATCH/'RUN_RECEIPT.json').read_bytes()) == SHA
summary=read(BATCH/'RUN_RECEIPT.json')
manifest=read(HERE/'config/nominal_motion_v1_manifest.json')
assert digest((HERE/'config/nominal_motion_v1_manifest.json').read_bytes())==summary['manifest_sha256']
for name, sha in manifest['runtime_sha256'].items():
    frozen=subprocess.check_output(['rtk','proxy','git','-C',str(ROOT),'show',summary['scientific_code_commit']+':tracks/thesis/'+name])
    assert digest(frozen)==sha, name
for name,sha in summary['source_artifact_sha256'].items(): assert digest((BATCH/name).read_bytes())==sha,name
lock=read(HERE/'sci.lock.json')
objects={}
for name,pin in lock['entries'].items():
    raw=subprocess.check_output(['rtk','proxy','git','-C',str(ROOT),'show',pin['commit']+':'+pin['path']])
    assert digest(raw)==pin['sha256'],name
    blob=subprocess.check_output(['rtk','proxy','git','-C',str(ROOT),'rev-parse',pin['commit']+':'+pin['path']],text=True).strip()
    assert blob==pin['blob_oid']
    objects[name]=json.loads(raw)
cases={c['id']:c for c in objects['inputs']['cases']}
auth=read(BATCH/'AUTHORIZATION.json');incident=read(BATCH/'ADMINISTRATIVE_INCIDENT.json')
assert 'first authorized case started before this record' in auth['recording_incident']
assert incident['initial_command_status']==1 and incident['retries']==0
assert incident['scientific_parameters_changed'] is False
assert auth['ordered_cases']==manifest['cases']
assert summary['counts']=={'COMPLETE':6,'FAILED_OR_INCOMPLETE':0,'NOT_RUN':0}
assert summary['authorization_consumed_or_closed'] is True
artifact_count=0;pair_count=0;per_agent_count=0;rows=[]

def validate_discrete(paths,c):
    assert set(paths)==set(c['endpoints'])
    blocked=set(c['blocked']);cols=c['cols'];rows=c['rows']
    for a,p in paths.items():
        assert [p[0],p[-1]]==c['endpoints'][a]
        assert all(0<=v<cols*rows and v not in blocked for v in p)
        assert all(abs(x//cols-y//cols)+abs(x%cols-y%cols)<=1 for x,y in zip(p,p[1:]))
    for t in range(max(map(len,paths.values()))):
        occupied=[p[min(t,len(p)-1)] for p in paths.values()]
        assert len(set(occupied))==len(occupied)
        if t:
            edges=[(p[min(t-1,len(p)-1)],p[min(t,len(p)-1)]) for p in paths.values()]
            assert all(not(a==d and b==c) for (a,b),(c,d) in itertools.combinations(edges,2))

def point(v,cols):return (v%cols,v//cols)
def minimum_squared(a0,a1,b0,b1):
    a=[x-y for x,y in zip(a0,b0)];b=[(v-u)-(z-w) for u,v,w,z in zip(a0,a1,b0,b1)]
    norm=sum(x*x for x in b);dot=sum(x*y for x,y in zip(a,b));aa=sum(x*x for x in a)
    if norm==0 or dot>=0:return Fraction(aa)
    if -dot>=norm:return Fraction(sum((x+y)**2 for x,y in zip(a,b)))
    return Fraction(aa*norm-dot*dot,norm)

for row in summary['rows']:
    cid=row['case'];c=cases[cid];folder=BATCH/cid;receipt=read(folder/'receipt.json')
    assert receipt['status']=='COMPLETE' and receipt['retry_allowed'] is False
    costs=receipt['worker_costs']
    assert costs['exit_code']==0 and costs['forced_cleanup'] is False
    assert receipt['entry_through_import_input_validation_output_and_hash_ns']<60e9
    assert costs['all_descendant_user_s']+costs['all_descendant_system_s']<45
    assert costs['largest_child_maxrss_kib']<512*1024
    for name,entry in receipt['artifacts'].items():
        raw=(folder/name).read_bytes();assert digest(raw)==entry['sha256'] and len(raw)==entry['bytes'];artifact_count+=1
        assert len(raw)<=16*1024*1024
    old={a:list(p) for a,p in c['paths'].items()}
    final=objects[cid+'__remaining_bound_result']['final_paths']
    vals={}
    for armrow in row['arms']:
        arm=armrow['arm'];record=read(folder/('arm_'+arm+'.json'))
        m=record['motion'];sch=m['schedule'];metrics=record['metrics']
        assert m['certified_nominal_reference'] is True and m['error_model_applied'] is False
        assert m['certificate']['terminal_holds_permanent'] is True
        assert m['model']==manifest['motion_model']
        assert all(h==0 for h in m['initial_headings_quarters'].values())
        selected=record['selection']['selected']
        if selected=='incumbent':expected=old
        elif selected in ('frozen_proposal','proposal'):expected=final
        else:
            assert selected=='retain_equal_cost_batch'
            expected={a:(old[a] if len(old[a])==len(p) else p) for a,p in final.items()}
        validate_discrete(expected,c)
        assert record['soc']==sum(len(p)-1 for p in expected.values())
        assert record['grid_makespan']==max(len(p)-1 for p in expected.values())
        sums={'MOVE':0.,'TURN':0.,'TURN_BARRIER':0.,'DISCRETE_WAIT_SLOT':0.}
        counts={'move_actions':0,'turn_actions':0,'discrete_wait_actions':0,'turn_quarters_including_initial':0}
        completions=[];allpaths={};peragent={}
        stages=sch['stages'];last=0
        slots=[s for s in stages if s['kind']=='SHARED_MOVE_SLOT']
        for s in stages:
            close(s['start_s'],last);assert s['end_s']>last;last=s['end_s']
            if s['kind']=='SHARED_MOVE_SLOT':close(s['end_s']-s['start_s'],2.)
        close(last,sch['makespan_s'])
        for a,actions in sch['agents'].items():
            per_agent_count+=1;prev=0.;heading=0;pos=old[a][0];path=[pos];local={k:0. for k in sums}
            for i,act in enumerate(actions):
                close(act['start_s'],prev)
                kind=act['kind'];x,y=Fraction(act.get('center_m',act.get('from_m',[0,0]))[0]),Fraction(act.get('center_m',act.get('from_m',[0,0]))[1])
                assert (x,y)==(Fraction(pos%c['cols'],2),Fraction(-(pos//c['cols']),2))
                if kind=='GOAL_HOLD':
                    assert i==len(actions)-1 and act['end_s'] is None and act['end_semantics']=='PERMANENT'
                    assert act['center_m']==[str(Fraction(pos%c['cols'],2)),str(Fraction(-(pos//c['cols']),2))]
                    close(act['start_s'],sch['completion_s'][a]);close(prev,metrics['per_agent'][a]['completion_s'])
                    assert pos==c['endpoints'][a][1];completions.append(prev);break
                assert act['end_s']>prev;duration=act['end_s']-prev
                if kind=='MOVE':
                    assert act['from_m']==[str(Fraction(pos%c['cols'],2)),str(Fraction(-(pos//c['cols']),2))]
                    target=act['to_m'];col=Fraction(target[0])*2;r=-Fraction(target[1])*2
                    assert col.denominator==1 and r.denominator==1
                    new=int(r)*c['cols']+int(col);assert abs(new//c['cols']-pos//c['cols'])+abs(new%c['cols']-pos%c['cols'])==1
                    delta=(new%c['cols']-pos%c['cols'],pos//c['cols']-new//c['cols']);assert heading=={(1,0):0,(0,1):1,(-1,0):2,(0,-1):3}[delta]
                    slot=next(s for s in slots if s['phase_id']==act['phase_id']);close(act['start_s'],slot['start_s']);close(act['end_s'],slot['end_s'])
                    assert int(a) in slot['moving_agents'];close(duration,2.);pos=new;path.append(pos);key='MOVE';counts['move_actions']+=1
                elif kind=='TURN':
                    assert act['heading_from_quarters']==heading;heading=(heading+act['signed_quarters'])%4
                    assert heading==act['heading_to_quarters'];close(duration,1+abs(act['signed_quarters'])*math.pi/2)
                    key='TURN';counts['turn_actions']+=1;counts['turn_quarters_including_initial']+=abs(act['signed_quarters'])
                else:
                    assert kind=='WAIT';key=act['reason'];assert key in ('TURN_BARRIER','DISCRETE_WAIT_SLOT')
                    assert act['heading_quarters']==heading
                    if key=='DISCRETE_WAIT_SLOT':close(duration,2.);path.append(pos);counts['discrete_wait_actions']+=1
                sums[key]+=duration;local[key]+=duration;prev=act['end_s']
            else:raise AssertionError('no permanent hold')
            close(sum(local.values()),prev);close(local['TURN_BARRIER']+local['DISCRETE_WAIT_SLOT'],metrics['per_agent'][a]['wait_s'])
            assert path==expected[a];allpaths[a]=path;peragent[a]=dict(local,completion=prev)
        for field,val in [('move_s',sums['MOVE']),('turn_s',sums['TURN']),('turn_barrier_wait_s',sums['TURN_BARRIER']),('discrete_wait_slot_s',sums['DISCRETE_WAIT_SLOT']),('completion_sum_s',sum(completions)),('makespan_s',max(completions)),('wait_sum_s',sums['TURN_BARRIER']+sums['DISCRETE_WAIT_SLOT'])]:
            close(val,metrics[field]);close(val,armrow['metrics'][field])
        close(sum(sums.values()),metrics['completion_sum_s'])
        assert counts=={k:armrow['metrics'][k] for k in counts}
        assert metrics['permanent_goal_hold_count']==len(expected)
        for stage in stages:
            if stage['kind']!='TURN_BARRIER':continue
            durations=[]
            for actions in sch['agents'].values():
                for act in actions:
                    if act['kind']=='TURN' and math.isclose(act['start_s'],stage['start_s'],abs_tol=1e-7):
                        assert act['end_s']<=stage['end_s']+1e-7
                        durations.append(act['end_s']-act['start_s'])
            assert durations
            close(max(durations),stage['end_s']-stage['start_s'])
        # Independent exact common-progress pair check, including permanent goal holds.
        # Legal grid-unit axis segments have obstacle/boundary clearance >= half a cell;
        # declared rho^2/cell^2=37/500 < 1/4, so all obstacle/boundary checks follow.
        assert Fraction(m['certificate']['body_circle_radius_squared_m2'])/Fraction(1,4)==Fraction(37,500)<Fraction(1,4)
        for t in range(record['grid_makespan']):
            segs=[(point(p[min(t,len(p)-1)],c['cols']),point(p[min(t+1,len(p)-1)],c['cols'])) for p in expected.values()]
            for (a0,a1),(b0,b1) in itertools.combinations(segs,2):
                assert minimum_squared(a0,a1,b0,b1)>Fraction(37,125);pair_count+=1
        vals[arm]={'soc':record['soc'],'completion_sum_s':metrics['completion_sum_s'],'makespan_s':metrics['makespan_s'],**sums,'selected':selected,'per_agent':peragent}
    rows.append({'case':cid,'arms':vals,'frozen_minus_original_completion_s':vals['frozen_soc']['completion_sum_s']-vals['original']['completion_sum_s'],'turn_minus_original_completion_s':vals['turn_aware']['completion_sum_s']-vals['original']['completion_sum_s'],'entry_wall_s':receipt['entry_through_import_input_validation_output_and_hash_ns']/1e9})
assert artifact_count==42
out={'status':'PASS','schema':'INDEPENDENT_OFFLINE_FROZEN_MOTION_AUDIT_V1','batch_receipt_sha256':SHA,'script_sha256':digest(Path(__file__).read_bytes()),'scientific_search_or_motion_construction_executed':False,'frozen_code_pins_checked':len(manifest['runtime_sha256']),'sci_git_object_pins_checked':len(objects),'job_artifact_hashes_checked':artifact_count,'full_arm_schedules_checked':18,'per_agent_decompositions_checked':per_agent_count,'exact_common_progress_pair_segments_checked':pair_count,'administrative_recording_incident_preserved':True,'scope':'Declared zero-error synchronized reference primitives, not actual robot/error-model validation; source frozen REMAINING_BOUND not new ADDRESS','rows':rows}
Path('/tmp/mapf_motion_independent_audit.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k!='rows'},ensure_ascii=False))
for r in rows:print(r['case'],r['frozen_minus_original_completion_s'],r['turn_minus_original_completion_s'])
