# The novelty exposed — data, coding and scripts

[![arXiv](https://img.shields.io/badge/arXiv-2611.20003-b31b1b.svg)](https://arxiv.org/abs/2611.20003)
[![Dataset on HF](https://img.shields.io/badge/%F0%9F%A4%97-Dataset-yellow)](https://huggingface.co/datasets/bturkoglu/llm-novelty-exposed)

Supplementary material for

> Bahaeddin Türkoğlu. **The novelty exposed: ablation, reproducibility and transparency in 40 technical reports of
> open-weight large language models (LLMs).** arXiv:2611.20003, 2026. https://arxiv.org/abs/2611.20003

The repository has everything needed to check or repeat the analysis: the sampling frame, the coding protocol
(written before any report was read), the raw and verified outputs of both coders and the resolver, and the scripts.
It is the same material as the arXiv ancillary files. See [`README_S1.md`](README_S1.md) for a file-by-file guide.

## What is in it

| File | Content |
|---|---|
| `Table_S1_sampling_frame.csv` | 171 causal LM architectures in Hugging Face `transformers` (commit 0d7a6219), eligibility and sampling |
| `Table_S2_coded_claims.csv` | 73 architectural/training novelty claims in the 40 reports, with page, verbatim quote and ablation level |
| `Table_S3_coded_reports.csv` | per-report coding: ablations, training runs, baseline reruns, data/token/compute disclosure |
| `protocol/` | coding protocol, the exact coder instructions, language-check verdicts |
| `coding/` | coder A (Claude Opus 5.5), coder B (GPT-6.1 Sol), resolver (Grok 4.7): raw outputs and script-verified versions |
| `data/` | frame, sample (seed 20261114), library census, code comparisons, agreement, reference checks |
| `scripts/` | the pipeline, in the order given in `README_S1.md` |

Report PDFs are not redistributed; each report is identified by its arXiv id (licences in `data/reports_manifest.json`).

## Checking the results (no network, no model calls)

The scripts were written for one flat working directory. `make_workdir.sh` rebuilds that layout in `./work`:

```sh
sh make_workdir.sh
cd work
python3 agreement.py              # Table A1: inter-coder agreement  -> agreement.json / agreement.md
python3 summarize_coding.py final # coding summary                  -> coding_summary_final.md
```

Both outputs are identical to the published files in `data/` (checked before release).

## Re-running the model calls

`code_reports.py` and `resolve.py` call the models through thin wrappers from the author's research tool
(ResearchOS: tool-less, isolated model calls plus a licence gate), which is not part of this release. Set
`RESEARCHOS_ROOT` to provide equivalent `researchos.llm.backends` and `researchos.security.policy` modules, or replace
the calls with your own client. All model outputs are included, so no call is needed to check any number in the paper.
The page-numbered report texts (`_cache/reports/<arxiv>.txt`) are rebuilt by `fetch_reports.py` from arxiv.org.

## Licence

Code: MIT (`LICENSE`). Data and tables: CC BY 4.0 (`LICENSE-DATA`). Quotes in Table S2 are short excerpts from the
cited reports, used for verification; copyright stays with their authors.

## Citation

```bibtex
@misc{turkoglu2026novelty,
  author        = {T{\"u}rko{\u{g}}lu, Bahaeddin},
  title         = {The novelty exposed: ablation, reproducibility and transparency in 40 technical reports of
                   open-weight large language models ({LLMs})},
  year          = {2026},
  eprint        = {2611.20003},
  archivePrefix = {arXiv},
  primaryClass  = {cs.CL},
  url           = {https://arxiv.org/abs/2611.20003}
}
```
