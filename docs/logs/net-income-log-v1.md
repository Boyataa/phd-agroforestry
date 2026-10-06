# Net-income sensitivity v1 — 2026-10-05
Script: `data/build_net_income.py` (inputs: `Survey_Cleaned_v1.csv`, `Survey_Income_MI_v1.csv`, regenerated with `clean_survey.py`; reproduces the Project files exactly). Gross income, in-kind and benchmarks are rebuilt as in gap v1 and match it exactly (median 5.51M / 3.82M; 27.3% / 19.3% of benchmark). Benchmark parameters are solved from `Household_Gap_v1.csv` values and checked against five other household compositions (exact).

**Net income = gross income incl. in-kind (gap v1, central) − annual cash production costs.** 20 imputations, statistic per imputation, then averaged.

## Cost rules (Ezra's decisions, 2026-10-05)
| Item | Rule |
|---|---|
| Labour | Survey records a wage **rate** per work period, not spend. Days/acre/yr from **Fairtrade Living Income Reference Price, Robusta Uganda (Oct 2022), Table 3**: weeding 36, pest mgmt 48, fertilisation 20, rejuvenation 48 (= survey "in-season management"), harvest 50 + post-harvest 45, replanting 2 (= survey "planting"). Trenching/terracing, soil & water conservation, intercropping: not costed (no Fairtrade days). |
| Hired vs family | Only hired labour costed: positive rate = hired, 0/missing = family (Fairtrade practice). Upper bound: all days costed (own rate, else district median day rate). |
| Scaling | Days × coffee acres; harvest + post-harvest also × yield/1,000 kg FAQ per acre (cap 1; Kiboko→FAQ × 0.5; latest harvest year; 11 HH missing yield → district median). |
| Periods | daily ×1, hourly ×8, weekly ÷6, monthly ÷26 → day rate. "annually" = annual spend, added as is. |
| Wage cap | Day rates capped at **25,000 UGX** (Fairtrade daily living wage); 79 entries capped (reported up to 60,000). |
| Inputs | Manure/compost, urea, NPK, DAP: cost × frequency (once 1, every season 2, >3×/yr 4). Low bound ×1. |
| Plot block | Only seedlings, mulching, thinning (no overlap with activity block); season ×2, bi-annual ×2, annual ×1. 125 daily/weekly/monthly entries not used. |
| Land rent | Only the 17 non-owners (11 with values); owners' "cost if hired" treated as hypothetical. |
| Rehabilitation | Total_Labour_Cost ÷ cycle years (1–30, else district median). |

## Results (pooled, reference benchmark 20.17M Mukono / 19.78M Nakaseke)
| Scenario | District | Median income | % of benchmark | % below ref | % below HH-specific | Median gap (ref) | % HH net < 0 |
|---|---|---|---|---|---|---|---|
| Gross (gap v1) | Mukono | 5.51M | 27.3 | 92.6 | 93.9 | 14.65M | 0 |
| | Nakaseke | 3.82M | 19.3 | 97.6 | 95.5 | 15.96M | 0 |
| **Net central** | Mukono | **4.00M** | **19.8** | 93.6 | 95.9 | 16.16M | 1.5 |
| | Nakaseke | **2.56M** | **12.9** | 99.2 | 98.6 | 17.22M | 4.6 |
| Net, inputs ×1 | Mukono | 4.08M | 20.3 | 93.6 | 95.9 | 16.08M | 1.5 |
| | Nakaseke | 2.61M | 13.2 | 99.1 | 98.2 | 17.17M | 3.9 |
| Net, all labour costed | Mukono | 3.54M | 17.6 | 94.6 | 96.9 | 16.62M | 2.8 |
| | Nakaseke | 1.79M | 9.0 | 99.2 | 98.7 | 17.99M | 14.9 |

Costs (central): median 0.86M (Mukono) / 0.97M (Nakaseke) UGX/yr; mean 1.52M / 2.41M. Hired labour is most of it (mean 1.35M / 2.04M); inputs mean 0.14M / 0.26M. 84% / 88% of HH have some cost. Median cost = 18.6% / 27.3% of gross income. Median yield 180 / 62.5 kg FAQ per acre.

## Caveats
- Fairtrade days are for a sustainable target yield; costing all of an activity's days as hired when a positive rate is reported likely overstates hired labour on larger farms (17 HH have net < 0, mostly Nakaseke farms of 2–20 acres). Partial hiring is not observable in the survey.
- Activity costs may cover coffee and other crops together; gross income includes non-farm sources, so costs are subtracted from total income.
- Three uncosted activities and family labour make the central net an upper estimate of true net *cash* income in that respect; the all-labour scenario gives the lower bound.
- Kiboko→FAQ 0.5 is an assumption; harvest-year records with years outside 2020–2025 were ignored.
- Livestock, trade and off-farm costs are not in the survey; those incomes stay gross.
