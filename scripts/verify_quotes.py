"""Deterministic quote check (coding_protocol.md, invariant 4). A coded value survives only if its quote is found
verbatim (after whitespace/hyphenation/case normalisation) on the stated page or an adjacent one (+-1, for
page-break spill). Failed values -> NR (ablation -> NO). Usage: verify_quotes.py A|B -> coding/<coder>_verified.json"""
import json, re, sys, pathlib
from code_reports import pages, HERE

def norm(s):
    s = s.replace("­", "").replace("ﬁ", "fi").replace("ﬂ", "fl").replace("’", "'").replace("“", '"').replace("”", '"')
    s = re.sub(r"-\s*\n\s*", "", s)              # line-end hyphenation
    return re.sub(r"[^a-z0-9]+", "", s.lower())  # alnum only: robust to layout spacing and punctuation

def found(q, pg, P):
    nq = norm(q)
    if len(nq) < 20: return False
    for p in (pg, pg - 1, pg + 1):
        if 1 <= p <= len(P) and nq in P[p - 1]: return True
    return False

FIELDS = ["seeds", "rerun", "scores_copied", "third_party", "data_disclosure", "tokens_disclosed", "compute_disclosed"]
LOW = {"seeds": "NR", "rerun": "NR", "scores_copied": "NR", "third_party": "NO", "data_disclosure": "NONE",
       "tokens_disclosed": "N", "compute_disclosed": "N"}

def verify(coder):
    out, stats = {}, {"checked": 0, "failed": 0}
    for f in sorted((HERE / "coding" / coder).glob("*.json")):
        d = json.load(open(f)); c = d["coding"]; P = [norm(p) for p in pages(d["arxiv"])]
        v = {"is_release_report": c["is_release_report"], "comparators": c["comparators"], "failed": []}
        def chk(label, q, pg):
            stats["checked"] += 1
            ok = found(q, pg, P)
            if not ok: stats["failed"] += 1; v["failed"].append({"field": label, "quote": q[:120], "page": pg})
            return ok
        v["claims"] = []
        for i, k in enumerate(c["claims"]):
            if not chk(f"claim{i}", k["quote"], k["page"]): continue          # unverified claim dropped
            ab = k["ablation"]
            if ab in ("YES", "PARTIAL") and not chk(f"claim{i}.ablation", k["ablation_quote"], k["ablation_page"]): ab = "NO"
            v["claims"].append({"category": k["category"], "ablation": ab, "claim": k["claim"], "page": k["page"],
                               "quote": k["quote"], "ablation_quote": k["ablation_quote"] if ab != "NO" or k["ablation"] == "NO" else "",
                               "ablation_page": k["ablation_page"]})
        for fld in FIELDS:
            val = c[fld]["value"]
            if val != LOW[fld] and not chk(fld, c[fld]["quote"], c[fld]["page"]): val = LOW[fld]
            v[fld] = val
            v[fld + "_evidence"] = {"quote": c[fld]["quote"], "page": c[fld]["page"]} if val == c[fld]["value"] else {"quote": "", "page": 0}
        v["renames"] = [r for i, r in enumerate(c["renames"]) if chk(f"rename{i}", r["quote"], r["page"])]
        out[d["arxiv"]] = {"model": d["model"], **v}
    json.dump({"coder": coder, "stats": stats, "reports": out}, open(HERE / "coding" / f"{coder}_verified.json", "w"), indent=1)
    print(coder, len(out), "reports;", stats)

if __name__ == "__main__":
    verify(sys.argv[1])
