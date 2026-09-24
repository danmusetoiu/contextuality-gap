"""
Figures 3 and 4 for the paper.
  fig_validation.pdf : (a) histogram of certified GPU bound minus exact theta over all 11,117 connected 8-vertex graphs
                       (no pruning, 100 iterations); (b) at n=10, number of graphs with gap >= x (exact table) and the
                       screen's survivor count at threshold 0.65.
  fig_n11_survivors.pdf : the 100 exact survivors of the n=11 screen: gap vs |E|, triangle-free vs not.
Run from research/contextuality:  python paper/make_figures2.py
"""
import os, sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
import torch

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
import gpu_screen as gs
from gap_search import g6_to_adj


def fig_validation(path):
    ref = pd.read_csv(os.path.join(ROOT, "results/n8.csv"))
    lines = list(ref.g6)
    chunk = np.frombuffer("".join(lines).encode(), dtype=np.uint8).reshape(len(lines), -1)
    A = torch.from_numpy(gs.g6_chunk_to_edges(chunk, 8)).to(gs.DEV)
    ub, _ = gs.theta_ub_gpu(A, iters=100)
    d = ub.cpu().numpy() - ref.theta.values
    n10 = pd.read_csv(os.path.join(ROOT, "results/n10_top2000.csv"))
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.2, 2.9))
    a1.hist(np.log10(np.maximum(d, 1e-12)), bins=50, color="#1f4e79")
    a1.set_xlabel(r"$\log_{10}(\mathrm{certified\ bound} - \vartheta)$"); a1.set_ylabel("graphs ($n=8$)")
    a1.set_title(f"min {d.min():.1e}, median {np.median(d):.3f}, max {d.max():.2f}; no violations", fontsize=8)
    xs = np.linspace(0.55, 0.72, 200); counts = [(n10.gap >= x).sum() for x in xs]
    a2.plot(xs, counts, color="#1f4e79", label=r"graphs with $\Delta\geq x$ (exact)")
    a2.axvline(0.65, color="#c55a11", ls="--", lw=1); a2.plot([0.65], [30], "s", color="#c55a11", label="GPU screen survivors at 0.65: 30")
    a2.set_yscale("log"); a2.set_xlabel(r"threshold $x$"); a2.set_ylabel("count ($n=10$)"); a2.legend(fontsize=7)
    fig.tight_layout(); fig.savefig(path); plt.close(fig)


def fig_n11(path):
    d = pd.read_csv(os.path.join(ROOT, "results/n11_survivors_exact.csv"))
    tri = []
    for s in d.g6:
        n, E = g6_to_adj(s); g = nx.Graph(E); tri.append(sum(nx.triangles(g).values()) // 3)
    d["tri"] = tri
    fig, ax = plt.subplots(figsize=(5.6, 3.2))
    tf = d[d.tri == 0]; nt = d[d.tri > 0]
    ax.scatter(tf.edges, tf.gap, s=22, color="#c55a11", label=r"triangle-free ($\alpha=4$)", zorder=3)
    ax.scatter(nt.edges, nt.gap, s=22, color="#1f4e79", marker="^", label=r"with triangles ($\alpha=3$)", zorder=3)
    ax.axhline(2 ** -0.5, color="0.6", ls=":", lw=1); ax.text(30.5, 2 ** -0.5 + 0.002, r"$n=10$ record $1/\sqrt{2}$", fontsize=7, color="0.4")
    ax.set_xlabel("number of edges"); ax.set_ylabel(r"$\Delta=\vartheta-\alpha$"); ax.legend(fontsize=8)
    ax.set_title("the 100 survivors of the $n=11$ screen (exact values)", fontsize=9)
    fig.tight_layout(); fig.savefig(path); plt.close(fig)


if __name__ == "__main__":
    out = os.path.join(HERE, "figures")
    fig_validation(os.path.join(out, "fig_validation.pdf"))
    fig_n11(os.path.join(out, "fig_n11_survivors.pdf"))
    print("done")
