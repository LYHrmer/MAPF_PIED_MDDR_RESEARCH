#!/usr/bin/env python3
"""Upgrade prior successful audit caches by proving all bound inputs unchanged.

No solver math is rerun: the prior verifier hash and episode hash must match,
and every externally stored graph/model must still match its canonical content
hash that the prior audit already checked. Scientific source/input and runtime
receipts are freshly verified. An unverifiable dependency leaves the cache alone
for the regular auditor to recheck fully. This is not an experiment replay.
"""
import gzip
import json
from pathlib import Path
import sys
sys.dont_write_bytecode=True
from audit_episode import Auditor, canon, read
from audit_study import sha, evidence_fingerprint


def main():
    root=Path(__file__).resolve().parent.parent;auditor_hash=sha(Path(__file__).with_name('audit_episode.py'))
    memo={};model_memo={};upgraded=[];skipped=[]
    for target in sorted((root/'review/episodes').glob('*/*/*.json')):
        try:
            cached=read(target)
            if cached.get('evidence_fingerprint') or not cached.get('passed') or cached.get('auditor_sha256')!=auditor_hash:continue
            episode=Path(cached['episode']);raw=read(episode);receipt=read(episode.parent/'RUN_RECEIPT.json')
            assert sha(episode)==cached['episode_sha256']==receipt['episode_sha256']
            a=Auditor(episode,root/receipt['spec']['case']['case_path'])
            a.source_and_input();assert not a.errors,a.errors[:2]
            for s in raw['solves']:
                folder=episode.parent/'solves'/f"{s['gate_index']:05d}"
                assert read(folder/'receipt.json')==s
                assert canon(read(folder/'before.json'))==s['before_sha256']
                assert canon(read(folder/'after.json'))==s['after_sha256']
                m=folder/'model.json.gz'
                if not m.exists() and s.get('cached_model_file'):m=Path(s['cached_model_file'])
                if m.exists():
                    stat=m.stat();key=(str(m),stat.st_size,stat.st_mtime_ns)
                    if key not in model_memo:
                        with gzip.open(m,'rt') as f:model_memo[key]=canon(json.load(f))
                    assert model_memo[key]==s['model']['model_sha256']
                else:assert not s['model']['feasible']
                if s.get('cache_source') and Path(s['cache_source']).exists():
                    index=read(s['cache_source'])
                    assert index['semantic_key']==s['semantic_key'] and index['before_sha256']==s['before_sha256']
                    assert index['model']==s['model']
                    if index.get('model_file'):
                        assert sha(index['model_file'])==index['model_file_sha256']
            fingerprint,n=evidence_fingerprint(root,episode,receipt,raw,memo)
            cached.update(evidence_fingerprint=fingerprint,evidence_files=n,
                cache_upgrade='Prior same-verifier/episode PASS rebound by fresh source/receipt checks and every external graph/model canonical hash; no new simulation or repeated model algebra.')
            temporary=target.with_suffix('.upgrade.tmp');temporary.write_text(json.dumps(cached,indent=2,sort_keys=True)+'\n');temporary.replace(target)
            upgraded.append(str(episode.relative_to(root)))
        except Exception as exc:skipped.append({'audit':str(target.relative_to(root)),'reason':repr(exc)})
    result={'upgraded':len(upgraded),'skipped':skipped,'episodes':upgraded,'scientific_episodes':0,
        'policy_or_engine_imported':False,'method':'same prior verifier + same raw + canonically identical external inputs; fresh source receipt validation'}
    (root/'review/CACHE_UPGRADE_PROOF.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'upgraded':len(upgraded),'skipped':skipped}))


if __name__=='__main__':main()
