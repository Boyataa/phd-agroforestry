# tree_analysis (old notebook: Farm Dynamics.ipynb, cell 6)
| New figure | Shows | Replaces |
|---|---|---|
| `trees_on_farm_distribution.png` (+ 2 csv) | % of HH by tree-count class, by district (n, medians, Mann-Whitney) | `tree_distribution`, `tree_by_district` (merged) |
| `trees_vs_land.png` (+csv) | Trees on farm vs land owned, log-log, Spearman rho by district | `trees_vs_land` |
| `trees_by_li_group.png` (+csv) | Median trees on farm and trees per cropped acre by LI group within each district (Kruskal) | new; links to living income |

What changed and why
- Namyenya's tree counts (Nakaseke, 100 HH, median 258, probably coffee bushes) are excluded (`trees_on_farm` is already NaN). The old histogram and boxplot included them, which inflated the Nakaseke counts. Nakaseke n = 198, median 6. Mukono n = 295, median 20.
- The histogram and the district boxplot are merged into one grouped-bar distribution.
- Trees vs land: rho = 0.45 in Mukono (p < 0.001) and 0.09 in Nakaseke (n.s.).
- Trees by LI group: in Mukono, trees on farm rise with LI group (20 to 50; p = 0.002) while density is flat. In Nakaseke, density falls with LI group (9 to 1 per acre; p < 0.001). These are associations only, consistent with module C (C3d).
