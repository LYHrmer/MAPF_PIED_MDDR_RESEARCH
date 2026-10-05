"""R20 public POSITION-conditioned capture residual. Standard-library runtime."""
import json
import math
from pathlib import Path

from end_predictor import conditional_mean, summarize

FEATURE_NAMES = [
    'log_nominal', 'progress', 'log_remaining_fraction', 'log1p_capture_age_ratio',
    'log1p_history_count', 'log_history_ratio', 'log_ewma03_ratio', 'log_last_ratio',
    'history_cv', 'log1p_age_excess', 'progress_log1p_capture_age_ratio',
]
MODES = ['position_learned', 'position_constant', 'history_linear', 'ewma_linear',
         'end_learned', 'end_ewma_survival', 'observed_average']


def features(nominal, capture_elapsed, progress, stats):
    age_ratio = capture_elapsed / nominal
    log_age = math.log1p(age_ratio)
    return [math.log(nominal), progress, math.log(max(1.0-progress, 1e-6)), log_age,
            math.log1p(stats['count']), math.log(stats['all_history']),
            math.log(stats['ewma03']), math.log(stats['last']), stats['cv'],
            math.log1p(max(0.0, age_ratio-progress*stats['ewma03'])), progress*log_age]


def distribution(model, nominal, capture_elapsed, progress, stats, constant=False):
    if constant:
        mu_ratio, sigma = model['constant']['mu'], model['constant']['sigma']
    else:
        x = features(nominal, capture_elapsed, progress, stats)
        z = [(v-m)/s for v,m,s in zip(x, model['mean'], model['scale'])]
        mu_ratio = model['intercept'] + sum(v*b for v,b in zip(z, model['coefficients']))
        sigma = model['sigma']
    # Registered numerical domain guards, inherited from the R19 arithmetic.
    mu_ratio = min(20.0, max(-20.0, mu_ratio))
    return math.log(nominal)+mu_ratio, min(5.0, max(0.05, sigma))


def predict_values(model, nominal, capture_elapsed, progress, age, stats, constant=False):
    mu, sigma = distribution(model, nominal, capture_elapsed, progress, stats, constant)
    remaining, survival = conditional_mean(mu, sigma, age)
    return remaining, dict(method='position_constant' if constant else 'position_learned',
        mu_log_capture_remaining=mu, sigma=sigma, capture_remaining_mean=math.exp(mu+.5*sigma*sigma),
        survival_probability=survival, observation_age=age,
        conditions_on='same occurrence not END at current time', calibrated_probability=False)


class PositionPredictor:
    """Caller must provide a delivered POSITION and its capture-time END prefix.

    Public timestamp/source authentication and the correctness of the history cut
    belong to the execution adapter; no private state is queried by this module.
    """
    def __init__(self, model_path, mode='position_learned'):
        self.model = json.loads(Path(model_path).read_text()) if not isinstance(model_path, dict) else model_path
        if self.model['schema'] != 'r20-position-capture-lognormal-v1' or self.model['feature_names'] != FEATURE_NAMES:
            raise ValueError('Position model/schema mismatch')
        if mode not in ('position_learned', 'position_constant'):
            raise ValueError('Unsupported position runtime mode')
        self.mode = mode

    def __call__(self, context):
        status = context['status']
        if status == 'COMPLETED':
            return dict(remaining_time=0.0, metadata=dict(method=self.mode, completed=True))
        if status != 'IN_PROGRESS':
            raise ValueError('POSITION residual requires an active occurrence; dependency WAIT is not elapsed')
        required = {'status', 'occurrence_id', 'nominal_duration', 'elapsed', 'completed_history', 'position'}
        if set(context) != required:
            raise ValueError('Position context must contain exactly the public contract fields')
        position = context['position']
        pfields = {'occurrence_id', 'progress', 'captured_elapsed', 'age', 'delivered_age'}
        if not isinstance(position, dict) or set(position) != pfields:
            raise ValueError('Missing or malformed delivered POSITION')
        if not context['occurrence_id'] or position['occurrence_id'] != context['occurrence_id']:
            raise ValueError('Stale POSITION occurrence')
        nominal, elapsed = float(context['nominal_duration']), float(context['elapsed'])
        capture, age, delivered, progress = (float(position[k]) for k in
                                              ['captured_elapsed', 'age', 'delivered_age', 'progress'])
        if not all(math.isfinite(v) for v in [nominal, elapsed, capture, age, delivered, progress]):
            raise ValueError('Public times and progress must be finite')
        if nominal <= 0 or min(elapsed, capture, age, delivered) < 0 or not 0 <= progress <= 1:
            raise ValueError('Invalid public time/progress range')
        if delivered > age+1e-9 or abs(elapsed-capture-age) > 1e-8*max(1.0, elapsed):
            raise ValueError('Undelivered POSITION or inconsistent START-relative age')
        for h in context['completed_history']:
            if h.get('vertex') == context['occurrence_id']:
                raise ValueError('Current occurrence END leaked into history')
        stats = summarize(context['completed_history'])
        remaining, metadata = predict_values(self.model, nominal, capture, progress, age, stats,
                                              self.mode == 'position_constant')
        metadata['feature_names'] = FEATURE_NAMES
        return dict(remaining_time=remaining, metadata=metadata)

    predict = __call__
