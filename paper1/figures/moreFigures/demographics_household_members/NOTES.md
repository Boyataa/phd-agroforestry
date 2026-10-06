# demographics_household_members (roster) - redo
Source: `Generic Dataset Analysis.ipynb` cells 24-27, 38, 40 (they used `household_members_long.csv`, built from the Excel-damaged file). Script: `scripts/morefigures/demographics.py`.

The roster has up to 6 member rows per household. Age groups are the KoBo codes restored in cleaning (0_5, 6_15, 16_25, 26_40, 41_60, 61_and_above). 576 of 597 HH have at least one roster row, and 1,860 members are listed.

| New figure | Shows |
|---|---|
| `roster_age_structure_by_district.png` (+csv) | Listed members by age group and district, split into resident and non-resident. |
| `household_composition_by_district.png` (+csv) | Distribution of resident adults, children and household size per HH, by district (Mann-Whitney). Uses the same definitions as the living-income benchmark (`Household_Analysis_v1`). |
| `relationship_and_age_of_members.png` (+ `relationship_to_head_by_district.csv`, `age_by_relationship.csv`) | (a) relationship to head by district; (b) relationship x age-group counts. |
| `dependency_ratio_by_district.png` (+csv) | Household dependency ratio (children + 61+) / (adults 16-60): median 2.0 Mukono vs 1.5 Nakaseke, Mann-Whitney p < 0.001. |

**Changes vs the old figures**
- **Age codes.** The old notebooks read age groups after Excel had turned them into numbers. They then expected labels like "6-15" and so dropped the 0_5 group entirely. Now all six restored codes are used.
- **Children and household size.** Mukono rosters list **no one under 16**: Mukono child counts come from the schooling section (cleaning log §2). Because of that:
  - The old "household size" (number of roster rows, capped at 6, with no Mukono children) was wrong. Household size now = resident adults + cleaned children count.
  - The old `district_age_structure_with_derived_mukono_6_15` replaced Mukono 6-15 with the summed *elementary-school* count. That is neither all 6-15-year-olds nor only them, and it excluded values > 15 ad hoc. It is replaced by the children panel of `household_composition_by_district`.
- **Merged and dropped variants.**
  - Age-structure variants (`_original`, `_no_missing`, `_line`, `district_age_*` incl. `_updated`, `_percent`, `_with_combined`) are merged into one figure. Line plots across age groups were removed.
  - `relationship_structure`, `relationship_line`, `age_relationship_heatmap(_no_missing)` and `age_relationship_scatter` are merged into one two-panel figure.
  - `dependency_scatter` is dropped. It plotted the share of "dependents" within each age group, which is 0 or 1 by definition. It is replaced by the household-level dependency ratio.
  - `household_size_scatter` (household index vs size) is dropped: it carries no information.

**Data issues found**
- **No "spouse" code.** 153 HH list two or more members as house_head, mostly a male-female pair. "Head" therefore includes spouses, and head counts > 597.
- **Non-resident members in Mukono.** 32% of listed Mukono members are non-resident, vs 4% in Nakaseke. Most are aged 26-40, probably adult children living elsewhere. Only residents enter adults and household size.
- **Roster cap.** The roster is capped at 6 rows (56 Mukono / 53 Nakaseke HH filled all 6), so adults may be undercounted in large households.
- **0-5 members counted as adults (not fixed here).** `scripts/obj1/build_household_analysis.py` excludes only 6_15 from adults. The 24 resident roster members coded 0_5 (Nakaseke) are therefore counted as **adults**, on top of the children count. This slightly inflates adults / household size / benchmark for those Nakaseke households. It should be fixed in the shared builder (not edited here, per brief).
- **Missing data.** 45 listed members have no relationship code and 30 have no age group. They are excluded only from the panel concerned.
