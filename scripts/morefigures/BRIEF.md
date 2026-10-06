# Brief for re-running Ezra's earlier Objective 1 analyses (moreFigures)
Repo: /home/claude/phd-agroforestry (do NOT git commit/push; do NOT edit anything outside your own files listed below; do NOT touch paper1/figures/*.png, paper1/tables, data/, scripts/obj1 etc.).
Old notebooks (read-only source of WHAT was analysed): /mnt/user-data/uploads/Objective_1/*.ipynb (some old output csv/txt in /mnt/user-data/uploads/Objective_1/output/). Old figure names per folder are listed in your task.

## Goal
For each old output folder assigned to you, re-run the SAME analysis on the NEW cleaned data, FIXED where the old one was wrong, and write outputs to
  paper1/figures/moreFigures/<old_folder_name>/   (PNG figures 300 dpi + CSV tables behind each figure)
via ONE script per group: scripts/morefigures/<group>.py, run as `python scripts/morefigures/<group>.py` from repo root (paths relative to repo root via Path(__file__).resolve().parents[2]). Deterministic. Must run without error in < 3 min.
Also write paper1/figures/moreFigures/<old_folder_name>/NOTES.md (short): which old notebook, what each new figure shows, what changed vs the old version and why, old figures dropped/merged and why.

## Data (use these, not the old files)
- data/derived/Household_Analysis_v1.csv — one row per household, 597 HH (297 Mukono, 300 Nakaseke). Columns: district, Sub_County, enumerator, hh composition (adults, children, hh_size, dependency_ratio, female_head, resp_edu..., married), land_owned_ac, coffee_ac, trees_on_farm (Namyenya's counts already NaN: trees_count_unreliable), yields (coffee_yield_faq_ac; >5000 already NaN), kiboko_price, income by source inc_*_mi (mean of 20 imputations, UGX/yr; inc_othercrops = Q162e SALE OF OTHER CROPS, not tree income), income_total_mi (cash), inkind_food_central (home-grown food), tree_inkind, gross (= cash + in-kind), cost_central, net_central, bench_ref_year / bench_hh_year (living income benchmark v0.02: Mukono 20.17M, Nakaseke 19.78M for 2 adults+3 children; bench_hh = household-size specific), ratio_ref/ratio_hh (% of benchmark), li_group (<25%,25-50%,50-100%,>=100% of hh benchmark).
- data/derived/Survey_Cleaned_v1.csv — all original survey columns (KoBo names) + cleaned vars (children_clean, floor_area_m2, floor_area_m2_model, inc_*_clean...). 600 rows: KEEP ONLY the 597 with District in {mukono, nakaseke} (merge on _id with Household_Analysis to get the analysis sample).
- data/derived/Survey_Income_MI_v1.csv (20 imputations, for any inference), data/derived/Household_Net_Gap_v1.csv, Production_Costs_v1.csv, Market_Prices_Tidy_v1_1.csv (market prices; local-unit guesses in price_std_guess), data/raw/ (raw files incl. benchmark workbooks v0.01, market survey).
- Docs on decisions: docs/logs/*.md, docs/decisions/*.md, docs/project-brief.md. Read cleaning-log-v1.md and obj1-analysis-log-v1.md first.

## Fixed rules (apply everywhere)
- Sample 597 HH; never invent numbers. Income = cleaned imputed income (inc_*_mi); show cash vs incl. home-grown food where relevant. Benchmarks: v0.02 only (old notebooks used 4.9M/5.07M/7.07M — wrong).
- Q162e is "sale of other crops"; tree product values come from Q168–170 (see scripts/obj1/module_c_coffee_trees.py for how tree products are read).
- Nakaseke recorded floor area is ft² and unreliable → use floor_area_m2_model for cross-district comparisons. Enumerator "housing below standard" judgement is not comparable across districts.
- Namyenya's tree counts are excluded (already NaN). Respect existing flags; don't re-clean differently from the cleaning log without saying so in NOTES.md.
- Drop superseded variants (e.g. "original" vs "corrected"/"clean" versions → keep the corrected one only). Don't draw lines across categorical x-axes (use bars/dots); merge duplicate views of the same numbers into one good figure. Pies → bar or 100%-stacked bar. Every figure: title stating what it shows (not a conclusion it can't support), axis labels with units, n in a note.
- Style: `sys.path.insert(0, <repo>/scripts/obj1); from li_style import *` and use its palette (DIST colours for districts, SRC for income sources in fixed order, ORD4 for LI groups), money() formatter and save(fig, path, note). matplotlib only.
- Percentages over the households with a valid answer; report n. Where you test differences use the same tests as scripts/obj1 modules (chi-square / Kruskal / Mann-Whitney).
- If an old analysis cannot be redone (data not in the survey), say so in NOTES.md and skip it.

## Return to the caller (final message, short)
Per folder: figures written (count), key changes vs old, anything you could not redo, any data problem found. Confirm the script runs cleanly.
