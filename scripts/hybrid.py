"""Untuned hybrid: model's top-1 prediction first, then the ranker's order. -> results/hybrid_<model>.json"""
import json, pickle, sys
from collections import defaultdict
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from seedspread.rank import RANKERS  # noqa: E402
from seedspread.tasks import load_tasks  # noqa: E402
ROOT = Path(__file__).resolve().parents[1]
tasks = {t.instance_id: t for t in load_tasks()}
tag = sys.argv[1]
rows = [json.loads(l) for l in open(ROOT / "results" / f"llm_{tag}.jsonl")]
by = defaultdict(list)
for r in rows:
    if r["cond"] != "none/none/0":
        by[r["cond"]].append(r)
out = {}
for cond, rs in by.items():
    rn = cond.split("/")[0]
    s = defaultdict(int)
    for r in rs:
        t = tasks[r["id"]]
        g = pickle.load(open(ROOT / "cache" / "graphs" / f"{r['id']}.pkl", "rb"))
        ranked = RANKERS[rn](t.issue, g)
        hybrid = (r["preds"][:1] + [f for f in ranked if f not in r["preds"][:1]])[:5]
        gold = set(t.gold_files)
        s["model1"] += r["rank"] == 1; s["model5"] += bool(r["rank"])
        s["ranker1"] += ranked[0] in gold; s["ranker5"] += bool(gold & set(ranked[:5]))
        s["hybrid5"] += bool(gold & set(hybrid))
    n = len(rs)
    out[cond] = {k: v / n for k, v in s.items()} | {"n": n}
    print(cond, out[cond], flush=True)
(ROOT / "results" / f"hybrid_{tag}.json").write_text(json.dumps(out, indent=1))
