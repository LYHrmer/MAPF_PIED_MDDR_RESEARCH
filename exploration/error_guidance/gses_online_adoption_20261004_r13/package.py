"""Descriptive publication packaging; no fitting or new experiment selection."""
from pathlib import Path
from fractions import Fraction as F
import argparse,collections,hashlib,json
HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(n):return json.loads((HERE/n).read_text())
def dec(x):return f'{float(F(x)):.2f}'.rstrip('0').rstrip('.')
def main():
 p=argparse.ArgumentParser();p.add_argument('--seal',action='store_true');args=p.parse_args()
 rows=load('RESULTS.json');reg=load('REGISTRATION.json');assert len(rows)==36
 for n,h in reg['source_pins'].items():assert sha(HERE/n)==h
 groups={s['id']:[r for r in rows if r['spec']['id']==s['id']] for s in reg['runs']}
 table=[];effects=[]
 for stem,rr in groups.items():
  by={r['method']:r for r in rr};b=by['original'];s=b['spec']
  table.append('|'+ '|'.join([s['case'],s['at'],s['profile']]+[dec(by[m]['sum_completion_time'])+' / '+dec(by[m]['makespan']) for m in ['original','GSES','Improved_GSES']])+'|')
  for m in ['GSES','Improved_GSES']:
   r=by[m];effects.append({'id':r['id'],'sum_gain_vs_original':str(F(b['sum_completion_time'])-F(r['sum_completion_time'])),
                         'makespan_gain_vs_original':str(F(b['makespan'])-F(r['makespan'])),
                         'reversed_families':len(r['guard']['removed_type2']),'active_moves_at_adoption':r['guard']['active_count']})
 summary={'scope':'two reused author instances, 12 contexts, no heldout inference','executions':36,'solver_calls':24,
          'source_pins_match':True,'statuses':dict(collections.Counter(r['status'] for r in rows if r['method']!='original')),
          'changed_graphs':sum(r['changed'] for r in rows),'changed_complete_traces':sum(r['behavior_changed'] for r in rows),
          'sum_improved':sum(F(r['sum_gain_vs_original'])>0 for r in effects),'sum_worsened':sum(F(r['sum_gain_vs_original'])<0 for r in effects),
          'makespan_improved':sum(F(r['makespan_gain_vs_original'])>0 for r in effects),'makespan_worsened':sum(F(r['makespan_gain_vs_original'])<0 for r in effects),
          'makespan_tied':sum(F(r['makespan_gain_vs_original'])==0 for r in effects),'effects':effects,
          'gzip_members':len(list((HERE/'raw').glob('*.gz'))),'gzip_bytes':sum(p.stat().st_size for p in (HERE/'raw').glob('*.gz'))}
 (HERE/'SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n')
 audit_note='Independent root audit is reported separately; see ROOT_AUDIT_BINDING.json once present.'
 if (HERE/'ROOT_AUDIT_BINDING.json').exists():audit_note='The independent root dynamic-dependency/resource/continuous audit passed; ROOT_AUDIT_BINDING.json pins its exact source and output.'
 text='''# R13: actual author suffix-graph adoption during primitive execution

All 24 real author calls returned within the registered budget and supplied a different graph that passed the adoption guard. All 24 changed full execution traces; the 12 original continuations and 24 adopted continuations passed local event/resource checks. This closes the specific R11 gap between same-graph checkpoint restore and actual different-graph adoption. It does not establish general planner superiority, original-feedback-controller equivalence or lifelong MAPF.

Two existing author instances, random60 and warehouse110, each use public checkpoints1/2 and5/2 and three unchanged primitive profiles. The 12 contexts are mechanism conditions, not12 independent heldout tasks. Their paths and original type2 relations come from the frozen R10 author exports. There was no case substitution, model training, outcome tuning, additional solver search or changed physical profile. Source registration precedes all24 calls; all43 compiled author source/header files remain unchanged.

## Actual data and execution boundary

At the checkpoint, the simulator serializes a full private continuation state and a separate allowlisted public author input. Only the latter is passed to the author executable. It contains actual ARRIVE states, current action identities/occupancy, known paths and unsatisfied dependencies. Active MOVE remains at its from-state. Public initial hold minus elapsed time gives a rounded nominal residual hold; all future search edges have unit weight. Private queued finish times, future segments/profile and pauses are excluded. Search weights never override physical primitive durations.

The unmodified author make_switchable fixes outgoing edges at current+1. Already satisfied incoming constraints of active movements are removed from the suffix optimizer and restored with their original directions when lifting back to the full graph. The guard preserves every canonical dependency family, full paths/type1 ordering, completed transitions, active incoming constraints and satisfied orientations, and checks the complete DAG. It then replaces the real executor graph/dependency map while every other state field, event queue, reservation and committed segment remains unchanged. Downstream MOVE_START records use the new dependency map.

These checkpoints declare present controller/reservation state public. That assumption is distinct from implementing the main line's paid-information contract. The solver transaction freezes virtual time; actual host grouping/search/subprocess durations are preserved, not inserted as robot motion delay. The experiments therefore do not establish a real-time asynchronous planning benefit.

## Full registered results

Each cell is sum completion time / makespan. Values are exact quarters or halves in these profiles; raw fractions remain in RESULTS.json. The primary descriptive outcome is completion sum; makespan is reported without omission.

|Author case|Checkpoint|Profile|Original continuation|GSES adoption|Improved GSES adoption|
|---|---|---|---:|---:|---:|
'''+ '\n'.join(table)+'''

Across the24 adopted continuations, completion sum improves18 times and worsens6 times. All12 random60 continuations lower the sum but increase makespan; all12 warehouse110 continuations keep makespan, with six sum gains and six losses. Therefore changed and legal adoption does not imply a better primitive objective. Examples of retained regressions: warehouse at1/2 nominal costs +4.5 for GSES and +14.75 for Improved; midpoint costs +6.75/+17. At5/2 midpoint the sum increases +17/+7.75. These are signed consequences of the same real author methods under the registered execution adaptation, not solver failures to be discarded.

The existence of both better and worse legal outcomes supplies a concrete future value-selection question. No model chose these results in R13, no full candidate-set optimality is claimed, and primitive truth did not enter the author inputs. A subsequent model must compare complete legal continuations using only the declared decision-time information and fresh TRAIN/TEST data.

## Safety, fallback and reproduction

All36 local audits independently reconstruct event/resource state and dependency versions. They retain destination geometric entry at2/5 and source geometric exit at3/5, midpoint state nonadvancement, TURN/STATION residence and goal holding. '''+audit_note+'''

MECHANICS.json retains seven rejected corruptions, exact same-graph checkpoint continuation, exact rejected-candidate fallback and exact fallback under injected Timeout/HostTimeout/AuthorError statuses. The altered-current control can fail earlier structural validation, and the commitment control uses a genuine author reversal against an explicitly protected target transition; these are not independent physical samples. The explicit-cycle control directly exercises the DAG checker. There were zero natural timeouts, rejections or author errors in the24 scientific calls. Injected timeout handling must not be reported as a naturally observed timed-out solver run.

Changing only private queued future times, future geometric segments and the private profile leaves the serialized author input identical. This tests the implemented message boundary; it is not a proof of arbitrary external noninterference.

The48 raw gzip members contain36 complete execution traces and12 serialized checkpoints, totaling44,495,082 bytes. AUTHOR_SOURCES.tar.gz contains43 pinned original compilation files and the MIT notice is preserved. `reproduce.py --build` reconstructs the author adapter offline from the archive and checks byte-identical ELF output. `reproduce.py --replay ID` resumes a stored checkpoint and compares the entire emitted trace, not only summary metrics; it does not launch a new author optimization or count as another scientific instance. REPRODUCTION.json records checks actually performed. Absolute historical paths in registration record provenance; replay inputs are included locally.

This is a finite fixed-path dependency-ordering interface with piecewise affine geometry, instantaneous velocity changes and synthetic per-vertex station stress. It does not independently certify map-obstacle clearance, acceleration/tracking dynamics or hardware. It does not issue new tasks, learn a policy, alter paths, implement LMAPF or use the original ARGoS continuous controller.
'''
 (HERE/'REPORT.md').write_text(text)
 if args.seal:
  files={str(p.relative_to(HERE)):sha(p) for p in sorted(HERE.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.name!='PUBLICATION_MEMBERS.json'}
  (HERE/'PUBLICATION_MEMBERS.json').write_text(json.dumps({'files':files,'count':len(files),'scope':'explicit package members only; no external expanded main workspace files'},indent=2)+'\n')
 print(json.dumps({k:v for k,v in summary.items() if k!='effects'}))
if __name__=='__main__':main()
