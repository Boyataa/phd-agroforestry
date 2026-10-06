# house_valuation_clean
Source: `House.ipynb` cell 10. Script: `scripts/morefigures/housing.py`. Questions are owner estimates: "cost to build this house" and "rent of a similar house in this village per month". They are not transactions.

| New figure | Shows | Replaces |
|---|---|---|
| `valuation_by_district.png` | build cost, monthly rent, build cost ÷ annual rent by district (log axes) | `build_cost_million_trimmed_boxplot`, `monthly_rent_thousand_trimmed_boxplot`, `build_to_rent_ratio_trimmed_boxplot`, `median_build_cost_line_scatter` |
| `valuation_by_li_group.png` | build cost and rent by LI group (dots coloured by district) | new (LI complement) |
| `build_vs_rent_scatter.png` | build cost vs rent, log-log, with 10- and 50-year lines | `build_cost_vs_rent_trimmed_scatter` |
| `house_age.png` | house age by district and LI group | `house_age_trimmed_boxplot` |

**Trimming rule (stated in each figure note).** Values outside a plausible range are set to missing *per variable*:
- build cost 100k–100M UGX (4 values dropped: 20k, 50k, 90k);
- rent 5k–2M UGX/month (4 dropped: 15, 2,000, 3M, 30M);
- year built 1950–2025 (6 dropped).

There is no 5–95 percentile trimming; log axes show the skew instead. See `cleaning_rule_values_set_missing.csv`.

**What changed and why**
- The old rule had an upper limit of 50M and dropped households *jointly*: a household lost its build cost if its rent was missing, and the top and bottom 5% of all three variables were then cut. This removed real Mukono houses (95th percentile 70M) and changed the n between plots.
- House age now uses the survey year 2025 (the old code used 2026).
- The median line across categorical districts is replaced by the median labels on the strip plots. The median table is `house_valuation_summary.csv`.
- Results:
  - Mukono houses are valued higher: median build cost 9.5M vs 6M UGX, and rent 100k vs 70k per month (both p<0.001). The ratio is about 6–7 years of rent in both districts (p=0.55).
  - Build cost and rent agree well in Mukono (Spearman 0.70) but poorly in Nakaseke (0.28), so Nakaseke valuations are less consistent.
  - Households at or above the living income report a higher build cost (median 19M) and rent (Kruskal p<0.001 and p=0.03).
