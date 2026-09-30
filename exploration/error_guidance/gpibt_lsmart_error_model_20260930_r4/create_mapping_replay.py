from common import HERE,sha,write
p=HERE.parent/'gpibt_lsmart_active_20260930_r3/parent_mapping_audit.py'
s=p.read_text().split('\ndef main():')[0]
assert s.count("e['tick']==200")==1
s=s.replace("e['tick']==200","e['tick']==400")
(HERE/'mapping_replay.py').write_text(s)
write(HERE/'mapping_replay_provenance.json',{'parent_source_sha256':sha(p),'successor_sha256':sha(HERE/'mapping_replay.py'),'only_check_function_change':'horizon200->400','entrypoint_omitted':True})
