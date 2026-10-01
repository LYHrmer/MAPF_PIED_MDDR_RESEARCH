from pathlib import Path
import json,random,shutil,hashlib,xml.etree.ElementTree as E
H=Path(__file__).resolve().parent;P=H.parent/'published_continuous_execution_20261001_r6c';M=Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence');O=M/H.name
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2)+'\n')
def inp(name,seed,mechanical=False):
 d=H/'inputs'/f'{name}_{seed}';d.mkdir(parents=True,exist_ok=True)
 if mechanical:
  cols=8;layout=['.'*8]*8;starts=[3*8+2,3*8+1,5*8+2,6*8+2];goals=[3*8+4,3*8+3,5*8+4,6*8+4];n=4
  env={'starts':starts,'source_map_sha256':None,'source_scenario_sha256':None}
 else:
  cols=32;src=P/'inputs'/name;layout=json.loads((src/'map.json').read_text())['layout'];env=json.loads((src/'environment.json').read_text());starts=env['starts'][:8];n=8
 free=[r*cols+c for r,row in enumerate(layout) for c,v in enumerate(row) if v!='@'];fifo=[]
 for a,start in enumerate(starts):
  rng=random.Random(f'r8:{seed}:{name}:{a}');seq=[];last=start
  for k in range(1002):
   opts=[v for v in free if v!=last];last=goals[a] if mechanical and k==0 else opts[rng.randrange(len(opts))];seq.append(last)
  fifo.append(seq)
 write(d/'map.json',{'name':name,'layout':layout,'n_row':cols,'n_col':cols,'n_endpoint':0,'n_agent_loc':0,'milp_runtime':None,'optimize_wait':False,'weight':False,'maxtime':1000})
 write(d/'environment.json',{'starts':starts,'FIFO_goals':fifo,'seed':seed,'source_map_sha256':env['source_map_sha256'],'source_scenario_sha256':env['source_scenario_sha256']})
 (d/f'tasks_n{n}.txt').write_text(str(n)+'\n'+'\n'.join(';'.join(f'{v},-1,0,0' for v in seq) for seq in fifo)+'\n')
 return d,starts,layout
runs=[]
for split,seeds,names,conds,policies in [('mechanical',[941800],['mechanical'],['nominal','unknown_pause'],['hm']),('test',[941821,941822],['empty-32-32','random-32-32-10'],['nominal','axis'],['hm','history','learned'])]:
 for seed in seeds:
  for name in names:
   d,starts,layout=inp(name,seed,split=='mechanical');n=len(starts);cols=len(layout[0])
   for cond in conds:
    for mode in ['global','local']:
     for pol in policies:
      ident=f'{split}_{name}_{seed}_{cond}_{mode}_{pol}';port=9760+len(runs);h=300 if split=='mechanical' else 4000
      cfg=json.loads((P/'hm_GPIBT_config.json').read_text());cfg['initial_priority_seed']=seed;write(H/'configs'/(ident+'.json'),cfg)
      tree=E.parse(P/'inputs/empty-32-32/experiment_n8.argos');root=tree.getroot();params=root.find('controllers/footbot_diffusion_controller/params');params.set('portNumber',str(port));params.set('simDuration',str(h));root.find('loop_functions/port_number').set('value',str(port));root.find('framework/experiment').set('random_seed',str(seed))
      arena=root.find('arena');arena.clear();arena.set('size',f'{cols+1},{cols+1},1');arena.set('center',f'{-(cols-1)/2},{-(cols-1)/2},0')
      mid=-(cols-1)/2
      for wid,size,pos in [('west',f'0.05,{cols+1},0.5',f'0.5,{mid},0'),('east',f'0.05,{cols+1},0.5',f'{-cols+.5},{mid},0'),('north',f'{cols+1},0.05,0.5',f'{mid},0.5,0'),('south',f'{cols+1},0.05,0.5',f'{mid},{-cols+.5},0')]:
       b=E.SubElement(arena,'box',id='wall_'+wid,size=size,movable='false');E.SubElement(b,'body',position=pos,orientation='0,0,0')
      for r,row in enumerate(layout):
       for c,ch in enumerate(row):
        if ch=='@':b=E.SubElement(arena,'box',id=f'o{r}_{c}',size='0.8,0.8,0.5',movable='false');E.SubElement(b,'body',position=f'{-r},{-c},0',orientation='0,0,0')
      for a,s in enumerate(starts):
       r,c=divmod(s,cols);b=E.SubElement(arena,'foot-bot',id=str(a));E.SubElement(b,'body',position=f'{-r},{-c},0',orientation='0,0,0');E.SubElement(b,'controller',config='fdc')
      (H/'xml').mkdir(exist_ok=True);tree.write(H/'xml'/(ident+'.argos'),encoding='unicode',xml_declaration=True)
      runs.append({'id':ident,'split':split,'map':name,'seed':seed,'N':n,'cols':cols,'condition':cond,'execution':mode,'policy':pol,'horizon_ticks':h,'port':port,'input_id':d.name})
write(H/'runs.json',{'runs':runs,'protocol_sha256':sha(H/'PROTOCOL.md')});print('registered',len(runs))
