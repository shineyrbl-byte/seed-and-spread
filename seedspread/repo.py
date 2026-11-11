"""Read a repository snapshot straight from a bare git object store.

No checkout is needed: we list blobs at a commit with `git ls-tree` and stream
their contents through one `git cat-file --batch` process. This makes it cheap
to build hundreds of historical snapshots (one per SWE-bench task).
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

TEST_PATH = re.compile(r"(^|/)(tests?|testing)(/|$)|(^|/)test_[^/]*\.py$|_tests?\.py$|(^|/)conftest\.py$")
SKIP_PATH = re.compile(r"(^|/)(docs?|examples?|benchmarks?|asv_bench|tutorials?|galleries|build|\.github)/")


def repo_dir(cache: Path, repo: str) -> Path:
    return cache / "repos" / (repo.replace("/", "__") + ".git")


def is_candidate(path: str) -> bool:
    """Source files a fix could plausibly touch (tests/docs/examples excluded)."""
    return path.endswith(".py") and not TEST_PATH.search(path) and not SKIP_PATH.search(path)


def python_files(gitdir: Path, commit: str) -> dict[str, str]:
    """Return {path: source} for every candidate .py file at `commit`."""
    out = subprocess.run(
        ["git", "--git-dir", str(gitdir), "ls-tree", "-r", "--full-tree", commit],
        check=True, capture_output=True, text=True,
    ).stdout
    entries = []
    for line in out.splitlines():
        meta, path = line.split("\t", 1)
        _mode, kind, sha = meta.split()
        if kind == "blob" and is_candidate(path):
            entries.append((path, sha))
    if not entries:
        return {}
    proc = subprocess.run(
        ["git", "--git-dir", str(gitdir), "cat-file", "--batch"],
        input="".join(sha + "\n" for _, sha in entries).encode(),
        check=True, capture_output=True,
    )
    buf, pos, files = proc.stdout, 0, {}
    for path, _sha in entries:
        nl = buf.index(b"\n", pos)
        size = int(buf[pos:nl].split()[2])
        start = nl + 1
        files[path] = buf[start:start + size].decode("utf-8", "replace")
        pos = start + size + 1
    return files
