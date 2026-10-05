# R18 execution orchestration

The original `run_benchmark.py all` tool session 36434 completed all TRAIN data collection, froze the model, completed all 135 CAL episodes, and completed all 90 random-map TEST episodes. After the freeze, independent warehouse and maze TEST workers called the exact frozen `register()` and `episode()` functions with the same registered specifications. No scientific code, model, split, world, budget, or disturbance setting changed.

Warehouse helper session 51928 completed with exit code 0. Maze helper session 11875 is managed independently by the engine worker. Their own registration, progress, completion and process records are under `parallel/`.

At `2026-10-05T04:48:57.497791+00:00`, the original process reached an episode that the maze worker was still executing. It exited with code 1, preserving the following error:

```
RuntimeError: unfinished attempt requires live-process inspection before rerun: /home/lyh/MAPF_LMAPF_ERROR_GUIDANCE_EXPLORE/exploration/error_guidance/sadg_benchmark_20261005_r18/episodes/TEST/maze-32-32-2__s04__n32__bounded_pause/dense_position
```

This is an orchestration refusal to duplicate a live attempt, not a physical or solver failure of that episode. No `STARTED.json` was deleted and no live episode was restarted. Root verified the original process's terminal tool status and left the maze process running. Once all workers have terminated, the original evaluation command can verify and reuse every complete receipt before final summarization; any missing episode would retain its registered specification.

Concurrent host solver and end-to-end wall times are retained as diagnostics. They are not a controlled single-process runtime comparison between policies. Simulated observation latency, action time, budget and completion metrics remain the registered quantities.

Maze session 11875 completed with exit code 0 at 04:59:25 UTC, with all 90 hashes verified. Root then ran the original `evaluate` command in tool session 51598: exit code 0, all 405 completed receipts reused, no new scientific episode. `PROGRESS.json` reached `execution_complete` at `2026-10-05T04:59:56.052536+00:00`; full resume stdout is `EVALUATION_RESUME.log`. The original `summarize` exited 0 with 405 rows and zero missing, followed by the read-only analyzer (exit 0). The final unique science episode count is 641.
