# tree_species (old: Objective 2 notebook tree_spiecies.ipynb, figure `top_species`; no Objective 1 notebook)
| New figure | Shows |
|---|---|
| `top_species.png` (+ `top_species.csv`, `tree_species_records.csv`, `tree_species_name_normalisation.csv`) | Top 15 species by number of sites where recorded (split by district), and median trees per acre where present |

What changed and why
- The household survey (Survey_Cleaned_v1, 597 HH) has no species question. The only species columns in the repo are in the Dynacof/shamba site survey `data/raw/cleaned shamba Survey.csv` (18 coffee sites, repeat `grp_trees/rp_species/*/species_scientific`, 127 records). The old figure used `Dynacof Trees cleaned.csv` from Objective 2, which is not in the repo data. Results are for 18 sites and cannot be linked to the household sample or LI groups.
- Simple spelling normalisation only: whitespace/case, plus 13 obvious misspellings (e.g. Psdium -> Psidium, Anonna -> Annona, Papaya carica -> Carica papaya, Melicia -> Milicia, Jatropha carcus -> curcas, Griveillea -> Grevillea). The mapping is in the CSV. Full taxonomic cleaning is left to Objective 2.
- Site id 'Nk003' was surveyed on 07/01/2026 together with the Mukono sites (Nakaseke sites were surveyed in Sept 2025, and NK003 exists separately; MK003 is missing). It is treated as MK003 (Mukono). Please confirm.
