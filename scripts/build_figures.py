"""
RecovHR figure generation script.
Produces all figures used in the paper and website.

Requirements: pip install matplotlib numpy
Run from project root: python scripts/build_figures.py
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.ticker import MultipleLocator
import os

OUT = "figures"
os.makedirs(OUT, exist_ok=True)

# ── Shared style ────────────────────────────────────────────────────────────
FONT = "sans-serif"
INK  = "#1c1c1c"
INK2 = "#555555"
INK3 = "#999999"
RULE = "#ebebeb"
GREEN_DARK  = "#1a7335"
GREEN_MID   = "#2e7d45"
GREEN_LIGHT = "#e4f3e8"
ORANGE      = "#d97706"
RED         = "#b91c1c"

plt.rcParams.update({
    "font.family":      FONT,
    "axes.spines.top":  False,
    "axes.spines.right":False,
    "axes.spines.left": True,
    "axes.spines.bottom": True,
    "axes.edgecolor":   RULE,
    "axes.labelcolor":  INK2,
    "xtick.color":      INK3,
    "ytick.color":      INK3,
    "text.color":       INK,
    "figure.facecolor": "white",
    "axes.facecolor":   "white",
})

# ── Sample athlete ───────────────────────────────────────────────────────────
HR_MAX  = 188
HR_REST = 48
LTHR    = 163
HRR     = HR_MAX - HR_REST  # 140

def karvonen(frac):
    return round(HRR * frac + HR_REST)


# ═══════════════════════════════════════════════════════════════════════════
# Fig 1: Recovery Curve — HR dropping from peak toward threshold
# ═══════════════════════════════════════════════════════════════════════════
def fig1_recovery_curve():
    fig, ax = plt.subplots(figsize=(8, 4.5))

    t = np.linspace(0, 240, 500)

    # Exponential decay model: HR(t) = HRrest + (HRpeak - HRrest) * exp(-t/tau)
    HR_PEAK = 182
    TAU = 70  # recovery time constant (seconds)
    hr_curve = HR_REST + (HR_PEAK - HR_REST) * np.exp(-t / TAU)

    threshold_vo2  = karvonen(0.42)  # 107
    threshold_lt   = karvonen(0.50)  # 118
    threshold_speed= karvonen(0.35)  # 97

    # Find crossing times
    t_vo2   = TAU * np.log((HR_PEAK - HR_REST) / (threshold_vo2  - HR_REST))
    t_lt    = TAU * np.log((HR_PEAK - HR_REST) / (threshold_lt   - HR_REST))
    t_speed = TAU * np.log((HR_PEAK - HR_REST) / (threshold_speed - HR_REST))

    ax.plot(t, hr_curve, color=INK, lw=2.2, zorder=5, label="Heart rate")

    # Threshold lines
    ax.axhline(threshold_vo2,   color=GREEN_DARK,  lw=1.2, ls="--", alpha=0.9)
    ax.axhline(threshold_lt,    color=GREEN_MID,   lw=1.2, ls="--", alpha=0.9)
    ax.axhline(threshold_speed, color="#166530",   lw=1.2, ls="--", alpha=0.9)

    # Vertical crossing markers
    for t_cross, thresh, col in [
        (t_lt,    threshold_lt,    GREEN_MID),
        (t_vo2,   threshold_vo2,   GREEN_DARK),
        (t_speed, threshold_speed, "#166530"),
    ]:
        ax.plot([t_cross, t_cross], [HR_REST - 5, thresh], color=col,
                lw=1, ls=":", alpha=0.6)
        ax.scatter([t_cross], [thresh], color=col, s=40, zorder=6)

    # Labels
    ax.text(245, threshold_lt    + 1.5, f"LT  {threshold_lt} bpm",    fontsize=9, color=GREEN_MID,  ha="left", va="bottom")
    ax.text(245, threshold_vo2   + 1.5, f"VO2max  {threshold_vo2} bpm", fontsize=9, color=GREEN_DARK, ha="left", va="bottom")
    ax.text(245, threshold_speed + 1.5, f"Speed  {threshold_speed} bpm", fontsize=9, color="#166530",  ha="left", va="bottom")

    # Shade the sweet spot for VO2max
    ax.axvspan(t_vo2, t_vo2 * 1.55, alpha=0.07, color=GREEN_DARK,
               label="Optimal VO2max rest window")

    ax.set_xlim(0, 280)
    ax.set_ylim(HR_REST - 10, HR_PEAK + 8)
    ax.set_xlabel("Seconds of recovery", fontsize=10)
    ax.set_ylabel("Heart rate (bpm)", fontsize=10)
    ax.set_title("Heart rate recovery and RecovHR thresholds by workout type",
                 fontsize=11, fontweight="normal", color=INK, pad=12)

    ax.annotate("Effort ends", xy=(0, HR_PEAK), xytext=(14, HR_PEAK + 4),
                fontsize=8.5, color=INK3,
                arrowprops=dict(arrowstyle="->", color=INK3, lw=0.8))

    ax.xaxis.set_minor_locator(MultipleLocator(15))
    ax.yaxis.set_minor_locator(MultipleLocator(5))
    ax.tick_params(axis="both", which="major", labelsize=9)

    fig.tight_layout(pad=1.4)
    path = f"{OUT}/fig1_recovery_curve.png"
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)
    print(f"  saved {path}")


# ═══════════════════════════════════════════════════════════════════════════
# Fig 2: Workout type comparison — bar chart of thresholds
# ═══════════════════════════════════════════════════════════════════════════
def fig2_workout_comparison():
    fig, ax = plt.subplots(figsize=(8, 4.5))

    types     = ["SPEED", "VO2MAX", "EASY", "LT"]
    fractions = [0.35,     0.42,    0.38,   0.50]
    thresholds= [karvonen(f) for f in fractions]
    colors    = [GREEN_DARK, GREEN_DARK, GREEN_MID, GREEN_MID]
    alphas    = [0.55, 0.80, 0.65, 1.0]

    bars = ax.barh(types, thresholds, color=colors,
                   alpha=0.0, height=0.55)
    for bar, thresh, col, alpha in zip(bars, thresholds, colors, alphas):
        bar.set_facecolor(col)
        bar.set_alpha(alpha)

    # Value labels
    for bar, thresh in zip(bars, thresholds):
        ax.text(thresh + 1.5, bar.get_y() + bar.get_height() / 2,
                f"{thresh} bpm", va="center", fontsize=9.5, color=INK2)

    # HRmax reference line
    ax.axvline(HR_MAX, color=RED, lw=1.0, ls="--", alpha=0.5)
    ax.text(HR_MAX + 1, 3.55, f"HR max\n{HR_MAX}", fontsize=8, color=RED, ha="left")

    # HRrest reference line
    ax.axvline(HR_REST, color=INK3, lw=1.0, ls=":", alpha=0.7)
    ax.text(HR_REST + 1, 3.55, f"Rest\n{HR_REST}", fontsize=8, color=INK3, ha="left")

    ax.set_xlim(0, 215)
    ax.set_xlabel("Recovery target heart rate (bpm)", fontsize=10)
    ax.set_title(
        f"RecovHR recovery thresholds by workout type\n"
        f"Sample athlete: HRmax {HR_MAX}  |  HRrest {HR_REST}  |  HRR {HRR}",
        fontsize=10.5, fontweight="normal", color=INK, pad=12
    )
    ax.tick_params(axis="both", labelsize=9)
    ax.set_xlim(HR_REST - 5, HR_MAX + 20)

    fig.tight_layout(pad=1.4)
    path = f"{OUT}/fig2_workout_comparison.png"
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)
    print(f"  saved {path}")


# ═══════════════════════════════════════════════════════════════════════════
# Fig 3: Cardiac drift — threshold across 8 reps, with and without correction
# ═══════════════════════════════════════════════════════════════════════════
def fig3_cardiac_drift():
    fig, ax = plt.subplots(figsize=(8, 4.5))

    reps = np.arange(1, 9)
    base = karvonen(0.42)

    corrected   = [base if r < 3 else round(base + (r - 1) * 1.5) for r in reps]
    uncorrected = [base] * len(reps)

    ax.plot(reps, corrected, color=GREEN_DARK, lw=2.2, marker="o", ms=6,
            label="RecovHR (drift-corrected)")
    ax.plot(reps, uncorrected, color=INK3, lw=1.5, marker="o", ms=5,
            ls="--", label="Fixed threshold (no correction)")

    # Annotate gap at rep 8
    gap = corrected[-1] - uncorrected[-1]
    ax.annotate(
        f"+{gap:.0f} bpm\ncorrection at rep 8",
        xy=(8, corrected[-1]), xytext=(6.9, corrected[-1] + 3),
        fontsize=8.5, color=GREEN_DARK,
        arrowprops=dict(arrowstyle="->", color=GREEN_DARK, lw=0.8)
    )

    ax.set_xticks(reps)
    ax.set_xlabel("Repetition number", fontsize=10)
    ax.set_ylabel("Recovery threshold (bpm)", fontsize=10)
    ax.set_title(
        "Cardiac drift correction across an 8×400m VO2max session\n"
        "Without correction, late-rep rest periods extend by 45–75 seconds",
        fontsize=10.5, fontweight="normal", color=INK, pad=12
    )
    ax.legend(fontsize=9, frameon=False)
    ax.set_ylim(base - 5, corrected[-1] + 12)
    ax.tick_params(axis="both", labelsize=9)

    fig.tight_layout(pad=1.4)
    path = f"{OUT}/fig3_cardiac_drift.png"
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)
    print(f"  saved {path}")


# ═══════════════════════════════════════════════════════════════════════════
# Fig 4: HRR vs %HRmax — why Karvonen matters
# ═══════════════════════════════════════════════════════════════════════════
def fig4_karvonen_vs_pct():
    fig, ax = plt.subplots(figsize=(8, 4.5))

    hr_rests = [38, 48, 58, 68]
    frac = 0.42
    pct_hrmax = 0.65 * HR_MAX  # raw 65% HRmax

    karvonen_vals = [round((HR_MAX - r) * frac + r) for r in hr_rests]
    raw_vals      = [round(pct_hrmax)] * len(hr_rests)

    x = np.arange(len(hr_rests))
    w = 0.3

    b1 = ax.bar(x - w / 2, karvonen_vals, width=w, color=GREEN_DARK, alpha=0.85,
                label="RecovHR (Karvonen HRR × 0.42)")
    b2 = ax.bar(x + w / 2, raw_vals,      width=w, color=INK3,       alpha=0.55,
                label="Fixed 65% HRmax")

    for bar, val in zip(b1, karvonen_vals):
        ax.text(bar.get_x() + bar.get_width() / 2, val + 1,
                str(val), ha="center", fontsize=9, color=GREEN_DARK, fontweight="500")
    for bar, val in zip(b2, raw_vals):
        ax.text(bar.get_x() + bar.get_width() / 2, val + 1,
                str(val), ha="center", fontsize=9, color=INK3)

    ax.set_xticks(x)
    ax.set_xticklabels([f"HRrest = {r}" for r in hr_rests], fontsize=9)
    ax.set_ylabel("Recovery threshold (bpm)", fontsize=10)
    ax.set_title(
        f"Karvonen (HRR-based) vs. fixed %HRmax for VO2max recovery\n"
        f"All athletes: HRmax = {HR_MAX}. Raw 65% HRmax = {round(pct_hrmax)} bpm for everyone.",
        fontsize=10.5, fontweight="normal", color=INK, pad=12
    )
    ax.legend(fontsize=9, frameon=False)
    ax.set_ylim(80, 135)
    ax.tick_params(axis="both", labelsize=9)

    fig.tight_layout(pad=1.4)
    path = f"{OUT}/fig4_karvonen_vs_pct.png"
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)
    print(f"  saved {path}")


# ═══════════════════════════════════════════════════════════════════════════
# Fig 5: PCr resynthesis curve
# ═══════════════════════════════════════════════════════════════════════════
def fig5_pcr_kinetics():
    fig, ax = plt.subplots(figsize=(8, 4.5))

    t = np.linspace(0, 210, 500)
    TAU_PCR = 43.7  # seconds (Harris et al. 1976)
    pcr = (1 - np.exp(-t / TAU_PCR)) * 100

    ax.plot(t, pcr, color=GREEN_DARK, lw=2.2)
    ax.fill_between(t, pcr, alpha=0.08, color=GREEN_DARK)

    milestones = [(60, 75), (90, 87), (120, 93), (180, 97)]
    for t_m, pct in milestones:
        ax.plot([t_m, t_m], [0, pct], color=INK3, lw=1, ls=":")
        ax.scatter([t_m], [pct], color=GREEN_DARK, s=40, zorder=5)
        ax.text(t_m + 3, pct - 4, f"{pct}%\nat {t_m}s",
                fontsize=8.5, color=INK2)

    # RecovHR floors
    floor_vo2  = 90
    floor_speed= 120
    ax.axvline(floor_vo2,   color=GREEN_DARK, lw=1.3, ls="--", alpha=0.7)
    ax.axvline(floor_speed, color=GREEN_MID,  lw=1.3, ls="--", alpha=0.7)

    ax.text(floor_vo2   + 2, 5, "VO2max\nfloor", fontsize=8, color=GREEN_DARK)
    ax.text(floor_speed + 2, 5, "Speed\nfloor",  fontsize=8, color=GREEN_MID)

    ax.set_xlim(0, 215)
    ax.set_ylim(0, 102)
    ax.set_xlabel("Seconds post-effort", fontsize=10)
    ax.set_ylabel("PCr restored (%)", fontsize=10)
    ax.set_title(
        "Phosphocreatine resynthesis kinetics (Harris et al., 1976)\n"
        "Basis for RecovHR minimum clock floors",
        fontsize=10.5, fontweight="normal", color=INK, pad=12
    )
    ax.tick_params(axis="both", labelsize=9)

    fig.tight_layout(pad=1.4)
    path = f"{OUT}/fig5_pcr_kinetics.png"
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)
    print(f"  saved {path}")


if __name__ == "__main__":
    print("Building RecovHR figures...")
    fig1_recovery_curve()
    fig2_workout_comparison()
    fig3_cardiac_drift()
    fig4_karvonen_vs_pct()
    fig5_pcr_kinetics()
    print("Done. Figures saved to figures/")
