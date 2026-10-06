"""Module B - income composition and drivers of the living income gap (Paper 1).
Usage: python module_b_income_drivers.py <Household_Analysis_v1.csv> <Survey_Income_MI_v1.csv> <out_dir>
B1 composition: mean UGX/yr by source (cash Q162 by source + in-kind food + tree in-kind), by district and LI group.
B2 diversification: number of cash sources vs income ratio.
B3 drivers: OLS of log(income / household-size benchmark) with HC1 errors, run on each of the 20 imputations and
   pooled with Rubin's rules. M1 = structural characteristics; M2 = M1 + coffee yield and price (proximate);
   M3 = M1 with net income (net v1). Logit of reaching >= 50% of the benchmark as a check.
Associations only - not causal.
"""
import sys, os, numpy as np, pandas as pd, statsmodels.api as sm
sys.path.insert(0, os.path.dirname(__file__)); from li_style import *
h = pd.read_csv(sys.argv[1]); mi = pd.read_csv(sys.argv[2]); out = sys.argv[3]
os.makedirs(f"{out}/tables", exist_ok=True); os.makedirs(f"{out}/figures", exist_ok=True)
h["li_group"] = pd.Categorical(h.li_group, LI_GROUPS, ordered=True)

# ---------------- B1 composition
SRC_MAP = {"Coffee": ["inc_coffee_mi"], "Other crops": ["inc_othercrops_mi"], "Livestock": ["inc_livestock_mi"],
           "Non-farm work & business": ["inc_offfarm_mi", "inc_trade_mi", "inc_professional_mi"],
           "Remittances & other": ["inc_remittances_mi", "inc_other_mi"], "Home-grown food (in-kind)": ["inkind_food_central"],
           "Tree products used at home": ["tree_inkind"]}
for k, v in SRC_MAP.items(): h[k] = h[v].sum(axis=1)
S = list(SRC_MAP)
def comp(g):
    m = g[S].mean(); return pd.concat([m.rename("mean_UGX"), (m / m.sum() * 100).rename("share_%")], axis=1)
B1 = pd.concat({**{DIST_LABEL[k]: comp(g) for k, g in h.groupby("district")}, "All": comp(h)}, axis=1).round(1)
B1.to_csv(f"{out}/tables/B1_income_composition_by_district.csv")
B1g = pd.concat({g: comp(x) for g, x in h.groupby("li_group", observed=True)}, axis=1).round(1)
B1g.to_csv(f"{out}/tables/B1b_income_composition_by_li_group.csv")
# share of households earning anything from each cash source
part = h.groupby("district")[["inc_coffee_mi", "inc_othercrops_mi", "inc_livestock_mi", "inc_offfarm_mi", "inc_trade_mi",
                              "inc_professional_mi", "inc_remittances_mi", "inc_other_mi"]].agg(lambda s: (s > 0).mean() * 100).round(1).T
part.to_csv(f"{out}/tables/B1c_participation_by_source.csv")

fig, ax = plt.subplots(figsize=(7.2, 3.6))
rows = [("Mukono", h[h.district == "mukono"]), ("Nakaseke", h[h.district == "nakaseke"])] + [(f"Income {g} of benchmark", h[h.li_group == g]) for g in LI_GROUPS]
y = np.arange(len(rows))[::-1]
for yi, (lab, g) in zip(y, rows):
    m = g[S].mean(); m = m / m.sum() * 100; left = 0
    for j, s in enumerate(S):
        ax.barh(yi, m[s], left=left, color=SRC[j], height=0.62, edgecolor=SURF, linewidth=1.5, label=s if yi == y[0] else None)
        if m[s] >= 7: ax.text(left + m[s] / 2, yi, f"{m[s]:.0f}", ha="center", va="center", fontsize=7.5, color="white" if j in (0, 5, 6) else INK)
        left += m[s]
ax.set_yticks(y, [f"{lab}  (n={len(g)})" for lab, g in rows]); ax.set_xlim(0, 100); ax.grid(axis="y", visible=False)
ax.axhline(y[1] - 0.5, color=GRID, lw=1); ax.set_xlabel("% of mean household income")
ax.legend(ncol=4, loc="upper left", bbox_to_anchor=(0, -0.2), fontsize=7.5)
ax.set_title("The poorest rely on home-grown food, the better-off on coffee")
save(fig, f"{out}/figures/B1_income_composition.png")

# ---------------- B2 diversification
B2 = h.groupby(["district", "n_income_sources"]).agg(households=("gross", "size"), median_ratio_hh=("ratio_hh", "median"),
                                                     median_income=("gross", "median")).round(1)
B2.to_csv(f"{out}/tables/B2_diversification.csv")

# ---------------- B3 drivers
X_DEF = {  # label: column transform
    "Nakaseke (vs Mukono)": lambda d: (d.district == "nakaseke").astype(float),
    "log coffee area (acres)": lambda d: np.log(d.coffee_ac.clip(lower=0.1)),
    "log land owned (acres)": lambda d: np.log(d.land_owned_ac.clip(lower=0.1)),
    "Household size": lambda d: d.hh_size,
    "Female household head": lambda d: d.female_head,
    "Respondent secondary education+": lambda d: d.resp_edu_secondary_plus,
    "Respondent age (10 years)": lambda d: d.resp_age / 10,
    "Number of cash income sources": lambda d: d.n_income_sources_m,
    "Farmer group / project member": lambda d: d.group_member,
    "Extension contact": lambda d: d.extension_contact,
    "Credit access": lambda d: d.credit_access,
}
TREES = {"Trees on farm (log, +1) x Mukono": lambda d: np.log1p(d.trees_on_farm.clip(upper=2000)) * (d.district == "mukono"),
         "Trees on farm (log, +1) x Nakaseke": lambda d: np.log1p(d.trees_on_farm.clip(upper=2000)) * (d.district == "nakaseke")}
# district-specific tree slopes; tree counts of one Nakaseke enumerator set to missing (likely counted coffee bushes)
PROX = {"log coffee yield (kg FAQ/acre)": lambda d: np.log(d.coffee_yield_faq_ac.clip(lower=5)),
        "log Kiboko price (UGX/kg)": lambda d: np.log(d.kiboko_price)}
comps = [c for c in mi.columns if c.startswith("inc_")]

def rubin(est):
    """est: list of (params, cov) per imputation -> pooled table."""
    Q = pd.concat([e[0] for e in est], axis=1); U = pd.concat([pd.Series(np.diag(e[1]), e[0].index) for e in est], axis=1)
    m = Q.shape[1]; qbar = Q.mean(1); ubar = U.mean(1); b = Q.var(1, ddof=1); T = ubar + (1 + 1 / m) * b
    r = (1 + 1 / m) * b / ubar; df = (m - 1) * (1 + 1 / r) ** 2
    from scipy import stats
    t = qbar / np.sqrt(T); p = 2 * stats.t.sf(np.abs(t), df)
    fmi = ((1 + 1 / m) * b / T)
    return pd.DataFrame({"coef": qbar, "se": np.sqrt(T), "p": p, "fmi": fmi})

def run(model_vars, dep, logit=False):
    est, ns, r2 = [], [], []
    for k, g in mi.groupby("imputation"):
        d = h.merge(g[["_id", "income_total"] + comps], on="_id")
        d["n_income_sources_m"] = (d[comps] > 0).sum(axis=1)
        gross = d.income_total + d.inkind_food_central + d.tree_inkind
        d["dep"] = {"gross": np.log(gross / d.bench_hh_year), "net": np.log((gross - d.cost_central).clip(lower=0.05 * d.bench_hh_year) / d.bench_hh_year),
                    "reach50": (gross / d.bench_hh_year >= 0.5).astype(float)}[dep]
        X = pd.DataFrame({lab: f(d) for lab, f in model_vars.items()})
        ok = X.notna().all(1) & d.dep.notna()
        Xc = sm.add_constant(X[ok])
        fit = (sm.Logit(d.dep[ok], Xc).fit(disp=0, cov_type="HC1") if logit else sm.OLS(d.dep[ok], Xc).fit(cov_type="HC1"))
        est.append((fit.params, fit.cov_params().values)); ns.append(int(ok.sum())); r2.append(fit.prsquared if logit else fit.rsquared)
    t = rubin(est); return t, ns[0], float(np.mean(r2))

ENUM = {f"Enumerator: {e}": (lambda d, e=e: (d.enumerator == e).astype(float)) for e in sorted(h.enumerator.dropna().unique())
        if e != "Kisira_Isaac"}   # reference: Kisira (Mukono); district dummy dropped (nested)
M1 = X_DEF; M2 = {**X_DEF, **PROX}
res = {"M1 gross": run(M1, "gross"), "M2 + yield/price": run(M2, "gross"), "M3 + trees": run({**X_DEF, **TREES}, "gross"),
       "M4 net": run(M1, "net"), "M5 logit reach 50%": run(M1, "reach50", logit=True),
       "M6 + enumerator FE": run({**{k: v for k, v in X_DEF.items() if not k.startswith("Nakaseke")}, **ENUM}, "gross")}
def fmt(t):
    s = t.apply(lambda r: f"{r.coef:.3f}{'***' if r.p < .001 else '**' if r.p < .01 else '*' if r.p < .05 else '+' if r.p < .1 else ''} ({r.se:.3f})", axis=1)
    return s
B3 = pd.concat({k: fmt(v[0]) for k, v in res.items()}, axis=1)
B3.loc["n households"] = [str(v[1]) for v in res.values()]
B3.loc["mean (pseudo) R2 across imputations"] = [f"{v[2]:.3f}" for v in res.values()]
B3.to_csv(f"{out}/tables/B3_drivers_regression.csv")
pd.concat({k: v[0] for k, v in res.items()}).round(4).to_csv(f"{out}/tables/B3_drivers_regression_full.csv")
print(B3.to_string())

# Figure B3: coefficient plot, M1 gross (percent change in income-to-benchmark ratio)
t = res["M1 gross"][0].drop("const")
eff = (np.exp(t.coef) - 1) * 100; lo = (np.exp(t.coef - 1.96 * t.se) - 1) * 100; hi = (np.exp(t.coef + 1.96 * t.se) - 1) * 100
order = eff.sort_values().index
fig, ax = plt.subplots(figsize=(6.6, 4.2))
yy = np.arange(len(order))
sig = t.p[order] < 0.05
ax.hlines(yy, lo[order], hi[order], color=np.where(sig, DIST["mukono"], "#b9b8b3"), lw=2)
ax.scatter(eff[order], yy, s=36, color=np.where(sig, DIST["mukono"], "#b9b8b3"), edgecolor=SURF, linewidth=1.5, zorder=3)
ax.axvline(0, color=INK2, lw=1); ax.set_yticks(yy, order); ax.grid(axis="y", visible=False)
ax.set_xlabel("% change in income-to-benchmark ratio (95% CI)")
ax.set_title("What goes with a smaller living income gap")
save(fig, f"{out}/figures/B3_drivers_coefficients.png",
     f"OLS on log(income incl. in-kind / household-size benchmark), HC1 errors, pooled over 20 imputations (Rubin). n={res['M1 gross'][1]}. "
     "Blue = p<0.05. Log-area terms: % change per 1-unit change in log area (about a 2.7-fold increase).")
