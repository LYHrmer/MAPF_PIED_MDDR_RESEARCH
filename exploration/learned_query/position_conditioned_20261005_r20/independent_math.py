"""Independent R20 numerical audit; imports neither trainer nor deployment code."""
import math
from scipy.special import log_ndtr

NAMES = ['log_nominal', 'progress', 'log_remaining_fraction', 'log1p_capture_age_ratio',
         'log1p_history_count', 'log_history_ratio', 'log_ewma03_ratio', 'log_last_ratio',
         'history_cv', 'log1p_age_excess', 'progress_log1p_capture_age_ratio']


def history_summary(history):
    pairs=[(float(h['nominal_duration']),float(h['duration'])) for h in history]
    if any(not math.isfinite(n+d) or n<=0 or d<=0 for n,d in pairs):
        raise ValueError('Invalid completed history')
    ratios=[d/n for n,d in pairs]
    avg=sum(d for n,d in pairs)/sum(n for n,d in pairs) if pairs else 1.
    ewma=1.
    for ratio in ratios: ewma=.7*ewma+.3*ratio
    arithmetic=sum(ratios)/len(ratios) if ratios else 1.
    cv=(sum((v-arithmetic)**2 for v in ratios)/len(ratios))**.5/arithmetic if ratios else 0.
    return {'count':len(pairs),'all_history':avg,'ewma03':ewma,'last':ratios[-1] if ratios else 1.,
            'recent4':sum(d for n,d in pairs[-4:])/sum(n for n,d in pairs[-4:]) if pairs else 1.,'cv':cv}


def feature_vector(nominal, capture_age, progress, history):
    s=history_summary(history);a=capture_age/nominal;la=math.log1p(a)
    return [math.log(nominal),progress,math.log(max(1-progress,1e-6)),la,
            math.log1p(s['count']),math.log(s['all_history']),math.log(s['ewma03']),
            math.log(s['last']),s['cv'],math.log1p(max(0.,a-progress*s['ewma03'])),progress*la]


def residual_mean(mu,sigma,age):
    if age == 0: return math.exp(mu+sigma*sigma/2),1.
    z=(math.log(age)-mu)/sigma
    log_s=float(log_ndtr(-z))
    log_t=mu+sigma*sigma/2+float(log_ndtr(sigma-z))-log_s
    result=max(1e-9,age*math.expm1(max(0.,log_t-math.log(age))))
    return result,math.exp(log_s) if log_s>-745 else 0.


def evaluate_position(context,model,constant=False):
    """Same public API as PositionPredictor, independently evaluated with SciPy.

    Identity and arithmetic checks are necessary but the caller must separately
    prove START/END/delivery times and the capture history from actual receipts.
    """
    status=context['status']
    if status=='COMPLETED':
        return {'remaining_time':0.,'metadata':{'completed':True}}
    if status!='IN_PROGRESS': raise ValueError('Only active occurrence can consume POSITION')
    if set(context)!={'status','occurrence_id','nominal_duration','elapsed','completed_history','position'}:
        raise ValueError('Non-public or missing context field')
    pos=context['position']
    if not isinstance(pos,dict) or set(pos)!={'occurrence_id','progress','captured_elapsed','age','delivered_age'}:
        raise ValueError('Position contract mismatch')
    if not context['occurrence_id'] or pos['occurrence_id']!=context['occurrence_id']:
        raise ValueError('Stale occurrence')
    n=float(context['nominal_duration']);e=float(context['elapsed'])
    p=float(pos['progress']);c=float(pos['captured_elapsed']);a=float(pos['age']);d=float(pos['delivered_age'])
    if not all(math.isfinite(v) for v in [n,e,p,c,a,d]) or n<=0 or min(e,c,a,d)<0 or not 0<=p<=1:
        raise ValueError('Invalid progress or time')
    if d>a+1e-9 or abs(e-c-a)>1e-8*max(1.,e): raise ValueError('Delivery or START-age inconsistency')
    if any(h.get('vertex')==context['occurrence_id'] for h in context['completed_history']):
        raise ValueError('Current END in history')
    if model['schema']!='r20-position-capture-lognormal-v1' or model['feature_names']!=NAMES:
        raise ValueError('Model schema mismatch')
    if constant:
        mu_ratio=float(model['constant']['mu']);sigma=float(model['constant']['sigma'])
    else:
        x=feature_vector(n,c,p,context['completed_history'])
        mu_ratio=model['intercept']+sum((x[i]-model['mean'][i])/model['scale'][i]*model['coefficients'][i] for i in range(len(x)))
        sigma=float(model['sigma'])
    sigma=max(.05,min(5.,sigma));mu=math.log(n)+max(-20.,min(20.,mu_ratio))
    remaining,survival=residual_mean(mu,sigma,a)
    return {'remaining_time':remaining,'metadata':{'mu_log_capture_remaining':mu,'sigma':sigma,
        'capture_remaining_mean':math.exp(mu+sigma*sigma/2),'survival_probability':survival}}


def evaluate_end(model,history,nominal,elapsed,mode):
    s=history_summary(history)
    if mode=='learned':
        x=[math.log(nominal),math.log1p(s['count']),math.log(s['all_history']),math.log(s['recent4']),
           math.log(s['ewma03']),math.log(s['last']),s['cv'],math.log(s['recent4'])-math.log(s['all_history'])]
        mr=model['intercept']+sum((v-m)/scale*b for v,m,scale,b in zip(x,model['mean'],model['scale'],model['coefficients']))
        sig=model['sigma']
    else:
        sig=model['baseline_sigma']['ewma03'];mr=math.log(s['ewma03'])-sig*sig/2
    return residual_mean(math.log(nominal)+max(-20.,min(20.,mr)),max(.05,min(5.,sig)),elapsed)[0]


def make_context(row,age=None):
    age=row['age'] if age is None else age
    return dict(status='IN_PROGRESS',occurrence_id=row['vertex'],nominal_duration=row['nominal'],
        elapsed=row['capture_elapsed']+age,completed_history=row['history'],
        position=dict(occurrence_id=row['vertex'],progress=row['progress'],
            captured_elapsed=row['capture_elapsed'],age=age,
            delivered_age=min(age,row['delivered']-row['captured'])))
