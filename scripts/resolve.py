"""Resolution pass (coding_protocol.md "third pass that sees both codings and the quotes").
Resolver = third model family on Bedrock (us.xai.grok-4.7): not Claude (coder A), not OpenAI (coder B), and not a
vendor with a report in the sample (D-072). It sees, per report, only the disagreeing items, both coders' values with
their quotes, and the text of the pages those quotes cite (+-1). Rule: choose the value supported by the verified
quote; its own quote is verified again deterministically. Agreed values are kept as is.
Output: coding/resolved/<arxiv>.json and coding/final.json (same shape as *_verified.json)."""
import json, sys, time, pathlib, concurrent.futures as cf
import os
sys.path.insert(0, os.environ.get("RESEARCHOS_ROOT", "."))  # model-call wrappers; see README "Re-running the model calls"
import boto3, botocore.config
from researchos.security.policy import assert_allowed, wrap_untrusted, INJECTION_NOTICE
from code_reports import pages, HERE
from verify_quotes import norm, found
from agreement import FIELDS

MODEL = "us.xai.grok-4.7"
LOW = {"seeds": "NR", "rerun": "NR", "scores_copied": "NR", "third_party": "NO", "data_disclosure": "NONE",
       "tokens_disclosed": "N", "compute_disclosed": "N"}
VALS = {"seeds": ["NR", "ONE", "MULTI", "VAR"], "rerun": ["YES", "NO", "MIXED", "NR"], "scores_copied": ["YES", "NO", "MIXED", "NR"],
        "third_party": ["YES", "NO"], "data_disclosure": ["FULL", "PARTIAL", "NONE"], "tokens_disclosed": ["Y", "N"],
        "compute_disclosed": ["Y", "N"]}
SYSTEM = (open(pathlib.Path(__file__).parent / "coder_instructions.md").read().strip() +
          "\n\nRESOLUTION TASK: two independent coders disagreed on the items listed. For each item choose the value "
          "that the report text supports, applying the definitions above strictly. Give a verbatim quote (8-40 words, one "
          "page) and its page for any value other than the lowest level. If neither coder's value is supported, give the "
          "correct value. For 'unaligned' claims decide keep=true only if it is an ARCH/TRAIN novelty claim the authors "
          "state as their own contribution, and code its ablation.")
I = lambda: {"type": "integer"}; S = lambda: {"type": "string"}
def obj(p): return {"type": "object", "additionalProperties": False, "properties": p, "required": list(p)}
SCHEMA = obj({
    "fields": {"type": "array", "items": obj({"field": {"type": "string", "enum": FIELDS}, "value": S(), "quote": S(), "page": I(), "reason": S()})},
    "claims": {"type": "array", "items": obj({"item_id": S(), "keep": {"type": "boolean"},
               "ablation": {"type": "string", "enum": ["YES", "PARTIAL", "NO"]}, "quote": S(), "page": I(), "reason": S()})},
})

def build(arxiv, d, A, B):
    items, cited = [], set()
    for f in FIELDS:
        if f in d:
            ea, eb = A[f + "_evidence"], B[f + "_evidence"]
            items.append(f"FIELD {f}: coder1={d[f]['A']} (p.{ea['page']}: \"{ea['quote']}\")  coder2={d[f]['B']} (p.{eb['page']}: \"{eb['quote']}\")")
            cited |= {ea["page"], eb["page"]}
    cl = []
    for n, pr in enumerate(d.get("ablation", [])):
        a, b = pr["A"], pr["B"]; iid = f"pair{n}"; cl.append((iid, "pair", a, b))
        items.append(f"CLAIM {iid} (both coders list it): \"{a['claim']}\" p.{a['page']} | coder1 ablation={a['ablation']} "
                     f"(p.{a['ablation_page']}: \"{a['ablation_quote']}\") | coder2 ablation={b['ablation']} (p.{b['ablation_page']}: \"{b['ablation_quote']}\")")
        cited |= {a["page"], a["ablation_page"], b["ablation_page"]}
    un = d.get("unaligned_arch_train", {})
    for src in ("A_only", "B_only"):
        for n, c in enumerate(un.get(src, [])):
            iid = f"{src}{n}"; cl.append((iid, src, c, None))
            items.append(f"CLAIM {iid} (listed by one coder only): [{c['category']}] \"{c['claim']}\" p.{c['page']} quote: \"{c['quote']}\" "
                         f"| that coder's ablation={c['ablation']} (p.{c['ablation_page']}: \"{c['ablation_quote']}\")")
            cited |= {c["page"], c["ablation_page"]}
    P = pages(arxiv); keep = sorted({p + k for p in cited if p > 0 for k in (-1, 0, 1) if 1 <= p + k <= len(P)})
    body = "\n\n".join(f"=== PAGE {p} ===\n{P[p-1]}" for p in keep)
    prompt = (f"{INJECTION_NOTICE}\n\nReport arXiv:{arxiv}. Disagreements to resolve:\n" + "\n".join(items) +
              "\n\nPages cited by the coders (+-1):\n" + wrap_untrusted(body, f"arXiv:{arxiv}"))
    return prompt, cl

def call(prompt):
    c = boto3.client("bedrock-runtime", region_name="us-east-1",
                     config=botocore.config.Config(read_timeout=1800, retries={"max_attempts": 6, "mode": "adaptive"}))
    for k in range(4):
        try:
            r = c.converse(modelId=MODEL, system=[{"text": SYSTEM}], messages=[{"role": "user", "content": [{"text": prompt}]}],
                           inferenceConfig={"maxTokens": 16000},
                           toolConfig={"tools": [{"toolSpec": {"name": "emit_resolution", "description": "Return the resolution.",
                                                               "inputSchema": {"json": SCHEMA}}}],
                                       "toolChoice": {"tool": {"name": "emit_resolution"}}})
            tu = [b["toolUse"]["input"] for b in r["output"]["message"]["content"] if "toolUse" in b]
            if tu: return tu[0], {"model": MODEL, "usage": r["usage"], "stop_reason": r.get("stopReason")}
        except Exception as e:
            if k == 3: raise
        time.sleep(30 * (k + 1))
    raise RuntimeError("no tool output")

def resolve_one(arxiv, d, A, B):
    out = HERE / "coding" / "resolved" / f"{arxiv}.json"
    if out.exists(): return json.load(open(out))
    assert_allowed(["OPEN"], "external_llm")
    prompt, cl = build(arxiv, d, A, B)
    res, info = call(prompt)
    out.parent.mkdir(parents=True, exist_ok=True)
    rec = {"arxiv": arxiv, "resolution": res, "items": [[i, k] for i, k, *_ in cl], "run_info": info}
    out.write_text(json.dumps(rec, indent=1, ensure_ascii=False)); return rec

if __name__ == "__main__":
    A = json.load(open("coding/A_verified.json"))["reports"]; B = json.load(open("coding/B_verified.json"))["reports"]
    D = json.load(open("disagreements.json"))
    with cf.ThreadPoolExecutor(3) as ex:
        R = dict(zip(D, ex.map(lambda i: resolve_one(i, D[i], A[i], B[i]), D)))
    final, stats = {}, {"fields_resolved": 0, "field_quote_fail": 0, "claims_resolved": 0, "claim_quote_fail": 0}
    for i in sorted(A):
        a, d = A[i], D.get(i, {}); f = {k: a[k] for k in ("model", "is_release_report", "comparators", "renames")}
        f["renames_B"] = B[i]["renames"]
        for fld in FIELDS: f[fld] = a[fld]                     # agreed (or A where B is missing; overwritten below)
        claims = []; aligned_ids = {}
        # aligned agreeing pairs: keep A's record
        from agreement import align
        pairs, _, _ = align(a["claims"], B[i]["claims"])
        for x, y in pairs:
            if x["ablation"] == y["ablation"]: claims.append({**x, "source": "agreed"})
        claims += [{**c, "source": "A_nonARCH"} for c in a["claims"] if c["category"] not in ("ARCH", "TRAIN")]
        if i in R:
            P = [norm(p) for p in pages(i)]
            for r in R[i]["resolution"]["fields"]:
                fld, val = r["field"], r["value"]
                if fld not in d or val not in VALS[fld]: continue
                stats["fields_resolved"] += 1
                if val != LOW[fld] and not found(r["quote"], r["page"], P): val = LOW[fld]; stats["field_quote_fail"] += 1
                f[fld] = val
            items = {iid: (kind, x, y) for iid, kind, x, y in build(i, d, a, B[i])[1]}
            for r in R[i]["resolution"]["claims"]:
                if r["item_id"] not in items or not r["keep"]: continue
                kind, x, _ = items[r["item_id"]]; ab = r["ablation"]; stats["claims_resolved"] += 1
                if ab in ("YES", "PARTIAL") and not found(r["quote"], r["page"], P): ab = "NO"; stats["claim_quote_fail"] += 1
                claims.append({**x, "ablation": ab, "source": f"resolved:{kind}"})
        f["claims"] = claims; final[i] = f
    json.dump({"coder": "final", "stats": stats, "reports": final}, open("coding/final_verified.json", "w"), indent=1)
    print(len(final), "reports;", stats)
