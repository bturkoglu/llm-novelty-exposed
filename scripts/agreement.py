"""Inter-coder agreement (coding_protocol.md): Cohen's kappa on verified codings of A and B.
Report-level fields: C3 seeds, C4 rerun/scores_copied/third_party, C5 data/tokens/compute.
C2 ablation: ARCH/TRAIN claims aligned across coders within a report (greedy, word-Jaccard >= 0.25 on the
claim text, same page +-2); kappa on aligned pairs; unaligned claims counted separately.
Output: agreement.json, agreement.md, disagreements.json (input to the resolution pass)."""
import json, re, collections

FIELDS = ["seeds", "rerun", "scores_copied", "third_party", "data_disclosure", "tokens_disclosed", "compute_disclosed"]

def kappa(pairs):
    n = len(pairs)
    if not n: return None, 0, None
    po = sum(a == b for a, b in pairs) / n
    ca, cb = collections.Counter(a for a, _ in pairs), collections.Counter(b for _, b in pairs)
    pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / n ** 2
    return (round((po - pe) / (1 - pe), 3) if pe < 1 else 1.0), n, round(po, 3)

W = lambda s: set(re.findall(r"[a-z0-9]{3,}", s.lower()))
def jac(a, b): A, B = W(a), W(b); return len(A & B) / max(1, len(A | B))

def align(ca, cb):
    ca = [c for c in ca if c["category"] in ("ARCH", "TRAIN")]; cb = [c for c in cb if c["category"] in ("ARCH", "TRAIN")]
    cand = sorted(((jac(x["claim"], y["claim"]), i, j) for i, x in enumerate(ca) for j, y in enumerate(cb)
                   if abs(x["page"] - y["page"]) <= 2), reverse=True)
    used_a, used_b, pairs = set(), set(), []
    for s, i, j in cand:
        if s < 0.25 or i in used_a or j in used_b: continue
        used_a.add(i); used_b.add(j); pairs.append((ca[i], cb[j]))
    return pairs, [c for i, c in enumerate(ca) if i not in used_a], [c for j, c in enumerate(cb) if j not in used_b]

if __name__ == "__main__":
    A = json.load(open("coding/A_verified.json"))["reports"]; B = json.load(open("coding/B_verified.json"))["reports"]
    ids = sorted(set(A) & set(B)); res, dis = {}, collections.defaultdict(dict)
    for f in FIELDS:
        pairs = [(A[i][f], B[i][f]) for i in ids]
        k, n, po = kappa(pairs); res[f] = {"kappa": k, "n": n, "agree": po}
        for i in ids:
            if A[i][f] != B[i][f]: dis[i][f] = {"A": A[i][f], "B": B[i][f]}
    abl, ua, ub = [], 0, 0
    for i in ids:
        pairs, oa, ob = align(A[i]["claims"], B[i]["claims"]); ua += len(oa); ub += len(ob)
        for x, y in pairs:
            abl.append((x["ablation"], y["ablation"]))
            if x["ablation"] != y["ablation"]:
                dis[i].setdefault("ablation", []).append({"A": x, "B": y})
        if oa or ob: dis[i]["unaligned_arch_train"] = {"A_only": oa, "B_only": ob}
    k, n, po = kappa(abl); res["C2_ablation_aligned"] = {"kappa": k, "n": n, "agree": po, "A_only": ua, "B_only": ub}
    json.dump(res, open("agreement.json", "w"), indent=1); json.dump(dis, open("disagreements.json", "w"), indent=1)
    md = ["| field | kappa | % agree | n |", "|---|---|---|---|"]
    md += [f"| {f} | {v['kappa']} | {v['agree']} | {v['n']} |" for f, v in res.items()]
    md.append(f"\nC2 unaligned ARCH/TRAIN claims: A-only {ua}, B-only {ub}. Reports with any disagreement: {len(dis)}/{len(ids)}")
    open("agreement.md", "w").write("\n".join(md)); print("\n".join(md))
