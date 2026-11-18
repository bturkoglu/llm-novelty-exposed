# Step 3 coding summary — FINAL: A (Claude Opus) + B (OpenAI gpt-6.1-sol) + resolver (xAI grok-4.7), quote-verified

| stratum | n | release rpt | ARCH/TRAIN claims | ablation YES | PARTIAL | NO | reports w/ seeds>=2 or var | rerun YES | scores copied YES/MIXED | 3rd-party | data FULL | tokens Y | compute Y | reports w/ rename |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2020-2022 | 9 | 9 | 10 | 3/10 (30%) | 3/10 (30%) | 4/10 (40%) | 3/9 (33%) | 1/9 (11%) | 7/9 (78%) | 2/9 (22%) | 1/9 (11%) | 3/9 (33%) | 3/9 (33%) | 0/9 (0%) |
| 2023 | 5 | 5 | 5 | 2/5 (40%) | 0/5 (0%) | 3/5 (60%) | 1/5 (20%) | 1/5 (20%) | 2/5 (40%) | 2/5 (40%) | 0/5 (0%) | 3/5 (60%) | 2/5 (40%) | 2/5 (40%) |
| 2024 | 14 | 14 | 28 | 11/28 (39%) | 5/28 (18%) | 12/28 (43%) | 0/14 (0%) | 2/14 (14%) | 8/14 (57%) | 2/14 (14%) | 1/14 (7%) | 12/14 (86%) | 4/14 (29%) | 2/14 (14%) |
| 2025 | 10 | 10 | 27 | 3/27 (11%) | 12/27 (44%) | 12/27 (44%) | 0/10 (0%) | 4/10 (40%) | 5/10 (50%) | 2/10 (20%) | 0/10 (0%) | 9/10 (90%) | 3/10 (30%) | 0/10 (0%) |
| 2026 | 2 | 2 | 3 | 0/3 (0%) | 0/3 (0%) | 3/3 (100%) | 0/2 (0%) | 0/2 (0%) | 0/2 (0%) | 0/2 (0%) | 0/2 (0%) | 2/2 (100%) | 0/2 (0%) | 0/2 (0%) |
| ALL | 40 | 40 | 73 | 19/73 (26%) | 20/73 (27%) | 34/73 (47%) | 4/40 (10%) | 8/40 (20%) | 22/40 (55%) | 8/40 (20%) | 2/40 (5%) | 29/40 (72%) | 12/40 (30%) | 4/40 (10%) |

Claim categories (all reports): {'OTHER': 64, 'ARCH': 44, 'EFF': 34, 'TRAIN': 29, 'DATA': 26, 'SCALE': 21, 'POST': 16, 'EVAL': 11, 'CTX': 9, 'TOK': 5}

Renames (verified quotes):
- falcon (2311.16867) p.28: 'monolayer' <- selective activation recomputation (Li et al., 2021)
- falcon (2311.16867) p.13: 'multigroup' <- grouped query attention (Ainslie et al., 2023)
- mamba (2312.00752) p.41: 'selection' <- RNN gating
- mamba2 (2405.21060) p.24: 'multi-contract SSM (MCS)' <- multi-query attention (MQA, Shazeer 2019)
- falcon_mamba (2410.05355) p.6: 'Parallel Prefill' <- standard parallel prompt processing (prefill)