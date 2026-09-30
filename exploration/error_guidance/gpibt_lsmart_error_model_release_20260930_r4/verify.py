"""Verify the immutable experiment mirror without extracting it."""
import hashlib,json,tarfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
m=json.loads((HERE/'manifest.json').read_text())
archive=HERE/'frozen_package.tar.gz'
assert archive.stat().st_size==m['archive_bytes']
assert hashlib.sha256(archive.read_bytes()).hexdigest()==m['archive_sha256']
with tarfile.open(archive) as tar:
    members=tar.getmembers(); assert len(members)==len(m['files'])==572
    assert {t.name for t in members}==set(m['files'])
    original=json.load(tar.extractfile('artifact_manifest.json'))
    for member in members:
        assert member.isfile()
        data=tar.extractfile(member).read(); expected=m['files'][member.name]
        digest=hashlib.sha256(data).hexdigest()
        assert len(data)==expected['bytes'] and digest==expected['sha256']
        if member.name!='artifact_manifest.json': assert original[member.name]==digest
        else: assert digest==m['frozen_original_manifest_sha256']
print('PASS: 572 archived files, original frozen manifest preserved')
