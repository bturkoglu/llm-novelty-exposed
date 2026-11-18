"""Union measure for causal-LM models: library code declares the model is (partly) built from another model,
either via modular inheritance or via '# Copied from transformers.models.<other>' markers."""
import json, re, sys, collections as C
from pathlib import Path
models = Path(sys.argv[1]) / "src/transformers/models"
tl = json.load(open(Path(__file__).parent / "timeline.json"))
CP = re.compile(r"# Copied from transformers\.models\.(\w+)\.")
for r in tl:
    txt = (models / r["model"] / f"modeling_{r['model']}.py").read_text()
    src = C.Counter(m for m in CP.findall(txt) if m != r["model"])
    r["copied_from"] = dict(src)
    r["declared_derivative"] = bool((r["parents"] or {})) or bool(src)
    r["sources"] = sorted(set((r["parents"] or {})) | set(src))
json.dump(tl, open(Path(__file__).parent / "timeline.json", "w"), indent=1)
n = len(tl); dd = sum(r["declared_derivative"] for r in tl)
print(f"causal-LM models {n}: declared derivative of another model {dd} ({dd/n:.0%})")
by = C.defaultdict(list)
for r in tl:
    if r["added"]: by[r["added"][:4]].append(r)
for y in sorted(by):
    g = by[y]; d = sum(r["declared_derivative"] for r in g); l = sum("llama" in r["sources"] for r in g)
    print(f"{y}: added {len(g):>3}  declared-derivative {d:>3} ({d/len(g):.0%})  borrows from llama {l:>3}")
print("not declared derivative:", sorted(r["model"] for r in tl if not r["declared_derivative"]))
