"""Root verify explicit publication bytes, keeping agents' frozen outputs untouched."""
from pathlib import Path
import argparse
import hashlib
import json

ROOT=Path(__file__).resolve().parent


def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('directory',type=Path)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    folder=args.directory.resolve()
    manifest=json.loads((folder/'PUBLICATION_MEMBERS.json').read_text())
    if isinstance(manifest.get('files'),dict):
        items=[dict(path=k,**v) for k,v in manifest['files'].items()]
    elif isinstance(manifest.get('files'),list):
        frozen=json.loads((folder/'FROZEN_MANIFEST.json').read_text())['frozen_files']
        assert set(manifest['files'])==set(frozen)|{'FROZEN_MANIFEST.json'}
        items=[dict(path=k,**v) for k,v in frozen.items()]
    else:
        items=manifest['members']
    names=[];total=0
    for entry in items:
        p=folder/entry['path'];names.append(entry['path'])
        assert p.resolve().is_relative_to(folder) and p.is_file(),entry['path']
        assert p.stat().st_size==entry['bytes'] and sha(p)==entry['sha256'],entry['path']
        assert p.stat().st_size<45*1024**2,entry['path']
        total+=p.stat().st_size
    assert len(set(names))==len(names)
    archive_path=folder/'archive_manifest.json'
    if not archive_path.exists():archive_path=folder/'RAW_ARCHIVE_MANIFEST.json'
    archives=members=0
    if archive_path.exists():
        archive=json.loads(archive_path.read_text())
        for entry in archive['archives']:
            p=folder/entry['path']
            assert sha(p)==entry['sha256'] and p.stat().st_size==entry['bytes']
            assert entry['path'] in names
            archives+=1;members+=len(entry['members'])
    out={'passed':True,'directory':str(folder),'publication_files':len(names),
         'publication_bytes':total,'raw_archives':archives,'manifest_raw_members':members,
         'scope':'all explicit publication hashes/sizes and archive-container bindings; full decompressed member audit retained separately by producer',
         'manifest_sha256':sha(folder/'PUBLICATION_MEMBERS.json')}
    args.output.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out))


if __name__=='__main__':main()
