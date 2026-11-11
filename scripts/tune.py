"""Grid over Seed & Spread variants. Run on dev to choose; run on test to report all.

usage: SS_DATASET=... SS_SPLIT=... SS_TAG=dev python scripts/tune.py
writes results/variants_<tag>.jsonl (per task ranks) and prints a table.
"""
from __future__ import annotations

import itertools
import json
import os
import pickle
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from seedspread.rank import rank_bm25, rank_seed, rank_ss, rrf  # noqa: E402
from seedspread.tasks import load_tasks  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
TAG = os.environ.get("SS_TAG", "test")

GRID = {f"ss[a={a},norm={int(n)},agg={g},fuse={f}]": dict(alpha=a, norm=n, agg=g, fuse=f)
        for a, n, g, f in itertools.product([0.2, 0.5, 0.8], [False, True], ["file+max", "max"], ["none", "rrf"])}


def rank_of(ranked, gold):
    pos = {f: i for i, f in enumerate(ranked)}
    r = [pos[f] for f in gold if f in pos]
    return min(r) + 1 if r else None


def main():
    out_path = ROOT / "results" / f"variants_{TAG}.jsonl"
    done = {json.loads(l)["id"] for l in open(out_path)} if out_path.exists() else set()
    out = open(out_path, "a")
    for t in load_tasks():
        if t.instance_id in done:
            continue
        p = ROOT / "cache" / "graphs" / f"{t.instance_id}.pkl"
        if not p.exists():
            continue
        g = pickle.load(open(p, "rb"))
        if not any(f in g.files for f in t.gold_files):
            continue                       # gold outside candidate set (e.g. only tests/docs changed)
        bm, sd = rank_bm25(t.issue, g), rank_seed(t.issue, g)
        ranks = {"bm25": rank_of(bm, t.gold_files), "seed": rank_of(sd, t.gold_files),
                 "rrf(bm25,seed)": rank_of(rrf(bm, sd), t.gold_files)}
        for name, kw in GRID.items():
            ranks[name] = rank_of(rank_ss(t.issue, g, **kw), t.gold_files)
        out.write(json.dumps(dict(id=t.instance_id, repo=t.repo, rank=ranks)) + "\n"); out.flush()
        print(t.instance_id, ranks["bm25"], ranks["seed"], flush=True)
    out.close()
    table(out_path)


def table(path):
    rows = [json.loads(l) for l in open(path)]
    n = len(rows)
    res = []
    for name in rows[0]["rank"]:
        rs = [r["rank"][name] for r in rows]
        a1 = sum(1 for x in rs if x and x <= 1) / n
        a5 = sum(1 for x in rs if x and x <= 5) / n
        mrr = sum(1 / x for x in rs if x) / n
        res.append((mrr, a1, a5, name))
    print(f"n={n}")
    for mrr, a1, a5, name in sorted(res, reverse=True):
        print(f"{name:45s} acc@1 {a1:.3f} acc@5 {a5:.3f} mrr {mrr:.3f}")


if __name__ == "__main__":
    if sys.argv[1:2] == ["--table"]:
        table(ROOT / "results" / f"variants_{TAG}.jsonl")
    else:
        main()
