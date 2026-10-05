"""Standalone descriptive figure; predictions and planning outcomes stay separate."""
from pathlib import Path
import json
import hashlib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

HERE=Path(__file__).resolve().parent
def main():
    analysis=json.loads((HERE/'ANALYSIS.json').read_text())
    rows={r['arm']:r for r in analysis['aggregates'] if r['stratum']=='core'}
    order=['history_no_query','learned_no_query','ewma_no_query','history_structural',
        'learned_structural','ewma_structural','fixed_update','history_rule']
    labels=['History / no query','Learned / no query','EWMA / no query',
        'History / structural','Learned / structural','EWMA / structural','Fixed update','History rule']
    colors=['#607d8b','#cf7041','#397960','#607d8b','#cf7041','#397960','#8b7b9f','#8b7b9f']
    ref=rows['history_no_query']['sum_completion']
    delta=[100*(rows[a]['sum_completion']/ref-1) for a in order]
    queries=[rows[a]['query_count'] for a in order]
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
    fig,axes=plt.subplots(1,2,figsize=(10.5,4.7),sharey=True,gridspec_kw={'width_ratios':[1.2,1]})
    yy=np.arange(len(order))
    axes[0].barh(yy,delta,color=colors,height=.65)
    axes[0].axvline(0,color='black',linewidth=.8)
    axes[0].set_yticks(yy,labels);axes[0].invert_yaxis()
    axes[0].set_xlabel('Change in total completion time (%)\nrelative to History / no query; lower is better')
    axes[0].set_title('A  Complete execution outcome',loc='left')
    width=max(abs(x) for x in delta) or .01
    axes[0].set_xlim(min(0,min(delta))-width*.18,max(0,max(delta))+width*.3)
    for y,v in zip(yy,delta):
        if v:
            axes[0].text(v/2,y,f'{v:+.4f}',va='center',ha='center',fontsize=8,color='white')
        else:
            axes[0].annotate(f'{v:+.4f}',(v,y),xytext=(4,0),textcoords='offset points',
                va='center',ha='left',fontsize=8)
    axes[1].barh(yy,queries,color=colors,height=.65)
    axes[1].set_xlabel('Total requested queries')
    axes[1].set_title('B  Information acquisition',loc='left')
    axes[1].set_xlim(0,max(queries)*1.16 if max(queries) else 1)
    for y,v in zip(yy,queries):axes[1].text(v+max(queries)*.015,y,str(v),va='center',fontsize=8)
    fig.suptitle('R19 fresh-scenario core: 36 paired worlds per method, 6 map–scenario families',fontsize=12)
    fig.text(.02,.02,'Author SADG core shared by all arms. Internal prediction/query factors; descriptive totals, not significance tests.',fontsize=9)
    fig.tight_layout(rect=(0,.065,1,.94))
    fig.savefig(HERE/'CORE_RESULTS.pdf',bbox_inches='tight')
    fig.savefig(HERE/'CORE_RESULTS.png',dpi=180,bbox_inches='tight')
    (HERE/'FIGURE_PROVENANCE.json').write_text(json.dumps(dict(
        source='ANALYSIS.json',sha256=hashlib.sha256((HERE/'ANALYSIS.json').read_bytes()).hexdigest(),
        statistic='pooled sum-completion relative difference; not family-mean percent',
        order=order,delta_percent=delta,query_count=queries),indent=2)+'\n')

if __name__=='__main__':main()
