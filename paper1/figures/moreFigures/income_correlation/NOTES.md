# income_correlation
Old notebook: `Income_sources.ipynb` (cells 2 and 4). The old version used Pearson on raw income with blanks = 0. Script: `scripts/morefigures/income.py` (run from repo root). Data: `data/derived/Household_Analysis_v1.csv` (597 HH) + `Survey_Cleaned_v1.csv` (Q168-170 tree products, tree-plantation acres). Income = cleaned imputed Q162 a-h (`inc_*_mi`, mean of 20 imputations); in-kind = home-grown food (`inkind_food_central`) + non-food tree products used at home (`tree_inkind`), as in gap v1. Benchmarks = v0.02 (Mukono 20.17M, Nakaseke 19.78M UGX/yr, reference household).

## New figures
- `spearman_heatmap_overall.png`: Spearman correlation matrix, lower triangle with values, for 20 variables:
  - the 8 cash sources, total cash and income incl. in-kind;
  - number of sources, land, coffee area, other-crops area, tree-plantation acres, trees on farm;
  - coffee yield, Kiboko price, household size, farming years.
  - Pairwise n = 461-597.
- `spearman_heatmap_by_district.png`: the same matrix for Mukono (n = 273-297) and Nakaseke (n = 182-300).
- `spearman_income_vs_characteristics.png`: rho with 95% CI (Fisher z, Bonett-Wright SE) for 14 farm and household characteristics vs total cash and vs income incl. in-kind, by district. The n for every pair is in the CSV.
  - Strongest overall: coffee yield (0.45), land (0.44), coffee area (0.41), group membership (0.30), secondary education (0.26).
  - Trees on farm: positive in Mukono (0.38), negative in Nakaseke (-0.15).
  - Kiboko price: negative in Mukono.

## Changes vs old
- Spearman instead of Pearson (income is very skewed), and n is reported.
- Trees on farm excludes Namyenya's counts (cleaning decision).
- The old "top correlations with total income" ranked income components against their own sum; Robusta 0.89 was mechanical. They are now dropped from that ranking. Components stay in the heatmap, with a note.
- coffee x coffee-area interaction dropped (mechanical).
- Added: yield, price, household size, education, group, extension.
- In Nakaseke, professional-job and other-source income are almost all zero, so their rho is unstable or blank.

## Dropped or merged
- The 3 old heatmaps (overall, Mukono, Nakaseke) become 2 figures.
- top_correlations_with_total_income_line (a line across variables) becomes the F3 dot plot.
- The duplicate correlation_heatmap from income_sources is merged here.
- These are bivariate associations; adjusted estimates are in Paper 1 B3.
