# income_sources
Old notebook: `Income_sources.ipynb` (cell 0). Script: `scripts/morefigures/income.py` (run from repo root). Data: `data/derived/Household_Analysis_v1.csv` (597 HH) + `Survey_Cleaned_v1.csv` (Q168-170 tree products, tree-plantation acres). Income = cleaned imputed Q162 a-h (`inc_*_mi`, mean of 20 imputations); in-kind = home-grown food (`inkind_food_central`) + non-food tree products used at home (`tree_inkind`), as in gap v1. Benchmarks = v0.02 (Mukono 20.17M, Nakaseke 19.78M UGX/yr, reference household).

## New figures
- `income_by_source_mean_by_district.png`: mean UGX/HH/yr for the 8 cash sources and the 2 in-kind components, by district. Table `income_by_source_summary.csv` adds the median, % of households earning, the median among earners and the shares.
- `income_share_by_source_district.png`: share of mean income by detailed source, cash only vs incl. in-kind, for Mukono, Nakaseke and both.
- `participation_and_source_count.png`: % of households earning from each cash source, and the number of cash sources per household (chi-square by district, p = 0.085).

## Changes vs old
- Raw Q162 with blanks = 0 on 600 rows replaced by cleaned and imputed income on 597 HH. Old totals (sum over households) are replaced by means per household.
- In-kind income is added. Q162e is labelled "other crop sales", not tree income.
- Coffee falls from 65% of cash to 43% of income incl. in-kind.

## Dropped or merged
- Merged into F1 (same numbers shown five ways): overall_income_by_source_bar, overall_income_composition_line (a line across categories), overall_income_composition_pie (a pie), average_household_income_by_source.
- district_income_sources_stacked_bar becomes F2. Old totals were stacked in UGX; F2 shows shares, and UGX per district is in F1.
- correlation_heatmap is moved to income_correlation.
