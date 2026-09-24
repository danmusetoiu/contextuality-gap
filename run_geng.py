"""
Generic exhaustive contextuality-gap search over a geng-defined graph class:
geng (nauty) -> GPU screen (rigorous upper bound on theta) -> Clarabel exact on survivors.

Examples:
  python run_geng.py --n 12 --tag tf12 --geng "-c -t" --mod 20 --thr 0.70
  python run_geng.py --n 12 --tag d4_12 --geng "-c -D4" --mod 20 --thr 0.70
  python run_geng.py --n 11 --tag all11 --geng "-c" --mod 50 --thr 0.707106

Resumable per part: results/<tag>/part_<res>.csv + .done.  Final: results/<tag>_survivors_exact.csv
"""
import os, sys, time, subprocess, argparse, csv, glob, shlex
import torch

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gpu_screen as gs
from gap_search import g6_to_adj, theta_clarabel, alpha_exact

GENG = os.path.join(HERE, "geng.exe")


def screen_part(n, geng_flags, res, mod, thr, batch, iters, outdir):
    out_csv = os.path.join(outdir, f"part_{res}.csv")
    done = os.path.join(outdir, f"part_{res}.done")
    if os.path.exists(done):
        return None
    cmd = [GENG] + shlex.split(geng_flags) + ["-q", str(n), f"{res}/{mod}"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, bufsize=1 << 20)
    t0 = time.time(); total = 0; surv = 0
    with open(out_csv, "w", newline="") as out:
        w = csv.writer(out); w.writerow(["g6", "alpha", "theta_ub"])
        for chunk in gs.read_g6_lines(p.stdout, n, batch):
            A = torch.from_numpy(gs.g6_chunk_to_edges(chunk, n)).to(gs.DEV)
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
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--geng", default="-c", help="geng flags, e.g. '-c -t' (connected, triangle-free)")
    ap.add_argument("--mod", type=int, default=20)
    ap.add_argument("--thr", type=float, required=True)
    ap.add_argument("--batch", type=int, default=32768)
    ap.add_argument("--iters", type=int, default=100)
    a = ap.parse_args()
    outdir = os.path.join(HERE, "results", a.tag)
    os.makedirs(outdir, exist_ok=True)
    print(f"[{a.tag}] device {gs.DEV}  n={a.n} geng='{a.geng}' mod={a.mod} thr={a.thr}", flush=True)
    T0 = time.time(); grand = 0; gsurv = 0
    for res in range(a.mod):
        r = screen_part(a.n, a.geng, res, a.mod, a.thr, a.batch, a.iters, outdir)
        if r is None:
            print(f"[{a.tag}] part {res}/{a.mod} already done", flush=True); continue
        total, surv, el = r
        grand += total; gsurv += surv
        print(f"[{a.tag}] part {res}/{a.mod}: {total} graphs in {el:.0f}s ({total/max(el,1e-9):.0f} g/s), survivors {surv} | "
              f"cumulative {grand} graphs, {gsurv} survivors, {(time.time()-T0)/60:.1f} min", flush=True)

    rows = []
    for f in sorted(glob.glob(os.path.join(outdir, "part_*.csv"))):
        with open(f) as fh:
            rows.extend(csv.DictReader(fh))
    print(f"[{a.tag}] exact re-solve of {len(rows)} survivors with Clarabel", flush=True)
    out = os.path.join(HERE, "results", f"{a.tag}_survivors_exact.csv")
    recs = []
    for r in rows:
        n, E = g6_to_adj(r["g6"])
        al = alpha_exact(n, E)
        th, st = theta_clarabel(n, E)
        recs.append((r["g6"], len(E), al, th, th - al, th / al, float(r["theta_ub"]), st))
    recs.sort(key=lambda x: -x[4])
    with open(out, "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["g6", "edges", "alpha", "theta", "gap", "ratio", "theta_ub", "status"])
        for rec in recs:
            w.writerow([rec[0], rec[1], rec[2], f"{rec[3]:.10f}", f"{rec[4]:.10f}", f"{rec[5]:.10f}", f"{rec[6]:.8f}", rec[7]])
    print(f"[{a.tag}] TOP 10 by gap:", flush=True)
    for rec in recs[:10]:
        print(f"  {rec[0]}  |E|={rec[1]} alpha={rec[2]} theta={rec[3]:.6f} gap={rec[4]:.6f} ratio={rec[5]:.6f} {rec[7]}", flush=True)
    print(f"[{a.tag}] ALL DONE in {(time.time()-T0)/3600:.2f} h", flush=True)


if __name__ == "__main__":
    main()
