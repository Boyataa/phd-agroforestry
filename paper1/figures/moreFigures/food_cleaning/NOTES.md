# food_cleaning (old notebook: FoodAnalysis.ipynb)
Script: `scripts/morefigures/food_prices_gap.py`. Tables only.
- `food_comments_long.csv`: one row per household x food group with a food-source comment, for the 597 analysis households. Columns: district, food group, comment text, usable flag (more than 2 characters), keyword codes (as Table D2).
- `food_comments_by_group.csv`: households with a comment per food group and district (n and % of all households in the district).
- `food_comments_counts.csv`: 940 non-empty comments, 933 usable, 7 junk/blank.

**What changed:** the old notebook treated the 11 `group_wg2nh50_*_food_source_comments` columns as yes/no or numeric and converted them to 0/1/None. They are free-text comments, so the "cleaned" file it produced was empty of information. They are now kept as text and coded with the same keyword rules as `scripts/obj1/module_d_living_conditions.py` (D2). The sample is the 597 analysis households, so the 3 interviews without a district are dropped. The survey has no structured food-source column, only the comments.

**Data issue:** in Mukono, comments exist for 82 of 297 households, and most of them are about dairy (69). In Nakaseke, 196 of 300 households have a comment. Mukono comments therefore cannot support district shares.
