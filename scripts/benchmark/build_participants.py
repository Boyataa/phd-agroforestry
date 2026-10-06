"""Select the 15 most complete Mukono households and derive the benchmark tool's participant inputs.
Run: python build_participants.py <Survey_Cleaned_v1.csv> <Standardized_Data.csv> <out.csv> [mukono|nakaseke]
Rules (all documented here; Ezra to confirm):
 - completeness = share of non-missing answers over the original Standardized_Data columns (Mukono only)
 - household size = resident adults (16+) + children_clean; FT/PT = work_type of resident adults
 - rent = owner's estimated monthly rent; water = per-day x 30; cooking fuel = sum of energy sources
   (per_day x30, per_week x30/7, per_month x1); electricity = number parsed from Q34 free text (monthly)
 - education/month = (fees+materials per term) x children at level x 3 terms /12 (university: per semester x2/12)
 - healthcare/month = 3-month spend /3 ; transport/month = cost x uses per month (everyday=30,twice=2,four=4,5+=6)
 - decent-housing flags follow the tool's own standard; NOTE the form reuses choice codes: roof 'bricks_blocks'=Iron sheet,
   'mud_and_wattle_reeds'=Metal sheet, 'stone'=Tile; floor 'wood'=SOIL, 'bricks_blocks'=Wood, 'mud_and_wattle_reeds'=Tiles."""
import sys, re, numpy as np, pandas as pd
sv, std, out = sys.argv[1:4]
district = sys.argv[4] if len(sys.argv) > 4 else "mukono"
d = pd.read_csv(sv, low_memory=False)
base = [c for c in pd.read_csv(std, nrows=0, low_memory=False).columns if c in d.columns]
m = d[d.District == district].copy()
m["completeness"] = m[base].notna().mean(axis=1)
rentc0="If_you_are_the_owner_of_the_house,_what_do_you_think_would_it_cost_to_rent_a_house_that_is_similar_to_this_one_in_this_village_Per_Month"
need=["Total_number_of_rooms","floor_area_m2" if district=="mukono" else "floor_area_m2_model",rentc0,"water_costs_per_day","energy_source_cost","children_clean","Gender_Sex","Age_of_Respondent_years","House_Walls","House_!Roof","House_Floor","Select_which_type_of_toile","Sources_of_Drinking_water"]
m["complete_for_tool"]=m[need].notna().all(axis=1)
# 15 most complete households among those that have every field the tool needs
m["completeness"]=m["completeness"].round(6)
top = m[m.complete_for_tool].sort_values(["completeness","_id"], ascending=[False,True]).head(15).copy()

def num(x):
    if pd.isna(x): return np.nan
    s = re.sub(r"(?<=\d),(?=\d{3})", "", str(x)); f = re.findall(r"\d+(?:\.\d+)?", s)
    return float(f[0]) if f else np.nan
def mid(a):
    f = re.findall(r"\d+", str(a))
    if len(f) >= 2: return (int(f[0]) + int(f[1])) / 2
    return 75 if f else np.nan
slots = [("Details_of_household_members_work_type_1","Details_of_household_members_age_1","Details_of_household_members_residential_status_1"),
 ("Details_of_household_members_work_type_2","Details_of_household_members_age_2","Details_of_household_members_househead__residential_status_2")]
for r in ["row_3_1_1","row1_4_1_1","row_5_1_1","row_6_1_1"]:
    p=f"SECTION_A/group_detailsofhhmembers_row_5/group_fd9pm11_{r}/group_fd9pm11_{r}_"
    slots.append((p+"work_type",p+"age",p+"residential_status"))
def comp(row):
    ad=ft=pt=0
    for w,a,rs in slots:
        if pd.isna(row.get(a)) or str(row.get(a))=="6_15": continue
        if not str(row.get(rs)).startswith("resident"): continue
        ad+=1; ft+=str(row.get(w)).startswith("full"); pt+=str(row.get(w)).startswith("part")
    return pd.Series({"adults":ad,"ft":ft,"pt":pt})
c = top.apply(comp, axis=1)
MULT = {"everyday":30,"twice":2,"four_times":4,"more_than_5_times":6}
def transport(row):
    tot=0
    for k,mean in [("private_motorcycle","private_motorcycle"),("public_motorcycle_boda_boda","public_motorcycle_boda_boda"),("bicycle_1","bicycle_1"),
                   ("public_taxi","public_taxi"),("private_car","private_car"),("other_1","other_1")]:
        cost=num(row.get([x for x in d.columns if x.endswith(f"group_iy5ab46_{mean}_cost")][0]))
        met=row.get([x for x in d.columns if x.endswith(f"group_iy5ab46_{mean}_frequency_metric")][0])
        fr=row.get([x for x in d.columns if x.endswith(f"group_ml8yl25_{mean}_frequency_of_use_per_month")][0]) if mean!="other_1" else None
        if pd.isna(cost): continue
        if met=="per_day": tot+=cost*MULT.get(str(fr),6)
        elif met=="per_week": tot+=cost*30/7
        elif met=="per_month": tot+=cost
    return tot
def edu(row):
    n=lambda k:num(row.get(k)); 
    def level(cnt,fee,mat,mult):
        c=n(cnt); f=n(fee); mt=n(mat)
        if pd.isna(c) or c<=0 or c>20: return 0
        mt=0 if (pd.isna(mt) or mt<100) else mt
        if mult!=2/12 and not pd.isna(f) and f>2_000_000: f=f/10   # 5,500,000 per term is an extra-digit typo (flagged in log)
        return c*((0 if pd.isna(f) else f)+mt)*mult
    k=level("SECTION_A/_49_Number_of_children_in_kind","SECTION_A/_53_Average_cost_of_Fees_ugx_per_term","SECTION_A/_54_Average_cost_of_rials_ugx_per_term",3/12)
    ncount=n("SECTION_A/_51_Number_of_children_in_elem")
    if ncount>20 or pd.isna(ncount): ncount=max(0,num(row["children_clean"])-sum(0 if pd.isna(n(x)) else n(x) for x in ["SECTION_A/_49_Number_of_children_in_kind","SECTION_A/_53_Number_of_children_in_high","SECTION_A/_55_Number_of_children_in_univ"]))
    row=row.copy(); row["SECTION_A/_51_Number_of_children_in_elem"]=ncount
    p=level("SECTION_A/_51_Number_of_children_in_elem","SECTION_A/_57_Average_cost_of_Fees_ugx_per_term","SECTION_A/_58_Average_cost_of_rials_ugx_per_term",3/12)
    s=level("SECTION_A/_53_Number_of_children_in_high","SECTION_A/_61_Average_cost_of_Fees_ugx_per_term","SECTION_A/_62_Average_cost_of_rials_ugx_per_term",3/12)
    u=level("SECTION_A/_55_Number_of_children_in_univ","SECTION_A/_65_Average_cost_of_s_ugx_per_semester","SECTION_A/_66_Average_cost_of_s_ugx_per_semester",2/12)
    return k+p+s+u
def fuel(row):
    tot=0
    pairs=[("energy_source_cost","unit_of_time_for_energy_source"),("energy_source_vs_cost","_energy_source_vs_unit_of_time"),
           ("5_energy_source_1_3_1_1_cost","5_energy_source_1_3_1_1_unit_of_time")]
    for cc,uu in pairs:
        cn=[x for x in d.columns if x.endswith(cc)]; un=[x for x in d.columns if x.endswith(uu)]
        v=num(row[cn[0]]) if cn else np.nan; u=row[un[0]] if un else None
        if pd.isna(v): continue
        tot+= v*{"per_day":30,"per_week":30/7,"per_month":1}.get(u,1)
    return tot
walls_ok={"cement","stone","bricks_blocks","wood"}; roof_ok={"cement","stone","bricks_blocks","mud_and_wattle_reeds"}; floor_ok={"cement","stone","bricks_blocks","mud_and_wattle_reeds"}
def allok(v,ok):
    t=[x for x in str(v).split() if x not in ("other","nan")]; return "Yes" if t and all(x in ok for x in t) else "No"
rentc="If_you_are_the_owner_of_the_house,_what_do_you_think_would_it_cost_to_rent_a_house_that_is_similar_to_this_one_in_this_village_Per_Month"
def km(x):
    v=num(x); return np.nan if pd.isna(v) else v
res=pd.DataFrame(index=top.index)
res["_id"]=top["_id"]; res["completeness"]=top["completeness"].round(3)
res["Age"]=top["Age_of_Respondent_years"].map(mid); res["Gender"]=top["Gender_Sex"].map({"male":"M","female":"F"})
res["Adults"]=c["adults"]; res["Children"]=top["children_clean"]; res["HHsize"]=res.Adults+res.Children
res["FT"]=c["ft"]; res["PT"]=c["pt"]
res["Rooms"]=top["Total_number_of_rooms"]; res["Area_m2"]=top["floor_area_m2"] if district=="mukono" else top["floor_area_m2_model"]   # Nakaseke: recorded area is unreliable (ft2), use the rooms-based model estimate
res["Rent"]=top[rentc].map(num)
res["Water"]=top["water_costs_per_day"]*30
elec=[x for x in d.columns if x.endswith("_32_If_you_have_elec_ch_do_you_pay_for_it")][0]
res["Electricity"]=top[elec].map(num).fillna(0)
res["CookingFuel"]=top.apply(fuel,axis=1)
h=[x for x in d.columns if "doctor/pharmacy_happened" in x][0]
res["Healthcare"]=(top[h].map(num)/3).fillna(0)
res["Education"]=top.apply(edu,axis=1); res["Transport"]=top.apply(transport,axis=1)
res["d_include"]="Yes"; res["d_walls"]=top["House_Walls"].map(lambda v:allok(v,walls_ok)); res["d_roof"]=top["House_!Roof"].map(lambda v:allok(v,roof_ok))
res["d_floor"]=top["House_Floor"].map(lambda v:allok(v,floor_ok))
res["d_toilet"]=top["Select_which_type_of_toile"].map(lambda v:"Yes" if v in ("inside","outside","flush_toilet") else "No")
def dist(v):
    """distance to water in km; Nakaseke answers are mostly metres ('200meters','500'), Mukono mostly km ('0.5','1km')."""
    x=num(v)
    if pd.isna(x): return np.nan
    t=str(v).lower()
    if "soccer" in t or "min" in t: return np.nan
    if "km" in t or "kilo" in t: return x
    if "m" in t: return x/1000
    return x if x<=20 else x/1000
res["d_water"]=[ "Yes" if (s in ("borehole","piped_water_system","rain_storage_in_tank") and (pd.isna(dist(dd)) or dist(dd)<3)) else "No" for s,dd in zip(top["Sources_of_Drinking_water"],top["DIstance_to_source_of_water"])]
res["d_cooking"]=[ "Yes" if str(k)=="No" or str(v)=="Yes" else "No" for k,v in zip(top["Is_your_kitchen_inside_the"],top["If cooking is inside, do you have a proper ventilation of smoke from cooking?"])]
res["d_electricity"]=["Yes" if (str(g)=="Yes" or "solar" in str(o)) else "No" for g,o in zip(top["Do_you_have_access_to_electricity"],top["Do_you_use_other_sources_of_electricity"])]
res["raw_walls"]=top["House_Walls"]; res["raw_roof"]=top["House_!Roof"]; res["raw_floor"]=top["House_Floor"]
res.to_csv(out,index=False); pd.set_option("display.width",250); print(res.drop(columns=["raw_walls","raw_roof","raw_floor"]).T.to_string())
