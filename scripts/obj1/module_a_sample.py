"""Module A - sample and household characteristics (Paper 1, Table 1), linked to living-income status.
Usage: python module_a_sample.py <Household_Analysis_v1.csv> <out_dir>
Outputs: tables/A1_sample.csv, A2_characteristics_by_district.csv, A3_characteristics_by_li_group.csv,
         figures/A1_ratio_distribution.png, A2_hhsize_vs_benchmark.png
Tests: Mann-Whitney U (continuous) and chi-square (binary/categorical) between districts; Kruskal-Wallis across LI groups.
"""
import sys, os, numpy as np, pandas as pd
from scipy import stats
sys.path.insert(0, os.path.dirname(__file__)); from li_style import *
h = pd.read_csv(sys.argv[1]); out = sys.argv[2]
os.makedirs(f"{out}/tables", exist_ok=True); os.makedirs(f"{out}/figures", exist_ok=True)
h["li_group"] = pd.Categorical(h.li_group, LI_GROUPS, ordered=True)

# A1 sample frame
A1 = h.groupby(["district", "Sub_County"]).size().rename("households").reset_index()
A1.to_csv(f"{out}/tables/A1_sample.csv", index=False)

VARS = [  # (column, label, kind)  kind: c = continuous (median [IQR]), b = binary (%)
    ("hh_size", "Household size (resident members)", "c"), ("adults", "Adults", "c"), ("children", "Children", "c"),
    ("dependency_ratio", "Dependency ratio", "c"), ("female_head", "Female household head (%)", "b"),
    ("female_respondent", "Female respondent (%)", "b"), ("resp_age", "Respondent age (years, class mid-point)", "c"),
    ("resp_edu_secondary_plus", "Respondent secondary education or higher (%)", "b"), ("married", "Respondent married (%)", "b"),
    ("farming_years", "Farming experience (years)", "c"), ("land_owned_ac", "Land owned (acres)", "c"), ("coffee_ac", "Coffee area (acres)", "c"),
    ("owns_land", "Owns land (%)", "b"), ("trees_on_farm", "Trees on farm (number)", "c"), ("system_has_trees", "Coffee system includes trees (%)", "b"),
    ("credit_access", "Access to credit (%)", "b"), ("group_member", "Member of farmer group/project (%)", "b"),
    ("extension_contact", "Contact with extension officer (%)", "b"), ("saves", "Saves for emergencies (%)", "b"),
    ("n_income_sources", "Number of cash income sources", "c"),
    ("gross", "Annual income incl. in-kind (UGX)", "c"), ("bench_hh_year", "Household-size living income benchmark (UGX/yr)", "c"),
    ("ratio_hh", "Income as % of household benchmark", "c"), ("below_ref", "Below reference benchmark (%)", "b")]

def summ(s, kind):
    s = s.dropna()
    if kind == "b": return f"{s.mean()*100:.1f}"
    q = s.quantile([.25, .5, .75])
    f = (lambda v: f"{v/1e6:.2f}M") if s.median() > 1e5 else (lambda v: f"{v:.1f}" if abs(v) < 100 else f"{v:.0f}")
    return f"{f(q[.5])} [{f(q[.25])}-{f(q[.75])}]"

def test(groups, kind):
    gs = [g.dropna() for g in groups if g.dropna().size]
    if len(gs) < 2: return np.nan
    if kind == "b":
        tab = np.array([[(g == 1).sum(), (g == 0).sum()] for g in gs])
        return stats.chi2_contingency(tab)[1] if (tab.sum(0) > 0).all() else np.nan
    return stats.mannwhitneyu(*gs).pvalue if len(gs) == 2 else stats.kruskal(*gs).pvalue

def stars(p): return "" if pd.isna(p) else "***" if p < .001 else "**" if p < .01 else "*" if p < .05 else ""

rows = []
for c, lab, k in VARS:
    r = {"variable": lab, "n": int(h[c].notna().sum())}
    for dname in ["mukono", "nakaseke"]: r[DIST_LABEL[dname]] = summ(h.loc[h.district == dname, c], k)
    r["All"] = summ(h[c], k); p = test([h.loc[h.district == x, c] for x in ["mukono", "nakaseke"]], k)
    r["p (district)"] = f"{p:.3f}{stars(p)}" if pd.notna(p) else ""
    rows.append(r)
pd.DataFrame(rows).to_csv(f"{out}/tables/A2_characteristics_by_district.csv", index=False)

rows = []
for c, lab, k in VARS[:-4]:
    r = {"variable": lab}
    for g in LI_GROUPS: r[g] = summ(h.loc[h.li_group == g, c], k)
    p = test([h.loc[h.li_group == g, c] for g in LI_GROUPS], k)
    r["p (groups)"] = f"{p:.3f}{stars(p)}" if pd.notna(p) else ""
    rows.append(r)
n = h.li_group.value_counts().reindex(LI_GROUPS)
A3 = pd.DataFrame(rows); A3.loc[-1] = ["Households (n)"] + [str(int(v)) for v in n] + [""]; A3 = A3.sort_index()
A3.to_csv(f"{out}/tables/A3_characteristics_by_li_group.csv", index=False)

# Figure A1: distribution of income / household benchmark, by district (strip + box, one axis, log-free %)
fig, ax = plt.subplots(figsize=(6.4, 3.4))
rng = np.random.default_rng(1)
for i, dname in enumerate(["mukono", "nakaseke"]):
    v = h.loc[h.district == dname, "ratio_hh"].dropna().clip(upper=200)
    y = i + rng.uniform(-0.18, 0.18, len(v))
    ax.scatter(v, y, s=9, color=DIST[dname], alpha=0.45, linewidths=0)
    q = v.quantile([.25, .5, .75])
    ax.plot([q[.25], q[.75]], [i, i], color=INK, lw=2.2, solid_capstyle="round"); ax.plot(q[.5], i, "o", color=INK, ms=6, mec=SURF, mew=2)
    ax.text(q[.5], i + 0.3, f"median {q[.5]:.0f}%", ha="center", fontsize=8, color=INK)
ax.axvline(100, color=INK2, lw=1, ls=(0, (4, 3))); ax.text(101, 1.42, "living income", fontsize=8, color=INK2, va="top")
ax.set_yticks([0, 1], ["Mukono", "Nakaseke"]); ax.set_ylim(-0.5, 1.5); ax.grid(axis="y", visible=False)
ax.set_xlabel("Household income incl. in-kind, % of household-size benchmark (capped at 200%)")
ax.set_title("Most households earn less than half of a living income")
save(fig, f"{out}/figures/A1_ratio_distribution.png", "Each dot is a household; bar = interquartile range, circle = median. Income averaged over 20 imputations.")

# Figure A2: household size vs income and benchmark (why larger households are further away)
fig, ax = plt.subplots(figsize=(6.4, 3.4))
g = h.assign(size=h.hh_size.clip(upper=10)).groupby("size").agg(income=("gross", "median"), bench=("bench_hh_year", "median"), n=("gross", "size"))
g = g[g.n >= 8]
ax.plot(g.index, g.bench, color=INK2, lw=2, ls=(0, (4, 3))); ax.plot(g.index, g.income, color=DIST["mukono"], lw=2, marker="o", ms=5, mec=SURF, mew=1.5)
ax.text(g.index[-1] + 0.15, g.bench.iloc[-1], "benchmark", color=INK2, fontsize=8, va="center")
ax.text(g.index[-1] + 0.15, g.income.iloc[-1], "median income", color=INK, fontsize=8, va="center")
ax.yaxis.set_major_formatter(money); ax.set_xlabel("Household size (10 = 10 or more; sizes with <8 households omitted)"); ax.set_ylabel("UGX per year")
ax.set_xlim(g.index.min() - 0.3, g.index.max() + 1.6)
ax.set_title("Benchmark rises with household size, income barely does")
save(fig, f"{out}/figures/A2_hhsize_vs_benchmark.png", "Both districts pooled; household-size benchmark from the NFC_LW tool (v0.02).")
print(pd.DataFrame(rows).head(3)); print(A1)
