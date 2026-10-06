"""moreFigures - housing group: dwelling, floor area, electricity, house valuation and water.
Re-runs the analyses of the old notebooks House.ipynb, Water.ipynb and the dwelling cells of
'Generic Dataset Analysis.ipynb' on the cleaned v1 data (597 households), with fixes:
  * floor area: Nakaseke recorded in ft2 and unreliable -> floor_area_m2_model for comparisons;
  * distance to water: units differ by district (Nakaseke mostly metres, Mukono mostly km);
  * time to water parsed as in scripts/obj1/module_d_living_conditions.py (plus seconds / unit fixes);
  * electricity purposes asked of grid AND solar users -> denominator = households answering;
  * no lines across categorical axes, no index-scatter plots; income group (li_group) breakdowns added.
Run from repo root:  python scripts/morefigures/housing.py
"""
import re, sys
from pathlib import Path
import numpy as np, pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "obj1"))
from li_style import *  # noqa: E402,F401
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.ticker import FuncFormatter, NullFormatter  # noqa: E402
from matplotlib.text import Text  # noqa: E402

OUT = ROOT / "paper1" / "figures" / "moreFigures"
SURVEY_YEAR = 2025
DISTS = ["mukono", "nakaseke"]
num = lambda x: pd.to_numeric(x, errors="coerce")


def odir(name):
    p = OUT / name; p.mkdir(parents=True, exist_ok=True); return p


# ------------------------------------------------------------------ data
h = pd.read_csv(ROOT / "data/derived/Household_Analysis_v1.csv")
sv = pd.read_csv(ROOT / "data/derived/Survey_Cleaned_v1.csv", low_memory=False)
sv = sv[sv["District"].isin(DISTS)]
d = h.merge(sv, on="_id", how="inner", suffixes=("", "_sv"))
assert len(d) == 597, len(d)
d = d.copy()
import warnings; warnings.simplefilter("ignore", pd.errors.PerformanceWarning)
d["li_group"] = pd.Categorical(d.li_group, LI_GROUPS, ordered=True)
NOTE_LI = "Income group = gross income incl. home-grown food as % of the household-size living income benchmark (v0.02)."


# ------------------------------------------------------------------ helpers
def p_fmt(p):
    return "n/a" if pd.isna(p) else ("<0.001" if p < 0.001 else f"{p:.3f}")


def mw_district(col):
    a, b = [d.loc[d.district == k, col].dropna() for k in DISTS]
    return stats.mannwhitneyu(a, b).pvalue if len(a) and len(b) else np.nan


def kw_li(col, df=None):
    df = d if df is None else df
    gs = [df.loc[df.li_group == g, col].dropna() for g in LI_GROUPS]
    gs = [g for g in gs if len(g)]
    return stats.kruskal(*gs).pvalue if len(gs) > 1 else np.nan


def chi_p(by, cat, df=None):
    df = d if df is None else df
    t = pd.crosstab(df[by], df[cat])
    t = t.loc[t.sum(axis=1) > 0, t.sum(axis=0) > 0]
    return stats.chi2_contingency(t)[1] if t.shape[0] > 1 and t.shape[1] > 1 else np.nan


def describe(df, col, by):
    g = df.groupby(by, observed=True)[col]
    t = pd.DataFrame({"n": g.count(), "mean": g.mean(), "p25": g.quantile(.25), "median": g.median(), "p75": g.quantile(.75)})
    allr = df[col]; t.loc["all"] = [allr.count(), allr.mean(), allr.quantile(.25), allr.median(), allr.quantile(.75)]
    return t


def strip_box(ax, groups, log=False, fmt="{:.0f}", seed=1, label_median=True):
    """groups: list of (label, values Series, colour or Series of district names). Jittered dots + IQR bar + median dot."""
    rng = np.random.default_rng(seed)
    for i, (lab, v, col) in enumerate(groups):
        v = v.dropna()
        if log: v = v[v > 0]
        if isinstance(col, pd.Series):
            c = col.reindex(v.index).map(DIST).fillna(INK2)
        else:
            c = col
        x = i + rng.uniform(-0.2, 0.2, len(v))
        ax.scatter(x, v, s=8, color=c, alpha=0.45, linewidths=0, zorder=2)
        if len(v):
            q = v.quantile([.25, .5, .75])
            ax.plot([i, i], [q[.25], q[.75]], color=INK, lw=2.4, solid_capstyle="round", zorder=3)
            ax.plot(i, q[.5], "o", color=INK, ms=6, mec=SURF, mew=2, zorder=4)
            if label_median:
                ax.text(i + 0.27, q[.5], fmt.format(q[.5]), fontsize=7.5, color=INK, va="center")
    ax.set_xticks(range(len(groups)), [f"{g[0]}\n(n={g[1].dropna().gt(0).sum() if log else g[1].notna().sum()})" for g in groups])
    ax.set_xlim(-0.6, len(groups) - 0.3); ax.grid(axis="x", visible=False)
    if log:
        ax.set_yscale("log"); ax.yaxis.set_minor_formatter(NullFormatter())


def dist_legend(ax, loc="upper right"):
    for k in DISTS:
        ax.scatter([], [], s=18, color=DIST[k], label=DIST_LABEL[k])
    ax.legend(loc=loc, handletextpad=0.2)


def stack100(ax, rows, cats, colors, labels=None):
    """rows: list of (row label, categorical Series). 100%-stacked horizontal bars; returns % table."""
    tab = {}
    for lab, s in rows:
        s = s.dropna(); vc = s.value_counts().reindex(cats, fill_value=0)
        tab[f"{lab} (n={len(s)})"] = vc / max(len(s), 1) * 100
    T = pd.DataFrame(tab).T
    y = np.arange(len(T))[::-1]
    left = np.zeros(len(T))
    for j, c in enumerate(cats):
        w = T[c].values
        ax.barh(y, w, left=left, color=colors[j], height=0.66, edgecolor=SURF, linewidth=1.2, label=(labels or cats)[j])
        for yi, l, wi in zip(y, left, w):
            if wi >= 7: ax.text(l + wi / 2, yi, f"{wi:.0f}", ha="center", va="center", fontsize=7.5,
                                color="white" if j in (0, 2) or colors[j] in ORD4[2:] else INK)
        left += w
    ax.set_yticks(y, T.index); ax.set_xlim(0, 100); ax.grid(axis="y", visible=False)
    ax.set_xlabel("% of households with a valid answer")
    return T.round(1)


def rows_dist_li(series):
    rows = [(DIST_LABEL[k], series[d.district == k]) for k in DISTS]
    rows += [(f"income {g}", series[d.li_group == g]) for g in LI_GROUPS]
    return rows


ugx = FuncFormatter(lambda x, p: money(x))
written = {}


def fig_save(fig, folder, name, note):
    for t_ in fig.findobj(Text):
        if "p=<" in t_.get_text(): t_.set_text(t_.get_text().replace("p=<", "p<"))
    note = note.replace("p=<", "p<").replace("p (all parsed) = <", "p (all parsed) < ")
    save(fig, folder / name, note); written.setdefault(folder.name, []).append(name)


# ================================================================== dwelling_analysis (inventory csv only)
DW = odir("dwelling_analysis")
dw_cols = {
    "Select_the_type_of_dwelling": "dwelling type", "Total_number_of_rooms": "rooms", "Number_of_Bedrooms": "bedrooms",
    "Number_of_kitchens": "kitchens", "Total_Surface_area_Square_Feet": "floor area (recorded)", "floor_area_m2": "floor area m2 (recorded, converted)",
    "floor_area_m2_model": "floor area m2 (modelled)", "House_Walls": "walls", "House_!Roof": "roof (unusable: form re-used wall codes)",
    "House_Floor": "floor", "Is_the_toilet_in_or_outside_the_house": "toilet inside/outside", "Select_which_type_of_toile": "toilet type",
    "Is_your_kitchen_inside_the": "kitchen inside", "Sources_of_Drinking_water": "drinking water source",
    "Sources_of_Non_Drinking_Water": "non-drinking water source", "Is_the_water_piped_inside_": "water piped inside",
    "DIstance_to_source_of_water": "distance to water", "Time_to_source_of_Water": "time to water", "water_costs_per_day": "water cost per day",
    "What_does_the_cost_consist": "water cost components", "energy_source": "cooking energy source", "energy_source_cost": "energy cost",
    "Do_you_have_access_to_electricity": "grid electricity", "Do_you_use_other_sources_of_electricity": "other electricity sources",
    "What_purposes_is_electricity": "electricity purposes", "SECTION_A/_32_If_you_have_elec_ch_do_you_pay_for_it": "grid bill (free text)",
    "If_you_are_the_owner_of_the_house,_(and_they_don_t_know_rent_costs),_how_much_would_it_cost_to_build_this_house": "build cost",
    "If_you_are_the_owner_of_the_house,_what_do_you_think_would_it_cost_to_rent_a_house_that_is_similar_to_this_one_in_this_village_Per_Month": "rent of similar house / month",
    "When_was_the_house_built": "year built", "Investigator_s_opinion_Does_h": "enumerator: housing meets standard (not comparable across districts)"}
inv = []
for c, lab in dw_cols.items():
    r = {"variable": lab, "survey column": c}
    for k in DISTS:
        s = d.loc[d.district == k, c]; r[f"answered {DIST_LABEL[k]}"] = int(s.notna().sum()); r[f"distinct {DIST_LABEL[k]}"] = int(s.nunique())
    inv.append(r)
pd.DataFrame(inv).to_csv(DW / "dwelling_variables_inventory.csv", index=False)

# ================================================================== dwelling_analysis_core
DC = odir("dwelling_analysis_core")

# --- household size (old clean_household_size)
t = describe(d, "hh_size", "district")
t2 = describe(d, "hh_size", "li_group")
pd.concat([t.assign(by="district"), t2.drop(index="all").assign(by="li_group")]).round(2).to_csv(DC / "household_size.csv")
fig, axs = plt.subplots(1, 2, figsize=(8.2, 3.6), gridspec_kw={"width_ratios": [2, 4]}, sharey=True)
strip_box(axs[0], [(DIST_LABEL[k], d.loc[d.district == k, "hh_size"], DIST[k]) for k in DISTS])
strip_box(axs[1], [(g, d.loc[d.li_group == g, "hh_size"], d.district) for g in LI_GROUPS])
axs[0].set_ylabel("Household members (persons)"); axs[0].set_title("Household size by district")
axs[1].set_title("…and by income group"); axs[1].set_xlabel("Income as % of household living income benchmark")
dist_legend(axs[1])
fig_save(fig, DC, "household_size.png",
         f"Dots = households, bar = interquartile range, circle = median (label). Mann-Whitney district p={p_fmt(mw_district('hh_size'))}; "
         f"Kruskal-Wallis across income groups p={p_fmt(kw_li('hh_size'))}. Household size from the cleaned roster (Household_Analysis_v1). {NOTE_LI}")

# --- floor area: recorded vs modelled (old avg_house_size_*, house_size_*; adjustment dropped)
d["floor_recorded"] = num(d.floor_area_m2); d["floor_model"] = num(d.floor_area_m2_model)
bed = num(d.Number_of_Bedrooms).where(lambda x: x > 0)
d["m2_per_person"] = d.floor_model / d.hh_size
d["persons_per_bedroom"] = d.hh_size / bed
fa = []
for k in DISTS:
    for col, lab in [("floor_recorded", "recorded"), ("floor_model", "modelled")]:
        s = d.loc[d.district == k, col]
        fa.append({"district": DIST_LABEL[k], "floor area": lab, "n": s.count(), "mean": s.mean(), "p25": s.quantile(.25), "median": s.median(), "p75": s.quantile(.75)})
pd.DataFrame(fa).round(1).to_csv(DC / "floor_area_recorded_vs_model.csv", index=False)
fig, ax = plt.subplots(figsize=(6.6, 3.8))
grp = []
for k in DISTS:
    grp += [(f"{DIST_LABEL[k]}\nrecorded", d.loc[d.district == k, "floor_recorded"], DIST[k]),
            (f"{DIST_LABEL[k]}\nmodelled", d.loc[d.district == k, "floor_model"], DIST[k])]
strip_box(ax, grp, log=True)
ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f"{x:g}"))
ax.set_ylabel("Floor area (m², log scale)")
ax.set_title("Floor area: recorded vs modelled, by district")
fig_save(fig, DC, "floor_area_recorded_vs_model.png",
         "Recorded: Mukono values behave like m²; Nakaseke values were recorded in ft² (converted ×0.0929) and are bunched and unrelated to rooms - low reliability. "
         "Modelled = floor_area_m2_model (log-linear on rooms, bedrooms, dwelling type, walls, floor; fitted on Mukono, R²=0.62), the same basis for both districts (cleaning log §3).")

fc = []
for col, lab in [("floor_model", "floor area modelled (m2)"), ("m2_per_person", "m2 per person"), ("persons_per_bedroom", "persons per bedroom")]:
    for by in ["district", "li_group"]:
        t = describe(d, col, by).drop(index="all") if by == "li_group" else describe(d, col, by)
        t.insert(0, "variable", lab); t.insert(1, "by", by)
        t["p"] = p_fmt(mw_district(col) if by == "district" else kw_li(col))
        fc.append(t)
pd.concat(fc).round(3).to_csv(DC / "floor_area_crowding_by_li_group.csv")
fig, axs = plt.subplots(1, 3, figsize=(10.8, 3.7), gridspec_kw={"wspace": 0.35})
for ax, (col, lab, lg) in zip(axs, [("floor_model", "Modelled floor area (m², log)", True), ("m2_per_person", "Modelled floor area per person (m², log)", True),
                                    ("persons_per_bedroom", "Persons per bedroom", False)]):
    strip_box(ax, [(g, d.loc[d.li_group == g, col], d.district) for g in LI_GROUPS], log=lg, fmt="{:.1f}" if not lg else "{:.0f}")
    if lg: ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f"{x:g}"))
    ax.set_ylabel(lab); ax.set_title(f"{lab.split(' (')[0]}\nKruskal-Wallis p={p_fmt(kw_li(col))}", fontsize=9.5)
    ax.tick_params(axis="x", labelsize=7.5)
dist_legend(axs[2])
fig.suptitle("Dwelling size and crowding by income group", x=0.0, ha="left", fontweight="bold", fontsize=10.5, y=1.04)
fig_save(fig, DC, "floor_area_crowding_by_li_group.png",
         f"Floor area = floor_area_m2_model (predicted from rooms/materials, so not an independent measurement). Bedrooms = reported number of bedrooms (>0). "
         f"x-axis: income as % of household living income benchmark. {NOTE_LI}")

# --- dwelling type (old dwelling_type_line)
dt = d.Select_the_type_of_dwelling.map({"permanent_house": "Permanent", "non_durable_house_semi_permanent": "Semi-permanent / non-durable", "other": "Other"})
fig, ax = plt.subplots(figsize=(6.8, 3.6))
T = stack100(ax, rows_dist_li(dt), ["Permanent", "Semi-permanent / non-durable", "Other"], [ORD4[2], ORD4[0], GRID])
ax.legend(loc="lower left", bbox_to_anchor=(0, 1.0), ncol=3)
ax.set_title("Dwelling type by district and income group", pad=24)
T["chi2 p (district)"] = p_fmt(chi_p("district", "_dt", d.assign(_dt=dt))); T["chi2 p (income groups)"] = p_fmt(chi_p("li_group", "_dt", d.assign(_dt=dt)))
T.to_csv(DC / "dwelling_type.csv")
fig_save(fig, DC, "dwelling_type.png",
         f"Segment labels in %. Chi-square: district p={T.iloc[0, -2]}, income groups p={T.iloc[0, -1]}. Income-group rows pool both districts (Nakaseke is over-represented in <25%). {NOTE_LI}")

# --- drinking water source (old water_source_line)
ws_map = {"borehole": "Borehole", "piped_water_system": "Piped", "rain_storage_in_tank": "Rain tank", "open_well": "Open well", "river": "River", "other": "Other"}
ws = d.Sources_of_Drinking_water.map(ws_map)
cats = ["Piped", "Borehole", "Rain tank", "Open well", "River", "Other"]
fig, ax = plt.subplots(figsize=(7.2, 3.7))
T = stack100(ax, rows_dist_li(ws), cats, [SRC[2], ORD4[2], ORD4[0], SRC[3], SRC[1], GRID])
ax.legend(loc="lower left", bbox_to_anchor=(0, 1.0), ncol=6, columnspacing=0.8)
ax.set_title("Main drinking-water source by district and income group", pad=24)
T["chi2 p (district)"] = p_fmt(chi_p("district", "_w", d.assign(_w=ws))); T["chi2 p (income groups)"] = p_fmt(chi_p("li_group", "_w", d.assign(_w=ws)))
T.to_csv(DC / "drinking_water_source.csv")
fig_save(fig, DC, "drinking_water_source.png",
         f"Segment labels in % (shown when ≥7%). Open well, river and other = unprotected (module D). Chi-square: district p={T.iloc[0, -2]}, income groups p={T.iloc[0, -1]}. {NOTE_LI}")

# --- cooking energy (old energy_source_rates / energy_source_by_district_line)
es = d.energy_source.map({"firewood": "Firewood", "charcoal": "Charcoal", "electricity": "Electricity", "gas_tank_cylinder": "Gas (LPG)"})
fig, ax = plt.subplots(figsize=(7.0, 3.6))
T = stack100(ax, rows_dist_li(es), ["Firewood", "Charcoal", "Electricity", "Gas (LPG)"], [SRC[1], SRC[3], ORD4[2], SRC[2]])
ax.legend(loc="lower left", bbox_to_anchor=(0, 1.0), ncol=4)
ax.set_title("Main cooking energy source by district and income group", pad=24)
T["chi2 p (district)"] = p_fmt(chi_p("district", "_e", d.assign(_e=es))); T["chi2 p (income groups)"] = p_fmt(chi_p("li_group", "_e", d.assign(_e=es)))
T.to_csv(DC / "cooking_energy_source.csv")
fig_save(fig, DC, "cooking_energy_source.png",
         f"Question 'energy source' (main source, single answer). Segment labels in % (shown when ≥7%). Chi-square: district p={T.iloc[0, -2]}, income groups p={T.iloc[0, -1]}. {NOTE_LI}")

# --- dwelling characteristics table (supporting; lack-of-element shares as in module D)
walls, floor = d.House_Walls.fillna(""), d.House_Floor.fillna("")
CH = {"Permanent dwelling": (dt.eq("Permanent"), dt.notna()),
      "Brick/block walls": (walls.str.contains("bricks_blocks"), walls != ""),
      "Cement/stone floor": (floor.str.contains("cement|stone"), floor != ""),
      "Toilet inside the house": (d.Is_the_toilet_in_or_outside_the_house.eq("inside"), d.Is_the_toilet_in_or_outside_the_house.notna()),
      "Kitchen inside (incl. both)": (d.Is_your_kitchen_inside_the.isin(["Yes", "both"]), d.Is_your_kitchen_inside_the.notna()),
      "Water piped inside": (d.Is_the_water_piped_inside_.eq("Yes"), d.Is_the_water_piped_inside_.notna())}
rows = []
for lab, (c, ok) in CH.items():
    s = c.astype(float).where(ok); r = {"characteristic": lab, "n": int(s.notna().sum())}
    for k in DISTS: r[DIST_LABEL[k]] = round(s[d.district == k].mean() * 100, 1)
    r["All"] = round(s.mean() * 100, 1)
    for g in LI_GROUPS: r[f"income {g}"] = round(s[d.li_group == g].mean() * 100, 1)
    r["chi2 p (district)"] = p_fmt(chi_p("district", "_s", d.assign(_s=s)))
    r["chi2 p (income groups)"] = p_fmt(chi_p("li_group", "_s", d.assign(_s=s)))
    rows.append(r)
pd.DataFrame(rows).to_csv(DC / "dwelling_characteristics_pct.csv", index=False)

# ================================================================== electricity_analysis
EL = odir("electricity_analysis")
grid = d.Do_you_have_access_to_electricity
solar = d.Do_you_use_other_sources_of_electricity.fillna("").str.contains("solar")
d["elec"] = np.select([grid.eq("Yes"), grid.eq("No") & solar, grid.eq("No")], ["Grid", "Solar only", "Neither"], default=None)
d.loc[grid.isna(), "elec"] = np.nan
fig, ax = plt.subplots(figsize=(6.8, 3.6))
T = stack100(ax, rows_dist_li(d.elec), ["Grid", "Solar only", "Neither"], [ORD4[2], SRC[3], GRID])
ax.legend(loc="lower left", bbox_to_anchor=(0, 1.0), ncol=3)
ax.set_title("Electricity access by district and income group", pad=24)
T["chi2 p (district)"] = p_fmt(chi_p("district", "elec")); T["chi2 p (income groups)"] = p_fmt(chi_p("li_group", "elec"))
T.to_csv(EL / "electricity_access.csv")
fig_save(fig, EL, "electricity_access.png",
         f"Grid = 'access to electricity' Yes (some grid households also use solar). Solar only = no grid but solar panels listed as other source. "
         f"Households with grid answer missing excluded (n={int(grid.isna().sum())}). Chi-square: district p={T.iloc[0, -2]}, income groups p={T.iloc[0, -1]}. {NOTE_LI}")

PURP = [("lighting", "Lighting"), ("television", "Television"), ("radio", "Radio"), ("cooking", "Cooking"), ("refrigeration", "Refrigeration"),
        ("home_sme_business", "Home business"), ("water_pumping", "Water pumping"), ("other", "Other (unspecified)")]
pt = d.What_purposes_is_electricity.fillna("").str.lower().str.split()
ans = d.What_purposes_is_electricity.notna()
for code, lab in PURP:
    d[f"use_{code}"] = pt.map(lambda L, c=code: float(c in L)).where(ans)
d["n_purposes"] = pt.map(len).where(ans).astype(float)
d["n_purposes_specific"] = pt.map(lambda L: len([x for x in L if x != "other"])).where(ans).astype(float)
rows = []
for code, lab in PURP:
    s = d[f"use_{code}"]; r = {"purpose": lab, "n answering": int(s.notna().sum())}
    for k in DISTS: r[DIST_LABEL[k]] = round(s[d.district == k].mean() * 100, 1)
    for e in ["Grid", "Solar only"]: r[e] = round(s[d.elec == e].mean() * 100, 1)
    r["All"] = round(s.mean() * 100, 1); r["chi2 p (district)"] = p_fmt(chi_p("district", f"use_{code}"))
    rows.append(r)
P = pd.DataFrame(rows); P.to_csv(EL / "electricity_purpose.csv", index=False)
fig, axs = plt.subplots(1, 2, figsize=(9.2, 3.8), sharey=True)
y = np.arange(len(P))[::-1]
for ax, keys, cols, ttl in [(axs[0], DISTS, [DIST[k] for k in DISTS], "by district"), (axs[1], ["Grid", "Solar only"], [ORD4[2], SRC[3]], "by electricity source")]:
    names = [DIST_LABEL[k] for k in keys] if keys == DISTS else keys
    lo, hi = P[names].min(axis=1), P[names].max(axis=1)
    ax.hlines(y, lo, hi, color=GRID, lw=3)
    for nm, c in zip(names, cols):
        nn = int(d.loc[(d.district == nm.lower()) if keys == DISTS else (d.elec == nm), "use_lighting"].notna().sum())
        ax.scatter(P[nm], y, s=42, color=c, edgecolor=SURF, linewidth=1.5, zorder=3, label=f"{nm} (n={nn})")
    ax.set_xlim(0, 100); ax.grid(axis="y", visible=False); ax.set_title(f"Uses of electricity {ttl}")
    ax.set_xlabel("% of households answering the purpose question"); ax.legend(loc="lower right")
axs[0].set_yticks(y, P.purpose)
fig_save(fig, EL, "electricity_purpose.png",
         f"Multiple answers allowed. The question was answered by grid AND solar users (n={int(ans.sum())}; the old notebook kept grid users only). "
         f"'Other' was not specified (frequent in Mukono; possibly phone charging). Electricity-source panel excludes {int((ans & ~d.elec.isin(['Grid', 'Solar only'])).sum())} answering households with no/missing grid answer and no solar.")

# use intensity (number of specific purposes)
ib = d.n_purposes_specific.clip(upper=4).map({0: "0 (only 'other')", 1: "1", 2: "2", 3: "3", 4: "4+"})
cats = ["0 (only 'other')", "1", "2", "3", "4+"]
fig, ax = plt.subplots(figsize=(6.8, 3.6))
T = stack100(ax, rows_dist_li(ib), cats, [GRID] + ORD4)
ax.legend(loc="lower left", bbox_to_anchor=(0, 1.0), ncol=5, title="number of named purposes", title_fontsize=8)
ax.set_title("Number of uses of electricity per household", pad=34)
T["mean"] = [d.loc[d.district == k, "n_purposes_specific"].mean() for k in DISTS] + [d.loc[d.li_group == g, "n_purposes_specific"].mean() for g in LI_GROUPS]
T["Mann-Whitney p (district)"] = p_fmt(mw_district("n_purposes_specific")); T["Kruskal p (income groups)"] = p_fmt(kw_li("n_purposes_specific"))
T.round(2).to_csv(EL / "electricity_use_intensity.csv")
fig_save(fig, EL, "electricity_use_intensity.png",
         f"Households answering the purpose question (grid or solar). Named purposes exclude 'other'. Mann-Whitney district p={T.iloc[0, -2]}; "
         f"Kruskal-Wallis income groups p={T.iloc[0, -1]}. {NOTE_LI}")

# grid bill (table only)
bill_txt = d["SECTION_A/_32_If_you_have_elec_ch_do_you_pay_for_it"]
d["grid_bill_month"] = bill_txt.map(lambda v: np.nan if pd.isna(v) else (float(m.group(1)) if (m := re.search(r"(\d{3,})", str(v).replace(",", ""))) else np.nan))
gb = describe(d[d.elec == "Grid"], "grid_bill_month", "district")
gb["note"] = "UGX per month as stated (free text; 'per month' assumed where unit missing); grid households only"
gb.round(0).to_csv(EL / "grid_bill_per_month.csv")

# ================================================================== house valuation
HV0 = odir("house_valuation"); HV = odir("house_valuation_clean")
BCOL = "If_you_are_the_owner_of_the_house,_(and_they_don_t_know_rent_costs),_how_much_would_it_cost_to_build_this_house"
RCOL = "If_you_are_the_owner_of_the_house,_what_do_you_think_would_it_cost_to_rent_a_house_that_is_similar_to_this_one_in_this_village_Per_Month"
B_LO, B_HI, R_LO, R_HI = 100_000, 100_000_000, 5_000, 2_000_000
braw, rraw, yraw = num(d[BCOL]), num(d[RCOL]), num(d.When_was_the_house_built)
d["build_cost"] = braw.where(braw.between(B_LO, B_HI))
d["rent_month"] = rraw.where(rraw.between(R_LO, R_HI))
d["years_to_recover"] = d.build_cost / (12 * d.rent_month)
d["year_built"] = yraw.where(yraw.between(1950, SURVEY_YEAR))
d["house_age"] = SURVEY_YEAR - d.year_built
dropped = pd.DataFrame({
    "variable": ["build cost", "monthly rent", "year built"],
    "rule": [f"{B_LO:,}-{B_HI:,} UGX", f"{R_LO:,}-{R_HI:,} UGX/month", f"1950-{SURVEY_YEAR}"],
    "answered": [int(braw.notna().sum()), int(rraw.notna().sum()), int(yraw.notna().sum())],
    "set missing": [int((braw.notna() & d.build_cost.isna()).sum()), int((rraw.notna() & d.rent_month.isna()).sum()), int((yraw.notna() & d.year_built.isna()).sum())],
    "values set missing": [sorted(braw[braw.notna() & d.build_cost.isna()].unique().tolist()), sorted(rraw[rraw.notna() & d.rent_month.isna()].unique().tolist()),
                           sorted(yraw[yraw.notna() & d.year_built.isna()].unique().tolist())]})
dropped.to_csv(HV / "cleaning_rule_values_set_missing.csv", index=False)
VV = [("build_cost", "Cost to build this house (UGX)"), ("rent_month", "Rent of a similar house (UGX / month)"),
      ("years_to_recover", "Build cost ÷ annual rent (years)"), ("house_age", "House age (years)")]
vs = []
for col, lab in VV:
    for by in ["district", "li_group"]:
        t = describe(d, col, by); t = t.drop(index="all") if by == "li_group" else t
        t.insert(0, "variable", lab); t.insert(1, "by", by)
        t["p"] = p_fmt(mw_district(col) if by == "district" else kw_li(col))
        vs.append(t)
pd.concat(vs).round(2).to_csv(HV / "house_valuation_summary.csv")

fig, axs = plt.subplots(1, 3, figsize=(10.8, 3.8), gridspec_kw={"wspace": 0.45})
for ax, (col, lab) in zip(axs, VV[:3]):
    strip_box(ax, [(DIST_LABEL[k], d.loc[d.district == k, col], DIST[k]) for k in DISTS], log=True,
              fmt="{:.1f}" if col == "years_to_recover" else "{}")
    if col != "years_to_recover":
        ax.yaxis.set_major_formatter(ugx)
        for t_ in ax.texts: t_.set_text(money(float(t_.get_text())))
    else:
        ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f"{x:g}"))
    ax.set_ylabel(lab + ", log scale", fontsize=8.5); ax.set_title(f"Mann-Whitney p={p_fmt(mw_district(col))}", fontsize=9, fontweight="normal")
fig.suptitle("Owner-estimated house value: build cost, rent and their ratio, by district", x=0.0, ha="left", fontweight="bold", fontsize=10.5, y=1.03)
fig_save(fig, HV, "valuation_by_district.png",
         f"Owner estimates (not market transactions). Cleaning rule: build cost kept if {B_LO/1e3:.0f}k-{B_HI/1e6:.0f}M UGX, rent if {R_LO/1e3:.0f}k-{R_HI/1e6:.0f}M UGX/month, "
         f"other values set missing (see cleaning_rule_values_set_missing.csv); no percentile trimming - log axes instead. Ratio needs both answers.")

fig, axs = plt.subplots(1, 2, figsize=(9.0, 3.8), gridspec_kw={"wspace": 0.35})
for ax, (col, lab) in zip(axs, VV[:2]):
    strip_box(ax, [(g, d.loc[d.li_group == g, col], d.district) for g in LI_GROUPS], log=True, fmt="{}")
    ax.yaxis.set_major_formatter(ugx)
    for t_ in ax.texts: t_.set_text(money(float(t_.get_text())))
    ax.set_ylabel(lab + ", log scale", fontsize=8.5); ax.set_title(f"Kruskal-Wallis p={p_fmt(kw_li(col))}", fontsize=9, fontweight="normal")
    ax.tick_params(axis="x", labelsize=7.5)
dist_legend(axs[1], loc="lower right")
fig.suptitle("Owner-estimated build cost and rent by income group", x=0.0, ha="left", fontweight="bold", fontsize=10.5, y=1.03)
fig_save(fig, HV, "valuation_by_li_group.png", f"Same cleaning rule as valuation_by_district. x-axis: income as % of household living income benchmark. {NOTE_LI}")

fig, ax = plt.subplots(figsize=(6.0, 4.4))
sc = d.dropna(subset=["build_cost", "rent_month"])
rng = np.random.default_rng(3)
for k in DISTS:
    s = sc[sc.district == k]
    ax.scatter(s.rent_month * np.exp(rng.normal(0, 0.03, len(s))), s.build_cost, s=12, color=DIST[k], alpha=0.55, linewidths=0,
               label=f"{DIST_LABEL[k]} (n={len(s)}, Spearman ρ={stats.spearmanr(s.rent_month, s.build_cost)[0]:.2f})")
for yrs, ls in [(10, (0, (4, 3))), (50, (0, (1, 2)))]:
    xx = np.array([R_LO, R_HI]); ax.plot(xx, xx * 12 * yrs, color=INK2, lw=1, ls=ls)
    ax.text(1.0e4 if yrs == 50 else 6e5, (1.0e4 if yrs == 50 else 6e5) * 12 * yrs * 1.25, f"{yrs} years of rent", color=INK2, fontsize=7.5, ha="left" if yrs == 50 else "right")
ax.set_xscale("log"); ax.set_yscale("log"); ax.xaxis.set_major_formatter(ugx); ax.yaxis.set_major_formatter(ugx)
ax.set_xlim(8e3, 2.2e6); ax.set_ylim(8e4, 1.2e8)
ax.set_xlabel("Rent of a similar house (UGX / month, log)"); ax.set_ylabel("Cost to build this house (UGX, log)")
ax.set_title("Build cost vs rent of a similar house"); ax.legend(loc="lower right", fontsize=7.5)
sc[["_id", "district", "li_group", "rent_month", "build_cost", "years_to_recover"]].to_csv(HV / "build_vs_rent_points.csv", index=False)
fig_save(fig, HV, "build_vs_rent_scatter.png", "Owner estimates, both answers present after cleaning rule. Rent jittered slightly (many round values). Reference lines: build cost = 10 and 50 years of rent.")

fig, axs = plt.subplots(1, 2, figsize=(8.4, 3.6), gridspec_kw={"width_ratios": [2, 4]}, sharey=True)
strip_box(axs[0], [(DIST_LABEL[k], d.loc[d.district == k, "house_age"], DIST[k]) for k in DISTS])
strip_box(axs[1], [(g, d.loc[d.li_group == g, "house_age"], d.district) for g in LI_GROUPS])
axs[0].set_ylabel(f"House age (years, {SURVEY_YEAR} − year built)"); axs[0].set_title("House age by district")
axs[1].set_title("…and by income group"); axs[1].tick_params(axis="x", labelsize=7.5); dist_legend(axs[1])
fig_save(fig, HV, "house_age.png",
         f"Year built kept if 1950-{SURVEY_YEAR} (survey year {SURVEY_YEAR}; old notebook used 2026). Mann-Whitney district p={p_fmt(mw_district('house_age'))}; "
         f"Kruskal-Wallis income groups p={p_fmt(kw_li('house_age'))}. {NOTE_LI}")

# ================================================================== water_analysis
WA = odir("water_analysis")
DIST_CAP = 3500


def dist_m(v):
    """distance to water in metres. Follows scripts/benchmark/build_participants.py dist() (km if 'km'; 'm' units;
    unit-less <=20 = km, >20 = m; 'soccer [pitches]' and minutes -> missing) with fixes: letter O for zero ('O.5km'),
    '0. 5km', '1k' = km, 'feet', 'In the compound' = 0 m, metre values < 1 with 'm' read as km ('0.02m')."""
    if pd.isna(v): return np.nan
    t = str(v).lower().strip()
    if "compound" in t: return 0.0
    if "soccer" in t or "min" in t: return np.nan
    t = re.sub(r"(?<![\d])o(?=[\.\d])", "0", t); t = re.sub(r"(\d)\.\s+(\d)", r"\1.\2", t)
    m = re.search(r"\d+(?:\.\d+)?", t)
    if not m: return np.nan
    x = float(m.group())
    if "feet" in t or "ft" in t: return x * 0.3048
    if "km" in t or "kilo" in t or re.search(r"\dk\b", t): return x * 1000
    if "m" in t: return x if x >= 1 else x * 1000
    return x * 1000 if x <= 20 else x


def to_min(s):
    """minutes; module D to_min() (number x 60 if 'hr/hour') plus: 'one hour' = 60, seconds /60,
    'km' answers and unit-less numbers > 180 (look like metres) -> missing."""
    if pd.isna(s): return np.nan
    s = str(s).lower().strip()
    if s.startswith("one hour"): return 60.0
    if "km" in s: return np.nan
    m = re.search(r"(\d+(?:\.\d+)?)", s)
    if not m: return np.nan
    x = float(m.group(1))
    if re.search(r"h(ou)?r", s): return x * 60
    if "sec" in s: return x / 60
    if not re.search(r"[a-z]", s) and x > 180: return np.nan
    return x


d["water_m"] = d.DIstance_to_source_of_water.map(dist_m)
d["water_min"] = d.Time_to_source_of_Water.map(to_min)
d["water_min_moduleD"] = d.Time_to_source_of_Water.map(lambda s: np.nan if pd.isna(s) else (lambda m: float(m.group(1)) * (60 if re.search(r"h(ou)?r", str(s).lower()) else 1) if m else np.nan)(re.search(r"(\d+(?:\.\d+)?)", str(s).lower())))
d["water_cost_day"] = num(d.water_costs_per_day)
d[["_id", "district", "li_group", "DIstance_to_source_of_water", "water_m", "Time_to_source_of_Water", "water_min", "water_min_moduleD", "water_costs_per_day"]].to_csv(
    WA / "water_parsed_household.csv", index=False)

wq = []
for k in DISTS:
    s = d[d.district == k]
    wq.append({"district": DIST_LABEL[k], "distance answered": int(s.DIstance_to_source_of_water.notna().sum()),
               "distance parsed": int(s.water_m.notna().sum()), "distance unparseable (incl. 'soccer pitches', minutes)": int((s.DIstance_to_source_of_water.notna() & s.water_m.isna()).sum()),
               f"distance > {DIST_CAP} m": int((s.water_m > DIST_CAP).sum()),
               "time answered": int(s.Time_to_source_of_Water.notna().sum()), "time parsed": int(s.water_min.notna().sum()),
               "time > 30 min (this parse)": int((s.water_min > 30).sum()), "time > 30 min (module D parse)": int((s.water_min_moduleD > 30).sum())})
pd.DataFrame(wq).to_csv(WA / "water_parsing_quality.csv", index=False)

# distance by district (old: avg/boxplot/trimmed/scatter)
ds = []
for k in DISTS + ["all"]:
    s = d.water_m if k == "all" else d.loc[d.district == k, "water_m"]
    st = s[s <= DIST_CAP]
    ds.append({"district": DIST_LABEL.get(k, "All"), "n parsed": int(s.notna().sum()), "median all (m)": s.median(), "mean all (m)": s.mean(),
               f"n > {DIST_CAP} m": int((s > DIST_CAP).sum()), f"n <= {DIST_CAP} m": int(st.count()), "p25 (m)": st.quantile(.25), f"median <= {DIST_CAP} m": st.median(),
               "p75 (m)": st.quantile(.75), f"mean <= {DIST_CAP} m": st.mean(), "% > 1 km": (s > 1000).mean() * 100 if s.notna().any() else np.nan})
ds = pd.DataFrame(ds); ds["Mann-Whitney p (district, all parsed)"] = p_fmt(mw_district("water_m")); ds.round(1).to_csv(WA / "distance_to_water_by_district.csv", index=False)
fig, ax = plt.subplots(figsize=(5.4, 3.9))
strip_box(ax, [(DIST_LABEL[k], d.loc[(d.district == k) & (d.water_m <= DIST_CAP), "water_m"], DIST[k]) for k in DISTS])
ax.axhline(1000, color=INK2, lw=1, ls=(0, (4, 3))); ax.text(1.55, 1010, "1 km", fontsize=7.5, color=INK2, va="bottom")
ax.set_ylabel("Distance to drinking-water source (m)"); ax.set_title(f"Distance to water source by district (≤ {DIST_CAP/1000:g} km)")
fig_save(fig, WA, "distance_to_water_by_district.png",
         f"Units harmonised: Mukono answers mostly km (unit-less ≤20 read as km), Nakaseke mostly metres. Not shown: >{DIST_CAP} m "
         f"(Mukono {ds.iloc[0][f'n > {DIST_CAP} m']}, Nakaseke {ds.iloc[1][f'n > {DIST_CAP} m']}) and unparseable answers incl. 'x soccer pitches' "
         f"(see water_parsing_quality.csv). Mann-Whitney district p (all parsed) = {ds.iloc[0, -1]}.")

# distance and time by LI group
wl = []
for col in ["water_m", "water_min"]:
    t = describe(d, col, "li_group").drop(index="all"); t.insert(0, "variable", col); t["Kruskal p"] = p_fmt(kw_li(col))
    t["Mann-Whitney p (district)"] = p_fmt(mw_district(col)); wl.append(t)
pd.concat(wl).round(2).to_csv(WA / "water_access_by_li_group.csv")
fig, axs = plt.subplots(1, 2, figsize=(9.6, 3.9))
strip_box(axs[0], [(g, d.loc[(d.li_group == g) & (d.water_m <= DIST_CAP), "water_m"], d.district) for g in LI_GROUPS])
axs[0].set_ylabel(f"Distance to water source (m, ≤ {DIST_CAP} m)"); axs[0].set_title(f"Distance  (Kruskal-Wallis p={p_fmt(kw_li('water_m'))})", fontsize=9.5)
strip_box(axs[1], [(g, d.loc[(d.li_group == g) & (d.water_min <= 120), "water_min"], d.district) for g in LI_GROUPS])
axs[1].axhline(30, color=INK2, lw=1, ls=(0, (4, 3))); axs[1].text(3.2, 31, "30 min", fontsize=7.5, color=INK2, va="bottom")
axs[1].set_ylabel("Time to water source (minutes, ≤ 120)"); axs[1].set_title(f"Time  (Kruskal-Wallis p={p_fmt(kw_li('water_min'))})", fontsize=9.5)
for ax in axs: ax.tick_params(axis="x", labelsize=7.5)
dist_legend(axs[1])
fig.suptitle("Distance and time to drinking water by income group", x=0.0, ha="left", fontweight="bold", fontsize=10.5, y=1.03)
fig_save(fig, WA, "water_access_by_li_group.png",
         f"Tests use all parsed values (display capped at {DIST_CAP} m / 120 min). Time not stated as one-way or round trip. x-axis: income as % of household living income benchmark. {NOTE_LI}")

# distance vs time (consistency check; replaces index scatter)
fig, ax = plt.subplots(figsize=(5.8, 4.2))
for k in DISTS:
    s = d[(d.district == k) & (d.water_m > 0) & (d.water_min > 0)]
    ax.scatter(s.water_m, s.water_min, s=12, color=DIST[k], alpha=0.55, linewidths=0,
               label=f"{DIST_LABEL[k]} (n={len(s)}, Spearman ρ={stats.spearmanr(s.water_m, s.water_min)[0]:.2f})")
ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlabel("Distance to water source (m, log)"); ax.set_ylabel("Time to water source (min, log)")
ax.xaxis.set_major_formatter(FuncFormatter(lambda x, p: f"{x:g}")); ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f"{x:g}"))
xx = np.array([1, 2e4]); ax.plot(xx, xx / 1000 / 4 * 60, color=INK2, lw=1, ls=(0, (4, 3))); ax.text(3000, 0.6, "line: walking 4 km/h one way", fontsize=7.5, color=INK2, ha="center")
ax.set_ylim(0.05, 600)
ax.legend(loc="upper left", fontsize=7.5); ax.set_title("Reported distance vs time to water (unit check)")
fig_save(fig, WA, "distance_vs_time.png", f"Households with both answers > 0 after parsing. A positive relation supports the unit harmonisation; points far above the line may be queueing or round trips. Data problem: {int(((d.district=='nakaseke') & (d.water_m < 50) & (d.water_min >= 5)).sum())} Nakaseke answers of <50 m (e.g. '10m', '15m') come with 5-30 min - 'm' may mean minutes there.")

# water cost per day
wc = []
for k in DISTS + ["all"]:
    s = d.water_cost_day if k == "all" else d.loc[d.district == k, "water_cost_day"]
    pos = s[s > 0]
    wc.append({"district": DIST_LABEL.get(k, "All"), "n answered": int(s.notna().sum()), "% paying 0": (s == 0).sum() / s.notna().sum() * 100,
               "n paying > 0": int(pos.count()), "p25 (UGX/day, >0)": pos.quantile(.25), "median (UGX/day, >0)": pos.median(),
               "p75 (UGX/day, >0)": pos.quantile(.75), "mean (UGX/day, >0)": pos.mean(), "median x 365 (UGX/yr, >0)": pos.median() * 365})
wc = pd.DataFrame(wc)
pos = d[d.water_cost_day > 0]
wc["Mann-Whitney p (district, >0)"] = p_fmt(stats.mannwhitneyu(*[pos.loc[pos.district == k, "water_cost_day"] for k in DISTS]).pvalue)
wc["Kruskal p (income groups, >0)"] = p_fmt(kw_li("water_cost_day", pos))
wc.round(1).to_csv(WA / "water_cost_by_district.csv", index=False)
comp = d.What_does_the_cost_consist.fillna("").str.lower()
cc = pd.DataFrame({c: [round(comp[(d.district == k) & (comp != "")].str.contains(c).mean() * 100, 1) for k in DISTS] for c in ["fees", "maintenance", "collection"]},
                  index=[DIST_LABEL[k] for k in DISTS])
cc["n"] = [int(((d.district == k) & (comp != "")).sum()) for k in DISTS]; cc.to_csv(WA / "water_cost_components_pct.csv")
fig, axs = plt.subplots(1, 2, figsize=(9.0, 3.8), gridspec_kw={"width_ratios": [2, 3]})
grp = [(DIST_LABEL[k], d.loc[d.district == k, "water_cost_day"], DIST[k]) for k in DISTS]
strip_box(axs[0], grp, log=True)
axs[0].yaxis.set_major_formatter(FuncFormatter(lambda x, p: f"{x:,.0f}"))
axs[0].set_ylabel("Water cost (UGX per day, log; > 0 only)")
for i, k in enumerate(DISTS):
    axs[0].text(i, 9, f"{wc.iloc[i]['% paying 0']:.0f}% pay 0", ha="center", fontsize=7.5, color=INK2)
axs[0].set_ylim(6, 8000); axs[0].set_title("By district", fontsize=9.5)
strip_box(axs[1], [(g, pos.loc[pos.li_group == g, "water_cost_day"], pos.district) for g in LI_GROUPS], log=True)
axs[1].yaxis.set_major_formatter(FuncFormatter(lambda x, p: f"{x:,.0f}")); axs[1].set_ylim(6, 8000)
axs[1].set_title(f"By income group (Kruskal-Wallis p={wc.iloc[0]['Kruskal p (income groups, >0)']})", fontsize=9.5); axs[1].tick_params(axis="x", labelsize=7.5)
dist_legend(axs[1], loc="upper right")
fig.suptitle("Reported water cost per day (households paying something)", x=0.0, ha="left", fontweight="bold", fontsize=10.5, y=1.03)
fig_save(fig, WA, "water_cost.png",
         f"No outliers removed (log axis). Cost components differ: Mukono mostly maintenance, Nakaseke more fees/collection (water_cost_components_pct.csv); "
         f"Mukono values like 33/67/167 look like monthly amounts ÷30. The income-group gradient largely mirrors the district difference (Nakaseke dominates <25%). Mann-Whitney district p={wc.iloc[0]['Mann-Whitney p (district, >0)']}. {NOTE_LI}")

for k, v in written.items():
    print(f"{k}: {len(v)} figures -> {', '.join(v)}")
print("done")
