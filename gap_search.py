"""
Exhaustive CSW contextuality-gap search over connected graphs on n vertices.

For each graph G (exclusivity graph):
  alpha(G)  = independence number  (classical / noncontextual bound)   -- exact, bitmask brute force
  theta(G)  = Lovasz theta number  (quantum bound)                     -- SDP via Clarabel (direct API)
  gap       = theta - alpha
  ratio     = theta / alpha

Input : graph6 file (one graph per line), e.g. McKay's graph9c.g6
Output: CSV with g6, n_edges, alpha, theta, gap, ratio, solver status

Usage:
  python gap_search.py data/graph8c.g6 results/n8.csv [--workers 20] [--limit N]
"""
import sys, os, time, argparse, csv
import numpy as np
import scipy.sparse as sp
import clarabel
from multiprocessing import Pool


# ---------- graph6 ----------
def g6_to_adj(line: str):
    """Decode a graph6 string into (n, list of edges)."""
    s = line.strip()
    if s.startswith(">>graph6<<"):
        s = s[10:]
    data = [ord(c) - 63 for c in s]
    n = data[0]
    bits = []
    for d in data[1:]:
        bits.extend([(d >> k) & 1 for k in range(5, -1, -1)])
    edges = []
    k = 0
    for j in range(1, n):
        for i in range(j):
            if bits[k]:
                edges.append((i, j))
            k += 1
    return n, edges


# ---------- alpha ----------
_SUBSETS = {}

def alpha_exact(n, edges):
    """Independence number by brute force over 2^n subsets (fine for n <= 12)."""
    if n not in _SUBSETS:
        _SUBSETS[n] = np.arange(1 << n, dtype=np.int64)
    S = _SUBSETS[n]
    ok = np.ones(S.shape, dtype=bool)
    for (u, v) in edges:
        ok &= ~(((S >> u) & 1) & ((S >> v) & 1)).astype(bool)
    # popcount of surviving subsets
    pc = np.zeros(S.shape, dtype=np.int64)
    for b in range(n):
        pc += (S >> b) & 1
    return int(pc[ok].max())


# ---------- theta via Clarabel (direct) ----------
# Primal:  theta = max <J, X>  s.t.  tr X = 1,  X_ij = 0 (ij in E),  X PSD
# Clarabel:  min c'x  s.t.  A x + s = b,  s in K
#   x = svec(X) in Clarabel's PSD-triangle convention (upper-tri, column-major,
#   off-diagonals scaled by sqrt(2)).  We use x directly as the cone slack:
#   constraint block 1 (Zero cone): tr X = 1 and X_ij = 0 for edges
#   constraint block 2 (PSD cone):  -x + s = 0  ->  s = x in PSD triangle
def _svec_index(n):
    """Map (i,j), i<=j, to index in Clarabel's upper-triangular column-major svec."""
    idx = {}
    k = 0
    for j in range(n):
        for i in range(j + 1):
            idx[(i, j)] = k
            k += 1
    return idx

_IDX = {}

def theta_clarabel(n, edges, tol=1e-9):
    if n not in _IDX:
        _IDX[n] = _svec_index(n)
    idx = _IDX[n]
    edges = [(min(i, j), max(i, j)) for (i, j) in edges]   # accept edges in any orientation
    m = n * (n + 1) // 2
    r2 = np.sqrt(2.0)

    # objective: maximize sum_ij X_ij = sum_i X_ii + 2 * sum_{i<j} X_ij
    # in svec coords, off-diag entry x_k = sqrt2 * X_ij  ->  2 X_ij = sqrt2 * x_k
    c = np.zeros(m)
    for (i, j), k in idx.items():
        c[k] = -1.0 if i == j else -r2       # minus: Clarabel minimizes

    rows, cols, vals = [], [], []
    b = []
    row = 0
    # trace = 1
    for i in range(n):
        rows.append(row); cols.append(idx[(i, i)]); vals.append(1.0)
    b.append(1.0); row += 1
    # X_ij = 0 for edges
    for (i, j) in edges:
        rows.append(row); cols.append(idx[(i, j)]); vals.append(1.0)
        b.append(0.0); row += 1
    n_zero = row
    # PSD block: -x + s = 0
    for k in range(m):
        rows.append(row + k); cols.append(k); vals.append(-1.0)
        b.append(0.0)
    row += m

    A = sp.csc_matrix((vals, (rows, cols)), shape=(row, m))
    P = sp.csc_matrix((m, m))
    cones = [clarabel.ZeroConeT(n_zero), clarabel.PSDTriangleConeT(n)]
    settings = clarabel.DefaultSettings()
    settings.verbose = False
    settings.tol_gap_abs = tol
    settings.tol_gap_rel = tol
    settings.tol_feas = tol
    solver = clarabel.DefaultSolver(P, c, A, np.array(b), cones, settings)
    sol = solver.solve()
    status = str(sol.status)
    theta = -sol.obj_val
    return theta, status


# ---------- worker ----------
def process(line):
    n, edges = g6_to_adj(line)
    a = alpha_exact(n, edges)
    th, st = theta_clarabel(n, edges)
    return (line.strip(), len(edges), a, th, th - a, th / a, st)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("g6file")
    ap.add_argument("outcsv")
    ap.add_argument("--workers", type=int, default=max(1, os.cpu_count() - 4))
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--chunk", type=int, default=200)
    args = ap.parse_args()

    with open(args.g6file) as f:
        lines = [l for l in f if l.strip()]
    if args.limit:
        lines = lines[: args.limit]
    N = len(lines)
    os.makedirs(os.path.dirname(os.path.abspath(args.outcsv)), exist_ok=True)
    print(f"{N} graphs, {args.workers} workers", flush=True)

    t0 = time.time()
    done = 0
    with open(args.outcsv, "w", newline="") as out:
        w = csv.writer(out)
        w.writerow(["g6", "edges", "alpha", "theta", "gap", "ratio", "status"])
        with Pool(args.workers) as pool:
            for rec in pool.imap(process, lines, chunksize=args.chunk):
                w.writerow([rec[0], rec[1], rec[2], f"{rec[3]:.10f}", f"{rec[4]:.10f}", f"{rec[5]:.10f}", rec[6]])
                done += 1
                if done % 5000 == 0 or done == N:
                    el = time.time() - t0
                    print(f"{done}/{N}  {el:.0f}s  ({done/el:.1f} g/s)  ETA {(N-done)/(done/el):.0f}s", flush=True)
    print("done", time.time() - t0, flush=True)


if __name__ == "__main__":
    main()
