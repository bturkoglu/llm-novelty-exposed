"""Step 3 descriptive summary from verified codings (single coder until B + resolution exist: PRELIMINARY)."""
import json, sys, collections
coder = sys.argv[1] if len(sys.argv) > 1 else "A"
V = json.load(open(f"coding/{coder}_verified.json"))["reports"]
s = json.load(open("sample.json"))
stratum = {i: k for k, v in s["strata"].items() for i in v["drawn"]}
G = collections.defaultdict(list)
for a, r in V.items(): G[stratum[a]].append(r); G["ALL"].append(r)
def pct(n, d): return f"{n}/{d} ({100*n/d:.0f}%)" if d else "-"
TAG = {"final": "FINAL: A (Claude Opus) + B (OpenAI gpt-6.1-sol) + resolver (xAI grok-4.7), quote-verified"}
lines = [f"# Step 3 coding summary — {TAG.get(coder, f'coder {coder} only, quote-verified, single coder')}\n"]
lines.append("| stratum | n | release rpt | ARCH/TRAIN claims | ablation YES | PARTIAL | NO | reports w/ seeds>=2 or var | rerun YES | scores copied YES/MIXED | 3rd-party | data FULL | tokens Y | compute Y | reports w/ rename |")
lines.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
for k in ["2020-2022", "2023", "2024", "2025", "2026", "ALL"]:
    R = G[k]; n = len(R)
    at = [c for r in R for c in r["claims"] if c["category"] in ("ARCH", "TRAIN")]
    ab = collections.Counter(c["ablation"] for c in at)
    lines.append(f"| {k} | {n} | {sum(r['is_release_report'] for r in R)} | {len(at)} | {pct(ab['YES'],len(at))} | {pct(ab['PARTIAL'],len(at))} | {pct(ab['NO'],len(at))} | "
                 f"{pct(sum(r['seeds'] in ('MULTI','VAR') for r in R),n)} | {pct(sum(r['rerun']=='YES' for r in R),n)} | "
                 f"{pct(sum(r['scores_copied'] in ('YES','MIXED') for r in R),n)} | {pct(sum(r['third_party']=='YES' for r in R),n)} | "
                 f"{pct(sum(r['data_disclosure']=='FULL' for r in R),n)} | {pct(sum(r['tokens_disclosed']=='Y' for r in R),n)} | "
                 f"{pct(sum(r['compute_disclosed']=='Y' for r in R),n)} | {pct(sum(bool(r['renames']) for r in R),n)} |")
cat = collections.Counter(c["category"] for r in V.values() for c in r["claims"])
lines.append(f"\nClaim categories (all reports): {dict(cat.most_common())}")
lines.append("\nRenames (verified quotes):")
for a, r in V.items():
    for x in r["renames"]: lines.append(f"- {r['model']} ({a}) p.{x['page']}: '{x['new_name']}' <- {x['existing_technique']}")
open(f"coding_summary_{coder}.md", "w").write("\n".join(lines)); print("\n".join(lines))
