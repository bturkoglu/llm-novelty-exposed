"""arXiv OAI-PMH metadata (title, abstract, dates, licence) for frame ids. 3.5 s pacing, cached."""
import json, time, ssl, urllib.request, pathlib, xml.etree.ElementTree as ET, certifi
ctx = ssl.create_default_context(cafile=certifi.where())
cache = pathlib.Path("_cache/arxiv_oai"); cache.mkdir(parents=True, exist_ok=True)
NS = {"o": "http://www.openarchives.org/OAI/2.0/", "a": "http://arxiv.org/OAI/arXiv/"}
ids = sorted({r["arxiv"] for r in json.load(open("report_frame_raw.json")) if r["arxiv"]})
out = {}
for i in ids:
    f = cache / f"{i}.xml"
    if not f.exists():
        url = f"https://export.arxiv.org/oai2?verb=GetRecord&identifier=oai:arXiv.org:{i}&metadataPrefix=arXiv"
        req = urllib.request.Request(url, headers={"User-Agent": "ResearchOS/0.1 (academic research)"})
        for k in range(4):
            try:
                f.write_bytes(urllib.request.urlopen(req, context=ctx, timeout=60).read()); break
            except Exception as e:
                print("retry", i, e); time.sleep(10 * (k + 1))
        time.sleep(3.5)
    root = ET.parse(f).getroot(); m = root.find(".//a:arXiv", NS)
    if m is None: out[i] = {"error": "no record"}; continue
    g = lambda t: (m.findtext(f"a:{t}", default="", namespaces=NS) or "").strip()
    out[i] = {"title": " ".join(g("title").split()), "abstract": " ".join(g("abstract").split()),
              "created": g("created"), "license": g("license") or "arXiv-default-nonexclusive(absent tag)",
              "authors_n": len(m.findall(".//a:author", NS))}
json.dump(out, open("arxiv_meta.json", "w"), indent=1)
print(len(out), sum(1 for v in out.values() if "error" in v))
