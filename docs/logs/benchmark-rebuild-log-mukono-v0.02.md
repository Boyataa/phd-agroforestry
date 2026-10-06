# Mukono benchmark rebuild v0.02 (2026-10-05)

Workbook: `NFC_LW_Benchmark_Mukono_v0.02.xlsx` (all of the tool's formulas kept; inputs replaced; four clear formula fixes).
Open it in Excel: it recalculates on opening (values are not cached in the file).

## Result (reference household = 2 adults + 3 children, rural, 3,675 UGX/USD)
| Component | UGX / month | v0.01 (2+2, peri-urban) |
|---|---|---|
| Housing | 153,005 | 98,297 |
| Food | 713,711 | 648,048 |
| NFNH | 664,544 | 553,121 |
| Elder care (5%) | 76,563 | 64,973 |
| Margins (5%) | 72,741 | 63,307 |
| **Household cost of decent living** | **1,680,564** | 1,427,746 |
| Per year | 20,166,769 | 16,373,270 |

## What changed
1. Participants: the 15 most complete Mukono households (completeness = share of the original 461 answers filled), ids in `Mukono_participants_v1.csv`. Household size = resident adults + children (v0.01 had 4 for everyone).
2. Zone Rural; reference household 1 man + 1 woman + 3 children, 2 full-time workers.
3. Food prices: July 2025 Mukono market prices (outliers excluded because the tool prices the diet at the lowest observed price). Items without usable market prices keep the tool's values (see `Mukono_food_price_log_v0.02.csv`).
4. Formula fixes: housing average no longer includes the stray 1; OUTPUT G31 (USD margins) pointed to elder care; yearly table now has its own elder-care and margins rows and sums them.
5. Dropdowns lost when saving were re-created (E15 reference household; Nutritional input E112:E130). Some conditional-formatting colours on the food and nutrition sheets may be missing.

## Derivation rules for participant inputs (see `build_participants.py`)
- Rent = owner's estimated monthly rent; water = per-day cost x 30; cooking fuel = all energy sources (per day x30, per week x30/7); electricity = number in the Q34 free text.
- Education/month = (fees + materials per term) x children at the level x 3 terms / 12 (university: per semester x2/12). One secondary fee of 5,500,000 per term (HH 619306547) was treated as 550,000 (extra digit). One household had 25,000 children in primary (shifted entry) -> replaced by children minus other levels.
- Healthcare/month = spend in the last 3 months / 3. The column carrying it is labelled "number of visits" in the data but holds amounts (5,000-100,000) - treated as cost.
- Transport/month = cost x uses per month (everyday 30, twice 2, four times 4, more than 5 = 6).
- Decent housing flags use the tool's own standard. The form re-uses choice codes: roof 'bricks_blocks' = Iron sheet, 'mud_and_wattle_reeds' = Metal sheet, 'stone' = Tile; floor 'wood' = SOIL (not durable), 'bricks_blocks' = Wood, 'mud_and_wattle_reeds' = Tiles. Mixed answers count as durable only if every listed material is durable. Safe toilet = pit latrine with slab, VIP or flush. Safe water = borehole, piped or rain tank within 3 km. Electricity = grid or solar.
- 10 of 15 participants meet the tool's decent-housing standard.
- Floor area: Mukono values are in square metres (v0.01 had converted them from square feet).

## How it was checked
LibreOffice cannot evaluate XLOOKUP, so a test copy with XLOOKUP replaced by INDEX/MATCH was recalculated. On the original v0.01 inputs it reproduces every key figure exactly (housing 98,297; food 648,048; NFNH 553,121; total 1,427,746). The same method gives the v0.02 results above; the yearly total equals 12 x monthly.

## Open points for Ezra
- E31 'Margins' = 5% of food + NFNH + elder care (housing excluded); looks unintended but left as in the tool.
- Egg prices converted from tray prices assuming 1.8 kg per tray.
- Local-unit prices (cassava, yams, matooke, greens, sweet banana) are my guessed conversions.
- Items with no market price (fish, chapati, doughnut, pumpkin, cabbage, watermelon, mangoes, pineapple, drinks, spinach, sukuma, spring onions, ghee) keep the tool's old prices.
