"""Verify every reference the paper will cite (invariant 2). arXiv ids via arXiv OAI-PMH; DOIs via Crossref;
references without a known id via Crossref bibliographic search, accepted only on title match (>= 0.9 word overlap).
Output: refs_verified.json (+ printed table). Unverified refs must not be cited."""
import json, re, sys, time, ssl, urllib.request, pathlib, xml.etree.ElementTree as ET, certifi
import os
sys.path.insert(0, os.environ.get("RESEARCHOS_ROOT", "."))  # model-call wrappers; see README "Re-running the model calls"
from researchos.search.crossref import Crossref, parse_item
ctx = ssl.create_default_context(cafile=certifi.where()); cache = pathlib.Path("_cache/arxiv_oai")
NS = {"a": "http://arxiv.org/OAI/arXiv/"}
cr = Crossref(cache_dir=pathlib.Path("_cache/crossref"))
REFS = [  # key, id (arxiv:/doi:/title:), expected title words (for the check)
 ("sorensen2015", "doi:10.1111/itor.12001", "Metaheuristics the metaphor exposed"),
 ("weyland2010", "title:A rigorous analysis of the harmony search algorithm", "A rigorous analysis of the harmony search algorithm"),
 ("camacho2023", "title:Exposing the grey wolf, moth-flame, whale, firefly, bat, and antlion algorithms: six misleading optimization techniques inspired by bestial metaphors", "Exposing the grey wolf moth-flame whale firefly bat and antlion algorithms"),
 ("vaswani2017", "arxiv:1706.03762", "Attention Is All You Need"),
 ("devlin2019", "arxiv:1810.04805", "BERT"),
 ("brown2020", "arxiv:2005.14165", "Language Models are Few-Shot Learners"),
 ("kaplan2020", "arxiv:2001.08361", "Scaling Laws for Neural Language Models"),
 ("hoffmann2022", "arxiv:2203.15556", "Training Compute-Optimal Large Language Models"),
 ("ouyang2022", "arxiv:2203.02155", "Training language models to follow instructions with human feedback"),
 ("shazeer2017", "arxiv:1701.06538", "Outrageously Large Neural Networks"),
 ("fedus2022", "arxiv:2101.03961", "Switch Transformers"),
 ("snell2024", "arxiv:2408.03314", "Scaling LLM Test-Time Compute"),
 ("touvron2023", "arxiv:2302.13971", "LLaMA: Open and Efficient Foundation Language Models"),
 ("narang2021", "arxiv:2102.11972", "Do Transformer Modifications Transfer Across Implementations and Applications"),
 ("laufer2025", "arxiv:2508.06811", ""), ("hugginggraph2025", "arxiv:2507.14240", ""),
 ("disruptive2026", "arxiv:2604.11618", ""), ("polysemy2026", "arxiv:2604.21043", ""), ("narang_update2026", "arxiv:2605.20798", ""),
 ("lipton2018", "arxiv:1807.03341", "Troubling Trends in Machine Learning Scholarship"),
 ("dodge2019", "arxiv:1909.03004", "Show Your Work"),
 ("bouthillier2021", "arxiv:2103.03098", "Accounting for Variance in Machine Learning Benchmarks"),
 ("melis2018", "arxiv:1707.05589", "On the State of the Art of Evaluation in Neural Language Models"),
 ("wolf2020", "arxiv:1910.03771", "Transformers"), ("qwen2_2024", "arxiv:2407.10671", "Qwen2 Technical Report"),
 ("qwen3_2025", "arxiv:2505.09388", "Qwen3 Technical Report"), ("olmo2_2025", "arxiv:2501.00656", "OLMo 2"),
 ("mistral2023", "arxiv:2310.06825", "Mistral 7B"), ("falcon2023", "arxiv:2311.16867", "The Falcon Series of Open Language Models"),
 ("gemma2024", "arxiv:2403.08295", "Gemma"), ("mamba2023", "arxiv:2312.00752", "Mamba"),
 ("dehghani2023", "arxiv:2302.05442", "Scaling Vision Transformers to 22 Billion Parameters"),
 ("ainslie2023", "arxiv:2305.13245", "GQA"),
 ("mitchell2019", "arxiv:1810.03993", "Model Cards for Model Reporting"),
 ("gebru2021", "arxiv:1803.09010", "Datasheets for Datasets"),
 ("pineau2021", "arxiv:2003.12206", "Improving Reproducibility in Machine Learning Research"),
 ("child2019", "arxiv:1904.10509", "Generating Long Sequences with Sparse Transformers"),
 ("beltagy2020", "arxiv:2004.05150", "Longformer"), ("shazeer2019", "arxiv:1911.02150", "Fast Transformer Decoding"),
 ("shazeer2020", "arxiv:2002.05202", "GLU Variants Improve Transformer"), ("mamba2_2024", "arxiv:2405.21060", "Transformers are SSMs"),
 ("falconmamba2024", "arxiv:2410.05355", "Falcon Mamba"),
]
W = lambda s: set(re.findall(r"[a-z0-9]+", s.lower()))
def arxiv(i):
    f = cache / f"{i}.xml"
    if not f.exists():
        url = f"https://export.arxiv.org/oai2?verb=GetRecord&identifier=oai:arXiv.org:{i}&metadataPrefix=arXiv"
        f.write_bytes(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "ResearchOS/0.1 (academic research)"}), context=ctx, timeout=60).read()); time.sleep(3.5)
    m = ET.parse(f).getroot().find(".//a:arXiv", NS)
    if m is None: return None
    au = [(a.findtext("a:keyname", namespaces=NS) or "") for a in m.findall(".//a:author", NS)]
    return {"title": " ".join(m.findtext("a:title", namespaces=NS).split()), "authors": au[:6], "n_authors": len(au),
            "year": int(m.findtext("a:created", namespaces=NS)[:4]), "doi": m.findtext("a:doi", default="", namespaces=NS), "arxiv": i, "registry": "arxiv"}
out = {}
for key, ident, exp in REFS:
    kind, val = ident.split(":", 1); rec = None
    if kind == "arxiv": rec = arxiv(val)
    elif kind == "doi":
        it = cr.work(val); rec = parse_item(it) if it else None
    else:
        res = cr.search("ref", val, max_results=5)
        for r in res.records:
            if len(W(val) & W(r["title"])) / max(1, len(W(val))) >= 0.9: rec = r; break
    if rec and kind != "arxiv":
        rec = {"title": rec["title"], "authors": [a["family"] for a in rec["authors"]][:6], "n_authors": len(rec["authors"]),
               "year": rec["year"], "venue": rec["venue"], "volume": rec["volume"], "pages": rec["pages"], "doi": rec["doi"], "registry": "crossref"}
    ok = bool(rec) and (not exp or len(W(exp) & W(rec["title"])) / len(W(exp)) >= 0.8)
    out[key] = {"id": ident, "verified": ok, **(rec or {})}
    print(f"{'OK ' if ok else 'XX '} {key:18} {(rec or {}).get('year')} {', '.join((rec or {}).get('authors', [])[:2]):24} | {(rec or {}).get('title','')[:70]} | {(rec or {}).get('venue') or ''} {(rec or {}).get('doi') or ''}")
json.dump(out, open("refs_verified.json", "w"), indent=1, ensure_ascii=False)
