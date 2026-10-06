# Survey cleaning log — version 1 (2026-10-05)

**Input:** `Standardized_Data.csv` (Ezra's cleaned file, 600 households) + `Clean Responses Social Economi Survey.csv` (original KoBo export, used only to restore values damaged by Excel).
**Outputs (folder `data/`):**
- `Survey_Cleaned_v1.csv`: one row per household. All original columns kept unchanged except the Excel repairs; new variables end in `_clean`, `_m2`, `_model` or `_flag`.
- `Survey_Income_MI_v1.csv`: 20 imputed versions of the income variables (long format: `_id`, `imputation` 1–20). Use for inference with Rubin's rules.
- `clean_survey.py`: reproducible script (fixed random seed 20251005).

## 1. Excel repairs
| Problem | Fix |
|---|---|
| `start`, `end` cut to mm:ss; `Date_Time` shifted −3 h and reformatted | Restored full ISO timestamps (+03:00, Uganda time) from the KoBo export by `_id` |
| Household-member age groups turned into numbers (0_5→5, 6_15→615, 16_25→1625, 26_40→2640, 41_60→4160) | Mapped back to the original codes (1,600+ cells across six roster columns); checked 100% identical to the KoBo export |
| Respondent age header became "n and" | Renamed `Age_of_Respondent_years` (values are age bands: 20-29 … ≥70) |

## 2. Number of children → `children_clean`, `children_flag`
- Mukono counts were derived from the schooling section (confirmed by Ezra), so they're kept as reported. Values of 13–15 match the number of children in school.
- Three Nakaseke keying errors were corrected. The rule takes the first digit, or the number of children in school if that is larger:
  - `_id` 561200542: 36 → 3 (3 in school)
  - `_id` 561202398: 58 → 5 (1 in school)
  - `_id` 589549118: 350 → 3 (1 in school)
- 17 missing counts were filled with the number of children in school. That number is a lower bound, because it misses children not in school.
- 11 counts remain missing.
- Result: median 3 children in both districts; mean 3.5 (Mukono), 2.6 (Nakaseke).

## 3. Floor area → `floor_area_m2`, `floor_area_m2_model`, `floor_area_flag`
**Diagnosis.** The question label says square feet, but the two districts were clearly recorded differently.
- **Mukono values behave like m².** The median is 64 for 4 rooms, values are products like 8×9 and 9×10, and area tracks rooms, rent and build cost (Spearman 0.64–0.70).
- **Nakaseke values behave like ft².** The median is 198, i.e. 18 m² for 3 rooms. They are tightly bunched (IQR 16.6–20.1 m²) and barely related to rooms (0.20) or rent (0.08). That suggests estimates rather than measurements.

**Treatment.**
- `floor_area_m2` is the recorded value in m²: Mukono as recorded, Nakaseke × 0.0929. 3 implausible values (< 4 or > 400 m²) were set to missing. All Nakaseke values are flagged as low reliability.
- `floor_area_m2_model` predicts floor area from rooms, bedrooms, permanent dwelling, brick/block walls and cement floor, using a log-linear model fitted on Mukono (n = 285, R² = 0.62). It is applied to both districts, so both share the same measurement basis.
  - Predicted medians: Mukono 68 m², Nakaseke 61 m² (recorded Nakaseke: 18 m²).
- **Recommendation:** use `floor_area_m2_model` (or number of rooms) for comparisons between districts. Don't use the recorded Nakaseke areas as measurements. Ask the Nakaseke enumerators (Kawalya Dan, Najjuma Olivia, Namyenya Lillian) how area was recorded.

## 4. Household income (Q162 a–h, UGX per year) → `inc_<source>_clean`, `inc_<source>_flag`, `income_total_clean`, `income_any_imputed`
**Why income is missing.** Most of the 62 Nakaseke households without income figures were interviewed on 1–9 September 2025. The income block was probably not in the form yet, so this looks like missingness by form version rather than refusal. Missing-at-random given district and covariates is therefore a reasonable assumption.

**Steps.**
1. **Sources not listed = 0.** Among households that answered both questions, a source not ticked in "income sources" never had an amount (checked for all 8 sources).
2. **Coffee income from seasonal sales.** Q162a equals the sum of seasonal coffee income (Kiboko + FAQ, Nov–Jan + May–Jun) for most households (median ratio 1.0). For the 65 households missing Q162a, the seasonal sum is used.
3. **Listed sources with no amount.** These are imputed by predictive mean matching (PMM) on log amount. One model is fitted per source on the households reporting that source.
   - Predictors: district, log land owned, log coffee income, number of children, respondent age (band midpoint).
   - 20 imputations with bootstrapped coefficients and 5 nearest donors. The most common case is other crops (29 households).
4. **Source list not answered (17 households).** Each non-coffee source is imputed by PMM on log(1 + amount) over all households, zeros included. This predicts whether the household has the source as well as how much.

**Other fixes.** One land value of 120,000 acres was treated as missing when used as a predictor (the raw column is unchanged).

**Result.** Every household now has a total income.
- 81 households have at least one imputed component (Nakaseke 75, Mukono 6).
- Median total income: Mukono 2.40M UGX; Nakaseke 1.40M UGX (mean of medians across the 20 imputations; between-imputation SD ≈ 25,000).
- Households with imputed components have similar or slightly higher incomes (Nakaseke median 1.59M vs 1.37M observed).

**How to use.**
- For description, use `income_total_clean`, the mean of the 20 imputations.
- For regressions and gap estimates, run the analysis on each of the 20 datasets in `Survey_Income_MI_v1.csv` and pool the results with Rubin's rules. In Stata: `mi import`; in R: `mice::as.mids` / `mitools`.
- Report the imputation share and do a sensitivity check that excludes imputed households.

## Still open
- 3 households without district (`_id` 554399870, 552806065, 554403180): Ezra says manageable. The last two are in the Nakaseke agro-ecological zone.
- Income is still **gross** and the recall period is unconfirmed (open question 1). Production costs and the value of home-consumed food are not yet subtracted or added.
- Enumerator names and GPS are still in the file. Remove them before sharing outside the project.
