from pathlib import Path
import json,shutil,xml.etree.ElementTree as E
H=Path(__file__).resolve().parent;O=Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence')/H.name
r=json.loads((H/'runs.json').read_text());src=H/'inputs/mechanical_941800';dst=H/'inputs/midpoint_941800';shutil.copytree(src,dst)
env=json.loads((dst/'environment.json').read_text())
for a,s in enumerate(env['starts']):env['FIFO_goals'][a][0]=s+1
(dst/'environment.json').write_text(json.dumps(env,indent=2)+'\n');(dst/'tasks_n4.txt').write_text('4\n'+'\n'.join(';'.join(f'{g},-1,0,0' for g in seq) for seq in env['FIFO_goals'])+'\n')
for mode in ['global','local']:
 old=next(s for s in r['runs'] if s['split']=='mechanical' and s['condition']=='nominal' and s['execution']==mode);s=dict(old);s['id']='midpoint_'+old['id'];s['input_id']=dst.name;s['mechanical_case']='midpoint';s['port']=9820+len([x for x in r['runs'] if x.get('mechanical_case')=='midpoint']);r['runs'].append(s)
 shutil.copyfile(H/'configs'/(old['id']+'.json'),H/'configs'/(s['id']+'.json'));t=E.parse(H/'xml'/(old['id']+'.argos'));t.getroot().find('controllers/footbot_diffusion_controller/params').set('portNumber',str(s['port']));t.getroot().find('loop_functions/port_number').set('value',str(s['port']));t.write(H/'xml'/(s['id']+'.argos'),encoding='unicode',xml_declaration=True)
(H/'runs.json').write_text(json.dumps(r,indent=2)+'\n')
for d in (O/'runs').iterdir():d.rename(O/'failed_attempts'/(d.name+'_preorientation_refit_labels'))
