# land_vs_coffee (old notebook: Farm Dynamics.ipynb, cell 1)
| New figure | Shows | Replaces |
|---|---|---|
| `land_vs_coffee.png` (+ `land_vs_coffee_households.csv`, `coffee_share_of_land_summary.csv`) | (a) land owned vs coffee area, log-log, by district, with a 1:1 line and Spearman rho; (b) median coffee share of land by LI group and district | `land_vs_coffee_scatter` |

What changed and why
- No 95th-percentile trimming. Land > 500 acres set to missing (cleaning rule). n = 590.
- Log axes and slight jitter, because the areas are heaped at 0.25/0.5/1/2 acres.
- 2 HH report more coffee than land owned (probably rented-in land); they are kept.
- Added coffee share by LI group (median about 50% throughout; Kruskal p = 0.09). The coffee_intensity column from the old version is now `coffee_share_pct` in the household CSV.
