# Contextuality-gap search — lab notes

Started 2026-09-24. Goal: extend Tamer et al., "The Quad-C5 Graph: Maximum Contextuality
Gap on Eight Vertices" (arXiv 2605.12828) to n = 9, 10 (exhaustive) and beyond.

Gap = Δ(G) = ϑ(G) − α(G) on the exclusivity graph G (CSW framework):
α = noncontextual bound (independence number), ϑ = quantum bound (Lovász theta).

## Pipeline (`gap_search.py`)
- graph6 parser; α exact by bitmask brute force; ϑ by Clarabel (direct API, PSD-triangle cone), tol 1e-9.
- 20 worker processes on the 24-core laptop: n=8 in 2 s, n=9 in 30 s (8.5k graphs/s), n=10 ≈ 4.6k graphs/s.
- Data: McKay's `graph{8,9,10}c.g6` (connected, non-isomorphic). `graph10c.g6` arrives gzipped.
- `geng.exe` compiled from nauty 2.8.9 with MinGW gcc (no `make`; direct gcc line, -DMAXN=WORDSIZE -DWORDSIZE=32).
  `geng -c -q 11 res/mod` works → n = 11 (1,006,700,565 connected graphs) is generatable locally.

## Validation
- ϑ unit tests: C5 = √5, C7 = 3.3177, Petersen = 4, Wagner = 1+... = 3.414214, Quad-C5 (g6 `GCQb`o`) = 3.467844. All match the paper.
- n=8 top-10 by Δ reproduces the paper's Table II exactly (ranks, |E|, α, ϑ, ratio maximizer = CHSH-type graph, ratio 1.171573).
- Danielsen database (Cabello–Danielsen–López-Tarrida–Portillo, https://www.codetables.de/larsed/quantum_graphs/):
  lists all graphs with α < ϑ up to n=10 with ϑ to 4 dp. Our n=9 set of 16,533 graphs with Δ>0 is identical
  (same graph6 strings, ϑ agrees to rounding). So n ≤ 10 maxima are *derivable from an existing table* —
  never reported as such, but the exhaustive novelty starts at n = 11.
- Clarabel "AlmostSolved" statuses (4 at n=8, 60 at n=9) differ from SCS by < 5e-8; irrelevant to rankings.

## Results
| n | max Δ | ϑ | α | graph6 | |E| | notes |
|---|---|---|---|---|---|---|
| 5 | 0.236068 | √5 | 2 | C5 | 5 | KCBS |
| 7 | 0.317667 | 3.3177 | 3 | C7 | 7 | (paper) |
| 8 | 0.467844 | 3.467844 | 3 | `GCQb`o` | 10 | Quad-C5 (paper) |
| 9 | **2/3 exactly** | 11/3 | 3 | `HCRbdO{` | 15 | new; see below |
| 10 | 1/√2 = 0.707107 (CONFIRMED by our full CPU run, 51 min) | 3+√2/2 | 3 | `ICRb`yiu?` | 20 | 4-regular, contains Wagner |
| 11 | **0.774889** (EXHAUSTIVE, all 1,006,700,565 connected graphs, GPU screen 2.41 h, 100 survivors re-solved exactly) | 4.774889 | 4 | `J?`D@pgd?{?` | 17 | triangle-free, girth 4, degrees 2^1 3^8 4^2, |Aut|=2, 11 induced C5 + 4 induced C7, rank-4 X (d=4) |

n=11 top-10: 0.774889, 0.754686 (`J?`@f?kUDG_`, 17e), 0.753664, 0.752419, 0.747377 — all α=4, triangle-free, 17-19 edges;
then 0.735505 (`JCRbeo{ifI?`, 25e, α=3, = n10 winner + vertex, contains Quad-C5/Wagner/n9/n10 winners), 0.734338, 0.725688,
0.719179, 0.712900. REGIME CHANGE at n=11: the sparse triangle-free α=4 family overtakes the dense Wagner-based α=3 family.
Ratio maximizer among survivors is the α=3 graph (1.2452) — gap and ratio maximizers differ again.
Calibration: exhaustive over the 90,842 connected triangle-free 11-vertex graphs (CPU, 39 s) gives the same top-6 → the
triangle-free class contains the global maximizer at n=11. Plan (Dan agreed 2026-09-24): exhaustive within the triangle-free
class for n=12 (thr 0.70), 13 (thr 0.74), maybe 14 (468M tf graphs, ~1.5 h); plus max-degree-4 class at n=12; plus local search
for general n=12-16. Full brute force n=12 (1.64e11 graphs ≈ 3 weeks GPU) kept in reserve only.

n=10 own run: 11,716,571 graphs, all 975,330 Danielsen "quantum" graphs recovered by g6 string, max |ϑ − ϑ_table| = 5.3e-5 (table is 4 dp);
2,385 AlmostSolved statuses (harmless). Ratio maximizer `IUZurzmmo` (α=2, ϑ=2.5).

n=9 winner `HCRbdO{`: degrees 3^6 4^3, |Aut| = 12, vertex orbits {2,5,8} ∪ {0,1,3,4,6,7}, 12 induced C5, 1 triangle,
diameter 2, non-planar, ϑ = 11/3 to 12 digits (Clarabel 1e-12), optimal X has rank 4 → realization in d = 4.
Spectrum: 2+√2, 1, 1, √2−1 (×2), 2−√2, −2, −(1+√2) (×2). Does NOT contain Quad-C5 or Wagner as induced subgraph.
n=9 runner-up `HCrb`qi`: ϑ = 2+φ = 3.618034 exactly, = Wagner + one vertex.
Then a plateau of many graphs at exactly Quad-C5's 0.467844 (Quad-C5 plus a vertex that doesn't change ϑ or α).
n=9 ratio maximizer = same graph as gap maximizer (1.2222).

n=10 (from Danielsen table, to be confirmed by our run): winner `ICRb`yiu?` ϑ = 3.707107 = 3 + 1/√2, 4-regular, 20 edges,
|Aut| = 16, orbits {2,9} ∪ 8 others, 16 induced C5, 4 triangles, spectrum max = 4; contains Wagner (delete 2 vertices).
Runner-up `ICQeR`[Mg` ϑ = 3.667155 (strictly above 11/3), contains both Quad-C5 and the n=9 winner.
n=10 ratio maximizer differs: `IUZurzmmo` α=2, ϑ=2.5, ratio 1.25.

Observation: the maximizers are NOT a nested family — n=8 (10 edges, sparse), n=9 (15 edges, 3-fold symmetry),
n=10 (4-regular, Wagner-based). The "add a vertex to the previous winner" lineage only reaches 2nd place.

## GPU screening (`gpu_screen.py`, `run_n11.py`) — 2026-09-24
Dual SDP: ϑ(G) = min λ_max(J+Y), Y supported on E → any Y gives a rigorous upper bound. Per-graph Adam on the
smoothed max eigenvalue (τ-softmax over batched fp32 `eigh`, τ 0.3→0.02, 100 iters), progressive pruning every
10 iters on fp32 λ_max + 1e-3 margin, final fp64 certificate for survivors; α exact on GPU (all 2^n subsets).
Survive iff ub − α ≥ thr. Validation:
- n=8, no pruning, 100 iters: ub − ϑ median 0.006, max 0.21, zero violations (ub < ϑ) over 11,117 graphs.
- n=9, thr 0.60: 261,080 graphs in 3 s (90k g/s) → survivors = exactly the 2 true winners.
- n=10, thr 0.65: 11.7M graphs in 106 s (110k g/s) → 30 survivors = exactly the 30 table graphs with Δ ≥ 0.65.
- geng n=11: ~300k g/s per process (not the bottleneck). Launched n=11 (1.0e9 graphs, 50 parts, thr 0.707106)
  2026-09-24 ~10:15, expected ≈ 3 h; logs/n11.out, results/screen11/part_*.csv, final results/n11_survivors_exact.csv.

## Triangle-free class, n=12 and n=13 (2026-09-24, `run_geng.py --geng "-c -t"`)
- n=12 tf (1,144,061 connected tf graphs, seconds): max Δ = **0.930021** (ϑ 4.930021, α 4, 20 edges, `K?`DA`gd?{Dg`),
  |Aut| 8, degrees 3^8 4^4, 20 induced C5 + 4 C7, rank-5 X. Top-10 all α=4, 20–24 edges.
- n=13 tf (~19.3M connected tf graphs, 33 min — GPU α computation was memory-bound at 2^13 subsets; fixed by chunking,
  now ~14k g/s at n=13 and ~24k g/s at n=14 with 0.6 GB peak): max Δ = **1.181737** (ϑ 5.181737, α 4, 26 edges),
  a SINGLE graph far above the rest (next: 0.854 with α=5). It is the **Ramsey graph C13(1,5)** (unique R(3,5)-critical
  graph on 13 vertices, 4-regular, |Aut| 52); ϑ = 13·(−λmin)/(λmax−λmin) = 5.181736625 (edge-transitive Lovász formula).

## THE KEY INSIGHT — gap maximizers are Ramsey-critical graphs
Triangle-free graphs on n vertices with α ≤ k−1 are exactly the R(3,k)-graphs; they exist only for n < R(3,k).
Counts (connected tf with α ≤ 4): n=11: 105 (= |r35_11|), n=12: 12 (= |r35_12|), n=13: 1 (C13(1,5)). Our winners:
n=8 Quad-C5 ∈ R(3,4)-graphs on 8 vertices (3 graphs, incl. Wagner); n=11 global winner ∈ r35_11; n=12 tf winner ∈ r35_12;
n=13 tf winner = r35_13. At n=9,10 (R(3,4)=9 kills tf α=3) the winners keep α=3 by admitting 1 and 4 triangles.
So Δ_max(n) is driven by R(3,k): α is pinned at k−1 while ϑ grows with n. Lower bounds from McKay's Ramsey collection
(α = k−1 analytic; ϑ by SDP, `ramsey_theta.py`):
| family | n | #graphs | α | max ϑ | max Δ | graph |
|---|---|---|---|---|---|---|
| R(3,5) | 13 | 1 | 4 | 5.181737 | 1.181737 | C13(1,5) |
| R(3,6) | 14 | 263,520 | 5 | 6.181737 | 1.181737 | = C13(1,5) + isolated vertex (McKay's lists include disconnected graphs); best connected ≈ 1.0724 (`MqGOOH@_gQ?oGFCJ?`, 24 e) |
| R(3,6) | 15 | 64,732 | 5 | 6.250964 | 1.250964 | `NoCOWGACGQIKGePIDI?` (28 e) |
| R(3,6) | 16 | 2,576 | 5 | 6.465350 | 1.465350 | `OoC?Igi_?E_eKcRCE@iO[` (35 e) |
| R(3,6) | 17 | 7 | 5 | 6.606664 | 1.606664 | `P@oGQA?`ACcdCtDYC]Ah?goC` (40 e) |
| R(3,7) | 21 | 1,118,436 | 6 | 8.141315 | 2.141315 | `THoGG?JODHsOADs_wg?`GgSCZ??ig@@D@?GT` (56 e), 74 min CPU |
| R(3,7) | 22 | 191 | 6 | 8.398747 | 2.398747 | `UsaC?GGC?DccQDCpKEJAOKW`Bo?kD_[_okHCUR??` (66 e) |
| R(3,8) | 27 | 477,142 | 7 | 10.060569 | 3.060569 | `Z@O\MagCADc`e@O__`KoHO_CCHN?_G@DO?d??oCwQi??GTSPK?Dc?@YdI?c?` (91 e), 88 min CPU |
| R(3,9) | 35 | 1 | 8 | 12.410586 | 4.410586 | the unique R(3,9)-critical graph |
All Ramsey families done 2026-09-24 evening; full summary in PAPER_SUMMARY.md.
Consequence: within the tf class Δ_max is NOT monotone in n (n=14 forces α ≥ 5 → max ≈ 0.85–0.9 < 1.18), while the
global Δ_max(n) is monotone via "+ universal vertex" (θ, α unchanged). Exhaustive tf n=14 (~5 h) therefore low priority.

## Certificates (2026-09-24 evening, `certify.py` → `certificates/`)
Primal X (trace 1, zeros on edges, PSD) and dual Y (on edges) recomputed in float64 bracket ϑ within < 1e-9 for all
record graphs; SCS agrees. rank(X) of the interior-point (max-rank) solution: 4 for Quad-C5, Wagner, n=9, n=10, n=11
(both top graphs); 5 for tf12 max, C13(1,5), R(3,6) n=16; 6 for R(3,6) n=17 and R(3,7) n=22. Orthogonal representation
from X = BᵀB (u_i = b_i/|b_i|, ψ ∝ Σ b_i) attains ϑ to 1e-10 with edge overlaps < 1e-10. Visibility v* = (α − n/r)/(ϑ − n/r):
Quad-C5 0.681, Wagner 0.707, n9 0.529, n10 0.414, n11 0.617, n11 rank-2 0.624, tf12 0.632, C13 0.542, R36-16 0.551,
R36-17 0.574, R37-22 0.493. NOTE: smaller v* = MORE robust (least visibility needed). Ranking: n10 (0.414) most robust, then n9, C13, n11,
Quad-C5, Wagner (0.707) least. An earlier draft sentence claiming the sparse family is more robust was WRONG and was
corrected 2026-09-24 evening. Burer–Monteiro minimal-rank search was inconclusive (projection too crude) → paper reports r
as an upper bound on the realization dimension only. Paper draft now 13 pages: Discussion + Appendix C written.
Public repo: https://github.com/danmusetoiu/contextuality-gap

## tf n=14 exhaustive (2026-09-24 night, 6.1 h GPU, `results/tf14/`, `results/tf14_survivors_exact.csv`)
445,781,050 connected triangle-free graphs on 14 vertices, thr 1.0, 12,764 survivors (ALL α=5), max Δ = 1.072373
(ϑ 6.072373, 24 edges, `M?AA@agwAg@WM_Dc?`) = isomorphic to the best connected R(3,6)-catalogue graph on 14 vertices.
Confirms the Ramsey-predicted drop 1.18 → 1.07 exhaustively.

## n=12 local search with triangles (`localsearch12.py`, 90 min, 2026-09-24 evening)
1,425,556 distinct 12-vertex graphs evaluated (exact ϑ, α); best overall = tf record 0.930021; best WITH a triangle
0.866462 (1 triangle, 21 edges, α=4). Evidence for Conjecture at n=12. Results: `results/localsearch12.csv` (top 5000).

## Circulant Ramsey-critical scan (`circulant_scan.py`)
Exhaustive over connection sets: n=13: C13(1,5) only (edge-transitive: multipliers {±1,±5}, 5²≡−1 → Lovász–Hoffman formula
attained, closed form proven); n=16: one circulant R(3,6) (gap 1.1648 < family max 1.4654); n=17, 22, 27: NONE;
n=21: two non-isomorphic circulant R(3,7) (gaps 1.9768, 1.7560 < 2.1413); n=35: C35(1,7,11,16) = Kalbfleisch graph =
the unique R(3,9)-critical graph (isomorphism confirmed), vertex- but not edge-transitive: ϑ = 12.410586 (LP optimum)
< Hoffman ratio 12.4979. Exact closed form for ϑ(C35) still TODO (sympy symbolic solve hung; do LP active set + linear
solve in Q(ζ35)^+).

## Open items
- n=10 own run (`results/n10.csv`) → cross-check vs table, then n=11: ~1e9 graphs. Clarabel path ≈ 2.5–4k g/s ≈ 3–4 days
  → design a GPU batched screen (rigorous dual upper bound on ϑ, prune if bound − α < best) + Clarabel re-verification.
- Exact/rational certificates for 11/3 and 3+1/√2 (dual SDP solution, closed form).
- Minimal realization dimension d*, noise robustness (visibility v*) à la Quad-C5 paper §IV.
- Name/identify `HCRbdO{` (House of Graphs lookup).
