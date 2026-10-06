# tree_products (old notebook: Tree Income vs Cofffee.ipynb, cells 0-6)
Tree products are read from Q168-170 as in `scripts/obj1/module_c_coffee_trees.py`: up to 3 products per HH; the most recent harvest year per product; price = Q169 (`_169_Farmgate_Price...`), falling back to `Farmgate_Price_for...`; home use capped at the quantity harvested. Value = quantity x price. Sold = (harvest - home) x price. Long table: `tree_products_long.csv`.

| New figure | Shows | Replaces |
|---|---|---|
| `tree_products_reported.png` (+csv) | % of HH reporting each product, by district (annual crops shown but marked as not a tree product) | `tree_product_frequency`, `tree_products_clean` (merged) |
| `tree_product_value.png` (+csv) | Median value harvested per reporting HH by product and district; share of total tree-product value | `tree_product_grouped_no_annuals`, `tree_product_percentage`, `tree_product_income_bar` |
| `tree_product_home_vs_sold.png` (+csv) | Mean share of the harvest used at home vs sold, by product (district split in CSV) | `tree_product_consumption_vs_sold` |
| `tree_products_by_li_group.png` (+csv) | % of HH harvesting tree products and median value sold, by LI group within district | new; links to living income |

What changed and why
- Old 'grouped' and 'percentage' charts summed farm-gate unit prices across households, which is not a value. They now use quantity x price.
- Old income bar (table `tree_product_income_summary.csv`) was all zeros. The old code read only `Farmgate_Price_for...` (37 prices) and missed Q169 (338 prices).
- Old code used row index as the HH id and kept every repeat. Now the code uses `_id`, the 597-HH sample and the most recent year per product, following module C.
- Product names are fixed KoBo options, so the old keyword grouping ('Other') is no longer needed.
- New data rule (not in module C): 36 records whose value for a single product is greater than the household's whole gross income are left out of value statistics, because the price was probably entered as a total. Module-C medians without this rule are kept in `tree_product_value.csv` for comparison.
- Annual crops are excluded from tree-product totals and from the LI figure. Including annuals gives 69% / 73% reporting any product (= module C); without them it is 43% (Mukono) / 58% (Nakaseke).
- Q162e ('sale of other crops') is not treated as tree income.
