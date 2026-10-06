# Data cleaning and imputation: methods summary

_Condensed from `data/cleaning-log-v1.md`; reproduced by `data/clean_survey.py` (fixed random seed). Draft text for the thesis methods._

**Data.** Household survey of 600 Robusta coffee farmers (Mukono 297, Nakaseke 300, 3 with no district recorded), collected September–December 2025 with KoBo. All cleaning was scripted so it can be repeated from the raw files, and every altered value has a flag column.

**1. Repair of format corruption.** Re-saving the file through a spreadsheet had truncated the interview timestamps and turned age-group categories into numbers (e.g. "26_40" became 2640). Both were restored by joining to the original KoBo export on the unique questionnaire ID. The restored age groups were checked against the original and were identical in every non-missing cell.

**2. Household composition.** Child counts in Mukono were derived from the schooling section, and the large Mukono values (13–15) agree with the number of children in school. Three implausible Nakaseke counts (36, 58, 350) were treated as keying errors and replaced by their leading digit (3, 5, 3), which is never below the number of children reported in school. Missing counts (17) were set to the number of children in school, which is a lower bound; 11 remain missing.

**3. Floor area.** Recorded areas were not on one scale (median 64 in Mukono, 198 in Nakaseke). Mukono values behaved like m² (Spearman correlation with rooms 0.70, with rent 0.64). Nakaseke values were consistent with ft² but tightly clustered (IQR 17–20 m² after conversion) and almost unrelated to rooms (0.20) or rent (0.08), which suggests estimates rather than measurements. We (i) converted Nakaseke values to m² and flagged them as low reliability, and (ii) predicted floor area for all households from a log-linear model of rooms, bedrooms, dwelling type and wall and floor material, fitted on Mukono (n = 285, in-sample R² = 0.62) with a lognormal back-transformation. The prediction assumes the same relationship between house characteristics and area in both districts, and predicted values are shrunk toward the mean, so they are for comparison and not measurements.

**4. Income.** Annual income from eight sources. Sixty-four households (62 in Nakaseke) had no income figures, mostly interviewed on 1–9 September 2025. That pattern suggests a questionnaire-version problem rather than refusal, so we assumed data missing at random given district and household covariates (this cannot be tested).
- A source the household did not list was set to zero; among respondents, no unlisted source ever had an amount.
- Missing coffee income was replaced by the sum of reported seasonal coffee sales. This equals the annual figure for 66% of households reporting both (median ratio 1.0) and assumes the seasonal fields are household totals.
- Remaining listed but blank sources were imputed by predictive mean matching on log amount, one model per source. Predictors: district, log land, log coffee income, number of children, respondent age band. Five nearest donors, bootstrapped coefficients, 20 imputations.
- For 17 households that skipped the income-source question entirely, each source was imputed on log(1 + amount) across all households, so that zeros are possible.

In total 81 households have at least one imputed component (Nakaseke 75, Mukono 6). Descriptive statistics use the mean of the 20 imputations; model-based results should be estimated on each dataset and pooled with Rubin's rules, with a sensitivity analysis that excludes imputed households.

**Limitations.** Income is gross, and the recall period is not yet confirmed. Sources were imputed independently, so correlation between them comes only from the shared predictors. The floor-area model extrapolates from Mukono to Nakaseke.

**References.** Little, R.J.A. (1988) Missing-data adjustments in large surveys. *J. Business & Economic Statistics* 6, 287–296. Rubin, D.B. (1987) *Multiple Imputation for Nonresponse in Surveys*. Wiley. van Buuren, S. (2018) *Flexible Imputation of Missing Data*, 2nd ed. CRC Press.
