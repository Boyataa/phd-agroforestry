# coffee_vs_trees_vs_other
Old notebook: `Income_sources.ipynb` / `Tree Income vs Cofffee.ipynb`. Old result: Coffee 67.9%, "Trees" 11.1% (actually Q162e other crops), Other 21%. Script: `scripts/morefigures/income.py` (run from repo root). Data: `data/derived/Household_Analysis_v1.csv` (597 HH) + `Survey_Cleaned_v1.csv` (Q168-170 tree products, tree-plantation acres). Income = cleaned imputed Q162 a-h (`inc_*_mi`, mean of 20 imputations); in-kind = home-grown food (`inkind_food_central`) + non-food tree products used at home (`tree_inkind`), as in gap v1. Benchmarks = v0.02 (Mukono 20.17M, Nakaseke 19.78M UGX/yr, reference household).

## New figure
- `coffee_trees_other_by_district.png`, for coffee sales, tree products (Q168-170), other crop sales, other cash and home-grown food:
  - (a) % of households reporting each;
  - (b) the median amount among those reporting.
- Tree products are reported by 43% (Mukono) and 58% (Nakaseke) of households, with a median of 290k / 500k UGX/yr when reported. Coffee medians are 1.2M / 1.0M.
- Tables: `coffee_trees_other_by_district.csv` (also gives means) and `tree_products_by_type.csv` (all products, incl. annual crops).

## Changes vs old
- Tree value is quantity x farm-gate price from Q168-170 (read as in module C), not Q162e.
- "Annual crops" is excluded because it is not a tree product. Module C's 69-73% "any product" included it.
- Tree values partly overlap Q162e sales and home-grown food, so they are not added into shares of a total. The old pie did exactly that.

## Data problem
- In Nakaseke the farm-gate "price" (Q169) is often a total (e.g. 1,000,000 per bunch of bananas). Household tree value reaches 100M, and the household 95th percentile is 14M.
- Means are capped at 2.04M per household, the gap v1 tree in-kind cap. Medians are uncapped.
- Q169 needs checking before tree values are used in Paper 2.

## Dropped or merged
- coffee_tree_other_pie and coffee_tree_other_line (shares of an overlapping total, and a line across categories) are dropped.
- combo_chart is replaced by the two-panel bar figure.
