# food_constraints (old notebook: foodAnslysisNew.ipynb)
Script: `scripts/morefigures/food_prices_gap.py`.
- `overall_food_constraints_bar.png` (+ `overall_food_constraints.csv`): % of Nakaseke households (n = 300) that name each constraint for any food group. Pests & diseases 48%, price 31%, distance/market 27%, quality 21%, availability 15%, weather 8%, "no constraint" 6%, other (no keyword) 42%. These are the same numbers as paper1 Table D2. Mukono counts are in the CSV.
- `food_constraints_by_food_group.png` (+ `food_constraints_by_food_group_nakaseke.csv`): for each food group, the % of Nakaseke households commenting on that group who name each constraint. Pests dominate for cereals, legumes and roots (58–62%), price and distance for cooking oil and drinks, and quality for dairy (49%). Mukono counts are in `food_constraints_by_food_group_mukono_counts.csv`.

**What changed:**
- Keyword coding now uses the D2 rules from `module_d_living_conditions.py`, not the notebook's longer 12-category list, so results are consistent with the paper.
- Results are shares of households, not counts of mentions, and are for Nakaseke only, because Mukono enumerators recorded comments for few households (82/297, mostly dairy).
- Sample: the 597 analysis households.

**Dropped/merged:** the old bubble scatter and stacked bar showed the same food-group x constraint counts. They are merged into one annotated matrix. Stacking was also wrong here, because one comment can carry several codes. `overall_food_constraints_bar` is kept with the same name.
