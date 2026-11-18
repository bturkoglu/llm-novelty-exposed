"""How much of each model in HF transformers is declared as inherited from another model?
Reads modular_*.py (the library's own source of truth for derived models). AST only, nothing executed."""
import ast, json, sys, collections as C
from pathlib import Path
root = Path(sys.argv[1]) / "src/transformers/models"
out = []
for f in sorted(root.glob("*/modular_*.py")):
    model = f.parent.name
    tree = ast.parse(f.read_text())
    imp = {}  # class name -> source model
    for n in ast.walk(tree):
        if isinstance(n, ast.ImportFrom) and n.module and n.level >= 2 and ".modeling_" in n.module:
            src = n.module.split(".")[0]
            for a in n.names: imp[a.asname or a.name] = src
    classes = [n for n in tree.body if isinstance(n, ast.ClassDef)]
    derived, rename, parents = 0, 0, C.Counter()
    for c in classes:
        ps = [b.id for b in c.bases if isinstance(b, ast.Name) and b.id in imp]
        if not ps: continue
        derived += 1; parents.update(imp[p] for p in ps)
        body = [s for s in c.body if not (isinstance(s, ast.Expr) and isinstance(getattr(s, "value", None), ast.Constant))]
        if all(isinstance(s, ast.Pass) for s in body) or not body: rename += 1
    is_lm = any(c.name.endswith("ForCausalLM") for c in classes) or (root / model / f"modeling_{model}.py").exists() and "ForCausalLM" in (root / model / f"modeling_{model}.py").read_text()
    out.append({"model": model, "classes": len(classes), "derived": derived, "pure_rename": rename,
                "parents": dict(parents), "causal_lm": is_lm, "modular_lines": len(f.read_text().splitlines()),
                "modeling_lines": len((root / model / f"modeling_{model}.py").read_text().splitlines()) if (root / model / f"modeling_{model}.py").exists() else None})
json.dump(out, open(Path(__file__).parent / "modular_inheritance.json", "w"), indent=1)
lm = [o for o in out if o["causal_lm"]]
print("modular models:", len(out), " causal-LM among them:", len(lm), " total model dirs:", len(list(root.iterdir())))
for name, grp in (("all", out), ("causal-LM", lm)):
    d = sum(o["derived"] for o in grp); c = sum(o["classes"] for o in grp); r = sum(o["pure_rename"] for o in grp)
    print(f"[{name}] classes {c}, inherited from another model {d} ({d/c:.0%}), pure renames (body = pass) {r} ({r/c:.0%})")
    pc = C.Counter()
    for o in grp:
        for p in o["parents"]: pc[p] += 1
    print(f"   most-inherited-from models (number of models borrowing from them): {pc.most_common(12)}")
llama = sorted([o["model"] for o in lm if "llama" in o["parents"]])
print(len(llama), "causal-LM models inherit from llama:", ", ".join(llama))
ml = sum(o["modular_lines"] for o in lm); gl = sum(o["modeling_lines"] or 0 for o in lm)
print(f"causal-LM: modular source {ml} lines expands to {gl} lines of modeling code ({ml/gl:.0%} written, rest copied)")
