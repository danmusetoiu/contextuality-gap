# Referee pass — draft of 2026-09-24 (16 pp., commit after round 4)

Legend: **SOLID** = will hold; **ATTACK** = a skeptical referee will go here; **FIX** = objective error or inconsistency, must change; **CUT** = can go; **STEP** = the argument skips a step.

## Abstract
- SOLID: the sequence exhaustive → transition at 11 → Ramsey → ladder → asymptotics is all there.
- FIX: "Quad-C5 and the Wagner graph are R(3,4)-graphs" is listed under "record graphs at the Ramsey-critical scales" — Wagner is not a record graph (rank 3 at n=8). Say "Quad-C5 (and the former benchmark, the Wagner graph)".
- ATTACK: length ≈ 330 words; PRA/QIP/J. Phys. A want ≤ 250. Cut the Wagner clause, the "found by numerical optimization but valid…" clause (keep in intro), and one of the two Ramsey sentences.

## 1 Introduction
- SOLID: hook, the boxed conjecture, the four contributions.
- FIX: "For eight vertices the answer was found last year" — Tamer et al. is May 2026, i.e. this year. Write "recently".
- STEP: "verified over all graphs at n=8 (k=4)" — true only because Quad-C5 is triangle-free with α=3 on 8 = R(3,4)−1 vertices; say so in half a sentence, otherwise the reader has to check.
- ATTACK: contribution 1 claims "first exhaustive computation of a Lovász-number extremum at this scale". Keep "to our knowledge" and add that the Danielsen table stopped at 10 vertices — that is the evidence for the claim.

## 2 Preliminaries
- SOLID: (1), (2), Lemma 1 with proof (θ unchanged by a universal vertex; f(n−1) ≤ Δ_max(n) ≤ f(n)).
- FIX (Lemma 2): "a triangle-free graph on n < R(3,k) vertices can have α = k−1, and the graphs achieving it are exactly the R(3,k)-graphs" — R(3,k)-graphs have α ≤ k−1, not = k−1. Correct statement: for R(3,k−1) ≤ n < R(3,k), a triangle-free graph on n vertices has α ≥ k−1, and the ones with α = k−1 are exactly the R(3,k)-graphs on n vertices. (The lower bound needs n ≥ R(3,k−1); at n=13 an R(3,6)-graph can have α=4, as the C13(1,5) row of the r36_13 catalogue shows.)
- FIX: "Complete catalogues of R(3,k)-graphs for k ≤ 9 are available" — McKay's site is complete for all n only for k ≤ 7; for k=8,9 only the critical sizes (27, 35) are catalogued. Write "for k ≤ 7, and at the critical sizes for k = 8, 9".
- STEP: "θ and α are additive over disjoint unions [knuth1994]" is used in three places; give the one-line reason for θ (block-diagonal X) or the exact theorem number in Knuth.

## 3 Exhaustive results
- SOLID: Table 1, the n=9/10 exact values, the Danielsen cross-check (honest and disarming), Table 2, Figure 2.
- FIX: Table 1 caption defines d* but the table has no d* column. Either add a column "r" (rank of X) or drop the sentence.
- FIX: the symbol d* is used in the n=11 paragraph and in §3.2 as if it were the minimal dimension, while §6 says rank is only an upper bound. Use r (rank of the optimal X) everywhere and reserve d* for the (unknown) minimum. This is exactly the kind of inconsistency a referee quotes back.
- FIX: "the dense graph of rank 6 in Table 2" — "rank" here means table row; write "row 6" (matrix rank is used elsewhere).
- FIX (§3.2): "about 1.9×10^7 for n=13" → exact: 19,425,052 connected triangle-free graphs screened.
- STEP/FIX (§3.2): "the next best triangle-free graph has Δ = 0.854 and α = 5" is NOT established by the run as performed: parts 0–4 were screened at threshold 0.74, parts 5–19 at 0.95, so a graph with gap in [0.854, 0.95) and α ≥ 6 in parts 5–19 could have been missed. What IS established: (a) no other triangle-free graph on 13 vertices reaches 0.95 (exhaustive), (b) among all triangle-free graphs with α ≤ 5 (= the R(3,6) catalogue on 13 vertices, 275,086 graphs, all solved exactly) the best connected α=5 graph is L?`?`CWHKAGPN? with Δ = 0.854480. Either (i) reword to exactly this, or (ii) rerun the screen at 0.80 (queued, ~40 min after the n=14 run) and then keep the sentence.
- ATTACK: uniqueness. Say explicitly that the maximizers at n = 9, 10, 11 are unique up to isomorphism (the runner-up values differ: 0.618, 0.667, 0.755) — otherwise "the maximizer" is undefined.
- ATTACK: n=6 row (EUZO) and n=5,7 rows — say in the caption that n ≤ 8 were recomputed by us (they were), so the table is one run, not a mixture.
- CUT: the "Gap versus ratio" paragraph can shrink to one sentence with a pointer to Table 2/Appendix; it interrupts the n=11 story.

## 4 Ramsey structure
- SOLID: 4.1 primer, the isomorphism identifications, the two regime changes sitting on R(3,4)=9 and R(3,5)=14, Prop. 2 (circulants) with the multiplier argument, Prop. 3 and its proof, Corollary 1.
- FIX (4.1): "θ grows with n (roughly like √n for sparse graphs)" contradicts §4.4, which proves Δ_max = Θ(n) (θ of the record family grows linearly: it is bounded below by 0.126 n + α). Write "θ grows with n" and leave the rate out, or "at least linearly along the record family (Prop. 3)".
- FIX (4.2, closing paragraph): "it identifies every computed maximizer with a Ramsey graph" — false for n = 9, 10. Write "every computed triangle-free maximizer, and the global maximizers at n = 8 and 11".
- FIX (Conjecture 1, second clause): "from n = 11 on the maximizer is triangle-free with the least independence number that Ramsey theory allows" is contradicted two sentences later ("at n = 14 … the global maximum is attained only by the degenerate extension of C13(1,5)"), and by Lemma 1 itself: at n = 14 the maximizer has a universal vertex, hence triangles. This is the sentence a referee will kill the paper with. Fix by defining a *new* maximizer (one not obtainable from a smaller record by adding universal vertices) and conjecturing: (a) at n = R(3,k)−1 the maximizer is R(3,k)-critical; (b) for n ≥ 11 every new maximizer is triangle-free. Then n = 14 is consistent (no new maximizer).
- STEP (Prop. 2(ii)): uniqueness of the (3,9,35) graph needs a citation (the catalogue [mckay-ramsey] / [goedgebeur2013]); Kalbfleisch's thesis gives existence, not uniqueness. Same for the uniqueness of C13(1,5) as the (3,5,13) graph.
- STEP (Prop. 2(iii)): the scan considered connected circulants only; say so (a disconnected circulant cannot be critical at these sizes, one line).
- ATTACK (4.4 heuristics paragraph): "θ = Θ(n/√d)" for G(n, d/n) with d fixed — Coja-Oghlan's theorem is for p ≥ C/n with constants; quoting a numerical "c* ≳ 0.12 from a second family" from an asymptotic Θ(·) is heuristic and is labelled so, but a referee may ask to remove the number. Keep the qualitative statement, drop "≈ 0.12" or say "of the same order as the Ramsey bound".
- CUT: the sentence "the data of Table 3 suggest Δ_max(R(3,k)−1) ≈ 0.12 (R(3,k)−1)" at the end of 4.2 duplicates 4.4; keep one.

## 5 Methods
- SOLID: the certificate/search separation; the error-bound argument; validation with zero misses.
- STEP (5.2 certificate): the claim "computed λ_max differs by at most c·n·u·‖J+Y‖₂ ≲ 10⁻⁵" — give the actual numbers once: u = 2⁻²⁴ ≈ 6×10⁻⁸, ‖J+Y‖₂ ≤ 11·(1+max|Y|) ≤ 33 with |Y| ≤ 2 in practice, so the bound is ≈ 2×10⁻⁵·c; the margin 10⁻³ is 50× that. Also name the eigensolver (cuSOLVER batched Jacobi, backward stable).
- ATTACK: "α computed exactly by bit operations on the GPU" — state that survivors' α was recomputed on the CPU independently (it was, in the exact stage). One sentence.
- ATTACK: reproducibility — say the total wall time of the whole pipeline and that the res/mod split makes the run resumable and auditable per part (the 50 part files are in the repository).

## 6 Discussion
- SOLID: certificates paragraph; the corrected visibility discussion (smaller v* = more robust; the ten-vertex graph is the most robust witness in the tables; larger gap ≠ more robust).
- STEP: v* uses d = rank of X; since rank is only an upper bound on the minimal dimension, v* as given is an *upper bound on the true critical visibility* (a lower-dimensional realization, if it exists, would have a larger noise term n/d, hence a *worse* v*… careful: n/d grows as d shrinks, so v* = (α − n/d)/(θ − n/d) increases as d decreases). State the direction explicitly: the quoted v* are for the realization we exhibit; a lower-dimensional one would be less robust, not more.
- ATTACK: "closed forms for the eleven-vertex maximizer … remain to be identified" — fine, but say what was tried (minimal polynomial search up to degree N failed / not attempted).
- CUT: the local-search paragraph can lose the parenthetical move list; keep the numbers.

## 7 Conclusion
- FIX: "the record graphs are Ramsey R(3,k)-graphs" — same overclaim as before (n = 9, 10). 
- FIX: "which Proposition 1 confines to [c, 1/2]" → Proposition 3 and 0.126.
- FIX: "realizations in dimension four" → "realizations in dimension four (from the rank of the SDP optimum; minimality not claimed)".

## Appendices / references
- Table 5: fine; add the column "α*" (fractional packing) for the record graphs? optional, supports the "none is fully contextual" remark.
- FIX: [alon] must be verified (title/venue/year).
- Add: a reference for uniqueness of the (3,5,13) and (3,9,35) graphs (Radziszowski survey DS1 covers both).
- Figure 2 caption: "the dense family (α=3, containing the Wagner graph)" — not all dense survivors contain Wagner; write "based on the n=10 maximizer".

## Priority order
1. Conjecture 1 second clause (contradiction) — FIX now.
2. "every record graph / every maximizer is a Ramsey graph" in abstract, 4.2, conclusion — FIX now.
3. tf13 runner-up statement — reword now, rerun queued.
4. Lemma 2 statement; catalogue completeness; d* vs rank; Table 1 caption; "last year"; conclusion refs — FIX now.
5. Abstract length; heuristics number; cuts — editorial, before submission.
