"""Download the 40 sampled reports from arXiv only (licence gate per coding_protocol.md); page text via pdftotext.
Untrusted data: stored under _cache/reports, never executed. 4 s pacing."""
import json, time, ssl, subprocess, urllib.request, pathlib, certifi
ctx = ssl.create_default_context(cafile=certifi.where())
s = json.load(open("sample.json")); meta = json.load(open("arxiv_meta.json"))
d = pathlib.Path("_cache/reports"); man = []
ids = [i for v in s["strata"].values() for i in v["drawn"]]
for i in ids:
    pdf, txt = d / f"{i}.pdf", d / f"{i}.txt"
    if not pdf.exists():
        req = urllib.request.Request(f"https://arxiv.org/pdf/{i}", headers={"User-Agent": "ResearchOS/0.1 (academic research)"})
        for k in range(4):
            try: pdf.write_bytes(urllib.request.urlopen(req, context=ctx, timeout=120).read()); break
            except Exception as e: print("retry", i, e); time.sleep(10 * (k + 1))
        time.sleep(4)
    ok = pdf.exists() and pdf.read_bytes()[:4] == b"%PDF"
    if ok and not txt.exists():
        subprocess.run(["pdftotext", "-layout", str(pdf), str(txt)], check=False)
    pages = txt.read_text(errors="replace").count("\f") if txt.exists() else 0
    man.append({"arxiv": i, "model": s["model_of"][i], "pdf_ok": ok, "pages": pages,
                "license": meta[i]["license"], "access_class": "OPEN", "source": "arxiv"})
    print(i, s["model_of"][i], ok, pages, flush=True)
json.dump(man, open("reports_manifest.json", "w"), indent=1)
