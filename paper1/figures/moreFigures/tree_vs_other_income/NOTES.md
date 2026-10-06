# tree_vs_other_income
Old notebook: `Income_sources.ipynb` (cell 8). The old "strict" tree income was Q162e (11%), and the "agroforestry" version was coffee + Q162e (79%). Both were wrong because Q162e is sale of other crops. Script: `scripts/morefigures/income.py` (run from repo root). Data: `data/derived/Household_Analysis_v1.csv` (597 HH) + `Survey_Cleaned_v1.csv` (Q168-170 tree products, tree-plantation acres). Income = cleaned imputed Q162 a-h (`inc_*_mi`, mean of 20 imputations); in-kind = home-grown food (`inkind_food_central`) + non-food tree products used at home (`tree_inkind`), as in gap v1. Benchmarks = v0.02 (Mukono 20.17M, Nakaseke 19.78M UGX/yr, reference household).

## New figure
- `tree_vs_non_tree_share.png`: share of mean income for Mukono, Nakaseke and both, cash only vs incl. in-kind, in five categories:
  - tree crop (coffee);
  - non-food tree products used at home;
  - mixed / cannot split: other crop sales (Q162e);
  - mixed / cannot split: home-grown food;
  - non-tree: livestock, non-farm work, transfers.
- Tree-based income incl. in-kind is 36% / 54% (coffee plus about 1% tree in-kind).
- Sensitivity in the CSV: adding Q168-170 tree product values (capped) gives 37% / 56%. This is an upper bound because of overlap.

## Changes vs old
- Q162e is no longer counted as tree income; it is shown as "mixed" because it includes banana and fruit as well as annual crops.

## Dropped or merged
- tree_vs_non_tree_pie becomes a 100% bar.
