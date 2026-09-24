# Contextuality gap search: exhaustive to 11 vertices, and the Ramsey connection

Code, results and paper sources for

> **Maximum Contextuality Gap up to Eleven Vertices and the Ramsey Structure of Its Maximizers** — Dan Musetoiu, 2026 (arXiv, in preparation).

In the Cabello–Severini–Winter exclusivity-graph framework, a noncontextuality inequality is a graph `G`,
its noncontextual bound is the independence number `α(G)` and its quantum bound is the Lovász number `ϑ(G)`.
This repository maximizes the absolute contextuality gap `Δ(G) = ϑ(G) − α(G)`:

| n | connected graphs | max Δ | ϑ | α | graph6 | note |
|---|---|---|---|---|---|---|
| 8 | 11,117 | 0.467844 | 3.467844 | 3 | `GCQb`o` | Quad-C5 (Tamer et al. 2026), reproduced |
| 9 | 261,080 | **2/3** | 11/3 | 3 | `HCRbdO{` | new |
| 10 | 11,716,571 | **1/√2** | 3+1/√2 | 3 | `ICRb`yiu?` | new |
| 11 | 1,006,700,565 | **0.774889** | 4.774889 | 4 | `J?`D@pgd?{?` | new; triangle-free, an R(3,5)-graph |

Triangle-free class, exhaustive: n=12 → 0.930021 (`K?`DA`gd?{Dg`), n=13 → 1.181737 = the Ramsey graph C13(1,5),
n=14 → 1.072373 (445,781,050 graphs, 6.1 h; the drop is forced by R(3,5)=14, which pushes α to 5).
Every record graph is an R(3,k)-graph (triangle-free with α ≤ k−1); computing ϑ over McKay's complete catalogues of
R(3,k)-graphs gives lower bounds on Δ_max(n) up to n=35 (Δ ≥ 4.4106 from the unique R(3,9)-critical graph).
See `PAPER_SUMMARY.md` and `NOTES.md` for the full story and the lab log.

## Method in one paragraph
`α` is computed exactly by enumerating all 2^n vertex subsets. `ϑ` is computed exactly with the Clarabel interior-point
SDP solver. For n=11 (10^9 graphs) a **rigorous GPU screen** is used first (`gpu_screen.py`): any matrix `Y` supported on
the edges gives a certified upper bound `λ_max(J+Y) ≥ ϑ(G)` (dual SDP); `Y` is optimized per graph with a few Adam steps on
the softmax-smoothed largest eigenvalue using batched `eigh` on the GPU, graphs whose certified bound cannot beat the
running record are dropped, and the ~100 survivors are solved exactly. All 1,006,700,565 connected 11-vertex graphs were
screened in 2.4 h on an RTX 2000 Ada (8 GB). The screen was validated on n=9 and n=10 against the known answers with
zero misses.

## Files
| file | purpose |
|---|---|
| `gap_search.py` | exact α (bitmask) + exact ϑ (Clarabel direct API), multiprocessing; `python gap_search.py data/graph9c.g6 results/n9.csv` |
| `gpu_screen.py` | GPU batched α and rigorous dual upper bound on ϑ with progressive pruning |
| `run_n11.py` | the n=11 exhaustive run: `geng` → GPU screen (50 resumable parts) → Clarabel on survivors |
| `run_geng.py` | same pipeline for any geng-defined class, e.g. `--geng "-c -t"` (connected triangle-free) |
| `ramsey_theta.py` | ϑ over McKay's R(3,k) catalogues (α = k−1 analytically) |
| `paper/` | LaTeX source, `make_figures.py`, figures |
| `results/` | CSVs: exhaustive n=6..9 (full), n=10 (top excerpt; full file is 730 MB, reproducible in 51 min), n=11 survivors (exact), triangle-free n=11..13, Ramsey families (full for ≤ 20 MB, top excerpts otherwise) |
| `NOTES.md`, `PAPER_SUMMARY.md` | lab log and paper-level summary |

## Reproduce
```
pip install numpy scipy networkx clarabel torch pandas
# graph lists: https://users.cecs.anu.edu.au/~bdm/data/graphs.html  (graph8c.g6 ... graph10c.g6)
# Ramsey graphs: https://users.cecs.anu.edu.au/~bdm/data/ramsey.html
# geng: build nauty 2.8.9 (https://pallini.di.uniroma1.it/); on Windows/MinGW:
#   gcc -O3 -DMAXN=WORDSIZE -DWORDSIZE=32 -o geng.exe geng.c gtools.c nauty.c nautil.c naugraph.c schreier.c naurng.c
python gap_search.py data/graph8c.g6 results/n8.csv          # 2 s, reproduces Tamer et al. Table II
python gap_search.py data/graph9c.g6 results/n9.csv          # 30 s
python gpu_screen.py data/graph10c.g6 results/screen10.csv --n 10 --thr 0.65   # 106 s, 30 survivors
python run_n11.py --mod 50 --thr 0.707106                    # 2.4 h on an 8 GB GPU
python run_geng.py --n 12 --tag tf12 --geng "-c -t" --thr 0.70
python ramsey_theta.py data/r36_17.g6 6 results/ramsey_r36_17.csv
```
Graph identifiers are graph6 strings (nauty); decode with `gap_search.g6_to_adj` or networkx.

## License
MIT for the code. Result tables: CC BY 4.0.
