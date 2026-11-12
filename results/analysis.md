## Snapshots (SWE-bench Lite test)

tasks 300; candidate files median 701.5 (max 863); symbols median 9432.0 (max 29122); edges median 139393.0 (max 1163007); files skipped (syntax/recursion) 15; gold file in candidate set 300/300

## Table 1: rankers, SWE-bench Lite test (n=300), no LLM

| ranker | Acc@1 | Acc@5 | Acc@10 | MRR [95% CI] |
|---|---|---|---|---|
| tree | 0.000 | 0.017 | 0.030 | 0.016 [0.011, 0.023] |
| pagerank | 0.020 | 0.037 | 0.060 | 0.046 [0.031, 0.063] |
| ppr | 0.310 | 0.637 | 0.697 | 0.452 [0.409, 0.496] |
| seed | 0.357 | 0.673 | 0.757 | 0.497 [0.450, 0.544] |
| ppr+bm25 | 0.457 | 0.740 | 0.823 | 0.584 [0.539, 0.631] |
| bm25 | 0.487 | 0.763 | 0.823 | 0.608 [0.564, 0.654] |
| seed+bm25 | 0.527 | 0.773 | 0.847 | 0.642 [0.597, 0.684] |

seed+bm25 vs bm25, Acc@1: diff +0.040, paired bootstrap p=0.060

seed+bm25 vs bm25, MRR: diff +0.034, paired bootstrap p=0.015

### Per-repo MRR

| repo | n | tree | pagerank | ppr | seed | ppr+bm25 | bm25 | seed+bm25 |
|---|---|---|---|---|---|---|---|---|
| django/django | 114 | 0.00 | 0.03 | 0.41 | 0.44 | 0.59 | 0.61 | 0.63 |
| sympy/sympy | 77 | 0.00 | 0.02 | 0.54 | 0.59 | 0.66 | 0.59 | 0.66 |
| scikit-learn/scikit-learn | 23 | 0.01 | 0.03 | 0.69 | 0.76 | 0.83 | 0.83 | 0.85 |
| matplotlib/matplotlib | 23 | 0.06 | 0.09 | 0.41 | 0.45 | 0.49 | 0.52 | 0.57 |
| pytest-dev/pytest | 17 | 0.03 | 0.11 | 0.22 | 0.24 | 0.35 | 0.48 | 0.52 |
| sphinx-doc/sphinx | 16 | 0.02 | 0.08 | 0.19 | 0.28 | 0.31 | 0.68 | 0.59 |
| pylint-dev/pylint | 6 | 0.02 | 0.02 | 0.14 | 0.22 | 0.31 | 0.53 | 0.52 |
| astropy/astropy | 6 | 0.01 | 0.01 | 0.73 | 0.73 | 0.77 | 0.84 | 0.85 |
| psf/requests | 6 | 0.12 | 0.06 | 0.65 | 0.69 | 0.69 | 0.67 | 0.67 |
| pydata/xarray | 5 | 0.02 | 0.29 | 0.49 | 0.52 | 0.40 | 0.43 | 0.57 |
| mwaskom/seaborn | 4 | 0.05 | 0.32 | 0.52 | 0.52 | 0.52 | 0.54 | 0.53 |
| pallets/flask | 3 | 0.19 | 0.16 | 0.54 | 0.73 | 0.56 | 0.56 | 0.58 |

## Table 2: gold file visible in the map, by budget (Gemma 4 tokens)

| ranker | paths/500 | paths/1000 | paths/2000 | paths/4000 | paths/8000 | sigs/500 | sigs/1000 | sigs/2000 | sigs/4000 | sigs/8000 |
|---|---|---|---|---|---|---|---|---|---|---|
| tree | 0.14 | 0.28 | 0.42 | 0.53 | 0.74 | 0.04 | 0.07 | 0.09 | 0.21 | 0.37 |
| pagerank | 0.33 | 0.54 | 0.76 | 0.92 | 1.00 | 0.05 | 0.13 | 0.21 | 0.36 | 0.60 |
| ppr | 0.84 | 0.88 | 0.93 | 0.97 | 1.00 | 0.68 | 0.72 | 0.80 | 0.86 | 0.90 |
| seed | 0.90 | 0.95 | 0.97 | 1.00 | 1.00 | 0.74 | 0.79 | 0.87 | 0.92 | 0.96 |
| ppr+bm25 | 0.94 | 0.97 | 0.98 | 0.99 | 1.00 | 0.82 | 0.88 | 0.92 | 0.95 | 0.98 |
| bm25 | 0.92 | 0.96 | 0.98 | 1.00 | 1.00 | 0.82 | 0.86 | 0.90 | 0.94 | 0.97 |
| seed+bm25 | 0.93 | 0.96 | 0.98 | 1.00 | 1.00 | 0.84 | 0.88 | 0.91 | 0.94 | 0.97 |

## Variant grid on dev (n=223)

| variant | Acc@1 | Acc@5 | MRR |
|---|---|---|---|
| rrf(bm25,seed) | 0.605 | 0.843 | 0.714 |
| ss[a=0.5,norm=0,agg=file+max,fuse=rrf] | 0.574 | 0.807 | 0.677 |
| bm25 | 0.565 | 0.807 | 0.676 |
| ss[a=0.2,norm=0,agg=max,fuse=rrf] | 0.565 | 0.830 | 0.675 |
| ss[a=0.2,norm=0,agg=file+max,fuse=rrf] | 0.565 | 0.816 | 0.675 |
| ss[a=0.5,norm=0,agg=max,fuse=rrf] | 0.556 | 0.830 | 0.669 |
| ss[a=0.2,norm=1,agg=file+max,fuse=rrf] | 0.538 | 0.821 | 0.659 |
| ss[a=0.2,norm=1,agg=max,fuse=rrf] | 0.534 | 0.830 | 0.658 |
| ss[a=0.5,norm=1,agg=max,fuse=rrf] | 0.534 | 0.825 | 0.657 |
| ss[a=0.8,norm=1,agg=max,fuse=rrf] | 0.534 | 0.821 | 0.656 |
| ss[a=0.5,norm=1,agg=file+max,fuse=rrf] | 0.534 | 0.821 | 0.655 |
| ss[a=0.8,norm=0,agg=max,fuse=rrf] | 0.529 | 0.812 | 0.652 |
| ss[a=0.8,norm=0,agg=file+max,fuse=rrf] | 0.520 | 0.807 | 0.650 |
| seed | 0.511 | 0.825 | 0.649 |
| ss[a=0.8,norm=1,agg=file+max,fuse=rrf] | 0.525 | 0.812 | 0.646 |
| ss[a=0.8,norm=1,agg=max,fuse=none] | 0.511 | 0.776 | 0.622 |
| ss[a=0.5,norm=1,agg=max,fuse=none] | 0.502 | 0.776 | 0.614 |
| ss[a=0.2,norm=0,agg=file+max,fuse=none] | 0.493 | 0.767 | 0.613 |
| ss[a=0.2,norm=0,agg=max,fuse=none] | 0.493 | 0.758 | 0.612 |
| ss[a=0.2,norm=1,agg=max,fuse=none] | 0.498 | 0.776 | 0.611 |
| ss[a=0.5,norm=0,agg=max,fuse=none] | 0.489 | 0.762 | 0.610 |
| ss[a=0.5,norm=0,agg=file+max,fuse=none] | 0.489 | 0.762 | 0.610 |
| ss[a=0.5,norm=1,agg=file+max,fuse=none] | 0.498 | 0.776 | 0.609 |
| ss[a=0.2,norm=1,agg=file+max,fuse=none] | 0.493 | 0.776 | 0.608 |
| ss[a=0.8,norm=1,agg=file+max,fuse=none] | 0.484 | 0.767 | 0.602 |
| ss[a=0.8,norm=0,agg=max,fuse=none] | 0.435 | 0.753 | 0.573 |
| ss[a=0.8,norm=0,agg=file+max,fuse=none] | 0.395 | 0.735 | 0.548 |

Mean MRR by alpha (fuse=none): a=0.2: 0.611, a=0.5: 0.611, a=0.8: 0.586

## Variant grid on test (n=300)

| variant | Acc@1 | Acc@5 | MRR |
|---|---|---|---|
| rrf(bm25,seed) | 0.527 | 0.773 | 0.642 |
| ss[a=0.2,norm=1,agg=max,fuse=rrf] | 0.527 | 0.737 | 0.620 |
| ss[a=0.2,norm=1,agg=file+max,fuse=rrf] | 0.520 | 0.743 | 0.619 |
| ss[a=0.2,norm=0,agg=max,fuse=rrf] | 0.520 | 0.747 | 0.617 |
| ss[a=0.5,norm=1,agg=file+max,fuse=rrf] | 0.507 | 0.753 | 0.615 |
| ss[a=0.8,norm=1,agg=file+max,fuse=rrf] | 0.513 | 0.740 | 0.615 |
| ss[a=0.2,norm=0,agg=file+max,fuse=rrf] | 0.513 | 0.737 | 0.614 |
| ss[a=0.8,norm=1,agg=max,fuse=rrf] | 0.510 | 0.743 | 0.611 |
| ss[a=0.5,norm=1,agg=max,fuse=rrf] | 0.507 | 0.740 | 0.611 |
| ss[a=0.5,norm=0,agg=file+max,fuse=rrf] | 0.507 | 0.737 | 0.609 |
| bm25 | 0.487 | 0.763 | 0.608 |
| ss[a=0.5,norm=0,agg=max,fuse=rrf] | 0.507 | 0.720 | 0.608 |
| ss[a=0.8,norm=0,agg=max,fuse=rrf] | 0.490 | 0.733 | 0.601 |
| ss[a=0.8,norm=0,agg=file+max,fuse=rrf] | 0.480 | 0.737 | 0.593 |
| seed | 0.357 | 0.673 | 0.497 |
| ss[a=0.2,norm=0,agg=max,fuse=none] | 0.340 | 0.627 | 0.469 |
| ss[a=0.2,norm=0,agg=file+max,fuse=none] | 0.333 | 0.630 | 0.466 |
| ss[a=0.8,norm=1,agg=max,fuse=none] | 0.337 | 0.627 | 0.462 |
| ss[a=0.5,norm=0,agg=max,fuse=none] | 0.333 | 0.630 | 0.462 |
| ss[a=0.5,norm=1,agg=max,fuse=none] | 0.337 | 0.617 | 0.461 |
| ss[a=0.2,norm=1,agg=max,fuse=none] | 0.337 | 0.610 | 0.458 |
| ss[a=0.5,norm=1,agg=file+max,fuse=none] | 0.330 | 0.617 | 0.457 |
| ss[a=0.8,norm=1,agg=file+max,fuse=none] | 0.323 | 0.630 | 0.457 |
| ss[a=0.2,norm=1,agg=file+max,fuse=none] | 0.330 | 0.610 | 0.455 |
| ss[a=0.5,norm=0,agg=file+max,fuse=none] | 0.310 | 0.637 | 0.452 |
| ss[a=0.8,norm=0,agg=max,fuse=none] | 0.327 | 0.617 | 0.450 |
| ss[a=0.8,norm=0,agg=file+max,fuse=none] | 0.273 | 0.607 | 0.421 |

Mean MRR by alpha (fuse=none): a=0.2: 0.462, a=0.5: 0.458, a=0.8: 0.447

## Table 3: gemma-4-e2b-it-4bit file localization (tasks with all conditions: 100)

| condition | n | Acc@1 [95% CI] | Acc@5 | gold in map | Acc@1 given gold in map | ranker top-1 | prompt tokens | sec/task |
|---|---|---|---|---|---|---|---|---|
| none/none/0 | 100 | 0.15 [0.08, 0.22] | 0.20 | - | - | - | 566 | 2.3 |
| bm25/paths/2000 | 100 | 0.54 [0.44, 0.64] | 0.75 | 0.99 | 0.55 | 0.54 | 2370 | 6.3 |
| bm25/sigs/2000 | 100 | 0.63 [0.54, 0.72] | 0.78 | 0.93 | 0.68 | 0.54 | 2577 | 6.8 |
| pagerank/sigs/2000 | 100 | 0.25 [0.17, 0.34] | 0.35 | 0.23 | 0.52 | 0.01 | 2577 | 6.0 |
| ppr/sigs/2000 | 100 | 0.57 [0.47, 0.67] | 0.75 | 0.85 | 0.67 | 0.40 | 2576 | 6.4 |
| ppr+bm25/sigs/2000 | 100 | 0.63 [0.53, 0.72] | 0.79 | 0.94 | 0.67 | 0.50 | 2577 | 6.5 |
| seed+bm25/paths/2000 | 100 | 0.56 [0.46, 0.66] | 0.77 | 0.97 | 0.58 | 0.63 | 2370 | 6.3 |
| seed+bm25/sigs/500 | 100 | 0.67 [0.58, 0.76] | 0.81 | 0.90 | 0.74 | 0.63 | 1090 | 3.8 |
| seed+bm25/sigs/1000 | 100 | 0.63 [0.54, 0.73] | 0.80 | 0.90 | 0.70 | 0.63 | 1590 | 4.8 |
| seed+bm25/sigs/2000 | 100 | 0.65 [0.55, 0.74] | 0.81 | 0.93 | 0.70 | 0.63 | 2577 | 7.1 |
| seed+bm25/sigs/4000 | 100 | 0.64 [0.54, 0.73] | 0.80 | 0.96 | 0.67 | 0.63 | 4500 | 10.6 |
| tree/paths/2000 | 100 | 0.37 [0.28, 0.47] | 0.49 | 0.47 | 0.51 | 0.00 | 2369 | 5.6 |
- seed+bm25/sigs/2000 vs none/none/0: Acc@1 diff +0.50 (n=100, paired bootstrap p=0.000)
- seed+bm25/sigs/2000 vs bm25/paths/2000: Acc@1 diff +0.11 (n=100, paired bootstrap p=0.000)
- seed+bm25/sigs/2000 vs bm25/sigs/2000: Acc@1 diff +0.02 (n=100, paired bootstrap p=0.272)
- seed+bm25/sigs/2000 vs pagerank/sigs/2000: Acc@1 diff +0.40 (n=100, paired bootstrap p=0.000)
- seed+bm25/sigs/2000 vs ppr/sigs/2000: Acc@1 diff +0.08 (n=100, paired bootstrap p=0.029)
- seed+bm25/sigs/2000 vs ppr+bm25/sigs/2000: Acc@1 diff +0.02 (n=100, paired bootstrap p=0.262)
- seed+bm25/sigs/2000 vs seed+bm25/paths/2000: Acc@1 diff +0.09 (n=100, paired bootstrap p=0.001)
- seed+bm25/sigs/2000 vs seed+bm25/sigs/500: Acc@1 diff -0.02 (n=100, paired bootstrap p=0.800)
- seed+bm25/sigs/2000 vs seed+bm25/sigs/1000: Acc@1 diff +0.02 (n=100, paired bootstrap p=0.317)
- seed+bm25/sigs/2000 vs seed+bm25/sigs/4000: Acc@1 diff +0.01 (n=100, paired bootstrap p=0.354)
- seed+bm25/sigs/2000 vs tree/paths/2000: Acc@1 diff +0.28 (n=100, paired bootstrap p=0.000)

Hybrid (model top-1, then ranker order) vs ranker alone vs model alone, same tasks:
- ppr+bm25/sigs/2000: Acc@1 model 0.63 / ranker 0.50; Acc@5 model 0.79 / ranker 0.81 / hybrid 0.85 (n=100)
- tree/paths/2000: Acc@1 model 0.37 / ranker 0.00; Acc@5 model 0.49 / ranker 0.01 / hybrid 0.37 (n=100)
- bm25/sigs/2000: Acc@1 model 0.63 / ranker 0.54; Acc@5 model 0.78 / ranker 0.81 / hybrid 0.85 (n=100)
- pagerank/sigs/2000: Acc@1 model 0.25 / ranker 0.01; Acc@5 model 0.35 / ranker 0.04 / hybrid 0.27 (n=100)
- ppr/sigs/2000: Acc@1 model 0.57 / ranker 0.40; Acc@5 model 0.75 / ranker 0.72 / hybrid 0.77 (n=100)
- seed+bm25/sigs/2000: Acc@1 model 0.65 / ranker 0.63; Acc@5 model 0.81 / ranker 0.86 / hybrid 0.87 (n=100)
- seed+bm25/sigs/500: Acc@1 model 0.67 / ranker 0.63; Acc@5 model 0.81 / ranker 0.86 / hybrid 0.86 (n=100)
- seed+bm25/sigs/1000: Acc@1 model 0.63 / ranker 0.63; Acc@5 model 0.80 / ranker 0.86 / hybrid 0.86 (n=100)
- seed+bm25/sigs/4000: Acc@1 model 0.64 / ranker 0.63; Acc@5 model 0.80 / ranker 0.86 / hybrid 0.86 (n=100)
- seed+bm25/paths/2000: Acc@1 model 0.56 / ranker 0.63; Acc@5 model 0.77 / ranker 0.86 / hybrid 0.88 (n=100)
- bm25/paths/2000: Acc@1 model 0.54 / ranker 0.54; Acc@5 model 0.75 / ranker 0.81 / hybrid 0.85 (n=100)

responses with no valid path: 108/1200

## Table 3: gemma-4-e4b-it-4bit file localization (tasks with all conditions: 45)

| condition | n | Acc@1 [95% CI] | Acc@5 | gold in map | Acc@1 given gold in map | ranker top-1 | prompt tokens | sec/task |
|---|---|---|---|---|---|---|---|---|
| none/none/0 | 45 | 0.33 [0.20, 0.47] | 0.47 | - | - | - | 632 | 9.1 |
| bm25/sigs/2000 | 45 | 0.69 [0.56, 0.82] | 0.89 | 0.96 | 0.72 | 0.51 | 2627 | 21.9 |
| pagerank/sigs/2000 | 45 | 0.33 [0.20, 0.47] | 0.44 | 0.24 | 0.73 | 0.02 | 2628 | 23.6 |
| seed+bm25/sigs/2000 | 45 | 0.69 [0.56, 0.82] | 0.89 | 0.93 | 0.74 | 0.60 | 2627 | 31.1 |
- seed+bm25/sigs/2000 vs none/none/0: Acc@1 diff +0.36 (n=45, paired bootstrap p=0.000)
- seed+bm25/sigs/2000 vs bm25/sigs/2000: Acc@1 diff +0.00 (n=45, paired bootstrap p=0.615)
- seed+bm25/sigs/2000 vs pagerank/sigs/2000: Acc@1 diff +0.36 (n=45, paired bootstrap p=0.000)

responses with no valid path: 25/181
