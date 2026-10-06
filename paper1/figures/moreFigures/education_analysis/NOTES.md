# education_analysis: notes
Source: old notebook `education.ipynb` (figures `education_correlation_heatmap`, `education_correlation_line`, `education_correlation_multiline_by_district`, and `education_correlation_report.txt`). Redone by `scripts/morefigures/gender_education.py`.

## Figures (each PNG has a CSV of the same name)
| Figure | Shows |
|---|---|
| E1 | Spearman rho between **respondent** education level and each income source, total cash, home-grown food, income incl. in-kind, ratio to the household-size LI benchmark v0.02, net income, number of income sources, land, coffee area, other crops area, tree plantation area, trees on farm, coffee yield, farming years and household size. Shown for Mukono, Nakaseke and both districts, with significance stars. Imputed income: mean rho and median p over the 20 imputations. |
| E2 | (a) Median cash income and median income incl. in-kind by education level × district. (b) Income incl. in-kind as % of the HH benchmark by education level × district (boxplots, log scale). Kruskal-Wallis within district, median p over imputations. |

## Main results
- Education is positively related to:
  - total cash income (rho 0.24 Mukono, 0.32 Nakaseke);
  - coffee income (0.14 / 0.36);
  - the living income ratio (0.20 / 0.29);
  - Nakaseke coffee yield (0.30).
- It is negatively related to remittances (−0.24 / −0.14) and farming years.
- Median ratio to the benchmark rises from about 18–24% (no formal or primary education) to 27–35% (secondary or higher). Kruskal p = 0.004 in Mukono, < 0.001 in Nakaseke.

## What changed vs the old version and why
- **Old education coding was broken.** The old map had no keys for the survey codes `seconary`, `non_formal` or `college_university`. The report therefore used only 331 of ~597 respondents and left out **every** secondary-educated and no-formal-education respondent. Its correlations (e.g. total income 0.10, coffee −0.003) are not valid. Now all 596 respondents with an answer are used.
  - Coding: 0 no formal, 1 primary, 2 secondary, 3 vocational + college/university. These two are merged (n = 27) because the ranking of vocational vs secondary is unclear and the cells are small.
- Pearson on skewed raw income is replaced by **Spearman** on cleaned imputed income. Income incl. in-kind, the ratio to the v0.02 benchmark and net income are added.
- Labels: "Tree Income" (Q162e) is now "Sale of other crops". One Nakaseke enumerator's tree counts are excluded, and yields > 5,000 kg/acre are set to missing (cleaning log).
- The line and multi-line charts drew lines across a categorical list of variables. They are dropped, and their content (rho by district) is now the three columns of the E1 heatmap. E2 adds the direct view of income by education level.
- Education is the respondent's, as in the old notebook. Household-head education (`head_edu`) is missing for 104 HH, so it is not used.
- "Tree plantation area" is the raw survey value (`group_fs0df76/e_Tree_plantations`, mostly 0), because no cleaned version exists.
