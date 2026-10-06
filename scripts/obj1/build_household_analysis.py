"""Shared household analysis file for Paper 1 (Objective 1), one row per household.
Usage: python build_household_analysis.py <Survey_Cleaned_v1.csv> <Survey_Income_MI_v1.csv> <Household_Net_Gap_v1.csv> <out_dir>
Links every descriptive module to the living income results (gap v1 gross, central in-kind; net v1).
Income components are averaged over the 20 imputations here (for description only); regressions use the
imputations directly (see module_b_income_drivers.py).
"""
import sys, numpy as np, pandas as pd
sv, mi_f, net_f, out = sys.argv[1:5]
d = pd.read_csv(sv, low_memory=False); mi = pd.read_csv(mi_f); net = pd.read_csv(net_f)
num = lambda x: pd.to_numeric(x, errors="coerce")
d["district"] = d["District"].str.lower()
d = d[d.district.isin(["mukono", "nakaseke"])].copy()

# ---------- household members (same rules as the gap scripts: resident, age group known; 6_15 counted as child)
slots = [("Details_of_household_members_gender_1", "Details_of_household_members_age_1", "Details_of_household_members_residential_status_1", "Details_of_household_members_househead_relationship_1", "Details_of_household_members_educ_level_1"),
         ("Details_of_household_members_gender_2", "Details_of_household_members_age_2", "Details_of_household_members_househead__residential_status_2", "Details_of_household_members_househead_relationship_2", "Details_of_household_members_educ_level_2")]
for r in ["row_3_1_1", "row1_4_1_1", "row_5_1_1", "row_6_1_1"]:
    p = f"SECTION_A/group_detailsofhhmembers_row_5/group_fd9pm11_{r}/group_fd9pm11_{r}_"
    slots.append((p + "gender", p + "age", p + "residential_status", p + "househead_relationship", p + "educ_level"))
def members(row):
    m = f = elder = 0; head_g = head_age = head_edu = None
    for g, a, rs, rel, ed in slots:
        if pd.isna(row.get(a)): continue
        if str(row.get(rel)) == "house_head" and head_g is None:
            head_g, head_age, head_edu = row.get(g), row.get(a), row.get(ed)
        if str(row.get(a)) == "6_15" or not str(row.get(rs)).startswith("resident"): continue
        if str(row.get(g)).startswith("male"): m += 1
        elif str(row.get(g)).startswith("female"): f += 1
        if str(row.get(a)) == "61_and_above": elder += 1
    return pd.Series({"n_male": m, "n_female": f, "n_elder": elder, "head_gender": head_g, "head_age": head_age, "head_edu": head_edu})
d = pd.concat([d, d.apply(members, axis=1)], axis=1)
nog = (d.n_male + d.n_female) == 0
d.loc[nog, "n_female"] = np.where(d.loc[nog, "Gender_Sex"].astype(str).str.startswith("male"), 0, 1)
d.loc[nog, "n_male"] = np.where(d.loc[nog, "Gender_Sex"].astype(str).str.startswith("male"), 1, 0)
d["adults"] = d.n_male + d.n_female
d["children"] = d["children_clean"].fillna(d.groupby("district")["children_clean"].transform("median")).round()
d["hh_size"] = d.adults + d.children
d["dependency_ratio"] = (d.children + d.n_elder) / (d.adults - d.n_elder).clip(lower=1)
d["female_respondent"] = d.Gender_Sex.eq("female").astype(float).where(d.Gender_Sex.notna())
d["head_gender"] = d.head_gender.fillna(d.Gender_Sex)   # respondent assumed head when no member is coded head
d["female_head"] = d.head_gender.eq("female").astype(float).where(d.head_gender.notna())
AGE_MID = {"20-29": 25, "30-39": 35, "40-49": 45, "50-59": 55, "60-69": 65, ">=_70": 75}
d["resp_age"] = d["Age_of_Respondent_years"].map(AGE_MID)
EDU = {"non_formal": 0, "primary": 1, "seconary": 2, "vocational": 3, "college_university": 4}
d["resp_edu"] = d["Education_Level_of_respondent"].map(EDU)
d["resp_edu_secondary_plus"] = (d.resp_edu >= 2).astype(float).where(d.resp_edu.notna())
d["farming_years"] = num(d["Farming_experience_in_years"]).where(lambda x: x <= 80)
d["married"] = d.Marital_Status.eq("married").astype(float).where(d.Marital_Status.notna())

# ---------- land, coffee, trees, services
d["land_owned_ac"] = num(d["What_is_the_total_land_he_she_owns"]).mask(lambda x: x > 500)
d["coffee_ac"] = num(d["Size_used_for_Robusta_coffee"])
d["other_crops_ac"] = num(d["size_used_for_Other_crops"])
d["owns_land"] = d["Does_the_respondent_own_the_land?"].eq("Yes").astype(float).where(d["Does_the_respondent_own_the_land?"].notna())
d["land_tenure"] = d["If_yes_what_is_the_form_of_landownership"]
d["enumerator"] = d["Name_of_Enumerator_001"].str.replace(r"_\d+$", "", regex=True)
d["trees_on_farm"] = num(d["Ask_the_Farmer_for_Number_Trees_on_their_farm"])
# Namyenya (Nakaseke) recorded median 258 trees vs 5-17 for the other enumerators -> likely counted coffee bushes
# (Ezra, 2026-10-05): tree counts set to missing for her households; the rest of her data kept.
d["trees_count_unreliable"] = d.enumerator.eq("Namyenya_Lillian")
d.loc[d.trees_count_unreliable, "trees_on_farm"] = np.nan
d["trees_per_acre"] = (d.trees_on_farm / (d.coffee_ac.fillna(0) + d.other_crops_ac.fillna(0)).where(lambda x: x > 0))
sysv = d["group_vf5ln20/_84_Ask_the_respondent_for_the"].fillna("")
d["system_has_trees"] = sysv.str.contains("tree").astype(float).where(sysv != "")
d["system_has_banana"] = sysv.str.contains("banana").astype(float).where(sysv != "")
d["system_has_annuals"] = sysv.str.contains("annual").astype(float).where(sysv != "")
orig = d["_5_Ask_the_respondent_if_the_t"].fillna("")
d["trees_planted_any"] = orig.str.contains("planted|both").astype(float).where(orig != "")
d["removed_trees"] = d["_120_Have_you_removed_trees_in"].eq("Yes").astype(float)
d["credit_access"] = d["Do_you_have_access_to_credit_services"].eq("Yes").astype(float).where(d["Do_you_have_access_to_credit_services"].notna())
d["group_member"] = d["Are_you_currently_partici"].eq("Yes").astype(float).where(d["Are_you_currently_partici"].notna())
d["extension_contact"] = d["group_vf5ln20/_161_Are_you_in_touc_al_extension_officer"].eq("Yes").astype(float).where(d["group_vf5ln20/_161_Are_you_in_touc_al_extension_officer"].notna())
d["saves"] = d["group_to3ec88/Do_you_save_money_for_unexpect"].eq("Yes").astype(float).where(d["group_to3ec88/Do_you_save_money_for_unexpect"].notna())
d["sells_to_cooperative"] = d["group_wz3xj67/_168_How_did_you_sell_your_cof"].astype(str).str.contains("ooperative").astype(float)

# coffee harvest records: latest harvest year 2020-2025; Kiboko price per kg, FAQ-equivalent kg (Kiboko x 0.5, as net v1)
rec = []
for i in range(3):
    p = f"group_wz3xj67/group_pw7lb76/{i}/group_wz3xj67/group_pw7lb76/"
    if p + "Coffee_harvested_in_Kilograms" not in d: continue
    rec.append(pd.DataFrame({"_id": d["_id"], "year": num(d[p + "Year_of_Harvest"]), "cat": d[p + "Category_of_Coffee_Sold"].astype(str),
                             "kg": num(d[p + "Coffee_harvested_in_Kilograms"]), "price": num(d[p + "Farm_gate_price_UGX_per_Kg"])}))
R = pd.concat(rec); R = R[R.year.between(2020, 2025) & (R.kg > 0)]
R = R[R.year == R.groupby("_id").year.transform("max")]
R["faq"] = np.where(R["cat"].str.startswith("FAQ"), R.kg, R.kg * 0.5)
R["price_ok"] = R.price.where(R.price.between(1000, 20000))                 # >20,000/kg = totals keyed as prices
R["kib_price"] = R.price_ok.where(R["cat"] == "Kibooko")
agg = R.groupby("_id").agg(coffee_kg_faq=("faq", "sum"), coffee_kg_raw=("kg", "sum"), kiboko_price=("kib_price", "median"), harvest_year=("year", "max"))
d = d.merge(agg, left_on="_id", right_index=True, how="left")
d["coffee_yield_faq_ac"] = (d.coffee_kg_faq / d.coffee_ac).where(d.coffee_ac > 0)
d.loc[d.coffee_yield_faq_ac > 5000, "coffee_yield_faq_ac"] = np.nan     # > 5 t FAQ/acre impossible (e.g. 700,000) -> keying error

# ---------- income by source, averaged over imputations
comps = ["inc_coffee", "inc_livestock", "inc_offfarm", "inc_remittances", "inc_othercrops", "inc_trade", "inc_professional", "inc_other"]
inc = mi.groupby("_id")[comps + ["income_total"]].mean().add_suffix("_mi").reset_index()
d = d.merge(inc, on="_id", how="left")
d["n_income_sources"] = (mi.groupby("_id")[comps].mean() > 0).sum(axis=1).reindex(d["_id"]).values
farm = ["inc_coffee", "inc_livestock", "inc_othercrops"]
d["share_farm_cash"] = (d[[c + "_mi" for c in farm]].sum(axis=1) / d.income_total_mi.where(d.income_total_mi > 0))
d["share_coffee_cash"] = d.inc_coffee_mi / d.income_total_mi.where(d.income_total_mi > 0)

# ---------- living-income results (gap v1 gross central + net v1)
keep = ["_id", "bench_ref_year", "bench_hh_year", "inkind_food_central", "tree_inkind", "gross", "net_central", "cost_central"]
d = d.merge(net[keep], on="_id", how="left")
d["ratio_ref"] = d.gross / d.bench_ref_year * 100
d["ratio_hh"] = d.gross / d.bench_hh_year * 100
d["ratio_net_ref"] = d.net_central / d.bench_ref_year * 100
d["gap_ref"] = d.bench_ref_year - d.gross
d["below_ref"] = (d.gross < d.bench_ref_year).astype(float)
d["income_pc"] = d.gross / d.hh_size
bins = [-np.inf, 25, 50, 100, np.inf]; labels = ["<25%", "25-50%", "50-100%", ">=100%"]
d["li_group"] = pd.cut(d.ratio_hh, bins, labels=labels, right=False)   # household-size benchmark = fair comparison across sizes

cols = ["_id", "district", "Sub_County", "Parish", "enumerator", "trees_count_unreliable", "n_male", "n_female", "adults", "children", "children_imputed", "n_elder", "hh_size", "dependency_ratio",
        "female_respondent", "female_head", "head_age", "head_edu", "resp_age", "resp_edu", "resp_edu_secondary_plus", "married", "farming_years",
        "land_owned_ac", "coffee_ac", "other_crops_ac", "owns_land", "land_tenure", "trees_on_farm", "trees_per_acre", "system_has_trees", "system_has_banana",
        "system_has_annuals", "trees_planted_any", "removed_trees", "credit_access", "group_member", "extension_contact", "saves", "sells_to_cooperative",
        "coffee_kg_faq", "coffee_kg_raw", "coffee_yield_faq_ac", "kiboko_price", "harvest_year"] + [c + "_mi" for c in comps] + \
       ["income_total_mi", "n_income_sources", "share_farm_cash", "share_coffee_cash", "inkind_food_central", "tree_inkind", "gross", "cost_central", "net_central",
        "bench_ref_year", "bench_hh_year", "ratio_ref", "ratio_hh", "ratio_net_ref", "gap_ref", "below_ref", "income_pc", "li_group"]
d["children_imputed"] = d["children_clean"].isna()
d[cols].to_csv(f"{out}/Household_Analysis_v1.csv", index=False)
print(d.groupby("district")[["hh_size", "coffee_ac", "coffee_yield_faq_ac", "kiboko_price", "gross", "ratio_ref", "ratio_hh"]].median().round(1))
print(pd.crosstab(d.district, d.li_group, normalize="index").round(3) * 100)
