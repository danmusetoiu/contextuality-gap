"""
Local search for large-gap graphs on n=12 WITHOUT the triangle-free restriction.

Question: is there a 12-vertex graph with triangles beating the triangle-free record 0.930021?
Start points: the triangle-free n=12 top graphs, and the n=11 top graphs + one vertex (random attachments).
Moves: add edge, delete edge, move edge (delete one, add another). Accept if gap does not decrease (plateau moves
allowed), with random restarts. Exact theta (Clarabel 1e-9) and exact alpha at every step; connectedness required.

Usage: python localsearch12.py --minutes 60 --seed 0 --out results/localsearch12.csv
"""
import os, sys, time, csv, argparse, random
import numpy as np
import networkx as nx
from gap_search import g6_to_adj, theta_clarabel, alpha_exact

N = 12
TF12 = ["K?`DA`gd?{Dg", "K?`DE`gLAsAs", "K?`DE`glAsDg", "K?`DB_kSg{U_", "K?`DA`gl?{Dg"]
N11 = ["J?`D@pgd?{?", "J?`@f?kUDG_", "J?`@f@WFTH?", "J?`FBQoFCi?", "J?`@f@Wl?y?", "JCRbeo{ifI?"]


def gap_of(E):
    g = nx.Graph(E); g.add_nodes_from(range(N))
    if not nx.is_connected(g):
        return -1, 0, 0
    th, _ = theta_clarabel(N, E)
    al = alpha_exact(N, E)
    return th - al, th, al


def canon(E):
    return tuple(sorted((min(u, v), max(u, v)) for u, v in E))


def neighbors(E, rng):
    Es = set(canon(E)); allpairs = [(i, j) for i in range(N) for j in range(i + 1, N)]
    non = [p for p in allpairs if p not in Es]
    moves = []
    for _ in range(12):
        r = rng.random()
        if r < 0.35 and non:
            moves.append(canon(list(Es) + [rng.choice(non)]))
        elif r < 0.65 and len(Es) > N - 1:
            e = rng.choice(list(Es)); moves.append(canon([x for x in Es if x != e]))
        elif non:
            e = rng.choice(list(Es)); f = rng.choice(non); moves.append(canon([x for x in Es if x != e] + [f]))
    return moves


def start_points(rng):
    pts = []
    for s in TF12:
        n, E = g6_to_adj(s); pts.append(canon(E))
    for s in N11:
        n, E = g6_to_adj(s)
        for _ in range(3):
            k = rng.randint(1, 4); att = rng.sample(range(11), k)
            pts.append(canon(list(E) + [(v, 11) for v in att]))
    return pts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--minutes", type=float, default=60); ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default="results/localsearch12.csv")
    a = ap.parse_args()
    rng = random.Random(a.seed)
    seen = {}
    def ev(E):
        if E not in seen: seen[E] = gap_of(list(E))
        return seen[E]
    t0 = time.time(); best_overall = (-1, None); best_tri = (-1, None); starts = start_points(rng); si = 0
    while time.time() - t0 < a.minutes * 60:
        cur = starts[si % len(starts)] if si < 3 * len(starts) else rng.choice(list(seen.keys())[-200:])
        si += 1
        cg = ev(cur)[0]; stall = 0
        while stall < 60 and time.time() - t0 < a.minutes * 60:
            cand = neighbors(cur, rng)
            vals = [(ev(c)[0], c) for c in cand]
            v, c = max(vals)
            if v >= cg - 1e-9:
                if v > cg + 1e-9: stall = 0
                else: stall += 1
                cur, cg = c, v
            else:
                stall += 1
            g = nx.Graph(list(cur)); tri = sum(nx.triangles(g).values()) // 3
            if cg > best_overall[0]: best_overall = (cg, cur)
            if tri > 0 and cg > best_tri[0]:
                best_tri = (cg, cur)
                print(f"[{(time.time()-t0)/60:.1f} min] best WITH triangles: gap {cg:.6f} tri={tri} |E|={len(cur)} "
                      f"alpha={ev(cur)[2]} theta={ev(cur)[1]:.6f}", flush=True)
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    rows = sorted(((v[0], v[1], v[2], E) for E, v in seen.items() if v[0] > 0.5), reverse=True)
    with open(a.out, "w", newline="") as f:
        w = csv.writer(f); w.writerow(["gap", "theta", "alpha", "edges", "triangles", "edge_list"])
        for gval, th, al, E in rows[:5000]:
            g = nx.Graph(list(E)); w.writerow([f"{gval:.8f}", f"{th:.8f}", al, len(E), sum(nx.triangles(g).values()) // 3, str(list(E))])
    print(f"evaluated {len(seen)} graphs; best overall {best_overall[0]:.6f}; best with triangles {best_tri[0]:.6f}", flush=True)


if __name__ == "__main__":
    main()
