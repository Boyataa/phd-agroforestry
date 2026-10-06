# Objective 1 analysis v1: household profile, income drivers, coffee & trees, living conditions (2026-10-05)
> **Note (2026-10-05):** a run with all 600 interviews (the three without a district assigned to Nakaseke, Kasangombe) was tried and reverted at Ezra's request. The analysis stays at 597 households. The same check corrected two numbers below: Nakaseke median yield 58 kg FAQ/acre (all households; 65 was the levers subset) and 2% reaching 1,000 kg in both districts.


This redoes Ezra's earlier Objective_1 notebooks on the cleaned data and links every result to the living income (LI) results (gap v1 gross central; net v1).
- **Scripts** (`data/analysis/`): `build_household_analysis.py` → `Household_Analysis_v1.csv`; then `module_a_sample.py`, `module_b_income_drivers.py`, `module_c_coffee_trees.py`, `module_d_living_conditions.py`; plotting style in `li_style.py`.
- **Inputs:** `Survey_Cleaned_v1.csv`, `Survey_Income_MI_v1.csv`, `Household_Net_Gap_v1.csv`.
- **Sample:** 597 HH (3 without district excluded). Gross medians match gap v1: 5.54M / 3.90M; 92.6% / 98.0% below the reference benchmark.
- **LI groups:** income incl. in-kind as a % of the **household-size** benchmark, in four bands: <25%, 25–50%, 50–100% and ≥100% of the benchmark (313 / 194 / 58 / 32 HH).

## What changed versus the earlier notebooks
| Earlier notebook | Now |
|---|---|
| Benchmark 4.9M / 5.07M / 7.07M UGX/yr (inconsistent with own monthly value) | Rebuilt tool v0.02: 20.17M / 19.78M (reference HH) and household-size benchmarks |
| Raw Q162 income, blanks = 0, cash only | Cleaned income, 20 PMM imputations, plus home-grown food and tree products used at home |
| Q162e labelled "tree income" | Q162e = sale of other crops; tree products valued from Q168–170 |
| Gap regressed on its own income components (R² 0.63 by construction) | log(income / HH benchmark) on household and farm characteristics; Rubin-pooled; HC1 errors |
| Tree product income table all zeros | Values from quantity × farm-gate price |

## A. Household profile (tables A1–A3, figures A1–A2)
- Two subcounties per district, ~150 HH each.
- **Profiles:** both districts have a median household size of 5. Mukono has more children and a higher dependency ratio. Nakaseke respondents are better educated (43% vs 26% secondary or higher) and save more.
- **Furthest below the benchmark:** large households (median 6 members in the <25% group vs 3 in the ≥100% group), female-headed households (56% vs 31%), households with less education (27% vs 66% secondary or higher) and households with less land (2 vs 5 acres). These households also have less coffee area and less group membership.
- **Household size:** the benchmark rises steeply with household size while income barely rises (figure A2). Size is the main reason large households are far from a living income.

## B. Income composition and drivers (tables B1–B3, figures B1, B3)
- **Mean income shares (Mukono / Nakaseke):**
  - coffee 36% / 53%;
  - home-grown food 34% / 35%;
  - other crops 10% / 4%;
  - non-farm work and business 11% / 4%;
  - tree products used at home about 1% or less.
- **The poorest group is food-dependent:** in the <25% group, home-grown food is 66% of income and coffee 22%. In the ≥100% group, coffee is 68% and home food 7%.
- **Participation:** almost every household sells coffee. About half sell other crops, about 30% receive remittances, and 10% / 24% have off-farm work.
- **Drivers model:** OLS of log(income / HH benchmark), n = 581, pooled R² 0.35, values are % change in the ratio. Main model M1:
  - secondary education or higher of the respondent +36%;
  - farmer-group membership +24%;
  - coffee area +23% per log unit;
  - land owned +17% per log unit;
  - each extra household member −8%;
  - credit access −16% (probably poorer households borrowing, i.e. reverse causation);
  - Nakaseke −32%.
  - Number of cash income sources +4% (p < 0.10). It becomes significant once yield and price are added (M2).
- **M2, adding yield and price:** yield elasticity 0.32, Kiboko price 0.12, R² 0.59. Group membership is no longer significant, which suggests it works through yield.
- **M4, net income:** coffee area turns negative. This is an artifact of net v1, where hired-labour cost grows with acres by construction, so it should not be interpreted.
- **M6, enumerator fixed effects (robustness):** R² rises from 0.35 to 0.52 and enumerator differences are large (−0.69 to +0.46 log points). Household size, land, coffee area, education and diversification keep the same sign and significance. Female headship weakens; credit and group membership lose significance.

## C. Coffee and trees (tables C1–C3d, figure C2)
- **Yield:** median 180 (Mukono) and 58 (Nakaseke) kg FAQ-equivalent per acre (Kiboko × 0.5). Only 2% of HH in each district reach Fairtrade's sustainable 1,000 kg.
- **Price and income:** median Kiboko price 5,000 / 6,000 UGX/kg. Coffee income rises from 0.6M in the <25% group to 9.0M in the ≥100% group. Coffee area rises from 1 to 3 acres and yield from 64 to 200 kg across the same groups.
- **Closing the gap with coffee alone** (other income unchanged, current price and area; n = 516):
  - median required yield 1,968 / 1,060 kg FAQ per acre, about 11–14 times today's yield;
  - or a median FAQ price of 93,000–169,000 UGX/kg, about 9–14 times today's price;
  - or a median of 9.5 / 17.9 acres.
  - Only 27% / 47% of households would close the gap at a yield of 1,000 kg or less.
  - **Coffee alone cannot close the gap; other income sources are needed.** This is the bridge to the AFS scenarios in Paper 3.
- **Cross-check:** coffee income implied by yield × price matches reported Q162a (median ratio 1.0 / 0.8).
- **Tree products:** 69% / 73% of HH report at least one tree product, most often annual crops, bananas, fruit and firewood. Median value sold is 0.23M / 0.40M UGX/yr, which is 7% / 14% of cash income for those who report.
- **Trees on farm vs income:** the link differs by district.
  - In Mukono, the third of households with the most trees have a higher ratio (36% vs 22%; net 32% vs 15%).
  - In Nakaseke (tree counts of one enumerator excluded, see below) the link is negative (M3: −0.18 per log unit, p < 0.01). In Mukono it is flat in the model.
  - Associations only; to be tested properly with AFS types and tree diversity in Paper 2.

## D. Living conditions (tables D1–D2, figure D1)
- **Missing for nearly everyone:** health insurance (>99% lack it), clean cooking (93% use firewood), grid electricity (78% lack it) and internet (75% lack it). These barely differ by income group.
- **Lacking more in the poorest group (<25% vs ≥100%):**
  - children not all in school: 51% vs 25% (p < 0.001), though this measure counts under-5s;
  - internet: 77% vs 50%;
  - unprotected drinking water: 17% vs 6%;
  - earth floor: 20% vs 6%;
  - open pit latrine: 11% vs 3%;
  - water fetch over 30 minutes: 10% vs 3%.
  - Only school enrolment, internet and firewood differ significantly across groups.
- **Not comparable across districts:** the enumerator's housing judgement says 98% of Mukono houses are below standard vs 12% in Nakaseke, so it is excluded from the figure.
- **Food constraints (Nakaseke only;** Mukono enumerators recorded few comments): pests and diseases 48% of HH, price 31%, market access 27%, quality 21%.

## Data-quality decisions (Ezra, 2026-10-05)
- **Tree counts:** enumerator Namyenya (Nakaseke, 100 HH) recorded a median of 258 trees on farm vs 5–17 for the others, probably counting coffee bushes. Her tree counts are set to missing; the rest of her data is kept.
- **Enumerator effects:** enumerator fixed effects are a robustness model (M6), not part of the main model.
- **Yield outlier:** a yield above 5,000 kg FAQ per acre (one household recorded 700,000) is set to missing. Kiboko prices outside 1,000–20,000 UGX/kg are set to missing.

## Caveats
- Cross-section; associations only.
- Household size is partly mechanical: both the benchmark and the in-kind food value scale with size.
- Enumerator effects are large: the two Nakaseke enumerators differ about 2.4-fold in income ratio for comparable households. Discuss in the paper; M6 shows the main results hold.
- The net-income model inherits the labour-cost assumptions of net v1.
- Food-constraint codes come from keyword matching of free text ("Other" is 42% in Nakaseke).

## Next
1. Ezra to review the model specification and variable choices.
2. Objective 2: fix species-name spellings, recompute Simpson and Shannon, settle the AFS type rule.
3. Link the AFS types to the household survey for Paper 2.
