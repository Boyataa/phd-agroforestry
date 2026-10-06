"""moreFigures - gender_education group: redo of Gender.ipynb and education.ipynb on the cleaned data.
Run from repo root:  python scripts/morefigures/gender_education.py
Outputs: paper1/figures/moreFigures/gender_analysis_outputs_standardized/  and  .../education_analysis/
Income = cleaned imputed income (mean of 20 imputations for description; tests run on each imputation, median p reported).
Benchmark = living income benchmark v0.02, household-size specific (ratio_hh).
"""
import sys
from pathlib import Path
import numpy as np, pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "obj1"))
from li_style import *  # noqa: F401,F403
from matplotlib.ticker import FuncFormatter
from matplotlib.patches import Patch

OUT_G = ROOT / "paper1/figures/moreFigures/gender_analysis_outputs_standardized"
OUT_E = ROOT / "paper1/figures/moreFigures/education_analysis"
for o in (OUT_G, OUT_E): o.mkdir(parents=True, exist_ok=True)

h = pd.read_csv(ROOT / "data/derived/Household_Analysis_v1.csv")
sv = pd.read_csv(ROOT / "data/derived/Survey_Cleaned_v1.csv", low_memory=False)
sv = sv[sv.District.str.lower().isin(["mukono", "nakaseke"])]
sv = sv[sv._id.isin(h._id)].set_index("_id").reindex(h._id)
mi = pd.read_csv(ROOT / "data/derived/Survey_Income_MI_v1.csv")
assert len(h) == 597 and sv.index.notna().all()

D = ["mukono", "nakaseke"]
GCOL = {"Male": "#4a3aa7", "Female": "#eda100"}            # SRC slots 7 and 4 (validated palette), not district colours
num = lambda x: pd.to_numeric(x, errors="coerce")
def stars(p): return "" if pd.isna(p) else "***" if p < .001 else "**" if p < .01 else "*" if p < .05 else ""
def pfmt(p): return "n/a" if pd.isna(p) else "p<0.001" if p < .001 else f"p={p:.3f}"

# ---------------- variables
h["head_sex"] = h.female_head.map({0.0: "Male", 1.0: "Female"})
h["resp_sex"] = h.female_respondent.map({0.0: "Male", 1.0: "Female"})
# was a household member explicitly coded as head? (otherwise the build script uses the respondent's gender)
rel_cols = [c for c in sv.columns if "househead_relationship" in c]
h["head_coded"] = sv[rel_cols].astype(str).eq("house_head").any(axis=1).values
SRC_MAP = {"Coffee": ["inc_coffee_mi"], "Other crops": ["inc_othercrops_mi"], "Livestock": ["inc_livestock_mi"],
           "Non-farm work & business": ["inc_offfarm_mi", "inc_trade_mi", "inc_professional_mi"],
           "Remittances & other": ["inc_remittances_mi", "inc_other_mi"], "Home-grown food (in-kind)": ["inkind_food_central"],
           "Tree products used at home": ["tree_inkind"]}
for k, v in SRC_MAP.items(): h[k] = h[v].sum(axis=1)
S = list(SRC_MAP)
EDU_LAB = {0: "No formal", 1: "Primary", 2: "Secondary", 3: "Vocational /\ntertiary", 4: "Vocational /\ntertiary"}
EDU_ORDER = ["No formal", "Primary", "Secondary", "Vocational /\ntertiary"]
h["edu_cat"] = h.resp_edu.map(EDU_LAB)
h["edu4"] = h.resp_edu.clip(upper=3)                       # ordinal 0-3 used for Spearman (vocational + tertiary merged, n=27)
h["marital"] = sv["Marital_Status"].str.strip().str.lower().values
h["tree_plantation_ac"] = num(sv["group_fs0df76/e_Tree_plantations"]).values

# per-imputation frame (for tests)
m = mi.merge(h[["_id", "district", "head_sex", "edu4", "inkind_food_central", "tree_inkind", "bench_hh_year"]], on="_id")
m["gross"] = m.income_total + m.inkind_food_central + m.tree_inkind
m["ratio_hh"] = m.gross / m.bench_hh_year * 100
IMP = [g for _, g in m.groupby("imputation")]

def mw_mi(var, sub=None):
    """Mann-Whitney male- vs female-headed on each imputation; median p."""
    ps = []
    for g in IMP:
        g = g if sub is None else g[g.district == sub]
        a, b = g.loc[g.head_sex == "Male", var].dropna(), g.loc[g.head_sex == "Female", var].dropna()
        ps.append(stats.mannwhitneyu(a, b).pvalue)
    return float(np.median(ps))

def mw(df, var):
    a, b = df.loc[df.head_sex == "Male", var].dropna(), df.loc[df.head_sex == "Female", var].dropna()
    return stats.mannwhitneyu(a, b).pvalue if len(a) and len(b) else np.nan

# =====================================================================================================
# GENDER
# =====================================================================================================
hg = h[h.head_sex.notna()]
NOTE_HEAD = (f"Head gender from the household roster (member coded 'house head'); where no member was coded head "
             f"({(~h.head_coded).sum()} HH) the respondent's gender is used (build_household_analysis.py). ")

# ---- G1 respondent vs head gender
rows = []
for d in D + ["all"]:
    x = h if d == "all" else h[h.district == d]
    for var, lab in [("female_respondent", "Respondent"), ("female_head", "Household head")]:
        s = x[var].dropna()
        rows.append({"district": d, "who": lab, "n_valid": len(s), "n_female": int(s.sum()), "n_male": int(len(s) - s.sum()),
                     "pct_female": round(s.mean() * 100, 1)})
G1 = pd.DataFrame(rows); G1.to_csv(OUT_G / "G1_respondent_and_head_gender.csv", index=False)
ct = pd.crosstab([h.district, h.resp_sex], h.head_sex, margins=True); ct.to_csv(OUT_G / "G1b_respondent_x_head_gender.csv")
fig, ax = plt.subplots(figsize=(6.4, 3.2))
xs = np.arange(3); w = 0.36
for j, lab in enumerate(["Respondent", "Household head"]):
    t = G1[G1.who == lab].set_index("district").loc[D + ["all"]]
    b = ax.bar(xs + (j - 0.5) * w, t.pct_female, w, color=[ORD4[1], ORD4[3]][j], label=f"{lab} is female")
    for xi, (p, n) in zip(xs + (j - 0.5) * w, zip(t.pct_female, t.n_valid)):
        ax.text(xi, p + 1.2, f"{p:.0f}%\n(n={n})", ha="center", va="bottom", fontsize=7.5, color=INK2)
ax.set_xticks(xs, ["Mukono", "Nakaseke", "Both districts"]); ax.set_ylim(0, 80); ax.set_ylabel("% female")
ax.axhline(50, color=INK2, lw=0.8, ls=":"); ax.grid(axis="x", visible=False); ax.legend(loc="upper left", ncol=2)
ax.set_title("Share of respondents and household heads who are female, by district")
save(fig, OUT_G / "G1_respondent_and_head_gender.png",
     f"n = 597 HH (595 with respondent gender, 596 with head gender). {NOTE_HEAD}"
     f"Respondent and head gender agree in {(h.resp_sex == h.head_sex).sum()} of {h[['resp_sex','head_sex']].dropna().shape[0]} HH.")

# ---- G2 income by head gender (cash, coffee cash, cash + in-kind)
VARS2 = [("income_total_mi", "income_total", "Cash income (all sources)"), ("inc_coffee_mi", "inc_coffee", "Coffee sales (cash)"),
         ("gross", "gross", "Cash + home-grown food + tree products used at home")]
rows = []
fig, axs = plt.subplots(1, 3, figsize=(10, 3.8), sharey=True)
for ax, (v, vm, lab) in zip(axs, VARS2):
    for i, d in enumerate(D):
        for j, sx in enumerate(["Male", "Female"]):
            s = hg[(hg.district == d) & (hg.head_sex == sx)][v]
            pos = i + (j - 0.5) * 0.38
            sp = s.clip(lower=1e4)                       # log axis: zero coffee income shown at 10k
            ax.boxplot(sp, positions=[pos], widths=0.32, patch_artist=True, showfliers=True,
                       boxprops=dict(facecolor=GCOL[sx], alpha=0.85, edgecolor=INK2), medianprops=dict(color="white", lw=1.6),
                       whiskerprops=dict(color=INK2), capprops=dict(color=INK2),
                       flierprops=dict(marker="o", ms=2, mfc=GCOL[sx], mec="none", alpha=0.5))
            ax.text(pos, 6e7 * 1.15, money(s.median()), ha="center", fontsize=7, color=INK2)
            rows.append({"variable": lab, "district": d, "head": sx, "n": len(s), "median": round(s.median()), "mean": round(s.mean()),
                         "q25": round(s.quantile(.25)), "q75": round(s.quantile(.75)), "pct_zero": round((s == 0).mean() * 100, 1)})
        p = mw_mi(vm, d); rows[-1]["MW_p_median_over_20_imputations"] = rows[-2]["MW_p_median_over_20_imputations"] = round(p, 4)
        ax.text(i, 1.15e4, pfmt(p), ha="center", fontsize=7, color=INK, bbox=dict(fc=SURF, ec="none", pad=1))
    ax.set_yscale("log"); ax.set_ylim(8e3, 1.2e8); ax.yaxis.set_major_formatter(FuncFormatter(money))
    ax.set_xticks([0, 1], ["Mukono", "Nakaseke"]); ax.set_title(lab, fontsize=9); ax.grid(axis="x", visible=False)
axs[0].set_ylabel("UGX per year (log scale)")
axs[0].legend(handles=[Patch(color=GCOL[k], label=f"{k}-headed") for k in GCOL], loc="lower left", bbox_to_anchor=(0, 0.06))
fig.suptitle("Annual household income by gender of household head and district", x=0.01, ha="left", fontweight="bold", fontsize=10.5)
fig.tight_layout()
G2 = pd.DataFrame(rows); G2.to_csv(OUT_G / "G2_income_by_head_gender.csv", index=False)
nn = hg.groupby(["district", "head_sex"]).size()
save(fig, OUT_G / "G2_income_by_head_gender.png",
     "Boxes = IQR, white line = median (value above each box), points beyond 1.5 IQR shown. Cleaned imputed income (mean of 20 imputations); "
     "zero coffee income plotted at 10k. Mann-Whitney male vs female head within district, median p over the 20 imputations. "
     f"n: Mukono {nn['mukono','Male']} male / {nn['mukono','Female']} female-headed; Nakaseke {nn['nakaseke','Male']} / {nn['nakaseke','Female']}. "
     + NOTE_HEAD)

# ---- G3 living income ratio by head gender
rows = []; fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 3.9), gridspec_kw=dict(width_ratios=[1, 1.25]))
for i, d in enumerate(D + ["all"]):
    x = hg if d == "all" else hg[hg.district == d]
    for j, sx in enumerate(["Male", "Female"]):
        s = x[x.head_sex == sx].ratio_hh; pos = i + (j - 0.5) * 0.38
        a1.boxplot(s, positions=[pos], widths=0.32, patch_artist=True, boxprops=dict(facecolor=GCOL[sx], alpha=0.85, edgecolor=INK2),
                   medianprops=dict(color="white", lw=1.6), whiskerprops=dict(color=INK2), capprops=dict(color=INK2),
                   flierprops=dict(marker="o", ms=2, mfc=GCOL[sx], mec="none", alpha=0.5))
        a1.text(pos, 3.3e2 * 1.1, f"{s.median():.0f}%", ha="center", fontsize=7, color=INK2)
        grp = x[x.head_sex == sx].li_group.value_counts(normalize=True).reindex(LI_GROUPS).fillna(0) * 100
        rows.append({"district": d, "head": sx, "n": len(s), "median_ratio_hh_%": round(s.median(), 1), "mean_ratio_hh_%": round(s.mean(), 1),
                     "pct_reach_50": round((s >= 50).mean() * 100, 1), "pct_reach_100": round((s >= 100).mean() * 100, 1),
                     **{f"pct_{g}": round(grp[g], 1) for g in LI_GROUPS}})
    p = mw_mi("ratio_hh", None if d == "all" else d)
    chi = stats.chi2_contingency(pd.crosstab(x.head_sex, x.li_group))[1]
    rows[-1].update(MW_p_ratio=round(p, 4), chi2_p_li_group=round(chi, 4)); rows[-2].update(MW_p_ratio=round(p, 4), chi2_p_li_group=round(chi, 4))
    a1.text(i, 2.3, pfmt(p), ha="center", fontsize=7, color=INK, bbox=dict(fc=SURF, ec="none", pad=1))
a1.set_yscale("log"); a1.set_ylim(1.8, 450); a1.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}%"))
a1.axhline(100, color=INK2, lw=0.8, ls="--"); a1.text(2.55, 100, "living\nincome", fontsize=7, color=INK2, va="center")
a1.set_xticks([0, 1, 2], ["Mukono", "Nakaseke", "Both"]); a1.grid(axis="x", visible=False)
a1.set_ylabel("% of household benchmark (log scale)"); a1.set_title("a  Income as % of living income benchmark", fontsize=9)
a1.legend(handles=[Patch(color=GCOL[k], label=f"{k}-headed") for k in GCOL], loc="lower left", bbox_to_anchor=(0, 0.07))
G3 = pd.DataFrame(rows); G3.to_csv(OUT_G / "G3_living_income_ratio_by_head_gender.csv", index=False)
labs = []; y = np.arange(6)[::-1]
for yi, r in zip(y, G3.itertuples()):
    left = 0
    for k, g in enumerate(LI_GROUPS):
        v = G3.loc[r.Index, f"pct_{g}"]
        a2.barh(yi, v, left=left, color=ORD4[k], height=0.62, edgecolor=SURF, lw=1.2, label=g if yi == y[0] else None)
        if v >= 6: a2.text(left + v / 2, yi, f"{v:.0f}", ha="center", va="center", fontsize=7.5, color="white" if k else INK)
        left += v
    labs.append(f"{ {'mukono':'Mukono','nakaseke':'Nakaseke','all':'Both'}[r.district]}, {r.head.lower()} head (n={r.n})")
for yi, d in zip([y[1], y[3], y[5]], D + ["all"]):
    a2.text(101, yi + 0.5, "chi² " + pfmt(G3[G3.district == d].chi2_p_li_group.iloc[0]), fontsize=7, color=INK, va="center")
a2.set_yticks(y, labs); a2.set_xlim(0, 100); a2.grid(axis="y", visible=False); a2.set_xlabel("% of households")
a2.axhline(y[1] - 0.5, color=GRID, lw=1); a2.axhline(y[3] - 0.5, color=GRID, lw=1)
a2.legend(title="Income as % of HH benchmark", ncol=4, loc="upper left", bbox_to_anchor=(0, -0.13), fontsize=7.5, title_fontsize=7.5)
a2.set_title("b  Households by living income group", fontsize=9)
fig.suptitle("Living income ratio by gender of household head", x=0.01, ha="left", fontweight="bold", fontsize=10.5)
fig.tight_layout()
save(fig, OUT_G / "G3_living_income_ratio_by_head_gender.png",
     "Income = cash (cleaned, imputed) + home-grown food + tree products used at home, as % of the household-size living income benchmark v0.02 "
     "(Mukono 20.17M / Nakaseke 19.78M UGX/yr for 2 adults + 3 children). a: Mann-Whitney, median p over 20 imputations. "
     "b: chi-square of head gender x LI group. n = 596 HH with head gender. " + NOTE_HEAD)

# ---- G4 income composition by head gender
rows = []; fig, ax = plt.subplots(figsize=(7.4, 3.3)); y = np.arange(4)[::-1]; labs = []
for yi, (d, sx) in zip(y, [(d, s) for d in D for s in ["Male", "Female"]]):
    g = hg[(hg.district == d) & (hg.head_sex == sx)]; mm = g[S].mean(); sh = mm / mm.sum() * 100; left = 0
    for j, s in enumerate(S):
        ax.barh(yi, sh[s], left=left, color=SRC[j], height=0.62, edgecolor=SURF, lw=1.5, label=s if yi == y[0] else None)
        if sh[s] >= 6: ax.text(left + sh[s] / 2, yi, f"{sh[s]:.0f}", ha="center", va="center", fontsize=7.5, color="white" if j in (0, 5, 6) else INK)
        left += sh[s]
    ax.text(101, yi, f"mean {money(mm.sum())}", va="center", fontsize=7.5, color=INK2)
    labs.append(f"{DIST_LABEL[d]}, {sx.lower()}-headed (n={len(g)})")
    rows += [{"district": d, "head": sx, "n": len(g), "source": s, "mean_UGX": round(mm[s]), "share_%": round(sh[s], 1)} for s in S]
pd.DataFrame(rows).to_csv(OUT_G / "G4_income_composition_by_head_gender.csv", index=False)
ax.set_yticks(y, labs); ax.set_xlim(0, 100); ax.grid(axis="y", visible=False); ax.axhline(1.5, color=GRID, lw=1)
ax.set_xlabel("% of mean household income (cash + in-kind)")
ax.legend(ncol=4, loc="lower left", bbox_to_anchor=(0, 1.0), fontsize=7.5)
ax.set_title("Income composition by gender of household head and district", pad=36)
save(fig, OUT_G / "G4_income_composition_by_head_gender.png",
     "Shares of the group mean (UGX/yr). Cash by source = cleaned imputed Q162 (mean of 20 imputations); 'Other crops' = Q162e sale of other crops "
     "(not tree income); tree products used at home valued from Q168-170. n = 596 HH. " + NOTE_HEAD)

# ---- G5 farm resources by head gender
VARS5 = [("land_owned_ac", "Land owned (acres)"), ("coffee_ac", "Coffee area (acres)"),
         ("trees_on_farm", "Trees on farm (count)"), ("n_income_sources", "Cash income sources (number)")]
rows = []; fig, axs = plt.subplots(1, 4, figsize=(10.5, 3.2))
for ax, (v, lab) in zip(axs, VARS5):
    for i, d in enumerate(D):
        x = hg[hg.district == d]
        for j, sx in enumerate(["Male", "Female"]):
            s = x[x.head_sex == sx][v].dropna(); pos = i + (j - 0.5) * 0.34
            q1, q2, q3 = s.quantile([.25, .5, .75])
            ax.plot([pos, pos], [q1, q3], color=GCOL[sx], lw=2.4, solid_capstyle="butt")
            ax.plot(pos, q2, "o", color=GCOL[sx], ms=6, mec=SURF)
            ax.text(pos + 0.05, q2, f"{q2:g}", fontsize=7, color=INK2, va="center")
            rows.append({"variable": lab, "district": d, "head": sx, "n": len(s), "median": q2, "q25": q1, "q75": q3, "mean": round(s.mean(), 2)})
        p = mw(x, v); rows[-1]["MW_p"] = rows[-2]["MW_p"] = round(p, 4)
        ax.text(i, 1.02, pfmt(p), transform=ax.get_xaxis_transform(), ha="center", fontsize=7, color=INK)
    ax.set_xticks([0, 1], ["Mukono", "Nakaseke"]); ax.set_xlim(-0.6, 1.6); ax.set_ylim(bottom=0); ax.grid(axis="x", visible=False)
    ax.set_title(lab, fontsize=9, pad=14)
axs[0].legend(handles=[Patch(color=GCOL[k], label=f"{k}-headed") for k in GCOL], loc="upper left", fontsize=7)
fig.suptitle("Farm resources and income diversification by gender of household head (median and IQR)", x=0.01, ha="left", fontweight="bold", fontsize=10.5, y=1.04)
fig.tight_layout()
G5 = pd.DataFrame(rows); G5.to_csv(OUT_G / "G5_farm_resources_by_head_gender.csv", index=False)
ntr = hg.groupby("district").trees_on_farm.count()
save(fig, OUT_G / "G5_farm_resources_by_head_gender.png",
     f"Dot = median, bar = IQR; Mann-Whitney male vs female head within district. Valid n per variable in the CSV "
     f"(trees: Mukono {ntr['mukono']}, Nakaseke {ntr['nakaseke']}; one Nakaseke enumerator's tree counts excluded as unreliable). " + NOTE_HEAD)

# ---- G6 respondent education and marital status by respondent gender
hr = h[h.resp_sex.notna()]
MAR = ["married", "single", "divorced", "other"]
rows = []; fig, axs = plt.subplots(1, 2, figsize=(10, 3.2), sharey=True)
y = np.arange(4)[::-1]; labs = []
for ax, (v, cats, lab) in zip(axs, [("edu_cat", EDU_ORDER, "a  Respondent education"), ("marital", MAR, "b  Respondent marital status")]):
    for yi, (d, sx) in zip(y, [(d, s) for d in D for s in ["Male", "Female"]]):
        g = hr[(hr.district == d) & (hr.resp_sex == sx)][v].dropna()
        sh = g.value_counts(normalize=True).reindex(cats).fillna(0) * 100; left = 0
        for k, c in enumerate(cats):
            col = ORD4[k] if v == "edu_cat" else SRC[k]
            ax.barh(yi, sh[c], left=left, color=col, height=0.62, edgecolor=SURF, lw=1.2, label=c.replace("\n", " ") if yi == y[0] else None)
            if sh[c] >= 6: ax.text(left + sh[c] / 2, yi, f"{sh[c]:.0f}", ha="center", va="center", fontsize=7.5,
                                   color="white" if (v == "edu_cat" and k) or (v == "marital" and k in (0,)) else INK)
            left += sh[c]
        rows.append({"variable": v, "district": d, "respondent": sx, "n": len(g), **{c.replace("\n", " "): round(sh[c], 1) for c in cats}})
        if v == "edu_cat": labs.append(f"{DIST_LABEL[d]}, {sx.lower()} (n={len(g)})")
    for i, d in enumerate(D):
        x = hr[hr.district == d]; p = stats.chi2_contingency(pd.crosstab(x.resp_sex, x[v]))[1]
        ax.text(101, y[2 * i] - 0.5, "chi² " + pfmt(p), fontsize=7, rotation=90, va="center")
        for r in rows[-4:]:
            if r["district"] == d: r["chi2_p"] = round(p, 4)
    ax.set_xlim(0, 100); ax.grid(axis="y", visible=False); ax.axhline(1.5, color=GRID, lw=1); ax.set_xlabel("% of respondents")
    ax.set_title(lab, fontsize=9); ax.legend(ncol=4, loc="upper left", bbox_to_anchor=(0, -0.2), fontsize=7.5)
axs[0].set_yticks(y, labs)
fig.suptitle("Education and marital status of respondents by respondent gender and district", x=0.01, ha="left", fontweight="bold", fontsize=10.5)
fig.tight_layout()
pd.DataFrame(rows).to_csv(OUT_G / "G6_respondent_education_marital_by_gender.csv", index=False)
save(fig, OUT_G / "G6_respondent_education_marital_by_gender.png",
     "Respondent attributes, so grouped by respondent gender (not head gender). Shares of respondents with a valid answer (n in labels; 595 with gender). "
     "Vocational and college/university merged (n = 27). 'Other' marital status as recorded (the questionnaire offered married / single / divorced / other; widowed not separated). Chi-square of gender x category within district.")

# =====================================================================================================
# EDUCATION
# =====================================================================================================
EV = [("Coffee sales", "inc_coffee_mi", "inc_coffee"), ("Sale of other crops (Q162e)", "inc_othercrops_mi", "inc_othercrops"),
      ("Livestock", "inc_livestock_mi", "inc_livestock"), ("Off-farm employment", "inc_offfarm_mi", "inc_offfarm"),
      ("Trade", "inc_trade_mi", "inc_trade"), ("Professional job", "inc_professional_mi", "inc_professional"),
      ("Remittances", "inc_remittances_mi", "inc_remittances"), ("Other cash income", "inc_other_mi", "inc_other"),
      ("Total cash income", "income_total_mi", "income_total"), ("Home-grown food (in-kind)", "inkind_food_central", None),
      ("Income incl. in-kind", "gross", "gross"), ("Income incl. in-kind, % of HH benchmark", "ratio_hh", "ratio_hh"),
      ("Net income (net v1)", "net_central", None), ("Number of cash income sources", "n_income_sources", None),
      ("Land owned (acres)", "land_owned_ac", None), ("Coffee area (acres)", "coffee_ac", None),
      ("Other crops area (acres)", "other_crops_ac", None), ("Tree plantation area (acres)", "tree_plantation_ac", None),
      ("Trees on farm (count)", "trees_on_farm", None), ("Coffee yield (kg FAQ/acre)", "coffee_yield_faq_ac", None),
      ("Farming experience (years)", "farming_years", None), ("Household size", "hh_size", None)]
rows = []
for lab, v, vm in EV:
    for d in D + ["all"]:
        x = h if d == "all" else h[h.district == d]
        sub = x[["edu4", v]].dropna(); r, p = stats.spearmanr(sub.edu4, sub[v])
        rec = {"variable": lab, "district": d, "n": len(sub), "rho": round(r, 3), "p": round(p, 4)}
        if vm:   # imputed income: test on each imputation
            rr = [];pp = []
            for g in IMP:
                g = g if d == "all" else g[g.district == d]; g = g.dropna(subset=["edu4"])
                a, b = stats.spearmanr(g.edu4, g[vm]); rr.append(a); pp.append(b)
            rec.update(rho=round(float(np.mean(rr)), 3), p=round(float(np.median(pp)), 4), note="mean rho / median p over 20 imputations")
        rows.append(rec)
E1 = pd.DataFrame(rows); E1.to_csv(OUT_E / "E1_education_spearman.csv", index=False)
R = E1.pivot(index="variable", columns="district", values="rho").loc[[e[0] for e in EV], D + ["all"]]
P = E1.pivot(index="variable", columns="district", values="p").loc[R.index, R.columns]
Nn = E1.pivot(index="variable", columns="district", values="n").loc[R.index, R.columns]
fig, ax = plt.subplots(figsize=(6.2, 7.4))
from matplotlib.colors import LinearSegmentedColormap
cmap = LinearSegmentedColormap.from_list("div", ["#eb6834", "#f6c9b3", SURF, "#b5d1f3", "#1c5cab"])
im = ax.imshow(R.values, cmap=cmap, vmin=-0.4, vmax=0.4, aspect="auto")
for i in range(R.shape[0]):
    for j in range(R.shape[1]):
        ax.text(j, i, f"{R.values[i, j]:+.2f}{stars(P.values[i, j])}", ha="center", va="center", fontsize=7.5,
                color="white" if abs(R.values[i, j]) > 0.3 else INK)
ax.set_xticks(range(3), [f"Mukono\n(n≤{int(Nn['mukono'].max())})", f"Nakaseke\n(n≤{int(Nn['nakaseke'].max())})", f"Both\n(n≤{int(Nn['all'].max())})"])
ax.set_yticks(range(R.shape[0]), R.index); ax.grid(False); ax.xaxis.tick_top()
for s in [8.5, 12.5, 13.5]: ax.axhline(s, color=INK2, lw=0.6)
cb = fig.colorbar(im, ax=ax, fraction=0.04, pad=0.03); cb.set_label("Spearman rho with respondent education level")
ax.set_title("Spearman correlation of respondent education level with income and farm variables", fontsize=9.5, pad=34)
save(fig, OUT_E / "E1_education_spearman_heatmap.png",
     "Education coded 0 no formal, 1 primary, 2 secondary, 3 vocational/college/university. Cash income = cleaned imputed income "
     "(mean rho, median p over 20 imputations). * p<0.05, ** p<0.01, *** p<0.001. Pairwise n in E1_education_spearman.csv "
     "(trees: one Nakaseke enumerator's counts excluded; yield >5000 kg/acre excluded). Associations only.")

# ---- E2 income and LI ratio by education level
rows = []; fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 3.9))
xs = np.arange(len(EDU_ORDER))
for i, d in enumerate(D):
    x = h[h.district == d]; off = (i - 0.5) * 0.3
    for k, e in enumerate(EDU_ORDER):
        g = x[x.edu_cat == e]
        rows.append({"district": d, "education": e.replace("\n", " "), "n": len(g), "median_cash": round(g.income_total_mi.median()),
                     "median_incl_inkind": round(g.gross.median()), "median_ratio_hh_%": round(g.ratio_hh.median(), 1),
                     "pct_reach_50": round((g.ratio_hh >= 50).mean() * 100, 1)})
        a1.plot(xs[k] + off, g.income_total_mi.median(), "o", mfc=SURF, mec=DIST[d], mew=1.6, ms=6)
        a1.plot(xs[k] + off, g.gross.median(), "o", color=DIST[d], ms=6)
        a1.plot([xs[k] + off] * 2, [g.income_total_mi.median(), g.gross.median()], color=DIST[d], lw=1, alpha=0.6)
        a2.boxplot(g.ratio_hh, positions=[xs[k] + off], widths=0.26, patch_artist=True,
                   boxprops=dict(facecolor=DIST[d], alpha=0.85, edgecolor=INK2), medianprops=dict(color="white", lw=1.6),
                   whiskerprops=dict(color=INK2), capprops=dict(color=INK2), flierprops=dict(marker="o", ms=2, mfc=DIST[d], mec="none", alpha=0.5))
    ps = [stats.kruskal(*g[g.district == d].dropna(subset=["edu4"]).groupby("edu4").income_total.apply(list).values).pvalue for g in IMP]
    pk_cash = float(np.median(ps))
    ps = [stats.kruskal(*g[g.district == d].dropna(subset=["edu4"]).groupby("edu4").ratio_hh.apply(list).values).pvalue for g in IMP]
    pk_ratio = float(np.median(ps))
    for r in rows[-4:]: r.update(KW_p_cash=round(pk_cash, 4), KW_p_ratio=round(pk_ratio, 4))
    a2.text(0.02, 0.97 - i * 0.07, f"{DIST_LABEL[d]}: Kruskal-Wallis {pfmt(pk_ratio)}", transform=a2.transAxes, fontsize=7.5, color=DIST[d], va="top")
    a1.text(0.02, 0.80 - i * 0.07, f"{DIST_LABEL[d]}: Kruskal-Wallis (cash) {pfmt(pk_cash)}", transform=a1.transAxes, fontsize=7.5, color=DIST[d], va="top")
a1.set_xticks(xs, EDU_ORDER); a1.yaxis.set_major_formatter(FuncFormatter(money)); a1.set_ylim(0, 11e6); a1.grid(axis="x", visible=False)
a1.set_ylabel("Median UGX per year"); a1.set_xlabel("Respondent education"); a1.set_title("a  Median household income", fontsize=9)
from matplotlib.lines import Line2D
a1.legend(handles=[Line2D([], [], marker="o", ls="", mfc=SURF, mec=INK2, label="Cash income"),
                   Line2D([], [], marker="o", ls="", color=INK2, label="Cash + in-kind (food, tree products)")] +
          [Patch(color=DIST[d], label=DIST_LABEL[d]) for d in D], loc="upper right", ncol=2, fontsize=7.5)
a2.set_yscale("log"); a2.set_ylim(1.5, 450); a2.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}%"))
a2.axhline(100, color=INK2, lw=0.8, ls="--")
NE = h.groupby(["edu_cat", "district"]).size()
a2.set_xticks(xs, [f"{e}\nn={NE[e, 'mukono']} / {NE[e, 'nakaseke']}" for e in EDU_ORDER]); a2.grid(axis="x", visible=False)
a2.set_ylabel("% of household benchmark (log scale)"); a2.set_xlabel("Respondent education (n Mukono / Nakaseke)")
a2.set_title("b  Income as % of living income benchmark", fontsize=9)
fig.suptitle("Household income and living income ratio by respondent education level and district", x=0.01, ha="left", fontweight="bold", fontsize=10.5)
fig.tight_layout()
pd.DataFrame(rows).to_csv(OUT_E / "E2_income_by_education.csv", index=False)
save(fig, OUT_E / "E2_income_by_education.png",
     "n = 596 HH with respondent education (Mukono 296, Nakaseke 300). Benchmark = household-size living income benchmark v0.02. "
     "Vocational and college/university merged (n = 27). Kruskal-Wallis across education levels within district, median p over 20 imputations. "
     "Dashed line = 100% (living income reached).")
print("done:", sorted(p.name for p in OUT_G.glob("*.png")), sorted(p.name for p in OUT_E.glob("*.png")))
