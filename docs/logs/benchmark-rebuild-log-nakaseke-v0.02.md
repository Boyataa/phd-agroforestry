# Nakaseke benchmark rebuild v0.02 (2026-10-05)

Workbook: `NFC_LW_Benchmark_Nakaseke_v0.02.xlsx` (tool formulas kept; inputs replaced; the same formula fixes as Mukono). Recalculates on opening in Excel.

## Result (reference household = 2 adults + 3 children, rural, 3,675 UGX/USD)
| Component | Nakaseke UGX / month | Mukono v0.02 | Nakaseke v0.01 (2+2, peri-urban, tall heights) |
|---|---|---|---|
| Housing | 211,247 | 153,005 | 76,891 |
| Food | 643,882 | 713,711 | 772,623 |
| NFNH | 649,487 | 664,544 | 599,498 |
| Elder care (5%) | 75,231 | 76,563 | 72,451 |
| Margins (5%) | 68,430 | 72,741 | 72,229 |
| **Household cost of decent living** | **1,648,277** | **1,680,564** | 1,593,691 |
| Per year | 19,779,322 | 20,166,769 | 18,257,554 |

## What changed (same as Mukono unless stated)
1. Participants: the 15 most complete Nakaseke households that also have every field the tool needs (rooms, area, rent, water, fuel, children, materials, toilet, water source). Ids in `Nakaseke_participants_v1.csv`. (Three of the very top households lacked rooms or rent and were skipped.) For Mukono this rule changes nothing.
2. Heights set to 1.6 m (men) / 1.5 m (women), as in Mukono (v0.01 had 2.2 / 2.0). Energy target is now 2,769 kcal (v0.01: ~4,030).
3. Zone Rural; reference household 1 man + 1 woman + 3 children, 2 full-time workers.
4. Food prices: July 2025 Nakaseke market prices (outliers excluded; guessed-unit prices below half of their median dropped, e.g. one matooke value of 250 per kg). Items without usable market prices keep the tool's old values (`Nakaseke_food_price_log_v0.02.csv`).
5. Formula fixes: stray ',1' in the housing average (G51 here), OUTPUT G31, yearly margins row.
6. Floor area: recorded Nakaseke areas were square feet and look unreliable, so the rooms-based model estimate (`floor_area_m2_model`) was used for the decent-housing space check.
7. Distance to water: Nakaseke answers are mostly in metres ("200meters", "500"); parsed with units (a first pass read them as km and failed everyone on safe water).
8. 12 of 15 participants meet the tool's decent-housing standard.

## Points to know
- NFNH post-check: reported education spending per child is about 10x the tool's calculated share, so the tool raises NFNH by 8.3% (+25%/3); transport and health are within range. In Mukono the factor is 0.
- Same assumptions as Mukono: health cost column treated as cost, eggs 1.8 kg per tray, guessed local-unit conversions, roof/floor choice codes re-used by the form.
- Items still at the tool's old prices: chapati, doughnut, yams, pumpkin, green pepper, mpuuta, mukene, dried ngege, spinach, sukuma, spring onions, cabbage, watermelon, mangoes, pineapple, ghee, fats, drinks (see food price log).

## Check
Original Nakaseke v0.01 reproduces exactly in the test copy (total 1,593,691). v0.02 recalculates without errors; yearly total = 12 x monthly; USD margins = UGX margins / 3,675.
