"""Step 4 deconstruction (Sörensen's harmony-search analogue): how far is model X from Llama in the reference
implementation? Compares the generated standalone modeling_<x>.py with modeling_llama.py (HF transformers 0d7a621)
after (1) renaming X's class prefix to Llama, (2) stripping comments, docstrings, imports, decorators, blank lines,
type-only/doc/logging lines. Reports differing executable lines per class. Usage: deconstruct.py <tf_root> x [x...]"""
import ast, difflib, json, re, sys
from pathlib import Path
ROOT = Path(sys.argv[1]) / "src/transformers/models"
PREFIX = {"qwen2": "Qwen2", "qwen3": "Qwen3", "mistral": "Mistral", "olmo2": "Olmo2", "gemma": "Gemma"}

def classes(path, prefix):
    src = path.read_text()
    if prefix: src = re.sub(rf"\b{prefix}(?=[A-Z])", "Llama", src)
    tree = ast.parse(src); out = {}
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            for n in ast.walk(node):   # drop docstrings
                if isinstance(n, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)) and n.body and isinstance(n.body[0], ast.Expr) \
                   and isinstance(getattr(n.body[0], "value", None), ast.Constant) and isinstance(n.body[0].value.value, str):
                    n.body = n.body[1:] or [ast.Pass()]
            node.decorator_list = []
            lines = [l.rstrip() for l in ast.unparse(node).splitlines()]
            lines = [l for l in lines if l.strip() and not re.match(r"\s*(logger\.|warnings\.warn|_CHECKPOINT|_CONFIG_FOR_DOC)", l)]
            out[node.name] = lines
    return out

L = classes(ROOT / "llama/modeling_llama.py", None)
res = {}
for m in sys.argv[2:]:
    X = classes(ROOT / f"{m}/modeling_{m}.py", PREFIX[m]); r = {"classes": {}, "only_in_x": [], "only_in_llama": []}
    for name, xl in X.items():
        if name not in L: r["only_in_x"].append({"class": name, "lines": len(xl), "code": xl}); continue
        d = [l for l in difflib.unified_diff(L[name], xl, lineterm="", n=0) if l[:1] in "+-" and not l.startswith(("+++", "---"))]
        if d: r["classes"][name] = {"llama_lines": len(L[name]), "changed": d}
    r["only_in_llama"] = [n for n in L if n not in X]
    r["llama_total_lines"] = sum(len(v) for v in L.values()); r["x_total_lines"] = sum(len(v) for v in X.values())
    r["diff_lines"] = sum(len(v["changed"]) for v in r["classes"].values()) + sum(c["lines"] for c in r["only_in_x"])
    res[m] = r
    print(f"\n=== {m}: {r['x_total_lines']} exec lines vs llama {r['llama_total_lines']}; differing lines {r['diff_lines']}")
    for k, v in r["classes"].items():
        print(f"  ~ {k} ({len(v['changed'])} lines)"); [print("     ", l[:150]) for l in v["changed"][:14]]
    for c in r["only_in_x"]: print(f"  + {c['class']} ({c['lines']} lines, new class)")
    if r["only_in_llama"]: print("  - missing vs llama:", r["only_in_llama"])
json.dump(res, open("deconstruction.json", "w"), indent=1)
