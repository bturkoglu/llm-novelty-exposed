"""Figure 2: Qwen3 vs Llama attention in HF transformers 0d7a621 (generated modeling files). Lines are read from the
source, not typed by hand; Qwen3's class prefix is shown as is. Usage: fig_qwen3_llama.py <tf_root> <out.png>"""
import re, sys, textwrap
from pathlib import Path
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
R = Path(sys.argv[1]) / "src/transformers/models"
def grab(m, cls):
    import ast
    tree = ast.parse((R / m / f"modeling_{m}.py").read_text())
    c = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == cls); out = []
    for f in c.body:
        if isinstance(f, ast.FunctionDef) and f.name in ("__init__", "forward"):
            for st in ast.walk(f):
                if isinstance(st, ast.Assign):
                    t = ast.unparse(st)
                    if re.search(r"q_proj|k_proj|q_norm|k_norm|^query_states =|^key_states =|sliding_window|attention_interface\(self", t) and t not in out: out.append(t)
    return out
L, Q = grab("llama", "LlamaAttention"), grab("qwen3", "Qwen3Attention")
norm = lambda s: s.replace("Qwen3", "Llama")
Ln = {norm(x) for x in L}
fig, ax = plt.subplots(1, 2, figsize=(13, 0.42 * max(len(L), len(Q)) + 1.4))
for a, lines, title, other in ((ax[0], L, "Llama (modeling_llama.py)", None), (ax[1], Q, "Qwen3 (modeling_qwen3.py)", Ln)):
    a.axis("off"); a.set_title(title, loc="left", fontsize=11, family="monospace")
    y = 1.0
    for l in lines:
        new = other is not None and norm(l) not in other
        for k, part in enumerate(textwrap.wrap(l, 66, subsequent_indent="    ", break_long_words=False, break_on_hyphens=False)):
            a.text(0, y, part, family="monospace", fontsize=8.4, va="top", color="#000",
                   bbox=dict(facecolor="#d9f0d3", edgecolor="none", pad=1.2) if new else None, transform=a.transAxes)
            y -= 1 / (max(len(L), len(Q)) * 1.9)
fig.text(0.01, 0.01, "Lines of the attention class that touch the query/key projections, read from HF transformers commit 0d7a621.\n"
         "Shaded: statements in Qwen3 that differ from Llama after renaming the class prefix (the attention call differs only by passing sliding_window).", fontsize=8)
plt.tight_layout(rect=(0, 0.07, 1, 1)); plt.savefig(sys.argv[2], dpi=200); print("saved", sys.argv[2], len(L), len(Q))
for l in Q: print(("+ " if norm(l) not in Ln else "  ") + l[:120])
