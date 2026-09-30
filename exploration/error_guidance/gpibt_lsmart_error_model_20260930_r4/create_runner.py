"""Retain the already exercised bounded RPC lifecycle; adapt only frozen inputs/forecasts."""
from common import HERE
p=HERE.parent/'gpibt_lsmart_active_20260930_r3/run_trial.py';s=p.read_text()
def edit(a,b):
 global s
 assert s.count(a)==1,(a[:80],s.count(a));s=s.replace(a,b)
edit('import msgpack','import msgpack\nfrom common import context,forecast,events as read_events')
edit("gpibt_lsmart_active_20260930_r3')","gpibt_lsmart_error_model_20260930_r4')")
edit("    identities,pins=verify();pause=trial.startswith('pause');port=9351+int(pause)","""    identities,pins=verify()
    spec=next(r for r in json.loads((HERE/'runs.json').read_text())['runs'] if r['id']==trial)
    pause=spec['condition']=='unknown_pause';port=9461;seed=spec['seed']
    model=None;amplitude=0.0;checkpoint_sha=None
    if spec['split']=='test':
        freeze=json.loads((HERE/'model_freeze.json').read_text())
        for name,h in freeze['files'].items():assert sha(HERE/name)==h,name
        model=json.loads((HERE/'trained_model.json').read_text());amplitude=freeze['amplitude']
        checkpoint_sha=sha(HERE/'trained_model.json')""")
edit("env.update(INTEGRATION_TRACE=str(dst/'events.jsonl'),INTEGRATION_PAUSE=str(int(pause)),GPIBT_R0_SEED='42')","env.update(INTEGRATION_TRACE=str(dst/'events.jsonl'),INTEGRATION_PAUSE=str(int(pause)),GPIBT_R0_SEED=str(seed),R4_CONDITION=spec['condition'])")
edit("    config=config.replace(str(OLD/'lsmart_compat/client/build'),str(OUT/'client_build'))","    config=config.replace(str(OLD/'lsmart_compat/client/build'),str(OUT/'client_build')).replace('random_seed=\"42\"',f'random_seed=\"{seed}\"').replace('simDuration=\"200\"','simDuration=\"400\"')")
edit("'--total_sim_step_tick=200'","'--total_sim_step_tick=400'")
edit("'--seed=42'","f'--seed={seed}'")
edit("                req={'mapf_instance':view['mapf_instance'],'rows':5,'cols':5,'map':[int(ch=='@') for row in layout for ch in row]}","""                delivered=read_events(dst/'events.jsonl')
                assert delivered[-1]['kind']=='view' and delivered[-1]['view']==view
                fc=forecast(context(delivered),view,layout,spec['policy'],model,amplitude)
                req={'mapf_instance':view['mapf_instance'],'rows':5,'cols':5,'map':[int(ch=='@') for row in layout for ch in row],'priority_bias':fc['bias']}""")
edit("decision={'snapshot':snapshot,'view':view,'request':req,'result':result,'proposal':proposal}","decision={'snapshot':snapshot,'view':view,'request':req,'result':result,'proposal':proposal,'forecast':fc,'model_sha256':checkpoint_sha}")
edit("e['tick']==200 for e in events),'no real200tick horizon'","e['tick']==400 for e in events),'no real400tick horizon'")
start=s.index("        receipt={'trial':trial,");end=s.index("\n        if receipt['wall_seconds']",start)
s=s[:start]+"""        receipt={'trial':trial,'run_spec':spec,'commands':commands,'launch_prefix':['rtk','proxy'],'wall_seconds':time.monotonic()-start,'decisions':len(decisions),'error':error,'processes':status,'trigger_ticks':trigger,'actual_pause_ticks_inclusive':[trigger[0],trigger[0]+19] if pause and len(trigger)==1 else None,'protocol_sha256':pins['protocol_sha256'],'fixed_horizon_ticks':400,'ticks_per_second':10,'seed':seed,'blocking_guard_seconds':49,'whole_trial_limit_seconds_including_cleanup':54,'binary_identities':identities,'model_sha256':checkpoint_sha}
""".rstrip()+s[end:]
start=s.index("if __name__=='__main__':")
s=s[:start]+"""if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('trial',nargs='?');parser.add_argument('--offline-check',action='store_true')
    args=parser.parse_args();assert bool(args.trial)!=args.offline_check
    if args.offline_check:
        ids,pins=verify(False);assert not (HERE/'attempts').exists()
        frozen=['PROTOCOL.md','runs.json','prepare.py','build.py','run_trial.py','common.py','gpibt_bridge.cpp','controller_condition.patch','source_manifest.json','native_source_tree_manifest.json','preflight_identity.json','binary_manifest.json','map.json']
        ready={'status':'READY_FOR_SPLIT_COLLECTION','verified_binary_and_objects':len(ids),'whole_trial_seconds':54,'frozen_files':{p:sha(HERE/p) for p in frozen}}
        with (HERE/'ready_for_trial.json').open('x') as f:json.dump(ready,f,indent=2);f.write('\\n')
        print(json.dumps(ready,indent=2))
    else:raise SystemExit(main(args.trial))
"""
(HERE/'run_trial.py').write_text(s)
