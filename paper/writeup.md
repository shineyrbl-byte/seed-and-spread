# Seed, Don't Spread: What a Small On-Device Model Needs to See of a Repository

### A token-budgeted repo-map benchmark on SWE-bench Lite, measured with Gemma 4 running on an 8 GB laptop

## Abstract

Small coding agents that run offline cannot read a whole repository, so what they see first decides what they can fix. We study the first step of issue resolution, finding the file to edit, when a small model gets only a *k*-token "repo map" alongside the issue. We release an open, standard-library-only toolkit. It builds code graphs for all 300 SWE-bench Lite snapshots straight from git objects, ranks files with seven strategies, and renders maps that fit an exact Gemma token budget. We then run Gemma 4 E2B and E4B locally (4-bit, Apple MLX, 8 GB of RAM). Three findings stand out. **(1) What the map is conditioned on matters most.** Issue-conditioned maps lift Gemma 4 E2B from 15% to 63% top-1 file accuracy. A map of the repository's most central code, the global-PageRank construction used by popular agents, scores 25%, barely better than no map. **(2) Use the code graph as an index, not as a diffusion network.** Spreading relevance with personalized PageRank from issue-mentioned symbols consistently *hurts*, and the more it spreads the worse it gets. Using the graph's definition table to weight issue identifiers by rarity, then fusing with BM25, is the best ranker on a held-out dev split and improves test MRR from 0.608 to 0.642 (paired bootstrap p = 0.015). **(3) The small model re-ranks.** Given a well-ranked map, Gemma 4 E2B picks the right file more often than the ranker that built the map. <!-- BUDGET/E4B sentence -->

## 1. Introduction

A coding agent can only fix what it can find. Before a model edits a line, it has to decide where in a repository of hundreds of files the problem lives. Cloud agents get there with long contexts and many tool calls. A model on a laptop cannot: prefill costs seconds per thousand tokens, and small models are easily distracted by irrelevant context.

The standard remedy is a *repo map*, a compact listing of files and perhaps signatures placed in the prompt. Agents build these maps in different ways: global PageRank over a reference graph (Aider), lexical retrieval (Agentless-style BM25), or a plain directory tree. With only a few thousand tokens to spend, that choice determines what a small model can see.

We ask: **given k tokens, which map lets a small on-device model localize the file that must change?** We started out expecting graph *propagation*, personalized PageRank seeded by the issue, to win. It did not, and that negative result turned out to be the most useful thing we learned. Our contributions:

1. **A budgeted-localization benchmark and toolkit** (Apache-2.0). It reads 300 historical snapshots directly from bare git clones, builds a file/symbol graph with Python's `ast`, and implements seven rankers and two map layouts with exact Gemma-token budgets. It also reports a *visibility ceiling* (is the gold file in the map at all?) separately from model accuracy.
2. **A controlled study of graph use.** In a 24-variant grid selected on a disjoint dev split, propagation never beats seeding alone. Our dev-selected ranker, `seed+bm25`, is the best ranker on test.
3. **On-device measurements** with Gemma 4 E2B and E4B. We measure accuracy, visibility, prompt size and latency across map strategies, layouts and budgets, all on one 8 GB laptop.

## 2. Related work

**Repository-level localization.** SWE-bench (Jimenez et al., 2024) is the standard benchmark for issue resolution, and SWE-bench Lite its 300-task subset. SWE-agent (Yang et al., 2024) and AutoCodeRover (Zhang et al., 2024) localize interactively. Agentless (Xia et al., 2024) showed a fixed localize-then-repair pipeline is competitive. We isolate its first, file-level step for models small enough to run offline.

**Code graphs for LLMs.** RepoGraph (Ouyang et al., 2025), CodexGraph (Liu et al., 2024) and LocAgent (Chen et al., 2025) give large models graph-structured access to repositories, typically via multi-step traversal. Aider ranks definitions with PageRank and packs them into a token budget (Gauthier, 2023). We keep budgeted packing, compare global against issue-personalized walks, and target models that cannot afford many tool calls.

**Seeded propagation.** Personalized PageRank (Page et al., 1999; Haveliwala, 2002) biases a random walk toward a restart set. HippoRAG (Gutiérrez et al., 2024) seeds PPR with query entities for multi-hop QA. We test the same idea on code and find it does not transfer to file localization. Reciprocal rank fusion (Cormack et al., 2009) is our fusion operator.

**Context and small models.** Models use mid-context information unreliably (Liu et al., 2024), so short, well-ranked contexts matter for small models such as Gemma 4 (Gemma Team, 2026).

## 3. Method

### 3.1 Snapshots and code graph

Each task pins a repository to a base commit. We read snapshots from bare clones (`git ls-tree` plus one `git cat-file --batch` stream), with no checkouts. Candidates are Python files outside test, docs and example directories. In SWE-bench Lite the gold patch never edits tests, and the gold file is a candidate in 300/300 tasks.

We parse files with Python's `ast`. Nodes are files and their classes, functions and methods, each with a one-line signature. Edges are **contains** (both directions), **imports** (resolved by longest module prefix, including relative imports) and **references**: each name used inside a definition links to all definitions of that name, weight 1/k, with names defined more than 50 times dropped. Resolution is approximate (no types), which keeps construction to seconds per snapshot and dependency-free. Median snapshot: 702 files, 9,432 symbols and 139k edges (max 863 files, 29k symbols, 1.16M edges). 15 of 168,597 file snapshots were skipped (syntax errors or pathological nesting).

### 3.2 Seeds: the graph as an index

Issues name things. We map issue text onto graph nodes in three ways:

1. any `*.py` path matching a repository file (weight 3);
2. dotted module paths resolved to the longest matching module, plus the trailing symbol if defined there (weight 2);
3. identifiers (three or more characters, not stopwords) that name definitions: each of the k definitions gets `log(N/k) · log(1 + mentions) / k`, where N is the number of symbols in the repository.

Rare names (`separability_matrix`) dominate, and common ones (`save`) barely count. The **seed** ranker scores a file by its own seed weight plus its best symbol's.

### 3.3 Spreading (the hypothesis we rejected)

**ppr** runs personalized PageRank with the seeds as the restart distribution, x = α(Mx + d·v) + (1−α)v, and aggregates node mass to files. We grid α ∈ {0.2, 0.5, 0.8}, optional normalization by global PageRank (to remove hub bias), file aggregation (file mass + best symbol, or best symbol only) and optional fusion with BM25: 24 variants.

### 3.4 Baselines and the selected ranker

**tree** lists paths alphabetically. **pagerank** is global PageRank over the same graph (Aider-style centrality). **bm25** is Okapi BM25 over file contents and paths with identifier splitting. **ppr+bm25** adds BM25's top 10 to the PPR restart set. **seed+bm25** is reciprocal rank fusion (k = 60) of the BM25 and seed rankings, chosen by MRR on the dev split (§4.1).

### 3.5 Budgeted rendering

Files are rendered in rank order as **paths** (one per line) or **sigs** (path plus up to eight top-level signatures, with seeded methods first). Rendering stops before the Gemma-tokenized map would exceed k tokens, and a file whose signatures don't fit falls back to its bare path.

## 4. Experiments

**Data.** SWE-bench Lite test (300 tasks, 12 repositories) for all reported results. For model selection we use the SWE-bench **dev** split: 225 tasks from 6 repositories that do not appear in the test set (sqlfluff, pvlib, astroid, pydicom, marshmallow, pyvista). All 300 Lite tasks edit exactly one non-test file, so we report **Acc@k** (gold file in the top k) and **MRR**.

**Models and hardware.** Gemma 4 E2B-it and E4B-it, 4-bit MLX conversions (`mlx-community/gemma-4-e{2,4}b-it-4bit`), on an Apple laptop with 8 GB of unified memory, greedy decoding, thinking disabled. The prompt contains the issue (truncated to 6,000 characters), the map, and an instruction to list the five most likely files. Predicted paths are matched to repository files exactly or by unique suffix. LLM experiments use a fixed, repo-stratified random sample of 100 test tasks (seed 0), and every condition runs on the same tasks. Confidence intervals are 95% bootstrap (2,000 resamples), and comparisons use paired bootstrap tests over tasks.

### 4.1 Selecting a ranker on dev: spreading never helps

On dev (n = 223 with a non-test gold file), the best of the 24 propagation variants reaches MRR 0.677. That is level with plain BM25 (0.676) and below `rrf(bm25, seed)` (0.714). Without fusion, every PPR variant (0.548–0.622) is below the seeds alone (0.649), and more spreading is monotonically worse: mean MRR is 0.611, 0.611 and 0.586 for α = 0.2, 0.5 and 0.8, and the worst α = 0.8 variants fall to 0.548–0.573. Global-PageRank normalization only partly recovers the loss. We therefore select **seed+bm25** and report everything on test.

<!-- VARIANT TEST GRID sentence -->

### 4.2 Rankers on test (no LLM)

| ranker | Acc@1 | Acc@5 | Acc@10 | MRR [95% CI] |
|---|---|---|---|---|
| tree | 0.000 | 0.017 | 0.030 | 0.016 [0.011, 0.023] |
| global PageRank | 0.020 | 0.037 | 0.060 | 0.046 [0.031, 0.063] |
| ppr (α=0.5) | 0.310 | 0.637 | 0.697 | 0.452 [0.409, 0.496] |
| seed | 0.357 | 0.673 | 0.757 | 0.497 [0.450, 0.544] |
| ppr+bm25 | 0.457 | 0.740 | 0.823 | 0.584 [0.539, 0.631] |
| bm25 | 0.487 | 0.763 | 0.823 | 0.608 [0.564, 0.654] |
| **seed+bm25** | **0.527** | **0.773** | **0.847** | **0.642** [0.597, 0.684] |

*Table 1. File ranking on SWE-bench Lite test (n = 300).*

The dev ordering holds on test. seed+bm25 beats BM25 by +0.034 MRR (p = 0.015) and +4.0 points Acc@1 (p = 0.06). It ties or wins in 9 of 12 repositories (largest gains: sympy 0.59→0.66 and matplotlib 0.52→0.57). It loses on sphinx (0.68→0.59), where issues describe behavior rather than naming code. Global PageRank places the gold file first in only 2% of tasks: centrality says what is important to the repository, not to the issue.

<!-- HUB BIAS paragraph -->

### 4.3 Visibility under a budget

![Gold-file visibility by budget](fig_coverage.png)

*Figure 1. Fraction of tasks whose gold file appears in the map, by ranker, layout and budget (Gemma 4 tokens).*

<!-- COVERAGE paragraph -->

### 4.4 Gemma 4 on device

![Gemma 4 E2B accuracy by map](fig_llm_e2b.png)

*Figure 2. Gemma 4 E2B Acc@1 with 2,000-token maps (bars) and the top-1 accuracy of the ranker that built each map, without an LLM (ticks). Same 100 tasks in every condition.*

<!-- LLM TABLE + paragraphs -->

### 4.5 How many tokens does a small model need?

<!-- BUDGET SWEEP -->

## 5. Discussion

<!-- DISCUSSION -->

**Limitations.** We study file-level localization only, not patch generation or end-to-end resolution. All tasks are Python and single-file. Name resolution is untyped. LLM results use 100 tasks per condition, so differences under about 10 points are within noise. We report intervals and avoid such claims. SWE-bench issues may appear in model pre-training data. This affects all conditions equally, and the no-map baseline (15%) bounds how much the model can recall.

## 6. Reproducibility

All code, per-task outputs and the scripts that produce every table and figure are at **github.com/shineyrbl-byte/seed-and-spread** (Apache-2.0), mirrored in a public Kaggle notebook. Pipeline: `build_snapshots.py` → `eval_rankers.py` / `tune.py` → `eval_llm.py` → `analyze.py` / `figures.py`. Building all 300 graphs takes about 30 minutes on a laptop CPU. Each 100-task LLM condition takes about 10–20 minutes on the 8 GB laptop.

## References

* Chen, Z. et al. (2025). LocAgent: Graph-Guided LLM Agents for Code Localization. ACL 2025.
* Cormack, G. V., Clarke, C. L. A., Büttcher, S. (2009). Reciprocal Rank Fusion outperforms Condorcet and individual rank learning methods. SIGIR 2009.
* Gauthier, P. (2023). Building a better repository map with tree-sitter. aider.chat.
* Gemma Team, Google DeepMind (2026). Gemma 4 model card.
* Gutiérrez, B. J. et al. (2024). HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models. NeurIPS 2024.
* Haveliwala, T. (2002). Topic-sensitive PageRank. WWW 2002.
* Jimenez, C. E. et al. (2024). SWE-bench: Can Language Models Resolve Real-World GitHub Issues? ICLR 2024.
* Liu, N. F. et al. (2024). Lost in the Middle: How Language Models Use Long Contexts. TACL.
* Liu, X. et al. (2024). CodexGraph: Bridging Large Language Models and Code Repositories via Code Graph Databases. arXiv:2408.03910.
* Ouyang, S. et al. (2025). RepoGraph: Enhancing AI Software Engineering with Repository-level Code Graph. ICLR 2025.
* Page, L., Brin, S., Motwani, R., Winograd, T. (1999). The PageRank Citation Ranking: Bringing Order to the Web. Stanford InfoLab.
* Robertson, S., Zaragoza, H. (2009). The Probabilistic Relevance Framework: BM25 and Beyond. FnTIR.
* Xia, C. S. et al. (2024). Agentless: Demystifying LLM-based Software Engineering Agents. arXiv:2407.01489.
* Yang, J. et al. (2024). SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering. NeurIPS 2024.
* Zhang, Y. et al. (2024). AutoCodeRover: Autonomous Program Improvement. ISSTA 2024.
