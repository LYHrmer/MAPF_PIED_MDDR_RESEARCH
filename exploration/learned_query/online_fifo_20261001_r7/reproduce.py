"""Run the frozen statistical protocol into a NEW output directory."""
from pathlib import Path
import sys
import pipeline
out=Path(sys.argv[1]).resolve();assert not out.exists(),'reproduction needs a fresh destination';pipeline.OUT=out;pipeline.main()
