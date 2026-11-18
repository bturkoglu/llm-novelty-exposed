# Step 5 — Novelty-claim reporting checklist (constructive part, draft v0.1)

Each item is tied to a Step 3 field and to the measured gap (final coding, n=40 reports; `coding_summary_final.md`).
Items are deliberately checkable by a reader or a script; none requires releasing weights or data.

| # | Item (the report states...) | Why (gap measured in Step 3 / Step 4) | Field |
|---|---|---|---|
| N1 | Each claimed architectural or training novelty is listed separately and labelled NEW (first proposed here) or ADOPTED (with the citation of its origin). | Step 4: every "new" switch in five reference implementations is a published 2019–2023 component; vendors cite them in the architecture section but the abstract/intro claim the model as new. | C1, C6 |
| N2 | For every NEW architectural/training element: a with/without comparison at matched size, data and tokens, in a table. | Only 26% of ARCH/TRAIN claims have a controlled ablation; 27% are confounded (different size/data/tokens); 47% have none. 2025: 11% controlled. | C2 |
| N3 | Number of independent runs (seeds) behind each ablation and main result, with spread. | 10% of reports state >=2 runs or variance; none after 2023 in the sample. | C3 |
| N4 | Comparator scores: which were re-run by the authors under one harness (named, with version and prompts) and which were copied from other reports. | 20% re-run comparators under the same harness; 55% copy some or all comparator scores. | C4 |
| N5 | At least one evaluation run by a party other than the authors, or the evaluation code and outputs released so that others can rerun it. | 20% report any third-party evaluation. | C4 |
| N6 | Training-data mixture: sources and proportions; number of pre-training tokens; compute (accelerator-hours or FLOPs). | Data mixture fully disclosed in 5%; tokens 72%; compute 30%. | C5 |
| N7 | When a known technique is given a new name, the existing name and origin are given in the same sentence. | Kept as a rule, not as a measured gap: the five candidate renames in the sample all disclose the known name or are new analogues (Falcon 'multigroup' cites Ainslie et al. in the same sentence). Practice to preserve. | C6 |
| N8 | A one-paragraph "difference from the closest public baseline" (e.g. Llama), naming the code-level changes. | Step 4: Qwen3 vs Llama = QK-norm (4 lines); Mistral = sliding-window mask; Qwen2 = QKV bias. Readers cannot see this from the reports. | Step 4 |

Good practice already in the sample (to cite as models, not only failures):
- OLMo 2 (2501.00656): cites the origin of each architectural change and shows its effect (Fig. 7, p.15). Tick N1, N2.
- Mistral 7B (2310.06825): re-runs all comparators with its own pipeline (coded rerun YES). Tick N4.
- OLMo 2 is outside the coded sample (eligible, not drawn); its evidence above is from its own report, checked by hand.

Scoring the 40 coded reports on the five items that the coding measures (N2 all ARCH/TRAIN claims with controlled
ablation; N3 seeds; N4 re-run comparators; N5 third-party evaluation; N6 data FULL + tokens + compute):
0 items 24/40, 1 item 10/40, 2 items 3/40, 3 items 3/40 (X-MOD 2205.06266, OLMoE 2409.02060, ELECTRA 2003.10555);
no report meets 4 or 5. The checklist is therefore not a description of current practice but a target.

Use: authors (self-check), reviewers (request), leaderboards and model hubs (structured fields).
Not claimed: that the checklist predicts model quality; that undisclosed reports are of low quality.
