"""
Cleaning script for the Robusta coffee household survey (Mukono & Nakaseke, 2025).
(Copy of the Project version data/clean_survey.py, used to regenerate its outputs.)
Run:  python clean_survey.py <standardized.csv> <original_export.csv> <output_dir>
"""
import sys
import numpy as np
import pandas as pd

SEED = 20251005
M_IMPUTATIONS = 20
SQFT_TO_M2 = 0.09290304

std_path, orig_path, out_dir = sys.argv[1], sys.argv[2], sys.argv[3]
s = pd.read_csv(std_path, encoding="utf-8", low_memory=False)
o = pd.read_csv(orig_path, encoding="cp1252", low_memory=False).set_index("_id")
log = []


def num(x):
    return pd.to_numeric(x, errors="coerce")


def col(pattern, endswith=False):
    hits = [c for c in s.columns if (c.endswith(pattern) if endswith else pattern in c)]
    if len(hits) != 1:
        raise KeyError(f"{pattern!r} matched {hits}")
    return hits[0]


# 1. Repair Excel damage
s = s.copy()
ref = o.reindex(s["_id"])
for c in ["start", "end", "Date_Time"]:
    s[c] = ref[c].values
    log.append(("1 Excel repair", len(s), f"{c}: restored full ISO timestamp (+03:00) from KoBo export"))

s = s.rename(columns={"n and": "Age_of_Respondent_years"})
log.append(("1 Excel repair", 0, "Header 'n and' renamed back to Age_of_Respondent_years"))

AGE_BACK = {"5": "0_5", "615": "6_15", "1625": "16_25", "2640": "26_40", "4160": "41_60"}
age_cols = [c for c in s.columns if c.endswith(("_age_1", "_age_2", "_1_1_age"))]
for c in age_cols:
    before = s[c].copy()
    s[c] = s[c].map(lambda v: v if pd.isna(v) else AGE_BACK.get(str(v).replace(".0", ""), str(v)))
    log.append(("1 Excel repair", int((before.notna() & (before.astype(str) != s[c].astype(str))).sum()),
                f"{c[-40:]}: age-group codes restored (e.g. 4160 -> 41_60)"))

# 2. Children
kids_col = col("Children_ in_ the_ Household")
edu_cols = [c for c in s.columns if "Number_of_children_in" in c]
edu_sum = s[edu_cols].apply(num).sum(axis=1, min_count=1)
kids = num(s[kids_col])
s["children_clean"] = kids
s["children_flag"] = np.where(kids.notna(), "reported", "missing")

big = kids > 20
first_digit = kids[big].astype(int).astype(str).str[0].astype(float)
fix = np.where(first_digit >= edu_sum[big].fillna(0), first_digit, edu_sum[big])
s.loc[big, "children_clean"] = fix
s.loc[big, "children_flag"] = "keying_error_corrected"
for i in s.index[big]:
    log.append(("2 Children", 1, f"_id {s.at[i,'_id']}: {kids[i]:.0f} -> {s.at[i,'children_clean']:.0f} "
                                 f"(children in school = {edu_sum[i]:.0f})"))

fill = kids.isna() & edu_sum.notna()
s.loc[fill, "children_clean"] = edu_sum[fill]
s.loc[fill, "children_flag"] = "from_schooling_section"
log.append(("2 Children", int(fill.sum()), "missing child count filled with number of children in school"))

# 3. Floor area
area = num(s["Total_Surface_area_Square_Feet"])
dist = s["District"]
s["floor_area_m2"] = np.where(dist == "nakaseke", area * SQFT_TO_M2, area)
s["floor_area_flag"] = np.select(
    [area.isna(), dist == "mukono", dist == "nakaseke"],
    ["missing", "recorded_m2", "recorded_ft2_converted_low_reliability"], "no_district")
implaus = (s["floor_area_m2"] < 4) | (s["floor_area_m2"] > 400)
s.loc[implaus, "floor_area_flag"] = "implausible_set_missing"
s.loc[implaus, "floor_area_m2"] = np.nan
log.append(("3 Floor area", int(implaus.sum()), "implausible areas (<4 or >400 m^2) set to missing"))
log.append(("3 Floor area", int((dist == "nakaseke").sum()), "Nakaseke areas converted ft^2 -> m^2"))

rooms = num(s["Total_number_of_rooms"])
beds = num(s["Number_of_Bedrooms"])
X = pd.DataFrame({
    "rooms": rooms,
    "bedrooms": beds,
    "permanent": (s["Select_the_type_of_dwelling"] == "permanent_house").astype(float),
    "brick_walls": s["House_Walls"].astype(str).str.contains("brick|block|cement", case=False).astype(float),
    "cement_floor": s["House_Floor"].astype(str).str.contains("cement|tile|concrete", case=False).astype(float),
})
train = (dist == "mukono") & s["floor_area_m2"].notna() & X.notna().all(axis=1)
A = np.column_stack([np.ones(train.sum()), X[train].values])
beta, *_ = np.linalg.lstsq(A, np.log(s.loc[train, "floor_area_m2"].values), rcond=None)
resid_var = np.var(np.log(s.loc[train, "floor_area_m2"].values) - A @ beta)
pred_ok = X.notna().all(axis=1)
s["floor_area_m2_model"] = np.nan
s.loc[pred_ok, "floor_area_m2_model"] = np.exp(
    np.column_stack([np.ones(pred_ok.sum()), X[pred_ok].values]) @ beta + resid_var / 2)
log.append(("3 Floor area", int(pred_ok.sum()),
            f"floor_area_m2_model from Mukono log-linear model (n={int(train.sum())}); coefs "
            + ", ".join(f"{k}={v:.3f}" for k, v in zip(["const"] + list(X.columns), beta))))

# 4. Income
rng = np.random.default_rng(SEED)
SOURCES = {
    "_sale_of_robusta_coffee": "_162_a_Income_from_le_of_Robust",
    "__livestock": "_162_b_Income_from_Livestock",
    "off_farm_employment": "_162_c_Income_from_Off_farm",
    "__remittances": "_162_d_Income_from_Remittances",
    "sale_of_other_crops__specify": "_162_e_income_from_Sale_of",
    "trade": "_162_f_Income_from_Trade",
    "professional_or_white_collar_j": "_162_g_Professional",
    "other": "_162_h_income_form_other",
}
listed = s["group_wz3xj67/What_have_been_your_household_"].fillna("").str.split()
has_list = listed.str.len() > 0
seasonal = s[[c for c in s.columns if "group_wx41e92" in c]].apply(num).sum(axis=1, min_count=1)
land = num(s["What_is_the_total_land_he_she_owns"])
land = land.mask(land > 500)
AGE_MID = {"20-29": 25, "30-39": 35, "40-49": 45, "50-59": 55, "60-69": 65, ">=_70": 75}
age_mid = s["Age_of_Respondent_years"].map(AGE_MID)

inc = pd.DataFrame(index=s.index)
status = pd.DataFrame(index=s.index)
for tok, frag in SOURCES.items():
    c = col(frag)
    v = num(s[c])
    is_listed = listed.apply(lambda l: tok in l)
    st = pd.Series("observed", index=s.index)
    st[v.isna() & has_list & ~is_listed] = "zero_not_listed"
    v = v.mask(v.isna() & has_list & ~is_listed, 0.0)
    if tok == "_sale_of_robusta_coffee":
        use = v.isna() & seasonal.notna()
        v[use] = seasonal[use]
        st[use] = "from_seasonal_coffee_income"
    st[v.isna()] = "to_impute"
    st[v.isna() & ~has_list] = "no_source_info"
    inc[tok], status[tok] = v, st

coffee = inc["_sale_of_robusta_coffee"]
P = pd.DataFrame({
    "nakaseke": (dist == "nakaseke").astype(float),
    "log_land": np.log1p(land),
    "log_coffee": np.log1p(coffee),
    "children": s["children_clean"],
    "age": age_mid,
})
P = P.fillna(P.median())

draws = {tok: np.tile(inc[tok].values[:, None], (1, M_IMPUTATIONS)).astype(float) for tok in SOURCES}
for tok in SOURCES:
    need = (status[tok] == "to_impute").values
    if not need.any():
        continue
    donor = (status[tok] == "observed").values & (inc[tok].values > 0)
    y = np.log(inc[tok].values[donor])
    Xd = np.column_stack([np.ones(donor.sum()), P.values[donor]])
    Xm = np.column_stack([np.ones(need.sum()), P.values[need]])
    for m in range(M_IMPUTATIONS):
        bi = rng.integers(0, donor.sum(), donor.sum())
        b, *_ = np.linalg.lstsq(Xd[bi], y[bi], rcond=1e-6)
        yhat_d, yhat_m = Xd @ b, Xm @ b
        for j, idx in enumerate(np.where(need)[0]):
            nearest = np.argsort(np.abs(yhat_d - yhat_m[j]))[:5]
            draws[tok][idx, m] = np.exp(y[rng.choice(nearest)])
    log.append(("4 Income", int(need.sum()),
                f"{SOURCES[tok]}: PMM-imputed ({donor.sum()} donors, {M_IMPUTATIONS} imputations)"))

for tok in SOURCES:
    need = (status[tok] == "no_source_info").values
    if not need.any():
        continue
    donor = status[tok].isin(["observed", "zero_not_listed", "from_seasonal_coffee_income"]).values
    y = np.log1p(inc[tok].values[donor])
    Xd = np.column_stack([np.ones(donor.sum()), P.values[donor]])
    Xm = np.column_stack([np.ones(need.sum()), P.values[need]])
    for m in range(M_IMPUTATIONS):
        bi = rng.integers(0, donor.sum(), donor.sum())
        b, *_ = np.linalg.lstsq(Xd[bi], y[bi], rcond=1e-6)
        yhat_d, yhat_m = Xd @ b, Xm @ b
        for j, idx in enumerate(np.where(need)[0]):
            nearest = np.argsort(np.abs(yhat_d - yhat_m[j]))[:5]
            draws[tok][idx, m] = np.expm1(y[rng.choice(nearest)])
    status.loc[need, tok] = "imputed_PMM_no_source_list"
    log.append(("4 Income", int(need.sum()),
                f"{SOURCES[tok]}: source list unanswered -> PMM incl. zeros ({donor.sum()} donors)"))

for tok in SOURCES:
    n = int((status[tok] == "zero_not_listed").sum())
    if n:
        log.append(("4 Income", n, f"{SOURCES[tok]}: set to 0 (source not listed by household)"))
log.append(("4 Income", int((status["_sale_of_robusta_coffee"] == "from_seasonal_coffee_income").sum()),
            "coffee income taken from seasonal coffee sales (Kiboko + FAQ)"))

total_draws = sum(draws.values())
short = dict(zip(SOURCES, ["coffee", "livestock", "offfarm", "remittances",
                           "othercrops", "trade", "professional", "other"]))
for tok in SOURCES:
    s[f"inc_{short[tok]}_clean"] = np.nanmean(draws[tok], axis=1)
    s[f"inc_{short[tok]}_flag"] = status[tok].replace({"to_impute": "imputed_PMM"}).values
s["income_total_clean"] = np.nanmean(total_draws, axis=1)
s["income_any_imputed"] = status.isin(["to_impute", "imputed_PMM_no_source_list",
                                         "from_seasonal_coffee_income"]).any(axis=1)

mi = []
for m in range(M_IMPUTATIONS):
    d = pd.DataFrame({"_id": s["_id"], "District": dist, "imputation": m + 1})
    for tok in SOURCES:
        d[f"inc_{short[tok]}"] = draws[tok][:, m]
    d["income_total"] = total_draws[:, m]
    mi.append(d)
pd.concat(mi).to_csv(f"{out_dir}/Survey_Income_MI_v1.csv", index=False)

# 5. Save
s.to_csv(f"{out_dir}/Survey_Cleaned_v1.csv", index=False, encoding="utf-8")
pd.DataFrame(log, columns=["step", "rows_affected", "note"]).to_csv(f"{out_dir}/cleaning_log_v1.csv", index=False)
print("done", len(s))
