# income_analysis
Old notebook: `Tree Income vs Cofffee.ipynb` (cells 7-10). The old version used tree income = 6.6M summed over all households (0.28%), hard-coded numbers, and a line across categories with 50/10/1% "reference" lines. Script: `scripts/morefigures/income.py` (run from repo root). Data: `data/derived/Household_Analysis_v1.csv` (597 HH) + `Survey_Cleaned_v1.csv` (Q168-170 tree products, tree-plantation acres). Income = cleaned imputed Q162 a-h (`inc_*_mi`, mean of 20 imputations); in-kind = home-grown food (`inkind_food_central`) + non-food tree products used at home (`tree_inkind`), as in gap v1. Benchmarks = v0.02 (Mukono 20.17M, Nakaseke 19.78M UGX/yr, reference household).

## New figure
- `income_by_category_vs_benchmark.png`: by district, mean per household of:
  - tree products (Q168-170, capped);
  - coffee;
  - coffee + tree products;
  - all other income incl. home-grown food;
  - total cash;
  - total incl. in-kind.
- Each bar is labelled with its % of the v0.02 reference benchmark (dashed line).
  - Tree products: 0.7% / 1.7% of the benchmark.
  - Coffee: 14% / 15%.
  - Total incl. in-kind: 39% / 28%.

## Changes vs old
- Values are computed from the data instead of typed in.
- Tree products come from Q168-170 (household total capped at 2.04M, see coffee_vs_trees_vs_other NOTES).
- Reference lines are the v0.02 benchmark, not the arbitrary 50/10/1% thresholds.

## Dropped or merged
- Merged into one figure: income_by_category, income_percentage(_by_category), income_line_with_reference, tree_vs_non_tree_income and tree_vs_non_tree_pie.
- income_by_source duplicates income_sources F1, so it is dropped here.
