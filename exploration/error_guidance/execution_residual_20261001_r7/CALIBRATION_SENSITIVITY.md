Calibration-only mechanism check: take the first four public current-head-change
decisions (including the initial decision) from every fixed calibration run.
Restore the exact baseline private planner state by replaying every preceding
request with zero edge additions and requiring identical actions/priorities.
At the selected call, separately supply same-history and learned costs; record
actual cost-call/nonzero-call counts and the returned official actions. Also
run a zero-cost current call and require an exact baseline match. Stop each
probe after that one call; do not pretend alternative actions were executed in
the baseline world. All zero effects remain. This check neither tunes the
mapping nor gates the predeclared test on a positive result.
