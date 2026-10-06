# market_prices (old notebook: marketPrices.ipynb; tex tables from modalDietCosting.ipynb)
Script: `scripts/morefigures/food_prices_gap.py`. Data: `Market_Prices_Tidy_v1_1.csv`. The 17 outlier-flagged prices and the non-food items are excluded.

**Figures**
- `market_food_group_prices.png`: median price per kg or litre for each of 33 items, in each of the 4 markets: Kasawo and Nakifuma (Mukono), Kasangombe and Kiwoko (Nakaseke). Items are grouped by food group, on a log scale. Items marked * include local-unit prices converted with the guessed kg factors.
- `heatmap_market_food_groups.png`: relative price index by food group and market (all-market item median = 100). Kiwoko (urban Nakaseke) is dearer for vegetables, roots and matooke (index 133–160). Rural Kasawo is cheaper for dairy and oils.
- `food_group_price_variability.png`: coefficient of variation of each item's price across vendors and visits, by district. Prices of local-unit foods (tomatoes, matooke, sweet potatoes, cassava) vary most. Packaged and staple items (maize, rice, beef, groundnuts) vary under 15%.

**Tables:**
- `district_item_prices.csv/.tex`: n, median, min, max and CV by district for every food item, each in its own unit.
- `market_item_median_prices.csv`
- `market_food_group_price_index.csv/.tex`
- `market_prices_used.csv`: the rows used.

**What changed and why:**
- The old figures took the median of raw prices across all items of a food group. That mixed kg, pieces, trays, bunches and piles, and quantities from 1/2 kg to 50 kg, so a group "price" had no meaning. They are replaced by standardised prices (UGX per kg or litre; pieces and trays kept separate).
- For comparisons between food groups, a unit-free relative index is used.
- The old `combined_`, `mukono_` and `nakaseke_market_food_group_prices` figures were three views of the same numbers as grouped bars. They are merged into one dot plot, `market_food_group_prices.png`.
- The old variability figure (min/max bars plus an SD line on a twin axis across a categorical axis) is replaced by a CV dot plot.
- The old heatmap of raw group medians is replaced by the relative index.
- The old exploratory figures that were not saved (top 10 expensive foods, affordability classes with a placeholder income of 5,000/day, boxplot) are dropped. The affordability index used an invented income.
