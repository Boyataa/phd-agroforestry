# Project brief — Ezra Mwesigwa, PhD (Makerere / Univ. of Copenhagen IFRO)

_Last updated: 2026-10-05 evening (paper draft v2; n = 600 tried and reverted to 597). Kept by Claude so a new thread can start from here. Read this first, then `claude/decisions-log.md`, `claude/decisions-log-gap-v1.md`, `data/gap-log-v1.md`, `data/net-income-log-v1.md`, `data/analysis/obj1-analysis-log-v1.md`, `claude/phd-roadmap.md`._

## Reminders for Claude
- DONE 2026-10-05: net-income v1; Objective 1 analysis v1 (Ezra's notebooks redone); Paper 1 draft v2 (n = 597; a 600-household run was tried and reverted at Ezra's request). Next: Ezra/Aske review draft v2; then Objective 2.
- Ezra's earlier notebooks are on his PC (read-only via the linked desktop): ...\Academic Files\Data Analysis - CAI\Python\Objective_1 and \Objective_2. Goal: "we are re-doing everything here"; analyses must complement the living income results.
- Standing preference: **ask clarifying questions before giving answers**; open questions one by one. Follow the benchmark tool and published methods, do not reinvent.
- Ezra works on his PC: keep files in the cloud container/Project; do not move anything to his machine. The Project accepts text files only.
- Project storage FULL (2 MB cap): large CSV writes are refused. Project CSVs are the 597-household run and current; scripts regenerate everything.
- Paper 1 draft v2 (shared doc): https://claude.ai/code/artifact/2ed7a2b1-ed93-454c-a6c0-b14aa94dc860 (alt https://claude.ai/artifact/6nVMRL3qCFFtg27uXgosXm; blank on Ezra's PC, opens on phone; Word export sent). Ezra's v1 = `Paper Draft.docx` (comments from supervisor Aske Skovmand Bosselmann).
- **Working repository (from 2026-10-06): GitHub `Boyataa/phd-agroforestry` (private)** — raw + derived data, all scripts, logs, Paper 1 outputs, SHAMBA setup. Start each session by cloning it; `python run_all.py` rebuilds Paper 1 identically. Commit and push changes there; the Project keeps the brief and logs.
- `paper1_figures.zip` (sent in chat): run_all.py rebuilds all Paper 1 figures/tables from Standardized_Data.csv + KoBo export; verified identical.

## Research
- **Title:** Modeling Coffee Agroforestry Systems and Robusta Coffee Farming Household Income in Uganda (proposal March 2025).
- **Main objective:** potential of agroforestry systems (AFS) to reduce the living income gap of Robusta coffee farmers.
- **Structure (`claude/phd-roadmap.md`):** Paper 1 living income gap and drivers; Paper 2 tree diversity/AFS type vs coffee yield and income; Paper 3 AFS scenarios with SHAMBA carbon.
- **Sites:** Mukono (lake_victoria_basin) and Nakaseke (Western_Savannah_Grassland in survey).
- **Status:** fieldwork done (Sep–Dec 2025 survey; Jul 2025 markets; 4 FGDs). **Current focus: Paper 1 draft v2.**

## Working data files (two files, never merged)
1. `data/Survey_Cleaned_v1.csv` (600 rows; 597 with a district analysed; `data/clean_survey.py`) plus `data/Survey_Income_MI_v1.csv` (20 PMM imputations; Rubin's rules).
2. `data/Market_Prices_Tidy_v1.csv` / `_v1_1.csv` (local-unit guesses still to review). Log: `data/market-cleaning-log-v1.md`.

### Key cleaning decisions
- Mukono child counts from schooling section; Nakaseke keying errors fixed; 11 HH imputed children (district median).
- Floor area: Mukono m²; Nakaseke unreliable → model/rooms.
- Income: unlisted sources = 0; coffee from seasonal sales; other sources PMM. 66 HH seasonal coffee sum kept (Ezra).
- 3 HH without a recorded district excluded (Ezra: keep 597) → 297 Mukono, 300 Nakaseke. v1 draft said 300 Mukono; data hold 297.
- Tree counts of enumerator Namyenya (Nakaseke, 100 HH; median 258) set missing. Yield > 5,000 kg FAQ/acre and Kiboko price outside 1,000–20,000 → missing.

### Recall periods
- Q162 a–h: 12 months. Q163 coffee: per season. Q168/170 tree products: last season. Management-activity costs: wage rates per period or annual spend.

## Benchmarks (v0.02, NFC_LW tool)
2 adults + 3 children, rural (UGX/month): **Mukono 1,680,564 (20.17M/yr); Nakaseke 1,648,277 (19.78M/yr).** Ezra: use these, ignore v1 draft benchmarks (USD 1,332; 5,485/4,949) and the 2+2 reference household.

## Results (n = 597; gross incl. in-kind, central)
- Median income 5.51M / 3.82M → **27.3% / 19.3% of benchmark**; 92.6% / 97.6% below; cash only 11.9% / 7.1%; in-kind range 20.5–29.2 / 13.5–21.1%.
- Net v1: 19.8% / 12.9%; all labour costed 17.6% / 9.0%.
- LI groups (HH-size benchmark) <25/25–50/50–100/≥100%: 313/194/58/32 HH. Poorest: 66% of income home-grown food.
- Drivers (OLS log ratio, Rubin, HC1, n = 581): education +36%, group +24%, coffee area, land +; HH member −8%; credit −16%; Nakaseke −32%; enumerator FE R² 0.35→0.52, main results hold.
- Coffee yield median 180 / 58 kg FAQ/acre (2% reach 1,000 kg in each district); closing gap via coffee alone needs ~11–14× yield. Trees: + Mukono, − Nakaseke.

## Models
- **SHAMBA v1.2** for Paper 3: runs in the cloud workspace (`bash models/setup_shamba.sh` in the repo; Python 3.10.16). Climate/soil downloads are blocked there, so enter them in the input template. 2 of SHAMBA's 5 own tests fail on branch cirevo/initial-improvements — check vs main before use. DynACof not used.

## Next steps
1. Ezra/Aske review draft v2 ([to confirm] points: USD rate, diet checks, Fairtrade benchmark citation, ethics numbers, FGD quotes, enumerator explanation, 297 vs 300 Mukono).
2. Objective 2: fix species spellings, recompute Simpson + Shannon on 17 plots, one AFS-type rule.
3. Triangulate benchmarks with published rural Uganda values.
4. Paper 2, then SHAMBA scenarios for Paper 3.

## Open questions
1. In-kind low/high rules; Mpigi shares in both districts.
2. Margins base. 3. Local-unit guesses. 4. Nakaseke floor area. 5. Thesis format/deadline.
6. SHAMBA scenario mapping. 7. Source of tool's original food prices. 8. Tree in-kind cap.
9. Net income: Kiboko→FAQ 0.5; partial hiring; days for 3 uncosted activities.
10. Enumerator effects (~2.4× between Nakaseke enumerators): field explanation?
