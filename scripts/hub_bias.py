"""Why does spreading hurt? Compare the global-PageRank percentile of each ranker's top-1 file."""
import json, pickle, statistics as st, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from seedspread.rank import rank_pagerank, rank_ppr, rank_seed, rank_bm25  # noqa: E402
from seedspread.tasks import load_tasks  # noqa: E402
ROOT = Path(__file__).resolve().parents[1]
out = open(ROOT / "results" / "hub_bias.jsonl", "w")
for t in load_tasks():
    g = pickle.load(open(ROOT / "cache" / "graphs" / f"{t.instance_id}.pkl", "rb"))
    pr = rank_pagerank(t.issue, g)
    pct = {f: 1 - i / len(pr) for i, f in enumerate(pr)}       # 1.0 = most central file
    row = dict(id=t.instance_id, gold_pct=max(pct[f] for f in t.gold_files))
    for name, fn in [("ppr", rank_ppr), ("seed", rank_seed), ("bm25", rank_bm25)]:
        top = fn(t.issue, g)[0]
        row[name] = dict(top_pct=pct[top], correct=top in t.gold_files)
    out.write(json.dumps(row) + "\n"); out.flush()
rows = [json.loads(l) for l in open(ROOT / "results" / "hub_bias.jsonl")]
print("gold file centrality percentile: median", round(st.median(r["gold_pct"] for r in rows), 3))
for name in ("ppr", "seed", "bm25"):
    wrong = [r[name]["top_pct"] for r in rows if not r[name]["correct"]]
    print(f"{name}: median centrality of top-1 {st.median(r[name]['top_pct'] for r in rows):.3f}; "
          f"of WRONG top-1 {st.median(wrong):.3f} (n={len(wrong)}); wrong top-1 in top-5% most central: {sum(w >= 0.95 for w in wrong)/len(wrong):.2f}")
