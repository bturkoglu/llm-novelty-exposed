"""Step 3 coding (coding_protocol.md). Two independent coders (A: claude -p, B: codex exec), same prompt, same
page-numbered text. Uses ResearchOS backends (tool-less, scrubbed env, empty cwd) and the licence policy gate.
Coder B runs on AWS Bedrock (OpenAI family, us.openai.gpt-6.1-sol) because the Codex subscription hit its usage
limit until 2026-11-16 (D-071); same system prompt, same text, same schema (forced tool call).
Usage: code_reports.py A|B [arxiv ...]   -> coding/<coder>/<arxiv>.json"""
import json, re, sys, pathlib, concurrent.futures as cf
import os
sys.path.insert(0, os.environ.get("RESEARCHOS_ROOT", "."))  # model-call wrappers; see README "Re-running the model calls"
from researchos.llm.backends import ClaudeCLI, CodexCLI
from researchos.security.policy import assert_allowed, wrap_untrusted, INJECTION_NOTICE

HERE = pathlib.Path(__file__).parent
E = lambda vals: {"type": "string", "enum": vals}
def obj(props): return {"type": "object", "additionalProperties": False, "properties": props, "required": list(props)}
QP = {"quote": {"type": "string"}, "page": {"type": "integer"}}
def coded(vals): return obj({"value": E(vals), **QP})
SCHEMA = obj({
    "is_release_report": {"type": "boolean"},
    "claims": {"type": "array", "items": obj({
        "claim": {"type": "string"}, "category": E(["ARCH", "DATA", "SCALE", "TRAIN", "POST", "TOK", "CTX", "EFF", "EVAL", "OTHER"]),
        **QP, "ablation": E(["YES", "PARTIAL", "NO", "NA"]), "ablation_quote": {"type": "string"}, "ablation_page": {"type": "integer"}})},
    "seeds": coded(["NR", "ONE", "MULTI", "VAR"]),
    "comparators": {"type": "array", "items": {"type": "string"}},
    "rerun": coded(["YES", "NO", "MIXED", "NR"]),
    "scores_copied": coded(["YES", "NO", "MIXED", "NR"]),
    "third_party": coded(["YES", "NO"]),
    "data_disclosure": coded(["FULL", "PARTIAL", "NONE"]),
    "tokens_disclosed": coded(["Y", "N"]),
    "compute_disclosed": coded(["Y", "N"]),
    "renames": {"type": "array", "items": obj({"new_name": {"type": "string"}, "existing_technique": {"type": "string"}, **QP})},
    "note": {"type": "string"},
})

def pages(arxiv):
    raw = (HERE / "_cache/reports" / f"{arxiv}.txt").read_text(errors="replace").split("\f")
    return [re.sub(r"[ \t]{2,}", "  ", p).strip() for p in raw]

def prompt(arxiv, model):
    body = "\n\n".join(f"=== PAGE {i} ===\n{p}" for i, p in enumerate(pages(arxiv), 1) if p)
    return (f"{INJECTION_NOTICE}\n\nReport: arXiv:{arxiv} (HF transformers architecture '{model}').\n"
            f"Code it per your instructions. Page numbers are the '=== PAGE n ===' markers.\n\n"
            + wrap_untrusted(body, f"arXiv:{arxiv}"))

BEDROCK_MODEL = "us.openai.gpt-6.1-sol"

def run_bedrock(p):
    import time, boto3, botocore.config
    from researchos.llm.agents import load_agent
    from researchos.util import now_iso, sha256_text
    agent = load_agent("novelty-coder")
    c = boto3.client("bedrock-runtime", region_name="us-east-1",
                     config=botocore.config.Config(read_timeout=1800, retries={"max_attempts": 6, "mode": "adaptive"}))
    for k in range(4):
        try:
            r = c.converse(modelId=BEDROCK_MODEL, system=[{"text": agent.body}],
                           messages=[{"role": "user", "content": [{"text": p}]}],
                           inferenceConfig={"maxTokens": 16000},
                           toolConfig={"tools": [{"toolSpec": {"name": "emit_coding", "description": "Return the coding.",
                                                               "inputSchema": {"json": SCHEMA}}}],
                                       "toolChoice": {"tool": {"name": "emit_coding"}}})
            break
        except Exception as e:
            if k == 3: raise
            time.sleep(30 * (k + 1))
    tu = [b["toolUse"]["input"] for b in r["output"]["message"]["content"] if "toolUse" in b]
    if not tu: raise RuntimeError(f"no tool output, stop={r.get('stopReason')}")
    return tu[0], {"backend": "bedrock_converse", "model": BEDROCK_MODEL, "agent": "novelty-coder",
                   "agent_version": agent.version, "prompt_sha256": sha256_text(p), "usage": r["usage"],
                   "stop_reason": r.get("stopReason"), "timestamp": now_iso()}

def run(coder, arxiv, model):
    out = HERE / "coding" / coder / f"{arxiv}.json"
    if out.exists(): return arxiv, "cached"
    man = {m["arxiv"]: m for m in json.load(open(HERE / "reports_manifest.json"))}
    assert_allowed([man[arxiv]["access_class"]], "external_llm")
    if coder == "A":
        b = ClaudeCLI(); b.cfg = {**b.cfg, "max_budget_usd_per_call": 6.0, "timeout_s": 1500}
        obj_, info = b.run("novelty-coder", prompt(arxiv, model), SCHEMA, model="opus")
    else:
        obj_, info = run_bedrock(prompt(arxiv, model))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"arxiv": arxiv, "model": model, "coding": obj_, "run_info": info}, indent=1, ensure_ascii=False))
    return arxiv, "ok"

if __name__ == "__main__":
    coder = sys.argv[1]; s = json.load(open(HERE / "sample.json"))
    ids = sys.argv[2:] or [i for v in s["strata"].values() for i in v["drawn"]]
    with cf.ThreadPoolExecutor(3) as ex:
        futs = {ex.submit(run, coder, i, s["model_of"][i]): i for i in ids}
        for f in cf.as_completed(futs):
            try: print(*f.result(), flush=True)
            except Exception as e: print(futs[f], "FAIL", str(e)[:300], flush=True)
