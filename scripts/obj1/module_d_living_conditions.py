"""Module D - living conditions profile: which decent-living elements households lack, by district and LI group.
Usage: python module_d_living_conditions.py <Household_Analysis_v1.csv> <Survey_Cleaned_v1.csv> <out_dir>
Indicators follow the decent-living elements of the benchmark tool (housing, water & sanitation, energy, health,
education, food, communication). Codes re-used by the form are handled as in the benchmark rebuild:
roof codes unusable (form re-used wall choices); floor 'wood' = earth/soil (decisions log).
NB 'housing below standard' is an enumerator judgement (98% Mukono vs 12% Nakaseke) - not comparable across districts.
D1 % of households lacking each element, by district and LI group (chi-square p across LI groups).
D2 food access constraints (open comments coded by keyword), by food group and district.
"""
import sys, os, re, numpy as np, pandas as pd
from scipy import stats
sys.path.insert(0, os.path.dirname(__file__)); from li_style import *
h = pd.read_csv(sys.argv[1]); sv = pd.read_csv(sys.argv[2], low_memory=False); out = sys.argv[3]
os.makedirs(f"{out}/tables", exist_ok=True); os.makedirs(f"{out}/figures", exist_ok=True)
num = lambda x: pd.to_numeric(x, errors="coerce")
d = h.merge(sv, on="_id", how="left", suffixes=("", "_sv"))
d["li_group"] = pd.Categorical(d.li_group, LI_GROUPS, ordered=True)
def flag(cond, notna): return cond.astype(float).where(notna)

walls, floor = d["House_Walls"].fillna(""), d["House_Floor"].fillna("")
def to_min(s):
    if pd.isna(s): return np.nan
    s = str(s).lower(); m = re.search(r"(\d+(?:\.\d+)?)", s)
    return float(m.group(1)) * (60 if re.search(r"h(ou)?r", s) else 1) if m else np.nan
mins = d["Time_to_source_of_Water"].map(to_min)
students = d[[c for c in d.columns if re.search(r"Number_of_children_in_(elem|high|kind)", c)]].apply(num).sum(axis=1, min_count=1)
school_age = d.children.where(d.children > 0)
IND = {  # label: (lack-of-element flag)
    "Housing judged below standard by enumerator": flag(d["Investigator_s_opinion_Does_h"].eq("No"), d["Investigator_s_opinion_Does_h"].notna()),
    "Semi-permanent / non-durable dwelling": flag(d["Select_the_type_of_dwelling"].ne("permanent_house"), d["Select_the_type_of_dwelling"].notna()),
    "Mud & wattle walls": flag(walls.str.contains("mud_and_wattle"), walls != ""),
    "Earth floor (no cement/stone)": flag(~floor.str.contains("cement|stone"), floor != ""),
    "Open pit latrine without slab": flag(d["Select_which_type_of_toile"].eq("open_pit_latrine_without_slab"), d["Select_which_type_of_toile"].notna()),
    "Unprotected drinking water (open well, river, other)": flag(d["Sources_of_Drinking_water"].isin(["open_well", "river", "other"]), d["Sources_of_Drinking_water"].notna()),
    "Water fetch > 30 minutes": flag(mins > 30, mins.notna()),
    "Cooks with firewood": flag(d["energy_source"].eq("firewood"), d["energy_source"].notna()),
    "No grid electricity": flag(d["Do_you_have_access_to_electricity"].eq("No"), d["Do_you_have_access_to_electricity"].notna()),
    "No health insurance": flag(d["SECTION_A/_45_Do_you_have_health_insuran"].eq("No"), d["SECTION_A/_45_Do_you_have_health_insuran"].notna()),
    "No internet in household": flag(d["_2_Do_you_have_access_to_the_i"].astype(str).str.startswith("No"), d["_2_Do_you_have_access_to_the_i"].notna()),
    "No member with mobile phone": flag(num(d["_85_How_many_members_ss_to_a_mobile_phone"]).eq(0), num(d["_85_How_many_members_ss_to_a_mobile_phone"]).notna()),
    "Fewer children reported in school than children (incl. under-5s)": flag(students.fillna(0) < school_age, school_age.notna()),
}
D = pd.DataFrame(IND)
rows = []
for lab in D:
    s = D[lab]; r = {"element lacking": lab, "n": int(s.notna().sum())}
    for k in ["mukono", "nakaseke"]: r[DIST_LABEL[k]] = round(s[d.district == k].mean() * 100, 1)
    r["All"] = round(s.mean() * 100, 1)
    for g in LI_GROUPS: r[f"income {g}"] = round(s[d.li_group == g].mean() * 100, 1)
    tab = pd.crosstab(d.li_group, s)
    r["p (LI groups)"] = round(stats.chi2_contingency(tab)[1], 3) if tab.shape == (4, 2) else np.nan
    tab2 = pd.crosstab(d.district, s); r["p (district)"] = round(stats.chi2_contingency(tab2)[1], 3) if tab2.shape == (2, 2) else np.nan
    rows.append(r)
D1 = pd.DataFrame(rows); D1.to_csv(f"{out}/tables/D1_living_conditions.csv", index=False)
d["n_lacking"] = D.drop(columns=["Fewer children reported in school than children (incl. under-5s)"]).sum(axis=1, min_count=8)
D1b = d.groupby("li_group", observed=True).n_lacking.describe()[["count", "mean", "50%"]].round(2)
D1b.to_csv(f"{out}/tables/D1b_elements_lacking_by_li_group.csv")
print(D1.to_string()); print(D1b)

# Figure D1: dot plot, % lacking each element, lowest vs highest income groups
sel = D1[~D1["element lacking"].str.startswith("Housing judged")].sort_values("All")   # enumerator judgement, not comparable
fig, ax = plt.subplots(figsize=(6.8, 4.4)); yy = np.arange(len(sel))
lo, hi = sel["income <25%"], sel["income 50-100%"].where(sel["income 50-100%"].notna())
hi2 = sel["income >=100%"]
ax.hlines(yy, np.minimum(lo, hi2), np.maximum(lo, hi2), color=GRID, lw=3)
ax.scatter(lo, yy, s=42, color=ORD4[3], edgecolor=SURF, linewidth=1.5, zorder=3, label="income <25% of benchmark")
ax.scatter(hi2, yy, s=42, color=ORD4[0], edgecolor=SURF, linewidth=1.5, zorder=3, label="income at/above benchmark")
ax.set_yticks(yy, sel["element lacking"]); ax.set_xlim(0, 100); ax.grid(axis="y", visible=False)
ax.set_xlabel("% of households lacking the element"); ax.legend(loc="lower right")
ax.set_title("Basics are missing for most; the poorest also lack water, sanitation, schooling")
save(fig, f"{out}/figures/D1_living_conditions.png", "Income incl. in-kind as % of household-size benchmark; both districts pooled. Enumerator housing judgement omitted (not comparable across districts).")

# ---------------- D2 food constraints (open comments per food group)
fg = {c: c.split("group_wg2nh50_")[1].split("/")[0] for c in sv.columns if "group_wg2nh50_" in c and c.endswith("food_source_comments")}
CODES = [("Pests & diseases", r"pest|disease|worm|insect|mosaic|rot|blight|army|rat|bird|zibugo|kiwotokwa"),
         ("Price / cannot afford", r"expens|money|afford|price|cost"), ("Distance / market access", r"far|distance|town|market|transport|hawker|reach|shop"),
         ("Weather / drought", r"weather|sun|drought|rain|heat|dry"), ("Quality / safety", r"dilut|water|spoil|quality|fresh|cold|small"),
         ("Availability / seasonal", r"scarc|season|availab|hard to get|rare|once in a while|take long"),
         ("No constraint", r"^no |none|no problem|not .*problem|^nothing")]
long = []
for c, g in fg.items():
    s = sv[["_id", c]].dropna(); s = s[s[c].astype(str).str.strip().str.len() > 2]
    for _, r in s.iterrows():
        t = str(r[c]).lower(); hit = [k for k, rx in CODES if re.search(rx, t)] or ["Other"]
        for k in hit: long.append({"_id": r["_id"], "food_group": g, "constraint": k})
L = pd.DataFrame(long).merge(h[["_id", "district"]], on="_id")
# Mukono enumerators rarely recorded comments (Mukono: few comments) -> report shares for Nakaseke; Mukono shown for completeness
D2 = (L.drop_duplicates(["_id", "constraint"]).groupby(["district", "constraint"])._id.nunique() /
      h.groupby("district").size() * 100).round(1).unstack(0)
D2.to_csv(f"{out}/tables/D2_food_constraints_households.csv")
L.groupby(["food_group", "constraint"])._id.nunique().unstack(fill_value=0).to_csv(f"{out}/tables/D2b_food_constraints_by_group.csv")
print(D2)
