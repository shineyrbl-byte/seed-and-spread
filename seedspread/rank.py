"""File rankers. Every ranker maps (issue text, CodeGraph) -> files ordered best-first.

  tree        alphabetical paths (what a naive "repo map" shows first)
  bm25        lexical retrieval over file contents (Agentless-style baseline)
  pagerank    global PageRank on the code graph (Aider-style repo map)
  seed        issue-seeded symbols/files only, no propagation
  ppr         Seed & Spread: personalized PageRank restarted at issue seeds
  ppr+bm25    Seed & Spread with BM25 hits added to the restart distribution
"""
from __future__ import annotations

import math
import re
from collections import Counter, defaultdict

import numpy as np
from rank_bm25 import BM25Okapi

from .graph import CodeGraph, module_name

IDENT = re.compile(r"[A-Za-z_][A-Za-z0-9_]{2,}")
DOTTED = re.compile(r"[A-Za-z_][\w]*(?:\.[A-Za-z_]\w*)+")
PATHLIKE = re.compile(r"[\w./-]+\.py")
STOP = set("""the and for this that with from not are was but have has had you your can will would should could
into when then than there their what which while where who why how does did done use used using get set
true false none self cls return import def class pass raise print error errors issue bug fix expected actual
output input value values type types file files code line lines example version python result results test tests
following work works working also just like make made need any all some one two new old first last data object""".split())


def tokenize_code(text: str) -> list[str]:
    out = []
    for tok in IDENT.findall(text):
        low = tok.lower()
        out.append(low)
        parts = [p for p in re.split(r"_|(?<=[a-z])(?=[A-Z])", tok) if len(p) > 2]
        if len(parts) > 1:
            out.extend(p.lower() for p in parts)
    return out


def rank_tree(issue: str, g: CodeGraph) -> list[str]:
    return sorted(g.files)


_BM25_CACHE: dict = {"g": None, "by_issue": {}}


def rank_bm25(issue: str, g: CodeGraph) -> list[str]:
    # cache holds a reference to g itself: id() can be reused after garbage collection
    if _BM25_CACHE["g"] is not g:
        _BM25_CACHE["g"], _BM25_CACHE["by_issue"] = g, {}
    if issue not in _BM25_CACHE["by_issue"]:
        _BM25_CACHE["by_issue"][issue] = _rank_bm25(issue, g)
    return list(_BM25_CACHE["by_issue"][issue])


def _rank_bm25(issue: str, g: CodeGraph) -> list[str]:
    paths = list(g.files)
    docs = [tokenize_code(p.replace("/", " ") + " " + g.files[p]) for p in paths]
    q = [t for t in tokenize_code(issue) if t not in STOP]
    scores = BM25Okapi(docs).get_scores(q) if q else np.zeros(len(paths))
    return [paths[i] for i in np.argsort(-scores, kind="stable")]


def _transition(g: CodeGraph):
    nodes = g.nodes
    idx = {n: i for i, n in enumerate(nodes)}
    rows, cols, vals = [], [], []
    for a, outs in g.edges.items():
        tot = sum(outs.values())
        for b, w in outs.items():
            rows.append(idx[b]); cols.append(idx[a]); vals.append(w / tot)
    from scipy.sparse import csr_matrix
    M = csr_matrix((vals, (rows, cols)), shape=(len(nodes), len(nodes)))
    dangling = np.ones(len(nodes), dtype=bool)
    dangling[[idx[a] for a, o in g.edges.items() if o]] = False
    return nodes, idx, M, dangling


def _pagerank(g: CodeGraph, restart: np.ndarray | None, alpha: float = 0.85, iters: int = 60) -> dict[str, float]:
    nodes, idx, M, dangling = _transition(g)
    n = len(nodes)
    v = np.full(n, 1.0 / n) if restart is None else restart / restart.sum()
    x = v.copy()
    for _ in range(iters):
        x_new = alpha * (M @ x + x[dangling].sum() * v) + (1 - alpha) * v
        if np.abs(x_new - x).sum() < 1e-9:
            x = x_new
            break
        x = x_new
    return dict(zip(nodes, x))


def file_scores(g: CodeGraph, node_scores: dict[str, float]) -> dict[str, float]:
    """A file's score = its own mass + the max mass of any symbol it defines."""
    out = {}
    for f in g.files:
        syms = g.file_symbols.get(f, [])
        out[f] = node_scores.get(f, 0.0) + max((node_scores.get(s, 0.0) for s in syms), default=0.0)
    return out


def _order(g: CodeGraph, scores: dict[str, float], tiebreak: list[str] | None = None) -> list[str]:
    tb = {p: i for i, p in enumerate(tiebreak or sorted(g.files))}
    return sorted(g.files, key=lambda p: (-scores.get(p, 0.0), tb[p]))


def rank_pagerank(issue: str, g: CodeGraph) -> list[str]:
    return _order(g, file_scores(g, _pagerank(g, None)))


def seeds(issue: str, g: CodeGraph) -> dict[str, float]:
    """Map issue text onto graph nodes, weighting rare names more (IDF over definitions).

    Signals: explicit file paths / tracebacks, dotted module paths, and identifiers
    that match defined symbol names. Each seed weight is idf * log(1 + mentions).
    """
    w: dict[str, float] = defaultdict(float)
    n_sym = max(len(g.symbols), 1)
    # 1) explicit paths (tracebacks, "in django/db/models/query.py")
    for m in PATHLIKE.findall(issue):
        m = m.lstrip("./")
        for f in g.files:
            if f == m or f.endswith("/" + m) or (m.count("/") >= 1 and m.endswith(f)):
                w[f] += 3.0
    # 2) dotted module paths ("django.db.models.query.QuerySet")
    for d in DOTTED.findall(issue):
        parts = d.split(".")
        for k in range(len(parts), 1, -1):
            f = g.module_to_file.get(".".join(parts[:k]))
            if f:
                w[f] += 2.0
                rest = parts[k:]
                if rest:
                    for sid in g.by_name.get(rest[-1], []):
                        if g.symbols[sid].path == f:
                            w[sid] += 2.0
                break
    # 3) identifiers that name definitions
    counts = Counter(t for t in IDENT.findall(issue) if t.lower() not in STOP)
    for name, c in counts.items():
        defs = g.by_name.get(name)
        if not defs:
            continue
        idf = math.log(n_sym / len(defs))
        if idf <= 0:
            continue
        share = idf * math.log1p(c) / len(defs)
        for sid in defs:
            w[sid] += share
    return dict(w)


def rank_seed(issue: str, g: CodeGraph) -> list[str]:
    s = seeds(issue, g)
    return _order(g, file_scores(g, s), rank_bm25(issue, g))


def _ppr_from(g: CodeGraph, seed_w: dict[str, float], alpha: float) -> dict[str, float]:
    nodes = g.nodes
    idx = {n: i for i, n in enumerate(nodes)}
    v = np.zeros(len(nodes))
    for n, wt in seed_w.items():
        v[idx[n]] += wt
    if v.sum() == 0:
        return {}
    return file_scores(g, _pagerank(g, v, alpha=alpha))


def rank_ppr(issue: str, g: CodeGraph, alpha: float = 0.5) -> list[str]:
    s = seeds(issue, g)
    bm = rank_bm25(issue, g)
    if not s:
        return bm
    return _order(g, _ppr_from(g, s, alpha), bm)


def rank_ppr_bm25(issue: str, g: CodeGraph, alpha: float = 0.5, k: int = 10) -> list[str]:
    s = dict(seeds(issue, g))
    bm = rank_bm25(issue, g)
    total = sum(s.values()) or 1.0
    for r, f in enumerate(bm[:k]):           # BM25 top-k join the restart set, rank-decayed
        s[f] = s.get(f, 0.0) + total * 0.5 / (r + 1) / sum(1 / (i + 1) for i in range(k))
    return _order(g, _ppr_from(g, s, alpha), bm)


RANKERS = {
    "tree": rank_tree,
    "bm25": rank_bm25,
    "pagerank": rank_pagerank,
    "seed": rank_seed,
    "ppr": rank_ppr,
    "ppr+bm25": rank_ppr_bm25,
}


# ---------------------------------------------------------------------------
# Seed & Spread, parametrized. Variants are selected on SWE-bench *dev* (repos
# disjoint from Lite test) by scripts/tune.py; every variant is reported on test.
# ---------------------------------------------------------------------------
_PR_CACHE: dict = {"g": None, "pr": None}


def _global_pr(g: CodeGraph) -> dict[str, float]:
    if _PR_CACHE["g"] is not g:
        _PR_CACHE["g"], _PR_CACHE["pr"] = g, _pagerank(g, None)
    return _PR_CACHE["pr"]


def ss_scores(issue: str, g: CodeGraph, alpha: float = 0.5, norm: bool = False,
              agg: str = "file+max") -> dict[str, float]:
    """File scores from personalized PageRank restarted at issue seeds.

    alpha  probability of following an edge (1 - alpha = restart)
    norm   divide by global PageRank (smoothed): removes hub bias, keeps what is
           specifically close to *this* issue rather than central to the repo
    agg    "file+max": file mass + best symbol;  "max": best symbol only;
           "sum": file mass + all symbol mass
    """
    s = seeds(issue, g)
    if not s:
        return {}
    nodes = g.nodes
    idx = {n: i for i, n in enumerate(nodes)}
    v = np.zeros(len(nodes))
    for n, wt in s.items():
        v[idx[n]] += wt
    x = _pagerank(g, v, alpha=alpha)
    if norm:
        pr = _global_pr(g)
        smooth = float(np.median(list(pr.values())))
        x = {n: val / (pr[n] + smooth) for n, val in x.items()}
    out = {}
    for f in g.files:
        syms = [x.get(sym, 0.0) for sym in g.file_symbols.get(f, [])]
        own = x.get(f, 0.0)
        if agg == "max":
            out[f] = max(syms, default=0.0) + (own if f in s else 0.0)
        elif agg == "sum":
            out[f] = own + sum(syms)
        else:
            out[f] = own + max(syms, default=0.0)
    return out


def rrf(*rankings: list[str], k: int = 60, weights: list[float] | None = None) -> list[str]:
    """Reciprocal rank fusion (Cormack et al., 2009)."""
    weights = weights or [1.0] * len(rankings)
    score: dict[str, float] = defaultdict(float)
    for w, r in zip(weights, rankings):
        for i, f in enumerate(r):
            score[f] += w / (k + i + 1)
    return sorted(score, key=lambda f: -score[f])


def rank_ss(issue: str, g: CodeGraph, alpha: float = 0.5, norm: bool = False, agg: str = "file+max",
            fuse: str = "none") -> list[str]:
    bm = rank_bm25(issue, g)
    sc = ss_scores(issue, g, alpha, norm, agg)
    ss = _order(g, sc, bm) if sc else bm
    if fuse == "rrf":
        return rrf(bm, ss)
    if fuse == "rrf3":
        return rrf(bm, ss, rank_seed(issue, g))
    return ss
