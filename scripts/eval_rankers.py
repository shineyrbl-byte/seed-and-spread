"""Experiment 1 (no LLM): file-localization quality of each ranker on all of SWE-bench Lite.

Writes results/rankers.jsonl (per task: rank of first gold file under each ranker) and
results/rankers_summary.json (Acc@k, MRR, and "coverage under budget" for each ranker).
"""
from __future__ import annotations

import json
import pickle
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from seedspread.rank import RANKERS  # noqa: E402
from seedspread.render import render  # noqa: E402
from seedspread.tasks import load_tasks  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
BUDGETS = [500, 1000, 2000, 4000, 8000]
import os
SUFFIX = "_" + os.environ["SS_TAG"] if os.environ.get("SS_TAG") else ""


def first_gold_rank(ranked, gold):
    pos = {f: i for i, f in enumerate(ranked)}
    ranks = [pos[f] for f in gold if f in pos]
    return min(ranks) + 1 if ranks else None


def main():
    only = set(sys.argv[1:]) or set(RANKERS)
    tasks = load_tasks()
    out = open(ROOT / "results" / f"rankers{SUFFIX}.jsonl", "w")
    for i, t in enumerate(tasks):
        g = pickle.load(open(ROOT / "cache" / "graphs" / f"{t.instance_id}.pkl", "rb"))
        row = dict(id=t.instance_id, repo=t.repo, n_files=len(g.files), gold=t.gold_files, rank={}, in_map={})
        for name, fn in RANKERS.items():
            if name not in only:
                continue
            ranked = fn(t.issue, g)
            row["rank"][name] = first_gold_rank(ranked, t.gold_files)
            for layout in ("paths", "sigs"):
                for b in BUDGETS:
                    shown = {ln for ln in render(g, ranked, b, layout).splitlines() if not ln.startswith(" ")}
                    row["in_map"][f"{name}/{layout}/{b}"] = any(f in shown for f in t.gold_files)
        out.write(json.dumps(row) + "\n"); out.flush()
        print(i, t.instance_id, row["rank"], flush=True)
    out.close()
    summarize()


def summarize():
    rows = [json.loads(l) for l in open(ROOT / "results" / f"rankers{SUFFIX}.jsonl")]
    n = len(rows)
    summ = {"n": n, "rankers": {}}
    for name in rows[0]["rank"]:
        rs = [r["rank"][name] for r in rows]
        acc = {f"acc@{k}": sum(1 for x in rs if x and x <= k) / n for k in (1, 3, 5, 10, 20)}
        mrr = sum(1 / x for x in rs if x) / n
        cov = {key.split("/", 1)[1]: sum(r["in_map"][key] for r in rows) / n
               for key in rows[0]["in_map"] if key.startswith(name + "/")}
        summ["rankers"][name] = {**acc, "mrr": mrr, "gold_in_map": cov}
    json.dump(summ, open(ROOT / "results" / f"rankers{SUFFIX}_summary.json", "w"), indent=1)
    for name, s in summ["rankers"].items():
        print(f"{name:10s} acc@1 {s['acc@1']:.3f} acc@5 {s['acc@5']:.3f} acc@10 {s['acc@10']:.3f} mrr {s['mrr']:.3f}")


if __name__ == "__main__":
    if sys.argv[1:2] == ["--summarize"]:
        summarize()
    else:
        main()
