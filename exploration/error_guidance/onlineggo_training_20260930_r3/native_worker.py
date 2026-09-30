"""Run one unchanged official native OnlineGGO evaluation in a fresh process."""
import importlib.util
import json
from pathlib import Path
import sys
import time

job_path = Path(sys.argv[1])
job = json.loads(job_path.read_text())
spec = importlib.util.spec_from_file_location("py_driver", job["module_path"])
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
start = time.monotonic()
result = json.loads(module.run(**job["kwargs"]))
receipt = {"result": result, "wall_seconds": time.monotonic() - start}
job_path.with_suffix(".result.json").write_text(json.dumps(receipt, indent=2) + "\n")
