"""Replace backticks inside \\g{...} graph6 macros with \\textasciigrave{} (T1 straight grave)."""
import sys
p = sys.argv[1] if len(sys.argv) > 1 else "contextuality-arxiv.tex"
s = open(p, encoding="utf-8").read()
out = []; i = 0; n_macros = 0; n_ticks = 0
key = "\\g{"
while True:
    j = s.find(key, i)
    if j < 0:
        out.append(s[i:]); break
    out.append(s[i:j + len(key)])
    k = j + len(key); depth = 1; arg = []
    while k < len(s) and depth > 0:
        c = s[k]
        if c == "\\" and k + 1 < len(s):          # escaped char (\{ \} \_ ...)
            arg.append(s[k:k + 2]); k += 2; continue
        if c == "{": depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0: break
        arg.append(c); k += 1
    a = "".join(arg)
    n_ticks += a.count("`")
    out.append(a.replace("`", "\\textasciigrave{}"))
    n_macros += 1
    i = k  # points at closing brace, which the next slice will include
open(p, "w", encoding="utf-8").write("".join(out))
print(f"macros: {n_macros}, backticks replaced: {n_ticks}")
