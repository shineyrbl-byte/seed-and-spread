"""SWE-bench Lite tasks with gold edit locations parsed from the reference patch."""
from __future__ import annotations

import re
from dataclasses import dataclass

DIFF_FILE = re.compile(r"^diff --git a/(\S+) b/(\S+)$", re.M)
HUNK = re.compile(r"^@@ -\d+(?:,\d+)? \+\d+(?:,\d+)? @@ ?(.*)$", re.M)


@dataclass
class Task:
    instance_id: str
    repo: str
    base_commit: str
    issue: str
    gold_files: list[str]


def gold_files(patch: str) -> list[str]:
    return sorted({b for _a, b in DIFF_FILE.findall(patch)})


def load_tasks(split: str | None = None, dataset: str | None = None) -> list[Task]:
    """Default: SWE-bench Lite test. Override with SS_DATASET / SS_SPLIT env vars
    (we tune on princeton-nlp/SWE-bench dev, whose repos are disjoint from Lite test)."""
    import os
    from datasets import load_dataset
    dataset = dataset or os.environ.get("SS_DATASET", "princeton-nlp/SWE-bench_Lite")
    split = split or os.environ.get("SS_SPLIT", "test")
    ds = load_dataset(dataset, split=split)
    tasks = [Task(r["instance_id"], r["repo"], r["base_commit"], r["problem_statement"], gold_files(r["patch"]))
             for r in ds]
    limit = int(os.environ.get("SS_LIMIT", "0"))      # quick runs: first N tasks
    return tasks[:limit] if limit else tasks
