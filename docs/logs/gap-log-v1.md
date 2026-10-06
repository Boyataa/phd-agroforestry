# Living income gap v1 (gross, incl. in-kind) — 2026-10-05
Script: data/build_income_gap.py. Benchmarks: rebuilt NFC_LW tool v0.02 (Mukono 20.17M, Nakaseke 19.78M UGX/yr, 2 adults + 3 children).
Income = Q162 a–h (12-month, PMM, 20 imputations, pooled) + home-consumed food (tool model diet x Nambooze 2025 own-farm shares; low 0.5x / central / high 1-bought) + non-food tree in-kind (firewood, poles, bark, leaves; capped at 95th pct = 2.04M, 3 HH capped; food tree products not added to avoid double counting).
## Pooled central results
| | Mukono | Nakaseke |
|---|---|---|
| n | 297 | 300 |
| median income incl. in-kind | 5.51M | 3.82M |
| median cash-only | 2.40M | 1.40M |
| % below reference benchmark | 92.6 | 97.6 |
| % below household-size benchmark | 93.9 | 95.5 |
| median income / benchmark | 27.3% | 19.3% |
| cash-only ratio | 11.9% | 7.1% |
| median gap (ref) | 14.65M | 15.96M |
| median gap (hh-specific) | 13.75M | 13.03M |
Low/high in-kind scenario: median ratio 20.5–29.2% (Mukono), 13.5–21.1% (Nakaseke).
## Caveats
In-kind food is a fixed fraction (~29% Mukono / ~27% Nakaseke) of tool food need, so depends on HH size, not farm output. Mpigi shares applied to both districts. 3 HH without district excluded; 11 with imputed children (district median); 4 without cropland get zero own food. Tree-product sales vs Q162 overlap not examined. Gross, not net of costs (net sensitivity pending).
