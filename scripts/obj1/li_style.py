"""Shared figure style and helpers for the Paper 1 analysis modules (reference palette, validated)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np, pandas as pd

DIST = {"mukono": "#2a78d6", "nakaseke": "#eb6834"}          # categorical slots 1-2 (validated adjacent + all-pairs)
DIST_LABEL = {"mukono": "Mukono", "nakaseke": "Nakaseke"}
ORD4 = ["#86b6ef", "#3987e5", "#1c5cab", "#0d366b"]          # ordinal blue ramp (steps 250, 400, 550, 700)
SRC = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"]  # fixed order
INK, INK2, GRID, SURF = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
LI_GROUPS = ["<25%", "25-50%", "50-100%", ">=100%"]

plt.rcParams.update({
    "figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF, "font.family": "DejaVu Sans", "font.size": 9,
    "axes.edgecolor": GRID, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2, "axes.titlesize": 10.5,
    "axes.titleweight": "bold", "axes.titlelocation": "left", "axes.titlecolor": INK, "axes.spines.top": False,
    "axes.spines.right": False, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "axes.axisbelow": True,
    "legend.frameon": False, "legend.fontsize": 8.5, "lines.linewidth": 2, "savefig.dpi": 300, "savefig.bbox": "tight"})

def money(x, pos=None):
    return "0" if x == 0 else f"{x/1e6:.0f}M" if abs(x) >= 1e6 else f"{x/1e3:.0f}k"

def save(fig, path, note=None):
    if note:
        fig.text(0.0, -0.02, note, fontsize=7.5, color=INK2, ha="left", va="top", wrap=True)
    fig.savefig(path); plt.close(fig)

def by_district(df, cols, how="mean"):
    g = df.groupby("district")[cols].agg(how).T
    g["all"] = df[cols].agg(how)
    return g
