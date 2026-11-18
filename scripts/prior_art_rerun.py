"""Rerun the rate-limited arXiv / Semantic Scholar queries of prior_art.py with slow pacing; merge into prior_art_raw.json."""
import json, sys, time
from pathlib import Path
import os; sys.path.insert(0, os.environ.get("RESEARCHOS_ROOT", "."))
from researchos.util import load_dotenv; load_dotenv()
from researchos.search.http import HttpClient
from researchos.search.arxiv import Arxiv
from researchos.search.semantic_scholar import SemanticScholar
import prior_art_queries as Q
CACHE = Path(__file__).parent / "_cache"; RAW = Path(__file__).parent / "prior_art_raw.json"
d = json.load(open(RAW))
ax = Arxiv(cache_dir=CACHE, client=HttpClient(min_interval_s=8, cache_dir=CACHE, timeout=60))
s2 = SemanticScholar(cache_dir=CACHE, client=HttpClient(min_interval_s=6, cache_dir=CACHE, timeout=60))
def keep(r):
    return {k: r.get(k) for k in ("doi", "ids", "title", "year", "venue", "work_type", "abstract")} | {
        "cites": {k: v.get("value") for k, v in (r.get("metrics") or {}).items() if k.startswith("citation_count")}}
for src, conn, qs, n in (("s2", s2, Q.S2_Q, 200), ("arxiv", ax, Q.AX_Q, 100)):
    for q, s in qs.items():
        if q in d[src]: continue
        for attempt in range(3):
            try:
                r = conn.search(q, s, {"from_year": 2015} if src == "s2" else {}, max_results=n)
                d[src][q] = {"total": r.total_hits, "records": [keep(x) for x in r.records]}
                print(src, q, "total", r.total_hits, flush=True); break
            except Exception as e:
                print(src, q, "retry", attempt, e, flush=True); time.sleep(90)
        json.dump(d, open(RAW, "w"), indent=1)
print("missing:", [q for q in Q.S2_Q if q not in d["s2"]] + [q for q in Q.AX_Q if q not in d["arxiv"]])
