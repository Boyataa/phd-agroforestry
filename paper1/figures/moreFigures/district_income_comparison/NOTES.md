# district_income_comparison
No notebook was found. Rebuilt from the old `output/district_income_comparison/tables/district_income_breakdown.csv`, which held Coffee / "Trees" (= Q162e) / Other totals by district. Script: `scripts/morefigures/income.py` (run from repo root). Data: `data/derived/Household_Analysis_v1.csv` (597 HH) + `Survey_Cleaned_v1.csv` (Q168-170 tree products, tree-plantation acres). Income = cleaned imputed Q162 a-h (`inc_*_mi`, mean of 20 imputations); in-kind = home-grown food (`inkind_food_central`) + non-food tree products used at home (`tree_inkind`), as in gap v1. Benchmarks = v0.02 (Mukono 20.17M, Nakaseke 19.78M UGX/yr, reference household).

## New figures
- `district_income_vs_benchmark.png`: mean income per household, stacked by category, against the v0.02 reference benchmark, with the median marked.
  - Mukono: mean 7.92M (39% of the benchmark), median 5.54M.
  - Nakaseke: mean 5.59M (28%), median 3.90M.
- `district_income_distribution.png`: each household's cash income and income incl. in-kind on a log scale, with IQR, median and benchmark lines. Mann-Whitney p < 0.001 for both. The CSV gives % below the reference and household-size benchmarks.

## Changes vs old
- "Trees" (Q162e) is relabelled "other crop sales". Means replace totals; in-kind and the v0.02 benchmark are added.
- The old Coffee/Trees/Other % were 55/15/30 (Mukono) and 83/6/11 (Nakaseke) of raw cash.

## Dropped or merged
- district_stacked_income becomes F1.
- mukono_combo_chart and nakaseke_combo_chart are merged into F1 and F2; the bar-plus-line combos are not repeated.
