# R18 figure captions

`test_tradeoff`: TEST only, 54 worlds per arm, grouped into six independent map/scenario families. Left: completion-time sum relative to history-only; negative is lower. Each disturbance contains 18 paired worlds nested under six families; error bars are fixed-seed 10,000-resample family bootstrap 95% intervals, descriptive for this small benchmark. Zero-height bars are zero measured change, not missing data. Right: mean queries divided by team size. Fixed, rule and learned share the N cap; dense is explicitly uncapped. All test episodes completed safely, including preserved-parent fallbacks. Numerical plot data and input hash are in FIGURE_DATA.json and PROVENANCE.json.

`test_scale`: TEST completion-time sum divided by team size, averaged over two held-out scenarios and three disturbances per map/scale/arm. Each panel has its own y-axis. Lines frequently overlap because the measured execution outcomes are identical or very close; no artificial offset is added. This is a descriptive scale plot, not a model-generalization confidence interval. Full denominators and failures remain in ANALYSIS.json.

Both figures were generated from the frozen SUMMARY.json without running scientific episodes. Root visually inspected the exported PNG files for clipping, labels and consistency with the tabulated metrics. SVG and PDF remain editable; PNG exports use 600 dpi.
