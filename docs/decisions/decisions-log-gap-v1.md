
## Gap v1 computed (2026-10-05; `data/gap-log-v1.md`, `data/build_income_gap.py`)
- Rules applied as proposed: in-kind food low = 0.5×own share, central = own, high = 1−bought; both reference-household and household-size-specific benchmarks shown; non-food tree in-kind added, food tree products not added (double count), capped at 95th pct (2.04M; 3 HH capped, e.g. 150 poles × 50,000).
- Central: median income incl. in-kind Mukono 5.51M / Nakaseke 3.82M UGX/yr vs benchmark 20.17M / 19.78M → 27% / 19% of benchmark (cash-only 12% / 7%); 93% / 98% of HH below benchmark; median gap 14.7M / 16.0M.
- Income shares (mean): Mukono coffee 36%, in-kind food 34%; Nakaseke coffee 53%, in-kind food 35%.
- Still open: confirm low/high rules; Mpigi shares applied to both districts.

## Net-income sensitivity v1 DONE (2026-10-05; `data/net-income-log-v1.md`, `data/build_net_income.py`)
Decisions (Ezra, asked one by one):
1. Management-activity costs are wage RATES → × labour-days from Fairtrade LIRP Robusta Uganda (Oct 2022) Table 3 (weeding 36, pests 48, fertilisation 20, rejuvenation 48, harvest 50 + post-harvest 45, replanting 2 days/acre/yr).
2. Hired labour only (positive rate = hired; family labour uncosted); all-labour-costed as upper-bound sensitivity.
3. Days × coffee acres; harvest/post-harvest also × yield/1,000 kg FAQ per acre (cap 1).
4. Mapping: in-season mgmt → rejuvenation, planting → replanting; trenching/terracing, soil & water conservation, intercropping left out.
5. "annually" = annual spend used as is; hourly ×8, weekly ÷6, monthly ÷26 → day rate.
6. Inputs = cost per application × frequency (1/2/4); low bound ×1.
7. Land rent only for non-owners. 8. Plot block: only seedlings, mulching, thinning. 9. Day rates capped at 25,000 UGX (Fairtrade living wage; 79 entries).
Claude's calls (flagged): Kiboko→FAQ ×0.5; rehab labour ÷ cycle; plot daily/weekly/monthly entries unused (125).
Result (net central): median 4.00M / 2.56M → 19.8% / 12.9% of benchmark (gross 27.3% / 19.3%); 93.6% / 99.2% below; median gap 16.2M / 17.2M; 4.6% of Nakaseke HH net < 0. Median costs 0.86M / 0.97M (18.6% / 27.3% of gross), mostly hired labour. All-labour bound: 17.6% / 9.0%.

## Objective 1 notebooks redone v1 (2026-10-05; `data/analysis/obj1-analysis-log-v1.md`, tables in `data/analysis/Obj1_tables_v1.md`)
- Ezra's earlier notebooks (PC: ...\Data Analysis - CAI\Python\Objective_1 and Objective_2; read-only) reviewed. Issues: inconsistent benchmarks (4.9–7.07M), raw cash Q162, Q162e mislabelled "tree income", gap regressed on its own components, tree product income table all zeros. Ezra: "we are re-doing everything here"; analysis must complement the LI results.
- Scope agreed: (A) sample/Table 1, (B) income sources & drivers, (C) coffee & trees, (D) living conditions; delivered as scripts + tables + figures + log. Objective 2 (17-plot tree diversity) AFTER Objective 1.
- LI groups by household-size benchmark: <25 / 25–50 / 50–100 / ≥100%. Drivers: OLS log(income incl. in-kind / HH benchmark), HC1, Rubin-pooled over 20 imputations; M2 adds yield/price, M3 trees by district, M4 net, M5 logit ≥50%, M6 enumerator FE.
- Data-quality decisions (Ezra): enumerator Namyenya's tree counts (median 258) set to missing (likely coffee bushes), rest of her data kept; enumerator fixed effects as robustness only. Claude: yield > 5,000 kg FAQ/acre → missing; Kiboko price outside 1,000–20,000 → missing.
- Key results: poorest group 66% of income from home-grown food; education, land, coffee area, group membership +; household size −; coffee alone would need ~11–14× today's yield to close the gap; enumerator effects large (R² 0.35 → 0.52) but main results hold.
- Project storage nearly full (≈1.99 of 2 MB): household analysis CSV and PNG figures not stored; rebuild with the scripts (figures sent to Ezra in chat).
