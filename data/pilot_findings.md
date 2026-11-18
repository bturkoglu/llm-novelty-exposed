# Pilot findings (2026-11-14)

## A. HF Hub config census (hf_census.py, census_analysis.py)
- Listed 921 text-generation repos (top 400 by downloads, likes, trending; deduplicated). 614 public config.json fetched;
  88 gated (not fetched, by design); 218 without config.json (mostly GGUF quantizations).
- 379/921 repos are quantized copies; 539 declare a base_model (110 quantized, 35 finetune, 2 merge relation tags).
- 275 "original" releases with config (no base_model, not quantized):
  101 distinct architecture class names collapse to 45 component signatures
  (norm, activation, position, attention, dense/MoE, full/sliding/hybrid).
- Largest signature (44 releases): RMSNorm + gated-SiLU + RoPE + GQA + dense + full attention, shared by
  Llama, Qwen3, Qwen2, Mistral, Granite, Phi3, Ernie4.5, MiniCPM, HunYuan, Seed-OSS class names.
- Limitation: signature is heuristic from config keys; missing keys (defaults) produce "?" and inflate distinct signatures,
  so 45 is an upper bound. Sample biased to popular repos.

## B. transformers modular source (modular_inheritance.py; commit 0d7a621, 2026-11-13)
- 548 model dirs; 326 written as "modular" files (the library's own declaration of what a model borrows).
- Causal-LM modular models: 127. Of their 1,594 classes, 1,112 (70%) inherit from another model's class;
  505 (32%) are pure renames (class body is only `pass`/docstring).
- 67 causal-LM models inherit from Llama classes (incl. Qwen2/3, Mistral, Gemma, DeepSeek-V2/V3/V4, OLMo, Granite, Phi, GPT-OSS ...).
- Caveat: modular inheritance is a code-reuse choice by maintainers; it measures shared implementation,
  not identical behaviour. Weights, data and training differ (that is the thesis).

## C. Deconstruction case (Sörensen's harmony-search analogue)
- modular_qwen2.py: Qwen2Attention(LlamaAttention) differs by `bias=True` on q/k/v projections plus optional sliding window;
  Qwen2MLP(LlamaMLP); Qwen2ForCausalLM(LlamaForCausalLM) is a rename.
- modular_qwen3.py: Qwen3Attention(LlamaAttention) adds RMSNorm on q and k heads (QK-norm); MLP borrowed from Gemma.
- Wording for paper: "in the reference implementation, the architectural distance between X and Llama is N lines".
  Always add: the vendor's reported differences (data, tokenizer, post-training) are not visible in code — that opacity is the point.

## Next
1. Rerun arXiv/S2 prior-art queries (rate-limited) with longer pacing.
2. Clean signature: fill config defaults from transformers Config classes; extend to the whole modular corpus by release date (timeline figure: names per year vs new components per year).
3. Code novelty claims in ~40 release technical reports (category, ablation, seeds, baselines chosen by whom).
4. Verify all neighbour references (Crossref/arXiv) before citing.

## D. Timeline (timeline.py, derivative_declared.py, core_blocks.py, fig_timeline.py -> ../fig_timeline_core_blocks.png)
- 171 causal-LM architectures in HF transformers (commit 0d7a621), 164 with a "contributed to HF Transformers on" date.
- Strict measure = core blocks (Attention, MLP, DecoderLayer) taken from another model via modular inheritance
  or "# Copied from transformers.models.<other>" markers.
- >=1/3 core blocks borrowed: 78%; >=2/3: 60%; all 3: 30%.
- Share with >=2 borrowed, by year added: 2020 33% (3/9), 2021 14%, 2022 8%, 2023 13%, 2024 57% (17/30), 2025 81% (39/48), 2026 88% (38/43).
- Llama is the main lender (80 core blocks), then DeepSeek-V3 (13), Qwen3-MoE (12), Mistral (10). 2026: lender shifts from Llama
  to MoE templates (DeepSeek-V3, Qwen3-MoE) — template changes, pattern stays.
- Looser measure (any declared borrowing): 160/171 (93%); 2024–2026: 97–98%.
- CONFOUND: modular files were introduced in the library around 2024, so recent models are written as diffs by construction.
  Copied-from markers partly cover the older period, but the 2024 jump is partly a tooling effect. Must be said in the paper;
  robustness check: compare with config-signature census (A), which is tooling-independent.
