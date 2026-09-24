"""
Certificates and physics quantities for the record graphs.

For each graph:
  theta      : primal SDP (Clarabel, tol 1e-12) and dual SDP (min t s.t. tI - (J+Y) >= 0, Y on edges)
  dual cert  : Y saved; lambda_max(J+Y) recomputed in float64 numpy  -> rigorous upper bound on theta
  primal cert: X saved; <J,X> with tr X = 1, X_ij = 0 on edges, X >= 0 -> rigorous lower bound on theta
  ONR        : from X = B^T B: psi = sum_i b_i / ||.||, u_i = b_i/||b_i|| ; sum_i <psi,u_i>^2 = theta,
               <u_i,u_j> = 0 on edges (CSW orthogonal representation of the exclusivity graph)
  d*         : minimal dimension attaining theta, searched by Burer-Monteiro (rank r = 2..rank X) with restarts
  visibility : v* = (alpha - n/d*) / (theta - n/d*)   (white-noise mixing, projectors of rank 1 in dimension d*)
  SCS check  : theta re-solved with SCS
Outputs: certificates/<name>.json and certificates/summary.csv
"""
import os, json, csv
import numpy as np
import cvxpy as cp
import networkx as nx
from gap_search import g6_to_adj, alpha_exact

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "certificates"); os.makedirs(OUT, exist_ok=True)

RECORDS = {
    "n8_QuadC5":   "GCQb`o",
    "n8_Wagner":   "GCrb`o",
    "n9_max":      "HCRbdO{",
    "n10_max":     "ICRb`yiu?",
    "n11_max":     "J?`D@pgd?{?",
    "n11_rank2":   "J?`@f?kUDG_",
    "n12_tf_max":  "K?`DA`gd?{Dg",
    "n13_C13_1_5": "L?`DE`gl@YJODg",
    "R36_n16_max": "OoC?Igi_?E_eKcRCE@iO[",
    "R36_n17_max": "P@oGQA?`ACcdCtDYC]Ah?goC",
    "R37_n22_max": "UsaC?GGC?DccQDCpKEJAOKW`Bo?kD_[_okHCUR??",
}


def solve_primal(n, E, tol=1e-12):
    X = cp.Variable((n, n), PSD=True)
    cons = [cp.trace(X) == 1] + [X[i, j] == 0 for i, j in E]
    p = cp.Problem(cp.Maximize(cp.sum(X)), cons)
    p.solve(solver=cp.CLARABEL, tol_gap_abs=tol, tol_gap_rel=tol, tol_feas=tol)
    return p.value, X.value


def solve_dual(n, E, tol=1e-12):
    t = cp.Variable(); Y = cp.Variable((n, n), symmetric=True)
    mask = np.zeros((n, n));
    for i, j in E: mask[i, j] = mask[j, i] = 1
    cons = [cp.multiply(1 - mask, Y) == 0, t * np.eye(n) - (np.ones((n, n)) + Y) >> 0]
    p = cp.Problem(cp.Minimize(t), cons)
    p.solve(solver=cp.CLARABEL, tol_gap_abs=tol, tol_gap_rel=tol, tol_feas=tol)
    return p.value, Y.value


def solve_scs(n, E):
    X = cp.Variable((n, n), PSD=True)
    p = cp.Problem(cp.Maximize(cp.sum(X)), [cp.trace(X) == 1] + [X[i, j] == 0 for i, j in E])
    p.solve(solver=cp.SCS, eps=1e-10, max_iters=500000)
    return p.value


def onr_from_X(X, E, tol=1e-9):
    w, V = np.linalg.eigh(X)
    keep = w > tol * w.max()
    B = (V[:, keep] * np.sqrt(w[keep])).T            # r x n, X = B^T B
    s = B.sum(axis=1); psi = s / np.linalg.norm(s)
    norms = np.linalg.norm(B, axis=0)
    U = B / norms                                    # unit vectors u_i (columns)
    val = float(np.sum((psi @ U) ** 2))
    orth = max(abs(float(U[:, i] @ U[:, j])) for i, j in E)
    return B.shape[0], psi, U, val, orth


def min_rank_bm(n, E, theta, rmax, trials=40, iters=3000, seed=0):
    """Burer-Monteiro: maximize ||sum_i b_i||^2 s.t. sum ||b_i||^2 = 1, b_i.b_j = 0 on edges (penalty), b_i in R^r.
    Returns smallest r for which theta is attained within 1e-6 (after projecting to feasibility)."""
    import torch
    rng = np.random.default_rng(seed)
    mask = torch.zeros(n, n)
    for i, j in E: mask[i, j] = mask[j, i] = 1
    best = {}
    for r in range(1, rmax + 1):
        bestval = -1
        for t in range(trials):
            B = torch.tensor(rng.standard_normal((r, n)), dtype=torch.float64, requires_grad=True)
            opt = torch.optim.Adam([B], lr=0.05)
            for it in range(iters):
                mu = 10.0 + it * 0.05
                Bn = B / torch.sqrt((B * B).sum())
                G = Bn.T @ Bn
                obj = -G.sum() + mu * ((G * mask) ** 2).sum()
                opt.zero_grad(); obj.backward(); opt.step()
            with torch.no_grad():
                Bn = (B / torch.sqrt((B * B).sum())).numpy()
            # project to exact feasibility: zero out edge inner products is nontrivial; instead evaluate the exact
            # primal value of the feasible matrix X = G with edge entries zeroed (may lose PSD) -> use eigen-clipping
            G = Bn.T @ Bn; G[mask.numpy() == 1] = 0
            w, V = np.linalg.eigh(G); w = np.clip(w, 0, None); G2 = (V * w) @ V.T; G2 /= np.trace(G2)
            # G2 is PSD, trace 1, but edge entries may be slightly nonzero again -> report residual
            val = float(G2.sum()); res = float(np.abs(G2[mask.numpy() == 1]).max())
            if res < 1e-7 and val > bestval: bestval = val
        best[r] = bestval
        if bestval >= theta - 1e-6:
            return r, best
    return None, best


BM_GRAPHS = ["n8_QuadC5", "n9_max", "n10_max", "n11_max", "n12_tf_max", "n13_C13_1_5"]   # minimal-dimension search only here


def main():
    import torch; torch.set_num_threads(4)
    rows = []
    for name, g6 in RECORDS.items():
        n, E = g6_to_adj(g6)
        al = alpha_exact(n, E)
        thP, X = solve_primal(n, E)
        thD, Y = solve_dual(n, E)
        thS = solve_scs(n, E)
        # rigorous checks in float64
        Yc = 0.5 * (Y + Y.T); mask = np.zeros((n, n))
        for i, j in E: mask[i, j] = mask[j, i] = 1
        Yc = Yc * mask                                             # enforce support exactly
        ub = float(np.linalg.eigvalsh(np.ones((n, n)) + Yc)[-1])   # certified upper bound
        Xc = 0.5 * (X + X.T); Xc[mask == 1] = 0                     # enforce zeros exactly
        w, V = np.linalg.eigh(Xc); w = np.clip(w, 0, None); Xc = (V * w) @ V.T; Xc /= np.trace(Xc)
        edge_res = float(np.abs(Xc[mask == 1]).max())
        lb = float(Xc.sum())                                        # certified lower bound if edge_res ~ 0
        rank, psi, U, onr_val, orth = onr_from_X(X, E)
        print(f"{name}: theta {thP:.10f} certified [{lb:.10f}, {ub:.10f}] rank(X)={rank}; BM search up to r={rank} ...", flush=True)
        dstar, bm = (min_rank_bm(n, E, thP, rmax=rank, trials=6, iters=800) if name in BM_GRAPHS else (None, {}))
        d_use = dstar if dstar else rank
        vis = (al - n / d_use) / (thP - n / d_use) if thP > n / d_use else None
        rec = dict(name=name, g6=g6, n=n, edges=len(E), alpha=al, theta_primal=thP, theta_dual=thD, theta_scs=thS,
                   certified_ub=ub, certified_lb=lb, lb_edge_residual=edge_res, rank_X=rank, onr_value=onr_val,
                   onr_max_edge_overlap=orth, d_star_bm=dstar, bm_best_by_rank=bm, visibility=vis,
                   gap=thP - al, Y=Yc.tolist(), X=Xc.tolist(), psi=psi.tolist(), U=U.tolist())
        with open(os.path.join(OUT, f"{name}.json"), "w") as f:
            json.dump(rec, f, indent=1)
        rows.append({k: rec[k] for k in ["name", "g6", "n", "edges", "alpha", "theta_primal", "theta_dual", "theta_scs",
                                          "certified_ub", "certified_lb", "lb_edge_residual", "rank_X", "d_star_bm",
                                          "onr_value", "onr_max_edge_overlap", "visibility", "gap"]})
        print(f"{name:14s} n={n:2d} alpha={al} theta={thP:.10f} dual={thD:.10f} scs={thS:.8f} ub={ub:.10f} lb={lb:.10f} "
              f"rankX={rank} d*={dstar} onr={onr_val:.10f} orth={orth:.1e} v*={vis}", flush=True)
    with open(os.path.join(OUT, "summary.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)


if __name__ == "__main__":
    main()
