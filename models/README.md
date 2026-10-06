# Models

## SHAMBA v1.2 (Paper 3: carbon in agroforestry scenarios)
- Source: https://github.com/shamba-model/shamba, branch `cirevo/initial-improvements` (University of Edinburgh). Not copied into this repository; `bash models/setup_shamba.sh` downloads it into `models/shamba/` and installs Python 3.10.16 and its dependencies.
- Run: `models/shamba/shamba/.venv/bin/python models/shamba/shamba/shamba_command_line.py` (interactive), using the input templates in `models/shamba/data-input-templates/`.
- **Climate and soil:** SHAMBA normally downloads them from Open-Meteo and ISRIC SoilGrids. The cloud workspace cannot reach those sites, so enter the values in the input template (from field data, or looked up separately).
- **Check before use (2026-10-06):** on this branch 2 of SHAMBA's own 5 tests fail (`test_crop_model`, `test_tree_model`: emission values differ from the expected numbers). To be checked against the `main` branch before results are used.
- Field input: `data/raw/cleaned shamba Survey.csv` (18-plot tree survey). Known issues (roadmap): tree ages derived from DBH, some legume flags wrong, plot ID "Nk003" in the Mukono series.

## DynACof
Not used (built for Arabica in Costa Rica; no Robusta calibration data). https://github.com/VEZY/DynACof
