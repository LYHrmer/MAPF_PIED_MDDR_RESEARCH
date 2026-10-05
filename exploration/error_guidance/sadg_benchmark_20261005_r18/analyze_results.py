#!/usr/bin/env python3
"""Read frozen episode summaries; never run planners, policies, or simulators."""
from pathlib import Path
from collections import Counter
import csv
import hashlib
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent
ARMS = ["history_only", "fixed_update", "history_rule", "learned_query", "dense_position"]
LABELS = ["History only", "Fixed updates", "History rule", "Learned query", "Dense (uncapped)"]
COLORS = ["#777777", "#4776a7", "#bd8d34", "#b24c63", "#58a092"]


def load(path):
    return json.loads(Path(path).read_text())


def dump(path, obj):
    Path(path).write_text(json.dumps(obj, indent=2, sort_keys=True, allow_nan=False)+"\n")


def bootstrap_family(values, seed=20261005):
    """Paired bootstrap across independent map/scenario families, not rows."""
    x = np.asarray(values, dtype=float)
    if not len(x):
        return None
    rng = np.random.default_rng(seed)
    samples = rng.choice(x, size=(10000, len(x)), replace=True).mean(axis=1)
    return dict(mean=float(x.mean()), lower=float(np.quantile(samples, .025)),
        upper=float(np.quantile(samples, .975)), families=len(x), resamples=10000,
        scope="six map/scenario test families; nested team sizes/disturbances kept together")


def main():
    summary = load(HERE/"SUMMARY.json")
    assert not summary["missing"], "incomplete requested evaluation matrix"
    rows = summary["rows"]
    assert len(rows) == 405
    failure_inventory = []
    for row in rows:
        path = HERE / row["episode_path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == row["episode_sha256"]
        raw = load(path)
        counts = Counter(f["kind"] for f in raw["failures"])
        row["failure_events"] = dict(counts)
        row["adoption_rejection_count"] = counts["ADOPTION_REJECTED_PARENT_GRAPH_RETAINED"]
        failure_inventory.append(dict(episode_path=row["episode_path"],
            episode_sha256=row["episode_sha256"], status=row["status"],
            failure_counts=dict(counts), error=raw.get("error")))
    test = [r for r in rows if r["split"] == "TEST"]
    assert len(test) == 3*3*2*3*5
    totals = []
    for split in ("CAL", "TEST"):
        for arm in ARMS:
            rr = [r for r in rows if r["split"] == split and r["arm"] == arm]
            available = [r for r in rr if r.get("episode_path")]
            totals.append(dict(split=split, arm=arm, registered_worlds=len(rr),
                executed_worlds=len(available), successful_worlds=sum(r["success"] for r in rr),
                completed_agents=sum(r.get("completed_agents") or 0 for r in available),
                safely_completed_agents=sum(r["completed_agents"] for r in available if r["success"]),
                registered_agents=sum(r["num_agents"] for r in rr),
                restricted_sum=sum(r.get("restricted_sum_completion") or 0. for r in available),
                queries=sum(r.get("query_count") or 0 for r in available),
                stale_queries=sum(r.get("stale_queries") or 0 for r in available),
                solver_calls=sum(r.get("solver_calls") or 0 for r in available),
                new_author_calls=sum(r.get("new_author_calls") or 0 for r in available),
                solver_failure_count=sum(r["solver_failure_count"] for r in available),
                adoption_rejection_count=sum(r["adoption_rejection_count"] for r in available),
                pending_queries=sum(r["pending_queries"] for r in available),
                failure_events=dict(sum((Counter(r["failure_events"]) for r in available), Counter())),
                reference_solver_seconds=sum(r.get("reference_solver_seconds") or 0. for r in available),
                statuses={s:sum(r["status"] == s for r in rr) for s in sorted({r["status"] for r in rr})}))
    indexed = {(r["case_id"], r["disturbance"], r["arm"]): r for r in test}
    pairs = []
    for reference in ("history_only", "fixed_update", "history_rule", "dense_position"):
        per_family = {}
        for row in test:
            if row["arm"] != "learned_query":
                continue
            ref = indexed[(row["case_id"], row["disturbance"], reference)]
            if not row["success"] or not ref["success"]:
                continue
            family = row["family"]
            delta = dict(time=row["restricted_sum_completion"]-ref["restricted_sum_completion"],
                relative_time=(row["restricted_sum_completion"]/ref["restricted_sum_completion"]-1.)*100.,
                queries=row["query_count"]-ref["query_count"], makespan=row["makespan"]-ref["makespan"])
            per_family.setdefault(family, []).append(delta)
        family_means = {f:{k:float(np.mean([v[k] for v in vals])) for k in vals[0]}
                        for f, vals in per_family.items()}
        pairs.append(dict(reference=reference, legal_paired_worlds=sum(len(v) for v in per_family.values()),
            total_registered_worlds=54, family_means=family_means,
            completion_time_outcomes={
                "lower": sum(v["time"] < -1e-8 for vals in per_family.values() for v in vals),
                "equal": sum(abs(v["time"]) <= 1e-8 for vals in per_family.values() for v in vals),
                "higher": sum(v["time"] > 1e-8 for vals in per_family.values() for v in vals)},
            uncertainty={k:bootstrap_family([v[k] for v in family_means.values()])
                for k in ("time", "relative_time", "queries", "makespan")},
            interpretation="negative is lower; dense reference has additional information budget"))
    strata = []
    for keys in (("map_name",), ("num_agents",), ("disturbance",), ("map_name", "num_agents", "disturbance")):
        groups = sorted({tuple(r[k] for k in keys) for r in test})
        for group in groups:
            for arm in ARMS:
                rr = [r for r in test if r["arm"] == arm and tuple(r[k] for k in keys) == group]
                strata.append(dict(group_by=list(keys), group=dict(zip(keys, group)), arm=arm,
                    worlds=len(rr), successful_worlds=sum(r["success"] for r in rr),
                    agents=sum(r["num_agents"] for r in rr),
                    restricted_sum=sum(r["restricted_sum_completion"] for r in rr),
                    queries=sum(r["query_count"] for r in rr),
                    stale_queries=sum(r["stale_queries"] for r in rr)))
    analysis = dict(summary_sha256=hashlib.sha256((HERE/"SUMMARY.json").read_bytes()).hexdigest(),
        totals=totals, paired_learned=pairs,
        test_strata=strata, failure_inventory=failure_inventory,
        independent_test_families=sorted({r["family"] for r in test}),
        statistical_note="CIs describe this small six-family benchmark; failures kept in totals, pair coverage explicit.")
    dump(HERE/"ANALYSIS.json", analysis)
    with (HERE/"TOTALS.csv").open("w", newline="") as f:
        flat=[{k:v for k,v in r.items() if k not in ("statuses", "failure_events")} for r in totals]
        writer=csv.DictWriter(f,fieldnames=list(flat[0]));writer.writeheader();writer.writerows(flat)

    figures=HERE/"figures";figures.mkdir(exist_ok=True)
    plt.rcParams.update({"font.size":10,"axes.spines.top":False,"axes.spines.right":False,
        "pdf.fonttype":42,"svg.fonttype":"none"})
    fig,axes=plt.subplots(1,2,figsize=(11,4.4))
    conditions=["stable","bounded_pause","speed_shift"]
    x=np.arange(3);width=.15
    figure_data=[]
    for j,(arm,label,color) in enumerate(zip(ARMS,LABELS,COLORS)):
        changes=[];lower=[];upper=[];costs=[]
        for condition in conditions:
            rr=[r for r in test if r["arm"]==arm and r["disturbance"]==condition]
            legal=[r for r in rr if r["success"] and indexed[(r["case_id"],condition,"history_only")]["success"]]
            grouped={}
            for r in legal:
                value=100.*(r["restricted_sum_completion"]/indexed[(r["case_id"],condition,"history_only")]["restricted_sum_completion"]-1.)
                grouped.setdefault(r["family"],[]).append(value)
            ci=bootstrap_family([float(np.mean(v)) for v in grouped.values()])
            changes.append(ci["mean"] if ci else np.nan)
            lower.append(max(0.,ci["mean"]-ci["lower"]) if ci else 0.)
            upper.append(max(0.,ci["upper"]-ci["mean"]) if ci else 0.)
            costs.append(np.mean([r["query_count"]/r["num_agents"] for r in rr if r.get("episode_path")]))
            figure_data.append(dict(arm=arm,condition=condition,relative_time_percent=ci,
                query_fraction=float(costs[-1]),legal_paired_worlds=len(legal),registered_worlds=len(rr)))
        axes[0].bar(x+(j-2)*width,changes,width,label=label,color=color,
            yerr=np.asarray([lower,upper]),capsize=2,error_kw={"elinewidth":.7})
        axes[1].bar(x+(j-2)*width,costs,width,label=label,color=color)
    axes[0].axhline(0,color="#333333",lw=.8,ls="--")
    axes[1].axhline(1,color="#333333",lw=.8,ls="--")
    axes[0].set_ylabel("Change in completion-time sum (%)")
    axes[1].set_ylabel("Position queries / team size")
    for ax in axes:
        ax.set_xticks(x,["Stable","Bounded pauses","Speed shift"])
        ax.grid(axis="y",alpha=.2);ax.set_axisbelow(True)
    axes[0].set_title("vs history only; paired family bootstrap 95%")
    axes[1].set_title("Same N-query cap; dense is uncapped")
    fig.legend(*axes[0].get_legend_handles_labels(),loc="lower center",ncol=5,frameon=False)
    fig.suptitle("SADG query policies: held-out MovingAI scenarios")
    fig.tight_layout(rect=(0,.11,1,.94))
    for ext in ["svg","pdf","png"]:
        fig.savefig(figures/f"test_tradeoff.{ext}",dpi=600,bbox_inches="tight")
    plt.close(fig)
    dump(figures/"FIGURE_DATA.json",figure_data)

    fig,axes=plt.subplots(1,3,figsize=(12,4),sharey=False)
    for ax,map_name in zip(axes,sorted({r["map_name"] for r in test})):
        for arm,label,color in zip(ARMS,LABELS,COLORS):
            yy=[]
            for n in (8,16,32):
                rr=[r for r in test if r["map_name"]==map_name and r["num_agents"]==n and r["arm"]==arm and r["success"]]
                yy.append(np.mean([r["restricted_sum_completion"]/n for r in rr]) if rr else np.nan)
            ax.plot([8,16,32],yy,"o-",label=label,color=color,ms=4)
        ax.set_title(map_name);ax.set_xlabel("Agents");ax.set_xticks([8,16,32]);ax.grid(alpha=.2)
    axes[0].set_ylabel("Mean completion time per agent")
    fig.legend(*axes[0].get_legend_handles_labels(),loc="lower center",ncol=5,frameon=False)
    fig.suptitle("Scale comparison: 2 unseen scenarios × 3 disturbances per point")
    fig.tight_layout(rect=(0,.13,1,.94))
    for ext in ["svg","pdf","png"]:
        fig.savefig(figures/f"test_scale.{ext}",dpi=600,bbox_inches="tight")
    plt.close(fig)
    dump(figures/"PROVENANCE.json",dict(source="SUMMARY.json",
        source_sha256=analysis["summary_sha256"],split="TEST",data_status="measured_author_SADG_in_continuous_simulation",
        legal_episode_filter_explicit=True,raw_failure_denominators="ANALYSIS.json totals",
        map_generalization_claim=False,no_experiments_run_by_plotter=True))
    print(json.dumps(dict(test_rows=len(test),totals=totals,paired=pairs),ensure_ascii=False))


if __name__=="__main__":main()
