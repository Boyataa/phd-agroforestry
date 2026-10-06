# tree_origin (old notebook: Nakaseke.ipynb, cells 13-14)
| New figure | Shows | Replaces |
|---|---|---|
| `tree_origin_by_district_li_group.png` (+csv, + `tree_origin_raw_answers.csv`) | Planted only / both / naturally growing-remnant only, 100% bars by district and LI group, with chi-square | `tree_origin_bar_chart`, `tree_origin_bar_chart_short_labels`, `tree_origin_by_district_stacked_bar` (merged) |

What changed and why
- Multi-select answers such as 'naturally_growing_remnant_trees planted' are now counted as Both. In the old classification they were split inconsistently, and an 'Unknown/Other' category appeared. All 597 HH answered, so no Unknown remains.
- The two versions of the same bar chart (long labels and short labels) and the district stacked bar are merged into one 100% figure with the LI group breakdown added.
- Remnant-only is more common in Nakaseke (27% vs 10%; p < 0.001). Across LI groups, the share of 'both' falls from 85% (<25%) to 55-70% (p < 0.001).
- `trees_planted_any` in Household_Analysis uses the same definition (planted or both).
