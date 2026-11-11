"""Produce every number in the paper from results/*.jsonl -> results/analysis.md (+ figures)."""
from __future__ import annotations

import json
import random
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
R = ROOT / "results"
B = 2000          # bootstrap resamples
rng = random.Random(0)


def load(p):
    return [json.loads(l) for l in open(p)] if p.exists() else []


def acc(ranks, k):
    return sum(1 for x in ranks if x and x <= k) / len(ranks)


def mrr(ranks):
    return sum(1 / x for x in ranks if x) / len(ranks)


def ci(vals, stat):
    n = len(vals)
    bs = sorted(stat([vals[rng.randrange(n)] for _ in range(n)]) for _ in range(B))
    return bs[int(0.025 * B)], bs[int(0.975 * B)]


def paired(a, b, stat):
    """Paired bootstrap: P(stat(a) <= stat(b)) under resampling tasks; returns diff and p (one-sided)."""
    n = len(a)
    d0 = stat(a) - stat(b)
    worse = 0
    for _ in range(B):
        idx = [rng.randrange(n) for _ in range(n)]
        if stat([a[i] for i in idx]) - stat([b[i] for i in idx]) <= 0:
            worse += 1
    return d0, worse / B


def main():
    out = []
    w = out.append

    # ---------- graph stats
    gs = [r for r in load(R / "graph_stats.jsonl") if "repo" in r]
    if gs:
        import statistics as st
        w("## Snapshots (SWE-bench Lite test)\n")
        w(f"tasks {len(gs)}; candidate files median {st.median(r['files'] for r in gs)} (max {max(r['files'] for r in gs)}); "
          f"symbols median {st.median(r['symbols'] for r in gs)} (max {max(r['symbols'] for r in gs)}); "
          f"edges median {st.median(r['edges'] for r in gs)} (max {max(r['edges'] for r in gs)}); "
          f"files skipped (syntax/recursion) {sum(r['parse_failures'] for r in gs)}; gold file in candidate set {sum(r['gold_in_candidates'] for r in gs)}/{len(gs)}\n")

    # ---------- rankers on test
    rows = load(R / "rankers.jsonl")
    sf = {r["id"]: r for r in load(R / "rankers_seedfuse.jsonl")}
    gt = {r["id"]: r for r in load(R / "rankers_gemmatok.jsonl")}
    budget_unit = "approx. tokens = chars/4"
    for r in rows:
        if r["id"] in sf:
            r["rank"].update(sf[r["id"]]["rank"]); r["in_map"].update(sf[r["id"]]["in_map"])
    if len(gt) == len(rows) and rows:            # prefer budgets counted with the Gemma tokenizer
        budget_unit = "Gemma 4 tokens"
        for r in rows:
            r["in_map"] = gt[r["id"]]["in_map"]
    if rows:
        w("## Table 1: rankers, SWE-bench Lite test (n=%d), no LLM\n" % len(rows))
        w("| ranker | Acc@1 | Acc@5 | Acc@10 | MRR [95% CI] |\n|---|---|---|---|---|")
        names = [n for n in ["tree", "pagerank", "ppr", "seed", "ppr+bm25", "bm25", "seed+bm25"] if n in rows[0]["rank"]]
        ranks = {n: [r["rank"][n] for r in rows] for n in names}
        for n in names:
            lo, hi = ci(ranks[n], mrr)
            w(f"| {n} | {acc(ranks[n],1):.3f} | {acc(ranks[n],5):.3f} | {acc(ranks[n],10):.3f} | {mrr(ranks[n]):.3f} [{lo:.3f}, {hi:.3f}] |")
        if "seed+bm25" in ranks:
            for stat_name, stat in [("Acc@1", lambda x: acc(x, 1)), ("MRR", mrr)]:
                d, p = paired(ranks["seed+bm25"], ranks["bm25"], stat)
                w(f"\nseed+bm25 vs bm25, {stat_name}: diff {d:+.3f}, paired bootstrap p={p:.3f}")
        w("\n### Per-repo MRR\n")
        repos = sorted({r["repo"] for r in rows}, key=lambda x: -sum(r["repo"] == x for r in rows))
        w("| repo | n | " + " | ".join(names) + " |\n|---|---|" + "---|" * len(names))
        for rp in repos:
            sub = [r for r in rows if r["repo"] == rp]
            w(f"| {rp} | {len(sub)} | " + " | ".join(f"{mrr([r['rank'][n] for r in sub]):.2f}" for n in names) + " |")
        w(f"\n## Table 2: gold file visible in the map, by budget ({budget_unit})\n")
        keys = sorted({k.split("/", 1)[1] for k in rows[0]["in_map"]}, key=lambda s: (s.split("/")[0], int(s.split("/")[1])))
        w("| ranker | " + " | ".join(keys) + " |\n|---|" + "---|" * len(keys))
        for n in names:
            w(f"| {n} | " + " | ".join(f"{sum(r['in_map'][f'{n}/{k}'] for r in rows)/len(rows):.2f}" for k in keys) + " |")

    # ---------- variant grids
    for tag in ("dev", "test"):
        vr = load(R / f"variants_{tag}.jsonl")
        if not vr:
            continue
        w(f"\n## Variant grid on {tag} (n={len(vr)})\n")
        w("| variant | Acc@1 | Acc@5 | MRR |\n|---|---|---|---|")
        res = sorted(((mrr([r['rank'][k] for r in vr]), k) for k in vr[0]["rank"]), reverse=True)
        for m, k in res:
            rs = [r["rank"][k] for r in vr]
            w(f"| {k} | {acc(rs,1):.3f} | {acc(rs,5):.3f} | {m:.3f} |")
        # effect of alpha with no fusion
        w("\nMean MRR by alpha (fuse=none): " + ", ".join(
            f"a={a}: {sum(mrr([r['rank'][k] for r in vr]) for k in vr[0]['rank'] if f'a={a},' in k and 'fuse=none' in k)/4:.3f}"
            for a in (0.2, 0.5, 0.8)))

    # ---------- LLM
    rank_by = {r["id"]: r["rank"] for r in rows}
    for p in sorted(R.glob("llm_*.jsonl")):
        lr = load(p)
        by = defaultdict(list)
        for r in lr:
            by[r["cond"]].append(r)
        ids_all = set.intersection(*[{r["id"] for r in v} for v in by.values()]) if by else set()
        w(f"\n## Table 3: {p.stem[4:]} file localization (tasks with all conditions: {len(ids_all)})\n")
        w("| condition | n | Acc@1 [95% CI] | Acc@5 | gold in map | Acc@1 given gold in map | ranker top-1 | prompt tokens | sec/task |\n|---|---|---|---|---|---|---|---|---|")
        order = sorted(by, key=lambda c: (c.split("/")[0] != "none", c.split("/")[0], c.split("/")[1], int(c.split("/")[2])))
        for c in order:
            rs = [r for r in by[c] if r["id"] in ids_all] or by[c]
            n = len(rs)
            r1 = [1 if r["rank"] == 1 else 0 for r in rs]
            lo, hi = ci(r1, lambda x: sum(x) / len(x))
            inmap = [r for r in rs if r["gold_in_map"]]
            ranker = c.split("/")[0]
            top1 = (sum(1 for r in rs if rank_by.get(r["id"], {}).get(ranker) == 1) / n) if ranker in (rows[0]["rank"] if rows else {}) else None
            w(f"| {c} | {n} | {sum(r1)/n:.2f} [{lo:.2f}, {hi:.2f}] | {sum(1 for r in rs if r['rank'])/n:.2f} | "
              + (f"{len(inmap)/n:.2f}" if c != "none/none/0" else "-") + " | "
              + (f"{sum(r['rank'] == 1 for r in inmap)/len(inmap):.2f}" if inmap else "-") + " | "
              + (f"{top1:.2f}" if top1 is not None else "-") + " | "
              + f"{sum(r['prompt_tokens'] for r in rs)/n:.0f} | {sum(r['secs'] for r in rs)/n:.1f} |")
        # paired comparisons against the selected ranker
        base = "seed+bm25/sigs/2000"
        if base in by:
            a = {r["id"]: r["rank"] == 1 for r in by[base]}
            for c in order:
                if c == base:
                    continue
                b = {r["id"]: r["rank"] == 1 for r in by[c]}
                common = sorted(set(a) & set(b))
                if len(common) < 20:
                    continue
                d, pv = paired([int(a[i]) for i in common], [int(b[i]) for i in common], lambda x: sum(x) / len(x))
                w(f"- {base} vs {c}: Acc@1 diff {d:+.2f} (n={len(common)}, paired bootstrap p={pv:.3f})")
        unparsable = sum(1 for r in lr if not r["preds"])
        w(f"\nresponses with no valid path: {unparsable}/{len(lr)}")

    (R / "analysis.md").write_text("\n".join(out) + "\n")
    print("\n".join(out))


if __name__ == "__main__":
    main()
