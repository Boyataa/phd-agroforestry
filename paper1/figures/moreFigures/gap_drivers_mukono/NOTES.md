# gap_drivers_mukono (old notebook: incomeGap-Mukono.ipynb, cell 7)
Script: `scripts/morefigures/food_prices_gap.py`.

**No new model is estimated.** The old OLS regressed the annual gap (benchmark minus income) on coffee, "tree" (actually Q162e, other crops) and off-farm income. These are components of the income that defines the gap, so R² 0.63 and coefficients near -1 hold by construction. It also used the wrong benchmark (5.07M), dropped rows with blanks set to 0, and covered Mukono only. The adjusted drivers model for both districts is **paper1 table B3**: OLS of log(income / household benchmark), with 20 imputations Rubin-pooled and HC1 errors. It is copied here unchanged as `B3_drivers_regression.csv`; see `docs/logs/obj1-analysis-log-v1.md`.

**Descriptive comparison only (both districts, gross income incl. in-kind / household-size benchmark v0.02):**
- `gap_drivers_spearman_by_district.png` + `gap_correlation_spearman.csv`: rank correlations of household and farm characteristics with the income ratio. Gross and net are both in the CSV, with p-values and n per variable.
  - In both districts: household size is negative (-0.25 / -0.30); coffee area (+0.35 / +0.36), yield (+0.33 / +0.52), education and group membership are positive.
  - The districts differ for trees on farm (Mukono +0.29, Nakaseke -0.15; Namyenya's counts excluded), number of income sources (+0.31 vs 0) and land (+0.51 vs +0.23). This is consistent with B3 M3.
- `gap_characteristics_by_li_group.csv`: medians (or %) of each characteristic in households at <25%, 25–50% and >=50% of the benchmark, by district. The top two groups are merged because of small n. Tests are Kruskal-Wallis for continuous variables and chi-square for binary ones.
- Tests use the mean of the 20 imputations (descriptive). Inference is in B3.

**Dropped:** `regression_summary.txt` (gap on its own components) and the old Mukono-only correlation matrix (it correlated the gap with its own income components).
