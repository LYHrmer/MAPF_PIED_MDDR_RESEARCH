"""Adapt the existing exact parser/ADG/service verifier to declared team/map sizes."""
from pathlib import Path
HERE=Path(__file__).resolve().parent;P=HERE.parent/'gpibt_lsmart_error_model_20260930_r4c/mapping_replay.py'
s=P.read_text()
s=s.replace('def check(events,decisions,pause_expected=False,strict_point_endpoints=True):','def check(events,decisions,pause_expected=False,strict_point_endpoints=True,layout=None,N=2,horizon_ticks=800):')
s=s.replace("    layout=json.loads((HERE/'map.json').read_text())['layout']","    if layout is None:layout=json.loads((HERE/'map.json').read_text())['layout']\n    rows,cols=len(layout),len(layout[0])")
s=s.replace('range(2)','range(N)').replace('len(observed)==2','len(observed)==N').replace("s['unfinished']==[0,0]","s['unfinished']==[0]*N").replace("len(inst['starts'])==2 and len(inst['goals'])==2","len(inst['starts'])==N and len(inst['goals'])==N").replace("len(d['result']['actions'])==2","len(d['result']['actions'])==N").replace('len(paths)==2','len(paths)==N')
s=s.replace("[st['location']%5,st['location']//5]","[st['location']%cols,st['location']//cols]").replace('[1,5,-1,-5,0]','[1,cols,-1,-cols,0]').replace('[s//5,s%5]','[s//cols,s%cols]').replace('[t//5,t%5]','[t//cols,t%cols]').replace('0<=row<5 and 0<=col<5','0<=row<rows and 0<=col<cols').replace("int(a[5][1])*5+int(a[5][0])","int(a[5][1])*cols+int(a[5][0])").replace("e['tick']==800","e['tick']==horizon_ticks")
s=s.replace("                a,b=observed.values();min_sep=min(min_sep,distance(a,b))","                values=list(observed.values())\n                for a in range(N):\n                    for b in range(a):min_sep=min(min_sep,distance(values[a],values[b]))")
s=s.replace("            require(paths[0][1][:2]!=paths[1][1][:2],'vertex_collision')\n            require(not(paths[0][0][:2]==paths[1][1][:2] and paths[1][0][:2]==paths[0][1][:2]),'edge_swap')","            require(len({tuple(p[1][:2]) for p in paths})==N,'vertex_collision')\n            for a in range(N):\n                for b in range(a):require(not(paths[a][0][:2]==paths[b][1][:2] and paths[b][0][:2]==paths[a][1][:2]),'edge_swap')")
(HERE/'mapping_replay.py').write_text(s)
print('exact replay adapted; source retained via parent and script')
