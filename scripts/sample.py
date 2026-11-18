"""Step 3 sample (coding_protocol.md): apply metadata overrides, stratify by arXiv-id year, draw seed 20261114."""
import json, random, collections
rows = json.load(open("eligibility_auto.json"))
OVERRIDE = {  # metadata-only corrections of the automatic name match, decided before any body was read
    "gpt_neox": ("ELIGIBLE", "title names GPT-NeoX-20B; auto match missed it because of the hyphen"),
    "gemma3n": ("NOT_ELIGIBLE", "component paper (LAuReL residual layer); auto hit was the letter 'n'"),
    "glm_moe_dsa": ("NOT_ELIGIBLE", "component paper (IndexCache sparse-attention reuse), not a release report"),
}
for r in rows:
    if r["model"] in OVERRIDE:
        r["status"], r["reason"] = OVERRIDE[r["model"]]; r["override"] = True
    elif r["status"] == "ELIGIBLE_AUTO":
        r["status"] = "ELIGIBLE"
json.dump(rows, open("eligibility.json", "w"), indent=1)
elig = [r for r in rows if r["status"] == "ELIGIBLE"]
def stratum(y): return "2020-2022" if y <= 2022 else str(y)
S = collections.defaultdict(list)
for r in elig: S[stratum(r["year"])].append(r["arxiv"])
for k in S: S[k].sort()
N, total = 40, len(elig)
alloc = {k: min(len(v), max(4, round(N * len(v) / total))) for k, v in S.items()}
# adjust to N by largest-remainder on strata with spare capacity
while sum(alloc.values()) != N:
    d = 1 if sum(alloc.values()) < N else -1
    cand = [k for k in S if (alloc[k] < len(S[k]) if d > 0 else alloc[k] > 4)]
    if not cand: break
    k = max(cand, key=lambda k: (N * len(S[k]) / total - alloc[k]) * d); alloc[k] += d
rng = random.Random(20261114); out = {}
for k in sorted(S):
    order = rng.sample(S[k], len(S[k]))   # full permutation: first alloc[k] drawn, rest = replacement queue
    out[k] = {"eligible": len(S[k]), "n": alloc[k], "drawn": order[:alloc[k]], "replacement_queue": order[alloc[k]:]}
by_id = {r["arxiv"]: r["model"] for r in elig}
json.dump({"seed": 20261114, "N_target": N, "N_eligible": total, "strata": out, "model_of": by_id},
          open("sample.json", "w"), indent=1)
cnt = collections.Counter(r["status"] for r in rows)
print(dict(cnt), "eligible:", total)
for k, v in out.items(): print(k, v["eligible"], "->", v["n"], [by_id[i] for i in v["drawn"]])
