# Supplementary Material S1 — "Large language models: the novelty exposed"

Everything needed to check or repeat the analysis. Report PDFs are not redistributed: each report is identified by
its arXiv identifier and was downloaded from arxiv.org (licences in data/reports_manifest.json).

## Readable tables
- Table_S1_sampling_frame.csv — the 171 causal language-model architectures in Hugging Face transformers
  (commit 0d7a6219, 13 Nov 2026): date added, first arXiv id linked in the documentation, eligibility decision and
  reason, stratum year, whether the report was sampled.
- Table_S2_coded_claims.csv — the 73 architectural/training novelty claims in the 40 coded reports: category,
  claim, page, verbatim quote, ablation level (YES controlled / PARTIAL confounded / NO), the quote supporting it,
  and whether the value came from both coders' agreement or from the third model.

## Protocol
- protocol/coding_protocol.md — sampling rule and coding scheme, written before any report was read.
- protocol/coder_instructions.md — the exact instructions given to both coders and the resolver.
- protocol/language_verdicts.md — how the automated language-check feedback was judged.

## Data (data/)
report_frame_raw.json, eligibility*.json, sample.json (seed 20261114), reports_manifest.json, arxiv_meta.json;
timeline.json, modular_inheritance.json, hf_census.json (library and Hub census); deconstruction.json and
config_defaults.json (code comparisons, Figure 2); agreement.json/.md (Table A1), checklist_scores.json (Table A2);
refs_verified.json, refs_published.json (every reference checked against arXiv/Crossref).

## Coding (coding/)
A/ (Claude Opus 5.5), B/ (OpenAI GPT-6.1 Sol), resolved/ (xAI Grok 4.7): raw outputs with quotes and run info.
A_verified.json, B_verified.json, final_verified.json: after the script check of every quote (verify_quotes.py).

## Scripts (scripts/), in order
1. report_frame.py <transformers>/docs/source/en/model_doc  -> frame
2. arxiv_meta.py, eligibility.py, sample.py, fetch_reports.py
3. code_reports.py A|B, verify_quotes.py A|B, agreement.py, resolve.py, summarize_coding.py final
4. core_blocks.py / modular_inheritance.py / fig_timeline.py <transformers root>  (Figure 1)
5. deconstruct.py, config_defaults.py, fig_qwen3_llama.py <transformers root>  (Figure 2)
6. verify_refs.py
The transformers source is a sparse checkout of https://github.com/huggingface/transformers at commit 0d7a6219.
Model calls need the claude CLI, AWS Bedrock access, or equivalent; outputs are included so no call is needed to check results.
