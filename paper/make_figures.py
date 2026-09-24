"""
Figures for the contextuality-gap paper.
  fig_ladder.pdf   : max gap vs n — exhaustive (all graphs), exhaustive triangle-free, Ramsey-critical lower bounds
  fig_winners.pdf  : drawings of the record graphs (n = 8, 9, 10, 11, 12tf, 13tf = C13(1,5))
Run from research/contextuality:  python paper/make_figures.py
"""
import os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from gap_search import g6_to_adj

# ---------------- data ----------------
exhaustive = {5: 0.236068, 6: 0.236068, 7: 0.317667, 8: 0.467844, 9: 2/3, 10: 2**-0.5, 11: 0.774889}
tf_exhaustive = {11: 0.774889, 12: 0.930021, 13: 1.181737}
ramsey = {  # n: (k, max gap over R(3,k)-graphs on n vertices)
    13: (5, 1.181737), 14: (6, 1.072373), 15: (6, 1.250964), 16: (6, 1.465350), 17: (6, 1.606664),
    21: (7, 2.141315), 22: (7, 2.398747), 27: (8, 3.060569), 35: (9, 4.410586),
}
R3k = {4: 9, 5: 14, 6: 18, 7: 23, 8: 28, 9: 36}

winners = {
    "n=8: Quad-$C_5$ ($\\Delta=0.4678$)": "GCQb`o",
    "n=9 ($\\Delta=2/3$)": "HCRbdO{",
    "n=10 ($\\Delta=1/\\sqrt{2}$)": "ICRb`yiu?",
    "n=11 ($\\Delta=0.7749$)": "J?`D@pgd?{?",
    "n=12, triangle-free ($\\Delta=0.9300$)": "K?`DA`gd?{Dg",
    "n=13: $C_{13}(1,5)$ ($\\Delta=1.1817$)": "L?`DE`gl@YJODg",
}


def fig_ladder(path):
    fig, ax = plt.subplots(figsize=(6.4, 3.6))
    xs = sorted(exhaustive); ax.plot(xs, [exhaustive[x] for x in xs], "o-", color="#1f4e79", label="exhaustive, all connected graphs")
    xs = sorted(tf_exhaustive); ax.plot(xs, [tf_exhaustive[x] for x in xs], "s--", color="#c55a11", label="exhaustive, triangle-free")
    xs = sorted(ramsey); ax.plot(xs, [ramsey[x][1] for x in xs], "^:", color="#548235", label="max over $R(3,k)$-graphs (lower bound)")
    for k, r in R3k.items():
        if r <= 36:
            ax.axvline(r - 0.5, color="0.8", lw=0.8, zorder=0)
            ax.text(r - 0.4, 4.3, f"$R(3,{k})={r}$", rotation=90, fontsize=6.5, color="0.4", va="top")
    ax.set_xlabel("number of vertices $n$"); ax.set_ylabel(r"maximum gap $\Delta=\vartheta-\alpha$")
    ax.set_xlim(4, 36); ax.set_ylim(0, 4.7); ax.grid(alpha=0.25); ax.legend(fontsize=7.5, loc="lower right")
    fig.tight_layout(); fig.savefig(path); plt.close(fig)


def fig_winners(path):
    fig, axes = plt.subplots(2, 3, figsize=(7.2, 4.9))
    for ax, (title, g6) in zip(axes.flat, winners.items()):
        n, E = g6_to_adj(g6); g = nx.Graph(E); g.add_nodes_from(range(n))
        if g6 == "L?`DE`gl@YJODg":
            g = nx.circulant_graph(13, [1, 5]); pos = nx.circular_layout(g)
        else:
            pos = nx.kamada_kawai_layout(g)
        nx.draw_networkx_edges(g, pos, ax=ax, width=0.9, edge_color="0.3")
        nx.draw_networkx_nodes(g, pos, ax=ax, node_size=60, node_color="#1f4e79", linewidths=0)
        ax.set_title(title, fontsize=8); ax.set_axis_off()
    fig.tight_layout(); fig.savefig(path); plt.close(fig)


if __name__ == "__main__":
    out = os.path.join(HERE, "figures"); os.makedirs(out, exist_ok=True)
    fig_ladder(os.path.join(out, "fig_ladder.pdf"))
    fig_winners(os.path.join(out, "fig_winners.pdf"))
    print("figures written to", out)
