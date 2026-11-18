"""Per causal-LM model in HF transformers: date contributed to the library (from model_doc header),
and how much of its modular source is inherited / pure rename. Output: timeline.json + summary by year."""
import json, re, sys, statistics as S, collections as C
from pathlib import Path
repo = Path(sys.argv[1]); docs = repo / "docs/source/en/model_doc"; models = repo / "src/transformers/models"
inh = {o["model"]: o for o in json.load(open(Path(__file__).parent / "modular_inheritance.json"))}
DATE = re.compile(r"contributed to Hugging Face Transformers on (\d{4}-\d{2}-\d{2})|added to Hugging Face Transformers on (\d{4}-\d{2}-\d{2})")
PUB = re.compile(r"(?:published|released)[^*]*? on (\d{4}-\d{2}-\d{2})")
rows = []
for d in sorted(p for p in models.iterdir() if p.is_dir()):
    mf = d / f"modeling_{d.name}.py"
    if not mf.exists() or "ForCausalLM(" not in mf.read_text(): continue
    doc = docs / f"{d.name}.md"; txt = doc.read_text()[:4000] if doc.exists() else ""
    m = DATE.search(txt); p = PUB.search(txt)
    o = inh.get(d.name)
    rows.append({"model": d.name, "added": (m.group(1) or m.group(2)) if m else None, "published": p.group(1) if p else None,
                 "modular": bool(o), "classes": o and o["classes"], "derived": o and o["derived"], "pure_rename": o and o["pure_rename"],
                 "parents": o and o["parents"]})
json.dump(rows, open(Path(__file__).parent / "timeline.json", "w"), indent=1)
print("causal-LM models:", len(rows), " with date:", sum(1 for r in rows if r["added"]), " modular:", sum(r["modular"] for r in rows))
by = C.defaultdict(list)
for r in rows:
    if r["added"]: by[r["added"][:4]].append(r)
print("year  added  modular  median%inherited  median%rename  llama-derived")
for y in sorted(by):
    g = by[y]; mo = [r for r in g if r["modular"] and r["classes"]]
    inh_ = [r["derived"] / r["classes"] for r in mo]; ren = [r["pure_rename"] / r["classes"] for r in mo]
    ll = sum(1 for r in mo if "llama" in (r["parents"] or {}))
    print(f"{y}  {len(g):>5}  {len(mo):>7}  {(S.median(inh_) if inh_ else float('nan')):>16.0%}  {(S.median(ren) if ren else float('nan')):>13.0%}  {ll:>5}")
