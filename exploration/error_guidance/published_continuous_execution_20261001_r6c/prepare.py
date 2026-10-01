from pathlib import Path
import json,hashlib,shutil,difflib,random,xml.etree.ElementTree as ET
HERE=Path(__file__).resolve().parent
MAIN=Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence');OUT=MAIN/HERE.name
P=MAIN/'gpibt_lsmart_error_model_20260930_r4c';REGISTER=HERE.parent/'mapf_evaluation_20260930_r5';INPUT=MAIN/'standard_map_pilot_20260930_r5/inputs'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,x):p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
assert not OUT.exists();OUT.mkdir();src=OUT/'lsmart_successor';src.mkdir()
for part in ['server','client']:shutil.copytree(P/'lsmart_successor'/part,src/part,ignore=shutil.ignore_patterns('.git','build','__pycache__'))
# S1 control variant: retain original R0 condition as a recorded source reference.
f=src/'client/controllers/footbot_diffusion/footbot_diffusion.cpp';old=f.read_text();needle='if (not q.empty() and q.back().type == Action::MOVE) {'
assert old.count(needle)==1
fixed=old.replace(needle,'if (false && not q.empty() and q.back().type == Action::MOVE) { // R6b S1: keep every original MOVE endpoint')
second='while (not q.empty() and q.front().type == Action::MOVE) {'
assert fixed.count(second)==1
fixed=fixed.replace(second,'while (false && not q.empty() and q.front().type == Action::MOVE) { // R6b S1: prevent per-tick re-merging')
f.write_text(fixed)
(HERE/'strict_point.patch').write_text(''.join(difflib.unified_diff(old.splitlines(True),f.read_text().splitlines(True),fromfile='R0/client/controllers/footbot_diffusion/footbot_diffusion.cpp',tofile='S1/client/controllers/footbot_diffusion/footbot_diffusion.cpp')))
write(HERE/'R0_reference.json',{'source':str(P/'lsmart_successor/client/controllers/footbot_diffusion/footbot_diffusion.cpp'),'source_sha256':hashlib.sha256(old.encode()).hexdigest(),'client_binary':str(P/'client_build/controllers/footbot_diffusion/libfootbot_diffusion.so'),'client_binary_sha256':sha(P/'client_build/controllers/footbot_diffusion/libfootbot_diffusion.so'),'new_R0_runs':0})
changes={}
for part in ['client','server']:
 for q in (src/part).rglob('*'):
  if q.is_file():
   prior=P/'lsmart_successor'/q.relative_to(src)
   if sha(q)!=sha(prior):
    changes[str(q.relative_to(src))]={'parent':sha(prior),'successor':sha(q)};dst=HERE/'source_snapshot'/q.relative_to(src);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(q,dst)
write(HERE/'source_changes.json',changes)
write(HERE/'native_source_manifest.json',{str(q.relative_to(src)):sha(q) for q in src.rglob('*') if q.is_file()})
job=json.loads((MAIN/'paired_published_guidance_20260930_r5/trained_930101/job.json').read_text());checkpoint=HERE.parent/'onlineggo_training_20260930_r3/training_02/trained_checkpoint.json'
cfg={k:job['kwargs'][k] for k in ['win_r','has_map','has_path','has_previous','use_all_flow','use_cached_nn','rotate_input','output_size','hidden_size','net_input_type','default_obst_flow','learn_obst_flow','net_type','past_traffic_interval']}
cfg['initial_priority_seed']=930401
for policy in ['hm_GPIBT','trained']:
 cfg['parameters']=json.loads((MAIN/f'paired_published_guidance_20260930_r5/{policy}_930101/job.json').read_text())['kwargs']['network_params'];cfg['parameters']=json.loads(cfg['parameters'])
 assert len(cfg['parameters'])==560
 if policy=='trained':assert cfg['parameters']==json.loads(checkpoint.read_text())['parameters']
 write(HERE/(policy+'_config.json'),cfg)
write(HERE/'model_identity.json',{'checkpoint_path':str(checkpoint),'checkpoint_sha256':sha(checkpoint),'parameters_sha256':hashlib.sha256(json.dumps(json.loads(checkpoint.read_text())['parameters']).encode()).hexdigest(),'parameters':560,'training_domain':'sortation_small_kiva','training_candidates':200,'network_role':'official guidance-flow predictor; not execution-error model'})
runs=[];registry=json.loads((REGISTER/'registry.json').read_text());template=ET.parse(MAIN/'baseline_selection_20260929/lsmart_smoke_03.argos')
for name in ['empty-32-32','random-32-32-10']:
 mp=INPUT/(name+'.map');scenario=INPUT/(name+'-random-1.scen');assert sha(mp)==registry['maps'][name]['map_sha256'];assert sha(scenario)==registry['maps'][name]['scenarios'][0]['sha256']
 inputs=HERE/'inputs'/name;inputs.mkdir(parents=True);shutil.copyfile(mp,inputs/mp.name);shutil.copyfile(scenario,inputs/scenario.name)
 grid=mp.read_text().splitlines()[4:];free=[i*32+j for i,row in enumerate(grid) for j,v in enumerate(row) if v not in '@T'];index={v:k for k,v in enumerate(free)}
 # Both registered maps have one reachable component; independently checked by registry.
 assert registry['maps'][name]['connected_component_sizes']==[len(free)]
 starts=[];goals=[]
 for a,line in enumerate(scenario.read_text().splitlines()[1:17]):
  p=line.split();x,y,gx,gy=map(int,p[4:8]);starts.append(y*32+x);seq=[gy*32+gx];rng=random.Random(f'r6:930401:{name}:{a}')
  while len(seq)<1002:
   choice=rng.randrange(len(free)-1);skip=index[seq[-1]];seq.append(free[choice+int(choice>=skip)])
  goals.append(seq)
 write(inputs/'environment.json',{'starts':starts,'FIFO_goals':goals,'future_lists_visible_to_actor':False,'seed':930401,'source_map_sha256':sha(mp),'source_scenario_sha256':sha(scenario)})
 layout=[''.join('@' if c in '@T' else '.' for c in row) for row in grid]
 write(inputs/'map.json',{'name':name,'layout':layout,'n_row':32,'n_col':32,'n_endpoint':0,'n_agent_loc':0,'milp_runtime':None,'optimize_wait':False,'weight':False,'maxtime':1000})
 for N in [8,16]:
  taskfile=inputs/f'tasks_n{N}.txt';taskfile.write_text(str(N)+'\n'+'\n'.join(';'.join(f'{g},-1,0,0' for g in seq) for seq in goals[:N])+'\n')
  config=ET.fromstring(ET.tostring(template.getroot()));controller=config.find('controllers/footbot_diffusion_controller');controller.set('library',str(OUT/'client_build/controllers/footbot_diffusion/libfootbot_diffusion'));params=controller.find('params');params.set('portNumber','9491');params.set('simDuration','8000');params.set('outputDir','metadata/');config.find('framework/experiment').set('random_seed','930401')
  lf=config.find('loop_functions');lf.set('library',str(OUT/'client_build/loop_functions/trajectory_loop_functions/libtrajectory_loop_functions'));lf.find('port_number').set('value','9491')
  arena=config.find('arena');arena.clear();arena.set('size','33,33,1');arena.set('center','-15.5,-15.5,0')
  for wall,size,pos in [('west','0.05,33,0.5','0.5,-15.5,0'),('east','0.05,33,0.5','-31.5,-15.5,0'),('north','33,0.05,0.5','-15.5,0.5,0'),('south','33,0.05,0.5','-15.5,-31.5,0')]:
   box=ET.SubElement(arena,'box',id='wall_'+wall,size=size,movable='false');ET.SubElement(box,'body',position=pos,orientation='0,0,0')
  for y,row in enumerate(layout):
   for x,ch in enumerate(row):
    if ch=='@':
     box=ET.SubElement(arena,'box',id=f'obstacle_{y}_{x}',size='0.8,0.8,0.5',movable='false');ET.SubElement(box,'body',position=f'{-y},{-x},0',orientation='0,0,0')
  for a,start in enumerate(starts[:N]):
   y,x=divmod(start,32);robot=ET.SubElement(arena,'foot-bot',id=str(a));ET.SubElement(robot,'body',position=f'{-y},{-x},0',orientation='0,0,0');ET.SubElement(robot,'controller',config='fdc')
  ET.ElementTree(config).write(inputs/f'experiment_n{N}.argos',encoding='unicode',xml_declaration=True)
  for policy in ['hm_GPIBT','trained']:
   for condition in ['nominal','slow065','unknown_pause']:runs.append({'id':f'{name}_n{N}_{policy}_{condition}','map':name,'N':N,'policy':policy,'condition':condition,'seed':930401,'horizon_ticks':8000,'dt_seconds':.1,'ACK_version':'S1_point_no_merge'})
write(HERE/'runs.json',{'protocol_sha256':sha(HERE/'PROTOCOL.md'),'runs':runs})
print(OUT,'24 fixed runs')
