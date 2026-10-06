"""Household annual income (incl. in-kind) and living income gap, both districts.
Usage: python build_income_gap.py <Survey_Cleaned_v1.csv> <Survey_Income_MI_v1.csv> <recalc_dir> <out_dir>
 recalc_dir holds Mukono_v002_verify.xlsx / Nakaseke_v002_verify.xlsx recalculated by LibreOffice (see xl_compat.py).
Method (decisions of 2026-10-05, see claude/decisions-log.md):
 - income = gross annual income Q162 (12-month recall, imputed by PMM; 20 imputations) + in-kind
 - in-kind food = benchmark-tool model diet by food group x own-farm share (Nambooze et al. 2025, Table 3); low = 0.5 x own share,
   central = own share, high = 1 - bought share. Home-grown tree FOOD products are NOT added (covered by the diet-based value).
 - in-kind non-food = home-consumed tree products firewood, logs/poles, bark, leaves at farm-gate price (Q170 x Q169)
 - benchmark = the tool's household cost of decent living, reproduced for each household's composition
   (housing = ceil(size/2) rooms x cost per room; food by kcal-equivalents; NFNH = food x ratio; elder care 5%; margins 5%).
"""
import sys, math, re, numpy as np, pandas as pd, openpyxl
sv, mi_f, rc, out = sys.argv[1:5]
d = pd.read_csv(sv, low_memory=False); mi = pd.read_csv(mi_f)
d["district"] = d["District"].str.lower()
# ---------- household composition
slots = [("Details_of_household_members_gender_1","Details_of_household_members_age_1","Details_of_household_members_residential_status_1")]
slots.append(("Details_of_household_members_gender_2","Details_of_household_members_age_2","Details_of_household_members_househead__residential_status_2"))
for r in ["row_3_1_1","row1_4_1_1","row_5_1_1","row_6_1_1"]:
    p=f"SECTION_A/group_detailsofhhmembers_row_5/group_fd9pm11_{r}/group_fd9pm11_{r}_"; slots.append((p+"gender",p+"age",p+"residential_status"))
def comp(row):
    m=f=0
    for g,a,rs in slots:
        if pd.isna(row.get(a)) or str(row.get(a))=="6_15": continue
        if not str(row.get(rs)).startswith("resident"): continue
        if str(row.get(g)).startswith("male"): m+=1
        elif str(row.get(g)).startswith("female"): f+=1
    return pd.Series({"n_male":m,"n_female":f})
c = d.apply(comp, axis=1); d = pd.concat([d, c], axis=1)
d["adults"] = d.n_male + d.n_female
nog = d.adults == 0
d.loc[nog, "n_female"] = np.where(d.loc[nog, "Gender_Sex"].astype(str).str.startswith("male"), 0, 1); d.loc[nog, "n_male"] = np.where(d.loc[nog, "Gender_Sex"].astype(str).str.startswith("male"), 1, 0)
d["adults"] = d.n_male + d.n_female
d["children_used"] = d["children_clean"]; d["children_imputed_flag"] = d["children_used"].isna()
d["children_used"] = d["children_used"].fillna(d.groupby("district")["children_clean"].transform("median")).round()
d["hh_size"] = d.adults + d.children_used
# ---------- district parameters read from the recalculated workbooks
GROUP = [("rice|bread|doughnut|chapati|naan|spaghetti|maize|millet","Cereals"),("cassava|matooke|potato|yam|banana","Tubers & roots"),("groundnut|bean|peas|soy","Legumes, nuts & seeds"),
 ("yoghurt|youghurt|milk","Milk & milk products"),("butter|oil|ghee|fat|margarine","Oils & fats"),("egg","Eggs"),("beef|chicken|goat","Meat"),("ngege|mukene|fish|mpuuta","Fish"),
 ("sukuma|doodo|spring|bbuga|nakati|spinach|cabbage|tomato|onion","Vegetables"),("pine|mango|water|avocado","Fruits"),("soda|kombucha|juice","Sweets")]
SHARE = {  # Nambooze et al. 2025, Table 3: own production %, bought %
 "Cereals":(9.9,81.9),"Tubers & roots":(82.4,13.3),"Legumes, nuts & seeds":(57.5,38.7),"Milk & milk products":(21.3,73.3),"Oils & fats":(0.9,98.0),
 "Eggs":(38.0,59.2),"Meat":(11.8,85.5),"Fish":(1.9,96.2),"Vegetables":(42.6,49.6),"Fruits":(85.0,8.5),"Sweets":(1.7,96.0)}
def group_of(name):
    n = str(name).lower()
    # 'oil' check must not catch 'doodo'/'spinach'; order in GROUP list resolves this (cooking oil -> Oils)
    if re.search("cooking oil|butter|ghee", n): return "Oils & fats"
    for rx, g in GROUP:
        if re.search(rx, n): return g
    return None
P = {}
for dist, fn in (("mukono","Mukono_v002_verify.xlsx"),("nakaseke","Nakaseke_v002_verify.xlsx")):
    wb = openpyxl.load_workbook(f"{rc}/{fn}", data_only=True); f = wb["3. Food costs"]; b = wb["Background calculations"]; h = wb["2. Housing costs"]; o = wb["OUTPUT_Living wage"]
    items = [(f.cell(r,3).value, f.cell(r,6).value) for r in range(49,68) if f.cell(r,3).value]
    costs = {}
    for nme, pr in items:
        g = group_of(nme); assert g, nme; costs[g] = costs.get(g, 0) + float(pr)
    tot = float(f["D75"].value)
    cm, cf, cc = float(b["D134"].value), float(b["D135"].value), float(b["D136"].value)
    gcell = "G50" if dist == "mukono" else "G51"
    P[dist] = dict(cm=cm, cf=cf, cc=cc, ratio=float(b["D278"].value), post=float(b["C298"].value), cpr=float(h[gcell].value), diet=costs, diet_tot=tot,
                   ref=float(o["E33"].value))
    own = {k: SHARE[k][0] / 100 for k in costs}; bought = {k: SHARE[k][1] / 100 for k in costs}
    P[dist]["f_low"] = sum(costs[k] * 0.5 * own[k] for k in costs) / tot
    P[dist]["f_cen"] = sum(costs[k] * own[k] for k in costs) / tot
    P[dist]["f_high"] = sum(costs[k] * (1 - bought[k]) for k in costs) / tot
def tool(dist, nm, nf, nc):
    p = P[dist]; size = nm + nf + nc
    H = math.ceil(size / 2) * p["cpr"]; F = p["cm"] * nm + p["cf"] * nf + p["cc"] * nc
    N = F * p["ratio"] * (1 + p["post"]); E = 0.05 * (H + F + N); M = 0.05 * (F + N + E)
    return dict(H=H, F=F, N=N, E=E, M=M, T=H + F + N + E + M)
# self-check: the reference household must reproduce the workbook
for dist in P:
    t = tool(dist, 1, 1, 3); assert abs(t["T"] - P[dist]["ref"]) < 1, (dist, t["T"], P[dist]["ref"])
pd.DataFrame({k: {kk: vv for kk, vv in v.items() if kk != "diet"} for k, v in P.items()}).T.to_csv(f"{out}/benchmark_parameters.csv")
# ---------- tree products consumed at home (Q168-170)
rows = []
for i in range(3):
    pre = f"group_wz3xj67/group_ta7np61/{i}/group_wz3xj67/group_ta7np61/"
    g = lambda s: d[pre + s] if (pre + s) in d else pd.Series(np.nan, index=d.index)
    price = pd.to_numeric(g("_169_Farmgate_Price_f_the_selected_product"), errors="coerce").fillna(pd.to_numeric(g("Farmgate_Price_for_the_selected_product"), errors="coerce"))
    rows.append(pd.DataFrame({"_id": d["_id"], "product": g("Select_the_tree_product"), "year": pd.to_numeric(g("Year_of_Harvest_001"), errors="coerce"),
        "qty": pd.to_numeric(g("Volume_Quatity_harvested"), errors="coerce"), "price": price, "cons": pd.to_numeric(g("_170_If_part_of_the_h_is_comsumed_at_home"), errors="coerce")}))
T = pd.concat(rows).dropna(subset=["product"])
T = T.sort_values("year").drop_duplicates(["_id", "product"], keep="last")     # keep the most recent year per product
T["cons"] = np.where(T.qty.notna(), np.minimum(T.cons, T.qty), T.cons)         # cannot eat more than harvested
T["value"] = (T.cons * T.price).where(T.cons.notna() & T.price.notna(), np.nan)
T["food"] = T["product"].isin(["fruits", "roots", "Annuals", "Bananas"])
tree_nonfood = T[~T.food].groupby("_id").value.sum(min_count=1).rename("tree_inkind_nonfood")
tree_food_rec = T[T.food].groupby("_id").value.sum(min_count=1).rename("tree_food_recorded_not_added")
T.to_csv(f"{out}/tree_products_long.csv", index=False)
# ---------- farm indicator (no cropland -> no own-grown food)
farm = pd.to_numeric(d["Size_used_for_Robusta_coffee"], errors="coerce").fillna(0) + pd.to_numeric(d["size_used_for_Other_crops"], errors="coerce").fillna(0)
d["has_cropland"] = farm > 0
# ---------- household benchmarks
res = []
for _, r in d.iterrows():
    if r.district not in P: res.append(dict(_id=r["_id"])); continue
    t = tool(r.district, r.n_male, r.n_female, r.children_used); ref = tool(r.district, 1, 1, 3)
    p = P[r.district]
    res.append(dict(_id=r["_id"], bench_ref_month=ref["T"], bench_hh_month=t["T"], bench_hh_food_month=t["F"],
        inkind_food_low=t["F"] * p["f_low"] * 12 * r.has_cropland, inkind_food_central=t["F"] * p["f_cen"] * 12 * r.has_cropland, inkind_food_high=t["F"] * p["f_high"] * 12 * r.has_cropland))
B = pd.DataFrame(res)
H = d[["_id","district","n_male","n_female","adults","children_used","children_imputed_flag","hh_size","has_cropland"]].merge(B, on="_id", how="left") \
      .merge(tree_nonfood, on="_id", how="left").merge(tree_food_rec, on="_id", how="left")
H["tree_inkind_nonfood"] = H.tree_inkind_nonfood.fillna(0)
H["tree_inkind_nonfood_uncapped"] = H.tree_inkind_nonfood
cap = H.loc[H.tree_inkind_nonfood > 0, "tree_inkind_nonfood"].quantile(0.95)      # winsorise extreme records (e.g. 150 poles x 50,000 all eaten at home)
H["tree_inkind_capped_flag"] = H.tree_inkind_nonfood > cap; H["tree_inkind_nonfood"] = H.tree_inkind_nonfood.clip(upper=cap)
print("tree in-kind cap (95th pct of positive values):", round(cap), "| households capped:", int(H.tree_inkind_capped_flag.sum()))
H["bench_ref_year"] = H.bench_ref_month * 12; H["bench_hh_year"] = H.bench_hh_month * 12
# ---------- gaps per imputation
mi = mi.merge(H, on=["_id"], suffixes=("", "_h"))
comps = ["inc_coffee","inc_livestock","inc_offfarm","inc_remittances","inc_othercrops","inc_trade","inc_professional","inc_other"]
long = []
for scen in ("low", "central", "high"):
    x = mi.copy(); x["scenario"] = scen
    x["inkind_food"] = x[f"inkind_food_{scen}"]
    x["income_cash"] = x["income_total"]; x["income_total_all"] = x.income_cash + x.inkind_food + x.tree_inkind_nonfood
    for b in ("ref", "hh"):
        x[f"gap_{b}"] = x[f"bench_{b}_year"] - x.income_total_all
        x[f"gap_pct_{b}"] = x[f"gap_{b}"] / x[f"bench_{b}_year"] * 100
        x[f"ratio_{b}"] = x.income_total_all / x[f"bench_{b}_year"] * 100
        x[f"below_{b}"] = x.income_total_all < x[f"bench_{b}_year"]
        x[f"gap_cash_{b}"] = x[f"bench_{b}_year"] - x.income_cash
        x[f"ratio_cash_{b}"] = x.income_cash / x[f"bench_{b}_year"] * 100
    long.append(x)
L = pd.concat(long); L = L[L.district.isin(P)]
L.to_csv(f"{out}/Gap_long_v1.csv.gz", index=False, compression="gzip")
# ---------- household-level file: average over the 20 imputations, central scenario
c = L[L.scenario == "central"].groupby("_id").agg(income_cash=("income_cash","mean"), income_total_all=("income_total_all","mean"), gap_ref=("gap_ref","mean"), gap_hh=("gap_hh","mean"),
        ratio_ref=("ratio_ref","mean"), ratio_hh=("ratio_hh","mean"), imputed_any=("income_total","size")).reset_index().drop(columns="imputed_any")
HH = H.merge(c, on="_id", how="left"); HH.to_csv(f"{out}/Household_Gap_v1.csv", index=False)
# ---------- pooled summaries (statistic per imputation, then mean and range across the 20 imputations)
def stat(g):
    return pd.Series(dict(n=len(g), income_median=g.income_total_all.median(), income_cash_median=g.income_cash.median(),
        bench_ref_year=g.bench_ref_year.median(), bench_hh_median=g.bench_hh_year.median(),
        pct_below_ref=g.below_ref.mean() * 100, pct_below_hh=g.below_hh.mean() * 100,
        ratio_ref_median=g.ratio_ref.median(), ratio_hh_median=g.ratio_hh.median(), ratio_cash_ref_median=g.ratio_cash_ref.median(),
        gap_ref_median=g.gap_ref.median(), gap_hh_median=g.gap_hh.median()))
S = L.groupby(["scenario", "district", "imputation"]).apply(stat).reset_index()
pool = S.groupby(["scenario", "district"]).agg(["mean", "min", "max"]); pool.columns = ["_".join(c) for c in pool.columns]
pool = pool.drop(columns=[c for c in pool.columns if c.startswith("imputation") or c.startswith("n_min") or c.startswith("n_max")])
# income by source (mean per household, averaged over imputations) for the central scenario
cen = L[L.scenario == "central"]
src = cen.groupby(["district","imputation"])[comps + ["inkind_food","tree_inkind_nonfood","income_total_all"]].mean().groupby("district").mean().T
src["mukono_share_%"] = src["mukono"] / src.loc["income_total_all","mukono"] * 100; src["nakaseke_share_%"] = src["nakaseke"] / src.loc["income_total_all","nakaseke"] * 100
src.round(1).to_csv(f"{out}/Gap_by_source_v1.csv"); print(src.round(1).to_string())
pool.to_csv(f"{out}/Gap_summary_v1.csv"); print(pool.filter(regex="mean").round(1).T.to_string())
