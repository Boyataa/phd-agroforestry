"""Net-income sensitivity for the living income gap (Paper 1). Companion to build_income_gap.py (gap v1, gross).
Usage: python build_net_income.py <Survey_Cleaned_v1.csv> <Survey_Income_MI_v1.csv> <out_dir>

Net income = gross income incl. in-kind (exactly as gap v1) - annual cash production costs (12-month basis).
Decisions (Ezra, 2026-10-05; see claude/decisions-log.md):
 1. Labour: the management-activity block records a WAGE RATE per work period, not the amount spent.
    Labour-days per acre per year come from the Fairtrade Living Income Reference Price for Robusta, Uganda
    (Oct 2022), Table 3: weeding 36, pest management 48, fertilisation 20, rejuvenation 48, harvest 50,
    post-harvest 45, replanting 2 (= 249 days/acre at a target 1,000 kg FAQ/acre).
    Day rates capped at 25,000 UGX (Fairtrade's daily rural living wage, same note).
 2. Only HIRED labour is a cost (Fairtrade/LI practice): an activity with a positive reported rate is hired;
    0 or missing = family labour, uncosted. Upper bound: all labour-days costed at the wage.
 3. Days scale with coffee acres; harvest and post-harvest also scale with yield / 1,000 kg FAQ per acre (cap 1).
 4. Mapping: weeding->weeding 36; pests_disease->pest mgmt 48; fertilization->fertilisation 20;
    harvesting->harvest 50 + post-harvest 45; in_season_management->rejuvenation 48; planting->replanting 2.
    Trenching/terracing, water & soil conservation and intercropping: no Fairtrade days -> left out.
 5. Period conversion to a day rate: daily x1, hourly x8, weekly /6, monthly /26.
    'annually' = amount spent on that activity per year -> added as is (not x days).
 6. Inputs (manure/compost, urea, NPK, DAP): cost per application x frequency (once a year 1, every season 2,
    more than three times a year 4). Low bound: cost as reported (x1).
 7. Land rent only for households that do not own their land (per season x2, per year x1, per month x12).
 8. Plot-level block: only seedlings, mulching, thinning (no overlap with the activity block); per season x2,
    bi-annually x2, annually x1; daily/weekly/monthly entries have no day count -> not used (counted).
 9. Coffee rehabilitation labour (Total_Labour_Cost) spread over its cycle (Rehabilitation_Cycle, years 1-30;
    otherwise district median cycle).
"""
import sys, math, re, numpy as np, pandas as pd

sv, mi_f, out = sys.argv[1:4]
d = pd.read_csv(sv, low_memory=False); mi = pd.read_csv(mi_f)
d["district"] = d["District"].str.lower()
num = lambda x: pd.to_numeric(x, errors="coerce")

# ======================================================================================
# A. Gross income incl. in-kind and benchmarks, as in build_income_gap.py (gap v1)
# ======================================================================================
slots = [("Details_of_household_members_gender_1", "Details_of_household_members_age_1", "Details_of_household_members_residential_status_1"),
         ("Details_of_household_members_gender_2", "Details_of_household_members_age_2", "Details_of_household_members_househead__residential_status_2")]
for r in ["row_3_1_1", "row1_4_1_1", "row_5_1_1", "row_6_1_1"]:
    p = f"SECTION_A/group_detailsofhhmembers_row_5/group_fd9pm11_{r}/group_fd9pm11_{r}_"; slots.append((p + "gender", p + "age", p + "residential_status"))
def comp(row):
    m = f = 0
    for g, a, rs in slots:
        if pd.isna(row.get(a)) or str(row.get(a)) == "6_15": continue
        if not str(row.get(rs)).startswith("resident"): continue
        if str(row.get(g)).startswith("male"): m += 1
        elif str(row.get(g)).startswith("female"): f += 1
    return pd.Series({"n_male": m, "n_female": f})
d = pd.concat([d, d.apply(comp, axis=1)], axis=1)
nog = (d.n_male + d.n_female) == 0
d.loc[nog, "n_female"] = np.where(d.loc[nog, "Gender_Sex"].astype(str).str.startswith("male"), 0, 1)
d.loc[nog, "n_male"] = np.where(d.loc[nog, "Gender_Sex"].astype(str).str.startswith("male"), 1, 0)
d["children_used"] = d["children_clean"].fillna(d.groupby("district")["children_clean"].transform("median")).round()

# Benchmark parameters. The v0.02 workbooks live with Ezra, so the tool parameters are solved from
# household values published in data/Household_Gap_v1.csv (food cost per adult man / woman / child,
# NFNH+housing via T = 1.0525*H + 1.1025*F*(1+k), H = ceil(size/2)*cost per room) and checked below.
ANCHOR = {  # district: (F for 0,1,0), (F for 1,0,0), (F for 0,1,2), (T for 0,1,0), (T for 1,1,3), f_central/F, f_high/F
    "mukono": (143794.368239151, 175358.985657501, 406832.846725403, 359824.56615789776, 1680564.056420399,
               3697162.47160089 / (1064429.0429410331 * 12), 4273302.946794584 / (1064429.0429410331 * 12)),
    "nakaseke": (129725.695892705, 158202.068161835, 367028.798135457, 361402.4830992099, 1648276.811268851,
                 2797306.9640710964 / (881185.51966142 * 12), 3176107.2809534557 / (881185.51966142 * 12))}
P = {}
for dist, (Ff, Fm, Ff2, T1, Tref, fcen, fhigh) in ANCHOR.items():
    cf, cm, cc = Ff, Fm, (Ff2 - Ff) / 2
    Fref = cm + cf + 3 * cc
    # T1 = 1.0525*1*cpr + 1.1025*Ff*(1+k);  Tref = 1.0525*3*cpr + 1.1025*Fref*(1+k)
    A = np.array([[1.0525, 1.1025 * Ff], [3 * 1.0525, 1.1025 * Fref]]); cpr, onek = np.linalg.solve(A, [T1, Tref])
    P[dist] = dict(cm=cm, cf=cf, cc=cc, cpr=cpr, onek=onek, f_cen=fcen, f_low=fcen / 2, f_high=fhigh)
def tool(dist, nm, nf, nc):
    p = P[dist]; size = nm + nf + nc
    H = math.ceil(size / 2) * p["cpr"]; F = p["cm"] * nm + p["cf"] * nf + p["cc"] * nc
    N = F * (p["onek"] - 1); E = 0.05 * (H + F + N); M = 0.05 * (F + N + E)
    return dict(F=F, T=H + F + N + E + M)
CHECK = [("mukono", 0, 1, 7, 2480939.3197069396), ("mukono", 2, 3, 3, 2719882.0706919637), ("nakaseke", 1, 2, 4, 2272444.525099997),
         ("nakaseke", 3, 1, 5, 3022739.549682472), ("nakaseke", 0, 5, 2, 2258430.3794609634)]
for dist, nm, nf, nc, T in CHECK:
    assert abs(tool(dist, nm, nf, nc)["T"] - T) < 1, (dist, nm, nf, nc, tool(dist, nm, nf, nc)["T"], T)

# tree products consumed at home (non-food), capped at the 95th percentile, as gap v1
rows = []
for i in range(3):
    pre = f"group_wz3xj67/group_ta7np61/{i}/group_wz3xj67/group_ta7np61/"
    g = lambda s_: d[pre + s_] if (pre + s_) in d else pd.Series(np.nan, index=d.index)
    price = num(g("_169_Farmgate_Price_f_the_selected_product")).fillna(num(g("Farmgate_Price_for_the_selected_product")))
    rows.append(pd.DataFrame({"_id": d["_id"], "product": g("Select_the_tree_product"), "year": num(g("Year_of_Harvest_001")),
                              "qty": num(g("Volume_Quatity_harvested")), "price": price, "cons": num(g("_170_If_part_of_the_h_is_comsumed_at_home"))}))
T_ = pd.concat(rows).dropna(subset=["product"]).sort_values("year").drop_duplicates(["_id", "product"], keep="last")
T_["cons"] = np.where(T_.qty.notna(), np.minimum(T_.cons, T_.qty), T_.cons)
T_["value"] = (T_.cons * T_.price).where(T_.cons.notna() & T_.price.notna(), np.nan)
tree = T_[~T_["product"].isin(["fruits", "roots", "Annuals", "Bananas"])].groupby("_id").value.sum(min_count=1)
d["tree_inkind"] = d["_id"].map(tree).fillna(0)
cap = d.loc[d.tree_inkind > 0, "tree_inkind"].quantile(0.95); d["tree_inkind"] = d.tree_inkind.clip(upper=cap)

coffee_ac = num(d["Size_used_for_Robusta_coffee"]).fillna(0)
d["has_cropland"] = (coffee_ac + num(d["size_used_for_Other_crops"]).fillna(0)) > 0
res = []
for _, r in d.iterrows():
    if r.district not in P: res.append(dict(_id=r["_id"])); continue
    t = tool(r.district, r.n_male, r.n_female, r.children_used); ref = tool(r.district, 1, 1, 3); p = P[r.district]
    res.append(dict(_id=r["_id"], bench_ref_year=ref["T"] * 12, bench_hh_year=t["T"] * 12,
                    **{f"inkind_food_{s_}": t["F"] * p[k_] * 12 * r.has_cropland
                       for s_, k_ in (("low", "f_low"), ("central", "f_cen"), ("high", "f_high"))}))
B = pd.DataFrame(res)

# ======================================================================================
# B. Production costs, 12-month basis
# ======================================================================================
FT_DAYS = {"weeding_1": 36, "pests_disease_management": 48, "fertilization": 20, "harvesting_1": 50 + 45,
           "in_season_management": 48, "planting_1": 2}
YIELD_SCALED = {"harvesting_1"}
NOT_COSTED = ["trenching_and_terracing", "water_and_soil_conservation", "intercropping"]
TO_DAY = {"daily": 1, "hourly": 8, "weekly": 1 / 6, "monthly": 1 / 26}

# yield (kg FAQ per acre): most recent harvest year 2020-2025, summed over plot records; Kiboko -> FAQ x 0.5
yr = []
for i in range(3):
    pre = f"group_wz3xj67/group_pw7lb76/{i}/group_wz3xj67/group_pw7lb76/"
    if pre + "Coffee_harvested_in_Kilograms" not in d: continue
    yr.append(pd.DataFrame({"_id": d["_id"], "year": num(d[pre + "Year_of_Harvest"]), "cat": d[pre + "Category_of_Coffee_Sold"],
                            "kg": num(d[pre + "Coffee_harvested_in_Kilograms"])}))
Y = pd.concat(yr).dropna(subset=["kg"]); Y = Y[Y.year.between(2020, 2025) & (Y.kg > 0)]
Y["faq"] = np.where(Y["cat"].astype(str).str.upper().str.startswith("FAQ"), Y.kg, Y.kg * 0.5)
Y = Y[Y.year == Y.groupby("_id").year.transform("max")].groupby("_id").faq.sum()
d["faq_kg"] = d["_id"].map(Y)
d["coffee_acres"] = coffee_ac
d["yield_faq_acre"] = (d.faq_kg / d.coffee_acres).where(d.coffee_acres > 0)
d["yield_ratio"] = (d.yield_faq_acre / 1000).clip(upper=1)
d["yield_ratio_imputed"] = d.yield_ratio.isna() & (d.coffee_acres > 0)
d["yield_ratio"] = d.yield_ratio.fillna(d.groupby("district").yield_ratio.transform("median"))

C = pd.DataFrame({"_id": d["_id"], "district": d["district"]})
day_rates, CAPPED = {}, []
DAY_RATE_CAP = 25000   # Fairtrade LIRP Uganda 2022 rural living wage per day (Ezra, 2026-10-05); 95th pct of reported rates = 20,000
for a, days in FT_DAYS.items():
    p = f"group_np5zx78_{a}/group_np5zx78_{a}_"
    per = d[p + "standard_work_period"].astype(str).str.lower(); rate = num(d[p + "estimated_cost_of_management_activity"])
    dr = rate * per.map(TO_DAY)                                   # wage per labour-day (NaN for 'annually')
    CAPPED.append(int((dr > DAY_RATE_CAP).sum())); dr = dr.clip(upper=DAY_RATE_CAP)
    day_rates[a] = dr
    eff_days = days * d.coffee_acres * (d.yield_ratio if a in YIELD_SCALED else 1)
    hired_rate = dr.where(dr > 0)
    C[f"lab_{a}"] = (hired_rate * eff_days).fillna(0) + rate.where((per == "annually") & (rate > 0)).fillna(0)
    # upper bound: all labour-days at the wage (household's own day rate, else district median day rate for the activity)
    med = dr.where(dr > 0).groupby(d.district).transform("median")
    rate_all = hired_rate.fillna(med)
    C[f"laball_{a}"] = np.where((per == "annually") & (rate > 0), rate, rate_all * eff_days)
    C[f"laball_{a}"] = C[f"laball_{a}"].fillna(0)
C["labour_hired"] = C.filter(regex="^lab_").sum(axis=1)
C["labour_all"] = C.filter(regex="^laball_").sum(axis=1)

FREQ = {"once_a_year": 1, "every_season": 2, "more_than_three_times_a_year": 4}
for f in ["organic_manure_compost_farmyard", "urea_1", "npk_1", "dap_1"]:
    cost = num(d[[c for c in d.columns if f in c and "estimated_cost" in c][0]])
    freq = d[[c for c in d.columns if f in c and "frequency_of_use" in c][0]].map(FREQ).fillna(1)
    C[f"inp_{f}"] = cost.where(cost > 0).fillna(0) * freq
    C[f"inplow_{f}"] = cost.where(cost > 0).fillna(0)
C["inputs"] = C.filter(regex="^inp_").sum(axis=1); C["inputs_low"] = C.filter(regex="^inplow_").sum(axis=1)

PLOT_PER = {"EverySeason": 2, "Bi-Annually": 2, "Annually": 1}
extra, rent, skipped = pd.Series(0.0, index=d.index), pd.Series(0.0, index=d.index), 0
non_owner = d["Does_the_respondent_own_the_land?"].eq("No")
RENT_PER = {"per_season": 2, "per_year": 1, "per_month": 12, "more_than_a_year": 1}
for i in range(7):
    p = f"group_wz3xj67/group_wj7zm87/{i}/group_wz3xj67/group_wj7zm87/"
    if p + "Select_a_a_management_Practice" in d:
        prac, per, c_ = d[p + "Select_a_a_management_Practice"], d[p + "Time_Period"], num(d[p + "Estimated_cost_amoun_elected_period_above"])
        sel = prac.isin(["Seedlings", "Mulching", "Thining"]) & (c_ > 0)
        skipped += int((sel & ~per.isin(PLOT_PER)).sum())
        extra += (c_ * per.map(PLOT_PER)).where(sel).fillna(0)
    if p + "Cost_of_farmland_in_n_shillings_if_hired" in d:
        h = num(d[p + "Cost_of_farmland_in_n_shillings_if_hired"]); dur = d.get(p + "Duration_of_hire_for_the_above_farmland")
        rent += (h * dur.map(RENT_PER).fillna(1)).where(non_owner & (h > 0)).fillna(0)
C["plot_extras"], C["land_rent"] = extra.values, rent.values

cyc = num(d["Rehabilitation_Cycle"]).where(lambda x: x.between(1, 30))
cyc = cyc.fillna(cyc.groupby(d.district).transform("median"))
C["rehab"] = (num(d["Total_Labour_Cost"]).where(lambda x: x > 0) / cyc).fillna(0).values

C["cost_central"] = C[["labour_hired", "inputs", "plot_extras", "land_rent", "rehab"]].sum(axis=1)
C["cost_low"] = C[["labour_hired", "inputs_low", "plot_extras", "land_rent", "rehab"]].sum(axis=1)
C["cost_all_labour"] = C[["labour_all", "inputs", "plot_extras", "land_rent", "rehab"]].sum(axis=1)
C = C.merge(d[["_id", "coffee_acres", "faq_kg", "yield_faq_acre", "yield_ratio", "yield_ratio_imputed"]], on="_id")
C.to_csv(f"{out}/Production_Costs_v1.csv", index=False)
print(f"day rates capped at {DAY_RATE_CAP}: {sum(CAPPED)}")
print(f"plot-block seedlings/mulching/thinning entries skipped (daily/weekly/monthly): {skipped}")
print(f"non-owners with rent: {int((C.land_rent > 0).sum())}; yield ratio imputed: {int(d.yield_ratio_imputed.sum())}")
dr_all = pd.concat(day_rates.values()); print("day-rate (hired) quantiles:", dr_all[dr_all > 0].quantile([.5, .9, .95, .99]).round().to_dict())

# ======================================================================================
# C. Net income gap (per imputation, pooled)
# ======================================================================================
H = d[["_id", "district", "tree_inkind"]].merge(B, on="_id").merge(C[["_id", "cost_central", "cost_low", "cost_all_labour"]], on="_id")
L = mi.merge(H, on="_id"); L = L[L.district.isin(P)]
L["gross"] = L.income_total + L.inkind_food_central + L.tree_inkind
SCEN = {"gross (gap v1)": None, "net central": "cost_central", "net low cost (inputs x1)": "cost_low", "net all labour costed": "cost_all_labour"}
def stat(g, inc):
    return pd.Series(dict(n=len(g), income_median=inc.median(), pct_below_ref=(inc < g.bench_ref_year).mean() * 100,
        pct_below_hh=(inc < g.bench_hh_year).mean() * 100, ratio_ref_median=(inc / g.bench_ref_year * 100).median(),
        gap_ref_median=(g.bench_ref_year - inc).median(), gap_hh_median=(g.bench_hh_year - inc).median(), pct_negative=(inc < 0).mean() * 100))
out_rows = []
for name, cc in SCEN.items():
    L["inc"] = L.gross - (L[cc] if cc else 0)
    s_ = L.groupby(["district", "imputation"]).apply(lambda g: stat(g, g.inc)).groupby("district").mean()
    s_["scenario"] = name; out_rows.append(s_.reset_index())
S = pd.concat(out_rows)[["scenario", "district", "n", "income_median", "ratio_ref_median", "pct_below_ref", "pct_below_hh", "gap_ref_median", "gap_hh_median", "pct_negative"]]
S.to_csv(f"{out}/Net_Gap_summary_v1.csv", index=False); print(S.round(1).to_string(index=False))

# cost composition (households with district), mean and median
cc_ = C[C.district.isin(P)]
comp_cols = ["labour_hired", "inputs", "plot_extras", "land_rent", "rehab", "cost_central", "cost_low", "cost_all_labour"]
CS = pd.concat({"mean": cc_.groupby("district")[comp_cols].mean(), "median": cc_.groupby("district")[comp_cols].median(),
                "share_HH_with_cost_%": cc_.groupby("district")[comp_cols].apply(lambda x: (x > 0).mean() * 100)}).round(0)
CS.to_csv(f"{out}/Net_Cost_components_v1.csv"); print(CS.to_string())

# household file (central, averaged over imputations)
hh = L.assign(inc=L.gross - L.cost_central).groupby("_id").agg(gross=("gross", "mean"), net_central=("inc", "mean")).reset_index()
hh = H.merge(hh, on="_id").merge(C[["_id", "labour_hired", "inputs", "plot_extras", "land_rent", "rehab", "coffee_acres", "yield_faq_acre", "yield_ratio"]], on="_id")
hh["cost_share_of_gross_%"] = hh.cost_central / hh.gross * 100
hh.to_csv(f"{out}/Household_Net_Gap_v1.csv", index=False)
print("median cost share of gross (%):", hh.groupby("district")["cost_share_of_gross_%"].median().round(1).to_dict())
