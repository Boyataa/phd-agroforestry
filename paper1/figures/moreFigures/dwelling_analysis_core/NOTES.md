# dwelling_analysis_core
Source: `House.ipynb` (cells 0–4) and `Generic Dataset Analysis.ipynb` (dwelling cells 29–36). Script: `scripts/morefigures/housing.py`. Sample 597 HH; % over valid answers; tests: Mann-Whitney (district), Kruskal-Wallis (income groups), chi-square (categorical).

| New figure | Shows | Replaces |
|---|---|---|
| `household_size.png` | household size by district and by LI group (dots, IQR, median) | `clean_household_size` |
| `floor_area_recorded_vs_model.png` | recorded vs modelled floor area per district (log) | `avg_house_size_line`, `house_size_scatter` |
| `floor_area_crowding_by_li_group.png` | modelled floor area, m² per person, persons per bedroom by LI group | `avg_house_size_adjusted_line(_scatter)`, `house_size_adjusted_scatter`, `house_size_adjustment` |
| `dwelling_type.png` | permanent / semi-permanent / other, 100% bars by district and LI group | `dwelling_type_line` |
| `drinking_water_source.png` | main drinking-water source, 100% bars | `water_source_line` |
| `cooking_energy_source.png` | main cooking fuel, 100% bars | `energy_source_rates`, `energy_source_by_district_line` |

Extra table: `dwelling_characteristics_pct.csv` (permanent dwelling, brick walls, cement floor, toilet/kitchen/water inside, by district and LI group).

**What changed and why**
- Floor area: the old notebook treated all values as ft², dropped values outside 50–5000 ft² and then added +5 m² (or +10 m², inconsistent between cells) to houses under 20 m². Per the cleaning log, Mukono recorded m² and Nakaseke ft² (unreliable, bunched at ~18 m²). Now: recorded values shown only to document the problem; comparisons use `floor_area_m2_model` (Mukono median 68 m², Nakaseke 61 m²). The arbitrary +5/+10 m² adjustment is dropped. Modelled area is predicted from rooms and materials, so it is not an independent measurement.
- Household size now comes from the cleaned roster in `Household_Analysis_v1` (mean 5.6 Mukono, 4.8 Nakaseke) instead of counting roster rows with a ≤15 cut-off.
- Lines across categorical axes replaced by 100%-stacked bars; household-index scatters removed (they show nothing). Income-group (li_group) rows added to every figure.
- Electricity figures (`electricity_scatter`, `district_electricity_line`, `electricity_boxplot`) are merged into `../electricity_analysis/electricity_access.png` (a 0/1 boxplot is not meaningful). `water_distance_scatter` moved to `../water_analysis` (its old version read text like "500m" as missing and mixed units).
- Key results: larger households are poorer (median 6 persons in <25% vs 3 in ≥100%), so m² per person and persons per bedroom improve with income (Kruskal p<0.001), while total floor area barely does. Dwelling type differs by district (Mukono 30% semi-permanent vs Nakaseke 6%) but not by income group (p=0.49). Firewood is used by 93%.
- Caution: income-group rows pool both districts, and Nakaseke dominates the <25% group.
