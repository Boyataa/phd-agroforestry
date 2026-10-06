# farm_analysis (old notebook: Farm Dynamics.ipynb, cell 0)
Script: `scripts/morefigures/farm_trees.py`. Sample: 597 HH (Household_Analysis_v1 + Survey_Cleaned_v1).

| New figure | Shows | Replaces |
|---|---|---|
| `land_owned_by_district_li_group.png` (+csv) | Land owned per HH by district (box + points, log scale) and median land by living-income (LI) group within each district. Mann-Whitney between districts, Kruskal across LI groups | `land_size_boxplot` |
| `land_tenure_by_district_li_group.png` (+csv) | Form of ownership (mailo/kibanja, freehold, customary, does not own) as 100% bars by district and LI group, with chi-square tests | `ownership_type_stacked_bar` |

What changed and why
- Land: uses `land_owned_ac` (values > 500 acres set to missing; one record of 120,000). The old version cut the top 5% (95th percentile), which removed real large farms. No trimming now. n = 592.
- Both districts have a median of 2 acres. Nakaseke farms are larger on average (mean 3.4 vs 2.4; Mann-Whitney p < 0.001). Land rises clearly with the LI group: in Mukono the median goes from 1 acre (<25%) to 5 acres (>=100%), and in Nakaseke from 2 to 6 acres.
- Tenure: the old chart stacked 'own yes/no' against tenure type in counts. Here tenure and 'does not own' are combined into one category set, shown as % of valid answers (589). All 17 non-owners are in Nakaseke. Customary tenure is 30% in Mukono and about 0% in Nakaseke, while freehold is 8% vs 33%. Districts p < 0.001; LI groups p = 0.049.
- Added the LI group breakdown.
