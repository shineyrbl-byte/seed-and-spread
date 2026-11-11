"""Paper figures -> paper/fig_*.png (palette validated with the dataviz validator; direct labels + marker shapes
as secondary encoding because three hues sit below 3:1 contrast on white)."""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
R, P = ROOT / "results", ROOT / "paper"
SURF, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
SERIES = {  # fixed order: entity -> slot, never by rank
    "seed+bm25": ("#2a78d6", "o", "seed+bm25 (ours, dev-selected)"),
    "bm25": ("#eb6834", "s", "BM25"),
    "ppr": ("#1baf7a", "^", "PPR spread"),
    "pagerank": ("#eda100", "D", "global PageRank"),
    "tree": ("#e87ba4", "v", "file tree"),
}
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.edgecolor": GRID, "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2, "axes.facecolor": SURF, "figure.facecolor": SURF,
                     "axes.spines.top": False, "axes.spines.right": False})


def load(p):
    return [json.loads(l) for l in open(p)] if p.exists() else []


def coverage():
    rows = load(R / "rankers_gemmatok.jsonl")
    if len(rows) < 300:
        print("coverage: gemmatok incomplete", len(rows)); return
    budgets = [500, 1000, 2000, 4000, 8000]
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.8), sharey=True)
    for ax, layout, title in [(axes[0], "paths", "paths only"), (axes[1], "sigs", "paths + signatures")]:
        for name, (c, m, label) in SERIES.items():
            ys = [sum(r["in_map"][f"{name}/{layout}/{b}"] for r in rows) / len(rows) for b in budgets]
            ax.plot(budgets, ys, color=c, marker=m, lw=2, ms=6, mec=SURF, mew=1.5, label=label)
        ax.set_xscale("log", base=2); ax.set_xticks(budgets, [str(b) for b in budgets])
        ax.set_title(title, color=INK, fontsize=10, loc="left")
        ax.set_xlabel("map budget (Gemma 4 tokens)"); ax.grid(axis="y", color=GRID, lw=0.8); ax.set_ylim(0, 1.02)
    axes[0].set_ylabel("gold file visible in map")
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, frameon=False, fontsize=8.5, loc="lower center", ncol=5, labelcolor=INK2, bbox_to_anchor=(0.5, 0.0))
    fig.suptitle("Is the file that needs fixing even in the map? (SWE-bench Lite test, n=300)", x=0.01, ha="left", color=INK, fontsize=11)
    fig.tight_layout(rect=(0, 0.08, 1, 1)); fig.savefig(P / "fig_coverage.png", dpi=200); plt.close(fig)


def llm_bars(tag="gemma-4-e2b-it-4bit", fname="fig_llm_e2b.png", title="Gemma 4 E2B"):
    lr = load(R / f"llm_{tag}.jsonl")
    rk = {r["id"]: r["rank"] for r in load(R / "rankers.jsonl")}
    for r in load(R / "rankers_seedfuse.jsonl"):
        rk.setdefault(r["id"], {}).update(r["rank"])
    conds = [("none/none/0", "no map (issue only)"), ("pagerank/sigs/2000", "global PageRank map"),
             ("tree/paths/2000", "file-tree map"), ("ppr/sigs/2000", "PPR-spread map"),
             ("bm25/sigs/2000", "BM25 map"), ("ppr+bm25/sigs/2000", "PPR+BM25 map"), ("seed+bm25/sigs/2000", "seed+bm25 map (ours)")]
    by = defaultdict(list)
    for r in lr:
        by[r["cond"]].append(r)
    conds = [(c, l) for c, l in conds if len(by[c]) >= 50]
    if not conds:
        return
    fig, ax = plt.subplots(figsize=(7.5, 0.45 * len(conds) + 1.2))
    for i, (c, label) in enumerate(conds):
        rs = by[c]; n = len(rs)
        a1 = sum(r["rank"] == 1 for r in rs) / n
        ax.barh(i, a1, height=0.6, color="#2a78d6")
        ax.text(a1 + 0.01, i, f"{a1:.2f}", va="center", fontsize=9, color=INK)
        rname = c.split("/")[0]
        if rname != "none":
            t1 = sum(1 for r in rs if rk.get(r["id"], {}).get(rname) == 1) / n
            ax.plot([t1], [i], marker="|", ms=18, mew=2.5, color="#eb6834")
    ax.set_yticks(range(len(conds)), [l for _, l in conds], color=INK)
    ax.set_xlim(0, 1); ax.set_xlabel("Acc@1 (top prediction is the gold file)")
    ax.grid(axis="x", color=GRID, lw=0.8); ax.set_axisbelow(True)
    ax.plot([], [], marker="|", ls="", ms=12, mew=2.5, color="#eb6834", label="ranker's own top-1, no LLM")
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(color="#2a78d6", label=f"{title} answer"), ax.lines[-1]],
              frameon=False, fontsize=8, loc="lower right", labelcolor=INK2)
    ax.set_title(f"{title} on-device file localization, 2,000-token maps (n={len(by[conds[0][0]])})", loc="left", color=INK, fontsize=11)
    fig.tight_layout(); fig.savefig(P / fname, dpi=200); plt.close(fig)


def budget_sweep():
    lr = load(R / "llm_gemma-4-e2b-it-4bit.jsonl")
    by = defaultdict(list)
    for r in lr:
        if r["cond"].startswith("seed+bm25/sigs/"):
            by[int(r["cond"].split("/")[2])].append(r)
    bs = sorted(b for b in by if len(by[b]) >= 50)
    if len(bs) < 3:
        return
    fig, ax = plt.subplots(figsize=(6, 3.7))
    a1 = [sum(r["rank"] == 1 for r in by[b]) / len(by[b]) for b in bs]
    a5 = [sum(1 for r in by[b] if r["rank"]) / len(by[b]) for b in bs]
    cov = [sum(1 for r in by[b] if r["gold_in_map"]) / len(by[b]) for b in bs]
    for ys, c, m, lab in [(cov, "#1baf7a", "^", "gold visible in map"), (a5, "#eb6834", "s", "Acc@5"), (a1, "#2a78d6", "o", "Acc@1")]:
        ax.plot(bs, ys, color=c, marker=m, lw=2, ms=6, mec=SURF, mew=1.5)
        ax.annotate(lab, (bs[-1], ys[-1]), textcoords="offset points", xytext=(6, -3), fontsize=8, color=INK2)
    secs = [sum(r["secs"] for r in by[b]) / len(by[b]) for b in bs]
    ax.set_xscale("log", base=2); ax.set_xticks(bs, [f"{b}\n{s_:.1f} s/task" for b, s_ in zip(bs, secs)]); ax.set_xlim(bs[0] * 0.8, bs[-1] * 2.2)
    ax.set_ylim(0, 1.02); ax.grid(axis="y", color=GRID, lw=0.8)
    ax.set_xlabel("map budget (Gemma 4 tokens) and mean on-device latency"); ax.set_ylabel("fraction of tasks")
    ax.set_title(f"Gemma 4 E2B, seed+bm25 signature maps (n={len(by[bs[0]])})", loc="left", color=INK, fontsize=11)
    fig.tight_layout(); fig.savefig(P / "fig_budget.png", dpi=200); plt.close(fig)


if __name__ == "__main__":
    coverage(); llm_bars(); llm_bars("gemma-4-e4b-it-4bit", "fig_llm_e4b.png", "Gemma 4 E4B"); budget_sweep()
    print(sorted(p.name for p in P.glob("fig_*.png")))
