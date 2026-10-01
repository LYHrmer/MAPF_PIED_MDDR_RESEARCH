from pathlib import Path
import hashlib,importlib.util,json
HERE=Path(__file__).resolve().parent;OUT=Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence')/HERE.name
SOURCE=HERE.parent/'published_continuous_root_review_20261001_r6/verify_physical_clearance_20261001_r6.py'
sp=importlib.util.spec_from_file_location('geometry',SOURCE);geometry=importlib.util.module_from_spec(sp);sp.loader.exec_module(geometry)
def main():
 results={}
 for spec in json.loads((HERE/'runs.json').read_text())['runs']:
  result=geometry.audit(OUT/'runs'/spec['id'],.095036758)
  assert result['ticks']==4000 and result['observations']==32000
  results[spec['id']]=result
  print(spec['id'],result['all_sampled_circular_envelopes_separated'],flush=True)
 (HERE/'sampled_geometry.json').write_text(json.dumps({'inherited_independent_auditor':str(SOURCE),'auditor_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'runs':results,'all_sampled_separated':all(r['all_sampled_circular_envelopes_separated'] for r in results.values()),'continuous_safety_claim':False},indent=2)+'\n')
if __name__=='__main__':main()
