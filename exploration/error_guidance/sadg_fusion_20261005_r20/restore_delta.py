"""Verify the published delta; optionally restore files without overwriting differences."""
from pathlib import Path
import argparse
import hashlib
import json
import tarfile

HERE=Path(__file__).resolve().parent
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--destination',type=Path)
    args=ap.parse_args();folder=HERE/'publication_delta'
    manifest=json.loads((folder/'MANIFEST.json').read_text())
    expected={'R20/'+e['path']:e for e in manifest['files']}
    assert len(expected)==len(manifest['files'])
    destination=args.destination.resolve() if args.destination else None
    seen=set();restored=0
    for part in manifest['parts']:
        path=folder/part['path'];assert sha(path)==part['sha256']
        with tarfile.open(path,'r:gz') as tar:
            for member in tar:
                assert member.isfile() and member.name in expected and member.name not in seen
                entry=expected[member.name];seen.add(member.name)
                data=tar.extractfile(member).read()
                assert len(data)==entry['bytes'] and hashlib.sha256(data).hexdigest()==entry['sha256']
                if destination:
                    target=(destination/entry['path']).resolve()
                    assert target.is_relative_to(destination), 'archive path outside destination'
                    target.parent.mkdir(parents=True,exist_ok=True)
                    if target.exists():assert sha(target)==entry['sha256'], f'existing different file: {target}'
                    else:
                        with target.open('xb') as f:f.write(data)
                        restored+=1
    assert seen==set(expected)
    print(json.dumps(dict(passed=True,verified_files=len(seen),newly_restored_files=restored,
        external_references=manifest['external_references'])))

if __name__=='__main__':main()
