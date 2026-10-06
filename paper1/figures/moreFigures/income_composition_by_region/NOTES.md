# income_composition_by_region
Old notebook: `Income_sources.ipynb` (cells 11-12). Script: `scripts/morefigures/income.py` (run from repo root). Data: `data/derived/Household_Analysis_v1.csv` (597 HH) + `Survey_Cleaned_v1.csv` (Q168-170 tree products, tree-plantation acres). Income = cleaned imputed Q162 a-h (`inc_*_mi`, mean of 20 imputations); in-kind = home-grown food (`inkind_food_central`) + non-food tree products used at home (`tree_inkind`), as in gap v1. Benchmarks = v0.02 (Mukono 20.17M, Nakaseke 19.78M UGX/yr, reference household).

## New figures
- `income_composition_by_district_ugx.png`: mean UGX/HH for coffee, other crop sales (Q162e), other cash, home-grown food and tree in-kind, for Mukono, Nakaseke and both. Error bars are 95% bootstrap CIs, seed 42; imputation uncertainty is not included.
- `income_composition_100pct.png`: the same categories as a share of mean income, cash only vs incl. in-kind.
- `coffee_dependence_by_district.png`: coffee share of each household's cash income and of its income incl. in-kind, by district. Each household is a dot, with a box plot. Mann-Whitney p < 0.001 for both.
  - Median coffee share of cash: 65% (Mukono) vs 78% (Nakaseke).
  - Median coffee share incl. in-kind: 25% vs 33%.

## Changes vs old
- The old "Trees (Non-Coffee)" category was Q162e, which is sale of other crops. It is relabelled. Tree in-kind is shown separately and is about 1% or less.
- Old coffee shares were 55% / 83% of raw cash totals. Now 55% / 82% of mean cleaned cash, and 36% / 53% incl. in-kind.

## Dropped or merged
- Merged into F1: income_composition_grouped_ugx, all_regions_income_composition_grouped_combo, and both/mukono/nakaseke_income_composition_combo. These were bar plus line combos, with lines drawn across categories.
- income_composition_100pct_stacked becomes F2.
- coffee_dependence_line (a line across districts) is replaced by F3, which shows the distribution across households.
