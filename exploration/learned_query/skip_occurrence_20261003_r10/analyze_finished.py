"""Audit and archive the fixed matrix after every native receipt has closed."""
import subprocess,time,json
import runner
P=runner.HERE
while not (P/'RECEIPT.json').exists():time.sleep(5)
for script in ['verify_matched_tail.py','summarize.py','label_diagnostics.py','skip_lifetimes.py','archive.py']:
 subprocess.run(['rtk','proxy','python3',str(P/script)],check=True,cwd=P)
runner.write(P/'ANALYSIS_FINISHED.json',dict(unix_time=time.time(),root_review_pending=True))
