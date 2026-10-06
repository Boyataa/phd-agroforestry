"""moreFigures group `farm_trees`: re-run of the old Objective 1 land / tree analyses on the cleaned data.
Old notebooks: 'Farm Dynamics.ipynb' (farm_analysis, land_vs_coffee, land_use_structure, tree_analysis, tree_dynamics),
'Nakaseke.ipynb' (tree_origin), 'Tree Income vs Cofffee.ipynb' (tree_products); tree_species = old Objective 2
'top_species' (tree_spiecies.ipynb), redone here from data/raw/cleaned shamba Survey.csv.
Run from repo root:  python scripts/morefigures/farm_trees.py
Writes PNG (300 dpi) + CSV per figure to paper1/figures/moreFigures/<folder>/ (NOTES.md files are written by hand).
"""
import sys, warnings
from pathlib import Path
import numpy as np, pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/obj1"))
from li_style import *  # noqa: E402,F401
from matplotlib.ticker import FuncFormatter  # noqa: E402
warnings.filterwarnings("ignore")

OUT = ROOT / "paper1/figures/moreFigures"
num = lambda x: pd.to_numeric(x, errors="coerce")
D = ["mukono", "nakaseke"]
GREY = "#b9b8b3"


import textwrap
from matplotlib.colors import to_rgb


def save(fig, path, note=None):     # li_style.save, but the note is placed below everything already drawn (legends/xlabels below axes)
    if note:
        fig.canvas.draw(); bb = fig.get_tightbbox(fig.canvas.get_renderer())
        width = int(fig.get_figwidth() * 15)
        fig.text(bb.x0 / fig.get_figwidth(), (bb.y0 - 0.08) / fig.get_figheight(), "\n".join(textwrap.wrap(note, width)),
                 fontsize=7.5, color=INK2, ha="left", va="top")
    fig.savefig(path); plt.close(fig)


def txtcol(c):
    r, g, b = to_rgb(c); return "white" if 0.299 * r + 0.587 * g + 0.114 * b < 0.55 else INK


def odir(name):
    p = OUT / name; p.mkdir(parents=True, exist_ok=True); return p


def pfmt(p):
    return "n/a" if pd.isna(p) else ("p < 0.001" if p < 0.001 else f"p = {p:.3f}")


def p_dist(s, by):          # Mann-Whitney between districts
    g = [s[by == d].dropna() for d in D]
    return stats.mannwhitneyu(*g).pvalue if all(len(x) > 1 for x in g) else np.nan


def p_li(s, by):            # Kruskal across LI groups
    g = [s[by == k].dropna() for k in LI_GROUPS]; g = [x for x in g if len(x) > 1]
    return stats.kruskal(*g).pvalue if len(g) > 1 else np.nan


def p_chi(a, b):
    t = pd.crosstab(a, b)
    return stats.chi2_contingency(t)[1] if t.shape[0] > 1 and t.shape[1] > 1 else np.nan


def summ(s):
    s = s.dropna()
    return pd.Series({"n": len(s), "median": s.median(), "q25": s.quantile(.25), "q75": s.quantile(.75), "mean": s.mean()})


def rows_label():
    return [DIST_LABEL[d] for d in D] + [f"LI {g}" for g in LI_GROUPS]


def stacked_rows(ax, tab, colors, title, xlabel="% of households"):
    """tab: rows = groups (plotted top->bottom), columns = categories, values in %."""
    y = np.arange(len(tab))[::-1]
    left = np.zeros(len(tab))
    for j, c in enumerate(tab.columns):
        v = tab[c].values
        ax.barh(y, v, left=left, color=colors[j], label=c, height=0.62, edgecolor=SURF, linewidth=0.6)
        for yi, l, w in zip(y, left, v):
            if w >= 7:
                ax.text(l + w / 2, yi, f"{w:.0f}", ha="center", va="center", fontsize=7.5, color=txtcol(colors[j]))
        left += v
    ax.set_yticks(y, tab.index); ax.set_xlim(0, 100); ax.set_xlabel(xlabel); ax.grid(axis="y", visible=False)
    ax.set_title(title)


# ------------------------------------------------------------------ data
h = pd.read_csv(ROOT / "data/derived/Household_Analysis_v1.csv")
sv = pd.read_csv(ROOT / "data/derived/Survey_Cleaned_v1.csv", low_memory=False)
sv = sv[sv.District.isin(D)]
h["li_group"] = pd.Categorical(h.li_group, LI_GROUPS, ordered=True)
s = sv.merge(h[["_id", "district", "li_group", "land_owned_ac", "coffee_ac", "trees_on_farm", "trees_per_acre", "income_total_mi", "gross",
               "trees_planted_any", "removed_trees", "trees_count_unreliable", "enumerator"]], on="_id", how="inner")
assert len(s) == 597
N = s.district.value_counts()
grp_row = lambda df: pd.concat([df.assign(row=df.district.map(DIST_LABEL)), df.assign(row="LI " + df.li_group.astype(str))], ignore_index=True)


# ================================================================== farm_analysis
o = odir("farm_analysis")
# F1 land owned by district and by LI group
L = s[["district", "li_group", "land_owned_ac"]].copy()
t = pd.concat({**{DIST_LABEL[d]: summ(L.land_owned_ac[L.district == d]) for d in D},
               **{f"{DIST_LABEL[d]} | LI {g}": summ(L.land_owned_ac[(L.district == d) & (L.li_group == g)]) for d in D for g in LI_GROUPS},
               "All": summ(L.land_owned_ac)}, axis=1).T.round(2)
pd_ = p_dist(L.land_owned_ac, L.district); pl = {d: p_li(L.land_owned_ac[L.district == d], L.li_group[L.district == d]) for d in D}
t["test"] = ""; t.loc["Mukono", "test"] = f"Mann-Whitney districts {pfmt(pd_)}"
for d in D: t.loc[f"{DIST_LABEL[d]} | LI <25%", "test"] = f"Kruskal LI groups {pfmt(pl[d])}"
t.to_csv(o / "land_owned_by_district_li_group.csv")
fig, ax = plt.subplots(1, 2, figsize=(9, 3.6), gridspec_kw={"width_ratios": [1, 1.6]})
for i, d in enumerate(D):
    v = L.land_owned_ac[L.district == d].dropna(); rng = np.random.default_rng(i)
    ax[0].scatter(i + rng.uniform(-.18, .18, len(v)), v, s=7, alpha=.35, color=DIST[d], linewidths=0)
    ax[0].boxplot(v, positions=[i], widths=.5, showfliers=False, medianprops=dict(color=INK, lw=1.6), boxprops=dict(color=INK2),
                  whiskerprops=dict(color=INK2), capprops=dict(color=INK2))
    ax[0].text(i, v.max() * 1.25, f"median {v.median():.1f}\nn = {len(v)}", ha="center", fontsize=7.5, color=INK2)
ax[0].set_yscale("log"); ax[0].set_xticks([0, 1], [DIST_LABEL[d] for d in D]); ax[0].set_ylabel("Land owned (acres, log scale)")
ax[0].set_ylim(0.15, 40); ax[0].yaxis.set_major_formatter(FuncFormatter(lambda x, p: f"{x:g}")); ax[0].grid(axis="x", visible=False)
ax[0].set_title("Land owned per household")
w = .38; x = np.arange(4)
for i, d in enumerate(D):
    m = L[L.district == d].groupby("li_group", observed=False).land_owned_ac.median()
    ax[1].bar(x + (i - .5) * w, m.values, w, color=DIST[d], label=f"{DIST_LABEL[d]} (Kruskal {pfmt(pl[d])})")
    for xi, v in zip(x + (i - .5) * w, m.values):
        if pd.notna(v): ax[1].text(xi, v + .05, f"{v:.1f}", ha="center", va="bottom", fontsize=7.5)
ax[1].set_xticks(x, [f"{g}\n(n={(L.li_group == g).sum()})" for g in LI_GROUPS]); ax[1].set_xlabel("Gross income as % of household living income benchmark")
ax[1].set_ylabel("Median land owned (acres)"); ax[1].legend(loc="upper left"); ax[1].set_title("Median land owned by living income group")
save(fig, o / "land_owned_by_district_li_group.png",
     f"Land owned = Q 'total land he/she owns'; values > 500 acres set to missing (one record of 120,000). n = {L.land_owned_ac.notna().sum()} of 597. "
     f"Districts: Mann-Whitney {pfmt(pd_)}. No 95th-percentile trimming (old version dropped the top 5%).")

# F2 tenure
ten = s["If_yes_what_is_the_form_of_landownership"].map({"mailo_kibanja": "Mailo / kibanja", "freehold_full_ownership": "Freehold",
                                                         "customary_divided_inheritance": "Customary / inherited"})
own = s["Does_the_respondent_own_the_land?"]
s["tenure"] = ten.where(~own.eq("No"), "Does not own land")
TCAT = ["Mailo / kibanja", "Freehold", "Customary / inherited", "Does not own land"]
G = grp_row(s[["district", "li_group", "tenure"]].dropna(subset=["tenure"]))
cnt = pd.crosstab(G.row, G.tenure).reindex(index=rows_label(), columns=TCAT, fill_value=0)
pct = cnt.div(cnt.sum(1), axis=0) * 100
p1 = p_chi(s.district, s.tenure); p2 = p_chi(s.li_group, s.tenure)
out = pd.concat([cnt.add_suffix(" (n)"), pct.round(1).add_suffix(" (%)")], axis=1); out["n valid"] = cnt.sum(1)
out["chi-square p"] = ""; out.loc["Mukono", "chi-square p"] = f"districts {pfmt(p1)}"; out.loc["LI <25%", "chi-square p"] = f"LI groups {pfmt(p2)}"
out.to_csv(o / "land_tenure_by_district_li_group.csv")
fig, ax = plt.subplots(figsize=(7.4, 3.4))
stacked_rows(ax, pct.set_axis([f"{r} (n={n})" for r, n in zip(pct.index, cnt.sum(1))]), [SRC[0], SRC[2], SRC[3], GREY],
             "Form of land ownership, by district and living income group")
ax.legend(ncol=4, loc="upper center", bbox_to_anchor=(0.45, -0.18)); ax.axhline(3.5, color=INK2, lw=.6)
save(fig, o / "land_tenure_by_district_li_group.png",
     f"% of households with a valid answer ({int(cnt.iloc[:2].sum().sum())} of 597). 'Does not own land' = answered No to ownership "
     f"(all in Nakaseke). Chi-square: districts {pfmt(p1)}; LI groups {pfmt(p2)}. LI group = gross income (cash + home-grown food) as % of the household-size benchmark (v0.02).")

# ================================================================== land_use_structure
o = odir("land_use_structure")
LU = {"Robusta coffee": "Size_used_for_Robusta_coffee", "Other crops": "size_used_for_Other_crops",
      "Livestock grazing": "group_fs0df76/b_Livestock_grazing_area", "Tree plantations": "group_fs0df76/e_Tree_plantations",
      "Rented out": "group_fs0df76/c_Land_under_rent_ut_to_other_at_a_fee", "Other activities": "land_use_for_Other_activities"}
A = pd.DataFrame({k: num(s[c].replace("O", "0")) for k, c in LU.items()})   # 8 'O' (letter) entries read as 0
A["district"] = s.district.values; A["li_group"] = s.li_group.values; A["owned"] = s.land_owned_ac.values
uses = list(LU)
used = A[uses].sum(axis=1, min_count=1)
den = np.fmax(A.owned, used)                     # if listed uses exceed land owned (31 HH), shares are of the listed total
ok = A.owned.notna() & used.notna()
S = A.loc[ok, uses].fillna(0).div(den[ok], axis=0) * 100
S["Not allocated (homestead, fallow, unrecorded)"] = (100 - S[uses].sum(1)).clip(lower=0)
S["district"] = A.district[ok]; S["li_group"] = A.li_group[ok]
G = grp_row(S); cats = uses + ["Not allocated (homestead, fallow, unrecorded)"]
comp = G.groupby("row")[cats].mean().reindex(rows_label()); ncomp = G.groupby("row").size().reindex(rows_label())
comp.round(1).assign(n=ncomp).to_csv(o / "land_use_composition.csv")
fig, ax = plt.subplots(figsize=(8, 3.6))
stacked_rows(ax, comp.set_axis([f"{r} (n={n})" for r, n in zip(comp.index, ncomp)]), SRC[:6] + [GREY],
             "Average share of each farm's land by use, by district and living income group", "Mean share of household land (%)")
ax.legend(ncol=4, loc="upper center", bbox_to_anchor=(0.45, -0.18), fontsize=7.5); ax.axhline(3.5, color=INK2, lw=.6)
save(fig, o / "land_use_composition.png",
     f"Mean of per-household shares (each farm weighted equally). Denominator = land owned, or the sum of listed uses where that is larger "
     f"({int(((used > A.owned) & ok).sum())} HH, e.g. rented-in land). Land rented in not shown (asked of 29 HH only). n = {ok.sum()} HH with land and at least one use.")

# F2 % using each use and median acres among users
rows = []
for d in D:
    for u in uses:
        v = A.loc[A.district == d, u]
        rows.append({"district": DIST_LABEL[d], "land use": u, "n answered": int(v.notna().sum()), "% of answering HH with >0 acres": round((v > 0).sum() / v.notna().sum() * 100, 1),
                     "median acres among users": v[v > 0].median(), "q25": v[v > 0].quantile(.25), "q75": v[v > 0].quantile(.75),
                     "Mann-Whitney p (users, districts)": p_dist(A.loc[A[u] > 0, u], A.district[A[u] > 0])})
U = pd.DataFrame(rows); U.round(3).to_csv(o / "land_use_by_type.csv", index=False)
fig, ax = plt.subplots(1, 2, figsize=(9, 3.4), sharey=True)
y = np.arange(len(uses))[::-1]; w = .38
for i, d in enumerate(D):
    u = U[U.district == DIST_LABEL[d]].set_index("land use").reindex(uses)
    ax[0].barh(y + (.5 - i) * w, u["% of answering HH with >0 acres"], w, color=DIST[d], label=DIST_LABEL[d])
    ax[1].barh(y + (.5 - i) * w, u["median acres among users"], w, color=DIST[d])
    for yi, v in zip(y + (.5 - i) * w, u["% of answering HH with >0 acres"]): ax[0].text(v + 1, yi, f"{v:.0f}", va="center", fontsize=7)
    for yi, v in zip(y + (.5 - i) * w, u["median acres among users"]):
        if pd.notna(v): ax[1].text(v + .03, yi, f"{v:.2g}", va="center", fontsize=7)
ax[0].set_yticks(y, uses); ax[0].set_xlabel("% of households with this use"); ax[0].set_title("Households using land for each purpose")
ax[1].set_xlabel("Median acres (households with this use)"); ax[1].set_title("Area among users")
for a in ax: a.grid(axis="y", visible=False)
ax[0].legend(loc="lower right")
save(fig, o / "land_use_by_type.png",
     "Percent of households answering each land-use item (n per item in CSV: coffee ~593, other crops/grazing/trees ~535, rented out 469, other activities 117). "
     "Replaces the old pooled boxplot (mostly zeros) and the radar/spider charts.")

# ================================================================== land_vs_coffee
o = odir("land_vs_coffee")
C = s[["_id", "district", "li_group", "land_owned_ac", "coffee_ac"]].dropna(subset=["land_owned_ac", "coffee_ac"]).copy()
C["coffee_share_pct"] = C.coffee_ac / C.land_owned_ac * 100
C.to_csv(o / "land_vs_coffee_households.csv", index=False)
rho = {d: stats.spearmanr(C.land_owned_ac[C.district == d], C.coffee_ac[C.district == d]) for d in D}
over = (C.coffee_ac > C.land_owned_ac).sum()
T = pd.concat({**{DIST_LABEL[d]: summ(C.coffee_share_pct[C.district == d]) for d in D},
               **{f"LI {g}": summ(C.coffee_share_pct[C.li_group == g]) for g in LI_GROUPS}}, axis=1).T.round(1)
T["spearman rho land vs coffee"] = [round(rho[d][0], 2) for d in D] + [np.nan] * 4
T.loc["Mukono", "test"] = f"coffee share, Mann-Whitney districts {pfmt(p_dist(C.coffee_share_pct, C.district))}"
T.loc["LI <25%", "test"] = f"coffee share, Kruskal LI groups {pfmt(p_li(C.coffee_share_pct, C.li_group))}"
T.to_csv(o / "coffee_share_of_land_summary.csv")
fig, ax = plt.subplots(1, 2, figsize=(9.2, 3.8), gridspec_kw={"width_ratios": [1.25, 1]})
for i, d in enumerate(D):
    g = C[C.district == d]; rng = np.random.default_rng(i)
    ax[0].scatter(g.land_owned_ac * np.exp(rng.normal(0, .04, len(g))), g.coffee_ac * np.exp(rng.normal(0, .04, len(g))), s=10, alpha=.45,
                  color=DIST[d], linewidths=0, label=f"{DIST_LABEL[d]} (n={len(g)}, Spearman rho={rho[d][0]:.2f})")
ax[0].plot([.1, 30], [.1, 30], color=INK2, lw=1, ls=(0, (4, 3))); ax[0].text(18, 22, "coffee = all land", fontsize=7.5, color=INK2, ha="right")
ax[0].set_xscale("log"); ax[0].set_yscale("log"); ax[0].set_xlim(.18, 25); ax[0].set_ylim(.05, 25)
for a in (ax[0].xaxis, ax[0].yaxis): a.set_major_formatter(FuncFormatter(lambda x, p: f"{x:g}"))
ax[0].set_xlabel("Land owned (acres, log scale)"); ax[0].set_ylabel("Land under Robusta coffee (acres, log scale)")
ax[0].legend(loc="upper left", fontsize=7.5); ax[0].set_title("Total land vs coffee land")
x = np.arange(4); w = .38
for i, d in enumerate(D):
    m = C[C.district == d].groupby("li_group", observed=False).coffee_share_pct.median()
    ax[1].bar(x + (i - .5) * w, m.values, w, color=DIST[d], label=DIST_LABEL[d])
    for xi, v in zip(x + (i - .5) * w, m.values): ax[1].text(xi, v + 1, f"{v:.0f}", ha="center", fontsize=7.5)
ax[1].set_xticks(x, LI_GROUPS); ax[1].set_xlabel("Gross income as % of household benchmark"); ax[1].set_ylabel("Median coffee area as % of land owned")
ax[1].set_ylim(0, 90); ax[1].legend(ncol=2, loc="upper center"); ax[1].set_title("Coffee share of land by LI group")
save(fig, o / "land_vs_coffee.png",
     f"n = {len(C)} HH with both values (land > 500 acres set to missing; no 95th-percentile trimming). Points jittered slightly. "
     f"{over} HH report more coffee than land owned (likely rented-in land). Coffee share Kruskal across LI groups {pfmt(p_li(C.coffee_share_pct, C.li_group))}.")

# ================================================================== tree_analysis
o = odir("tree_analysis")
TR = s[["district", "li_group", "trees_on_farm", "trees_per_acre", "land_owned_ac"]].copy()
excl = int(s.trees_count_unreliable.sum())
bins = [-.5, .5, 5.5, 10.5, 20.5, 50.5, 100.5, 1e9]; blab = ["0", "1-5", "6-10", "11-20", "21-50", "51-100", ">100"]
TR["class"] = pd.cut(TR.trees_on_farm, bins, labels=blab)
ct = pd.crosstab(TR["class"], TR.district).reindex(blab, fill_value=0); cp = ct / ct.sum() * 100
pd_t = p_dist(TR.trees_on_farm, TR.district)
out = pd.concat([ct.add_suffix(" (n)"), cp.round(1).add_suffix(" (%)")], axis=1)
desc = TR.groupby("district").trees_on_farm.describe().round(1)
out.to_csv(o / "trees_on_farm_distribution.csv"); desc.assign(mannwhitney_p=round(pd_t, 4)).to_csv(o / "trees_on_farm_by_district.csv")
fig, ax = plt.subplots(figsize=(7.2, 3.4)); x = np.arange(len(blab)); w = .38
for i, d in enumerate(D):
    ax.bar(x + (i - .5) * w, cp[d], w, color=DIST[d], label=f"{DIST_LABEL[d]} (n={int(ct[d].sum())}, median {TR.trees_on_farm[TR.district == d].median():.0f})")
    for xi, v in zip(x + (i - .5) * w, cp[d]): ax.text(xi, v + .5, f"{v:.0f}", ha="center", fontsize=7)
ax.set_xticks(x, blab); ax.set_xlabel("Number of trees on farm (farmer's count)"); ax.set_ylabel("% of households"); ax.legend()
ax.grid(axis="x", visible=False); ax.set_title("Number of trees on farm, by district")
save(fig, o / "trees_on_farm_distribution.png",
     f"Counts of enumerator Namyenya (Nakaseke, {excl} HH) excluded: median 258 'trees', probably coffee bushes. One further HH missing. "
     f"Mann-Whitney districts {pfmt(pd_t)}. Merges old histogram and district boxplot.")

r2 = {d: stats.spearmanr(TR.land_owned_ac[TR.district == d], TR.trees_on_farm[TR.district == d], nan_policy="omit") for d in D}
fig, ax = plt.subplots(figsize=(6.2, 3.8))
for i, d in enumerate(D):
    g = TR[TR.district == d].dropna(subset=["land_owned_ac", "trees_on_farm"]); rng = np.random.default_rng(10 + i)
    ax.scatter(g.land_owned_ac * np.exp(rng.normal(0, .04, len(g))), g.trees_on_farm + 1, s=10, alpha=.45, color=DIST[d], linewidths=0,
               label=f"{DIST_LABEL[d]} (n={len(g)}, Spearman rho={r2[d][0]:.2f}, {pfmt(r2[d][1])})")
ax.set_xscale("log"); ax.set_yscale("log")
for a in (ax.xaxis, ax.yaxis): a.set_major_formatter(FuncFormatter(lambda x, p: f"{x:g}"))
ax.set_xlabel("Land owned (acres, log scale)"); ax.set_ylabel("Trees on farm + 1 (log scale)"); ax.legend(loc="upper left", fontsize=7.5)
ax.set_title("Trees on farm vs land owned")
save(fig, o / "trees_vs_land.png", f"Namyenya's tree counts excluded; land > 500 acres missing. +1 so farms with 0 trees can be shown on a log axis.")
TR.dropna(subset=["land_owned_ac", "trees_on_farm"])[["district", "land_owned_ac", "trees_on_farm"]].to_csv(o / "trees_vs_land_households.csv", index=False)

rows = []
for d in D:
    for g in LI_GROUPS:
        q = TR[(TR.district == d) & (TR.li_group == g)]
        rows.append({"district": DIST_LABEL[d], "li_group": g, "n with tree count": int(q.trees_on_farm.notna().sum()),
                     "median trees on farm": q.trees_on_farm.median(), "median trees per cropped acre": q.trees_per_acre.median()})
LT = pd.DataFrame(rows)
pk = {d: (p_li(TR.trees_on_farm[TR.district == d], TR.li_group[TR.district == d]), p_li(TR.trees_per_acre[TR.district == d], TR.li_group[TR.district == d])) for d in D}
LT["Kruskal p trees (within district)"] = LT.district.map({DIST_LABEL[d]: round(pk[d][0], 4) for d in D})
LT["Kruskal p trees/acre (within district)"] = LT.district.map({DIST_LABEL[d]: round(pk[d][1], 4) for d in D})
LT.round(2).to_csv(o / "trees_by_li_group.csv", index=False)
fig, ax = plt.subplots(1, 2, figsize=(9, 3.4)); x = np.arange(4); w = .38
for k, (col, lab) in enumerate([("median trees on farm", "Median trees on farm"), ("median trees per cropped acre", "Median trees per acre (coffee + other crops)")]):
    for i, d in enumerate(D):
        q = LT[LT.district == DIST_LABEL[d]]
        ax[k].bar(x + (i - .5) * w, q[col], w, color=DIST[d], label=f"{DIST_LABEL[d]} (Kruskal {pfmt(pk[d][k])})")
        for xi, v, n in zip(x + (i - .5) * w, q[col], q["n with tree count"]): ax[k].text(xi, v * 1.02 + .2, f"{v:.0f}\nn={n}", ha="center", fontsize=6.5)
    ax[k].set_xticks(x, LI_GROUPS); ax[k].set_xlabel("Gross income as % of household benchmark"); ax[k].set_ylabel(lab)
    ax[k].set_ylim(0, LT[col].max() * 1.45); ax[k].legend(fontsize=7, loc="upper center", ncol=1); ax[k].grid(axis="x", visible=False)
ax[0].set_title("Trees on farm by living income group"); ax[1].set_title("Tree density by living income group")
save(fig, o / "trees_by_li_group.png", "Namyenya's tree counts excluded. Associations only (see module C, table C3d); not causal.")

# ================================================================== tree_origin
o = odir("tree_origin")
orig = s["_5_Ask_the_respondent_if_the_t"].fillna("")
hp = orig.str.contains("planted|both"); hn = orig.str.contains("natural|both")
s["tree_origin"] = np.select([hp & hn, hp, hn], ["Both planted and remnant", "Planted only", "Naturally growing / remnant only"], None)
OC = ["Planted only", "Both planted and remnant", "Naturally growing / remnant only"]
G = grp_row(s[["district", "li_group", "tree_origin"]].dropna(subset=["tree_origin"]))
cnt = pd.crosstab(G.row, G.tree_origin).reindex(index=rows_label(), columns=OC, fill_value=0); pct = cnt.div(cnt.sum(1), axis=0) * 100
p1 = p_chi(s.district, s.tree_origin); p2 = p_chi(s.li_group, s.tree_origin)
out = pd.concat([cnt.add_suffix(" (n)"), pct.round(1).add_suffix(" (%)")], axis=1); out["n valid"] = cnt.sum(1)
out.loc["Mukono", "chi-square p"] = f"districts {pfmt(p1)}"; out.loc["LI <25%", "chi-square p"] = f"LI groups {pfmt(p2)}"
out.to_csv(o / "tree_origin_by_district_li_group.csv")
pd.Series(orig).value_counts().rename_axis("raw answer").rename("n").to_csv(o / "tree_origin_raw_answers.csv")
fig, ax = plt.subplots(figsize=(7.4, 3.4))
stacked_rows(ax, pct.set_axis([f"{r} (n={n})" for r, n in zip(pct.index, cnt.sum(1))]), [SRC[2], SRC[0], GREY],
             "Origin of trees on farm, by district and living income group")
ax.legend(ncol=3, loc="upper center", bbox_to_anchor=(0.45, -0.18)); ax.axhline(3.5, color=INK2, lw=.6)
save(fig, o / "tree_origin_by_district_li_group.png",
     f"Multi-select answer: 'planted' + 'naturally growing' (any order) counted as Both. All 597 HH answered; no Unknown/Other category remains. "
     f"Chi-square: districts {pfmt(p1)}; LI groups {pfmt(p2)}.")

# ================================================================== tree_dynamics
o = odir("tree_dynamics")
s["removed"] = s["_120_Have_you_removed_trees_in"].map({"Yes": 1, "No": 0})
s["n_removed"] = np.where(s.removed == 0, 0, num(s.Trees_Removed))
s["asked_planting"] = s["Have_you_planted_or_removed_tress"].notna()
s["n_planted"] = num(s.Planted).where(s["Have_you_planted_or_removed_tress"].eq("Yes"))
s.loc[s["Have_you_planted_or_removed_tress"].eq("No"), "n_planted"] = 0
s["behaviour"] = np.select([hp & s.removed.eq(1), hp & s.removed.eq(0), ~hp & s.removed.eq(1), ~hp & s.removed.eq(0)],
                           ["Has planted trees, removed some", "Has planted trees, none removed", "Remnant trees only, removed some", "Remnant trees only, none removed"], None)
BC = ["Has planted trees, none removed", "Has planted trees, removed some", "Remnant trees only, removed some", "Remnant trees only, none removed"]
G = grp_row(s[["district", "li_group", "behaviour"]].dropna(subset=["behaviour"]))
cnt = pd.crosstab(G.row, G.behaviour).reindex(index=rows_label(), columns=BC, fill_value=0); pct = cnt.div(cnt.sum(1), axis=0) * 100
pr1 = p_chi(s.district, s.removed); pr2 = p_chi(s.li_group, s.removed)
out = pd.concat([cnt.add_suffix(" (n)"), pct.round(1).add_suffix(" (%)")], axis=1); out["n valid"] = cnt.sum(1)
out["% removed trees"] = G.groupby("row").behaviour.apply(lambda b: b.str.contains("removed some").mean() * 100).reindex(rows_label()).round(1)
out.loc["Mukono", "chi-square p (removed)"] = f"districts {pfmt(pr1)}"; out.loc["LI <25%", "chi-square p (removed)"] = f"LI groups {pfmt(pr2)}"
out.to_csv(o / "tree_behaviour_by_district_li_group.csv")
fig, ax = plt.subplots(figsize=(7.8, 3.5))
stacked_rows(ax, pct.set_axis([f"{r} (n={n})" for r, n in zip(pct.index, cnt.sum(1))]), [SRC[2], "#7fd3b4", SRC[1], GREY],
             "Tree planting and removal, by district and living income group")
ax.legend(ncol=2, loc="upper center", bbox_to_anchor=(0.45, -0.18)); ax.axhline(3.5, color=INK2, lw=.6)
save(fig, o / "tree_behaviour_by_district_li_group.png",
     f"'Has planted trees' = tree origin includes planted (planted only or both); 'removed' = Q120 'Have you removed trees' (all 597 answered). "
     f"Removal chi-square: districts {pfmt(pr1)}; LI groups {pfmt(pr2)}.")

# numbers planted / removed and net change (planting count asked only after an explicit 'planted' origin answer)
Q = s[["district", "li_group", "n_planted", "n_removed", "asked_planting"]].copy()
Q["net_change"] = (Q.n_planted - Q.n_removed).where(Q.n_planted.notna() & Q.n_removed.notna())
rows = []
for col, lab in [("n_planted", "trees planted"), ("n_removed", "trees removed (removers only)"), ("net_change", "net change (planted - removed)")]:
    for d in D:
        v = Q.loc[Q.district == d, col]
        if col == "n_removed": v = v[v > 0]
        rows.append({"measure": lab, "district": DIST_LABEL[d], **summ(v).round(1).to_dict(), "min": v.min(), "max": v.max()})
pd.DataFrame(rows).to_csv(o / "trees_planted_removed_counts.csv", index=False)
fig, ax = plt.subplots(1, 3, figsize=(10.5, 3.4)); fig.subplots_adjust(wspace=.5)
for k, (col, lab, logy) in enumerate([("n_planted", "Trees planted (count)", True), ("n_removed", "Trees removed (count)", True),
                                      ("net_change", "Net change, planted - removed", False)]):
    for i, d in enumerate(D):
        v = Q.loc[Q.district == d, col].dropna()
        if col == "n_removed": v = v[v > 0]
        rng = np.random.default_rng(20 + k * 2 + i)
        ax[k].scatter(i + rng.uniform(-.18, .18, len(v)), v if not logy else v.clip(lower=.8), s=8, alpha=.45, color=DIST[d], linewidths=0)
        ax[k].plot([i - .25, i + .25], [v.median()] * 2, color=INK, lw=2)
        ax[k].text(i, 1.02, f"n={len(v)}\nmedian {v.median():g}", transform=ax[k].get_xaxis_transform(), ha="center", va="bottom", fontsize=7)
    ax[k].set_xticks([0, 1], [DIST_LABEL[d] for d in D]); ax[k].set_ylabel(lab + (" (log)" if logy else "")); ax[k].grid(axis="x", visible=False)
    if logy: ax[k].set_yscale("log"); ax[k].yaxis.set_major_formatter(FuncFormatter(lambda x, p: f"{x:g}"))
    else: ax[k].set_yscale("symlog", linthresh=10); ax[k].axhline(0, color=INK2, lw=.8); ax[k].yaxis.set_major_formatter(FuncFormatter(lambda x, p: f"{x:g}"))
ax[2].set_ylim(-300, 30000); ax[0].set_title("Trees planted", pad=26); ax[1].set_title("Trees removed", pad=26); ax[2].set_title("Net change (sub-sample)", pad=26)
save(fig, o / "trees_planted_removed_counts.png",
     "Planted count was asked only of the 78 HH who ticked 'planted' as a separate tree-origin option (not of the 407 who answered 'both'), "
     "so planted and net-change panels describe that sub-sample only (planted 0 for 'No' answers; 0 values drawn at 0.8). Removed = HH answering Yes to Q120 "
     "with a count. Bar = median. One Nakaseke HH reports 15,000 planted (kept, unverified). Old version treated unanswered as 0 and as 'Neither'.")

# ================================================================== tree_products
o = odir("tree_products")
rows = []
for i in range(3):
    pre = f"group_wz3xj67/group_ta7np61/{i}/group_wz3xj67/group_ta7np61/"
    g = lambda c: sv[pre + c] if (pre + c) in sv else pd.Series(np.nan, index=sv.index)
    price = num(g("_169_Farmgate_Price_f_the_selected_product")).fillna(num(g("Farmgate_Price_for_the_selected_product")))
    rows.append(pd.DataFrame({"_id": sv["_id"], "product": g("Select_the_tree_product"), "year": num(g("Year_of_Harvest_001")),
                              "qty": num(g("Volume_Quatity_harvested")), "price": price, "home": num(g("_170_If_part_of_the_h_is_comsumed_at_home"))}))
TP = pd.concat(rows).dropna(subset=["product"]).sort_values("year").drop_duplicates(["_id", "product"], keep="last")   # most recent year per product
TP["home"] = np.minimum(TP.home, TP.qty).where(TP.qty.notna(), TP.home)                                             # home use <= harvest
NAMES = {"Bananas": "Bananas", "fruits": "Fruits", "firewood": "Firewood", "Annuals": "Annual crops*", "roots": "Roots", "leaves": "Leaves",
         "Logs/Poles": "Logs/poles", "bark": "Bark"}
TP["product"] = TP["product"].map(NAMES).fillna(TP["product"])
TP = TP.merge(s[["_id", "district", "li_group", "income_total_mi", "gross"]], on="_id")
TP["value_harvest"] = TP.qty * TP.price; TP["value_home"] = TP.home * TP.price; TP["value_sold"] = (TP.qty - TP.home.fillna(0)).clip(lower=0) * TP.price
TP["value_flag"] = TP.value_harvest > TP.gross        # value of one product > household's whole gross income: price probably entered as a total
for c in ["value_harvest", "value_home", "value_sold"]: TP[c + "_ok"] = TP[c].where(~TP.value_flag)
TP.to_csv(o / "tree_products_long.csv", index=False)
PORD = TP[TP["product"] != "Annual crops*"].groupby("product")._id.nunique().sort_values(ascending=False).index.tolist() + ["Annual crops*"]

# F1 % of HH reporting each product
rep = TP.groupby(["product", "district"])._id.nunique().unstack().reindex(PORD).fillna(0)
rp = rep / N.reindex(D).values * 100
any_tree = TP[TP["product"] != "Annual crops*"].groupby("district")._id.nunique() / N * 100
any_all = TP.groupby("district")._id.nunique() / N * 100
pc = {p: p_chi(s.district, s._id.isin(TP._id[TP["product"] == p])) for p in PORD}
out = pd.concat([rep.add_suffix(" (n HH)"), rp.round(1).add_suffix(" (% of 597-sample district)")], axis=1); out["chi-square p districts"] = pd.Series(pc).round(4)
out.loc["Any tree product (excl. annual crops)"] = [*[int(round(any_tree[d] * N[d] / 100)) for d in D], *any_tree.reindex(D).round(1).values, np.nan]
out.loc["Any product incl. annual crops"] = [*[int(round(any_all[d] * N[d] / 100)) for d in D], *any_all.reindex(D).round(1).values, np.nan]
out.to_csv(o / "tree_products_reported.csv")
fig, ax = plt.subplots(figsize=(7, 3.6)); y = np.arange(len(PORD))[::-1]; w = .38
for i, d in enumerate(D):
    ax.barh(y + (.5 - i) * w, rp[d], w, color=DIST[d], label=f"{DIST_LABEL[d]} (n={N[d]}; any tree product {any_tree[d]:.0f}%)")
    for yi, v in zip(y + (.5 - i) * w, rp[d]): ax.text(v + .4, yi, f"{v:.0f}", va="center", fontsize=7)
ax.set_yticks(y, PORD); ax.set_xlabel("% of households reporting a harvest (latest year)"); ax.legend(loc="upper right"); ax.grid(axis="y", visible=False)
ax.set_title("Tree and farm products harvested, by district")
save(fig, o / "tree_products_reported.png",
     "Q168-170 product list (up to 3 per HH). *Annual crops are a listed option but not a tree product; shown for completeness and excluded from tree-product totals. "
     "Percent of all households in the district. Merges old 'frequency' and 'clean (no annuals)' charts.")

# F2 value harvested per product
rows = []
for p in PORD:
    for d in D + ["all"]:
        q = TP[(TP["product"] == p) & ((TP.district == d) | (d == "all"))]
        v = q.value_harvest_ok.dropna()
        rows.append({"product": p, "district": DIST_LABEL.get(d, "All"), "n reporting": len(q), "n with value": len(v), "n flagged": int(q.value_flag.sum()),
                     "median value harvested (UGX/yr)": v.median(), "q25": v.quantile(.25), "q75": v.quantile(.75),
                     "median value sold (UGX/yr)": q.value_sold_ok.median(), "median value home (UGX/yr)": q.value_home_ok.median(),
                     "total value harvested (UGX/yr)": v.sum(), "median value harvested, unflagged (module C rule)": q.value_harvest.median()})
V = pd.DataFrame(rows)
tot = V[(V.district == "All") & (V["product"] != "Annual crops*")]
V["% of total tree-product value (excl. annual crops)"] = np.where((V.district == "All") & (V["product"] != "Annual crops*"),
                                                                     V["total value harvested (UGX/yr)"] / tot["total value harvested (UGX/yr)"].sum() * 100, np.nan)
V.round(1).to_csv(o / "tree_product_value.csv", index=False)
TPN = [p for p in PORD if p != "Annual crops*"]
fig, ax = plt.subplots(1, 2, figsize=(10, 3.5), gridspec_kw={"width_ratios": [1.4, 1]}); fig.subplots_adjust(wspace=.35); y = np.arange(len(TPN))[::-1]
for i, d in enumerate(D):
    q = V[V.district == DIST_LABEL[d]].set_index("product").reindex(TPN)
    ax[0].barh(y + (.5 - i) * w, q["median value harvested (UGX/yr)"], w, color=DIST[d], label=DIST_LABEL[d])
    for yi, v, n in zip(y + (.5 - i) * w, q["median value harvested (UGX/yr)"], q["n with value"]):
        if pd.notna(v): ax[0].text(v * 1.03, yi, f"{money(v)} (n={n})", va="center", fontsize=6.5)
ax[0].set_yticks(y, TPN); ax[0].xaxis.set_major_formatter(FuncFormatter(money)); ax[0].set_xlabel("Median value harvested per reporting HH (UGX/yr)")
ax[0].set_xlim(0, V.loc[V["product"].isin(TPN) & (V.district != "All"), "median value harvested (UGX/yr)"].max() * 1.35)
ax[0].legend(loc="lower right"); ax[0].grid(axis="y", visible=False); ax[0].set_title("Value of each tree product")
sh = tot.set_index("product").reindex(TPN)
ax[1].barh(y, sh["total value harvested (UGX/yr)"] / sh["total value harvested (UGX/yr)"].sum() * 100, .6, color=SRC[2])
for yi, v in zip(y, sh["total value harvested (UGX/yr)"] / sh["total value harvested (UGX/yr)"].sum() * 100): ax[1].text(v + .5, yi, f"{v:.0f}%", va="center", fontsize=7)
ax[1].set_yticks(y, TPN); ax[1].set_xlabel("% of total tree-product value, both districts"); ax[1].grid(axis="y", visible=False)
ax[1].set_title("Share of total value")
save(fig, o / "tree_product_value.png",
     f"Value = quantity harvested x farm-gate price, most recent harvest year per product. {int(TP.value_flag.sum())} records whose value exceeds the household's "
     "whole gross income (price probably entered as a total) are left out of values. Replaces old charts that summed unit prices across households "
     "and the old 'income' bar (all zeros; the old code read only the secondary price column and missed Q169, which holds 338 of the 375 prices).")

# F3 home vs sold
H = TP[(TP.qty > 0)].copy(); H["home_share"] = (H.home.fillna(0) / H.qty * 100)
hs = H.groupby("product").agg(n=("home_share", "size"), home=("home_share", "mean")).reindex(PORD); hs["sold"] = 100 - hs.home
hsd = H.groupby(["product", "district"]).home_share.agg(["size", "mean"]).unstack().round(1)
pd.concat([hs.round(1), hsd], axis=1).to_csv(o / "tree_product_home_vs_sold.csv")
fig, ax = plt.subplots(figsize=(7, 3.4))
stacked_rows(ax, hs[["home", "sold"]].set_axis(["Used at home", "Sold"], axis=1).set_axis([f"{p} (n={n})" for p, n in zip(hs.index, hs.n)]),
             [SRC[3], SRC[0]], "Share of each product's harvest used at home vs sold", "Mean share of quantity harvested (%)")
ax.legend(ncol=2, loc="upper center", bbox_to_anchor=(0.45, -0.18))
save(fig, o / "tree_product_home_vs_sold.png",
     "Mean of per-record shares; records with quantity > 0. Home use capped at quantity harvested; missing home use = 0 (all sold). District split in CSV.")

# F4 link to living income: tree products (excl. annual crops) by LI group
TT = TP[TP["product"] != "Annual crops*"]
hv = TT.groupby("_id").agg(v_sold=("value_sold_ok", lambda x: x.sum(min_count=1)), v_harv=("value_harvest_ok", lambda x: x.sum(min_count=1)))
HH = s[["_id", "district", "li_group", "income_total_mi", "gross"]].merge(hv, left_on="_id", right_index=True, how="left")
HH["reports"] = HH._id.isin(TT._id)
HH["sold_pct_cash"] = HH.v_sold / HH.income_total_mi.where(HH.income_total_mi > 0) * 100
rows = []
for d in D:
    for g in LI_GROUPS:
        q = HH[(HH.district == d) & (HH.li_group == g)]
        rows.append({"district": DIST_LABEL[d], "li_group": g, "n HH": len(q), "% reporting a tree product": q.reports.mean() * 100,
                     "n reporters with value": int(q.v_sold.notna().sum()), "median value sold, reporters (UGX/yr)": q.v_sold.median(),
                     "median value sold as % of cash income, reporters": q.sold_pct_cash.median()})
LG = pd.DataFrame(rows)
pq = {d: (p_chi(HH.li_group[HH.district == d], HH.reports[HH.district == d]), p_li(HH.v_sold[HH.district == d], HH.li_group[HH.district == d])) for d in D}
LG["chi-square p reporting (within district)"] = LG.district.map({DIST_LABEL[d]: round(pq[d][0], 4) for d in D})
LG["Kruskal p value sold (within district)"] = LG.district.map({DIST_LABEL[d]: round(pq[d][1], 4) for d in D})
LG.round(1).to_csv(o / "tree_products_by_li_group.csv", index=False)
fig, ax = plt.subplots(1, 2, figsize=(9, 3.4)); x = np.arange(4)
for k, (col, lab) in enumerate([("% reporting a tree product", "% of households reporting"), ("median value sold, reporters (UGX/yr)", "Median value sold (UGX/yr)")]):
    for i, d in enumerate(D):
        q = LG[LG.district == DIST_LABEL[d]]
        ax[k].bar(x + (i - .5) * w, q[col], w, color=DIST[d], label=f"{DIST_LABEL[d]} ({'chi-sq' if k == 0 else 'Kruskal'} {pfmt(pq[d][k])})")
        for xi, v, n in zip(x + (i - .5) * w, q[col], q["n HH"] if k == 0 else q["n reporters with value"]):
            if pd.notna(v): ax[k].text(xi, v * 1.02, (f"{v:.0f}" if k == 0 else money(v)) + f"\nn={n}", ha="center", fontsize=6.5)
    ax[k].set_xticks(x, LI_GROUPS); ax[k].set_xlabel("Gross income as % of household benchmark"); ax[k].set_ylabel(lab)
    ax[k].set_ylim(0, LG[col].max() * 1.45); ax[k].legend(fontsize=7, loc="upper center")
    ax[k].grid(axis="x", visible=False)
ax[1].yaxis.set_major_formatter(FuncFormatter(money))
ax[0].set_title("Households harvesting tree products"); ax[1].set_title("Value of tree products sold")
save(fig, o / "tree_products_by_li_group.png",
     "Tree products = bananas, fruit, firewood, logs/poles, roots, leaves, bark (annual crops excluded). Value sold = (harvest - home use) x farm-gate price, "
     "flagged records excluded. n under bars = households (left) / reporters with a value (right). Q162e 'sale of other crops' is NOT tree income.")

# ================================================================== tree_species (shamba / Dynacof site survey)
o = odir("tree_species")
sh = pd.read_csv(ROOT / "data/raw/cleaned shamba Survey.csv", low_memory=False)
# 'Nk003' was surveyed on 07/01/2026 between MK002 and MK004 (Nakaseke sites were surveyed in Sept 2025) -> MK003 typo; NK003 exists separately
sh["site"] = sh.site_id.str.upper().where(~((sh.site_id == "Nk003") & (sh.survey_date == "07/01/2026")), "MK003")
sh["district"] = np.where(sh.site.str.startswith("MK"), "mukono", "nakaseke")
FIX = {"Psdium guajava": "Psidium guajava", "Anonna muricata": "Annona muricata", "Papaya carica": "Carica papaya",
       "Artocarpus heterophylus": "Artocarpus heterophyllus", "Melicia excelsa": "Milicia excelsa", "Jatropha carcus": "Jatropha curcas",
       "Griveillea robusta": "Grevillea robusta", "Szygium cuminii": "Syzygium cumini", "Azadichirata indica": "Azadirachta indica",
       "Baurhania parpurea": "Bauhinia purpurea", "Tabebua rosea": "Tabebuia rosea", "Ficus thoningia": "Ficus thonningii",
       "Ficus branchypoda": "Ficus brachypoda"}
rows = []
for i in range(12):
    p = f"grp_trees/rp_species/{i}/grp_trees/rp_species/"
    if p + "species_scientific" not in sh: continue
    rows.append(pd.DataFrame({"site": sh.site, "district": sh.district, "raw": sh[p + "species_scientific"], "trees_per_acre": num(sh[p + "trees_per_acre"])}))
SP = pd.concat(rows).dropna(subset=["raw"])
SP["species"] = SP.raw.str.strip().str.replace(r"\s+", " ", regex=True).str.capitalize().replace(FIX)
SP.to_csv(o / "tree_species_records.csv", index=False)
SP.groupby(["raw", "species"]).size().rename("records").reset_index().to_csv(o / "tree_species_name_normalisation.csv", index=False)
NS = sh.groupby("district").site.nunique()
agg = SP.groupby(["species", "district"]).agg(sites=("site", "nunique"), trees_per_acre=("trees_per_acre", "sum")).unstack(fill_value=0)
tab = pd.DataFrame({"sites Mukono": agg["sites"].get("mukono", 0), "sites Nakaseke": agg["sites"].get("nakaseke", 0)})
tab["sites (of 18)"] = tab.sum(1); tab["% of sites"] = (tab["sites (of 18)"] / len(sh) * 100).round(1)
tab["median trees/acre where present"] = SP.groupby(["species", "site"]).trees_per_acre.sum().groupby("species").median()
tab["total trees/acre summed over sites"] = SP.groupby("species").trees_per_acre.sum()
tab = tab.sort_values(["sites (of 18)", "total trees/acre summed over sites"], ascending=False); tab.to_csv(o / "top_species.csv")
top = tab.head(15)
fig, ax = plt.subplots(1, 2, figsize=(9.2, 4.4), sharey=True, gridspec_kw={"width_ratios": [1.3, 1]}); y = np.arange(len(top))[::-1]
ax[0].barh(y, top["sites Mukono"], .62, color=DIST["mukono"], label=f"Mukono ({NS['mukono']} sites)")
ax[0].barh(y, top["sites Nakaseke"], .62, left=top["sites Mukono"], color=DIST["nakaseke"], label=f"Nakaseke ({NS['nakaseke']} sites)")
for yi, v in zip(y, top["sites (of 18)"]): ax[0].text(v + .15, yi, f"{v}", va="center", fontsize=7)
ax[0].set_yticks(y, top.index, fontstyle="italic"); ax[0].set_xlabel("Number of sites where recorded (of 18)"); ax[0].legend(loc="lower right")
ax[0].grid(axis="y", visible=False); ax[0].set_title("Most common shade / companion tree species")
ax[1].barh(y, top["median trees/acre where present"], .62, color=SRC[2])
for yi, v in zip(y, top["median trees/acre where present"]): ax[1].text(v + .15, yi, f"{v:g}", va="center", fontsize=7)
ax[1].set_xlabel("Median trees per acre where present"); ax[1].grid(axis="y", visible=False); ax[1].set_title("Density where present")
save(fig, o / "top_species.png",
     f"Source: Dynacof/shamba site survey (data/raw/cleaned shamba Survey.csv), 18 coffee sites, {len(SP)} species records; the household survey has no species question. "
     "Names given a simple spelling normalisation only (mapping in CSV); full taxonomic cleaning is left to Objective 2. Site 'Nk003' (surveyed with Mukono sites) treated as MK003.")

print("farm_trees: done ->", OUT)
