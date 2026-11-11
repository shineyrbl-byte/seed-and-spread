"""Render a ranked list of files into a repository map that fits a token budget.

Two layouts:
  paths  one path per line                     (cheap: ~10 tokens/file, high coverage)
  sigs   path + top-level signatures per file  (rich: shows what each file defines)

Within a file, symbols are listed by their own score (seeded/ranked symbols first),
then by source order. Rendering stops at the budget; the map never exceeds it.
"""
from __future__ import annotations

from typing import Callable

from .graph import CodeGraph


def approx_tokens(s: str) -> int:
    return max(1, len(s) // 4)          # calibrated against the Gemma tokenizer in scripts/calibrate


def render(g: CodeGraph, ranked_files: list[str], budget: int, layout: str = "sigs",
           symbol_scores: dict[str, float] | None = None, max_syms: int = 8,
           count: Callable[[str], int] = approx_tokens) -> str:
    symbol_scores = symbol_scores or {}
    lines, used = [], 0
    for f in ranked_files:
        block = [f]
        if layout == "sigs":
            syms = [g.symbols[s] for s in g.file_symbols.get(f, []) if g.symbols[s].kind != "method"
                    or symbol_scores.get(s, 0) > 0]
            syms.sort(key=lambda s: (-symbol_scores.get(s.id, 0.0), s.line))
            for s in syms[:max_syms]:
                indent = "    " if s.kind == "method" else "  "
                block.append(f"{indent}{s.signature}")
        text = "\n".join(block)
        cost = count(text) + 1
        if used + cost > budget:
            if layout == "sigs" and used + count(f) + 1 <= budget:   # fall back to bare path
                lines.append(f); used += count(f) + 1
                continue
            break
        lines.append(text); used += cost
    return "\n".join(lines)
