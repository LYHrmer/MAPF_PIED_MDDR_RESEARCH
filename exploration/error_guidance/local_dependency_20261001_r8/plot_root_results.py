"""Plot all paired worlds; no independence-based error bars or fitted trend."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

HERE=Path(__file__).resolve().parent
data=json.loads((HERE/'ROOT_EXECUTION_AUDIT.json').read_text())
shift=json.loads((HERE/'label_shift.json').read_text())
assert data['passed'] and data['episodes']==54
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,
                     'axes.spines.right':False,'svg.fonttype':'none','pdf.fonttype':42})
fig,axes=plt.subplots(1,3,figsize=(11.7,3.65),layout='constrained')
blue,orange='#286790','#BA5B2C'
rows=[r for r in data['rows'] if r['split']=='test']
index={(r['map'],r['seed'],r['condition'],r['execution'],r['policy']):r for r in rows}
worlds=sorted({k[:3] for k in index})
for i,world in enumerate(worlds):
    color=blue if world[0].startswith('empty') else orange
    marker='o' if world[2]=='nominal' else '^'
    y=[index[(*world,mode,'hm')]['served'] for mode in ('global','local')]
    axes[0].plot([0,1],y,color=color,marker=marker,alpha=.75,lw=1.2)
axes[0].set(xticks=[0,1],xticklabels=['Global gate','Local ADG'],ylabel='Completed FIFO tasks / episode',
            title='A  Shared execution improvement',ylim=(19.5,29.5),xlim=(-.2,1.2))
axes[0].text(.03,.96,'Official hm planner; 8 paired worlds',transform=axes[0].transAxes,va='top',fontsize=8)
for i,mode in enumerate(('global','local')):
    values=[]
    for j,world in enumerate(worlds):
        h=index[(*world,mode,'history')];m=index[(*world,mode,'learned')]
        assert h['served']==m['served']
        value=(m['fixed_first10_ticks']-h['fixed_first10_ticks'])/10
        values.append(value)
        color=blue if world[0].startswith('empty') else orange
        axes[1].scatter(i+(j-3.5)*.035,value,c=color,marker='o' if world[2]=='nominal' else '^',s=28,zorder=3)
    axes[1].text(i,-89,f'Sum: {sum(values):+.1f} s',ha='center',fontsize=8)
axes[1].axhline(0,color='#777777',lw=.8)
axes[1].set(xticks=[0,1],xticklabels=['Global gate','Local ADG'],xlim=(-.4,1.4),ylim=(-100,32),
            ylabel='Learned − history: fixed-prefix time (s)',title='B  Learning effect on completion times')
axes[1].text(.03,.96,'Task-count differences: 0 in all 16 pairs',transform=axes[1].transAxes,va='top',fontsize=8)
x=np.arange(2);width=.32
for offset,policy,color in [(-width/2,'history','#8DA6B3'),(width/2,'learned',blue)]:
    values=[shift['groups'][f'local_step{i}'][policy]['MAE'] for i in range(2)]
    bars=axes[2].bar(x+offset,values,width,label=policy,color=color)
    axes[2].bar_label(bars,fmt='%.2f',fontsize=8,padding=3)
axes[2].set(xticks=x,xticklabels=['Step 1','Step 2 (cumulative)'],ylabel='Prediction MAE (ticks)',
            title='C  Supervision-unit mismatch',ylim=(0,32))
axes[2].legend(frameon=False,loc='upper left',ncol=2,fontsize=8)
fig.supxlabel('Two maps × two task seeds × two paired conditions; N=8, horizon=4000 ticks. Global gate is an internal ablation.',fontsize=8)
for ax in axes:ax.grid(axis='y',alpha=.18);ax.set_axisbelow(True)
for extension in ('svg','pdf','png'):
    fig.savefig(HERE/f'root_results.{extension}',dpi=200)
print('Saved root_results.svg, .pdf, .png')
