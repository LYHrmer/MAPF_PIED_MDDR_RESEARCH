"""Plot every registered R10 geometry/history condition from measured results."""
from pathlib import Path
import hashlib
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

ROOT=Path(__file__).resolve().parent
DATA=ROOT.parent/'geometry_history_20261003_r10'
summary=json.loads((DATA/'summary.json').read_text())
prediction=json.loads((DATA/'prediction_same_hm_traces.json').read_text())
worlds=sorted(summary['worlds'],key=lambda w:(w['map'],w['seed'],w['condition']!='nominal'))
policies=['history','geometry','learned']
names=['History','Geometry','Full model']
labels=[('E' if w['map'].startswith('empty') else 'R')+str(w['seed'])[-2:]+('N' if w['condition']=='nominal' else 'A') for w in worlds]
tasks=np.array([[w[p]['tasks']-w['hm']['tasks'] for w in worlds] for p in policies])
time=np.array([[(w['hm']['restricted']-w[p]['restricted'])/10 for w in worlds] for p in policies])
assert tasks.sum(axis=1).tolist()==[-8,-8,-8]
assert np.allclose(time.sum(axis=1),[-748.2,-747.2,-735.2])
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':7,'axes.linewidth':.6,
                     'pdf.fonttype':42,'svg.fonttype':'none','savefig.facecolor':'white'})
fig=plt.figure(figsize=(7.09,5.0))
gs=fig.add_gridspec(3,2,height_ratios=[1,1,1.0],width_ratios=[1,.024],left=.14,right=.94,bottom=.1,top=.94,hspace=.84,wspace=.04)
cmap=LinearSegmentedColormap.from_list('loss_gain',['#B94A48','#ffffff','#2F6B9A'])
for i,(values,title,letter) in enumerate([(tasks,'Completed tasks relative to author hm (higher is better)','a'),
                                          (time,'Fixed FIFO completion-time saving (seconds; higher is better)','b')]):
    ax=fig.add_subplot(gs[i,0]);cax=fig.add_subplot(gs[i,1]);limit=max(1,float(np.abs(values).max()))
    im=ax.imshow(values,aspect='auto',cmap=cmap,vmin=-limit,vmax=limit)
    ax.set_yticks(range(3),names);ax.set_xticks(range(16),labels,rotation=50,ha='right',fontsize=6)
    ax.tick_params(length=0,pad=3)
    for r in range(3):
        for c in range(16):
            v=values[r,c]
            txt=f'{v:g}' if i==0 else f'{v:.1f}'
            ax.text(c,r,txt,ha='center',va='center',fontsize=5.8,color='white' if abs(v)>limit*.6 else '#252525')
    ax.axvline(7.5,color='#444444',lw=.9)
    ax.set_title(title,loc='left',fontsize=7.5,pad=9)
    ax.text(-.16,1.10,letter,transform=ax.transAxes,fontweight='bold',fontsize=9)
    cb=fig.colorbar(im,cax=cax);cb.ax.tick_params(labelsize=6,width=.5,length=2)
    for s in ax.spines.values():s.set_visible(False)
ax=fig.add_subplot(gs[2,0]);x=np.arange(3);width=.30
for i,(metric,color) in enumerate([('MAE','#2F6B9A'),('RMSE','#D97732')]):
    values=[prediction['all_motion'][p][metric] for p in policies]
    bars=ax.bar(x+(i-.5)*width,values,width,color=color,label=metric)
    for b,v in zip(bars,values):ax.text(b.get_x()+b.get_width()/2,v+.045,f'{v:.3f}',ha='center',fontsize=6)
ax.set_xticks(x,names);ax.set_ylim(0,4.2);ax.set_ylabel('Ticks (0.1 s)')
ax.set_title('Prediction error on the same 16 author-hm traces',loc='left',fontsize=7.5,pad=9)
ax.text(-.16,1.10,'c',transform=ax.transAxes,fontweight='bold',fontsize=9)
ax.spines[['top','right']].set_visible(False);ax.legend(frameon=False,loc='upper right',ncol=2,fontsize=6)
fig.text(.14,.014,'8 paired task families · E/R: empty/random map · N/A: nominal/axis perturbation · N=8, horizon=400 s',fontsize=6)
fig.canvas.draw()
renderer=fig.canvas.get_renderer();canvas=fig.bbox
outside=[]
for t in fig.findobj(matplotlib.text.Text):
    if t.get_visible() and t.get_text():
        b=t.get_window_extent(renderer)
        if b.x0<canvas.x0-1 or b.x1>canvas.x1+1 or b.y0<canvas.y0-1 or b.y1>canvas.y1+1:outside.append(t.get_text())
assert not outside,outside
for ext in ['svg','pdf']:
    fig.savefig(ROOT/('attribution_all_conditions.'+ext))
fig.savefig(ROOT/'attribution_all_conditions.png',dpi=600)
fig.savefig(ROOT/'attribution_preview.png',dpi=150)
manifest={'real_measured_data':True,'all_registered_conditions':len(worlds),'independent_families':8,
          'source_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [DATA/'summary.json',DATA/'prediction_same_hm_traces.json']},
          'no_outside_canvas_text':True,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
(ROOT/'FIGURE_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps(manifest))
