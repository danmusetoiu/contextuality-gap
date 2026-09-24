# Paper summary — "Contextuality gap records: exhaustive search to 11 vertices and the Ramsey connection"

Status 2026-09-24 (end of day 1). All numbers below are reproducible from `research/contextuality/` on Dan's laptop
(RTX 2000 Ada 8 GB, 24 CPU cores); nothing external was used except public graph lists (McKay) and public solvers.

## 1. Problem
CSW exclusivity-graph framework (Cabello–Severini–Winter 2014): for an exclusivity graph G,
- noncontextual (classical) bound = α(G), independence number;
- quantum bound = ϑ(G), Lovász theta number.
Absolute contextuality gap Δ(G) = ϑ(G) − α(G). Tamer, Müstecaplıoğlu, Dizdar, Gedik (arXiv 2605.12828, May 2026)
searched all 11,117 connected graphs on 8 vertices and found "Quad-C5" (Δ = 0.46784, 10 edges) as the n=8 maximizer,
beating the Wagner graph (0.41421). Question: what happens for n ≥ 9, and what structure do maximizers have?

## 2. Main results

### 2.1 Exhaustive maxima of Δ over ALL connected graphs (rigorous)
| n | #connected graphs | max Δ | ϑ | α | |E| | graph6 | structure |
|---|---|---|---|---|---|---|---|
| 5 | 21 | 0.236068 | √5 | 2 | 5 | C5 | KCBS pentagon |
| 7 | 853 | 0.317667 | 3.317667 | 3 | 7 | C7 | (Tamer et al.) |
| 8 | 11,117 | 0.467844 | 3.467844 | 3 | 10 | `GCQb`o` | Quad-C5 (Tamer et al.), reproduced exactly |
| 9 | 261,080 | **2/3 exactly** | 11/3 | 3 | 15 | `HCRbdO{` | new; |Aut|=12, 12 induced C5, 1 triangle, d=4 |
| 10 | 11,716,571 | **1/√2 = 0.707107** | 3+√2/2 | 3 | 20 | `ICRb`yiu?` | new; 4-regular, |Aut|=16, contains Wagner, 4 triangles |
| 11 | 1,006,700,565 | **0.774889** | 4.774889 | 4 | 17 | `J?`D@pgd?{?` | new; triangle-free, girth 4, an R(3,5)-graph, d=4 |

- n=9: ϑ = 11/3 to 12 digits; runner-up ϑ = 2+φ (Wagner + vertex). n=10: ϑ = 3 + 1/√2 to 12 digits.
- n=9, 10 maxima are derivable from the Cabello–Danielsen–López-Tarrida–Portillo "quantum graphs" table (ϑ to 4 dp for all
  graphs with α<ϑ up to 10 vertices); nobody had reported them. Our runs reproduce that table string-for-string
  (16,533 graphs at n=9; 975,330 at n=10; |Δϑ| ≤ 5.3e-5 = table rounding). **n=11 is beyond every existing table.**
- Regime change at n=11: the dense Wagner-based α=3 family (best 0.735505, = n10 winner + vertex) is overtaken by sparse
  triangle-free α=4 graphs (top five: 0.774889, 0.754686, 0.753664, 0.752419, 0.747377; 17–19 edges).
- Maximizers are NOT a nested family: n=8 (10 e) → n=9 (15 e, 3-fold symmetry) → n=10 (4-regular) → n=11 (tf, 17 e).
  "Previous winner + one vertex" only ever reaches 2nd place (n=9→10: 0.667155; n=10→11: 0.735505).
- Gap maximizer ≠ ratio (ϑ/α) maximizer for n = 8, 10, 11 (ratio maximizers have α=2, e.g. `IUZurzmmo` ratio 1.25 at n=10).

### 2.2 Triangle-free class, exhaustive (rigorous within the class)
| n | #connected tf graphs | max Δ | ϑ | α | |E| | graph6 | note |
|---|---|---|---|---|---|---|---|
| 11 | 90,842 | 0.774889 | 4.774889 | 4 | 17 | `J?`D@pgd?{?` | = global max |
| 12 | 1,144,061 | **0.930021** | 4.930021 | 4 | 20 | `K?`DA`gd?{Dg` | |Aut|=8, an R(3,5)-graph, rank-5 X |
| 13 | ~19.3M | **1.181737** | 5.181737 | 4 | 26 | `L?`DE`gl@YJODg` | = Ramsey graph C13(1,5); next best 0.854 (α=5) |

### 2.3 The Ramsey connection (the story of the paper)
Triangle-free graphs with α ≤ k−1 are exactly the R(3,k)-graphs, which exist only for n < R(3,k). Verified by isomorphism
against McKay's Ramsey lists: Quad-C5 and Wagner ∈ R(3,4)-graphs on 8 vertices (3 graphs); n=11 global winner ∈ R(3,5)
on 11 vertices (105 graphs); n=12 tf winner ∈ R(3,5) on 12 vertices (12 graphs); n=13 tf winner = the unique R(3,5) graph
on 13 vertices, C13(1,5), with ϑ = 13·(−λmin)/(λmax−λmin) = 5.181736625 in closed form (edge-transitive Lovász formula).
At n=9,10 (R(3,4)=9 forbids tf with α=3) the winners keep α=3 by admitting 1 resp. 4 triangles.
Interpretation: Δ_max(n) is governed by Ramsey numbers R(3,k): α is pinned at k−1 while ϑ grows with n; the gap jumps at
n = R(3,k)−1 and drops when α is forced up at n = R(3,k).

Lower bounds on Δ_max(n) from Ramsey-critical graphs (α = k−1 analytic, ϑ by SDP over McKay's complete lists):
| family | n | #graphs | α | max ϑ | max Δ | best graph |
|---|---|---|---|---|---|---|
| R(3,5) | 13 | 1 | 4 | 5.181737 | 1.181737 | C13(1,5) |
| R(3,6) | 14 | 263,520 | 5 | 6.072373 (connected) | 1.072373 | `MqGOOH@_gQ?oGFCJ?` |
| R(3,6) | 15 | 64,732 | 5 | 6.250964 | 1.250964 | `NoCOWGACGQIKGePIDI?` |
| R(3,6) | 16 | 2,576 | 5 | 6.465350 | 1.465350 | `OoC?Igi_?E_eKcRCE@iO[` |
| R(3,6) | 17 | 7 | 5 | 6.606664 | 1.606664 | `P@oGQA?`ACcdCtDYC]Ah?goC` |
| R(3,7) | 21 | 1,118,436 | 6 | 8.141315 | 2.141315 | `THoGG?JODHsOADs_wg?`GgSCZ??ig@@D@?GT` |
| R(3,7) | 22 | 191 | 6 | 8.398747 | 2.398747 | `UsaC?GGC?DccQDCpKEJAOKW`Bo?kD_[_okHCUR??` |
| R(3,8) | 27 | 477,142 | 7 | 10.060569 | 3.060569 | `Z@O\MagCADc`e@O__`KoHO_CCHN?_G@DO?d??oCwQi??GTSPK?Dc?@YdI?c?` (91 e), 88 min CPU |
| R(3,9) | 35 | 1 | 8 | 12.410586 | 4.410586 | the unique R(3,9)-critical graph |

Within the tf class Δ_max is not monotone in n (13: 1.18 → 14: 1.07); globally it is monotone (add a universal vertex:
ϑ, α unchanged), so global records are attained by the Ramsey-critical vertex counts n = R(3,k)−1.

## 3. Method (all local, reproducible)
- Enumeration: McKay's `graph{8,9,10}c.g6`; nauty 2.8.9 `geng` compiled with MinGW gcc for n=11 (1.0e9 graphs, 50
  resumable res/mod parts) and for classes (`-t` triangle-free).
- α: exact, bitmask enumeration of all 2^n subsets (CPU numpy for n ≤ 11; GPU batched, chunked over subsets, for n ≤ 14).
- ϑ exact: Clarabel interior-point SDP via its direct API (PSD-triangle cone), tol 1e-9; ~8k graphs/s on 20 processes.
- **GPU screening (the enabling tool for n=11):** dual SDP ϑ(G) = min λmax(J+Y), Y supported on E, so ANY Y is a rigorous
  upper bound. Per graph: 100 Adam steps on the softmax-smoothed λmax (τ 0.3→0.02) with batched fp32 `eigh`; every 10 steps
  prune graphs whose fp32 λmax + 1e-3 − α < threshold (rigorous: bound only decreases); float64 certificate for survivors;
  survivors re-solved exactly with Clarabel. 95k–130k graphs/s at n=11 → all 1.0e9 graphs in 2.41 h, 100 survivors.
- Validation: n=8 top-10 reproduces Tamer et al. Table II exactly; n=9 screen (thr 0.60) → exactly the 2 true winners;
  n=10 screen (thr 0.65) → exactly the 30 table graphs with Δ ≥ 0.65; n=10 full CPU run matches the Danielsen table.
- Ramsey families: `ramsey_theta.py` (α analytic, ϑ Clarabel, 12 processes): R(3,7) n=21 in 74 min, R(3,8) n=27 in ~1.6 h.

## 4. What is new vs. literature
- Tamer et al. 2026: n=8 only. We extend exhaustively to n=9, 10, 11 (n=11 = 1e9 graphs, first ever) and explain the winners.
- Cabello–Danielsen–López-Tarrida–Portillo 2013 / Danielsen table: ϑ for all "quantum" graphs ≤ 10 vertices — contains
  the n=9,10 maxima implicitly but never states them; no n=11; no structural explanation.
- Muller–Saniga 2026 (automated KS proofs) and Cañas et al. 2016 (ratio maximizers ≤ 10 vertices): different objective.
- The Ramsey-critical link (R(3,k)-graphs as gap maximizers, closed-form ϑ for C13(1,5), the Δ ladder up to n=35) appears
  to be new. Needs a literature check on "Lovász theta of Ramsey graphs" (there is work on ϑ of R(3,k) graphs in the context
  of Shannon capacity / Ramsey bounds — must cite and differentiate).
- The GPU rigorous-screening method (dual certificates + progressive pruning) is a reusable contribution for graph-parameter
  searches over 1e9 graphs on a consumer GPU.

## 5. Open items before a draft
1. **Theory:** state and prove what can be proved: (a) monotonicity of global Δ_max via universal vertex; (b) for tf graphs,
   Δ ≤ ϑ − (k−1) with n < R(3,k) — i.e. Ramsey numbers bound α from below; (c) upper bounds on ϑ for tf graphs
   (ϑ ≤ ... via Hoffman / degree) to bound Δ_max(n) from above; (d) the edge-transitive closed form for circulant winners.
2. **Is the global maximizer at n=12 Ramsey-critical?** Unknown (1.64e11 graphs ≈ 3 weeks GPU brute force). Options:
   local search from winners (edge moves + exact ϑ) to look for any graph with triangles beating 0.930021; or prove that
   triangles can't help beyond some bound.
3. **Physics content:** minimal realization dimension d* (rank of optimal X: 4 for n=9,10,11; 5 at n=12), noise robustness /
   visibility v* for the new winners (à la Tamer et al. §IV), explicit orthonormal representations (vectors) for the
   n=9 (ϑ=11/3), n=10 (3+1/√2) and C13(1,5) witnesses — these are the experimentally relevant deliverables.
4. **Certificates:** publish dual SDP certificates (rational or high-precision) for the record graphs; verify ϑ with a
   second solver (SCS/MOSEK-free) — already done informally for n=9,10,13.
5. **Literature check** (arXiv): "Lovász theta Ramsey graphs", "Shannon capacity R(3,k)", "contextuality Ramsey".
6. Optional compute: tf n=14 exhaustive (~5 h, predicted max ≈ 1.07–1.1 since α ≥ 5); complete R(3,6) n=13 with exact α;
   R(3,8) n=26 / R(3,9) n=34 lists if available.
7. Writing: target ~10–14 pages, quant-ph + math.CO, single author. Figures: (1) Δ_max(n) ladder with Ramsey thresholds
   marked; (2) the five record graphs drawn; (3) GPU screen validation (bound tightness histogram, survivors vs threshold);
   (4) tf-vs-all comparison at n=11.

## 6. Files
`gap_search.py` (CPU exact), `gpu_screen.py` (GPU rigorous screen), `run_n11.py`, `run_geng.py` (any geng class),
`ramsey_theta.py`, `geng.exe`, `NOTES.md` (lab log), `results/` (n8–n11 CSVs, screen*/tf*/ramsey_* CSVs), `data/` (graph lists).
