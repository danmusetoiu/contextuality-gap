"""Measure the range of the dual variable Y produced by the GPU screen (for the error-bound statement in the paper).
Mirrors gpu_screen.theta_ub_gpu without pruning and reports max |Y_ij| and max ||J+Y||_2 over a sample."""
import sys, numpy as np, torch
import gpu_screen as gs

path = sys.argv[1] if len(sys.argv) > 1 else "data/sample11.g6"
n = int(sys.argv[2]) if len(sys.argv) > 2 else 11
lines = [l.strip() for l in open(path) if l.strip()][:20000]
chunk = np.frombuffer("".join(lines).encode(), dtype=np.uint8).reshape(len(lines), -1)
A = torch.from_numpy(gs.g6_chunk_to_edges(chunk, n)).to(gs.DEV)
B = A.shape[0]; J = torch.ones(n, n, device=gs.DEV)
y = torch.full((B, n, n), -1.4, device=gs.DEV) * A
m = torch.zeros_like(y); v2 = torch.zeros_like(y); b1, b2, eps, lr = 0.9, 0.999, 1e-8, 0.08
ymax_hist = []
with torch.no_grad():
    for it in range(1, 101):
        tau = 0.3 * (0.02 / 0.3) ** ((it - 1) / 99)
        M = J[None] + y
        ev, V = torch.linalg.eigh(M)
        w = torch.softmax(ev / tau, dim=1)
        G = torch.einsum("bik,bk,bjk->bij", V, w, V) * A
        lr_t = lr * (0.5 ** (it // 40))
        m = b1 * m + (1 - b1) * G; v2 = b2 * v2 + (1 - b2) * G * G
        mh = m / (1 - b1 ** it); vh = v2 / (1 - b2 ** it)
        y = (y - lr_t * mh / (vh.sqrt() + eps)) * A
        ymax_hist.append(float(y.abs().max()))
    M = J[None] + y
    norms = torch.linalg.matrix_norm(M, ord=2)
print(f"graphs {B}: max|Y| over run = {max(ymax_hist):.3f}, final max|Y| = {ymax_hist[-1]:.3f}, "
      f"max ||J+Y||_2 = {float(norms.max()):.2f}, median ||J+Y||_2 = {float(norms.median()):.2f}")
