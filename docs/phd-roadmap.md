# PhD roadmap — agreed structure

_Agreed with Ezra on 2026-10-05. Replaces the broader scope in the March 2025 proposal._

## Decisions
- Thesis built around **three papers**, all using data already collected (socio-economic survey ~600 HH, July 2025 market survey, 18-plot SHAMBA tree survey).
- **DynACof dropped for now** (built for Arabica in Costa Rica; no Robusta physiological or multi-year yield data to calibrate it). Yield effects come from survey data and literature instead.
- **SHAMBA v1.2** used for carbon in scenario work.
- One scenario-modelling tool only (not Vensim + STELLA + Simulink). Web tool / RegenWorks integration / usability testing dropped or reduced to an optional appendix demonstration.

## Paper 1 — Living income gap of Robusta households in two agro-ecological zones
- **Question:** How large is the living income gap in Mukono and Nakaseke, and what drives it?
- **Data:** benchmark workbooks, market survey, socio-economic survey.
- **Method:**
  - Rebuild district benchmarks as **household** cost of decent living (not per-worker wage; no income tax).
  - Corrected inputs: actual household composition (~2 adults + 3 children), district market-survey food prices, survey imputed rent, rural zone, fixed formulas (height, margins row, housing average).
  - **Net** household income: all sources minus production costs, plus value of home-consumed produce.
  - Gap = benchmark − net income, in consistent units (per household per year, and per person per day).
  - Triangulate benchmark against published reference values for rural Uganda (Anker / Living Income Community of Practice).
  - Drivers of the gap: regression on land, coffee yield and price, income diversification, household characteristics, district.
- **Status:** data mostly ready; fastest paper.

## Paper 2 — Tree diversity, agroforestry type, coffee yield and household income
- **Question:** How are on-farm tree diversity and agroforestry configuration associated with coffee yield and household income?
- **Data:** socio-economic survey (trees on farm, tree products, coffee sales), SHAMBA plot survey, market prices.
- **Method:**
  - Classify farms by tree diversity (Shannon-Wiener: H′ = −Σ pᵢ ln pᵢ; not bounded 0–1; higher = more diverse) and/or species/configuration groups.
  - Value tree-product income (fruit, firewood, timber; sold and consumed) with market prices.
  - Regression controlling for confounders (land size, labour, farming experience, wealth proxies, district); consider propensity score matching. Report associations honestly unless identification supports causal claims.
  - Causal loop diagram as a conceptual synthesis, not a main result.
- **Fix from proposal:** Pearson r vs p-value confusion; Shannon-Wiener description.

## Paper 3 — Agroforestry scenarios for closing the living income gap
- **Question:** Which locally adoptable agroforestry scenarios are profitable and how much of the gap could they close?
- **Method:** farm-level bio-economic scenario model combining:
  - coffee yield effects (Paper 2 or literature),
  - tree-product revenues (market data),
  - carbon removals from **SHAMBA** (baseline vs project) and possible carbon-credit revenue,
  - establishment and labour costs.
  - Outputs: NPV, BCR (≥1 = cost effective), share of living income gap closed; base / best / worst cases; sensitivity to prices, discount rate, carbon price.
  - Feasibility check with farmers and experts using Franzel et al. (2002) criteria.
- **SHAMBA caveats to resolve:** tree ages derived from DBH (circular for growth curves); legume flags wrong for some species; "Nk003" plot ID in Mukono series.

## Thesis synthesis
Introduction + three papers + general discussion (policy: living income strategies, EU deforestation rules, certification, extension).

## Proposal clean-up for the thesis
- Citations that don't support claims (Bunn et al. 2019 for 2022 exports; "living income of 1.9 USD" confuses poverty line with living income).
- Report achieved samples (~300 per district vs 369/380 planned).
- Harmonise agro-ecological zone names (data: "Western Savannah Grassland" vs proposal: "Central Wooded Savanna").
- Define or drop "hyperlocal interventions" and "digital twins"; rewrite Research Question 3.

## Still to confirm
- Thesis format (paper-based?) and submission deadline.
- Supervisors' agreement to narrowed scope (DynACof, digital twins, web tool).
- Formal changes since proposal approval.
- Open data questions (income recall period, gross vs net, per-acre field, home consumption, missing incomes and outliers, source of tool food prices) — see project brief.
