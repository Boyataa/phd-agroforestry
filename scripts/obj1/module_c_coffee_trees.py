"""Module C - coffee and trees versus the living income gap (Paper 1; bridge to Papers 2-3).
Usage: python module_c_coffee_trees.py <Household_Analysis_v1.csv> <Survey_Cleaned_v1.csv> <out_dir>
C1 coffee: area, yield (kg FAQ/acre; Kiboko x 0.5), Kiboko farm-gate price, coffee income, by district and LI group.
C2 closing the gap with coffee alone (standard LI 'levers' check, per household, gross):
   required coffee income = household benchmark - non-coffee income (incl. in-kind);
   required yield at current area and price; required FAQ price at current area and yield; required area at
   current yield and price. FAQ price = 2 x Kiboko price (same 0.5 conversion). Households already at the
   benchmark need 0 extra. Reported as median multiples of today's value.
C3 trees: tree products harvested in the latest year (Q168-170): household shares, value harvested, sold
   (harvest - home use) and used at home; trees on farm, tree origin and coffee system type by LI group.
   NB: survey Q162e is 'sale of other crops', not tree income (fixes the earlier notebook label).
"""
import sys, os, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(__file__)); from li_style import *
h = pd.read_csv(sys.argv[1]); sv = pd.read_csv(sys.argv[2], low_memory=False); out = sys.argv[3]
os.makedirs(f"{out}/tables", exist_ok=True); os.makedirs(f"{out}/figures", exist_ok=True)
h["li_group"] = pd.Categorical(h.li_group, LI_GROUPS, ordered=True)
num = lambda x: pd.to_numeric(x, errors="coerce")

# ---------------- C1
h["coffee_income"] = h.inc_coffee_mi
h["coffee_share_gross"] = h.coffee_income / h.gross * 100
C1v = {"coffee_ac": "Coffee area (acres)", "coffee_yield_faq_ac": "Yield (kg FAQ-equivalent/acre)", "kiboko_price": "Kiboko price (UGX/kg)",
       "coffee_income": "Coffee income (UGX/yr)", "coffee_share_gross": "Coffee share of income incl. in-kind (%)"}
def med_iqr(s):
    q = s.dropna().quantile([.25, .5, .75]); f = (lambda v: f"{v:.1f}") if q[.75] < 20 else (lambda v: f"{v:,.0f}")
    return f"{f(q[.5])} [{f(q[.25])}-{f(q[.75])}]"
C1 = pd.DataFrame({lab: {**{DIST_LABEL[k]: med_iqr(g[c]) for k, g in h.groupby("district")},
                         **{g: med_iqr(x[c]) for g, x in h.groupby("li_group", observed=True)}, "All": med_iqr(h[c]), "n": int(h[c].notna().sum())}
                   for c, lab in C1v.items()}).T
C1.to_csv(f"{out}/tables/C1_coffee_by_district_and_li_group.csv")
yld_ref = (h.coffee_yield_faq_ac >= 1000).groupby(h.district).mean() * 100

# ---------------- C2 levers
c = h.dropna(subset=["coffee_ac", "coffee_yield_faq_ac", "kiboko_price"]).query("coffee_ac > 0 and coffee_yield_faq_ac > 0").copy()
c["faq_price"] = 2 * c.kiboko_price
c["noncoffee"] = c.gross - c.coffee_income
c["need_coffee"] = (c.bench_hh_year - c.noncoffee).clip(lower=0)
cur = c.coffee_ac * c.coffee_yield_faq_ac * c.faq_price          # coffee value implied by yield x price (cross-check of Q162a)
c["implied_vs_reported"] = cur / c.coffee_income.where(c.coffee_income > 0)
c["need_yield"] = c.need_coffee / (c.coffee_ac * c.faq_price)
c["need_price"] = c.need_coffee / (c.coffee_ac * c.coffee_yield_faq_ac)
c["need_area"] = c.need_coffee / (c.coffee_yield_faq_ac * c.faq_price)
c["x_yield"] = c.need_yield / c.coffee_yield_faq_ac; c["x_price"] = c.need_price / c.faq_price; c["x_area"] = c.need_area / c.coffee_ac
def lever(g):
    return pd.Series({"households": len(g), "median yield now": g.coffee_yield_faq_ac.median(), "median yield needed": g.need_yield.median(),
        "median FAQ price now": g.faq_price.median(), "median FAQ price needed": g.need_price.median(),
        "median coffee acres now": g.coffee_ac.median(), "median acres needed": g.need_area.median(),
        "yield multiple (median)": g.x_yield.median(), "% needing yield <= 1,000 kg FAQ/acre": (g.need_yield <= 1000).mean() * 100,
        "% already at benchmark": (g.need_coffee == 0).mean() * 100, "implied/reported coffee income (median)": g.implied_vs_reported.median()})
C2 = pd.concat({**{DIST_LABEL[k]: lever(g) for k, g in c.groupby("district")}, "All": lever(c)}, axis=1).round(1)
C2.to_csv(f"{out}/tables/C2_coffee_levers_to_close_gap.csv")
print(C2.to_string()); print("share yield >= 1000:", yld_ref.round(1).to_dict())

fig, ax = plt.subplots(figsize=(6.4, 3.4))
for i, dname in enumerate(["mukono", "nakaseke"]):
    g = c[c.district == dname]; rng = np.random.default_rng(i)
    for j, (col, lab) in enumerate([("coffee_yield_faq_ac", "now"), ("need_yield", "needed")]):
        v = g[col].clip(lower=10, upper=20000); yy = i * 2.4 + j + rng.uniform(-0.2, 0.2, len(v))
        ax.scatter(v, yy, s=8, alpha=0.4, color=DIST[dname] if j == 0 else "#b9b8b3", linewidths=0)
        m = v.median(); ax.plot(m, i * 2.4 + j, "o", ms=7, color=INK, mec=SURF, mew=2)
        ax.text(m * 1.12, i * 2.4 + j + 0.33, f"{m:,.0f}", fontsize=8, color=INK)
ax.set_xscale("log"); ax.axvline(1000, color=INK2, lw=1, ls=(0, (4, 3)))
ax.text(1050, -0.55, "Fairtrade sustainable yield 1,000 kg FAQ/acre", fontsize=7.5, color=INK2, va="bottom")
ax.set_yticks([0, 1, 2.4, 3.4], ["Mukono: yield now", "Mukono: needed", "Nakaseke: yield now", "Nakaseke: needed"]); ax.grid(axis="y", visible=False)
ax.set_xlabel("kg FAQ-equivalent per acre (log scale; capped 10-20,000)"); ax.set_ylim(-0.7, 4.0)
ax.set_title("Coffee alone would need yields far above today's")
save(fig, f"{out}/figures/C2_yield_now_vs_needed.png", "Needed = yield that would close each household's gap at its current coffee area and price, other income unchanged. Circle = median.")

# ---------------- C3 trees
rows = []
for i in range(3):
    pre = f"group_wz3xj67/group_ta7np61/{i}/group_wz3xj67/group_ta7np61/"
    g = lambda s_: sv[pre + s_] if (pre + s_) in sv else pd.Series(np.nan, index=sv.index)
    price = num(g("_169_Farmgate_Price_f_the_selected_product")).fillna(num(g("Farmgate_Price_for_the_selected_product")))
    rows.append(pd.DataFrame({"_id": sv["_id"], "product": g("Select_the_tree_product"), "year": num(g("Year_of_Harvest_001")),
                              "qty": num(g("Volume_Quatity_harvested")), "price": price, "home": num(g("_170_If_part_of_the_h_is_comsumed_at_home"))}))
T = pd.concat(rows).dropna(subset=["product"]).sort_values("year").drop_duplicates(["_id", "product"], keep="last")
T["home"] = np.minimum(T.home, T.qty).where(T.qty.notna(), T.home)
T["value_harvest"] = T.qty * T.price; T["value_home"] = T.home * T.price; T["value_sold"] = (T.qty - T.home.fillna(0)).clip(lower=0) * T.price
T = T.merge(h[["_id", "district"]], on="_id")
NAMES = {"Bananas": "Bananas", "fruits": "Fruits", "firewood": "Firewood", "Annuals": "Annual crops", "roots": "Roots", "leaves": "Leaves", "Logs/Poles": "Logs/poles", "bark": "Bark"}
T["product"] = T["product"].map(NAMES).fillna(T["product"])
C3 = T.groupby(["district", "product"]).agg(households=("_id", "nunique"), with_quantity=("qty", lambda s: s.notna().sum()),
        median_value_harvest=("value_harvest", "median"), median_value_sold=("value_sold", "median"), median_value_home=("value_home", "median")).reset_index()
nh = h.groupby("district").size(); C3["% of households"] = (C3.households / C3.district.map(nh) * 100).round(1)
C3.round(0).to_csv(f"{out}/tables/C3_tree_products.csv", index=False)
anyp = T.groupby("district")._id.nunique() / nh * 100
tv = T.groupby("_id")[["value_sold", "value_home"]].sum(min_count=1)
h = h.merge(tv, left_on="_id", right_index=True, how="left")
C3b = pd.DataFrame({"% reporting any tree product": anyp.round(1),
                    "median value sold, reporters (UGX/yr)": h.groupby("district").value_sold.median().round(0),
                    "median value sold as % of cash income, reporters": (h.value_sold / h.income_total_mi * 100).groupby(h.district).median().round(1)})
C3b.to_csv(f"{out}/tables/C3b_tree_products_summary.csv")

h["origin"] = np.select([h.trees_planted_any == 1], ["planted (any)"], "remnant only")
C3c = pd.DataFrame({
    "median trees on farm": h.groupby("li_group", observed=True).trees_on_farm.median(),
    "median trees per acre": h.groupby("li_group", observed=True).trees_per_acre.median().round(1),
    "% system with trees": (h.groupby("li_group", observed=True).system_has_trees.mean() * 100).round(1),
    "% planted any trees": (h.groupby("li_group", observed=True).trees_planted_any.mean() * 100).round(1),
    "% removed trees": (h.groupby("li_group", observed=True).removed_trees.mean() * 100).round(1),
    "% reporting tree products": (h.groupby("li_group", observed=True).value_sold.apply(lambda s: s.notna().mean()) * 100).round(1)})
C3c.to_csv(f"{out}/tables/C3c_trees_by_li_group.csv")
# trees-on-farm terciles within district vs income ratio
h["tree_tercile"] = h.groupby("district").trees_on_farm.transform(lambda s: pd.qcut(s.rank(method="first"), 3, labels=["few", "middle", "many"]))
C3d = h.groupby(["district", "tree_tercile"], observed=True).agg(households=("ratio_hh", "size"), median_trees=("trees_on_farm", "median"),
        median_coffee_ac=("coffee_ac", "median"), median_yield=("coffee_yield_faq_ac", "median"), median_ratio_hh=("ratio_hh", "median"),
        median_ratio_net=("ratio_net_ref", "median")).round(1)
C3d.to_csv(f"{out}/tables/C3d_tree_terciles.csv")
print(C3b, C3c, C3d, sep="\n\n")
