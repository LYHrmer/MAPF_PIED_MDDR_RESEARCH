"""Registered content-addressed calls; successful solver/trajectory work is never repeated."""
import sys
sys.dont_write_bytecode=True
import argparse,copy,datetime,gzip,hashlib,json,subprocess,time
from pathlib import Path
from bridge import *
from measurement import issue
from audit_events import audit
MAIN=Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence')/HERE.name
CONFIG={'method':'GSES','search_seconds':16,'host_seconds':25,'seed':10,'branch':'default','heuristic':'zero','early_termination':True,'incremental':False,'w_astar':1,'w_focal':1,'grouping':None,'concurrency':1}
SEMANTICS='R11 affine exact event executor + R13 guarded graph adoption'
def load(p):return json.loads(Path(p).read_text())
def readpacked(p):return json.loads(gzip.decompress(Path(p).read_bytes()))
def write(p,obj):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(obj,sort_keys=True,indent=2,default=str)+'\n')
def compact(p,obj):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(obj,sort_keys=True,separators=(',',':'),default=str)+'\n')
def packed(p,obj):
 p.parent.mkdir(parents=True,exist_ok=True);data=(json.dumps(obj,separators=(',',':'),default=str)+'\n').encode()
 with p.open('wb') as f:
  with gzip.GzipFile(fileobj=f,mode='wb',filename='',mtime=0) as z:z.write(data)
 return {'raw':str(p),'packed_sha256':sha(p),'raw_sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)}
def registration():
 reg=load(HERE/'REGISTRATION.json')
 for path,h in reg['source_pins'].items():assert sha(path)==h,('frozen source changed',path)
 assert sha(reg['binary'])==reg['binary_sha256'];return reg

def solver_identity(graph,reg):
 return {'canonical_input_sha256':graph_digest(graph),'method':'GSES','config':CONFIG,'binary_sha256':reg['binary_sha256'],
         'author_sources_sha256':reg['author_sources_sha256'],'author_binding_sha256':reg['author_binding_sha256'],
         'adapter_sha256':reg['adapter_sha256']}
def solver_key(graph,reg):return digest(solver_identity(graph,reg))
def continuation_key(snapshot_sha,graph,reg):
 return digest({'checkpoint_packed_sha256':snapshot_sha,'adopted_full_graph_sha256':graph_digest(graph),
                'executor_sha256':reg['executor_sha256'],'guard_sha256':reg['guard_sha256'],'semantics':SEMANTICS})
def freeze():
 if (HERE/'REGISTRATION.json').exists():registration();print('reuse registration');return
 old=load(R13/'REGISTRATION.json')
 files=[HERE/n for n in ['bridge.py','measurement.py','pipeline.py','mechanics.py','PROTOCOL.md']]
 files += [R13/n for n in ['REGISTRATION.json','RESULTS.json','executor.py','online.py','audit_events.py','author_online.cpp','AUTHOR_SOURCE.json','AUTHOR_SOURCES.tar.gz']]
 for run in old['runs']:
  files += [R13/'raw'/(run['id']+'__checkpoint.json.gz'),R13/'public'/(run['id']+'.json')]
  for m in ('GSES','Improved_GSES'):
   files += [R13/'calls'/(run['id']+'__'+m)/n for n in ('receipt.json','author_reply.json')]
 reg={'created_UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'frozen_unix_ns':time.time_ns(),
      'source_pins':{str(p):sha(p) for p in files},'R13_registration_sha256':sha(R13/'REGISTRATION.json'),'runs':old['runs'],
      'binary':old['binary'],'binary_sha256':old['binary_sha256'],'config':CONFIG,'new_solver_key_limit':12,
      'author_sources_sha256':sha(R13/'AUTHOR_SOURCES.tar.gz'),'author_binding_sha256':sha(R13/'AUTHOR_SOURCE.json'),
      'adapter_sha256':sha(R13/'author_online.cpp'),'executor_sha256':sha(R13/'executor.py'),'guard_sha256':sha(R13/'online.py'),
      'independent_units':'two reused author instances / twelve mechanism checkpoints; no new heldout test',
      'production_cost':None}
 write(HERE/'REGISTRATION.json',reg);print('frozen',sha(HERE/'REGISTRATION.json'))

def old_solver_cache(reg):
 cache={}
 for run in reg['runs']:
  folder=R13/'calls'/(run['id']+'__GSES');reply=load(folder/'author_reply.json');receipt=load(folder/'receipt.json')
  assert receipt['returncode']==0 and reply['status']=='Succ'
  assert Path(receipt['command'][2])==Path(reg['binary']) and receipt['command'][4]=='GSES'
  assert reply['input_graph']==load(R13/'public'/(run['id']+'.json'))['solver_graph']
  key=solver_key(reply['input_graph'],reg)
  record={'context':run['id'],'receipt':str(folder/'receipt.json'),'receipt_sha256':sha(folder/'receipt.json'),
          'reply':str(folder/'author_reply.json'),'reply_sha256':sha(folder/'author_reply.json'),'source':'reused_R13',
          'started_unix_ns':receipt['started_unix_ns'],'selected_graph_sha256':graph_digest(reply['selected_graph'])}
  cache.setdefault(key,[]).append(record)
 for records in cache.values():records.sort(key=lambda x:(x['started_unix_ns'],x['receipt']))
 return cache

def views():
 reg=registration()
 if (HERE/'VIEWS.json').exists():
  for r in load(HERE/'VIEWS.json')['rows']:
   for key in ('public_base','public_view','position_view','evidence'):
    if r[key]:assert sha(r[key]['path'])==r[key]['sha256']
  print('reuse successful view diagnostics');return
 cache=old_solver_cache(reg);rows=[];keys={}
 for spec in reg['runs']:
  cid=spec['id'];path=R13/'raw'/(cid+'__checkpoint.json.gz');snapshot=readpacked(path);engine=Executor.restore(snapshot)
  base=public_base(engine);req=request_for(base);evidence=None;verified=None
  if req:
   body,receipt=issue(snapshot,sha(path),req);trusted=digest(receipt)
   verified=verify_evidence(base,body,receipt,trusted)
   evidence={'request':req,'body':body,'receipt':receipt,'trusted_receipt_sha256':trusted}
  pub=search_view(base);paid=search_view(base,verified)
  paths={'public_base':HERE/'public'/(cid+'.json'),'public_view':HERE/'views'/(cid+'__public.json'),
         'position_view':HERE/'views'/(cid+'__position.json'),'evidence':HERE/'evidence'/(cid+'.json') if evidence else None}
  for label,value in [('public_base',base),('public_view',pub),('position_view',paid),('evidence',evidence)]:
   if paths[label]:compact(paths[label],value)
  row={'context':cid,'checkpoint':str(path),'checkpoint_sha256':sha(path),
       **{k:({'path':str(v),'sha256':sha(v)} if v else None) for k,v in paths.items()},
       'request_count':int(req is not None),'target':target(base),'public_solver_key':solver_key(pub['solver_graph'],reg),
       'position_solver_key':solver_key(paid['solver_graph'],reg),
       'graph_changed_by_position':pub['solver_graph']!=paid['solver_graph'],
       'public_graph_changed_vs_R13':pub['solver_graph']!=load(R13/'public'/(cid+'.json'))['solver_graph']}
  row['target_estimates']={opt:next((v for v in view['estimates'] if req and v['agent']==req['agent']),None) for opt,view in [('public',pub),('position',paid)]}
  rows.append(row)
  for opt,view in [('public',pub),('position',paid)]:
   key=solver_key(view['solver_graph'],reg);keys.setdefault(key,{'identity':solver_identity(view['solver_graph'],reg),'users':[],'old_records':cache.get(key,[])})['users'].append({'context':cid,'option':opt,'view':str(paths[opt+'_view'])})
 new=[k for k,v in keys.items() if not v['old_records']]
 summary={'rows':rows,'keys':keys,'unique_solver_keys':len(keys),'new_solver_keys':new,'new_solver_count':len(new),'request_count':sum(r['request_count'] for r in rows),
          'position_changed_graph_count':sum(r['graph_changed_by_position'] for r in rows),
          'old_duplicate_selected_graph_disagreement':{k:[r['selected_graph_sha256'] for r in v] for k,v in cache.items() if len(set(r['selected_graph_sha256'] for r in v))>1},
          'created_unix_ns':time.time_ns(),'registration_sha256':sha(HERE/'REGISTRATION.json')}
 write(HERE/'OLD_SOLVER_CACHE.json',cache);write(HERE/'VIEWS.json',summary)
 print(json.dumps({k:v for k,v in summary.items() if k not in ('rows','keys','new_solver_keys')}))
 assert len(new)<=reg['new_solver_key_limit'],'new keys exceed preregistered limit; no call made'

def old_continuations(reg):
 indexed={r['id']:r for r in load(R13/'RESULTS.json')};cache={}
 for spec in reg['runs']:
  cid=spec['id'];cp=R13/'raw'/(cid+'__checkpoint.json.gz');snapshot=readpacked(cp);g=Executor.restore(snapshot).g;pub=load(R13/'public'/(cid+'.json'))
  for method in ('original','GSES','Improved_GSES'):
   row=indexed[cid+'__'+method];final=g if method=='original' else merge_candidate(g,pub,load(R13/'calls'/(cid+'__'+method)/'author_reply.json')['selected_graph'])
   key=continuation_key(sha(cp),final,reg);raw=R13/row['raw'];assert sha(raw)==row['packed_sha256']
   candidate={'source':'reused_R13','raw':str(raw),'packed_sha256':row['packed_sha256'],'raw_sha256':row['raw_sha256'],
              'sum_completion_time':row['sum_completion_time'],'makespan':row['makespan'],'reference_id':row['id']}
   cache.setdefault(key,candidate)
 return cache

def call(key,entry,reg):
 if entry['old_records']:return entry['old_records'][0]
 folder=HERE/'calls'/key
 if (folder/'receipt.json').exists():
  rec=load(folder/'receipt.json');assert rec['solver_key']==key;assert sha(folder/'input.json')==rec['input_file_sha256'];return rec
 if folder.exists():raise RuntimeError('incomplete attempt retained; never automatically rerun '+key)
 folder.mkdir(parents=True);view=load(entry['users'][0]['view']);compact(folder/'input.json',{'solver_graph':view['solver_graph']})
 attempt={'solver_key':key,'identity':entry['identity'],'input_file_sha256':sha(folder/'input.json'),
          'registration_sha256':sha(HERE/'REGISTRATION.json'),'views_sha256':sha(HERE/'VIEWS.json'),'first_attempt':1,
          'started_unix_ns':time.time_ns(),'source':'new'}
 write(folder/'FIRST_ATTEMPT.json',attempt)
 output=folder/'author_reply.json';cmd=['rtk','proxy',reg['binary'],str(folder/'input.json'),'GSES',str(output)]
 with (folder/'stdout.log').open('w') as out,(folder/'stderr.log').open('w') as err:
  try:rc=subprocess.run(cmd,stdout=out,stderr=err,timeout=CONFIG['host_seconds']).returncode
  except subprocess.TimeoutExpired:rc=None
 rec=dict(attempt,command=cmd,finished_unix_ns=time.time_ns(),returncode=rc,receipt=str(folder/'receipt.json'),reply=str(output))
 rec['status']='HostTimeout' if rc is None else 'AuthorError'
 if rc==0:
  reply=load(output);assert reply['input_graph']==view['solver_graph'];rec['status']=reply['status'];rec['reply_sha256']=sha(output)
 write(folder/'receipt.json',rec);return rec

def run():
 reg=registration();manifest=load(HERE/'VIEWS.json');assert manifest['new_solver_count']<=reg['new_solver_key_limit']
 prior=load(HERE/'RESULTS.json') if (HERE/'RESULTS.json').exists() else [];done={r['id']:r for r in prior}
 cache=old_continuations(reg)
 if (HERE/'NEW_CONTINUATION_CACHE.json').exists():cache.update(load(HERE/'NEW_CONTINUATION_CACHE.json'))
 newcache={};calls={};rows=[]
 for entry in manifest['rows']:
  cid=entry['context'];assert sha(entry['checkpoint'])==entry['checkpoint_sha256'];snapshot=readpacked(entry['checkpoint']);initial=Executor.restore(snapshot).g
  base=load(entry['public_base']['path']);evidence=load(entry['evidence']['path']) if entry['evidence'] else None
  for option in ('keep','public','position'):
   name=cid+'__'+option
   if name in done:
    row=done[name];assert sha(row['continuation_source']['raw'])==row['continuation_source']['packed_sha256'];rows.append(row);continue
   rec=None;view=None;guard=None;status='Control';candidate=None;error=None;request_source=None
   if option=='keep':engine=Executor.restore(copy.deepcopy(snapshot))
   else:
    view=load(entry[option+'_view']['path']);key=entry[option+'_solver_key']
    if key not in calls:
     existing_receipt=(HERE/'calls'/key/'receipt.json').exists()
     calls[key]=call(key,manifest['keys'][key],reg)
     request_source='reused_R14' if existing_receipt else calls[key]['source']
    else:request_source='reused_R13' if calls[key]['source']=='reused_R13' else 'reused_R14'
    rec=calls[key];candidate=load(rec['reply']) if rec.get('reply') and Path(rec['reply']).exists() and rec.get('status','Succ') in ('Succ','Timeout') else None
    status=candidate['status'] if candidate else rec.get('status','AuthorError')
    if status=='Succ':
     try:
      kwargs={'body':evidence['body'],'receipt':evidence['receipt'],'trusted':evidence['trusted_receipt_sha256']} if option=='position' and evidence else {}
      engine,guard=adopt(snapshot,base,view,candidate['selected_graph'],**kwargs)
     except (AssertionError,KeyError,TypeError,ValueError,IndexError) as exc:
      error=repr(exc);status='Rejected';engine=Executor.restore(copy.deepcopy(snapshot))
    else:engine=Executor.restore(copy.deepcopy(snapshot))
   ckey=continuation_key(entry['checkpoint_sha256'],engine.g,reg)
   if ckey in cache:
    continuation=copy.deepcopy(cache[ckey]);assert sha(continuation['raw'])==continuation['packed_sha256']
    if continuation['source']=='new':continuation['source']='reused_R14'
   else:
    before=Executor.restore(snapshot);trace=finish(engine,initial,guard);local=audit(trace)
    assert trace['events'][:len(before.events)]==before.events and trace['segments'][:len(before.segments)]==before.segments
    continuation=dict(packed(HERE/'raw'/(ckey+'.json.gz'),trace),source='new',sum_completion_time=trace['sum_completion_time'],makespan=trace['makespan'],local_audit=local)
    cache[ckey]=copy.deepcopy(continuation);newcache[ckey]=copy.deepcopy(continuation)
    existing=load(HERE/'NEW_CONTINUATION_CACHE.json') if (HERE/'NEW_CONTINUATION_CACHE.json').exists() else {}
    existing.update(newcache);write(HERE/'NEW_CONTINUATION_CACHE.json',existing)
   row={'id':name,'context':cid,'option':option,'status':status,'guard_error':error,'guard':guard,
        'checkpoint_sha256':entry['checkpoint_sha256'],'public_base':entry['public_base'],'search_view':entry.get(option+'_view'),
        'evidence':entry['evidence'] if option=='position' else None,'request_count':entry['request_count'] if option=='position' else 0,
        'solver_key':entry.get(option+'_solver_key'),'call_source':request_source,'call_reference':rec,
        'candidate_graph_sha256':graph_digest(candidate['selected_graph']) if candidate else None,
        'adopted_graph_sha256':graph_digest(engine.g),'continuation_key':ckey,'continuation_source':continuation,
        'sum_completion_time':continuation['sum_completion_time'],'makespan':continuation['makespan'],'production_cost':None}
   compact(HERE/'guards'/(name+'.json'),{'status':status,'guard':guard,'guard_error':error,'actual_full_graph':engine.g})
   rows.append(row);write(HERE/'RESULTS.json',rows)
   print(name,status,'call',row['call_source'],'trace',continuation['source'],flush=True)
 write(HERE/'RESULTS.json',rows)
 summary={'finished_unix_ns':time.time_ns(),'rows':len(rows),'new_solver_calls':len(list((HERE/'calls').glob('*/receipt.json'))) if (HERE/'calls').exists() else 0,
          'new_continuations':len(list((HERE/'raw').glob('*.json.gz'))) if (HERE/'raw').exists() else 0,
          'reused_solver_requests':sum(r['call_source']=='reused_R13' for r in rows),'position_changed_search':manifest['position_changed_graph_count'],
          'registration_sha256':sha(HERE/'REGISTRATION.json'),'views_sha256':sha(HERE/'VIEWS.json'),'results_sha256':sha(HERE/'RESULTS.json')}
 write(HERE/'COMPLETE.json',summary);print(json.dumps(summary))

def main():
 p=argparse.ArgumentParser();p.add_argument('stage',choices=['freeze','views','run']);args=p.parse_args();globals()[args.stage]()
if __name__=='__main__':main()
