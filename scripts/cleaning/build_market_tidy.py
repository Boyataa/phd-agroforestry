"""
Tidy the July 2025 market price survey (8 market visits, KoBo export).

Input : Cleaned Market Prices Survey.csv   (wide: one row per visit, 486 item/vendor columns)
Output: Market_Prices_Tidy_v1.csv          (long: one row per visit x item x vendor slot with a price)
        market_cleaning_log_v1.csv         (what was changed / interpreted)

Run: python build_market_tidy.py <input.csv> <output_dir>

Rules
 - Enumerator name, e-mail and phone are NOT carried over.
 - A vendor slot with price 0 / blank is "no vendor recorded" -> row dropped.
 - Prices are converted to numbers; 9 free-text prices are handled one by one and flagged.
 - The quantity text is parsed into amount + unit. Where the unit is a mass, volume or count the price is
   standardised (UGX per kg / litre / piece). Local units (omulengo, pile, bunch, basin, cup ...) are
   kept as stated and are NOT converted: price_std is empty and unit_class = 'local'.
 - Nothing is deleted for being an outlier; outliers are only flagged.
"""
import re
import sys
import numpy as np
import pandas as pd

src, out_dir = sys.argv[1], sys.argv[2]
m = pd.read_csv(src, encoding="utf-8", low_memory=False)
log = []

# ---------------------------------------------------------------- wide -> long
recs = []
for c in m.columns:
    if c.count("/") != 2:
        continue
    cat, g, leaf = c.split("/")
    kind = ("quantity" if re.search(r"(quantity|qty)", g, re.I) else
            "price" if re.search(r"price", g, re.I) else "comment")
    item = re.sub(r"^group_", "", g, flags=re.I)
    item = re.sub(r"_(qty_unit|quantity|price|comment)(_1)?$", "", item, flags=re.I).lower().strip("_")
    mm = re.search(r"vendor_brand_(\d)(?:_(\w+))?$", leaf, re.I)
    slot, form_unit = int(mm.group(1)), (mm.group(2) or "").lower()
    for i, v in m[c].items():
        recs.append((m.at[i, "_id"], cat, item, slot, form_unit, kind, v))
L = pd.DataFrame(recs, columns=["visit_id", "category", "item", "vendor_slot", "form_unit", "kind", "value"])
W = (L.pivot_table(index=["visit_id", "category", "item", "vendor_slot"], columns="kind",
                   values="value", aggfunc="first").reset_index())
fu = L.drop_duplicates(["category", "item", "vendor_slot"])[["category", "item", "vendor_slot", "form_unit"]]
W = W.merge(fu, on=["category", "item", "vendor_slot"], how="left")
W = W.rename(columns={"quantity": "qty_text", "price": "price_text", "comment": "comment"})
W.columns.name = None

meta = m.set_index("_id")
W["district"] = W.visit_id.map(meta["Name_of_the_District"])
W["venue_type"] = W.visit_id.map(meta["Type_of_Venue"])
W["market"] = W.visit_id.map(meta["Market_Name"]).str.title()
W["location_number"] = W.visit_id.map(meta["Location_Number"])
W["survey_date"] = pd.to_datetime(W.visit_id.map(meta["Date_of_Survey"]), format="%d/%m/%Y").dt.date
geo = meta["Select_Market_Geolocation"].str.split(expand=True).iloc[:, :2].astype(float)
W["market_lat"], W["market_lon"] = W.visit_id.map(geo[0]), W.visit_id.map(geo[1])
log.append(("wide->long", len(W), "1296 = 8 visits x 54 items x 3 vendor slots"))

# ---------------------------------------------------------------- prices
W["price_text"] = W.price_text.astype(str).str.strip()
manual = {  # (visit_id, item, slot) -> (price, flag)   -- keyed by visit, NOT by market (two visits per market)
    (519549331, "irish_potatoes", 3): (np.nan, "multiple prices for different jerrycan sizes in text; see comment"),
    (519549331, "banana", 1): (5000.0, "price read from '5,000 small size.'"),
    (519549331, "banana", 2): (500.0, "'2 pcs at 500': 500 UGX for 2 pieces (amount set to 2)"),
    (519970874, "banana", 3): (20000.0, "price read from start of free text ('20,000car brings them ...')"),
    (520289298, "onions", 2): (np.nan, "'100p' unparseable (implausible for 1 kg onions)"),
}
placeholder = {"0", "", "nan", ".", "o", "p"}
price, pflag = [], []
for _, r in W.iterrows():
    key = (int(r.visit_id), r["item"], r.vendor_slot)
    t = r.price_text
    if key in manual:
        p, f = manual[key]
    elif t.lower() in placeholder:
        p, f = np.nan, "no vendor"
    else:
        t2 = t.replace(",", "")
        if re.fullmatch(r"\d+(\.\d+)?", t2):
            p, f = float(t2), ""
        else:
            p, f = np.nan, "free text, no price: " + t[:60]
    price.append(p); pflag.append(f)
W["price_ugx"], W["price_note"] = price, pflag

# these rows had free text instead of a price, other than the placeholders and the manual cases
no_vendor = W.price_note.eq("no vendor")
log.append(("drop", int(no_vendor.sum()), "vendor slots with price 0 / blank / placeholder ('.', 'O', 'P') -> no vendor recorded"))
free = W.price_note.str.startswith("free text")
for _, r in W[free].iterrows():
    log.append(("price missing", 1, f"{r.district}/{r.market}/{r['item']}/slot{r.vendor_slot}: {r.price_text[:70]}"))
W = W[~no_vendor].copy()
for k, (p, f) in manual.items():
    row = W[(W.visit_id == k[0]) & (W["item"] == k[1]) & (W.vendor_slot == k[2])].iloc[0]
    log.append(("manual price", 1, f"{row.district}/{row.market}/{k[1]}/slot{k[2]}: {f}"))

# ---------------------------------------------------------------- quantity text -> amount + unit
FR = {"half": 0.5, "half a": 0.5, "a half": 0.5, "quarter": 0.25, "1/2": 0.5, "1/4": 0.25, "one": 1, "a": 1, "i": 1}
NUM = r"(?<![a-z])(\d+(?:\.\d+)?|\d/\d|half a|half|quarter|a half|one|an?|i)"
MASS = {"kg": 1.0, "kgs": 1.0, "kilo": 1.0, "kilos": 1.0, "kilogram": 1.0, "g": 0.001, "gm": 0.001, "gms": 0.001,
        "gram": 0.001, "grams": 0.001}
VOL = {"l": 1.0, "ltr": 1.0, "ltrs": 1.0, "litre": 1.0, "litres": 1.0, "liter": 1.0, "ml": 0.001, "mls": 0.001}
COUNT = r"(?:pc|pcs|piece|pieces|fruit|fruits|bar|chapati|egg|eggs|roots|avocado|mangoes|tomatoes)"


def val(s):
    s = s.strip().lower()
    return FR[s] if s in FR else (float(s.split("/")[0]) / float(s.split("/")[1]) if "/" in s else float(s))


def parse(item, form_unit, text):
    """return (amount, unit, unit_class, note)"""
    t = str(text).strip().lower().replace("  ", " ")
    if t in ("", "nan", "0"):
        return fallback(form_unit, "no quantity text")
    if re.search(r"socket|sachet", t):   # powdered-milk sachet: sold by the sachet, not by weight
        return (1.0, "sachet", "item_unit", "sachet; grams stated in text not used")
    # mass / volume with explicit number
    mt = re.search(NUM + r"\s*(kgs?|kilos?|kilograms?|grams?|gms?|gm|g)\b", t)
    if mt:
        kg = val(mt.group(1)) * MASS[mt.group(2) if mt.group(2) in MASS else re.sub(r"s$", "", mt.group(2))]
        if kg < 0.01:   # e.g. 'half grams' -> 0.5 g: obviously 'half kg'; do not guess
            return (np.nan, t[:40], "unknown", "ambiguous amount ('half grams'); not converted")
        return (kg, "kg", "mass", "")
    mv = re.search(NUM + r"\s*(litres?|ltrs?|ltr|liters?|mls?|l)\b", t)
    if mv:
        return (val(mv.group(1)) * VOL[mv.group(2)], "litre", "volume", "")
    mm = re.search(r"(\d+)\s*(?:ml|mls)\b", t)
    if mm:
        return (int(mm.group(1)) / 1000, "litre", "volume", "")
    if re.search(r"\bhalf (?:a )?litre\b", t):
        return (0.5, "litre", "volume", "")
    if re.search(r"\bhalf (?:a )?kilo\b|\bhalf kg\b", t):
        return (0.5, "kg", "mass", "")
    # bare unit words: use the amount 1 of the unit written
    if re.fullmatch(r"(kg|kgs|kilo|kg pack)( .*)?", t) or re.fullmatch(r".*\bkg\b.*", t) and "flour" in t:
        return (1.0, "kg", "mass", "bare 'kg' = 1 kg")
    if re.fullmatch(r"litre|ltr", t):
        return (1.0, "litre", "volume", "bare 'litre' = 1 litre")
    # counts
    mc = re.search(r"(\d+)\s*(?:small |big |medium )?" + COUNT, t)
    if mc:
        return (float(mc.group(1)), "piece", "count", "")
    if re.fullmatch(r"(an? |each |1 )?(pcs?|piece|fruit|full pc|bar of soap|whole chicken|chapati)", t) or \
       re.search(r"\b(a|1|each) (pc|piece|fruit|bar|chapati|egg)\b", t) or t in ("pc", "each pc", "each", "a pc", "a full pc"):
        return (1.0, "piece", "count", "")
    if re.search(r"\b1 bar\b|\ba bar\b|\bbar\b", t):
        return (1.0, "bar", "count", "")
    if "polythene" in t:                 # 'packed in white small polythene bag' is a local measure, not a pack
        return (np.nan, t[:40], "local", "local unit, not converted")
    if re.search(r"tray", t):
        return (1.0, "tray", "item_unit", "tray size not recorded (30 eggs typical)")
    if re.search(r"carto+n|atoon", t):
        return (1.0, "carton", "item_unit", "carton size not recorded")
    if re.search(r"pack(et|age)?|\bpac\b|strip|\bbox\b|packge", t):
        return (1.0, "pack", "item_unit", "pack size not recorded")
    if re.search(r"bottle", t):
        return (1.0, "bottle", "item_unit", "bottle size not recorded")
    if re.search(r"bunch|bundle|branch|kiwagu|ekiwagu|akawagu|omulengo|pile|pike|basin|katasa|akatasa|cup|ndebe|endebbe|plate|kigand|akasero|akakanda|akanwa|mulengo|jerrycan|polythene|\btin\b|enkota", t):
        return (np.nan, t[:40], "local", "local unit, not converted")
    if re.search(r"\bfish\b|whole chicken", t):
        return (1.0, "piece", "count", "")
    if re.search(r"small|medium|big|large", t):
        return (1.0, "piece", "count", "size class; 1 piece assumed")
    return fallback(form_unit, "text gives brand/descriptor only")


FORM_UNIT = {"kg": (1.0, "kg", "mass"), "litre": (1.0, "litre", "volume"), "pc": (1.0, "piece", "count"),
             "pack": (1.0, "pack", "item_unit"), "bottle": (1.0, "bottle", "item_unit"),
             "botle": (1.0, "bottle", "item_unit"), "tray": (1.0, "tray", "item_unit"),
             "bunch": (np.nan, "bunch", "local"), "batch": (np.nan, "batch", "local"), "tin": (np.nan, "tin", "local")}


def fallback(form_unit, why):
    """No usable unit in the text: assume 1 of the unit the questionnaire asked for."""
    if form_unit in FORM_UNIT:
        a, u, c = FORM_UNIT[form_unit]
        return (a, u, c, f"{why}; 1 {form_unit} assumed from questionnaire")
    return (np.nan, "", "unknown", why)


parsed = W.apply(lambda r: parse(r["item"], r.form_unit, r.qty_text), axis=1, result_type="expand")
W[["quantity_amount", "quantity_unit", "unit_class", "unit_note"]] = parsed
# manual: '2 pcs at 500' for bananas
mask = (W.district == "nakaseke") & (W.market == "Kasangombe") & (W["item"] == "banana") & (W.vendor_slot == 2)
W.loc[mask, ["quantity_amount", "quantity_unit", "unit_class"]] = [2.0, "piece", "count"]

# ---------------------------------------------------------------- standardised price
std_unit = {"mass": "kg", "volume": "litre", "count": "piece"}
W["price_std"] = np.where(W.unit_class.isin(std_unit) & W.quantity_amount.gt(0) & W.price_ugx.notna(),
                          W.price_ugx / W.quantity_amount, np.nan)
W["price_std_unit"] = np.where(W.price_std.notna(), W.unit_class.map(std_unit), "")
iu = W.unit_class.eq("item_unit") & W.price_ugx.notna()
W.loc[iu, "price_std"] = W.price_ugx[iu]
W.loc[iu, "price_std_unit"] = "per " + W.quantity_unit[iu]

# ---------------------------------------------------------------- outlier flag (not removed)
grp = W.groupby(["item", "price_std_unit"]).price_std
med = grp.transform("median"); n = grp.transform("count")
W["outlier_flag"] = np.where((n >= 5) & W.price_std.notna() & ((W.price_std > 3 * med) | (W.price_std < med / 3)),
                             "price_std >3x or <1/3 of item median", "")
log.append(("outliers", int((W.outlier_flag != "").sum()), "flagged only, none removed"))
log.append(("final", len(W), f"{W.price_ugx.notna().sum()} with a numeric price; {W.price_std.notna().sum()} standardised"))

cols = ["visit_id", "district", "venue_type", "market", "location_number", "survey_date", "market_lat", "market_lon",
        "category", "item", "vendor_slot", "qty_text", "quantity_amount", "quantity_unit", "unit_class", "unit_note",
        "price_ugx", "price_note", "price_std", "price_std_unit", "outlier_flag", "comment"]
W = W[cols].sort_values(["district", "market", "survey_date", "category", "item", "vendor_slot"]).reset_index(drop=True)
W.to_csv(f"{out_dir}/Market_Prices_Tidy_v1.csv", index=False, encoding="utf-8")
pd.DataFrame(log, columns=["step", "rows", "note"]).to_csv(f"{out_dir}/market_cleaning_log_v1.csv", index=False)
print(pd.DataFrame(log, columns=["step", "rows", "note"]).to_string(max_colwidth=120))
print(W.unit_class.value_counts().to_dict())
