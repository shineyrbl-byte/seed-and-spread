"""Experiment 2: Gemma 4 on-device file localization from a budgeted repo map.

usage: eval_llm.py MODEL N_TASKS CONDITION[,CONDITION...]
  CONDITION = ranker/layout/budget, e.g. ppr/sigs/2000, or "none/none/0" (issue only)

Tasks are a fixed, seeded, repo-stratified sample of SWE-bench Lite (see sample_ids).
The model sees the issue + map and must list up to 5 files to edit. Results append to
results/llm_<model>.jsonl and finished (task, condition) pairs are skipped, so runs resume.
"""
from __future__ import annotations

import json
import pickle
import random
import re
import sys
import time
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from seedspread.rank import RANKERS  # noqa: E402
from seedspread.render import render  # noqa: E402
from seedspread.tasks import load_tasks  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
MAX_ISSUE_CHARS = 6000

PROMPT = """You are helping fix a bug in the repository `{repo}`.

<issue>
{issue}
</issue>
{map_block}
Which source files must be edited to resolve this issue? List the {k} most likely files, most likely first, one full path per line. Output only the paths, nothing else."""

MAP_BLOCK = """
Here is a partial map of the repository (file paths{sigs_note}):
<repo_map>
{map}
</repo_map>
"""


def sample_ids(tasks, n, seed=0):
    by_repo = defaultdict(list)
    for t in tasks:
        by_repo[t.repo].append(t)
    rng = random.Random(seed)
    for v in by_repo.values():
        rng.shuffle(v)
    picked, i = [], 0
    while len(picked) < n:                       # round-robin proportional sampling
        for repo in sorted(by_repo, key=lambda r: -len(by_repo[r])):
            quota = round(n * len(by_repo[repo]) / len(tasks) + 0.5)
            if i < len(by_repo[repo]) and i < quota and len(picked) < n:
                picked.append(by_repo[repo][i])
        i += 1
        if i > 400:
            break
    return [t.instance_id for t in picked]


def parse_paths(text: str, files: set[str]) -> list[str]:
    out = []
    for raw in re.findall(r"[\w./-]+\.py", text):
        p = raw.strip("`'\"./")
        hit = p if p in files else next((f for f in sorted(files) if f.endswith("/" + p)), None)
        if hit and hit not in out:
            out.append(hit)
    return out


def main():
    from mlx_lm import generate, load
    model_id, n, conds = sys.argv[1], int(sys.argv[2]), sys.argv[3].split(",")
    tasks = {t.instance_id: t for t in load_tasks()}
    ids = sample_ids(list(tasks.values()), n)
    tag = model_id.split("/")[-1]
    out_path = ROOT / "results" / f"llm_{tag}.jsonl"
    done = set()
    if out_path.exists():
        done = {(r["id"], r["cond"]) for r in map(json.loads, open(out_path))}
    model, tok = load(model_id)
    out = open(out_path, "a")
    for iid in ids:
        t = tasks[iid]
        g = pickle.load(open(ROOT / "cache" / "graphs" / f"{iid}.pkl", "rb"))
        ranked_cache = {}
        for cond in conds:
            if (iid, cond) in done:
                continue
            ranker, layout, budget = cond.split("/")
            if ranker == "none":
                map_block = ""
            else:
                if ranker not in ranked_cache:
                    ranked_cache[ranker] = RANKERS[ranker](t.issue, g)
                m = render(g, ranked_cache[ranker], int(budget), layout, count=lambda s: len(tok.encode(s, add_special_tokens=False)))
                map_block = MAP_BLOCK.format(map=m, sigs_note=" with key definitions" if layout == "sigs" else "")
            prompt = PROMPT.format(repo=t.repo, issue=t.issue[:MAX_ISSUE_CHARS], map_block=map_block, k=5)
            chat = tok.apply_chat_template([{"role": "user", "content": prompt}], add_generation_prompt=True, tokenize=False, enable_thinking=False)
            n_in = len(tok.encode(chat))
            t0 = time.time()
            text = generate(model, tok, prompt=chat, max_tokens=120, verbose=False)
            dt = time.time() - t0
            preds = parse_paths(text, set(g.files))
            ranks = [preds.index(f) + 1 for f in t.gold_files if f in preds]
            row = dict(id=iid, repo=t.repo, cond=cond, model=tag, prompt_tokens=n_in, secs=round(dt, 2),
                       preds=preds, raw=text, gold=t.gold_files, rank=min(ranks) if ranks else None,
                       gold_in_map=(any(f in map_block for f in t.gold_files) if map_block else None))
            out.write(json.dumps(row) + "\n"); out.flush()
            print(f"{iid:40s} {cond:20s} in={n_in:5d} {dt:5.1f}s rank={row['rank']} map={row['gold_in_map']}", flush=True)


if __name__ == "__main__":
    main()
