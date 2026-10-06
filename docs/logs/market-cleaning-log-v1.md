# Market price survey — tidy file, version 1 (2026-10-05)

**Input:** `Cleaned Market Prices Survey.csv` (wide, 8 market visits × 486 item/vendor columns).
**Output:** `data/Market_Prices_Tidy_v1.csv` (665 rows, one per market visit × item × vendor slot with a price), built by `data/build_market_tidy.py`. The file is **not linked to the household survey** (no shared IDs, no shared columns).

## What the file contains
8 visits, 14–18 July 2025: Mukono (Kasawo rural, Nakifuma urban), Nakaseke (Kasangombe rural, Kiwoko urban), two visits per market. 49 items (food, plus soap, sanitary products, contraceptives and baby oil), up to 3 vendors per item.

| Column | Meaning |
|---|---|
| `visit_id`, `district`, `venue_type`, `market`, `location_number`, `survey_date`, `market_lat`, `market_lon` | Visit identifiers (market-level coordinates only). Enumerator name, e-mail and phone are not carried over. |
| `category`, `item`, `vendor_slot` | Questionnaire category, item, vendor 1–3 |
| `qty_text` | What the enumerator wrote about the quantity or brand (as recorded) |
| `quantity_amount`, `quantity_unit`, `unit_class` | Parsed amount and unit. `unit_class`: `mass` (kg), `volume` (litre), `count` (pieces), `item_unit` (pack, tray, bottle, carton, sachet), `local` (omulengo, pile, bunch, basin, cup...), `unknown` |
| `unit_note` | How the unit was obtained when it was not stated plainly (38 rows use the unit the questionnaire asked for) |
| `price_ugx` | Price as recorded, in UGX, for the stated quantity |
| `price_note` | Manual interpretations of free-text prices |
| `price_std`, `price_std_unit` | Standardised price: UGX per kg, per litre or per piece; or per pack / tray / bottle / carton / sachet. Empty for local units. |
| `outlier_flag` | Flagged if more than 3× or less than ⅓ of the item median (17 rows). Nothing was removed. |
| `comment` | Enumerator's comment |

## What was done
1. **Wide to long.** 54 questionnaire items × 3 vendor slots × 8 visits = 1,296 cells; the 631 empty slots (price 0, blank, or "." / "O" / "P") were dropped, leaving 665 rows.
2. **Prices to numbers.** Commas removed. Five free-text prices were handled by hand, per visit:
   - Kasangombe, banana, vendor 1: "5,000 small size" → 5,000.
   - Kasangombe, banana, vendor 2: "2 pcs at 500" → 500 for 2 pieces.
   - Kiwoko, banana, vendor 3: "20,000car brings them from Mbarara…" → 20,000.
   - Kasangombe, Irish potatoes, vendor 3: five different jerrycan prices in one text → left missing, text kept in the comment.
   - Kasangombe, onions, vendor 2: "100p" → left missing (implausible for 1 kg).
   - One fish price was text with no number → missing.
3. **Units parsed** from the quantity text ("500 grams", "1/2ltr", "4 pcs", "Half kg"). Where the text gave only a brand (e.g. "Lydia", "Softcare"), 1 of the questionnaire's unit was assumed and noted.
4. **Standardisation.** Mass, volume and count prices were converted to per kg, per litre or per piece (550 rows). Local units and items without a stated size were not converted.
5. **Checks.** The count of numeric prices matches an independent recount of the raw file (659 + 3 text prices); 40 random rows matched the raw cells; no duplicate keys.

## Things to know before using the prices
- **108 rows are in local units** (e.g. a pile of cassava, a bunch of matooke, a basin of tomatoes, an omulengo of onions). Kg conversion factors are needed to put these in the benchmark basket; this is a separate step.
- **Eggs are per tray**; tray size was not recorded (30 eggs is typical). Three Kasawo trays are priced at 1,100 UGX, probably 11,000.
- Other flagged values include one sanitary-pack price of 2 UGX and 4 tomatoes for 100 UGX.
- "Half grams" / "Quarter grams" for chicken (2 rows) and three milk brands without a size were not converted.
- The two visits per market were recorded on the same or neighbouring days; `location_number` is as recorded and is not consistent across visits.
- Median prices by district (UGX/kg unless stated), rice 3,850 vs 4,250, maize 2,550 vs 2,800, dried beans 3,800 vs 3,500, onions 2,500 vs 4,250, Irish potatoes 1,200 vs 2,000 (Mukono vs Nakaseke); cooking oil 7,000 vs 7,450 per litre. Very different from the benchmark tool, which used identical prices in the two districts.
