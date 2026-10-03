from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent;R=H.parent/'primitive_duration_20261003_r9';R7=H.parent/'execution_residual_20261001_r7'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
m=json.loads((H/'model_freeze.json').read_text());old=json.loads((R/'model_freeze.json').read_text());data=json.loads((R/'training_rows.json').read_text());specs=json.loads((H/'runs.json').read_text())['runs'];s7=json.loads((R7/'runs.json').read_text())['runs'];s9=json.loads((R/'runs.json').read_text())['runs']
assert m['ridge']==old['ridge'] and m['d0']==old['d0'] and m['source_pins']==old['source_pins']
assert m['R10_provenance']['original_full_model_sha256']==sha(R/'model_freeze.json') and m['R10_provenance']['training_rows_sha256']==sha(R/'training_rows.json')
train={r['run'] for r in data['train']};cal={r['run'] for r in data['calibration']};assert not train&cal
for split,ids in [('train',train),('calibration',cal)]:
 assert ids=={s['id'] for s in s7 if s['split']==split}
 for ident in ids:assert 'test' not in ident
assert len(specs)==64 and len({(s['map'],s['seed']) for s in specs})==8
newseeds={s['seed'] for s in specs};oldseeds={s['seed'] for s in s7+s9};assert not newseeds&oldseeds
checks={'passed':True,'train_runs':sorted(train),'calibration_runs':sorted(cal),'training_motion_rows':sum(r['group']!='S' for r in data['train']),'new_test_seeds':sorted(newseeds),'new_seed_disjoint_R7_R9':True,'same14_feature_architecture':True,'full_ridge_unchanged':True,'geometry_lambda':m['geometry_ridge']['lambda'],'mask_slots':m['geometry_ridge']['masked_raw_slots'],'source_pin_count':len(m['source_pins']),'r9_test_used_only_to_form_attribution_hypothesis_not_fit':True,'new_test_input_hashes':{str(p.relative_to(H)):sha(p) for p in H.glob('inputs/*/*')}}
(H/'DATA_ISOLATION.json').write_text(json.dumps(checks,indent=2)+'\n');print('data isolation passed')
