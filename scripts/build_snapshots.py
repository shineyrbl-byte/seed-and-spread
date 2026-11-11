"""Build and cache one code graph per SWE-bench Lite task (pickled), plus graph stats."""
from __future__ import annotations

import json
import pickle
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from seedspread.graph import build_graph  # noqa: E402
from seedspread.repo import python_files, repo_dir  # noqa: E402
from seedspread.tasks import load_tasks  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "cache"


def main():
    sys.setrecursionlimit(20000)
    tasks = load_tasks()
    out = CACHE / "graphs"
    out.mkdir(parents=True, exist_ok=True)
    for i, t in enumerate(tasks):
        dst = out / f"{t.instance_id}.pkl"
        if dst.exists():
            continue
        t0 = time.time()
        files = python_files(repo_dir(CACHE, t.repo), t.base_commit)
        g = build_graph(files)
        g.by_name, g.edges, g.file_symbols = dict(g.by_name), {k: dict(v) for k, v in g.edges.items()}, dict(g.file_symbols)
        with open(dst, "wb") as fh:
            pickle.dump(g, fh, protocol=pickle.HIGHEST_PROTOCOL)
        s = dict(id=t.instance_id, files=len(files), symbols=len(g.symbols),
                 edges=sum(len(v) for v in g.edges.values()), parse_failures=g.parse_failures,
                 gold_in_candidates=all(f in files for f in t.gold_files), secs=round(time.time() - t0, 2))
        with open(ROOT / "results" / "graph_stats.jsonl", "a") as fh:
            fh.write(json.dumps(s) + "\n")
        print(i, json.dumps(s), flush=True)


if __name__ == "__main__":
    main()
