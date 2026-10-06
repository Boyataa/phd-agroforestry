# costing (old notebook: modalDietCosting.ipynb, "Modal Diet Cost")
Script: `scripts/morefigures/food_prices_gap.py`. Tables only (csv + tex).
- `benchmark_components_v002.csv/.tex`: benchmark components v0.02 (housing, food, NFNH, elder care, margins) for the reference household of 2 adults + 3 children, with the v0.01 total for comparison. Values come from `docs/logs/benchmark-rebuild-log-*.md`.
- `model_diet_cost_v002.csv/.tex`: cost of the tool's model diet per adult male per day: 4,802 UGX in Mukono and 4,332 UGX in Nakaseke. With +20% for salt, waste and variability this becomes 5,763 / 5,199 UGX per day, or 175k / 158k UGX per adult male per month. The household food cost is 713,711 / 643,882 UGX per month. The table also shows the v0.01 and old-notebook values.
- `model_diet_items_v002.csv`, `model_diet_items_<district>_v002.tex`: the 19 model-diet slots, with grams per day, price per kg, cost per day and price source.
- `food_price_inputs_v002.csv`: for each tool item, the market prices used (n, lowest, median) and their basis (the build_benchmark food price log).

**How the v0.02 numbers were obtained:** the v0.02 workbooks are not in the repo. The script rebuilds them in a temporary folder with the repo's own `scripts/benchmark/` scripts (build_participants, then build_benchmark, then the xl_compat test copy), recalculates them with LibreOffice and reads the model diet. The rebuilt components must match the published log values to within 1 UGX, and they do: food is 713,711 / 643,882. Without LibreOffice, only the component table, taken from the logs, is written.

**What changed vs the old notebook:** the old notebook had its own 13-item "modal diet" (AP grams typed in) and priced it at the **mean of all raw prices** for each item. Those prices mixed kg, pieces, trays and local units and included non-food items. It gave 167k / 172k UGX per month, with no household scaling and no link to the benchmark. That diet is dropped. The diet is now the benchmark tool's own model diet: it meets a 2,767 kcal energy target and is priced at the tool's rule, the **lowest** usable July 2025 district market price. This is the food component of the v0.02 benchmark.

**Things to know:**
- The tool fills its model-diet slots with the cheapest item in each category, so some items appear twice: drybeans and pineapple in Mukono; soy, pineapple and 3x spring onions in Nakaseke. v0.01 did the same.
- Several slots keep the tool's placeholder prices because they have no market price: fish, sukuma, spring onions, pineapple, soda and kombucha at 1,000 UGX/kg, and mukene. See the log.
- Because the tool uses the lowest observed price, Mukono milk is priced at 2,000 UGX/litre against a median of 5,000.
