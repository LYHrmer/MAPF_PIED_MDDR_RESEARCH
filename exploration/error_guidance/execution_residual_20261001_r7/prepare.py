from pathlib import Path
import hashlib,json,random,shutil,xml.etree.ElementTree as ET
HERE=Path(__file__).resolve().parent;PARENT=HERE.parent/'published_continuous_execution_20261001_r6c'
MAIN=Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence');OUT=MAIN/HERE.name;OLD=MAIN/PARENT.name
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2)+'\n')

def main():
 assert not OUT.exists();OUT.mkdir()
 runs=[]
 for split,seeds,conditions,policies in [('train',[931701,931702],['nominal','slow065','axis'],['hm_GPIBT']),('calibration',[931711],['nominal','slow065','axis'],['hm_GPIBT']),('test',[931721],['nominal','axis','unknown_shift'],['hm_GPIBT','trained','history','learned'])]:
  for seed in seeds:
   for name in ['empty-32-32','random-32-32-10']:
    parent=PARENT/'inputs'/name;inp=HERE/'inputs'/f'{name}_{seed}';inp.mkdir(parents=True)
    layout=json.loads((parent/'map.json').read_text())['layout'];env=json.loads((parent/'environment.json').read_text());starts=env['starts'][:8]
    free=[i*32+j for i,row in enumerate(layout) for j,v in enumerate(row) if v!='@'];fifo=[]
    for a,start in enumerate(starts):
     rng=random.Random(f'r7:{seed}:{name}:{a}');seq=[];last=start
     for _ in range(1002):
      candidates=[v for v in free if v!=last];last=candidates[rng.randrange(len(candidates))];seq.append(last)
     fifo.append(seq)
    shutil.copyfile(parent/'map.json',inp/'map.json')
    write(inp/'environment.json',{'starts':starts,'FIFO_goals':fifo,'seed':seed,'future_lists_visible_to_actor':False,'source_map_sha256':env['source_map_sha256'],'source_scenario_sha256':env['source_scenario_sha256']})
    (inp/'tasks_n8.txt').write_text('8\n'+'\n'.join(';'.join(f'{g},-1,0,0' for g in seq) for seq in fifo)+'\n')
    for cond in conditions:
     for policy in policies:
      number=len(runs);ident=f'{split}_{name}_{seed}_{cond}_{policy}';port=9580+number
      cfg=json.loads((PARENT/('trained_config.json' if policy=='trained' else 'hm_GPIBT_config.json')).read_text());cfg['initial_priority_seed']=seed
      write(HERE/'configs'/(ident+'.json'),cfg)
      xml=ET.parse(parent/'experiment_n8.argos');root=xml.getroot()
      root.find('controllers/footbot_diffusion_controller/params').set('simDuration','4000');root.find('controllers/footbot_diffusion_controller/params').set('portNumber',str(port));root.find('loop_functions/port_number').set('value',str(port));root.find('framework/experiment').set('random_seed',str(seed))
      (HERE/'xml').mkdir(exist_ok=True);xml.write(HERE/'xml'/(ident+'.argos'),encoding='unicode',xml_declaration=True)
      runs.append({'id':ident,'split':split,'map':name,'N':8,'horizon_ticks':4000,'dt_seconds':.1,'policy':policy,'condition':cond,'seed':seed,'port':port,'input_id':inp.name})
 write(HERE/'runs.json',{'runs':runs,'protocol_sha256':sha(HERE/'PROTOCOL.md')})
 binaries=json.loads((PARENT/'binary_manifest.json').read_text())
 write(HERE/'inherited_binary_manifest.json',binaries)
 write(HERE/'inherited_freeze_pin.json',{'path':str(PARENT/'freeze.json'),'sha256':sha(PARENT/'freeze.json')})
 print('prepared',len(runs),'runs',OUT)
if __name__=='__main__':main()
