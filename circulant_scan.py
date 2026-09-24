"""
Scan all circulant graphs C_n(S) on Ramsey-critical vertex counts for triangle-free graphs with alpha <= k-1
(i.e. circulant R(3,k)-graphs), compute theta exactly, test edge-transitivity via the multiplier group, and compare
theta with the Lovasz edge-transitive formula  n * (-lambda_min) / (lambda_max - lambda_min).

Usage: python circulant_scan.py  [--n 13 17 22 35 ...]
Output: results/circulant_scan.csv
"""
import argparse, csv, itertools, math, os
import numpy as np
import networkx as nx
from networkx.algorithms.clique import max_weight_clique
from gap_search import theta_clarabel

CASES = {13: 5, 16: 6, 17: 6, 21: 7, 22: 7, 27: 8, 35: 9}   # n -> k with n < R(3,k)


def is_tf(n, S):
    Sf = set(S) | {(n - s) % n for s in S}
    return not any(((a + b) % n) in Sf for a in Sf for b in Sf)


def alpha_nx(G):
    return max_weight_clique(nx.complement(G), weight=None)[1]


def multiplier_group(n, S):
    Sf = frozenset(set(S) | {(n - s) % n for s in S})
    return [u for u in range(1, n) if math.gcd(u, n) == 1 and frozenset((u * s) % n for s in Sf) == Sf]


def edge_transitive_by_multipliers(n, S):
    """Sufficient condition: the multiplier group (units u with uS = S) acts transitively on S (up to sign)."""
    Sf = set(S) | {(n - s) % n for s in S}
    U = multiplier_group(n, S)
    orbit = {(u * next(iter(Sf))) % n for u in U}
    return orbit == Sf


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--n", type=int, nargs="*", default=sorted(CASES)); a = ap.parse_args()
    os.makedirs("results", exist_ok=True)
    rows = []
    for n in a.n:
        k = CASES[n]; half = n // 2; found = 0; seen = set(); seen_graphs = {}
        for r in range(1, half + 1):
            for S in itertools.combinations(range(1, half + 1), r):
                if not is_tf(n, S):
                    continue
                G = nx.circulant_graph(n, list(S))
                if not nx.is_connected(G):
                    continue
                al = alpha_nx(G)
                if al > k - 1:
                    continue
                # skip isomorphic duplicates (multiplier-equivalent sets): exact isomorphism test against those kept
                th, _ = theta_clarabel(n, list(G.edges()))
                key = None
                for kk, Gk in seen_graphs.items():
                    if nx.is_isomorphic(G, Gk):
                        key = kk; break
                if key is None:
                    key = f"{n}-{len(seen_graphs)}"; seen_graphs[key] = G
                ev = np.linalg.eigvalsh(nx.to_numpy_array(G)); lmax, lmin = ev.max(), ev.min()
                formula = n * (-lmin) / (lmax - lmin)
                et = edge_transitive_by_multipliers(n, S)
                dup = key in seen; seen.add(key)
                rows.append(dict(n=n, k=k, S=" ".join(map(str, S)), degree=len(set(S) | {n - s for s in S}), alpha=al,
                                 theta=f"{th:.10f}", gap=f"{th-al:.10f}", formula=f"{formula:.10f}",
                                 formula_matches=abs(formula - th) < 1e-7, edge_transitive_mult=et,
                                 mult_group_size=len(multiplier_group(n, S)), iso_dup=dup))
                found += 1
                print(f"n={n} k={k} S={S} deg={rows[-1]['degree']} alpha={al} theta={th:.6f} gap={th-al:.6f} "
                      f"formula={formula:.6f} match={abs(formula-th)<1e-7} edge-trans(mult)={et} dup={dup}", flush=True)
        print(f"n={n}: {found} circulant R(3,{k})-graphs (with duplicates)", flush=True)
    with open("results/circulant_scan.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)


if __name__ == "__main__":
    main()
