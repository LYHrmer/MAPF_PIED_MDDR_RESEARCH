"""Verify frozen bytes without extracting the experiment archive."""
import hashlib
import json
import tarfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
manifest = json.loads((HERE/'manifest.json').read_text())
archive = HERE/'frozen_package.tar.gz'
assert archive.stat().st_size == manifest['archive_bytes']
assert hashlib.sha256(archive.read_bytes()).hexdigest() == manifest['archive_sha256']
with tarfile.open(archive) as tar:
    members = tar.getmembers()
    assert len(members) == len(manifest['files']) == 509
    assert {m.name for m in members} == set(manifest['files'])
    for member in members:
        assert member.isfile()
        data = tar.extractfile(member).read()
        expected = manifest['files'][member.name]
        assert len(data) == expected['bytes']
        assert hashlib.sha256(data).hexdigest() == expected['sha256']
    original = tar.extractfile('artifact_manifest.json').read()
    assert hashlib.sha256(original).hexdigest() == manifest['frozen_original_manifest_sha256']
print('PASS: all 509 frozen experiment files preserved')
