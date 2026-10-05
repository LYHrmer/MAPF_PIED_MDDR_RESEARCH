"""Public END-history duration model. Runtime uses only the standard library."""
import json
import math
from pathlib import Path

FEATURE_NAMES = ['log_nominal', 'log1p_count', 'log_history_ratio',
                 'log_recent4_ratio', 'log_ewma03_ratio', 'log_last_ratio',
                 'history_cv', 'recent_minus_history']
MODES = ['nominal', 'all_history', 'recent4', 'ewma03', 'constant_survival',
         'all_history_survival', 'recent4_survival', 'ewma03_survival', 'learned']


def summarize(history):
    ratios = []
    total = nominal = 0.0
    ewma = 1.0
    for h in history:
        n, d = float(h['nominal_duration']), float(h['duration'])
        if not (math.isfinite(n) and math.isfinite(d) and n > 0 and d > 0):
            raise ValueError('History must contain positive finite completed durations')
        q = d / n
        ratios.append(q)
        total += d
        nominal += n
        ewma = 0.3*q + 0.7*ewma
    average = total / nominal if ratios else 1.0
    recent = history[-4:]
    recent_ratio = (sum(float(h['duration']) for h in recent) /
                    sum(float(h['nominal_duration']) for h in recent)) if recent else 1.0
    mean = sum(ratios)/len(ratios) if ratios else 1.0
    cv = math.sqrt(sum((r-mean)**2 for r in ratios)/len(ratios))/mean if ratios else 0.0
    return dict(count=len(ratios), all_history=average, recent4=recent_ratio,
                ewma03=ewma, last=ratios[-1] if ratios else 1.0, cv=cv)


def features(nominal, s):
    return [math.log(nominal), math.log1p(s['count']), math.log(s['all_history']),
            math.log(s['recent4']), math.log(s['ewma03']), math.log(s['last']),
            s['cv'], math.log(s['recent4'])-math.log(s['all_history'])]


def log_survival(z):
    if z < 8.0:
        return math.log(0.5*math.erfc(z/math.sqrt(2.0)))
    # Mills expansion, positive and accurate in the tail; avoids erfc underflow.
    q = 1.0/(z*z)
    correction = 1-q+3*q*q-15*q**3+105*q**4-945*q**5
    return -0.5*z*z - math.log(z) - 0.5*math.log(2*math.pi) + math.log(correction)


def conditional_mean(mu, sigma, elapsed):
    unconditional = math.exp(mu + 0.5*sigma*sigma)
    if elapsed <= 0:
        return unconditional, 1.0
    z = (math.log(elapsed)-mu)/sigma
    log_s = log_survival(z)
    log_total = mu + 0.5*sigma*sigma + log_survival(z-sigma)-log_s
    # expm1 limits cancellation when the conditional total is close to elapsed.
    residual = elapsed*math.expm1(max(0.0, log_total-math.log(elapsed)))
    return max(1e-9, residual), math.exp(log_s) if log_s > -745 else 0.0


def predict_values(model, mode, nominal, elapsed, stats):
    if mode not in MODES:
        raise ValueError('Unknown duration mode: '+mode)
    if mode in ('nominal', 'all_history', 'recent4', 'ewma03'):
        ratio = 1.0 if mode == 'nominal' else stats[mode]
        return max(0.0, nominal*ratio-elapsed), ratio, dict(method=mode, survival_probability=None)
    if mode == 'learned':
        f = features(nominal, stats)
        z = [(v-a)/b for v,a,b in zip(f,model['mean'],model['scale'])]
        mu_ratio = model['intercept'] + sum(a*b for a,b in zip(z,model['coefficients']))
        sigma = model['sigma']
    elif mode == 'constant_survival':
        mu_ratio, sigma = model['constant']['mu'], model['constant']['sigma']
    else:
        key = mode.removesuffix('_survival')
        sigma = model['baseline_sigma'][key]
        mu_ratio = math.log(stats[key])-0.5*sigma*sigma
    # Explicit numerical domain guard, not learned from held-out performance.
    mu_ratio = min(20.0, max(-20.0, mu_ratio))
    sigma = min(5.0, max(0.05, sigma))
    mu = math.log(nominal)+mu_ratio
    remaining, survival = conditional_mean(mu, sigma, elapsed)
    ratio = math.exp(mu_ratio+0.5*sigma*sigma)
    return remaining, ratio, dict(method=mode, mu_log_duration=mu, sigma=sigma,
        survival_probability=survival, unconditional_mean=nominal*ratio)


class DurationPredictor:
    def __init__(self, model_path, mode='learned'):
        self.model = json.loads(Path(model_path).read_text()) if not isinstance(model_path, dict) else model_path
        self.mode = mode
        if self.model['feature_names'] != FEATURE_NAMES or mode not in MODES:
            raise ValueError('Model/schema mismatch')

    def __call__(self, context):
        status = context['status']
        if status == 'COMPLETED':
            return dict(remaining_time=0.0, future_duration_ratio=1.0,
                        metadata=dict(method=self.mode, completed=True))
        if status not in ('STAGED', 'IN_PROGRESS'):
            raise ValueError('Unknown execution status')
        nominal, elapsed = float(context['nominal_duration']), float(context['elapsed'])
        if not (math.isfinite(nominal) and nominal > 0 and math.isfinite(elapsed) and elapsed >= 0):
            raise ValueError('Invalid nominal duration or elapsed')
        if status == 'STAGED' and elapsed != 0:
            raise ValueError('STAGED elapsed must exclude dependency waiting and equal zero')
        stats = summarize(context['completed_history'])
        r, ratio, meta = predict_values(self.model, self.mode, nominal, elapsed, stats)
        return dict(remaining_time=r, future_duration_ratio=ratio, metadata=meta)

    predict = __call__
