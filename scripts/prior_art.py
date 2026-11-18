"""Prior-art search for 'LLMs - the novelty exposed'. Public scholarly APIs only; cached."""
import json, sys
from pathlib import Path
import os; sys.path.insert(0, os.environ.get("RESEARCHOS_ROOT", "."))
from researchos.search.registry import get
from researchos.util import load_dotenv; load_dotenv()

CACHE = Path(__file__).parent / "_cache"
OUT = Path(__file__).parent / "prior_art_raw.json"
oa, s2, ax = get("openalex", CACHE), get("semantic_scholar", CACHE), get("arxiv", CACHE)

LLM = '("large language model" OR "large language models" OR LLM OR LLMs OR "foundation model" OR "foundation models" OR transformer OR "language model" OR "language models" OR "deep learning")'
OA_Q = {
  "Q1_novelty_critique": LLM + ' AND (hype OR "novelty claims" OR "incremental" OR "troubling trends" OR "reality check" OR "exposed" OR "illusion of progress" OR "marketing")',
  "Q2_arch_variants": '(transformer OR "language model") AND ("architectural modifications" OR "architecture modifications" OR "architectural variants" OR "do not transfer" OR "architectural convergence" OR "same architecture")',
  "Q3_hf_lineage": '("Hugging Face" OR HuggingFace) AND (lineage OR "family tree" OR "derivative models" OR "supply chain" OR "model ecosystem" OR "fine-tuned derivatives" OR merging)',
  "Q4_leaderboard": LLM + ' AND (leaderboard OR "benchmark contamination" OR "data contamination" OR "benchmark saturation") AND (illusion OR gaming OR overfitting OR critique OR inflated)',
  "Q5_openwashing": LLM + ' AND ("open-washing" OR openwashing OR "transparency index" OR "technical report" OR "release practices" OR "documentation practices")',
  "Q6_ml_rigor": '("machine learning" OR "deep learning" OR "neural network") AND ("troubling trends" OR "reality check" OR "progress is illusory" OR "are we really making much progress" OR "worrying analysis" OR "illusion of progress")',
  "Q7_metaphor_ai": '(anthropomorphism OR "misleading terminology" OR "reasoning claims" OR "AI hype") AND ' + LLM,
}
S2_Q = {
  "S1": '("large language models" | LLM) + (hype | novelty | "reality check" | "troubling trends" | exposed)',
  "S2": 'transformer + ("architectural modifications" | "do not transfer" | "architectural variants")',
  "S3": '"Hugging Face" + (lineage | "family tree" | "supply chain" | derivatives)',
  "S4": '("language models" | LLM) + (leaderboard | contamination) + (illusion | gaming | inflated)',
  "S5": '("language models" | LLM) + ("open-washing" | openwashing | "transparency index")',
}
AX_Q = {
  "A1": 'ti:"reality check" AND (abs:"language model" OR abs:transformer)',
  "A2": 'ti:exposed AND (abs:"language model" OR abs:LLM)',
  "A3": 'ti:hype AND (abs:"language model" OR abs:LLM)',
  "A4": 'abs:"Hugging Face" AND (abs:lineage OR abs:"family tree" OR abs:"supply chain")',
  "A5": 'ti:illusion AND (ti:leaderboard OR ti:progress) AND abs:"language model"',
  "A6": 'abs:"architectural" AND abs:"open-weight" AND abs:"language models" AND (abs:comparison OR abs:convergence)',
}
res = {"openalex": {}, "s2": {}, "arxiv": {}, "citers_sorensen": [], "errors": []}
def keep(r):  # compact record
    return {k: r.get(k) for k in ("doi", "ids", "title", "year", "venue", "work_type", "abstract")} | {
        "cites": {k: v.get("value") for k, v in (r.get("metrics") or {}).items() if k.startswith("citation_count")}}
for q, s in OA_Q.items():
    try:
        r = oa.search(q, s, {"from_year": 2015}, max_results=200); res["openalex"][q] = {"total": r.total_hits, "records": [keep(x) for x in r.records]}
        print(q, "openalex total", r.total_hits, flush=True)
    except Exception as e: res["errors"].append([q, repr(e)]); print(q, "ERR", e)
for q, s in S2_Q.items():
    try:
        r = s2.search(q, s, {"from_year": 2015}, max_results=200); res["s2"][q] = {"total": r.total_hits, "records": [keep(x) for x in r.records]}
        print(q, "s2 total", r.total_hits, flush=True)
    except Exception as e: res["errors"].append([q, repr(e)]); print(q, "ERR", e)
import time
for q, s in AX_Q.items():
    time.sleep(6)
    try:
        r = ax.search(q, s, {}, max_results=100); res["arxiv"][q] = {"total": r.total_hits, "records": [keep(x) for x in r.records]}
        print(q, "arxiv total", r.total_hits, flush=True)
    except Exception as e: res["errors"].append([q, repr(e)]); print(q, "ERR", e)
# All works citing Sorensen 2015 (forward chaining), paged
try:
    w = oa.get_by_doi("10.1111/itor.12001"); wid = w["id"].rsplit("/", 1)[1]
    print("Sorensen cited_by_count (OpenAlex):", w.get("cited_by_count"))
    cursor = "*"
    while cursor:
        body = oa.get("/works", {"filter": f"cites:{wid}", "per-page": 200, "cursor": cursor,
                                  "select": "id,doi,title,publication_year,cited_by_count,abstract_inverted_index,primary_location,type"})
        if not body or not body.get("results"): break
        from researchos.search.openalex import parse_work
        res["citers_sorensen"] += [keep(parse_work(x)) for x in body["results"]]
        cursor = body["meta"].get("next_cursor")
    print("citers fetched:", len(res["citers_sorensen"]))
except Exception as e: res["errors"].append(["citers", repr(e)]); print("citers ERR", e)
json.dump(res, open(OUT, "w"), indent=1)
print("errors:", len(res["errors"]))
