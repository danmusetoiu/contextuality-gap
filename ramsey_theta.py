"""
Lovász theta (and CSW gap) for Ramsey-critical graphs R(3,k) from McKay's collection.

For an R(3,k)-graph on n vertices (triangle-free, alpha <= k-1) with n >= R(3,k-1), alpha = k-1 exactly.
So alpha is analytic; only theta needs the SDP.

Usage: python ramsey_theta.py data/r36_17.g6 7 results/r36_17.csv [--workers 20]
       (second arg = k, so alpha = k-1)
"""
import sys, os, time, csv, argparse
from multiprocessing import Pool
from gap_search import g6_to_adj, theta_clarabel


def work(line):
    n, E = g6_to_adj(line)
    th, st = theta_clarabel(n, E)
    return line.strip(), n, len(E), th, st


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("g6file"); ap.add_argument("k", type=int); ap.add_argument("outcsv")
    ap.add_argument("--workers", type=int, default=max(1, os.cpu_count() - 4))
    a = ap.parse_args()
    alpha = a.k - 1
    lines = [l for l in open(a.g6file) if l.strip()]
    os.makedirs(os.path.dirname(os.path.abspath(a.outcsv)), exist_ok=True)
    t0 = time.time(); recs = []
    with Pool(a.workers) as pool:
        for i, r in enumerate(pool.imap_unordered(work, lines, chunksize=50), 1):
            recs.append(r)
            if i % 20000 == 0:
                print(f"{i}/{len(lines)} {time.time()-t0:.0f}s", flush=True)
    recs.sort(key=lambda r: -r[3])
    with open(a.outcsv, "w", newline="") as f:
        w = csv.writer(f); w.writerow(["g6", "n", "edges", "alpha", "theta", "gap", "ratio", "status"])
        for g6, n, m, th, st in recs:
            w.writerow([g6, n, m, alpha, f"{th:.10f}", f"{th-alpha:.10f}", f"{th/alpha:.10f}", st])
    print(f"{a.g6file}: {len(recs)} graphs, n={recs[0][1]}, alpha={alpha}, {time.time()-t0:.0f}s")
    print("  max theta / gap:", ", ".join(f"{r[0]} |E|={r[2]} theta={r[3]:.6f} gap={r[3]-alpha:.6f}" for r in recs[:5]))
    print("  min theta:", f"{recs[-1][3]:.6f}")


if __name__ == "__main__":
    main()
