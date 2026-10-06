"""moreFigures - income group: re-runs the earlier income notebooks (Income_sources.ipynb, 'Tree Income vs Cofffee.ipynb',
Generic Dataset Analysis.ipynb) on the cleaned v1 data with the fixes listed in scripts/morefigures/BRIEF.md.
Run from repo root:  python scripts/morefigures/income.py
Writes paper1/figures/moreFigures/<folder>/ (PNG 300 dpi + CSV behind each figure + NOTES.md written separately).
Income = cleaned imputed Q162 a-h (inc_*_mi, mean of 20 imputations); Q162e = SALE OF OTHER CROPS (not tree income).
In-kind = home-grown food (inkind_food_central) + non-food tree products used at home (tree_inkind), as in gap v1.
Tree product values (Q168-170) are read as in scripts/obj1/module_c_coffee_trees.py; they partly overlap Q162 cash and
home-grown food, so they are never added into a total. Benchmarks = living income benchmark v0.02 only.
"""
import sys
from pathlib import Path
import numpy as np, pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "obj1"))
from li_style import *  # noqa: E402,F401

OUT = ROOT / "paper1" / "figures" / "moreFigures"
h = pd.read_csv(ROOT / "data" / "derived" / "Household_Analysis_v1.csv")
sv = pd.read_csv(ROOT / "data" / "derived" / "Survey_Cleaned_v1.csv", low_memory=False)
sv = sv[sv.District.isin(["mukono", "nakaseke"]) & sv._id.isin(h._id)]
assert len(h) == 597 and len(sv) == 597
num = lambda x: pd.to_numeric(x, errors="coerce")
D = ["mukono", "nakaseke"]
NOTE_SRC = "Income = cleaned Q162 a-h, mean of 20 imputations (UGX/yr). "
NEUTRAL = ["#7d7c78", "#b9b8b3"]


def outdir(name):
    p = OUT / name; p.mkdir(parents=True, exist_ok=True); return p



def money2(x, pos=None):
    """like li_style.money but keeps one decimal below 10M so 1.5M is not shown as 2M"""
    if x == 0: return "0"
    if abs(x) >= 1e6: return f"{x/1e6:g}M"
    return f"{x/1e3:.0f}k"


def save2(fig, path, note=None):
    """li_style.save, but the note is placed below everything already drawn (legends below axes)."""
    if note:
        fig.canvas.draw(); bb = fig.get_tightbbox(fig.canvas.get_renderer())
        fig.text(max(bb.x0 / fig.get_figwidth(), 0), bb.y0 / fig.get_figheight() - 0.015, note, fontsize=7.5, color=INK2,
                 ha="left", va="top", wrap=True)
    fig.savefig(path); plt.close(fig)


def fmt_m(v):
    return f"{v/1e6:.2f}M" if abs(v) >= 1e6 else f"{v/1e3:.0f}k"


def mwu(a, b):
    return stats.mannwhitneyu(a.dropna(), b.dropna(), alternative="two-sided").pvalue


def pfmt(p):
    return "p<0.001" if p < 0.001 else f"p={p:.3f}"


# ------------------------------------------------------------------ components
CASH = {"Coffee (Q162a)": "inc_coffee_mi", "Livestock (b)": "inc_livestock_mi", "Off-farm work (c)": "inc_offfarm_mi",
        "Remittances (d)": "inc_remittances_mi", "Other crop sales (e)": "inc_othercrops_mi", "Trade (f)": "inc_trade_mi",
        "Professional job (g)": "inc_professional_mi", "Other sources (h)": "inc_other_mi"}
INKIND = {"Home-grown food (in-kind)": "inkind_food_central", "Tree products used at home (in-kind)": "tree_inkind"}
ALL10 = {**CASH, **INKIND}
COL10 = SRC + NEUTRAL
BROAD = {"Coffee": ["inc_coffee_mi"], "Other crop sales": ["inc_othercrops_mi"],
         "Other cash (livestock, non-farm, transfers)": ["inc_livestock_mi", "inc_offfarm_mi", "inc_remittances_mi", "inc_trade_mi",
                                                         "inc_professional_mi", "inc_other_mi"],
         "Home-grown food (in-kind)": ["inkind_food_central"], "Tree products used at home (in-kind)": ["tree_inkind"]}
BCOL = [SRC[0], SRC[1], SRC[3], NEUTRAL[0], NEUTRAL[1]]
for k, v in BROAD.items():
    h[k] = h[v].sum(axis=1)
B_CASH, B_ALL = list(BROAD)[:3], list(BROAD)
chk = (h[list(CASH.values())].sum(axis=1) - h.income_total_mi).abs().max()
chk2 = (h.income_total_mi + h.inkind_food_central + h.tree_inkind - h.gross).abs().max()
assert chk < 1 and chk2 < 1, (chk, chk2)
mkG = lambda: [("Mukono", h[h.district == "mukono"]), ("Nakaseke", h[h.district == "nakaseke"]), ("Both", h)]
GROUPS = mkG()
BENCH = h.groupby("district").bench_ref_year.first()
n_m, n_n = (h.district == "mukono").sum(), (h.district == "nakaseke").sum()
NN = f"n = {len(h)} households (Mukono {n_m}, Nakaseke {n_n})."

# ------------------------------------------------------------------ tree products Q168-170 (as module C)
rows = []
for i in range(3):
    pre = f"group_wz3xj67/group_ta7np61/{i}/group_wz3xj67/group_ta7np61/"
    g = lambda s_: sv[pre + s_] if (pre + s_) in sv else pd.Series(np.nan, index=sv.index)
    price = num(g("_169_Farmgate_Price_f_the_selected_product")).fillna(num(g("Farmgate_Price_for_the_selected_product")))
    rows.append(pd.DataFrame({"_id": sv["_id"], "product": g("Select_the_tree_product"), "year": num(g("Year_of_Harvest_001")),
                              "qty": num(g("Volume_Quatity_harvested")), "price": price, "home": num(g("_170_If_part_of_the_h_is_comsumed_at_home"))}))
T = pd.concat(rows).dropna(subset=["product"]).sort_values("year").drop_duplicates(["_id", "product"], keep="last")
T["home"] = np.minimum(T.home, T.qty).where(T.qty.notna(), T.home)
T["value_harvest"] = T.qty * T.price
T["value_home"] = T.home * T.price
T["value_sold"] = (T.qty - T.home.fillna(0)).clip(lower=0) * T.price
NAMES = {"Bananas": "Bananas", "fruits": "Fruits", "firewood": "Firewood", "Annuals": "Annual crops", "roots": "Roots",
         "leaves": "Leaves", "Logs/Poles": "Logs/poles", "bark": "Bark"}
T["product"] = T["product"].map(NAMES).fillna(T["product"])
T = T.merge(h[["_id", "district"]], on="_id")
TT = T[T["product"] != "Annual crops"].copy()            # annual crops are not a tree product
CAP = TT.value_harvest.quantile(0.95)                     # farm-gate 'price' is sometimes a total -> cap extreme products
for c in ["value_harvest", "value_home", "value_sold"]:
    TT[c + "_cap"] = TT[c].clip(upper=CAP)
tv = TT.groupby("_id").agg(tree_reported=("product", "size"), tree_value=("value_harvest", lambda s: s.sum(min_count=1)),
                           tree_value_cap=("value_harvest_cap", lambda s: s.sum(min_count=1)),
                           tree_sold_cap=("value_sold_cap", lambda s: s.sum(min_count=1)),
                           tree_home_cap=("value_home_cap", lambda s: s.sum(min_count=1)))
h = h.merge(tv, left_on="_id", right_index=True, how="left")
h["tree_any"] = h.tree_reported.notna()
HCAP = 2.04e6   # household total capped at the gap v1 tree in-kind cap (95th pct = 2.04M); uncapped HH p95 is ~14M, driven by Nakaseke "prices" that look like totals
h["tree_value_cap"] = h.tree_value.clip(upper=HCAP)
h["tree_value_cap0"] = h.tree_value_cap.fillna(0)        # 0 for non-reporters (and reporters without a value)
tp = T.groupby(["district", "product"]).agg(households=("_id", "nunique"), with_value=("value_harvest", "count"),
                                             median_value_harvest=("value_harvest", "median"),
                                             median_value_sold=("value_sold", "median"),
                                             median_value_home=("value_home", "median")).reset_index()
tp["pct_of_households"] = tp.households / tp.district.map(h.district.value_counts()) * 100
TREE_NOTE = (f"Tree products = Q168-170 (bananas, fruit, firewood, poles, roots, leaves; 'annual crops' excluded), value = quantity x "
             f"farm-gate price (the reported 'price' is sometimes a total, so values are noisy); household total capped at "
             f"{fmt_m(HCAP)} UGX (gap v1 tree in-kind cap) for means. These values overlap Q162e and "
             "home-grown food, so they are not added to totals.")

GROUPS = mkG()
# ================================================================== 1. income_sources
od = outdir("income_sources")
tab = []
for lab, col in ALL10.items():
    for gname, g in GROUPS:
        s = g[col]
        tab.append({"source": lab, "group": gname, "n": len(s), "mean_UGX": s.mean(), "median_UGX": s.median(),
                    "pct_households_gt0": (s > 0).mean() * 100, "median_among_earners_UGX": s[s > 0].median(),
                    "share_of_mean_cash_%": s.mean() / g.income_total_mi.mean() * 100 if col in CASH.values() else np.nan,
                    "share_of_mean_gross_%": s.mean() / g.gross.mean() * 100})
tab = pd.DataFrame(tab)
tab.round(1).to_csv(od / "income_by_source_summary.csv", index=False)

# F1 mean by source and district
fig, ax = plt.subplots(figsize=(7.4, 4.6))
labs = list(ALL10); y = np.arange(len(labs))[::-1]
for j, d in enumerate(D):
    m = h[h.district == d][list(ALL10.values())].mean().values
    ax.barh(y + (0.2 if j == 0 else -0.2), m, height=0.38, color=DIST[d], label=f"{DIST_LABEL[d]} (n={(h.district == d).sum()})")
    for yi, v in zip(y, m):
        ax.text(v, yi + (0.2 if j == 0 else -0.2), " " + fmt_m(v), va="center", fontsize=7, color=INK2)
ax.axhline(y[7] - 0.5, color=INK2, lw=0.8, ls=(0, (3, 3)))
ax.set_yticks(y, labs); ax.grid(axis="y", visible=False); ax.xaxis.set_major_formatter(money2)
ax.set_xlabel("Mean per household (UGX/yr)"); ax.legend(loc="lower right")
ax.set_title("Mean household income by source and district (cash Q162 a-h, then in-kind)")
save2(fig, od / "income_by_source_mean_by_district.png",
     NOTE_SRC + "In-kind below dashed line: home-grown food (diet model, central) and non-food tree products used at home. "
     "Means are pulled up by a few large earners; medians and % earning in income_by_source_summary.csv. " + NN)

# F2 detailed shares, cash vs incl. in-kind
sh = []
for basis, cols in [("Cash only", CASH), ("Incl. in-kind", ALL10)]:
    for gname, g in GROUPS:
        m = g[list(cols.values())].mean(); sh.append(pd.Series(m / m.sum() * 100, name=(basis, gname)).rename(lambda c: {v: k for k, v in ALL10.items()}[c]))
sh = pd.DataFrame(sh); sh.index = pd.MultiIndex.from_tuples(sh.index, names=["basis", "group"])
sh.round(1).to_csv(od / "income_share_by_source_district.csv")
fig, ax = plt.subplots(figsize=(7.4, 3.9))
y = np.array([7, 6, 5, 3, 2, 1])
for yi, (idx, r) in zip(y, sh.iterrows()):
    left = 0
    for j, lab in enumerate(ALL10):
        v = r.get(lab, np.nan)
        if pd.isna(v): continue
        ax.barh(yi, v, left=left, color=COL10[j], height=0.66, edgecolor=SURF, linewidth=1, label=lab if yi == 3 else None)
        if v >= 6: ax.text(left + v / 2, yi, f"{v:.0f}", ha="center", va="center", fontsize=7, color="white" if j in (0, 2, 5, 6, 7, 8) else INK)
        left += v
ax.set_yticks(y, [f"{b}: {g}" for b, g in sh.index]); ax.set_xlim(0, 100); ax.grid(axis="y", visible=False)
ax.set_xlabel("% of mean household income"); ax.legend(ncol=3, loc="upper left", bbox_to_anchor=(0, -0.16), fontsize=7.2)
ax.set_title("Share of mean household income by source: cash only vs incl. in-kind")
save2(fig, od / "income_share_by_source_district.png", NOTE_SRC + "Share = source mean / total mean (share of pooled income). " + NN)

# F3 participation + number of sources
part = pd.DataFrame({DIST_LABEL[d]: (h[h.district == d][list(CASH.values())] > 0).mean() * 100 for d in D})
part.index = list(CASH); part["Both"] = (h[list(CASH.values())] > 0).mean().values * 100
part.round(1).to_csv(od / "participation_by_source.csv")
h["n_src5"] = h.n_income_sources.clip(upper=5)
cnt = pd.crosstab(h.n_src5, h.district)
chi = stats.chi2_contingency(cnt)
cntp = (cnt / cnt.sum() * 100).rename(columns=DIST_LABEL)
cntp.index = [str(i) if i < 5 else "5+" for i in cntp.index]
pd.concat([cnt.rename(columns=DIST_LABEL).add_suffix(" (n)"), cntp.round(1).set_index(cnt.index).add_suffix(" (%)")], axis=1).to_csv(od / "income_source_count_distribution.csv")
fig, (a1, a2) = plt.subplots(1, 2, figsize=(8.6, 3.6), gridspec_kw={"width_ratios": [1.5, 1]})
y = np.arange(len(CASH))[::-1]
for j, d in enumerate(D):
    a1.barh(y + (0.2 if j == 0 else -0.2), part[DIST_LABEL[d]], height=0.38, color=DIST[d], label=DIST_LABEL[d])
a1.set_yticks(y, list(CASH)); a1.grid(axis="y", visible=False); a1.set_xlim(0, 100)
a1.set_xlabel("% of households with income > 0"); a1.set_title("Households earning from each cash source"); a1.legend(loc="lower right")
x = np.arange(len(cntp))
for j, d in enumerate(D):
    a2.bar(x + (-0.2 if j == 0 else 0.2), cntp[DIST_LABEL[d]], width=0.38, color=DIST[d])
a2.set_xticks(x, cntp.index); a2.set_xlabel("Number of cash income sources (Q162 a-h)"); a2.set_ylabel("% of households")
a2.set_title("Number of cash sources per household"); a2.grid(axis="x", visible=False)
save2(fig, od / "participation_and_source_count.png",
     NOTE_SRC + f"A source counts if its imputed mean is > 0. District difference in distribution: chi-square = {chi[0]:.1f}, df = {chi[2]}, "
     f"{pfmt(chi[1])}. Median sources: Mukono {h[h.district == 'mukono'].n_income_sources.median():.0f}, "
     f"Nakaseke {h[h.district == 'nakaseke'].n_income_sources.median():.0f}. " + NN)

GROUPS = mkG()
# ================================================================== 2. income_composition_by_region
od = outdir("income_composition_by_region")
comp = []
for gname, g in GROUPS:
    for c in B_ALL:
        comp.append({"group": gname, "category": c, "n": len(g), "mean_UGX": g[c].mean(), "median_UGX": g[c].median(),
                     "share_of_mean_cash_%": g[c].mean() / g.income_total_mi.mean() * 100 if c in B_CASH else np.nan,
                     "share_of_mean_gross_%": g[c].mean() / g.gross.mean() * 100})
comp = pd.DataFrame(comp); comp.round(1).to_csv(od / "income_composition_by_district.csv", index=False)

# F1 grouped UGX with bootstrap CI
rng = np.random.default_rng(42)
fig, ax = plt.subplots(figsize=(7.6, 3.8))
x = np.arange(3); w = 0.16
ci_rows = []
for j, c in enumerate(B_ALL):
    ms, lo, hi = [], [], []
    for gname, g in GROUPS:
        v = g[c].values; bs = rng.choice(v, (2000, len(v))).mean(1)
        ms.append(v.mean()); lo.append(np.percentile(bs, 2.5)); hi.append(np.percentile(bs, 97.5))
        ci_rows.append({"group": gname, "category": c, "mean": v.mean(), "ci_low": lo[-1], "ci_high": hi[-1]})
    ax.bar(x + (j - 2) * w, ms, width=w, color=BCOL[j], label=c)
    ax.errorbar(x + (j - 2) * w, ms, yerr=[np.array(ms) - lo, np.array(hi) - ms], fmt="none", ecolor=INK2, elinewidth=0.8, capsize=2)
pd.DataFrame(ci_rows).round(0).to_csv(od / "income_composition_by_district_ugx_ci.csv", index=False)
ax.set_xticks(x, [f"{g} (n={len(d)})" for g, d in GROUPS]); ax.grid(axis="x", visible=False)
ax.yaxis.set_major_formatter(money2); ax.set_ylabel("Mean per household (UGX/yr)")
ax.legend(ncol=2, loc="upper left", bbox_to_anchor=(0, -0.12), fontsize=7.5)
ax.set_title("Mean household income by category and district")
save2(fig, od / "income_composition_by_district_ugx.png",
     NOTE_SRC + "Error bars = 95% bootstrap CI of the mean (households resampled; imputation uncertainty not included). "
     "'Other crop sales' is Q162e - not tree income.")

# F2 100% stacked cash vs incl in-kind
fig, axs = plt.subplots(1, 2, figsize=(8.6, 2.9), sharey=True)
shr = []
for ax, (basis, cats) in zip(axs, [("Cash only", B_CASH), ("Incl. home-grown food + tree in-kind", B_ALL)]):
    for yi, (gname, g) in zip([2, 1, 0], GROUPS):
        m = g[cats].mean(); m = m / m.sum() * 100; left = 0
        shr.append(pd.Series(m, name=(basis, gname)))
        for c in cats:
            j = B_ALL.index(c)
            ax.barh(yi, m[c], left=left, color=BCOL[j], height=0.62, edgecolor=SURF, lw=1, label=c if yi == 0 else None)
            if m[c] >= 6: ax.text(left + m[c] / 2, yi, f"{m[c]:.0f}", ha="center", va="center", fontsize=7.5, color="white" if j in (0, 3) else INK)
            left += m[c]
    ax.set_xlim(0, 100); ax.grid(axis="y", visible=False); ax.set_title(basis, fontsize=9.5); ax.set_xlabel("% of mean household income")
axs[0].set_yticks([2, 1, 0], [f"{g} (n={len(d)})" for g, d in GROUPS])
axs[1].legend(ncol=2, loc="upper left", bbox_to_anchor=(-1.1, -0.25), fontsize=7.5)
fig.suptitle("Income composition by district: cash only vs incl. in-kind", x=0.01, ha="left", fontweight="bold", fontsize=10.5, y=1.03)
pd.DataFrame(shr).round(1).to_csv(od / "income_composition_100pct.csv")
save2(fig, od / "income_composition_100pct.png", NOTE_SRC + "Share of pooled (mean) income.")

# F3 coffee dependence per household
h["coffee_share_cash"] = h.share_coffee_cash * 100
h["coffee_share_gross"] = h.inc_coffee_mi / h.gross * 100
cd = []
fig, axs = plt.subplots(1, 2, figsize=(8.0, 3.4), sharey=True)
for ax, (col, lab) in zip(axs, [("coffee_share_cash", "Coffee as % of cash income"), ("coffee_share_gross", "Coffee as % of income incl. in-kind")]):
    for i, d in enumerate(D):
        v = h.loc[h.district == d, col].dropna()
        xs = i + np.random.default_rng(i).uniform(-0.18, 0.18, len(v))
        ax.scatter(xs, v, s=6, alpha=0.35, color=DIST[d], linewidths=0)
        ax.boxplot(v, positions=[i], widths=0.5, showfliers=False, medianprops=dict(color=INK, lw=2),
                   boxprops=dict(color=INK2), whiskerprops=dict(color=INK2), capprops=dict(color=INK2))
        ax.text(i + 0.3, v.median(), f"{v.median():.0f}%", fontsize=8, va="center")
        g = h[h.district == d]
        cd.append({"measure": lab, "district": DIST_LABEL[d], "n": len(v), "median_%": v.median(), "q25": v.quantile(.25), "q75": v.quantile(.75),
                   "share_of_means_%": g.inc_coffee_mi.mean() / (g.income_total_mi if "cash" in col else g.gross).mean() * 100,
                   "pct_hh_coffee_ge_50%": (v >= 50).mean() * 100})
    p = mwu(h.loc[h.district == "mukono", col], h.loc[h.district == "nakaseke", col])
    cd[-1]["mann_whitney_p"] = p; cd[-2]["mann_whitney_p"] = p
    ax.set_xticks([0, 1], [f"{DIST_LABEL[d]}\n(n={h.loc[h.district == d, col].notna().sum()})" for d in D])
    ax.set_title(lab, fontsize=9.5); ax.grid(axis="x", visible=False); ax.set_ylim(-3, 112)
    ax.text(0.5, 108, f"Mann-Whitney {pfmt(p)}", ha="center", fontsize=7.5, color=INK2)
axs[0].set_ylabel("% of household income")
fig.suptitle("Household coffee dependence by district", x=0.01, ha="left", fontweight="bold", fontsize=10.5, y=1.02)
pd.DataFrame(cd).to_csv(od / "coffee_dependence_by_district.csv", index=False)
save2(fig, od / "coffee_dependence_by_district.png",
     NOTE_SRC + "One dot per household; box = median and quartiles. Households with zero cash income excluded from the cash panel.")

GROUPS = mkG()
# ================================================================== 3. income_contribution
od = outdir("income_contribution")
hs = []
for basis, cols, tot in [("Cash only", B_CASH, "income_total_mi"), ("Incl. in-kind", B_ALL, "gross")]:
    for gname, g in GROUPS:
        gg = g[g[tot] > 0]
        s = gg[cols].div(gg[tot], axis=0) * 100
        so = g[cols].mean() / g[tot].mean() * 100
        for c in cols:
            hs.append({"basis": basis, "group": gname, "n": len(gg), "category": c, "mean_household_share_%": s[c].mean(),
                       "median_household_share_%": s[c].median(), "share_of_mean_income_%": so[c]})
hs = pd.DataFrame(hs); hs.round(1).to_csv(od / "household_share_by_category.csv", index=False)
fig, axs = plt.subplots(1, 2, figsize=(8.6, 2.9), sharey=True)
for ax, basis in zip(axs, ["Cash only", "Incl. in-kind"]):
    for yi, (gname, _) in zip([2, 1, 0], GROUPS):
        r = hs[(hs.basis == basis) & (hs.group == gname)].set_index("category")["mean_household_share_%"]; left = 0
        for c, v in r.items():
            j = B_ALL.index(c)
            ax.barh(yi, v, left=left, color=BCOL[j], height=0.62, edgecolor=SURF, lw=1, label=c if yi == 0 else None)
            if v >= 6: ax.text(left + v / 2, yi, f"{v:.0f}", ha="center", va="center", fontsize=7.5, color="white" if j in (0, 3) else INK)
            left += v
    nlab = hs[(hs.basis == basis)].drop_duplicates("group").set_index("group").n
    ax.set_xlim(0, 100); ax.grid(axis="y", visible=False); ax.set_title(f"{basis}", fontsize=9.5); ax.set_xlabel("Mean of household shares (%)")
    if basis == "Cash only": ax.set_yticks([2, 1, 0], [f"{g} (n={nlab[g]})" for g, _ in GROUPS])
axs[1].legend(ncol=2, loc="upper left", bbox_to_anchor=(-1.1, -0.25), fontsize=7.5)
fig.suptitle("Average contribution of each category to a household's own income", x=0.01, ha="left", fontweight="bold", fontsize=10.5, y=1.03)
save2(fig, od / "household_share_by_category.png",
     NOTE_SRC + "Each household's category shares sum to 100; bars average those shares (differs from share of pooled income in "
     "income_composition_by_region; both in the CSV). Households with zero income on that basis excluded (n shown).")

# F2 main source
ms = []
for basis, cols in [("Cash only", B_CASH), ("Incl. in-kind", B_ALL)]:
    sub = h[h[cols].sum(axis=1) > 0]
    top = sub[cols].idxmax(axis=1)
    for gname, idx in [("Mukono", sub.district == "mukono"), ("Nakaseke", sub.district == "nakaseke"), ("Both", sub.district.notna())]:
        vc = top[idx].value_counts(normalize=True).reindex(cols, fill_value=0) * 100
        for c, v in vc.items():
            ms.append({"basis": basis, "group": gname, "n": int(idx.sum()), "largest_category": c, "pct_households": v})
    tabx = pd.crosstab(top, sub.district); p = stats.chi2_contingency(tabx)[1]
    ms.append({"basis": basis, "group": "chi-square district p", "n": len(sub), "largest_category": "", "pct_households": p})
ms = pd.DataFrame(ms); ms.to_csv(od / "largest_income_category.csv", index=False)
fig, axs = plt.subplots(1, 2, figsize=(8.6, 3.3), sharey=False)
for ax, (basis, cols) in zip(axs, [("Cash only", B_CASH), ("Incl. in-kind", B_ALL)]):
    y = np.arange(len(cols))[::-1]
    for j, d in enumerate(D):
        r = ms[(ms.basis == basis) & (ms.group == DIST_LABEL[d])].set_index("largest_category").pct_households.reindex(cols)
        ax.barh(y + (0.2 if j == 0 else -0.2), r.values, height=0.38, color=DIST[d], label=DIST_LABEL[d])
    p = ms[(ms.basis == basis) & (ms.group.str.startswith("chi"))].pct_households.iloc[0]
    ax.set_yticks(y, [c.replace(" (", "\n(") for c in cols], fontsize=7.5); ax.grid(axis="y", visible=False); ax.set_xlim(0, 100)
    ax.set_xlabel("% of households"); ax.set_title(f"{basis} (district chi-square {pfmt(p)})", fontsize=9.5)
axs[1].legend(loc="lower right")
fig.suptitle("Households by their largest income category", x=0.01, ha="left", fontweight="bold", fontsize=10.5, y=1.03)
save2(fig, od / "largest_income_category.png", NOTE_SRC + "Households with zero income on that basis excluded. " + NN)

# ================================================================== 4. income_correlation (Spearman)
od = outdir("income_correlation")
h = h.merge(sv[["_id", "group_fs0df76/e_Tree_plantations"]].rename(columns={"group_fs0df76/e_Tree_plantations": "tree_plant_ac"}), on="_id", how="left")
h["tree_plant_ac"] = num(h.tree_plant_ac)
CV = {**{k.split(" (")[0]: v for k, v in CASH.items()}, "Total cash income": "income_total_mi", "Income incl. in-kind": "gross",
      "No. cash sources": "n_income_sources", "Land owned (ac)": "land_owned_ac", "Coffee area (ac)": "coffee_ac",
      "Other crops area (ac)": "other_crops_ac", "Tree plantation (ac)": "tree_plant_ac", "Trees on farm": "trees_on_farm",
      "Coffee yield (kg FAQ/ac)": "coffee_yield_faq_ac", "Kiboko price": "kiboko_price", "Household size": "hh_size",
      "Farming years": "farming_years"}
CHAR = {"No. cash sources": "n_income_sources", "Land owned (ac)": "land_owned_ac", "Coffee area (ac)": "coffee_ac",
        "Other crops area (ac)": "other_crops_ac", "Tree plantation (ac)": "tree_plant_ac", "Trees on farm": "trees_on_farm",
        "Coffee yield (kg FAQ/ac)": "coffee_yield_faq_ac", "Kiboko price": "kiboko_price", "Household size": "hh_size",
        "Farming years": "farming_years", "Female respondent": "female_respondent",
        "Respondent secondary educ.+": "resp_edu_secondary_plus", "Group member": "group_member", "Extension contact": "extension_contact"}


def spearman_matrix(df):
    X = df[list(CV.values())].copy(); X.columns = list(CV)
    r = X.corr(method="spearman", min_periods=30)
    n = X.notna().astype(int).T @ X.notna().astype(int)
    return r, n


def heat(ax, r, title):
    k = len(r); mask = np.triu(np.ones((k, k), bool), 0)
    rr = r.values.copy(); rr[mask] = np.nan
    im = ax.imshow(rr, cmap="RdBu_r", vmin=-1, vmax=1)
    for i in range(k):
        for j in range(i + 1):
            v = rr[i, j]
            if i != j and not np.isnan(v): ax.text(j, i, f"{v:.2f}".replace("0.", ".").replace("-.", "-."), ha="center", va="center",
                                                    fontsize=5, color="white" if abs(v) > 0.55 else INK)
    ax.set_xticks(range(k), r.columns, rotation=90, fontsize=6.5); ax.set_yticks(range(k), r.index, fontsize=6.5)
    ax.grid(False); ax.set_title(title, fontsize=9.5); [s.set_visible(False) for s in ax.spines.values()]
    return im


r_all, n_all = spearman_matrix(h)
r_all.round(3).to_csv(od / "spearman_matrix_overall.csv"); n_all.to_csv(od / "spearman_pairwise_n_overall.csv")
fig, ax = plt.subplots(figsize=(7.4, 6.6))
im = heat(ax, r_all, "Spearman correlations among income sources and farm/household variables (both districts)")
fig.colorbar(im, ax=ax, shrink=0.6, label="Spearman rho")
save2(fig, od / "spearman_heatmap_overall.png",
     NOTE_SRC + f"Pairwise complete cases: n = {n_all.values.min()}-{n_all.values.max()} of 597 (Trees on farm excludes one enumerator's counts). "
     "Total cash includes each cash source, so source-total correlations are partly mechanical. Many zeros -> ties.")
fig, axs = plt.subplots(1, 2, figsize=(12.4, 5.4))
for ax, d in zip(axs, D):
    r, n = spearman_matrix(h[h.district == d])
    r.round(3).to_csv(od / f"spearman_matrix_{d}.csv"); n.to_csv(od / f"spearman_pairwise_n_{d}.csv")
    im = heat(ax, r, f"{DIST_LABEL[d]} (n = {n.values.min()}-{n.values.max()})")
    if d == "nakaseke": axs[1].set_yticklabels([])
fig.colorbar(im, ax=axs, shrink=0.55, label="Spearman rho")
fig.suptitle("Spearman correlations among income sources and farm/household variables, by district", x=0.01, ha="left",
             fontweight="bold", fontsize=10.5, y=0.98)
save2(fig, od / "spearman_heatmap_by_district.png", NOTE_SRC + "Pairwise complete cases; n range per panel title. Professional-job and other-source "
     "income: very few non-zero values in Nakaseke (1% and <1% of households), so those rho are unstable; blank = not computable.")


def rho_ci(x, y):
    ok = x.notna() & y.notna(); n = int(ok.sum())
    if n < 10 or x[ok].nunique() < 2: return np.nan, np.nan, np.nan, n, np.nan
    r, p = stats.spearmanr(x[ok], y[ok]); se = np.sqrt((1 + r ** 2 / 2) / (n - 3))  # Bonett-Wright SE
    z = np.arctanh(r); return r, np.tanh(z - 1.96 * se), np.tanh(z + 1.96 * se), n, p


top = []
for tot, tl in [("income_total_mi", "Total cash income"), ("gross", "Income incl. in-kind")]:
    for gname, g in [("Mukono", h[h.district == "mukono"]), ("Nakaseke", h[h.district == "nakaseke"]), ("Both", h)]:
        for lab, c in CHAR.items():
            r, lo, hi, n, p = rho_ci(g[c], g[tot])
            top.append({"income": tl, "group": gname, "variable": lab, "rho": r, "ci_low": lo, "ci_high": hi, "n": n, "p": p})
top = pd.DataFrame(top); top.round(4).to_csv(od / "spearman_income_vs_characteristics.csv", index=False)
order = top[(top.income == "Total cash income") & (top.group == "Both")].sort_values("rho").variable.tolist()
fig, axs = plt.subplots(1, 2, figsize=(8.6, 4.6), sharey=True)
for ax, tl in zip(axs, ["Total cash income", "Income incl. in-kind"]):
    for j, d in enumerate(D):
        s = top[(top.income == tl) & (top.group == DIST_LABEL[d])].set_index("variable").reindex(order)
        yy = np.arange(len(order)) + (0.15 if j == 0 else -0.15)
        ax.hlines(yy, s.ci_low, s.ci_high, color=DIST[d], lw=1.5)
        ax.scatter(s.rho, yy, s=22, color=DIST[d], zorder=3, edgecolor=SURF, label=DIST_LABEL[d])
    ax.axvline(0, color=INK2, lw=0.8); ax.set_xlim(-0.6, 0.8); ax.grid(axis="y", visible=False)
    ax.set_title(tl, fontsize=9.5); ax.set_xlabel("Spearman rho (95% CI)")
axs[0].set_yticks(np.arange(len(order)), order); axs[0].legend(loc="lower right")
nrng = top.n.min(), top.n.max()
fig.suptitle("Spearman correlation of household income with farm and household characteristics", x=0.01, ha="left",
             fontweight="bold", fontsize=10.5, y=1.02)
save2(fig, od / "spearman_income_vs_characteristics.png",
     NOTE_SRC + f"Pairwise complete cases, n = {nrng[0]}-{nrng[1]} per district (see CSV). CI: Fisher z with Bonett-Wright SE. "
     "Income incl. in-kind contains home-grown food valued from household size, so its link with household size is partly mechanical. "
     "Bivariate associations only (see B3 drivers model for adjusted estimates).")

# ================================================================== 5. district_income_comparison
od = outdir("district_income_comparison")
dc = []
for d in D:
    g = h[h.district == d]
    row = {"district": DIST_LABEL[d], "n": len(g), **{f"mean_{c}": g[c].mean() for c in B_ALL},
           "mean_cash": g.income_total_mi.mean(), "mean_gross": g.gross.mean(), "median_cash": g.income_total_mi.median(),
           "median_gross": g.gross.median(), "benchmark_ref_v0.02": BENCH[d], "median_benchmark_hh_size": g.bench_hh_year.median(),
           "mean_gross_%_of_ref": g.gross.mean() / BENCH[d] * 100, "median_gross_%_of_ref": g.gross.median() / BENCH[d] * 100,
           "pct_hh_at_or_above_hh_benchmark": (g.gross >= g.bench_hh_year).mean() * 100}
    dc.append(row)
pmw = {"cash": mwu(h[h.district == "mukono"].income_total_mi, h[h.district == "nakaseke"].income_total_mi),
       "gross": mwu(h[h.district == "mukono"].gross, h[h.district == "nakaseke"].gross)}
dc = pd.DataFrame(dc); dc["mann_whitney_p_cash"] = pmw["cash"]; dc["mann_whitney_p_gross"] = pmw["gross"]
dc.T.to_csv(od / "district_income_vs_benchmark.csv", header=False)
fig, ax = plt.subplots(figsize=(6.8, 3.8))
for i, d in enumerate(D):
    g = h[h.district == d]; bottom = 0
    for j, c in enumerate(B_ALL):
        v = g[c].mean(); ax.bar(i, v, bottom=bottom, color=BCOL[j], width=0.5, edgecolor=SURF, lw=1, label=c if i == 0 else None); bottom += v
    ax.text(i, bottom, f"mean {fmt_m(bottom)}\n({bottom / BENCH[d] * 100:.0f}% of benchmark)", ha="center", va="bottom", fontsize=7.5)
    ax.hlines(BENCH[d], i - 0.36, i + 0.36, color=INK, lw=1.6, ls=(0, (4, 2)))
    ax.text(i, BENCH[d] * 1.01, f"Living income benchmark {fmt_m(BENCH[d])}", ha="center", va="bottom", fontsize=7.2, color=INK)
    ax.plot(i, g.gross.median(), "D", color=INK, ms=5, mec=SURF, zorder=4, label="Median incl. in-kind" if i == 0 else None)
ax.set_xticks([0, 1], [f"{DIST_LABEL[d]} (n={(h.district == d).sum()})" for d in D]); ax.set_xlim(-0.5, 1.5); ax.set_ylim(0, 22e6)
ax.yaxis.set_major_formatter(money2); ax.set_ylabel("UGX per household per year"); ax.grid(axis="x", visible=False)
ax.legend(fontsize=7.2, loc="upper left", bbox_to_anchor=(1.0, 0.75))
ax.set_title("Mean household income by category vs the living income benchmark (v0.02)")
save2(fig, od / "district_income_vs_benchmark.png",
     NOTE_SRC + "Benchmark v0.02 for the reference household (2 adults + 3 children). Stacked = mean of each category; diamond = median "
     f"income incl. in-kind. District difference in income incl. in-kind: Mann-Whitney {pfmt(pmw['gross'])}.")

dist = []
fig, axs = plt.subplots(1, 2, figsize=(8.2, 3.8), sharey=True)
for ax, (col, lab) in zip(axs, [("income_total_mi", "Cash income"), ("gross", "Income incl. in-kind")]):
    for i, d in enumerate(D):
        v = h.loc[h.district == d, col].clip(lower=5e4)
        xs = i + np.random.default_rng(10 + i).uniform(-0.18, 0.18, len(v))
        ax.scatter(xs, v, s=6, alpha=0.35, color=DIST[d], linewidths=0)
        q = v.quantile([.25, .5, .75])
        ax.vlines(i + 0.27, q[.25], q[.75], color=INK, lw=3); ax.plot(i + 0.27, q[.5], "o", color=INK, ms=5, mec=SURF)
        ax.text(i + 0.33, q[.5], fmt_m(h.loc[h.district == d, col].median()), fontsize=7.5, va="center")
        ax.hlines(BENCH[d], i - 0.3, i + 0.3, color=INK, lw=1.4, ls=(0, (4, 2)))
        g = h[h.district == d]
        dist.append({"income": lab, "district": DIST_LABEL[d], "n": len(g), "q25": g[col].quantile(.25), "median": g[col].median(),
                     "q75": g[col].quantile(.75), "benchmark_ref": BENCH[d], "pct_below_ref": (g[col] < BENCH[d]).mean() * 100,
                     "pct_below_hh_benchmark": (g[col] < g.bench_hh_year).mean() * 100,
                     "mann_whitney_p": pmw["cash" if col == "income_total_mi" else "gross"]})
    ax.set_yscale("log"); ax.yaxis.set_major_formatter(money2)
    ax.set_xticks([0, 1], [DIST_LABEL[d] for d in D]); ax.grid(axis="x", visible=False)
    ax.set_title(f"{lab} (Mann-Whitney {pfmt(pmw['cash' if col == 'income_total_mi' else 'gross'])})", fontsize=9.5)
axs[0].set_ylabel("UGX per household per year (log scale)")
fig.suptitle("Distribution of household income by district, with the living income benchmark", x=0.01, ha="left",
             fontweight="bold", fontsize=10.5, y=1.02)
pd.DataFrame(dist).to_csv(od / "district_income_distribution.csv", index=False)
save2(fig, od / "district_income_distribution.png",
     NOTE_SRC + "Dots = households (values below 50k shown at 50k); black bar = interquartile range, circle = median; dashed line = "
     "reference benchmark v0.02 (Mukono 20.17M, Nakaseke 19.78M UGX/yr). " + NN)

GROUPS = mkG()
# ================================================================== 6. coffee_vs_trees_vs_other
od = outdir("coffee_vs_trees_vs_other")
h["other_cash"] = h.income_total_mi - h.inc_coffee_mi - h.inc_othercrops_mi
GROUPS = mkG()
CT = {"Coffee sales (Q162a)": "inc_coffee_mi", "Tree products harvested (Q168-170)": "tree_value_cap0",
      "Other crop sales (Q162e)": "inc_othercrops_mi", "Other cash (Q162 b,c,d,f,g,h)": "other_cash",
      "Home-grown food (in-kind)": "inkind_food_central"}
CTC = [SRC[0], SRC[5], SRC[1], SRC[3], NEUTRAL[0]]
ct = []
for gname, g in GROUPS:
    for lab, c in CT.items():
        s = g[c]
        pos = (g.tree_any & g.tree_value.notna()) if c == "tree_value_cap0" else (s > 0)
        ct.append({"group": gname, "category": lab, "n": len(g), "pct_households_gt0": (g.tree_any.mean() if c == "tree_value_cap0" else (s > 0).mean()) * 100,
                   "n_with_value": int(pos.sum()), "median_among_reporters_UGX": s[pos].median(), "mean_all_households_UGX": s.mean()})
ct = pd.DataFrame(ct); ct.round(1).to_csv(od / "coffee_trees_other_by_district.csv", index=False)
tp.round(1).to_csv(od / "tree_products_by_type.csv", index=False)
fig, axs = plt.subplots(1, 2, figsize=(8.8, 3.6), sharey=True)
y = np.arange(len(CT))[::-1]
for j, d in enumerate(D):
    s = ct[ct.group == DIST_LABEL[d]].set_index("category").reindex(list(CT))
    axs[0].barh(y + (0.2 if j == 0 else -0.2), s.pct_households_gt0, height=0.38, color=DIST[d], label=DIST_LABEL[d])
    axs[1].barh(y + (0.2 if j == 0 else -0.2), s.median_among_reporters_UGX, height=0.38, color=DIST[d])
    for yi, v, n in zip(y, s.median_among_reporters_UGX, s.n_with_value):
        axs[1].text(v, yi + (0.2 if j == 0 else -0.2), f" {fmt_m(v)} (n={n})", va="center", fontsize=6.8, color=INK2)
axs[0].set_yticks(y, list(CT)); axs[0].set_xlim(0, 100); axs[0].set_xlabel("% of households reporting")
axs[0].set_title("Households with income/value > 0", fontsize=9.5); axs[0].legend(loc="center right")
axs[1].xaxis.set_major_formatter(money2); axs[1].set_xlabel("Median among reporters (UGX/yr)"); axs[1].set_title("Typical amount when reported", fontsize=9.5)
axs[1].set_xlim(0, ct.median_among_reporters_UGX.max() * 1.45)
for a in axs: a.grid(axis="y", visible=False)
fig.suptitle("Coffee, tree products and other income: how many households and how much", x=0.01, ha="left", fontweight="bold", fontsize=10.5, y=1.03)
save2(fig, od / "coffee_trees_other_by_district.png", NOTE_SRC + TREE_NOTE + " Tree % = reported any tree product. " + NN)

# ================================================================== 7. tree_vs_other_income
od = outdir("tree_vs_other_income")
TN = {"Tree crop: coffee": ["inc_coffee_mi"], "Tree products used at home (non-food in-kind)": ["tree_inkind"],
      "Mixed / cannot split: other crop sales (Q162e)": ["inc_othercrops_mi"],
      "Mixed / cannot split: home-grown food (in-kind)": ["inkind_food_central"],
      "Non-tree: livestock, non-farm work, transfers": ["inc_livestock_mi", "inc_offfarm_mi", "inc_remittances_mi", "inc_trade_mi", "inc_professional_mi", "inc_other_mi"]}
TNC = [SRC[0], SRC[5], SRC[1], NEUTRAL[0], NEUTRAL[1]]
for k, v in TN.items(): h["tn_" + k] = h[v].sum(axis=1)
GROUPS = mkG()
tn = []
fig, axs = plt.subplots(1, 2, figsize=(8.6, 2.9), sharey=True)
for ax, (basis, cats) in zip(axs, [("Cash only", [list(TN)[0], list(TN)[2], list(TN)[4]]), ("Incl. in-kind", list(TN))]):
    for yi, (gname, g) in zip([2, 1, 0], GROUPS):
        m = g[["tn_" + c for c in cats]].mean(); m.index = cats; m = m / m.sum() * 100; left = 0
        up = (g.inc_coffee_mi.mean() + g.tree_value_cap0.mean()) / (g[["tn_" + c for c in cats]].sum(axis=1).mean() + g.tree_value_cap0.mean()) * 100
        tn.append({"basis": basis, "group": gname, "n": len(g), **{c + " %": m[c] for c in cats},
                   "sensitivity: coffee + Q168-170 tree product value as % of (total + that value)": up})
        for c in cats:
            j = list(TN).index(c)
            ax.barh(yi, m[c], left=left, color=TNC[j], height=0.62, edgecolor=SURF, lw=1, label=c if (yi == 0 and basis != "Cash only") else None)
            if m[c] >= 6: ax.text(left + m[c] / 2, yi, f"{m[c]:.0f}", ha="center", va="center", fontsize=7.5, color="white" if j in (0, 1, 3) else INK)
            left += m[c]
    ax.set_xlim(0, 100); ax.grid(axis="y", visible=False); ax.set_title(basis, fontsize=9.5); ax.set_xlabel("% of mean household income")
axs[0].set_yticks([2, 1, 0], [f"{g} (n={len(d)})" for g, d in GROUPS])
axs[1].legend(ncol=2, loc="upper left", bbox_to_anchor=(-1.1, -0.25), fontsize=7.2)
fig.suptitle("Tree-based vs non-tree income (share of mean household income)", x=0.01, ha="left", fontweight="bold", fontsize=10.5, y=1.03)
pd.DataFrame(tn).round(1).to_csv(od / "tree_vs_non_tree_share.csv", index=False)
save2(fig, od / "tree_vs_non_tree_share.png",
     NOTE_SRC + "Q162e (other crop sales) and home-grown food mix tree (banana, fruit) and annual crops and cannot be split. "
     "CSV adds a sensitivity using Q168-170 tree product values (overlaps Q162e/food, so an upper bound).")

GROUPS = mkG()
# ================================================================== 8. income_analysis
od = outdir("income_analysis")
h["non_tree"] = h.gross - h.inc_coffee_mi - h.tree_inkind
CAT = {"Tree products harvested, Q168-170 (excl. coffee)": "tree_value_cap0", "Coffee sales (Q162a)": "inc_coffee_mi",
       "Coffee + tree products": None, "All other income incl. home-grown food": "non_tree",
       "Total cash income": "income_total_mi", "Total incl. in-kind": "gross"}
ia = []
fig, axs = plt.subplots(1, 2, figsize=(8.8, 3.6), sharey=True)
for ax, d in zip(axs, D):
    g = h[h.district == d]
    vals = {k: (g[c].mean() if c else g.inc_coffee_mi.mean() + g.tree_value_cap0.mean()) for k, c in CAT.items()}
    y = np.arange(len(vals))[::-1]
    cols_ = [SRC[5], SRC[0], SRC[2], NEUTRAL[0], INK2, INK]
    ax.barh(y, list(vals.values()), color=cols_, height=0.6)
    for yi, (k, v) in zip(y, vals.items()):
        ax.text(v, yi, f" {fmt_m(v)} ({v / BENCH[d] * 100:.1f}%)", va="center", fontsize=7, color=INK2)
        ia.append({"district": DIST_LABEL[d], "n": len(g), "category": k, "mean_UGX": v, "median_UGX": (g[CAT[k]].median() if CAT[k] else np.nan),
                   "pct_of_benchmark_ref": v / BENCH[d] * 100, "pct_of_mean_gross": v / g.gross.mean() * 100})
    ax.axvline(BENCH[d], color=INK, lw=1.4, ls=(0, (4, 2)))
    ax.text(BENCH[d], y[0] + 0.55, f"Benchmark v0.02 {fmt_m(BENCH[d])} ", ha="right", va="bottom", fontsize=7.2, color=INK)
    ax.set_ylim(-0.6, y[0] + 1.1)
    ax.set_xlim(0, BENCH[d] * 1.08); ax.xaxis.set_major_formatter(money2); ax.grid(axis="y", visible=False)
    ax.set_title(f"{DIST_LABEL[d]} (n={len(g)})", fontsize=9.5); ax.set_xlabel("Mean per household (UGX/yr)")
axs[0].set_yticks(y, list(CAT), fontsize=7.8)
fig.suptitle("Mean household income by category against the living income benchmark", x=0.01, ha="left", fontweight="bold", fontsize=10.5, y=1.03)
pd.DataFrame(ia).round(1).to_csv(od / "income_by_category_vs_benchmark.csv", index=False)
save2(fig, od / "income_by_category_vs_benchmark.png",
     NOTE_SRC + "Label = mean and % of the reference benchmark (v0.02, 2 adults + 3 children). " + TREE_NOTE +
     " 'All other' = income incl. in-kind minus coffee minus non-food tree in-kind.")

print("done:", sorted(p.name for p in OUT.iterdir() if p.is_dir()))
