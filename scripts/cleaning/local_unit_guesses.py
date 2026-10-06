"""Assumed kg/litre/piece equivalents for local market units (GUESSES, to be checked by Ezra).
Usage: python local_unit_guesses.py Market_Prices_Tidy_v1.csv out_dir
Adds columns local_factor_guess, local_factor_unit, price_std_guess, guess_flag to the local-unit rows;
writes Market_Prices_Tidy_v1_1.csv and Local_Unit_Guesses_v1.csv (the factor table)."""
import sys, re, pandas as pd, numpy as np
src, out = sys.argv[1], sys.argv[2]
d = pd.read_csv(src)
# (item, regex on qty_text lowercase) -> (factor, out_unit, confidence); first match wins
R = [
 ("banana", r"3\s*ekiwagu", 4.5, "kg", "low"),
 ("banana", r"ki?wagu", 1.5, "kg", "low"),
 ("banana", r"bunch|enkota", 12, "kg", "medium"),
 ("sweet_banana", r"small", 0.5, "kg", "low"),
 ("sweet_banana", r"medium", 1.0, "kg", "low"),
 ("sweet_banana", r"abit big", 1.5, "kg", "low"),
 ("sweet_banana", r"ki?wagu|akawagu|ekiwagu|branch", 1.0, "kg", "low"),
 ("sweet_banana", r"bunch", 5, "kg", "low"),
 ("cassava", r"flour|batch", None, None, "unknown"),
 ("cassava", r"pile|omulengo", 2.0, "kg", "medium"),
 ("doodo", r"akakanda", 0.5, "kg", "low"),
 ("doodo", r"bundle|bunch", 0.3, "kg", "low"),
 ("nakati", r"akakanda", 0.5, "kg", "low"),
 ("nakati", r"bundle|bunch", 0.3, "kg", "low"),
 ("ebugga", r"akanwa|bundle|omulengo", 0.3, "kg", "low"),
 ("fresh_beans", r"basin", 5.0, "kg", "medium"),
 ("fresh_beans", r"cup", 0.5, "kg", "medium"),
 ("fresh_beans", r"omulengo", 1.0, "kg", "low"),
 ("irish_potatoes", r"ndebe", None, None, "unknown"),
 ("irish_potatoes", r"small pile|polythene", 0.5, "kg", "low"),
 ("irish_potatoes", r"small katasa", 1.5, "kg", "low"),
 ("irish_potatoes", r"medium katasa", 3.0, "kg", "low"),
 ("irish_potatoes", r"small mulengo", 1.5, "kg", "low"),
 ("irish_potatoes", r"medium", 2.5, "kg", "low"),
 ("irish_potatoes", r"big", 5.0, "kg", "low"),
 ("margarine", r"small tin", 0.2, "kg", "low"),
 ("milk", r"cup", 0.25, "litre", "medium"),
 ("yoghurt", r"cup", 0.25, "litre", "medium"),
 ("onions", r"ekigand", 2.5, "kg", "low"),
 ("onions", r"small", 0.2, "kg", "low"),
 ("onions", r"medium", 0.4, "kg", "low"),
 ("sweet_potatoes", r"pile|omulengo", 1.5, "kg", "medium"),
 ("tomatoes", r"6 bigfruits", 0.8, "kg", "low"),
 ("tomatoes", r"small basin", 4.0, "kg", "low"),
 ("tomatoes", r"plate", 0.7, "kg", "low"),
 ("tomatoes", r"akasero", 5.0, "kg", "low"),
 ("tomatoes", r"ekigandula", 10.0, "kg", "low"),
 ("tomatoes", r"omulengo", 0.4, "kg", "low"),
 ("yams", r"small basin|akatasa|katasa", 5.0, "kg", "low"),
 ("yams", r"pile", 3.0, "kg", "low"),
 ("avocado", r"omulengo", 3, "piece", "low"),
]
fac, un, conf = [], [], []
for _, r in d.iterrows():
    f = u = c = None
    if r.unit_class == "local":
        t = str(r.qty_text).lower()
        for it, rx, ff, uu, cc in R:
            if r["item"] == it and re.search(rx, t):
                f, u, c = ff, uu, cc; break
        if c is None: c = "unmatched"
    fac.append(f); un.append(u); conf.append(c)
d["local_factor_guess"] = fac; d["local_factor_unit"] = un; d["guess_flag"] = conf
ok = d.local_factor_guess.notna() & d.price_ugx.notna()
d["price_std_guess"] = np.where(ok, d.price_ugx / d.local_factor_guess.astype(float), np.nan)
# keep amount>1 consistent: price is for quantity_amount units
d.loc[ok & (d.quantity_amount.fillna(1) > 1), "price_std_guess"] = (d.price_ugx / (d.local_factor_guess.astype(float) * d.quantity_amount)).where(ok)
d.to_csv(f"{out}/Market_Prices_Tidy_v1_1.csv", index=False)
t = (d[d.unit_class == "local"].groupby(["item", "qty_text", "local_factor_guess", "local_factor_unit", "guess_flag"], dropna=False)
     .agg(n=("price_ugx", "size"), price_median=("price_ugx", "median"), implied_price_per_unit=("price_std_guess", "median")).reset_index())
t.to_csv(f"{out}/Local_Unit_Guesses_v1.csv", index=False)
print(d[d.unit_class == "local"].guess_flag.value_counts().to_dict())
