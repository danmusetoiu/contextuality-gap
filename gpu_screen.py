"""
GPU batched screening for the CSW contextuality gap  Δ(G) = ϑ(G) − α(G).

For every graph we compute
  α(G)      exactly (bitmask enumeration of all 2^n vertex subsets, on GPU)
  ub_ϑ(G)   a RIGOROUS upper bound on ϑ(G) from the dual SDP:
              ϑ(G) = min { λ_max(A) : A_ii = 1, A_ij = 1 for ij ∉ E }
            so for ANY symmetric Y supported on the edges, λ_max(J + Y) ≥ ϑ(G).
            We optimise Y per graph with a few Adam steps (top eigenvector by
            warm-started power iteration), then take one exact batched eigh
            (float64) for the final certificate.
A graph survives iff  ub_ϑ − α ≥ threshold − margin.  Survivors are re-solved
exactly with Clarabel (gap_search.theta_clarabel).

Usage:
  python gpu_screen.py data/graph9c.g6 results/screen9.csv --n 9 --thr 0.60
  geng -c -q 11 3/20 | python gpu_screen.py - results/screen11_3of20.csv --n 11 --thr 0.7071
"""
import sys, os, time, argparse, csv
import numpy as np
import torch

DEV = torch.device("cuda" if torch.cuda.is_available() else "cpu")


# ---------- vectorised graph6 decode (fixed n) ----------
def g6_chunk_to_edges(lines: np.ndarray, n: int):
    """lines: (B, L) uint8 array of graph6 chars (no newline). Returns (B, n, n) float32 adjacency."""
    nb = n * (n - 1) // 2
    L = 1 + (nb + 5) // 6
    data = lines[:, 1:L].astype(np.int64) - 63          # (B, L-1), 6 bits each
    bits = ((data[:, :, None] >> np.arange(5, -1, -1)) & 1).reshape(len(lines), -1)[:, :nb]
    iu = np.array([(i, j) for j in range(1, n) for i in range(j)])   # graph6 order: column-major upper
    A = np.zeros((len(lines), n, n), dtype=np.float32)
    A[:, iu[:, 0], iu[:, 1]] = bits
    A[:, iu[:, 1], iu[:, 0]] = bits
    return A


def read_g6_lines(fh, n, batch):
    """Yield (B, L) uint8 arrays from a text stream of graph6 lines with fixed n."""
    nb = n * (n - 1) // 2
    L = 1 + (nb + 5) // 6
    buf = []
    for line in fh:
        line = line.strip()
        if not line or line.startswith(">>"):
            continue
        if len(line) != L:
            raise ValueError(f"unexpected graph6 length {len(line)} for n={n}: {line}")
        buf.append(line)
        if len(buf) == batch:
            yield np.frombuffer("".join(buf).encode(), dtype=np.uint8).reshape(len(buf), L)
            buf = []
    if buf:
        yield np.frombuffer("".join(buf).encode(), dtype=np.uint8).reshape(len(buf), L)


# ---------- exact alpha on GPU ----------
_SUB = {}

def alpha_gpu(A: torch.Tensor):
    """A: (B,n,n) 0/1. Exact independence number via all 2^n subsets."""
    B, n, _ = A.shape
    if n not in _SUB:
        S = torch.arange(1 << n, device=DEV, dtype=torch.int64)
        bitsS = ((S[:, None] >> torch.arange(n, device=DEV)) & 1).to(torch.float32)   # (2^n, n)
        _SUB[n] = (bitsS, bitsS.sum(1))
    bitsS, pop = _SUB[n]
    # subset S independent  <=>  s^T A s == 0  (s = indicator).
    # Process subsets in chunks so the (B, chunk, n) intermediate stays small (n=13/14: 2^n = 8k/16k subsets).
    S_total = bitsS.shape[0]
    chunk = max(256, min(S_total, (256 << 20) // (B * n * 4)))     # ~256 MB intermediate
    alpha = torch.zeros(B, device=DEV, dtype=torch.float32)
    for s0 in range(0, S_total, chunk):
        bs = bitsS[s0:s0 + chunk]                                    # (c, n)
        AS = torch.matmul(bs, A)                                     # (B, c, n)  = (A s)^T per subset
        inside = (AS * bs[None]).sum(-1)                             # (B, c)     = s^T A s
        ok = inside < 0.5
        cand = torch.where(ok, pop[s0:s0 + chunk][None, :], torch.zeros(1, device=DEV))
        alpha = torch.maximum(alpha, cand.max(1).values)
    return alpha.to(torch.int64)


# ---------- rigorous theta upper bound on GPU ----------
FP32_MARGIN = 1e-3   # safety margin added to float32 eigenvalues before any pruning decision

@torch.no_grad()
def theta_ub_gpu(A: torch.Tensor, alpha=None, thr=None, iters=100, lr=0.08, y0=-1.4,
                 prune_every=10, tau0=0.3, tau1=0.02):
    """
    A: (B,n,n) 0/1 adjacency (float32).
    Returns (ub, keep): ub = float64 rigorous upper bounds on ϑ(G) (inf for graphs pruned early),
                        keep = bool mask of graphs whose bound − α could still reach thr.
    Dual: ϑ(G) = min_Y λ_max(J + Y), Y symmetric, supported on E.  Every Y gives a valid bound.
    Optimiser: Adam on the smoothed max-eigenvalue  τ·logsumexp(λ/τ)  (gradient V diag(softmax) V^T ⊙ A),
    τ annealed tau0→tau1.  Every `prune_every` iterations graphs whose fp32 λ_max + margin − α < thr are
    dropped from the batch (rigorous: the bound only decreases with more optimisation, and the prune test
    already includes the fp32 margin).  Final certificate for survivors: float64 eigvalsh.
    """
    B, n, _ = A.shape
    J = torch.ones(n, n, device=DEV)
    idx = torch.arange(B, device=DEV)                   # indices of graphs still active
    Aa = A
    y = torch.full((B, n, n), y0, device=DEV) * Aa
    m = torch.zeros_like(y); v2 = torch.zeros_like(y)   # Adam state
    b1, b2, eps = 0.9, 0.999, 1e-8
    ub = torch.full((B,), float("inf"), device=DEV, dtype=torch.float64)
    al = alpha.to(torch.float32) if alpha is not None else None
    for it in range(1, iters + 1):
        tau = tau0 * (tau1 / tau0) ** ((it - 1) / max(1, iters - 1))
        M = J[None] + y
        ev, V = torch.linalg.eigh(M)                    # ascending eigenvalues, (b,n),(b,n,n)
        w = torch.softmax(ev / tau, dim=1)              # smoothed-max weights
        G = torch.einsum("bik,bk,bjk->bij", V, w, V) * Aa   # gradient wrt y (symmetric, on edges)
        # Adam step (with cosine-free simple decay)
        lr_t = lr * (0.5 ** (it // 40))
        m = b1 * m + (1 - b1) * G
        v2 = b2 * v2 + (1 - b2) * G * G
        mh = m / (1 - b1 ** it); vh = v2 / (1 - b2 ** it)
        y = y - lr_t * mh / (vh.sqrt() + eps)
        y = y * Aa
        # progressive pruning on a rigorous fp32 bound
        if thr is not None and (it % prune_every == 0 or it == iters):
            lam = ev[:, -1] + FP32_MARGIN
            keep = (lam - al[idx]) >= thr
            if keep.sum() < len(idx):
                sel = torch.nonzero(keep).flatten()
                idx = idx[sel]; Aa = Aa[sel]; y = y[sel]; m = m[sel]; v2 = v2[sel]
                if len(idx) == 0:
                    break
    if len(idx) > 0:
        M = (J[None] + y).double()
        ub[idx] = torch.linalg.eigvalsh(M)[:, -1]
    keep = torch.zeros(B, dtype=torch.bool, device=DEV)
    if thr is not None:
        keep[idx] = (ub[idx] - alpha[idx].double()) >= thr
    else:
        keep[:] = True
    return ub, keep


def screen_file(path, out_csv, n, thr, batch=8192, margin=1e-6, iters=120, limit=0):
    fh = sys.stdin if path == "-" else open(path)
    t0 = time.time(); total = 0; surv = 0
    os.makedirs(os.path.dirname(os.path.abspath(out_csv)), exist_ok=True)
    with open(out_csv, "w", newline="") as out:
        w = csv.writer(out); w.writerow(["g6", "alpha", "theta_ub"])
        for chunk in read_g6_lines(fh, n, batch):
            if limit and total >= limit:
                break
            A_np = g6_chunk_to_edges(chunk, n)
            A = torch.from_numpy(A_np).to(DEV)
            al = alpha_gpu(A)
            ub, keep = theta_ub_gpu(A, alpha=al, thr=thr - margin, iters=iters)
            idx = torch.nonzero(keep).flatten().cpu().numpy()
            for i in idx:
                w.writerow([chunk[i].tobytes().decode(), int(al[i]), f"{float(ub[i]):.8f}"])
            total += len(chunk); surv += len(idx)
            if (total // batch) % 20 == 0:
                el = time.time() - t0
                print(f"{total} graphs  {el:.0f}s  {total/el:.0f} g/s  survivors {surv} ({100*surv/total:.3f}%)", flush=True)
    el = time.time() - t0
    print(f"DONE {total} graphs in {el:.0f}s ({total/el:.0f} g/s); survivors {surv}", flush=True)
    return total, surv


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("g6file")
    ap.add_argument("outcsv")
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--thr", type=float, required=True)
    ap.add_argument("--batch", type=int, default=8192)
    ap.add_argument("--iters", type=int, default=120)
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    print("device", DEV, flush=True)
    screen_file(a.g6file, a.outcsv, a.n, a.thr, a.batch, iters=a.iters, limit=a.limit)
