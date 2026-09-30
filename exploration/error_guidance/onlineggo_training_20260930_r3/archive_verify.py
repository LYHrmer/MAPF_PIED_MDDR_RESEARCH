"""Verify the portable raw archive without extracting or running its contents."""
import hashlib
import json
from pathlib import Path
import tarfile

HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((HERE/'native_archive_manifest.json').read_text())
archive=HERE/'native_evidence.tar.gz'
assert sha(archive)==m['native_archive_sha256'] and archive.stat().st_size==m['native_archive_bytes']
seen=set()
with tarfile.open(archive,'r:gz') as tar:
    for member in tar:
        assert member.isfile() and member.name not in seen and '..' not in Path(member.name).parts
        assert not Path(member.name).is_absolute();seen.add(member.name)
        expected=m['native_files'][member.name]
        data=tar.extractfile(member).read()
        assert len(data)==expected['bytes'] and hashlib.sha256(data).hexdigest()==expected['sha256']
assert seen==set(m['native_files'])
for name,digest in m['upstream_context'].items():assert sha(HERE/'upstream_context'/name)==digest
for stage in [0,1]:
    result=json.loads((HERE/f'training_02/generation_{stage}_results.json').read_text())
    assert len(result)==100
    for row in result:
        for replica in row['replicas']:
            prefix='attempt02/'+replica['label']+'/'
            assert m['native_files'][prefix+'job.json']['sha256']==replica['job_sha256']
            assert m['native_files'][prefix+'job.result.json']['sha256']==replica['result_sha256']
out={'passed':True,'native_files':len(seen),'archive_bytes':archive.stat().st_size,
     'source_files':len(m['upstream_context']),'verifier_sha256':sha(Path(__file__))}
(HERE/'archive_verification.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out))
