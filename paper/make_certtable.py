"""Generate paper/appendix_cert.tex from certificates/summary.csv.  Run from research/contextuality."""
import os, sys
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
BS = "\\"
LABEL = {"n8_QuadC5": "Quad-$C_5$ ($n=8$)", "n8_Wagner": "Wagner ($n=8$)", "n9_max": "$n=9$ maximizer",
         "n10_max": "$n=10$ maximizer", "n11_max": "$n=11$ maximizer", "n11_rank2": "$n=11$, rank 2",
         "n12_tf_max": "$n=12$ triangle-free max.", "n13_C13_1_5": "$C_{13}(1,5)$",
         "R36_n16_max": "$R(3,6)$ best, $n=16$", "R36_n17_max": "$R(3,6)$ best, $n=17$", "R37_n22_max": "$R(3,7)$ best, $n=22$"}

d = pd.read_csv(os.path.join(ROOT, "certificates/summary.csv"))
out = [BS + "begin{table}[h]" + BS + "centering" + BS + "small",
       BS + "caption{Certificates for the record graphs. $[" + BS + "theta_{" + BS + "rm lb}," + BS + "theta_{" + BS + "rm ub}]$ is the interval certified in double precision by an explicit primal feasible $X$ (trace one, zero on edges, PSD after eigenvalue clipping; the residual on edge entries is below $10^{-9}$) and an explicit dual feasible $Y$ (supported on the edges, $" + BS + "lambda_{" + BS + "max}(J+Y)$ recomputed with LAPACK). $r$ is the rank of the maximum-rank optimal $X$ returned by the interior-point solver, hence an upper bound on the minimal dimension of an orthogonal representation attaining $" + BS + "theta$; $v^*=(" + BS + "alpha-n/r)/(" + BS + "theta-n/r)$ is the critical visibility under white noise in dimension $r$. All matrices and the orthogonal representations are in the repository (" + BS + "texttt{certificates/*.json}).}",
       BS + "label{tab:cert}",
       BS + "begin{tabular}{lrrrllrr}" + BS + "toprule",
       "graph & $n$ & $|E|$ & $" + BS + "alpha$ & $" + BS + "theta_{" + BS + "rm lb}$ & $" + BS + "theta_{" + BS + "rm ub}$ & $r$ & $v^*$ " + BS + BS + " " + BS + "midrule"]
for _, r in d.iterrows():
    v = "--" if pd.isna(r.visibility) else f"{r.visibility:.4f}"
    out.append(f"{LABEL.get(r['name'], r['name'])} & {r.n} & {r.edges} & {r.alpha} & {r.certified_lb:.9f} & {r.certified_ub:.9f} & {r.rank_X} & {v} {BS}{BS}")
out += [BS + "bottomrule" + BS + "end{tabular}" + BS + "end{table}"]
open(os.path.join(HERE, "appendix_cert.tex"), "w", encoding="utf-8").write("\n".join(out) + "\n")
print("wrote appendix_cert.tex with", len(d), "rows")
