# Decisions log (Ezra, newest last). Complements `claude/project-brief.md`; fold into the brief at its next rewrite.

## 2026-10-05
- Two working data files, never merged: `data/Survey_Cleaned_v1.csv` (600 HH) and `data/Market_Prices_Tidy_v1.csv` (market prices).
- Recall periods: Q162 income = past 12 months (annual). Q163 seasonal coffee = per season; Q168/Q170 tree products = last season. Non-annual cost items must be converted to 12 months.
- 66 HH with seasonal coffee fields but no Q162a keep the plain seasonal sum (no ×acres).
- Main analysis uses gross income. **Net income (gross minus production costs, 12-month basis) = later sensitivity. REMIND EZRA.**
- Home-consumed food counts as income. Follow the benchmark tool, do not invent a new method: need from the tool's model diet (edible portion grams/day, quantity to purchase, adult-male equivalents), valued at district market prices. Tree products use Q170 quantity × market price.
- **Share of food supplied by own farm (Ezra reviewed two papers, 2026-10-05):** use food-group-specific shares from Nambooze et al. 2025, BMC Nutrition 11:216 (Mpigi district, 386 female smallholder farmers, Jan 2022, 7-day food frequency, share of consumption INSTANCES by source), Table 3. Own production / bought / other (gift, wild, others' garden, aid): fruits 85.0 / 8.5 / 6.5; tubers & roots (incl. plantain) 82.4 / 13.3 / 4.1; legumes, nuts & seeds 57.5 / 38.7 / 3.8; vegetables 42.6 / 49.6 / 7.8; eggs 38.0 / 59.2 / 2.8; milk & products 21.3 / 73.3 / 5.4; meat 11.8 / 85.5 / 2.6; cereals 9.9 / 81.9 / 8.2; sweets 1.7 / 96.0 / 2.3; fish 1.9 / 96.2 / 1.9; oils & fats 0.9 / 98.0 / 1.1. (Screenshot had tubers other 4.3 and meat other 2.7; paper gives 4.1 and 2.6.) The "70% of national food" line comes from Nalubowa et al. (Kampala farmers' markets paper): smallholders PRODUCE about 70% of Uganda's food; not a consumption share and not used.
  - Caveats: women of reproductive age, one district (Mpigi, closer to Mukono than Nakaseke), one season, shares of occasions not of quantity or value.
  - Proposed use (pending Ezra's OK): map each food in the tool's model diet to these groups; home food value = sum over groups of (model-diet cost of the group × household adult-male equivalents × 365 × own-production share); central = own-production share; low = half of it; high = all non-purchased share (own + gifts/wild/other).
- Nakaseke reference heights: use values similar to Mukono's (1.6 m / 1.5 m), replacing 2.2 / 2.0. (Applied in Nakaseke v0.02.)
- Local-unit market prices: Claude guessed kg/litre/piece equivalents, flagged as assumed (`data/Local_Unit_Guesses_v1.csv`, `data/Market_Prices_Tidy_v1_1.csv`, `data/local_unit_guesses.py`). 106 of 108 rows converted (72 low, 34 medium confidence). Ezra to review the factor table.
- Tool observations: model diet lists some foods twice (groundnuts, pineapple; doodo three times in Nakaseke) — not changed yet.

## Benchmark rebuild v0.02 (done 2026-10-05; logs in `data/benchmark-rebuild-log-<district>-v0.02.md`)
Household cost of decent living, 2 adults + 3 children, rural, UGX/month (workbooks are with Ezra; the project holds text only):
- **Mukono 1,680,564** (20.17M/yr): housing 153,005; food 713,711; NFNH 664,544; elder care 76,563; margins 72,741.
- **Nakaseke 1,648,277** (19.78M/yr): housing 211,247; food 643,882; NFNH 649,487; elder care 75,231; margins 68,430.
- Participants = 15 most complete households per district that also have all fields the tool needs (`data/*_participants_v1.csv`). Scripts: `data/build_participants.py`, `data/build_benchmark.py`, `data/xl_compat.py` (test copy that replaces XLOOKUP with INDEX/MATCH so LibreOffice can recalculate; reproduces v0.01 exactly).
- Formula fixes applied: stray ",1" in housing average; OUTPUT G31 USD margins; yearly table margins row. Left as in the tool: margins = 5% of food+NFNH+elder care (housing excluded) — question to Ezra still open.
- Assumptions to review: health cost column (labelled "visits" but holds amounts) treated as cost; eggs 1.8 kg per tray; secondary fee 5,500,000 read as 550,000; floor area: Mukono in m², Nakaseke rooms-based model estimate; roof/floor choice codes re-used by the form (floor 'wood' = soil).
- Items still at the tool's old prices (no usable market price): chapati, doughnut, pumpkin, green pepper, mpuuta, mukene, dried ngege, spinach, sukuma, spring onions, cabbage, watermelon, mangoes, pineapple, ghee, fats, drinks (+ yams in Nakaseke, fish in Mukono).

## Next steps agreed
1. ~~Rebuild district benchmarks~~ — done (v0.02, both districts).
2. Build annual household income (gross Q162 + home-consumed food and tree products at market prices).
3. Compute the household gap by district and source (Paper 1 first result). Open: gap per household as-is vs scaled to household size (adult-equivalents); plan to show both.
4. Later: net-income sensitivity (REMINDER), then SHAMBA scenarios.
