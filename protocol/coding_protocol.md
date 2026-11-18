# Step 3 protocol: novelty-claim coding of release reports (frozen 2026-11-14, before any report was read)

## Sampling frame
- The 171 causal-LM architectures in `discovery/timeline.json` (HF transformers commit 0d7a621, 2026-11-13).
- Report for each architecture = the FIRST arXiv identifier linked in its `docs/source/en/model_doc/<model>.md`
  (huggingface.co/papers/<id> or arxiv.org/abs|pdf/<id>). The library documentation, not us, names the report.
- Eligible: an arXiv id exists; the arXiv title or abstract names the model or its family (metadata check only,
  done before reading the body); report dated 2020-01-01 or later. One report per arXiv id (architectures that
  share a report, e.g. dense and MoE variants, count once; the earliest-added architecture keeps it).
- Not eligible and recorded: no arXiv link (vendor blog only), link is to a component paper (e.g. RoPE) rather
  than the release report, withdrawn paper.

## Sample
- Target n = 40. Stratified by year the report appeared on arXiv: 2020-2022, 2023, 2024, 2025, 2026.
- Allocation proportional to eligible counts per stratum, minimum 4 per stratum (or all if fewer).
- Within stratum: sort eligible arXiv ids, draw with `random.Random(20261114).sample`.
- No replacement after seeing content. A drawn report that turns out ineligible on reading (e.g. not a model
  release) is recorded as such and replaced by the next draw from the same stratum seed sequence.

## Licence gate (CLAUDE.md)
- Full text only from arXiv (the reports are arXiv preprints). Licence read from arXiv OAI-PMH (`arXiv` metadata
  format). arXiv-hosted texts are OPEN under `researchos/security/policy.py::classify_license`; CC licences recorded.
- Any report whose licence cannot be read is coded locally (rule-based counts only), not sent to a model.

## Coding scheme (per report)
- C1 Claimed novelties: each contribution stated in the abstract or the contribution list/introduction, verbatim
  quote + page. Category: ARCH (layer/attention/norm/position/MoE design), DATA, SCALE, TRAIN (optimizer, schedule,
  stability), POST (SFT/RL/preference), TOK (tokenizer), CTX (long context), EFF (inference/infra), EVAL, OTHER.
- C2 Ablation, per ARCH/TRAIN claim: YES = controlled comparison with vs without at matched other settings;
  PARTIAL = comparison exists but confounded (different size/data/tokens) or only loss curves without a table;
  NO = none.
- C3 Seeds: number of independent training runs/seeds stated for any ablation or main result
  (NR = not reported, 1, >=2, or variance/CI reported).
- C4 Baselines: COMPARATORS = models in the main results table; RERUN = authors re-evaluated comparators under the
  same harness (YES/NO/MIXED/NR); SCORES_COPIED = scores taken from other reports (YES/NO/MIXED/NR);
  THIRD_PARTY = any independent evaluation (leaderboard run by others, external harness) reported (YES/NO).
- C5 Disclosure: training-data composition (FULL/PARTIAL/NONE), token count (Y/N), compute (Y/N).
- C6 New names for existing components: verbatim quote where a known technique is given a new name.
- Every coded value with a verbatim quote and page; quotes verified deterministically against the PDF text.
  A value without a verified quote is set to NR.

## Coders and agreement
- Coder A: Claude (claude CLI, no tools), coder B: Codex (subscription), independent, same prompt, same text.
- Agreement: Cohen's kappa per field on C2, C3, C4.RERUN, C5; disagreements resolved by a third pass that sees
  both codings and the quotes; the resolution rule is "the value supported by the verified quote".
- Model output is a proposal; the quote check is the authority (invariant 4).

## What would falsify the thesis
- Majority of ARCH claims with YES ablations and >=2 seeds, and majority of reports re-running comparators under
  a shared harness. Reported as is, whatever the result.
