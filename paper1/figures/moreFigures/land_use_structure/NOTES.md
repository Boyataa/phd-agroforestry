# land_use_structure (old notebook: Farm Dynamics.ipynb, cells 2-5)
| New figure | Shows | Replaces |
|---|---|---|
| `land_use_composition.png` (+csv) | Mean share of each farm's land by use (coffee, other crops, grazing, tree plantations, rented out, other activities, not allocated), 100% bars by district and LI group | `land_use_stacked_percent`, `land_use_radar_chart`, `land_use_spider` |
| `land_use_by_type.png` (+csv) | % of HH using land for each purpose and median acres among users, by district (Mann-Whitney p in CSV) | `land_use_boxplot` |

What changed and why
- Radar and spider charts were dropped. They duplicated the stacked-percent figure, and the brief asks for bars.
- Old stacked bars: shares did not sum to 100%, the 120,000-acre record was not removed, and missing items were dropped silently. Now the denominator is land owned (> 500 acres = missing) or the sum of the listed uses where that is larger (32 HH list more use than land owned, probably rented-in land). The remainder is shown as 'not allocated' (homestead, fallow, unrecorded). Missing use items are counted as 0 for a HH that answered at least one item. 8 entries typed as the letter 'O' are read as 0.
- Land rented in is left out: only 29 HH answered it.
- The old pooled boxplot was mostly zeros. It is replaced by % of HH using each purpose plus area among users.
- Data note: 'Other crops' is > 0 for 57% of Mukono HH vs 96% of Nakaseke HH. Grazing (6% vs 44%) and tree plantations (2% vs 38%) also differ a lot. Some of this may be because enumerators recorded these items differently; it should be checked before interpreting.
