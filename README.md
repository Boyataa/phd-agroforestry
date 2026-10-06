# PhD: Coffee agroforestry and the living income of Robusta farmers (Uganda)

Ezra Mwesigwa — Makerere University / University of Copenhagen (IFRO).
Working repository for all data, analysis scripts, results and models. Private: the raw data contain names, phone numbers and GPS locations of respondents.

## Structure
| Folder | What is in it |
|---|---|
| `data/raw/` | Original files: household survey (`Standardized_Data.csv` + KoBo export), market price survey, SHAMBA plot survey, NFC_LW benchmark workbooks v0.01 |
| `data/derived/` | Files made by the scripts: cleaned survey, 20 income imputations, market prices (tidy), household gap, net income, household analysis file |
| `scripts/cleaning/` | Survey cleaning and imputation; market price tidying and local-unit conversions |
| `scripts/benchmark/` | Benchmark rebuild v0.02 (participants, workbook inputs, LibreOffice test copy) |
| `scripts/income/` | Income incl. home-grown food, living income gap, net income |
| `scripts/obj1/` | Objective 1 analysis modules A–D and plotting style |
| `paper1/` | Paper 1 figures, tables and `Obj1_tables_v1.md` |
| `models/` | SHAMBA set-up script and notes (SHAMBA code itself is downloaded, not stored) |
| `docs/` | Project brief, roadmap, decisions logs, cleaning/benchmark/gap/net-income/analysis logs, methods summary |

## Reproduce Paper 1
```
pip install -r requirements.txt
python run_all.py
```
Rebuilds `data/derived/` and `paper1/` from `data/raw/` in a few minutes; results are identical on every run (fixed random seed). Sample: 597 households (297 Mukono, 300 Nakaseke; 3 interviews without a district excluded).

Not part of `run_all.py` (run separately, already done): benchmark workbooks v0.02 (`scripts/benchmark/`, needs LibreOffice for the check copy), market tidying (`scripts/cleaning/build_market_tidy.py`, `local_unit_guesses.py`) and the gross gap file (`scripts/income/build_income_gap.py`).

## SHAMBA
`bash models/setup_shamba.sh` — see `models/README.md`.

## Working on your PC
Clone with GitHub Desktop into a folder **outside OneDrive** (e.g. `C:\Users\Envy\Documents\GitHub`). Pull to get Claude's latest changes; push your own.

## Key decisions
See `docs/project-brief.md` (current numbers and open questions) and `docs/decisions/`.
