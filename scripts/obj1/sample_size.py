"""Cochran (1977) sample size and achieved margin of error for Paper 1, section 2.2."""
import math

Z, P, E = 1.96, 0.5, 0.05
N = {"Mukono": 9322, "Nakaseke": 7086}          # coffee-growing households, UBOS 2017
ACHIEVED = {"Mukono": 297, "Nakaseke": 300}     # analysed households

n0 = Z**2 * P * (1 - P) / E**2
print(f"n0 (no correction) = {n0:.1f}")
for d, pop in N.items():
    n = n0 / (1 + (n0 - 1) / pop)
    m = ACHIEVED[d]
    moe = Z * math.sqrt(P * (1 - P) / m * (pop - m) / (pop - 1))
    print(f"{d}: target n = {math.ceil(n)}; achieved {m} -> margin of error {moe:.1%}")
