# living_income_gap_mukono (old notebook: incomeGap-Mukono.ipynb, cell 0)
Script: `scripts/morefigures/food_prices_gap.py`. Data: `Household_Analysis_v1.csv`, where net income comes from `Household_Net_Gap_v1` (central).
- `living_income_gap_summary.csv/.tex`: Mukono, Nakaseke and all households. The table gives:
  - the reference and household-size benchmarks (v0.02);
  - means and medians of cash income, home-grown food, tree products used at home, gross income, production costs and net income;
  - median income as % of the household benchmark;
  - % below the benchmark (cash only, gross, net; reference and household-size);
  - the median and mean gap.

  District tests: Mann-Whitney for incomes and ratios, chi-square for % below.
- Key numbers (Mukono / Nakaseke):
  - median gross 5.54M / 3.90M; net 4.00M / 2.57M UGX/yr;
  - median 26.5% / 20.1% of the household benchmark (gross), 17.6% / 13.6% (net);
  - below the household benchmark: 93.6% / 95.7% gross, 96.0% / 98.7% net;
  - median gap to the household benchmark 13.7M / 13.0M (gross), 14.8M / 14.7M (net).

**What changed:**
- The old table was Mukono only, with a benchmark of 5.07M/yr (398,076/month), which is wrong.
- It used raw Q162 cash income with blanks set to 0, and reported a mean gap of -69,522, i.e. above the benchmark on average.
- Now: both districts, the v0.02 benchmark (20.17M / 19.78M for 2+3, scaled to household size), cleaned and imputed income, and gross incl. in-kind and net shown side by side. Medians are reported because incomes are very skewed.
