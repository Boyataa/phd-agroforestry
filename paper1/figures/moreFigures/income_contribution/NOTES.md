# income_contribution
Old notebook: `Income_sources.ipynb` (cell 6). The old version averaged each household's % shares, giving coffee 67.9%. Script: `scripts/morefigures/income.py` (run from repo root). Data: `data/derived/Household_Analysis_v1.csv` (597 HH) + `Survey_Cleaned_v1.csv` (Q168-170 tree products, tree-plantation acres). Income = cleaned imputed Q162 a-h (`inc_*_mi`, mean of 20 imputations); in-kind = home-grown food (`inkind_food_central`) + non-food tree products used at home (`tree_inkind`), as in gap v1. Benchmarks = v0.02 (Mukono 20.17M, Nakaseke 19.78M UGX/yr, reference household).

## New figures
- `household_share_by_category.png`: mean of the household-level shares (each household's shares sum to 100), by district, cash only vs incl. in-kind.
  - Coffee: 63% / 74% of cash and 30% / 39% incl. in-kind.
  - Home-grown food: 48% of a household's income incl. in-kind on average.
  - The CSV also gives the share of pooled income for comparison.
- `largest_income_category.png`: % of households whose largest category is each source.
  - On cash, coffee is the largest for 73% / 90% of households.
  - Incl. in-kind, home-grown food is the largest for 57% / 59%.
  - Chi-square by district, p < 0.001.

## Changes vs old
- Cleaned imputed income and the Q162e relabel. The in-kind basis is added.
- The mean of household shares is now labelled explicitly and kept separate from the share of pooled income.

## Dropped or merged
- district_income_contribution_stacked becomes F1.
- overall_income_contribution_line (a line across categories) is dropped; the "Both" row of F1 replaces it.
