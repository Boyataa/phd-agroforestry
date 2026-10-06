# water_analysis
Source: `Water.ipynb` (cells 0–2) plus `water_distance_scatter` from `Generic Dataset Analysis.ipynb`. Script: `scripts/morefigures/housing.py`.

| New figure | Shows | Replaces |
|---|---|---|
| `distance_to_water_by_district.png` | distance (m) by district, ≤3.5 km | `avg_distance_to_water_by_district`, `_trimmed_3500m`, `distance_to_water_boxplot_by_district`, `_trimmed_3500m`, `distance_to_water_scatter`, dwelling_core `water_distance_scatter` |
| `water_access_by_li_group.png` | distance and time to water by LI group | new (LI complement) |
| `distance_vs_time.png` | distance vs time per household (unit check) | new (replaces index scatters) |
| `water_cost.png` | daily water cost (payers, log) by district and LI group, with % paying 0 | `avg_water_cost_by_district`, `water_cost_scatter`, `water_cost_scatter_by_district_no_outliers`, `water_cost_boxplot_by_district_no_outliers` |

Tables: `water_parsed_household.csv` (raw text and parsed value per household), `water_parsing_quality.csv`, `distance_to_water_by_district.csv`, `water_access_by_li_group.csv`, `water_cost_by_district.csv`, `water_cost_components_pct.csv`.

**What changed and why**
- **Distance units.** The rule follows `scripts/benchmark/build_participants.py dist()`: Mukono unit-less values ≤20 are km; Nakaseke values are mostly "200meters"/"500m". Several fixes were added:
  - "O.5km" with a letter O, and "0. 5km";
  - "1k" read as km;
  - "Feet 20" converted from feet;
  - "In the compound" set to 0 m;
  - "0.02m" read as km.
  "x soccer pitches" (30 Nakaseke answers) and answers given in minutes are set to missing, as in `dist()`.

  After harmonisation, no household is above 3.5 km. The old >3.5 km values came from unit errors, so the 3.5 km trim is kept only for display. Medians: Mukono 500 m, Nakaseke 300 m (p<0.001).
- **Time to water.** Parsed as module D `to_min()`, with these additions:
  - "One hour" = 60 min;
  - seconds divided by 60;
  - answers in km set to missing;
  - unit-less numbers >180 set to missing (Nakaseke "500", "1000" look like metres).

  This changes the >30 min count in Nakaseke from 33 (module D) to 28. Module D's D1 table is not changed by this script.
- **Water cost.** No IQR outlier removal (the old pooled IQR cut most Nakaseke values). Zero payers are shown as a %, and positive costs are shown on a log axis.
- Lines across categories and household-index scatters were removed. LI-group breakdowns were added.

**Data problems found**
- Nakaseke short distances such as "10m" and "15m" come with 5–30 min walks (`distance_vs_time.png`). There, "m" may mean minutes. The affected households are counted in the figure note.
- Water cost is not comparable across districts:
  - Mukono median 67 UGX/day, and 26% pay nothing; values like 33/67/167 look like monthly amounts ÷30.
  - Nakaseke median 500 UGX/day (about 180k/yr), and only 4% pay nothing.
  - Cost components also differ: collection cost appears in 34% of Nakaseke answers vs 1% in Mukono.
- The income-group gradient in cost mostly reflects the district difference. Check the recall unit with the enumerators before using water cost in the benchmark.
