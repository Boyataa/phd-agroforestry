# data_readiness_assessment (redo)
Source: `Generic Dataset Analysis.ipynb` (cells 1-22). Script: `scripts/morefigures/demographics.py`. Sample: 597 HH (Mukono 297, Nakaseke 300).

| New figure | Shows |
|---|---|
| `sample_by_subcounty.png` (+csv) | Households per sub-county, coloured by district: Nabaale 149, Kimenyedde 148, Kikamulo 153, Kasangombe 146, 1 Nakaseke HH without a sub-county. The csv also gives the number of parishes. |
| `section_completeness.png` (+csv) | Mean % of core questions answered per household, by survey section and district. The csv lists the items in each section and the % of HH with every core item answered. |
| `gps_households.png` (+ `gps_summary_by_subcounty.csv`, `gps_points_rounded_2dp.csv`) | GPS fixes (595/597) by district and sub-county. Equal-degree axes, no basemap. |

**Changes vs the old figures**
- **Sample.** The old figures counted the full 600-row file, including 3 HH without a district. The district bar and the sub-county bar are merged into one figure.
- **Section completeness.**
  - The old figures averaged the fill rate over *all* columns of a section, taken from a `Column_Dictionary.csv` that is not in the repo. That counted follow-up, "please specify" and repeat-row columns, where blanks are expected, so the sections looked incomplete for no real reason.
  - Now each section has a fixed list of always-asked core questions (listed in the csv).
  - Village is taken from `Village_Cell` *or* the parish-specific `SECTION_A/f_Village_Cell_*` columns (KoBo cascade). Read from `Village_Cell` alone, Nakaseke shows 68% instead of ~100%.
  - Six variants (clean / final / horizontal_bar / multiline / top20_multiline) are replaced by one dot plot. The line plots across categorical sections were dropped.
- **GPS.**
  - Points come from `GPS_Coordinates`, falling back to `_geolocation` (same values), with a Uganda bounding-box check.
  - The point csv is rounded to 0.01 deg (~1 km) and carries no `_id`, names or enumerator. Exact household coordinates should not be shared.
  - `spatial_summary_with_gps_map` (table plus map) is dropped. Its table is `sample_by_subcounty.csv` and its map is `gps_households.png`.
  - The hexbin variant was not kept.

**Findings and data issues**
- **Mukono** is ~99% complete in every section.
- **Nakaseke is less complete in some sections:**
  - savings 71%;
  - trust/risk items 80%;
  - schooling counts 84%;
  - raw income list / Q162a 87%;
  - food sources 89%;
  - coffee labour 89%;
  - first roster row 92%.
  
  This is consistent with the early-September form version (cleaning log §4). After cleaning, income is complete for all 597 HH (imputed).
- **GPS fixes:** 2 HH have none. 4 fixes have recorded accuracy > 50 m (one is 1,684 m). Median accuracy is 4.9 m.
- **Mukono sub-counties overlap on the map:** Kimenyedde and Nabaale households are spatially interleaved rather than forming two clusters (Nakaseke's two do separate). Either the sub-county was recorded as the respondent's administrative unit rather than the location, or there are entry errors. Check before any spatial analysis by sub-county.
