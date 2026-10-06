# gender_analysis_outputs_standardized: notes
Source: old notebook `Gender.ipynb` (76 PNGs). Redone by `scripts/morefigures/gender_education.py` on `Household_Analysis_v1.csv` (597 HH) and `Survey_Income_MI_v1.csv`.

## Which "gender"
- The old notebook used **respondent** gender (`Gender_Sex`) for every comparison, including income and land.
- Income, land and the living income ratio belong to the household, so they are now compared by **household-head gender** (`female_head`). Head gender comes from the household roster (the member coded `house_head`). In 101 HH no member was coded head, so the respondent's gender is used there (rule in `build_household_analysis.py`). Respondent and head gender agree in 481 of 595 HH.
- Respondent attributes (education, marital status) stay by **respondent** gender (G6).
- 596 HH have head gender: Mukono 134 male- and 162 female-headed; Nakaseke 148 and 152.

## Figures (each PNG has a CSV of the same name)
| Figure | Shows |
|---|---|
| G1 | % female among respondents and among household heads, by district (n on bars). G1b is the respondent × head cross-table. |
| G2 | Cash income, coffee cash income, and cash + home-grown food + tree products used at home, by head gender × district (boxplots, log scale). Mann-Whitney within district, median p over 20 imputations. |
| G3 | **New.** (a) Income incl. in-kind as % of the household-size living income benchmark v0.02, by head gender × district (MW). (b) Share in each LI group (<25 / 25–50 / 50–100 / ≥100%), with chi-square. |
| G4 | Income composition (shares of the group mean, incl. in-kind) by head gender × district. |
| G5 | Land owned, coffee area, trees on farm and number of cash income sources: median and IQR by head gender × district (MW). |
| G6 | Respondent education and marital status by respondent gender × district (100% stacked bars, chi-square). |

## Main results
- **Mukono:** female-headed households are clearly poorer.
  - Median cash income 1.95M vs 3.34M UGX/yr.
  - Living income ratio 25% vs 32%.
  - 7% vs 28% reach half the benchmark (MW and chi-square p < 0.001).
  - They have less land and coffee area, and rely more on home-grown food (46% vs 27% of income).
- **Nakaseke:** no difference in income or ratio (p = 0.55 / 0.92), although female heads also own less land.

## What changed vs the old figures
- Income: the old version used raw Q162 summed with blanks as 0, cash only. Now it uses cleaned, imputed income, shown as cash and as cash plus in-kind.
- Benchmark: there was no benchmark comparison before. The ratio uses v0.02.
- Labels: the old "Tree income" label on Q162e is now "Other crops"; tree products come from Q168–170.
- Tree counts: one Nakaseke enumerator's tree counts are excluded (as in the cleaning log). The old figures included them, inflating Nakaseke trees.
- "Total land components" (sum of several land-use questions) is replaced by cleaned `land_owned_ac`.
- Tests: Mann-Whitney / chi-square added, and n is reported everywhere.

## Old figures dropped or merged
- Count and percent gender distribution, repeated overall / Mukono / Nakaseke (01, 02, gender_distribution_*): merged into G1.
- Mean bar, median bar and boxplot of total income (02/03, 03–05): merged into G2. Means are kept in the CSV.
- Coffee income (04, 06): now a panel of G2.
- Income composition (08, stacked UGX): now G4 as shares, with the mean total labelled.
- Income sources count (07), coffee land (05, 09), total land and land boxplot (10, 11), trees and tree boxplot (06, 12, 13): merged into G5.
- Education level and marital status by gender (07, 08): merged into G6.
- Per-district duplicates are now district panels.
- Monthly education, health and electricity costs were computed in the notebook but not plotted for this folder, so they are not redone here.
