"""Step 3 eligibility (coding_protocol.md): metadata only (arXiv title+abstract), no report body read."""
import json, re
f = json.load(open("report_frame_raw.json")); m = json.load(open("arxiv_meta.json"))
QUAL = {"v", "moe", "text", "small", "flash", "melody", "lite", "dense", "shared", "multimodal", "hybrid", "dsa",
        "gpt", "japanese", "swa", "unified", "assistant", "exp", "note", "x", "h", "v1", "open"}
def toks(model):
    return [t for t in re.split(r"[_\d]+", model) if t and t not in QUAL]
rows, seen = [], {}
for r in f:
    a = r["arxiv"]
    row = {"model": r["model"], "added": r["added"], "arxiv": a}
    if not a:
        row.update(status="NOT_ELIGIBLE", reason="no arXiv link in model_doc"); rows.append(row); continue
    meta = m[a]; text = (meta["title"] + " " + meta["abstract"]).lower().replace("-", "")
    row["title"] = meta["title"]; row["year"] = 2000 + int(a[:2])  # arXiv id yymm = first-submission month
    hits = [t for t in toks(r["model"]) if re.search(r"\b" + re.escape(t.replace("-", "")), text)]
    row["name_hits"] = hits
    if a in seen:
        row.update(status="DUPLICATE", reason=f"report shared with {seen[a]}")
    elif row["year"] < 2020:
        row.update(status="NOT_ELIGIBLE", reason="report before 2020")
    elif not hits:
        row.update(status="NOT_ELIGIBLE", reason="arXiv title/abstract does not name the model or family")
    else:
        row.update(status="ELIGIBLE_AUTO")
    seen.setdefault(a, r["model"]); rows.append(row)
json.dump(rows, open("eligibility_auto.json", "w"), indent=1)
for r in rows:
    if r["arxiv"]: print(f'{r["status"]:14} {r["year"]} {r["model"]:18} {r.get("name_hits")} | {r["title"][:70]}')
