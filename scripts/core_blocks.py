"""Strict measure: are the core blocks (Attention, MLP, DecoderLayer) taken from another model?"""
import ast, json, re, sys, collections as C
from pathlib import Path
models = Path(sys.argv[1]) / "src/transformers/models"
tl = [r for r in json.load(open(Path(__file__).parent / "timeline.json")) if r["model"] != "auto"]
CORE = ("Attention", "MLP", "DecoderLayer")
CP = re.compile(r"# Copied from transformers\.models\.(\w+)\.modeling_\w+\.\w*?(Attention|MLP|DecoderLayer)\b")
for r in tl:
    borrowed = {}
    mod = models / r["model"] / f"modular_{r['model']}.py"
    if mod.exists():
        tree = ast.parse(mod.read_text()); imp = {}
        for n in ast.walk(tree):
            if isinstance(n, ast.ImportFrom) and n.module and n.level >= 2 and ".modeling_" in n.module:
                for a in n.names: imp[a.asname or a.name] = n.module.split(".")[0]
        for c in tree.body:
            if isinstance(c, ast.ClassDef):
                for k in CORE:
                    if c.name.endswith(k) and not c.name.endswith("CrossAttention"):
                        ps = [imp[b.id] for b in c.bases if isinstance(b, ast.Name) and b.id in imp]
                        if ps: borrowed.setdefault(k, ps[0])
    txt = (models / r["model"] / f"modeling_{r['model']}.py").read_text()
    for src, k in CP.findall(txt):
        if src != r["model"]: borrowed.setdefault(k, src)
    r["core_borrowed"] = borrowed
    r["n_core_borrowed"] = len(borrowed)
json.dump(tl, open(Path(__file__).parent / "timeline.json", "w"), indent=1)
n = len(tl)
for k in (1, 2, 3):
    m = sum(r["n_core_borrowed"] >= k for r in tl); print(f">= {k} of 3 core blocks borrowed: {m}/{n} ({m/n:.0%})")
by = C.defaultdict(list)
for r in tl:
    if r["added"]: by[r["added"][:4]].append(r)
for y in sorted(by):
    g = by[y]; a = sum(r["n_core_borrowed"] >= 2 for r in g); z = sum(r["n_core_borrowed"] == 0 for r in g)
    print(f"{y}: added {len(g):>3}  >=2 core blocks borrowed {a:>3} ({a/len(g):.0%})  no core block borrowed {z}")
src = C.Counter(v for r in tl for v in r["core_borrowed"].values())
print("core blocks lent by:", src.most_common(10))
print("own core (0 borrowed):", sorted(r["model"] for r in tl if r["n_core_borrowed"] == 0))
