"""Cover card -> paper/cover.png. 2:1 card whose centre square is also a complete thumbnail."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

P = Path(__file__).resolve().parents[1] / "paper"
SURF, INK, INK2, GRID, BLUE = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df", "#2a78d6"
fig = plt.figure(figsize=(8, 4), dpi=200, facecolor=SURF)
t = lambda x, y, s, **k: fig.text(x, y, s, family="DejaVu Sans", ha="center", va="center", **k)
# centre square (x 0.25-0.75): the thumbnail
t(.5, .78, "Seed,\nDon't Spread", size=30, weight="bold", color=INK, linespacing=1.0)
t(.5, .46, "15% → 65%", size=27, weight="bold", color=BLUE)
t(.5, .31, "Gemma 4 E2B finds the file to fix,\nno map → issue-seeded map", size=9.5, color=INK2, linespacing=1.4)
t(.5, .12, "on-device · 8 GB laptop · SWE-bench Lite", size=8.5, color=INK2)
# side panels: card only
for x in (.235, .765):
    fig.add_artist(plt.Line2D([x, x], [.15, .85], color=GRID, lw=1))
t(.118, .46, "25%", size=20, weight="bold", color=BLUE)
t(.118, .31, "with a global-\nPageRank map", size=8.5, color=INK2, linespacing=1.4)
t(.882, .46, "+0.034", size=20, weight="bold", color=BLUE)
t(.882, .31, "MRR over BM25\n(p = 0.015)", size=8.5, color=INK2, linespacing=1.4)
fig.savefig(P / "cover.png", facecolor=SURF)
