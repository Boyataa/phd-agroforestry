"""moreFigures - group 'demographics': re-runs of the old data-readiness, respondent-demographics and
household-member (roster) figures on the cleaned 597-household survey.
Old sources: 'Generic Dataset Analysis.ipynb' (data_readiness_assessment, demographics, demographics_household_members)
and 'Gender.ipynb'/'House.ipynb' (education x gender / marital views).
Run from repo root:  python scripts/morefigures/demographics.py
Outputs: paper1/figures/moreFigures/{data_readiness_assessment,demographics,demographics_household_members}/ (PNG + CSV)
"""
import sys, warnings
from pathlib import Path
import numpy as np, pandas as pd
from scipy import stats
from matplotlib.colors import LinearSegmentedColormap, to_rgb

warnings.filterwarnings("ignore", category=pd.errors.PerformanceWarning)
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "obj1"))
from li_style import *  # noqa: E402,F401

OUT = ROOT / "paper1" / "figures" / "moreFigures"
F_READY, F_DEMO, F_ROSTER = (OUT / n for n in ["data_readiness_assessment", "demographics", "demographics_household_members"])
for f in (F_READY, F_DEMO, F_ROSTER):
    f.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------- data (597 HH analysis sample)
h = pd.read_csv(ROOT / "data/derived/Household_Analysis_v1.csv")
s = pd.read_csv(ROOT / "data/derived/Survey_Cleaned_v1.csv", low_memory=False)
s["district"] = s["District"].str.lower()
s = s[s.district.isin(["mukono", "nakaseke"])]
s = s[s["_id"].isin(h["_id"])].copy()
assert len(s) == 597 and len(h) == 597
DISTS = ["mukono", "nakaseke"]
N = s.district.value_counts().reindex(DISTS)
NTXT = f"n = {N.sum()} households (Mukono {N['mukono']}, Nakaseke {N['nakaseke']})"


def ramp(k, lo="#d3e4f8", hi=ORD4[3]):
    """k ordinal steps between the li_style ramp ends."""
    cm = LinearSegmentedColormap.from_list("o", [lo, ORD4[0], ORD4[1], ORD4[2], hi])
    return [cm(x) for x in np.linspace(0, 1, k)]


def txtcol(c):
    r, g, b = to_rgb(c)[:3]
    return "white" if 0.299 * r + 0.587 * g + 0.114 * b < 0.55 else INK


def pfmt(p):
    return "p < 0.001" if p < 0.001 else f"p = {p:.3f}"


def chi2_p(tab):
    tab = np.asarray(tab)
    tab = tab[tab.sum(axis=1) > 0][:, tab.sum(0) > 0]
    return stats.chi2_contingency(tab)[1]


def stacked_rows(ax, table, colors, row_labels, min_label=6.0):
    """table: rows = bars (top to bottom), columns = categories; values in %."""
    y = np.arange(len(table))[::-1]
    left = np.zeros(len(table))
    for j, cat in enumerate(table.columns):
        v = table[cat].values
        ax.barh(y, v, left=left, color=colors[j], height=0.62, label=cat, edgecolor=SURF, linewidth=0.6)
        for yi, li, vi in zip(y, left, v):
            if vi >= min_label:
                ax.text(li + vi / 2, yi, f"{vi:.0f}", ha="center", va="center", fontsize=7.5, color=txtcol(colors[j]))
        left += v
    ax.set_yticks(y, row_labels)
    ax.set_xlim(0, 100)
    ax.grid(axis="y", visible=False)
    ax.set_xlabel("% of households with a valid answer")


# =====================================================================================================
# 1. DATA READINESS ASSESSMENT
# =====================================================================================================
# R1 sample by district and sub-county
s["sub_county"] = s["Sub_County"].fillna("Not recorded")
r1 = (s.groupby(["district", "sub_county"]).agg(n_households=("_id", "size"), n_parishes=("Parish", "nunique")).reset_index())
r1["district"] = r1.district.map(DIST_LABEL)
r1["pct_of_district"] = (r1.n_households / r1.groupby("district").n_households.transform("sum") * 100).round(1)
r1.to_csv(F_READY / "sample_by_subcounty.csv", index=False)

fig, ax = plt.subplots(figsize=(6.4, 3.0))
order = r1.sort_values(["district", "n_households"], ascending=[True, False]).reset_index(drop=True)
y = np.arange(len(order))[::-1]
for yi, (_, r) in zip(y, order.iterrows()):
    c = DIST[r.district.lower()]
    ax.barh(yi, r.n_households, color=c, height=0.6)
    ax.text(r.n_households + 2, yi, f"{r.n_households}", va="center", fontsize=8, color=INK)
ax.set_yticks(y, [f"{r.sub_county} ({r.district})" for _, r in order.iterrows()])
ax.set_xlabel("Households interviewed (number)")
ax.grid(axis="y", visible=False)
ax.set_xlim(0, order.n_households.max() * 1.15)
ax.set_title("Survey sample by district and sub-county")
save(fig, F_READY / "sample_by_subcounty.png",
     f"{NTXT}. Mukono: Nakifuma county; Nakaseke: Nakaseke Central and South. 3 interviews without a district are excluded. "
     f"'Not recorded' = sub-county missing in the survey file.")

# R2 section completeness: share of each section's core (always-asked) questions answered per household
P = "group_wz3xj67/group_pw7lb76/0/group_wz3xj67/group_pw7lb76/"
# village is stored in Village_Cell or in one of the parish-specific SECTION_A/f_Village_Cell_* columns (KoBo cascade)
s["village_any"] = s[[c for c in s.columns if c == "Village_Cell" or c.startswith("SECTION_A/f_Village_Cell")]].bfill(axis=1).iloc[:, 0]
SECTIONS = {
    "Location & GPS": ["District", "Sub_County", "Parish", "village_any", "GPS_Coordinates"],
    "Respondent profile": ["Age_of_Respondent_years", "Gender_Sex", "Marital_Status", "Education_Level_of_respondent",
                           "Residential_status", "Farming_experience_in_years"],
    "Household roster (1st member) & no. of children": [
        "Details_of_household_members_gender_1", "Details_of_household_members_age_1",
        "Details_of_household_members_househead_relationship_1", "Details_of_household_members_residential_status_1",
        "Ask_ the_ respondent_ to_ provide_ the_ number_ of_ Children_ in_ the_ Household."],
    "Housing": ["Select_the_type_of_dwelling", "Total_number_of_rooms", "Number_of_Bedrooms", "Total_Surface_area_Square_Feet",
                "House_Walls", "House_!Roof", "House_Floor", "Select_which_type_of_toile", "When_was_the_house_built"],
    "Water, energy & electricity": ["Sources_of_Drinking_water", "Time_to_source_of_Water", "energy_source",
                                    "Do_you_have_access_to_electricity"],
    "Food sources (13 food groups)": [c for c in s.columns if c.lower().startswith("source") and "comment" not in c.lower() and "water" not in c.lower()],
    "Health & schooling": ["In_the_past_3_months,_did_you_or_any_household_member_obtain_health_care?",
                           "SECTION_A/_45_Do_you_have_health_insuran", "SECTION_A/_49_Number_of_children_in_kind",
                           "SECTION_A/_51_Number_of_children_in_elem", "SECTION_A/_53_Number_of_children_in_high",
                           "SECTION_A/_55_Number_of_children_in_univ"],
    "Phone & internet": ["_85_How_many_members_ss_to_a_mobile_phone", "_2_Do_you_have_access_to_the_i"],
    "Land, credit & services": ["Does_the_respondent_own_the_land?", "What_is_the_total_land_he_she_owns",
                                "Size_used_for_Robusta_coffee", "Do_you_have_access_to_credit_services", "Are_you_currently_partici",
                                "group_vf5ln20/_161_Are_you_in_touc_al_extension_officer", "group_vf5ln20/_84_Ask_the_respondent_for_the",
                                "_120_Have_you_removed_trees_in"],
    "Coffee labour (planting, weeding, harvest)": [
        f"group_np5zx78_{a}/group_np5zx78_{a}_{b}" for a in ["planting_1", "weeding_1", "harvesting_1"]
        for b in ["standard_work_period", "estimated_cost_of_management_activity"]],
    "Coffee harvest & sales (latest record)": [P + "Year_of_Harvest", P + "Category_of_Coffee_Sold", P + "Coffee_harvested_in_Kilograms",
                                               P + "Farm_gate_price_UGX_per_Kg", "group_wz3xj67/_168_How_did_you_sell_your_cof"],
    "Income sources list & Q162a coffee income (raw)": ["group_wz3xj67/What_have_been_your_household_",
                                                        "group_wz3xj67/_162_a_Income_from_le_of_Robusta_coffee"],
    "Trust & risk attitudes": [c for c in s.columns if "group_ri4un44/" in c],
    "Savings": ["group_to3ec88/Do_you_save_money_for_unexpect"],
}
for k, v in SECTIONS.items():
    miss = [c for c in v if c not in s.columns]
    assert not miss, (k, miss)
rows = []
for sec, cols in SECTIONS.items():
    filled = s[cols].notna().mean(axis=1) * 100           # % of core items answered, per household
    complete = s[cols].notna().all(axis=1) * 100
    r = {"section": sec, "n_core_items": len(cols), "core_items": " | ".join(cols)}
    for d in DISTS:
        m = s.district == d
        r[f"{DIST_LABEL[d]}_mean_pct_items_answered"] = round(filled[m].mean(), 1)
        r[f"{DIST_LABEL[d]}_pct_hh_all_items"] = round(complete[m].mean(), 1)
    r["All_mean_pct_items_answered"] = round(filled.mean(), 1)
    r["All_pct_hh_all_items"] = round(complete.mean(), 1)
    rows.append(r)
r2 = pd.DataFrame(rows)
r2.to_csv(F_READY / "section_completeness.csv", index=False)

fig, ax = plt.subplots(figsize=(6.8, 5.0))
r2p = r2.iloc[::-1].reset_index(drop=True)
yy = np.arange(len(r2p))
for d, off, mk in [("mukono", 0.12, "o"), ("nakaseke", -0.12, "s")]:
    v = r2p[f"{DIST_LABEL[d]}_mean_pct_items_answered"]
    ax.scatter(v, yy + off, color=DIST[d], s=34, marker=mk, label=DIST_LABEL[d], zorder=3)
for i, r in r2p.iterrows():
    a, b = r["Mukono_mean_pct_items_answered"], r["Nakaseke_mean_pct_items_answered"]
    ax.plot([a, b], [i + 0.12, i - 0.12], color=GRID, lw=1.2, zorder=2)
ax.set_yticks(yy, [f"{r.section} ({r.n_core_items})" for r in r2p.itertuples()])
ax.set_xlim(50, 101.5)
ax.set_xlabel("Core questions answered, mean % per household")
ax.grid(axis="y", visible=False)
ax.legend(loc="lower left", bbox_to_anchor=(0, 1.0), ncol=2)
ax.set_title("Completeness of the cleaned household survey, by section and district", pad=20)
save(fig, F_READY / "section_completeness.png",
     f"{NTXT}. Core = questions asked of every household (number in brackets); follow-up, 'please specify', repeat "
     "rows beyond the first and skip-logic questions are excluded because blanks there are expected. Raw survey answers; "
     "after cleaning, total income is available for all 597 households (missing components imputed, 20 PMM imputations).")

# R3 GPS scatter (coordinates only)
g = s["GPS_Coordinates"].str.split(expand=True)
s["lat"] = pd.to_numeric(g[0], errors="coerce").fillna(pd.to_numeric(s.get("_geolocation/0"), errors="coerce"))
s["lon"] = pd.to_numeric(g[1], errors="coerce").fillna(pd.to_numeric(s.get("_geolocation/1"), errors="coerce"))
s["gps_acc_m"] = pd.to_numeric(g[3], errors="coerce")
okg = s.lat.between(-2, 5) & s.lon.between(29, 36)
gp = s[okg]
r3 = (gp.groupby(["district", "sub_county"]).agg(n_points=("_id", "size"), lat_centroid=("lat", "mean"), lon_centroid=("lon", "mean"),
                                                  lat_min=("lat", "min"), lat_max=("lat", "max"), lon_min=("lon", "min"),
                                                  lon_max=("lon", "max"), median_accuracy_m=("gps_acc_m", "median"),
                                                  n_accuracy_over_50m=("gps_acc_m", lambda x: int((x > 50).sum())))
      .round(3).reset_index())
r3["district"] = r3.district.map(DIST_LABEL)
r3.to_csv(F_READY / "gps_summary_by_subcounty.csv", index=False)
# point file is rounded to 0.01 deg (~1 km) and carries no IDs or names, so households cannot be located from it
gp[["district", "sub_county"]].assign(lat_2dp=gp.lat.round(2), lon_2dp=gp.lon.round(2)).sort_values(
    ["district", "sub_county", "lat_2dp", "lon_2dp"]).to_csv(F_READY / "gps_points_rounded_2dp.csv", index=False)

fig, ax = plt.subplots(figsize=(5.6, 5.6))
MK = {"Kimenyedde": "o", "Nabaale": "^", "Kasangombe": "o", "Kikamulo": "^", "Not recorded": "x"}
for (d, sc), sub in gp.groupby(["district", "sub_county"]):
    ax.scatter(sub.lon, sub.lat, s=10 if sc != "Not recorded" else 30, color=DIST[d] if sc != "Not recorded" else INK,
               marker=MK.get(sc, "o"), alpha=0.6 if sc != "Not recorded" else 1, linewidths=0 if sc != "Not recorded" else 1.2,
               label=f"{sc} ({DIST_LABEL[d]}, n={len(sub)})")
ax.set_aspect("equal")  # near the equator 1 deg lon ~ 1 deg lat
ax.set_xlim(gp.lon.min() - 0.03, gp.lon.max() + 0.05)
ax.set_xlabel("Longitude (deg E)")
ax.set_ylabel("Latitude (deg N)")
ax.legend(loc="upper right", fontsize=7.5, markerscale=1.6)
ax.set_title("Location of surveyed households (GPS)")
nacc = int((gp.gps_acc_m > 50).sum())
save(fig, F_READY / "gps_households.png",
     f"n = {len(gp)} of {len(s)} households with a GPS fix ({len(s) - len(gp)} missing). Median recorded accuracy "
     f"{gp.gps_acc_m.median():.1f} m; {nacc} fixes with accuracy > 50 m. No basemap; equal-degree axes.")

# =====================================================================================================
# 2. DEMOGRAPHICS (respondent)
# =====================================================================================================
LAB = {
    "Gender_Sex": ("Sex of respondent", {"female": "Female", "male": "Male"}),
    "Age_of_Respondent_years": ("Age of respondent (years)", {"20-29": "20-29", "30-39": "30-39", "40-49": "40-49",
                                                              "50-59": "50-59", "60-69": "60-69", ">=_70": "70+"}),
    "Marital_Status": ("Marital status", {"married": "Married", "single": "Single", "divorced": "Divorced", "other": "Other"}),
    "Education_Level_of_respondent": ("Education of respondent", {"non_formal": "None", "primary": "Primary", "seconary": "Secondary",
                                                                  "vocational": "Vocational", "college_university": "College/univ."}),
}
ORDINAL = {"Age_of_Respondent_years", "Education_Level_of_respondent"}
EDU_ORDER = list(LAB["Education_Level_of_respondent"][1].values())
EDU_COLORS = ramp(len(EDU_ORDER))
for c, (_, m) in LAB.items():
    s[c + "_lab"] = pd.Categorical(s[c].map(m), list(m.values()), ordered=True)

long_rows = []
fig, axes = plt.subplots(2, 2, figsize=(9.6, 4.6))
for ax, (c, (title, m)) in zip(axes.ravel(), LAB.items()):
    tab = pd.crosstab(s.district, s[c + "_lab"]).reindex(DISTS)
    pct = tab.div(tab.sum(axis=1), axis=0) * 100
    for d in DISTS:
        for cat in tab.columns:
            long_rows.append({"variable": title, "category": cat, "district": DIST_LABEL[d], "n": int(tab.loc[d, cat]),
                              "pct": round(pct.loc[d, cat], 1), "n_valid_district": int(tab.loc[d].sum())})
    for cat in tab.columns:
        long_rows.append({"variable": title, "category": cat, "district": "All", "n": int(tab[cat].sum()),
                          "pct": round(tab[cat].sum() / tab.values.sum() * 100, 1), "n_valid_district": int(tab.values.sum())})
    cols = ramp(len(tab.columns)) if c in ORDINAL else SRC[:len(tab.columns)]
    stacked_rows(ax, pct, cols, [f"{DIST_LABEL[d]} (n={tab.loc[d].sum()})" for d in DISTS])
    p = chi2_p(tab)
    ax.set_title(f"{title}  [chi-square {pfmt(p)}]", fontsize=9.5)
    ax.legend(ncol=len(tab.columns), loc="lower left", bbox_to_anchor=(0, 1.13), fontsize=7.5, handlelength=1, columnspacing=0.8)
    ax.set_xlabel("% of respondents" if ax in axes[1] else "")
fig.suptitle("Respondent profile by district", x=0.0, ha="left", fontweight="bold", fontsize=11, color=INK, y=0.99)
fig.tight_layout(h_pad=3.2)
pd.DataFrame(long_rows).to_csv(F_DEMO / "respondent_profile_by_district.csv", index=False)
save(fig, F_DEMO / "respondent_profile_by_district.png",
     f"{NTXT}; percentages over respondents with a valid answer (1-3 missing per item). Numbers in bars are %. "
     "Marital status has no 'widowed' option: 'Other' (26% Mukono) and 'Single' (26% Nakaseke) probably both hold widowed respondents, "
     "recorded differently by district - compare the 'Married' share only.")


def edu_by(group_col, group_lab, fname, title, note_extra):
    rows, tabs = [], []
    bars, labels = [], []
    for d in DISTS:
        sd = s[s.district == d]
        t = pd.crosstab(sd[group_col], sd["Education_Level_of_respondent_lab"]).reindex(columns=EDU_ORDER, fill_value=0)
        t = t[t.sum(axis=1) > 0]
        # chi-square on education collapsed to none / primary / secondary+ (sparse cells otherwise)
        t3 = pd.DataFrame({"None": t["None"], "Primary": t["Primary"], "Secondary+": t[EDU_ORDER[2:]].sum(axis=1)})
        p = chi2_p(t3)
        for gcat in t.index:
            pct = t.loc[gcat] / t.loc[gcat].sum() * 100
            bars.append(pct.values)
            labels.append(f"{DIST_LABEL[d]} - {gcat} (n={t.loc[gcat].sum()})")
            for e in EDU_ORDER:
                rows.append({"district": DIST_LABEL[d], group_lab: gcat, "education": e, "n": int(t.loc[gcat, e]),
                             "pct": round(pct[e], 1), "n_group": int(t.loc[gcat].sum()), "chi2_p_district (3 edu levels)": round(p, 4)})
        tabs.append((d, p, len(t)))
    table = pd.DataFrame(bars, columns=EDU_ORDER)
    fig, ax = plt.subplots(figsize=(7.4, 0.42 * len(table) + 1.4))
    stacked_rows(ax, table, EDU_COLORS, labels)
    k = tabs[0][2]
    ax.axhline(len(table) - k - 0.5, color=INK2, lw=0.8)
    ax.legend(ncol=5, loc="lower left", bbox_to_anchor=(0, 1.0), fontsize=7.5, handlelength=1)
    ax.set_xlabel("% of respondents in the group")
    ax.set_title(title, pad=22)
    ptxt = "; ".join(f"{DIST_LABEL[d]} chi-square {pfmt(p)}" for d, p, _ in tabs)
    pd.DataFrame(rows).to_csv(F_DEMO / f"{fname}.csv", index=False)
    save(fig, F_DEMO / f"{fname}.png",
         f"{NTXT}; respondents with valid answers. Numbers in bars are %. Test of independence within district, education collapsed "
         f"to none / primary / secondary or higher: {ptxt}. {note_extra}")


s["sex_lab"] = s["Gender_Sex_lab"]
edu_by("sex_lab", "sex", "education_by_sex",
       "Education of respondent by sex and district", "")
s["mar_lab"] = s["Marital_Status_lab"]
edu_by("mar_lab", "marital_status", "education_by_marital_status",
       "Education of respondent by marital status and district",
       "Small groups (Mukono single, Nakaseke other) are shown but are not interpretable. No 'widowed' option in the survey.")

# =====================================================================================================
# 3. HOUSEHOLD MEMBERS (roster, max 6 members per household)
# =====================================================================================================
slots = [("Details_of_household_members_gender_1", "Details_of_household_members_age_1",
          "Details_of_household_members_residential_status_1", "Details_of_household_members_househead_relationship_1"),
         ("Details_of_household_members_gender_2", "Details_of_household_members_age_2",
          "Details_of_household_members_househead__residential_status_2", "Details_of_household_members_househead_relationship_2")]
for r in ["row_3_1_1", "row1_4_1_1", "row_5_1_1", "row_6_1_1"]:
    p = f"SECTION_A/group_detailsofhhmembers_row_5/group_fd9pm11_{r}/group_fd9pm11_{r}_"
    slots.append((p + "gender", p + "age", p + "residential_status", p + "househead_relationship"))
L = pd.concat([pd.DataFrame({"_id": s["_id"].values, "district": s.district.values, "slot": k + 1, "gender": s[gc].values,
                             "age": s[ac].values, "res": s[rc].values, "rel": s[lc].values})
               for k, (gc, ac, rc, lc) in enumerate(slots)], ignore_index=True)
L = L[L[["gender", "age", "res", "rel"]].notna().any(axis=1)].copy()
AGE = {"0_5": "0-5", "6_15": "6-15", "16_25": "16-25", "26_40": "26-40", "41_60": "41-60", "61_and_above": "61+"}
AGE_ORDER = list(AGE.values())
REL = {"house_head": "Head (incl. spouse)", "biological_child": "Child of head", "other_relative": "Other relative",
       "sibling": "Sibling of head", "other": "Other (non-relative)"}
L["age_g"] = pd.Categorical(L.age.map(AGE), AGE_ORDER, ordered=True)
L["rel_g"] = pd.Categorical(L.rel.map(REL), list(REL.values()), ordered=True)
L["status"] = np.where(L.res.isna(), "status_missing", np.where(L.res.astype(str).str.startswith("resident"), "resident", "non_resident"))
n_roster_hh = L.groupby("district")["_id"].nunique().reindex(DISTS)
n_mem = L.groupby("district").size().reindex(DISTS)
n_full6 = L.groupby("_id").size().eq(6).groupby(L.groupby("_id").district.first()).sum().reindex(DISTS)
heads = L[L.rel == "house_head"].groupby("_id").size()
two_heads = int((heads >= 2).sum())

# M1 age structure of listed members, resident vs non-resident
ag = L[L.age_g.notna()]
t_res = pd.crosstab([ag.district, ag.age_g], ag.status)
t_res = t_res.reindex(pd.MultiIndex.from_product([DISTS, AGE_ORDER]), fill_value=0)
for col in ["resident", "non_resident", "status_missing"]:
    if col not in t_res: t_res[col] = 0
t_res["total"] = t_res.sum(axis=1)
t_res["pct_of_district_members"] = (t_res.total / t_res.groupby(level=0).total.transform("sum") * 100).round(1)
t_res.index.names = ["district", "age_group"]
t_res.reset_index().assign(district=lambda x: x.district.map(DIST_LABEL)).to_csv(F_ROSTER / "roster_age_structure_by_district.csv", index=False)

fig, ax = plt.subplots(figsize=(7.0, 3.6))
x = np.arange(len(AGE_ORDER))
w = 0.38
for i, d in enumerate(DISTS):
    tt = t_res.loc[d]
    xs = x + (i - 0.5) * w
    ax.bar(xs, tt.resident, width=w, color=DIST[d], label=f"{DIST_LABEL[d]} - resident")
    ax.bar(xs, tt.non_resident + tt.status_missing, width=w, bottom=tt.resident, color=DIST[d], alpha=0.35,
           label=f"{DIST_LABEL[d]} - non-resident / status missing")
    for xi, tot in zip(xs, tt.total):
        ax.text(xi, tot + 4, f"{tot}", ha="center", fontsize=7.5, color=INK2)
ax.set_xticks(x, AGE_ORDER)
ax.set_xlabel("Age group of household member (years)")
ax.set_ylabel("Members listed in roster (number)")
ax.grid(axis="x", visible=False)
ax.legend(fontsize=7.5, ncol=2, loc="lower left", bbox_to_anchor=(0, 1.0))
ax.set_ylim(0, t_res.total.max() * 1.08)
ax.set_title("Household members listed in the roster, by age group and district", pad=34)
save(fig, F_ROSTER / "roster_age_structure_by_district.png",
     f"Roster members with an age group: Mukono {int(t_res.loc['mukono'].total.sum())}, Nakaseke {int(t_res.loc['nakaseke'].total.sum())} "
     f"(from {n_roster_hh['mukono']} / {n_roster_hh['nakaseke']} households with a roster). The roster has at most 6 rows "
     f"({n_full6['mukono']} / {n_full6['nakaseke']} households filled all 6). Mukono enumerators listed no children under 16 - "
     "children are counted separately (see household_composition_by_district). Age groups are the survey codes restored in cleaning.")

# M2 household composition: adults, children, size (Household_Analysis definitions)
n05 = int(((L.age == "0_5") & (L.status == "resident")).sum())
comp = h[["_id", "district", "adults", "children", "hh_size", "children_imputed"]].copy()
rows = []
fig, axes = plt.subplots(1, 3, figsize=(10.4, 3.3), sharey=True)
for ax, (c, lab, cap) in zip(axes, [("adults", "Resident adults (roster, 16+)", 8), ("children", "Children (survey count)", 10),
                                    ("hh_size", "Household size (adults + children)", 12)]):
    cats = list(range(0 if c == "children" else 1, cap)) + [f"{cap}+"]
    pv = {}
    for d in DISTS:
        v = comp.loc[comp.district == d, c].dropna().astype(int)
        b = v.clip(upper=cap).map(lambda z: f"{cap}+" if z >= cap else z)
        cnt = b.value_counts().reindex(cats, fill_value=0)
        pv[d] = cnt / cnt.sum() * 100
        for k_, n_ in cnt.items():
            rows.append({"variable": c, "value": k_, "district": DIST_LABEL[d], "n_households": int(n_), "pct": round(pv[d][k_], 1)})
    xx = np.arange(len(cats))
    for i, d in enumerate(DISTS):
        ax.bar(xx + (i - 0.5) * 0.4, pv[d].values, width=0.4, color=DIST[d], label=DIST_LABEL[d])
    mw = stats.mannwhitneyu(comp.loc[comp.district == "mukono", c].dropna(), comp.loc[comp.district == "nakaseke", c].dropna()).pvalue
    med = comp.groupby("district")[c].median()
    ax.set_xticks(xx, [str(k_) for k_ in cats], fontsize=7.5)
    ax.set_xlabel(f"{lab} (number)")
    ax.grid(axis="x", visible=False)
    ax.set_title(f"{lab.split(' (')[0]}\nmedian {med['mukono']:.0f} / {med['nakaseke']:.0f}; Mann-Whitney {pfmt(mw)}", fontsize=9)
axes[0].set_ylabel("% of households")
axes[0].legend(loc="upper right")
fig.suptitle("Household composition by district", x=0.0, ha="left", fontweight="bold", fontsize=11, color=INK, y=1.06)
pd.DataFrame(rows).to_csv(F_ROSTER / "household_composition_by_district.csv", index=False)
n_imp = comp.groupby("district").children_imputed.sum().reindex(DISTS)
save(fig, F_ROSTER / "household_composition_by_district.png",
     f"{NTXT}. Adults = resident roster members not coded 6-15 (respondent counted if no roster); children = cleaned children count "
     f"(Mukono derived from the schooling section; Nakaseke as reported, 3 keying errors corrected); {n_imp['mukono']} / {n_imp['nakaseke']} "
     "households with no count given the district median. Same definitions as the living-income benchmark (Household_Analysis_v1). "
     f"Caveat: that file counts the {n05} resident roster members coded 0-5 (Nakaseke) as adults. Median Mukono / Nakaseke.")

# M3 relationship to head x age group (heatmap) + relationship composition by district
rel_d = pd.crosstab(L.rel_g, L.district).reindex(columns=DISTS)
rel_pct = (rel_d / rel_d.sum() * 100).round(1)
out = pd.concat([rel_d.add_prefix("n_"), rel_pct.add_prefix("pct_")], axis=1)
out.loc["Missing relationship"] = [int(L[L.rel.isna() & (L.district == d)].shape[0]) for d in DISTS] + [np.nan, np.nan]
out.to_csv(F_ROSTER / "relationship_to_head_by_district.csv")
ar = pd.crosstab(L.rel_g, L.age_g).reindex(index=list(REL.values()), columns=AGE_ORDER, fill_value=0)
ar_d = {d: pd.crosstab(L[L.district == d].rel_g, L[L.district == d].age_g).reindex(index=list(REL.values()), columns=AGE_ORDER, fill_value=0)
        for d in DISTS}
pd.concat({"All": ar, **{DIST_LABEL[d]: ar_d[d] for d in DISTS}}, names=["district", "relationship"]).to_csv(
    F_ROSTER / "age_by_relationship.csv")

fig, axes = plt.subplots(1, 2, figsize=(10.6, 3.4), gridspec_kw={"width_ratios": [1, 1.25]})
ax = axes[0]
yy = np.arange(len(rel_pct))[::-1]
for i, d in enumerate(DISTS):
    ax.barh(yy + (0.5 - i) * 0.38, rel_pct[d], height=0.38, color=DIST[d], label=f"{DIST_LABEL[d]} (n={rel_d[d].sum()})")
    for yi, v in zip(yy + (0.5 - i) * 0.38, rel_pct[d]):
        ax.text(v + 0.8, yi, f"{v:.0f}", va="center", fontsize=7.5, color=INK2)
ax.set_yticks(yy, rel_pct.index)
ax.set_xlabel("% of listed members with a relationship code")
ax.grid(axis="y", visible=False)
ax.legend(loc="lower right")
ax.set_title("(a) Relationship to household head")
ax = axes[1]
cm = LinearSegmentedColormap.from_list("q", [SURF, ORD4[0], ORD4[2], ORD4[3]])
im = ax.imshow(ar.values, cmap=cm, aspect="auto")
for i_ in range(ar.shape[0]):
    for j_ in range(ar.shape[1]):
        v = ar.values[i_, j_]
        ax.text(j_, i_, f"{v}", ha="center", va="center", fontsize=7.5, color="white" if v > ar.values.max() * 0.55 else INK)
ax.set_xticks(range(len(AGE_ORDER)), AGE_ORDER)
ax.set_yticks(range(len(ar.index)), ar.index)
ax.set_xlabel("Age group (years)")
ax.grid(False)
ax.set_title("(b) Members by relationship and age group, both districts (number)")
fig.colorbar(im, ax=ax, shrink=0.8, label="Members (number)")
fig.tight_layout(w_pad=2)
save(fig, F_ROSTER / "relationship_and_age_of_members.png",
     f"Roster members of {n_roster_hh.sum()} households (max 6 per household); {int(L.rel.isna().sum())} without relationship code and "
     f"{int(L.age_g.isna().sum())} without age group excluded from the panel concerned. The survey has no 'spouse' code: {two_heads} households "
     "list two or more members as head, mostly a male-female pair, so 'Head' includes spouses. Mukono rosters list no members under 16. "
     "District split of panel (b) in age_by_relationship.csv.")

# M4 dependency ratio
dep = h[["district", "dependency_ratio", "n_elder", "children", "adults"]].copy()
rows = []
fig, ax = plt.subplots(figsize=(6.4, 3.0))
rng = np.random.default_rng(1)
CAP = 6
for i, d in enumerate(DISTS):
    v = dep.loc[dep.district == d, "dependency_ratio"].dropna()
    vv = v.clip(upper=CAP)
    yv = i + rng.uniform(-0.18, 0.18, len(vv))
    ax.scatter(vv, yv, s=9, color=DIST[d], alpha=0.45, linewidths=0)
    q = v.quantile([.25, .5, .75])
    ax.plot([q[.25], q[.75]], [i, i], color=INK, lw=2.2, solid_capstyle="round")
    ax.plot(q[.5], i, "o", color=INK, ms=6, mec=SURF, mew=2)
    ax.text(q[.5], i + 0.3, f"median {q[.5]:.2f}", ha="center", fontsize=8, color=INK)
    rows.append({"district": DIST_LABEL[d], "n": len(v), "median": round(q[.5], 2), "q25": round(q[.25], 2), "q75": round(q[.75], 2),
                 "mean": round(v.mean(), 2), "n_above_cap_6": int((v > CAP).sum()),
                 "median_children": dep.loc[dep.district == d, "children"].median(),
                 "median_adults": dep.loc[dep.district == d, "adults"].median(),
                 "pct_hh_with_member_61plus": round((dep.loc[dep.district == d, "n_elder"] > 0).mean() * 100, 1)})
mw = stats.mannwhitneyu(dep.loc[dep.district == "mukono", "dependency_ratio"].dropna(),
                        dep.loc[dep.district == "nakaseke", "dependency_ratio"].dropna()).pvalue
pd.DataFrame(rows).assign(mann_whitney_p=round(mw, 5)).to_csv(F_ROSTER / "dependency_ratio_by_district.csv", index=False)
ax.set_yticks([0, 1], [DIST_LABEL[d] for d in DISTS])
ax.set_ylim(-0.5, 1.5)
ax.grid(axis="y", visible=False)
ax.set_xlabel(f"Dependency ratio = (children + members 61+) / (adults 16-60)   (capped at {CAP})")
ax.set_title(f"Household dependency ratio by district  [Mann-Whitney {pfmt(mw)}]")
save(fig, F_ROSTER / "dependency_ratio_by_district.png",
     f"{NTXT}; one dot per household, black bar = interquartile range. Denominator floored at 1 adult. Children from the cleaned "
     "children count; adults and 61+ members from resident roster members.")

# console summary
print("data_readiness_assessment:", sorted(p.name for p in F_READY.glob("*.png")))
print("demographics:", sorted(p.name for p in F_DEMO.glob("*.png")))
print("demographics_household_members:", sorted(p.name for p in F_ROSTER.glob("*.png")))
print("roster: members", n_mem.to_dict(), "HH with roster", n_roster_hh.to_dict(), "HH listing >=2 heads", two_heads)
print("roster 0-5 members (resident):", int(((L.age == "0_5") & (L.status == "resident")).sum()))
print(r2[["section", "Mukono_mean_pct_items_answered", "Nakaseke_mean_pct_items_answered"]].to_string(index=False))
