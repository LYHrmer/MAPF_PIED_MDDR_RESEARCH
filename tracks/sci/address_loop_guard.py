"""Common root-bound termination overlay; no Instance, search or build here.

Apply after address_adapter.adapt, before any recovery-policy overlay. This is
shared engineering: a valid unit-cost incumbent at sum(static h) cannot improve
SOC. The ordinary run() exit and the adapter's complete final checks remain.
"""

LOOP_ANCHOR = ('    while (runtime < time_limit && iteration_stats.size() <= num_of_iterations)\n'
               '    {\n')
GUARD = ('        // Shared termination: the validated incumbent attains its static SOC bound.\n'
         '        if (sum_of_costs == sum_of_distances)\n'
         '            break;\n')


def apply_loop_guard(files):
    """Return the one changed source; preserve the frozen base adapter inputs."""
    source = files['src/LNS.cpp'].decode()
    if ('#include "address_adapter_support.h"' not in source
            or 'neighbor.sum_of_costs = initial_sum_of_costs = sum_of_costs = cost;' not in source):
        raise ValueError('root-bound guard requires the common-initial adapter output')
    if source.count(LOOP_ANCHOR) != 1 or GUARD in source:
        raise ValueError('root-bound loop anchor drifted or guard already applied')
    return {'src/LNS.cpp': source.replace(LOOP_ANCHOR, LOOP_ANCHOR+GUARD, 1).encode()}


def adapt(files):
    """Build-extension entry: input is author sources merged with base adapter."""
    return apply_loop_guard(files)
