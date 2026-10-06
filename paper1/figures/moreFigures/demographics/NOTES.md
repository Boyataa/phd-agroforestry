# demographics (respondent) - redo
Source: `Generic Dataset Analysis.ipynb` cell 23 (gender/education/marital/district distributions) and the education x gender / marital bar-line figures (per district). Script: `scripts/morefigures/demographics.py`. Sample: 597 HH; percentages over valid answers (1-3 missing per item).

| New figure | Shows |
|---|---|
| `respondent_profile_by_district.png` (+csv) | 100%-stacked bars by district for sex, age band, marital status and education of the respondent, with a chi-square test per item. All differ between districts (sex p = 0.009, others p < 0.001). |
| `education_by_sex.png` (+csv) | Education distribution by sex within each district. Chi-square uses education collapsed to none / primary / secondary+. |
| `education_by_marital_status.png` (+csv) | Education distribution by marital status within each district, with the same test. |

**Changes vs the old figures**
- **Sample and categories.** The old figures used 600 rows with "Missing" as a category. Now the sample is 597 HH and percentages are over valid answers.
- **District comparison.** The four single-variable count bars (gender, education, marital, district) are merged into one district-comparison panel. `district_distribution` is dropped because it duplicates `data_readiness_assessment/sample_by_subcounty`.
- **Respondent age.** Age is a categorical band (20-29 ... 70+). The old histogram expected a numeric `Age_of_respondent` column that does not exist.
- **Per-district figures.** The bar-line and grouped-bar versions for each district (`education_gender_barline_*`, `education_marital_barline_*`, `education_marital_groupedbar_*`, 6 files) become 2 figures, each with both districts. Lines across categorical axes were removed.

**Data issues**
- **Marital status has no "widowed" option.** Mukono has 26% "other" and 3% "single"; Nakaseke has 26% "single" and 1% "other". Respondents are old (41% / 27% aged 60+), so both residual categories probably hold widowed respondents, recorded differently in each district. Only "married" is comparable across districts (57% vs 69%).
- **Education spelling.** The survey code is spelt `seconary` (shown as Secondary).
- **Respondent vs household head.** These figures describe the respondent, not the household head. Head gender is in Household_Analysis (`female_head`).
