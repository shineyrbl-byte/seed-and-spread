# Seed & Spread: What Should a Small On-Device Model See of a Repository?

### Issue-seeded code-graph maps under a token budget, measured with Gemma 4 on an 8 GB laptop

## Abstract

<!-- ABSTRACT: fill after results -->

## 1. Introduction

A coding agent can only fix what it can find. Before a model edits a single line, it has to decide where in a repository of hundreds or thousands of files the problem lives. Large cloud models get there by brute force: long contexts, many tool calls, and retries. A small model running on a laptop cannot afford that. Its context is short, every token of prefill costs real seconds, and it gets confused when the prompt is full of irrelevant code.

The usual remedy is a *repo map*: a compact text summary of the repository (file paths, perhaps signatures) placed in the prompt so the model can orient itself. Popular agents build these maps by ranking code with global PageRank over a dependency graph (Aider), by retrieving files lexically with BM25 (Agentless), or by printing a directory tree. Each of these choices quietly decides what the model can see, and for a small model with a few thousand tokens to spare, that decision matters more than almost anything else.

This paper asks a simple, measurable question: **given a budget of k tokens, which repo map lets a small on-device model localize the files that must change to fix an issue?** We contribute:

1. **Seed & Spread**, a method that builds a lightweight code graph (files, classes, functions, imports and name-resolved references) and ranks it with *personalized* PageRank restarted at "seeds" extracted from the issue: file paths and tracebacks, dotted module paths, and identifiers weighted by how rare they are among the repository's definitions. The ranking is rendered into a map that fits an exact token budget.
2. **A budgeted-localization benchmark** on all 300 SWE-bench Lite tasks. It measures, for each ranker, layout and budget, whether the gold file is even *visible* in the map (a ceiling on any model) and how highly it is ranked.
3. **On-device measurements with Gemma 4** (E2B and E4B, 4-bit, Apple MLX on an 8 GB laptop). We measure how localization accuracy, prompt size and latency trade off across map strategies and budgets.
4. **An open library** (Apache-2.0) that reads historical snapshots straight from git object stores, builds the graph in seconds with the Python standard library only, and reproduces every number in this paper.

<!-- KEY FINDINGS: fill after results -->

## 2. Related work

**Repository-level localization.** SWE-bench (Jimenez et al., 2024) made issue resolution on real repositories the standard test for coding agents, and SWE-bench Lite is its 300-task subset of self-contained bugs. Agent systems such as SWE-agent (Yang et al., 2024) and AutoCodeRover (Zhang et al., 2024) localize by interactive search. Agentless (Xia et al., 2024) showed that a fixed pipeline (hierarchical localization from a file tree, then repair) is competitive. Our setting isolates the first, file-level step of such pipelines for models small enough to run offline.

**Code graphs for LLMs.** RepoGraph (Ouyang et al., 2025), CodexGraph (Liu et al., 2024) and LocAgent (Chen et al., 2025) represent repositories as graphs and let large models traverse or query them, often through many tool calls. Aider's repo map ranks definitions with PageRank over a tree-sitter reference graph and packs them into a token budget (Gauthier, 2023). We keep Aider's budgeted packing but change *where the random walk restarts*. We also measure the effect on small models, which these systems do not target.

**Personalized PageRank for retrieval.** Personalized PageRank (Page et al., 1999; Haveliwala, 2002) biases a random walk toward a restart set. HippoRAG (Gutiérrez et al., 2024) uses query-seeded PPR over a knowledge graph for multi-hop question answering. Seed & Spread applies the same idea to code: the issue's identifiers are the query entities and the code graph is the knowledge graph.

**Long contexts and small models.** Models use information in the middle of long prompts less reliably (Liu et al., 2024), which argues for short, well-ranked contexts over long, exhaustive ones. This is especially true for small models like Gemma 4 (Gemma Team, 2026), which run on-device.

## 3. Method

### 3.1 Snapshots without checkouts

Each SWE-bench task pins a repository to a base commit. Instead of checking out 300 working trees, we read each snapshot straight from a bare clone: `git ls-tree` lists the blobs at the commit, and a single `git cat-file --batch` process streams their contents. Candidate files are Python sources outside test, documentation and example directories. The gold patch never touches tests in SWE-bench Lite, so excluding them loses nothing, and it removes a large class of distractors.

### 3.2 The code graph

We parse every candidate file with Python's `ast` module (no third-party parsers). Nodes are files and the symbols they define: classes, functions and methods, each with a one-line signature. Edges are:

* **contains** (file → symbol, class → method) and its reverse, so relevance can flow both down to definitions and back up to their file;
* **imports** (file → file), resolved for absolute and relative imports by longest known module prefix;
* **references** (symbol or file → symbol): every `Name` and `Attribute` used inside a definition links to all definitions with that name, with weight split 1/k over the k candidates. Names with more than 50 definitions (`get`, `__init__`) carry no signal and are dropped.

Name resolution is approximate by design: no type inference, no cross-file data flow. The graph for a Django snapshot (~850 files, ~9,500 symbols) builds in a few seconds on a laptop CPU.

### 3.3 Seeding from the issue

An issue usually names things. We map its text onto the graph in three ways:

1. **Paths.** Any `*.py` path (e.g. from a traceback) that matches a repository file seeds that file with weight 3.
2. **Dotted names.** `django.db.models.query.QuerySet` is resolved to the longest matching module, which is seeded with weight 2. The trailing name, if defined in that module, is also seeded.
3. **Identifiers.** Every identifier of three or more characters that names a definition and is not a stopword seeds those definitions with weight `idf · log(1 + mentions) / k`. Here idf = log(N / k), N is the number of symbols and k is the number of definitions sharing the name. A rare name like `separability_matrix` dominates. A common one like `save` barely registers.

### 3.4 Spreading

Seed weights form the restart distribution v of a personalized PageRank, x = α·(Mx + d·v) + (1 − α)·v, where M is the column-normalized weighted adjacency matrix and d is the dangling mass. We use α = 0.5, a short walk that stays close to the seeds. A file's score is its own mass plus the largest mass of any symbol it defines. In the **ppr+bm25** variant, the BM25 top-10 files also join the restart set with rank-decayed weight totalling half the seed mass, so issues that name nothing in the code still get a sensible start. Ties are broken by BM25 order.

### 3.5 Rendering under a budget

The ranked files are rendered into one of two layouts. **paths** shows one path per line. **sigs** shows the path plus up to eight top-level signatures, with seeded methods included and ordered by their own score. Files are added in rank order until the next one would exceed the budget, which is counted with the Gemma tokenizer. A file whose signatures do not fit falls back to its bare path. The map therefore never exceeds k tokens.

## 4. Experimental setup

<!-- SETUP / RESULTS / DISCUSSION: fill after results -->

## References

* Chen, Z. et al. (2025). LocAgent: Graph-Guided LLM Agents for Code Localization. ACL 2025.
* Gauthier, P. (2023). Building a better repository map with tree-sitter. aider.chat blog.
* Gemma Team, Google DeepMind (2026). Gemma 4 model card.
* Gutiérrez, B. J. et al. (2024). HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models. NeurIPS 2024.
* Haveliwala, T. (2002). Topic-sensitive PageRank. WWW 2002.
* Jimenez, C. E. et al. (2024). SWE-bench: Can Language Models Resolve Real-World GitHub Issues? ICLR 2024.
* Liu, N. F. et al. (2024). Lost in the Middle: How Language Models Use Long Contexts. TACL.
* Liu, X. et al. (2024). CodexGraph: Bridging Large Language Models and Code Repositories via Code Graph Databases. arXiv:2408.03910.
* Ouyang, S. et al. (2025). RepoGraph: Enhancing AI Software Engineering with Repository-level Code Graph. ICLR 2025.
* Page, L., Brin, S., Motwani, R., Winograd, T. (1999). The PageRank Citation Ranking: Bringing Order to the Web. Stanford InfoLab.
* Robertson, S., Zaragoza, H. (2009). The Probabilistic Relevance Framework: BM25 and Beyond.
* Xia, C. S. et al. (2024). Agentless: Demystifying LLM-based Software Engineering Agents. arXiv:2407.01489.
* Yang, J. et al. (2024). SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering. NeurIPS 2024.
* Zhang, Y. et al. (2024). AutoCodeRover: Autonomous Program Improvement. ISSTA 2024.
