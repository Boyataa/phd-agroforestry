# dwelling_analysis (tables only)
Source: `Generic Dataset Analysis.ipynb` (cell "IDENTIFY DWELLING VARIABLES"). Script: `scripts/morefigures/housing.py`.

- `dwelling_variables_inventory.csv` – every housing / water / energy / valuation variable used in the housing group, with answered count and number of distinct values per district (597-household sample).
- Changed vs old: the old version matched columns by keyword through a column dictionary on all 600 rows and wrote a raw extract (`dwelling_data.csv`). Now: fixed, documented variable list, analysis sample only (3 households without district dropped), split by district. The raw extract is not repeated (the data are in `data/derived/Survey_Cleaned_v1.csv`).
- Flags carried in the table: roof codes unusable (form re-used wall choices); recorded floor area is ft² in Nakaseke; enumerator "housing meets standard" judgement not comparable across districts.
