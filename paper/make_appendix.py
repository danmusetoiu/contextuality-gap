"""Generate paper/appendix_tables.tex (n=8 ranking table, edge lists of record graphs, R(3,8) record).
Run from research/contextuality:  python paper/make_appendix.py"""
import os, sys
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
from gap_search import g6_to_adj

BS = "\\"


def tex_g6(s):
    rep = [(BS, BS + "textbackslash{}"), ("{", BS + "{"), ("}", BS + "}"), ("_", BS + "_"), ("`", BS + "textasciigrave{}"),
           ("#", BS + "#"), ("&", BS + "&"), ("%", BS + "%"), ("^", BS + "^{}"), ("~", BS + "~{}")]
    out = []
    for ch in s:
        for a, b in rep:
            if ch == a:
                out.append(b); break
        else:
            out.append(ch)
    return "".join(out)


def main():
    out = []
    d = pd.read_csv(os.path.join(ROOT, "results/n8.csv")).sort_values("gap", ascending=False).head(10).reset_index(drop=True)
    notes = {0: "Quad-$C_5$", 2: "Wagner graph", 6: "CHSH-type graph, ratio maximizer"}
    out.append(BS + "begin{table}[h]" + BS + "centering" + BS + "small" + BS + "caption{Top ten connected graphs on eight vertices by $" + BS + "gap$ (our run, Clarabel), matching Table~II of~" + BS + "cite{tamer2026} rank for rank.}" + BS + "label{tab:n8}")
    out.append(BS + "begin{tabular}{rlrrrrrl}" + BS + "toprule rank & graph6 & $|E|$ & $" + BS + "alpha$ & $" + BS + "theta$ & $" + BS + "gap$ & $" + BS + "theta/" + BS + "alpha$ & " + BS + BS + " " + BS + "midrule")
    for i, r in d.iterrows():
        note = notes.get(i, "")
        out.append(f"{i+1} & {BS}g{{{tex_g6(r.g6)}}} & {r.edges} & {r.alpha} & {r.theta:.6f} & {r.gap:.6f} & {r.ratio:.6f} & {note} {BS}{BS}")
    out.append(BS + "bottomrule" + BS + "end{tabular}" + BS + "end{table}")

    recs = [("Quad-$C_5$ ($n=8$)", "GCQb`o"), ("$n=9$ maximizer", "HCRbdO{"), ("$n=10$ maximizer", "ICRb`yiu?"),
            ("$n=11$ maximizer", "J?`D@pgd?{?"), ("$n=12$ triangle-free maximizer", "K?`DA`gd?{Dg"), ("$C_{13}(1,5)$", "L?`DE`gl@YJODg")]
    out.append("")
    out.append(BS + "paragraph{Edge lists of the record graphs} Vertices are $0," + BS + "dots,n-1$ in the labelling induced by the graph6 string.")
    out.append(BS + "begin{itemize}")
    for name, g6 in recs:
        n, E = g6_to_adj(g6)
        es = ", ".join(f"{u}{v}" if n <= 10 else f"({u},{v})" for u, v in sorted(E))
        out.append(BS + f"item {name}, {BS}g{{{tex_g6(g6)}}}: {es}.")
    out.append(BS + "end{itemize}")
    r38 = pd.read_csv(os.path.join(ROOT, "results/ramsey_r38_27_top2000.csv")).iloc[0]
    g = tex_g6(r38.g6)
    # allow line breaks inside the long string (only between escaped tokens)
    parts, buf, i = [], "", 0
    while i < len(g):
        if g[i] == BS:                       # copy a whole control sequence/symbol + its braces
            j = i + 1
            if j < len(g) and g[j].isalpha():
                while j < len(g) and g[j].isalpha(): j += 1
            else:
                j += 1                       # control symbol like \_ \{ \} \# \& \%
            if j < len(g) and g[j] == "{":
                k = g.find("}", j); j = k + 1
            buf += g[i:j]; i = j
        else:
            buf += g[i]; i += 1
        if len(buf) >= 12:
            parts.append(buf); buf = ""
    if buf: parts.append(buf)
    gbreak = (BS + "allowbreak{}").join(parts)
    out.append(BS + f"paragraph{{The $R(3,8)$ record on 27 vertices}} graph6 {BS}g{{{gbreak}}}, $|E|={r38.edges}$, ${BS}theta={r38.theta:.6f}$, ${BS}gap={r38.gap:.6f}$.")
    path = os.path.join(HERE, "appendix_tables.tex")
    open(path, "w", encoding="utf-8").write("\n".join(out) + "\n")
    print("wrote", path)


if __name__ == "__main__":
    main()
