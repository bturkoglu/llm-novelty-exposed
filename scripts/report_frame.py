"""Step 3 frame: first arXiv id in each causal-LM model_doc page (coding_protocol.md)."""
import json, re, sys, pathlib
DOC = pathlib.Path(sys.argv[1])  # transformers/docs/source/en/model_doc @0d7a621
t = json.load(open("timeline.json"))
pat = re.compile(r"(?:huggingface\.co/papers/|arxiv\.org/(?:abs|pdf)/)(\d{4}\.\d{4,5})")
rows = []
for m in sorted(t, key=lambda x: (x["added"] or "9999", x["model"])):
    f = DOC / f"{m['model']}.md"
    ids = pat.findall(f.read_text()) if f.exists() else []
    rows.append({"model": m["model"], "added": m["added"], "doc": f.exists(), "arxiv": ids[0] if ids else None,
                 "all_ids": list(dict.fromkeys(ids))[:5]})
json.dump(rows, open("report_frame_raw.json", "w"), indent=1)
print(len(rows), "with arxiv:", sum(1 for r in rows if r["arxiv"]), "no doc:", sum(1 for r in rows if not r["doc"]))
print("distinct ids:", len({r['arxiv'] for r in rows if r['arxiv']}))
