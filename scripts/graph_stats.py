"""Recompute per-snapshot graph statistics from cached pickles -> results/graph_stats.jsonl."""
import json, pickle, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from seedspread.tasks import load_tasks  # noqa: E402
ROOT = Path(__file__).resolve().parents[1]
with open(ROOT / "results" / "graph_stats.jsonl", "w") as fh:
    for t in load_tasks():
        g = pickle.load(open(ROOT / "cache" / "graphs" / f"{t.instance_id}.pkl", "rb"))
        fh.write(json.dumps(dict(id=t.instance_id, repo=t.repo, files=len(g.files), symbols=len(g.symbols),
                 edges=sum(len(v) for v in g.edges.values()), parse_failures=g.parse_failures,
                 n_gold=len(t.gold_files), gold_in_candidates=all(f in g.files for f in t.gold_files))) + "\n")
