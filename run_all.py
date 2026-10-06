"""Rebuild everything for Objective 1 / Paper 1 from the raw survey files in data/raw.

Run from the repository folder:   python run_all.py
Outputs (overwritten each run, deterministic - fixed random seed):
  data/derived/   cleaned survey, 20 income imputations, net-income files, household analysis file
  paper1/figures  PNG figures (300 dpi)      paper1/tables  CSV tables
"""
import subprocess, sys
from pathlib import Path

R = Path(__file__).resolve().parent
RAW, DER, P1 = R / "data" / "raw", R / "data" / "derived", R / "paper1"
STD = RAW / "Standardized_Data.csv"
KOBO = RAW / "Clean Responses Social Economi Survey.csv"
for f in (STD, KOBO):
    if not f.exists():
        sys.exit(f"Missing input file: {f}")
for d in (DER, P1 / "figures", P1 / "tables"):
    d.mkdir(parents=True, exist_ok=True)


def run(script, *args):
    print(f"\n=== {script} ===", flush=True)
    subprocess.run([sys.executable, "-W", "ignore", str(R / "scripts" / script), *map(str, args)],
                   check=True, cwd=(R / "scripts" / script).parent)


cleaned, mi = DER / "Survey_Cleaned_v1.csv", DER / "Survey_Income_MI_v1.csv"
hh = DER / "Household_Analysis_v1.csv"
run("cleaning/clean_survey.py", STD, KOBO, DER)                       # cleaning + 20 income imputations
run("income/build_net_income.py", cleaned, mi, DER)                   # benchmark, in-kind income, gross & net gap
run("obj1/build_household_analysis.py", cleaned, mi, DER / "Household_Net_Gap_v1.csv", DER)
run("obj1/module_a_sample.py", hh, P1)                                # Table 3, Figures 1-2
run("obj1/module_b_income_drivers.py", hh, mi, P1)                    # Figures 3-4, regression tables
run("obj1/module_c_coffee_trees.py", hh, cleaned, P1)                 # Figure 5, coffee & tree tables
run("obj1/module_d_living_conditions.py", hh, cleaned, P1)            # Table 4
for g in ("demographics", "housing", "income", "gender_education", "farm_trees", "food_prices_gap"):
    run(f"morefigures/{g}.py")                                          # earlier analyses re-run -> paper1/figures/moreFigures
print(f"\nDone. Figures: {P1 / 'figures'}   Tables: {P1 / 'tables'}")
