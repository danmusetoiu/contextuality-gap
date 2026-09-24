"""
Exhaustive n=11 contextuality-gap search: geng (nauty) -> GPU screen -> Clarabel exact on survivors.

Resumable: the run is split into MOD parts (geng res/mod); each finished part leaves
results/screen11/part_<res>.csv and part_<res>.done.  Re-running skips finished parts.
At the end, all survivors are re-solved exactly with Clarabel -> results/n11_survivors_exact.csv

Usage:  python run_n11.py [--mod 50] [--thr 0.707106] [--batch 32768] [--iters 100]
"""
import os, sys, time, subprocess, argparse, csv, glob
import numpy as np
import torch

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gpu_screen as gs
from gap_search import g6_to_adj, theta_clarabel, alpha_exact

N = 11
GENG = os.path.join(HERE, "geng.exe")


def screen_part(res, mod, thr, batch, iters, outdir):
    out_csv = os.path.join(outdir, f"part_{res}.csv")
    done = os.path.join(outdir, f"part_{res}.done")
    if os.path.exists(done):
        return None
    cmd = [GENG, "-c", "-q", str(N), f"{res}/{mod}"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, bufsize=1 << 20)
    t0 = time.time(); total = 0; surv = 0
    with open(out_csv, "w", newline="") as out:
        w = csv.writer(out); w.writerow(["g6", "alpha", "theta_ub"])
        for chunk in gs.read_g6_lines(p.stdout, N, batch):
            A = torch.from_numpy(gs.g6_chunk_to_edges(chunk, N)).to(gs.DEV)
            al = gs.alpha_gpu(A)
            ub, keep = gs.theta_ub_gpu(A, alpha=al, thr=thr, iters=iters)
            idx = torch.nonzero(keep).flatten().cpu().numpy()
            for i in idx:
                w.writerow([chunk[i].tobytes().decode(), int(al[i]), f"{float(ub[i]):.8f}"])
            total += len(chunk); surv += len(idx)
    rc = p.wait()
    if rc != 0:
        raise RuntimeError(f"geng exited with {rc} on part {res}/{mod}")
    el = time.time() - t0
    with open(done, "w") as f:
        f.write(f"{total} {surv} {el:.1f}\n")
    return total, surv, el


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mod", type=int, default=50)
    ap.add_argument("--thr", type=float, default=0.707106)   # n=10 record 1/sqrt2 minus 1e-6
    ap.add_argument("--batch", type=int, default=32768)
    ap.add_argument("--iters", type=int, default=100)
    a = ap.parse_args()
    outdir = os.path.join(HERE, "results", "screen11")
    os.makedirs(outdir, exist_ok=True)
    print(f"device {gs.DEV}  mod={a.mod} thr={a.thr}", flush=True)
    T0 = time.time(); grand = 0; gsurv = 0
    for res in range(a.mod):
        r = screen_part(res, a.mod, a.thr, a.batch, a.iters, outdir)
        if r is None:
            print(f"part {res}/{a.mod} already done", flush=True); continue
        total, surv, el = r
        grand += total; gsurv += surv
        print(f"part {res}/{a.mod}: {total} graphs in {el:.0f}s ({total/el:.0f} g/s), survivors {surv} | "
              f"cumulative {grand} graphs, {gsurv} survivors, {(time.time()-T0)/60:.1f} min", flush=True)

    # ---- exact re-solve of all survivors ----
    rows = []
    for f in sorted(glob.glob(os.path.join(outdir, "part_*.csv"))):
        with open(f) as fh:
            rd = csv.DictReader(fh)
            rows.extend(rd)
    print(f"exact re-solve of {len(rows)} survivors with Clarabel", flush=True)
    out = os.path.join(HERE, "results", "n11_survivors_exact.csv")
    with open(out, "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["g6", "edges", "alpha", "theta", "gap", "ratio", "theta_ub", "status"])
        recs = []
        for r in rows:
            n, E = g6_to_adj(r["g6"])
            al = alpha_exact(n, E)
            th, st = theta_clarabel(n, E)
            recs.append((r["g6"], len(E), al, th, th - al, th / al, float(r["theta_ub"]), st))
        recs.sort(key=lambda x: -x[4])
        for rec in recs:
            w.writerow([rec[0], rec[1], rec[2], f"{rec[3]:.10f}", f"{rec[4]:.10f}", f"{rec[5]:.10f}", f"{rec[6]:.8f}", rec[7]])
    print("TOP 10 by gap:", flush=True)
    for rec in recs[:10]:
        print(f"  {rec[0]}  |E|={rec[1]} alpha={rec[2]} theta={rec[3]:.6f} gap={rec[4]:.6f} ratio={rec[5]:.6f} {rec[7]}", flush=True)
    print(f"ALL DONE in {(time.time()-T0)/3600:.2f} h", flush=True)


if __name__ == "__main__":
    main()
