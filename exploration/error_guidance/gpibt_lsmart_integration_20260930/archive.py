from pathlib import Path
import shutil,json,hashlib
HERE=Path(__file__).resolve().parent
OUT=Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence/gpibt_lsmart_integration_20260930')
for name in ['nominal_attempt01','nominal_attempt02']:
    shutil.copytree(OUT/name,HERE/'attempts'/name,dirs_exist_ok=True)
for p in OUT.glob('*/receipt.json'):
    if p.parent.name.startswith(('build','configure')):
        dst=HERE/'build_receipts'/p.parent.name
        dst.mkdir(parents=True,exist_ok=True)
        for f in p.parent.iterdir():
            if f.is_file():shutil.copy2(f,dst/f.name)
# Final binaries are build-verified, never represented as the failed run binaries.
manifest=json.loads((HERE/'binary_manifest.json').read_text())
for p in list(manifest):
    manifest[p]=hashlib.sha256(Path(p).read_bytes()).hexdigest()
(HERE/'binary_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
(HERE/'artifact_manifest.json').write_text(json.dumps({str(p.relative_to(HERE)):hashlib.sha256(p.read_bytes()).hexdigest() for p in HERE.rglob('*') if p.is_file() and p.name!='artifact_manifest.json'},indent=2)+'\n')
print('archived failed attempts, build receipts, final binary identities')
