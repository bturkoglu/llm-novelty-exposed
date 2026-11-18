# Step 3 coding summary — coder A, quote-verified, PRELIMINARY (no second coder yet)

| stratum | n | release rpt | ARCH/TRAIN claims | ablation YES | PARTIAL | NO | reports w/ seeds>=2 or var | rerun YES | scores copied YES/MIXED | 3rd-party | data FULL | tokens Y | compute Y | reports w/ rename |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2020-2022 | 9 | 9 | 17 | 7/17 (41%) | 5/17 (29%) | 5/17 (29%) | 3/9 (33%) | 1/9 (11%) | 7/9 (78%) | 2/9 (22%) | 1/9 (11%) | 3/9 (33%) | 4/9 (44%) | 0/9 (0%) |
| 2023 | 5 | 5 | 7 | 3/7 (43%) | 0/7 (0%) | 4/7 (57%) | 1/5 (20%) | 1/5 (20%) | 2/5 (40%) | 1/5 (20%) | 1/5 (20%) | 4/5 (80%) | 2/5 (40%) | 2/5 (40%) |
| 2024 | 14 | 14 | 30 | 13/30 (43%) | 2/30 (7%) | 15/30 (50%) | 0/14 (0%) | 3/14 (21%) | 8/14 (57%) | 3/14 (21%) | 2/14 (14%) | 12/14 (86%) | 4/14 (29%) | 2/14 (14%) |
| 2025 | 10 | 10 | 26 | 4/26 (15%) | 10/26 (38%) | 12/26 (46%) | 0/10 (0%) | 4/10 (40%) | 5/10 (50%) | 1/10 (10%) | 0/10 (0%) | 9/10 (90%) | 2/10 (20%) | 0/10 (0%) |
| 2026 | 2 | 2 | 4 | 0/4 (0%) | 1/4 (25%) | 3/4 (75%) | 0/2 (0%) | 0/2 (0%) | 0/2 (0%) | 0/2 (0%) | 0/2 (0%) | 2/2 (100%) | 0/2 (0%) | 0/2 (0%) |
| ALL | 40 | 40 | 84 | 27/84 (32%) | 18/84 (21%) | 39/84 (46%) | 4/40 (10%) | 9/40 (22%) | 22/40 (55%) | 7/40 (18%) | 4/40 (10%) | 30/40 (75%) | 12/40 (30%) | 4/40 (10%) |

Claim categories (all reports): {'OTHER': 64, 'ARCH': 55, 'EFF': 34, 'TRAIN': 29, 'DATA': 26, 'SCALE': 21, 'POST': 16, 'EVAL': 11, 'CTX': 9, 'TOK': 5}

Renames (verified quotes):
- falcon (2311.16867) p.28: 'monolayer' <- selective activation recomputation (Li et al., 2021)
- falcon (2311.16867) p.13: 'multigroup' <- grouped query attention (Ainslie et al., 2023)
- mamba (2312.00752) p.41: 'selection' <- RNN gating
- mamba2 (2405.21060) p.24: 'multi-contract SSM (MCS)' <- multi-query attention (MQA, Shazeer 2019)
- falcon_mamba (2410.05355) p.6: 'Parallel Prefill' <- standard parallel prompt processing (prefill)