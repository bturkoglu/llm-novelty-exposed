"""Figure 1 (redrawn 2026-11-14): causal-LM architectures added to HF transformers per year (to 13 Nov 2026),
share taking >=2 of 3 core blocks from another model, and count taking >=1 core block from Llama. From timeline.json."""
import json, collections as C
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
tl = json.load(open("timeline.json")); by = C.defaultdict(list)
for r in tl:
    if r["added"] and r["added"][:4] >= "2020": by[r["added"][:4]].append(r)
ys = sorted(by); n = [len(by[y]) for y in ys]
b2 = [sum(r["n_core_borrowed"] >= 2 for r in by[y]) for y in ys]
ll = [sum(1 for r in by[y] if "llama" in r["core_borrowed"].values()) for y in ys]
lab = [y if y != "2026" else "2026\n(to 13 Nov)" for y in ys]; x = range(len(ys))
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9})
fig, ax = plt.subplots(figsize=(6.6, 4.3))
ax.bar(x, n, color="#d9d9d9", width=0.7, label="Architectures added in that year")
ax.bar(x, b2, color="#4f7fab", width=0.7, label="  of which take at least 2 of 3 core blocks from another model")
ax.plot(x, ll, "o-", color="#b8463f", ms=4, lw=1.4, label="Architectures taking at least 1 core block from Llama")
for i, (a, b) in enumerate(zip(n, b2)): ax.text(i, a + 0.9, f"{b}/{a}\n({b/a:.0%})", ha="center", va="bottom", fontsize=7.5, linespacing=0.95)
k = ys.index("2024"); ax.axvline(k - 0.5, color="#555", ls="--", lw=0.8)
ax.text(k - 0.58, 34, "from about 2024 the library\nwrites new models as edits\nof older ones (modular files)", fontsize=7, va="top", ha="right", color="#333")
ax.set_xticks(list(x)); ax.set_xticklabels(lab); ax.set_ylabel("Number of architectures"); ax.set_ylim(0, max(n) * 1.15)
ax.legend(fontsize=7.5, frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=1); ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout(); fig.savefig("../fig_timeline_core_blocks.png", dpi=300)
print(dict(zip(ys, zip(n, b2, ll))), "llama total", sum(ll))
