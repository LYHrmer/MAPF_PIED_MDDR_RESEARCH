"""Publish complete new native traces and receipts, not build intermediates."""
import hashlib
import json
from pathlib import Path
import tarfile

HERE=Path(__file__).resolve().parent
MAIN=Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence')
RAW=MAIN/'published_guidance_comparison_20260930_r4'
UP=MAIN/'baseline_selection_20260929/OnlineGGO'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
def main():
    target=HERE/'native_evidence.tar.gz';assert not target.exists()
    paths=sorted(p for p in RAW.rglob('*') if p.is_file() and 'build_hm' not in p.relative_to(RAW).parts)
    paths += [RAW/'build_hm/CMakeCache.txt',RAW/'build_hm/CMakeFiles/py_driver.dir/flags.make']
    entries=[]
    with tarfile.open(target,'w:gz') as archive:
        for p in paths:
            name=str(p.relative_to(RAW));archive.add(p,arcname=name,recursive=False)
            entries.append({'path':name,'bytes':p.stat().st_size,'sha256':sha(p)})
        license=UP/'LICENSE';archive.add(license,arcname='upstream_LICENSE',recursive=False)
        entries.append({'path':'upstream_LICENSE','bytes':license.stat().st_size,'sha256':sha(license)})
    with tarfile.open(target,'r:gz') as archive:
        assert set(archive.getnames())=={r['path'] for r in entries}
        for row in entries:
            data=archive.extractfile(row['path']).read()
            assert len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256']
    write(HERE/'archive_manifest.json',{'passed':True,'archive_sha256':sha(target),'entries':entries})
    print(json.dumps({'archive_bytes':target.stat().st_size,'verified_files':len(entries)}))
if __name__=='__main__':main()
