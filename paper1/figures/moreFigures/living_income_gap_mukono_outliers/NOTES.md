# living_income_gap_mukono_outliers (old notebook: incomeGap-Mukono.ipynb, cells 2–11)
Script: `scripts/morefigures/food_prices_gap.py`. Both districts, all 597 households.
- `income_scatter_clean_colored.png`: households ranked by gross income as % of their household-size benchmark (dots), with net income (grey) and the 100% line. Below the benchmark: Mukono 94% gross and 96% net; Nakaseke 96% and 99%. Replaces `income_scatter_clean` and `income_scatter_clean_colored`, which were two versions of the same plot; the coloured one is kept.
- `living_income_gap_comparison.png`: median cash, gross (incl. home-grown food) and net income vs the reference benchmark, by district. Mean values are in the summary CSV of living_income_gap_mukono.
- `living_income_stacked.png` (+ `living_income_groups.csv`): 100% stacked bars of households by income as % of the household benchmark (<25, 25–50, 50–100, >=100%), gross vs net, by district. At or above the benchmark: Mukono 6% gross and 4% net; Nakaseke 4% and 1%. Replaces the old below/above stacked bars.
- `income_gap_outlier_sensitivity.csv`: what the old IQR rule would do (kept as a check only).

**What changed:**
- The old analysis removed "outliers" with the IQR rule on total income (35 Mukono households), i.e. it dropped the best-off farmers, and then compared the rest with a 4.89M or 5.07M benchmark.
- Implausible values are already handled in the cleaning (cleaning-log-v1), so no households are removed now. Medians are used where skew matters.
- Applying the IQR rule would remove 31 Mukono and 23 Nakaseke households. It would lower mean gross income by 30% / 22%, but change the median ratio by only about 1 point. This shows the rule changes means, not the conclusion.
- Benchmarks are v0.02, both districts are covered, and gross and net are shown.
