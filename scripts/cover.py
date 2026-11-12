"""Cover card -> paper/cover.png (numbers from results/analysis.md)."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

P = Path(__file__).resolve().parents[1] / "paper"
SURF, INK, INK2, GRID, BLUE = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df", "#2a78d6"
fig = plt.figure(figsize=(9, 4.5), dpi=200, facecolor=SURF)
t = lambda x, y, s, **k: fig.text(x, y, s, family="DejaVu Sans", va="top", **k)
t(.058, .88, "Seed, Don't Spread", size=34, weight="bold", color=INK)
t(.058, .72, "What a small on-device model needs to see of a repository", size=15, color=INK2)
fig.add_artist(plt.Line2D([.058, .942], [.575, .575], color=GRID, lw=1.2))
cols = [(.058, "15% → 65%", "Gemma 4 E2B top-1 file accuracy,\nno map → issue-conditioned map"),
        (.383, "25%", "with a global-PageRank map\n(centrality, not the issue)"),
        (.633, "+0.034 MRR", "seed+bm25 over BM25 on SWE-bench\nLite test (p = 0.015), dev-selected")]
for x, big, small in cols:
    t(x, .48, big, size=24, weight="bold", color=BLUE)
    t(x, .32, small, size=10, color=INK2, linespacing=1.5)
t(.058, .12, "Gemma 4 E2B / E4B · 4-bit MLX · one 8 GB laptop · 300 SWE-bench Lite tasks · Apache-2.0", size=10.5, color=INK2)
fig.savefig(P / "cover.png", facecolor=SURF)
