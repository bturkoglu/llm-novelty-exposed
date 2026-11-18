# Prior-art check (2026-11-14) — has "LLMs, the novelty exposed" been written?

Sources searched: OpenAlex (7 queries, title+abstract, 2015+), Semantic Scholar (S1, S5; S2–S4 rate-limited),
arXiv (A6 only; A1–A5 rate-limited, to rerun), forward citations of Sörensen 2015 (OpenAlex: 1,137 cited-by, 1,123 fetched).
Raw: prior_art_raw.json. Script: prior_art.py.

## Result
- No direct transfer found. Of 1,123 works citing Sörensen 2015, 70 mention ML/LLM; all are metaheuristic+ML
  applications or reviews, none applies the critique to LLM/deep-learning model releases.
- No paper found that combines (a) architecture census of released models, (b) coding of novelty claims in release
  reports, (c) Sörensen-style critique. Gap looks open. Caveat: arXiv/S2 runs incomplete.

## Closest neighbours (use as evidence, cite, differentiate)
| Work | What it shows | Role in our paper |
|---|---|---|
| Narang et al. 2021, EMNLP (arXiv 2102.11972) | most of 40+ transformer modifications do not transfer | Weyland-analogue |
| "Most Transformer Modifications Still Do Not Transfer at 1-3B" 2026 (arXiv 2605.20798) | 20 post-2021 mods, iso-compute, multi-seed: only 2 survive Bonferroni | strongest single evidence |
| Singh et al., The Leaderboard Illusion, NeurIPS 2025 (arXiv 2504.20879) | private variant testing, selective disclosure (27 Llama-4 variants) | up-the-wall game |
| Balloccu et al., Leak, Cheat, Repeat 2024 (arXiv 2402.03927) | contamination + evaluation malpractice in 255 papers | testing practice |
| What Carries Forward? 2026 (arXiv 2610.37465) | FMTI disclosure falls in 11/24 successive releases | opacity of real differences |
| Foundation Model Transparency Index 2023 | disclosure scoring | opacity |
| Strategic Competition and Convergence in LLM Leaderboards 2026 (arXiv 2611.09780) | crowded frontier, convergence | sameness, counter-view (not interchangeable) |
| Laufer et al. 2025 (arXiv 2508.06811); HuggingGraph (2507.14240); model-reuse studies | HF lineage / supply chain | lineage evidence |
| Lipton & Steinhardt 2019 Troubling Trends; Dacrema et al. 2019 "Are we really making much progress?" | ML-wide rigor critiques | genre precedent |
| Same Architecture, Different Capacity 2026 (arXiv 2605.21803) | same arch, optimizer changes capacity | counter-evidence: "only numbers" can matter |

To verify before citing: every item above via Crossref/DataCite/arXiv (invariant 2).

## Rerun 2026-11-14 (S2 S2–S4, arXiv A1–A5 completed; all queries now done)
Gap still open at code/architecture + novelty-claim level. New close neighbours:
| Work | What it shows | Role / how we differ |
|---|---|---|
| Identifying Disruptive Models in the Open-Source LLM Community 2026 (arXiv 2604.11618) | 2.56M HF models, lineage network, Model Disruption Index: most models consolidative, path-dependent | closest empirical neighbour; metadata lineage only, no code/architecture, no novelty-claim audit |
| Strategic Polysemy in AI Discourse 2026 (arXiv 2604.21043) | "glosslighting": technical terms with anthropomorphic pull (CoT, introspection, agent) | our "metaphor" section (vocabulary) |
| The ATOM Report 2026 (arXiv 2604.07190) | ~1.5K mainline open models, adoption, derivatives | ecosystem context |
| Founder effects ... open LLM families 2026 (arXiv 2603.22287) | lineage, capability propagation | lineage context |
| Can a Crow Hatch a Falcon? 2025 (arXiv 2504.19811) | lineage predicts performance | supports "family, not novelty" |
| PTM naming conventions 2023/2025 EMSE (doi 10.1007/s10664-025-10711-4) | HF model names inaccurate / misleading | naming = renaming argument |
| Luccioni/Varoquaux/Whittaker, Hype, Sustainability... FAccT 2025 (doi 10.1145/3715275.3732006) | refutes bigger-is-better assumptions | hype context |
