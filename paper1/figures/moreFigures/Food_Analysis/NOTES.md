# Food_Analysis (old notebook: marketPrices.ipynb, cells 1-4)
Script: `scripts/morefigures/food_prices_gap.py`. Tables only (no figures, as before).
- `groups_by_district.csv`: number of food price observations by district and food group (plus items and markets).
- `group_summary.csv`: observations, items and districts per food group, plus how many prices are outlier-flagged and how many are in local units (kg factor guessed).

**What changed:** the source is now `data/derived/Market_Prices_Tidy_v1_1.csv` (665 rows, 8 visits) instead of the raw wide file. Non-food items (soap, pads, contraceptives, baby oil, antenatal vitamins) are excluded. Food groups follow the questionnaire categories, with readable names. Before, every column containing "price" was counted, including non-food items.
