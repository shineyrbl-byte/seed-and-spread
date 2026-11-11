# Seed & Spread

**How should a small, on-device model *see* a repository under a token budget?**

Seed & Spread turns a Python repository into a compact, budgeted "repo map" for small coding agents.
It builds a lightweight code graph (files, classes, functions, imports, references) with Python's `ast`,
seeds it with what the issue mentions (paths, dotted names, rare identifiers), and spreads relevance
with personalized PageRank. The map is then rendered to fit exactly k tokens.

This repository holds the library, the benchmark harness on SWE-bench Lite, and every experiment in our
paper for the Google Gemma 4 Developer Agent Paper Track. All LLM results come from Gemma 4 running
locally on an 8 GB laptop (Apple MLX, 4-bit).

Status: work in progress (experiments running).

## License
Apache-2.0
