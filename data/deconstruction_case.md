# Step 4 — Deconstruction case (Sörensen's harmony-search analogue)

Reproduce: `deconstruct.py _cache/tf qwen2 qwen3 mistral olmo2 gemma` -> `deconstruction.json`;
`config_defaults.py _cache/tf llama qwen2 qwen3 mistral olmo2 gemma` -> `config_defaults.json`.
Source: HF transformers commit 0d7a6219 (2026-11-13), generated standalone `modeling_<x>.py` vs `modeling_llama.py`,
class prefix renamed to Llama, docstrings/comments/imports/decorators stripped. Component refs verified on arXiv
(`component_refs.json`). Vendor quotes are verbatim from the arXiv PDFs (pdftotext), page = PDF page; all 9 checked by `verify_quotes.norm` (9/9).

## Raw distance (executable lines, includes plumbing noise)
| model | exec lines | Llama exec lines | differing lines (raw) |
|---|---|---|---|
| Qwen2 | 184 | 177 | 43 |
| Qwen3 | 186 | 177 | 41 |
| Mistral | 178 | 177 | 37 |
| OLMo 2 | 178 | 177 | 35 |
| Gemma | 189 | 177 | 56 |
Most raw lines are plumbing (mask construction, signatures, `...` vs `pass`). The computational differences are below.

## Computational differences from Llama, by hand from the diff (each is a line in `deconstruction.json`)
| model | difference in code | prior source of the component | vendor's own description (verbatim, page) |
|---|---|---|---|
| Qwen2 | q/k/v projections `bias=True` (Llama: config, default False) | QKV bias, Su 2023 (cited by vendor) | "we follow Qwen with the usage of SwiGLU ..., Rotary Positional Embeddings ..., QKV bias (Su, 2023) for attention, RMSNorm ... and pre-normalization" (2407.10671 p.4) |
| Qwen2 | optional sliding-window layers (default off: `use_sliding_window=False`) | Sparse Transformer 1904.10509; Longformer 2004.05150 | — |
| Qwen2 | GQA (config `num_key_value_heads`; Llama class already supports it) | Ainslie et al. 2305.13245 | "We adopt Grouped Query Attention (GQA, Ainslie et al., 2023) instead of conventional multi-head attention" (p.4) |
| Qwen3 | RMSNorm on per-head q and k (QK-norm); QKV bias removed | Dehghani et al. 2302.05442 | "we remove QKV-bias used in Qwen2 ... and introduce QK-Norm (Dehghani et al., 2023) to the attention mechanism to ensure stable training" (2505.09388 p.3) |
| Mistral | sliding-window causal mask | 1904.10509; 2004.05150 (vendor cites [6,3]) | "Mistral 7B leverages grouped-query attention (GQA) [1], and sliding window attention (SWA) [6, 3]." (2310.06825 p.1) |
| OLMo 2 | norm moved from sublayer input to output (post-sublayer RMSNorm); QK-norm over full q/k | Swin v2 2111.09883 (cited by vendor); Dehghani 2302.05442 | "Reordered norm: We normalize the outputs to the attention and feedforward (MLP) layers within each transformer block, instead of the inputs." (2501.00656 p.5); ablation shown (Fig. 7, p.15) |
| Gemma | RMSNorm weight parametrised as (1+w), zero init; embeddings scaled by sqrt(d); GeLU-tanh gate (config) ; tied embeddings | GLU variants 2002.05202; MQA 1911.02150 | "We also utilize several GeGLU Activations (Shazeer, 2020)" / MQA "based on ablations that showed that multi-query attention works well at small scales" (2403.08295 p.2) |

Config defaults (`config_defaults.json`): apart from Gemma's activation, all five use SiLU/SwiGLU, RMSNorm, RoPE;
differences are sizes (vocab 32k–256k, FFN width, layers), context length and the switches above.

## What the case shows (wording for the paper)
1. In the reference implementation each of these "new" architectures is Llama plus one to three switches, each
   switch a published component from 2019–2023 (QKV bias, sliding window, GQA/MQA, QK-norm, norm placement, GeGLU).
   Qwen3 = Llama + QK-norm (one RMSNorm on q and one on k: 2 added lines in __init__, 2 changed lines in forward),
   plus the same optional sliding-window switch as Qwen2, off by default.
2. Fairness: the vendors' architecture sections credit these components with citations (Qwen2 p.4, Qwen3 p.3,
   OLMo 2 p.5, Mistral p.1). The problem is not plagiarism of components; it is that what the reports present as
   their contribution (abstract/introduction claims, coded in Step 3) is carried by scale, data and post-training,
   which the code does not contain and which are rarely ablated (Step 3: ARCH/TRAIN ablation YES 26%) and seldom
   disclosed (training-data FULL 5%).
3. OLMo 2 is the counter-example worth naming: it cites the origin of each change and shows its effect (Fig. 7).
4. Caveat: modular/generated files are a maintainer choice; same code does not imply same model (weights, data,
   tokenizer and training differ). The claim is about the architectural novelty, not about model quality.
