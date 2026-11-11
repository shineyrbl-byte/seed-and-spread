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

## Variant grid on test (n=265)

| variant | Acc@1 | Acc@5 | MRR |
|---|---|---|---|
| rrf(bm25,seed) | 0.517 | 0.777 | 0.637 |
| ss[a=0.2,norm=1,agg=file+max,fuse=rrf] | 0.509 | 0.740 | 0.611 |
| ss[a=0.2,norm=1,agg=max,fuse=rrf] | 0.513 | 0.732 | 0.610 |
| bm25 | 0.483 | 0.766 | 0.609 |
| ss[a=0.2,norm=0,agg=max,fuse=rrf] | 0.509 | 0.743 | 0.609 |
| ss[a=0.5,norm=1,agg=file+max,fuse=rrf] | 0.494 | 0.751 | 0.606 |
| ss[a=0.2,norm=0,agg=file+max,fuse=rrf] | 0.502 | 0.732 | 0.606 |
| ss[a=0.8,norm=1,agg=file+max,fuse=rrf] | 0.498 | 0.736 | 0.605 |
| ss[a=0.5,norm=0,agg=file+max,fuse=rrf] | 0.498 | 0.732 | 0.602 |
| ss[a=0.5,norm=1,agg=max,fuse=rrf] | 0.494 | 0.736 | 0.601 |
| ss[a=0.8,norm=1,agg=max,fuse=rrf] | 0.494 | 0.740 | 0.600 |
| ss[a=0.5,norm=0,agg=max,fuse=rrf] | 0.498 | 0.713 | 0.600 |
| ss[a=0.8,norm=0,agg=max,fuse=rrf] | 0.479 | 0.725 | 0.593 |
| ss[a=0.8,norm=0,agg=file+max,fuse=rrf] | 0.468 | 0.728 | 0.584 |
| seed | 0.332 | 0.664 | 0.481 |
| ss[a=0.2,norm=0,agg=max,fuse=none] | 0.317 | 0.611 | 0.452 |
| ss[a=0.8,norm=1,agg=max,fuse=none] | 0.325 | 0.608 | 0.449 |
| ss[a=0.2,norm=0,agg=file+max,fuse=none] | 0.309 | 0.615 | 0.448 |
| ss[a=0.5,norm=1,agg=max,fuse=none] | 0.325 | 0.596 | 0.447 |
| ss[a=0.5,norm=0,agg=max,fuse=none] | 0.313 | 0.615 | 0.447 |
| ss[a=0.5,norm=1,agg=file+max,fuse=none] | 0.321 | 0.600 | 0.445 |
| ss[a=0.8,norm=1,agg=file+max,fuse=none] | 0.313 | 0.611 | 0.445 |
| ss[a=0.2,norm=1,agg=max,fuse=none] | 0.325 | 0.592 | 0.444 |
| ss[a=0.2,norm=1,agg=file+max,fuse=none] | 0.317 | 0.592 | 0.441 |
| ss[a=0.5,norm=0,agg=file+max,fuse=none] | 0.291 | 0.623 | 0.435 |
| ss[a=0.8,norm=0,agg=max,fuse=none] | 0.309 | 0.604 | 0.435 |
| ss[a=0.8,norm=0,agg=file+max,fuse=none] | 0.253 | 0.592 | 0.404 |

Mean MRR by alpha (fuse=none): a=0.2: 0.446, a=0.5: 0.444, a=0.8: 0.433

## Table 3: gemma-4-e2b-it-4bit file localization (tasks with all conditions: 8)

| condition | n | Acc@1 [95% CI] | Acc@5 | gold in map | Acc@1 given gold in map | ranker top-1 | prompt tokens | sec/task |
|---|---|---|---|---|---|---|---|---|
| none/none/0 | 8 | 0.12 [0.00, 0.38] | 0.25 | - | - | - | 751 | 3.2 |
| bm25/paths/2000 | 8 | 0.75 [0.38, 1.00] | 0.88 | 1.00 | 0.75 | 0.62 | 2422 | 7.1 |
| bm25/sigs/2000 | 8 | 0.75 [0.38, 1.00] | 0.88 | 1.00 | 0.75 | 0.62 | 2775 | 6.9 |
| pagerank/sigs/2000 | 8 | 0.12 [0.00, 0.38] | 0.12 | 0.25 | 0.50 | 0.00 | 2775 | 6.6 |
| ppr/sigs/2000 | 8 | 0.62 [0.25, 1.00] | 0.88 | 0.88 | 0.71 | 0.50 | 2774 | 6.2 |
| ppr+bm25/sigs/2000 | 8 | 0.75 [0.38, 1.00] | 0.88 | 1.00 | 0.75 | 0.38 | 2775 | 7.1 |
| seed+bm25/paths/2000 | 8 | 0.75 [0.38, 1.00] | 0.88 | 1.00 | 0.75 | 0.62 | 2421 | 7.5 |
| seed+bm25/sigs/500 | 8 | 0.75 [0.38, 1.00] | 0.88 | 0.88 | 0.86 | 0.62 | 1275 | 4.6 |
| seed+bm25/sigs/1000 | 8 | 0.62 [0.25, 1.00] | 0.75 | 0.88 | 0.71 | 0.62 | 1773 | 6.0 |
| seed+bm25/sigs/2000 | 8 | 0.75 [0.38, 1.00] | 0.88 | 1.00 | 0.75 | 0.62 | 2776 | 10.7 |
| seed+bm25/sigs/4000 | 8 | 0.75 [0.38, 1.00] | 0.88 | 1.00 | 0.75 | 0.62 | 4642 | 12.1 |
| tree/paths/2000 | 8 | 0.50 [0.12, 0.88] | 0.75 | 0.75 | 0.50 | 0.00 | 2424 | 6.1 |

responses with no valid path: 105/652
