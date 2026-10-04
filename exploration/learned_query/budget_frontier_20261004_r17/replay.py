#!/usr/bin/env python3
"""Recompute all offline products in a new output directory, preserving originals."""
from pathlib import Path
import argparse,importlib.util,shutil,sys
sys.dont_write_bytecode=True
B=Path(__file__).resolve().parent
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output-dir',type=Path,required=True);a=p.parse_args();out=a.output_dir.resolve()
 if out.exists():raise SystemExit('Output must be a new directory; existing products are never overwritten.')
 out.mkdir(parents=True)
 for name in ['PROTOCOL.md','REGISTRATION.json','ANALYSIS_START.json']:shutil.copy2(B/name,out/name)
 spec=importlib.util.spec_from_file_location('frozen_study',B/'study.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);module.HERE=out;module.main()
if __name__=='__main__':main()
