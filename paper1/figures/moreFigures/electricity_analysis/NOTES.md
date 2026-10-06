# electricity_analysis
Source: `House.ipynb` (cells 5–7). Script: `scripts/morefigures/housing.py`.

| New figure | Shows | Replaces |
|---|---|---|
| `electricity_access.png` | grid / solar only / neither, by district and LI group (100% bars) | `electricity_access`, `_by_district`, `_full_sample` (+ dwelling_core `electricity_scatter`, `district_electricity_line`, `electricity_boxplot`) |
| `electricity_purpose.png` | % using electricity for each purpose, by district and by grid vs solar | `electricity_purpose`, `_grouped`, `_grouped_corrected`, `_by_district_corrected`, `_binary_boxplot`, `_boxplot_counts` |
| `electricity_use_intensity.png` | number of named purposes per household, by district and LI group | `electricity_use_intensity_boxplot` |

Extra table: `grid_bill_per_month.csv` (stated grid bill, grid households; median 13k UGX/month Mukono, 20k Nakaseke).

**What changed and why**
- Access now separates grid from solar-only (taken from "other sources of electricity"). Only 22% have grid, but about 68% have solar only, so a grid yes/no figure understates access to some electricity. Access does not differ by income group (chi² p=0.58).
- Purposes: the old code kept only grid "yes" households, but the purpose question was answered by 372 households, 222 of them solar-only. All answering households are now kept. Purposes are read from the KoBo codes (not keyword matching) and reported as % of households, not % of mentions. "Other" is unspecified: 47% in Mukono, 0% in Nakaseke, so it looks like an enumerator/form difference.
- Six purpose figures (counts, % of mentions, 0/1 boxplots, by district) showed the same numbers. They are merged into one dot plot. Boxplots of 0/1 indicators and of counts across two districts are dropped as not meaningful.
- Intensity counts named purposes only ("other" excluded, because it is recorded only in Mukono).
