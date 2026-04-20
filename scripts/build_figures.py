"""
RecovHR figure generation — dark telemetry aesthetic.
Teal/blue lines on black-bean backgrounds.

Requirements: pip install matplotlib numpy
Run from project root: python3 scripts/build_figures.py
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import os

OUT = "figures"
os.makedirs(OUT, exist_ok=True)

# ── Palette ──────────────────────────────────────────────────────────────────
BG      = "#0d0002"       # near-black with red tint
BG2     = "#1a0404"       # slightly lighter panel bg
TEAL    = "#12BFBF"       # robin egg blue — primary data line
TEAL_D  = "#007F7F"       # deeper teal — secondary
RED     = "#CD0B0B"       # engineering red — warning / danger
DARK_R  = "#7A0000"       # barn red — reference lines
WHITE   = "#ffffff"
W60     = "#999999"  # not used in mpl directly
GRID    = "#1e0404"       # faint grid

def dark_style():
    plt.rcParams.update({
        "figure.facecolor":   BG,
        "axes.facecolor":     BG,
        "axes.edgecolor":     "#2a0808",
        "axes.labelcolor":    "#888888",
        "xtick.color":        "#666666",
        "ytick.color":        "#666666",
        "text.color":         WHITE,
        "grid.color":         "#200606",
        "grid.linewidth":     0.6,
        "axes.spines.top":    False,
        "axes.spines.right":  False,
        "axes.spines.left":   True,
        "axes.spines.bottom": True,
        "font.family":        "sans-serif",
        "axes.grid":          True,
    })

# Athlete profile
HR_MAX  = 188
HR_REST = 48
HRR     = HR_MAX - HR_REST   # 140

def karvonen(frac):
    return round(HRR * frac + HR_REST)


# ═══════════════════════════════════════════════════════════════════════════
# Fig 1 — Recovery curve
# ═══════════════════════════════════════════════════════════════════════════
def fig1_recovery_curve():
    dark_style()
    fig, ax = plt.subplots(figsize=(9, 5))
    fig.patch.set_facecolor(BG)

    t = np.linspace(0, 240, 600)
    HR_PEAK = 183
    TAU = 70
    hr = HR_REST + (HR_PEAK - HR_REST) * np.exp(-t / TAU)

    thr_vo2   = karvonen(0.42)   # 107
    thr_lt    = karvonen(0.50)   # 118
    thr_speed = karvonen(0.35)   # 97

    def t_cross(thr):
        return TAU * np.log((HR_PEAK - HR_REST) / (thr - HR_REST))

    tc_lt    = t_cross(thr_lt)
    tc_vo2   = t_cross(thr_vo2)
    tc_speed = t_cross(thr_speed)

    # Main HR curve
    ax.plot(t, hr, color=TEAL, lw=2.5, zorder=6)

    # Glow effect
    ax.plot(t, hr, color=TEAL, lw=8, alpha=0.08, zorder=5)

    # Threshold horizontals
    ax.axhline(thr_vo2,   color=TEAL_D,  lw=1.2, ls="--", alpha=0.8)
    ax.axhline(thr_lt,    color=TEAL,    lw=1.2, ls="--", alpha=0.6)
    ax.axhline(thr_speed, color="#005f5f", lw=1.2, ls="--", alpha=0.7)

    # Sweet spot shading (VO2max window)
    ax.axvspan(tc_vo2, tc_vo2 * 1.55, alpha=0.07, color=TEAL)

    # Crossing dots
    for tc, thr, col in [(tc_lt, thr_lt, TEAL), (tc_vo2, thr_vo2, TEAL_D), (tc_speed, thr_speed, "#005f5f")]:
        ax.scatter([tc], [thr], color=col, s=55, zorder=8, linewidths=0)
        ax.plot([tc, tc], [HR_REST - 8, thr], color=col, lw=0.8, ls=":", alpha=0.5)

    # Labels
    ax.text(248, thr_lt    + 1.5, f"LT  {thr_lt} bpm",    fontsize=9,  color=TEAL,    ha="left", va="bottom")
    ax.text(248, thr_vo2   + 1.5, f"VO2max  {thr_vo2} bpm", fontsize=9, color=TEAL_D,  ha="left", va="bottom")
    ax.text(248, thr_speed + 1.5, f"Speed  {thr_speed} bpm", fontsize=9, color="#008888", ha="left", va="bottom")

    ax.text(tc_vo2 + 4, (thr_vo2 + 97) / 2,
            "SWEET\nSPOT", fontsize=7.5, color=TEAL, alpha=0.55,
            ha="left", va="center", fontweight="bold", linespacing=1.3)

    ax.annotate("Effort ends", xy=(0, HR_PEAK),
                xytext=(16, HR_PEAK + 5), fontsize=8,
                color="#666666",
                arrowprops=dict(arrowstyle="->", color="#404040", lw=0.8))

    ax.set_xlim(-4, 285)
    ax.set_ylim(HR_REST - 12, HR_PEAK + 12)
    ax.set_xlabel("Seconds of recovery", fontsize=9, color="#777777")
    ax.set_ylabel("Heart rate (bpm)", fontsize=9, color="#777777")
    ax.set_title("HEART RATE RECOVERY CURVE  ·  RECOVHR THRESHOLDS BY WORKOUT TYPE",
                 fontsize=9, color="#555555", pad=14, loc="left", fontweight="bold")
    ax.tick_params(labelsize=8)

    fig.tight_layout(pad=1.6)
    path = f"{OUT}/fig1_recovery_curve.png"
    fig.savefig(path, dpi=160, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    print(f"  {path}")


# ═══════════════════════════════════════════════════════════════════════════
# Fig 2 — Workout type comparison
# ═══════════════════════════════════════════════════════════════════════════
def fig2_workout_comparison():
    dark_style()
    fig, ax = plt.subplots(figsize=(9, 5))
    fig.patch.set_facecolor(BG)

    types     = ["SPEED", "EASY", "VO2MAX", "LT"]
    fractions = [0.35,    0.38,   0.42,     0.50]
    thresholds= [karvonen(f) for f in fractions]
    colors    = [TEAL_D, "#008888", TEAL, "#14d4d4"]
    alphas    = [0.6, 0.65, 0.85, 1.0]

    bars = ax.barh(types, thresholds, height=0.5, color=colors, alpha=0.0)
    for bar, col, alpha in zip(bars, colors, alphas):
        bar.set_facecolor(col); bar.set_alpha(alpha)

    for bar, thresh, col in zip(bars, thresholds, colors):
        ax.text(thresh + 1.2, bar.get_y() + bar.get_height() / 2,
                f"{thresh} bpm", va="center", fontsize=10,
                color=col, fontweight="600")

    ax.axvline(HR_MAX, color=RED, lw=1.2, ls="--", alpha=0.4)
    ax.text(HR_MAX + 1, 3.48, f"HRmax {HR_MAX}", fontsize=7.5, color=RED, alpha=0.6)

    ax.axvline(HR_REST, color="#333333", lw=1, ls=":")
    ax.text(HR_REST + 1, 3.48, f"Rest {HR_REST}", fontsize=7.5, color="#4d4d4d")

    ax.set_xlim(HR_REST - 8, HR_MAX + 22)
    ax.set_xlabel("Recovery threshold (bpm)", fontsize=9, color="#777777")
    ax.set_title(f"RECOVHR THRESHOLDS BY WORKOUT TYPE  ·  HRmax {HR_MAX}  HRrest {HR_REST}  HRR {HRR}",
                 fontsize=9, color="#555555", pad=14, loc="left", fontweight="bold")
    ax.tick_params(labelsize=8)

    fig.tight_layout(pad=1.6)
    path = f"{OUT}/fig2_workout_comparison.png"
    fig.savefig(path, dpi=160, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    print(f"  {path}")


# ═══════════════════════════════════════════════════════════════════════════
# Fig 3 — Cardiac drift
# ═══════════════════════════════════════════════════════════════════════════
def fig3_cardiac_drift():
    dark_style()
    fig, ax = plt.subplots(figsize=(9, 5))
    fig.patch.set_facecolor(BG)

    reps = np.arange(1, 9)
    base = karvonen(0.42)
    corrected   = [base if r < 3 else round(base + (r - 1) * 1.5) for r in reps]
    uncorrected = [base] * len(reps)

    ax.plot(reps, corrected, color=TEAL, lw=2.5, marker="o", ms=7,
            label="RecovHR (drift-corrected)", zorder=6)
    ax.plot(reps, corrected, color=TEAL, lw=9, alpha=0.07, zorder=5)
    ax.plot(reps, uncorrected, color="#404040", lw=1.5,
            marker="o", ms=5, ls="--", label="Fixed threshold")

    gap = corrected[-1] - uncorrected[-1]
    ax.annotate(f"+{gap:.0f} bpm at rep 8",
                xy=(8, corrected[-1]), xytext=(6.6, corrected[-1] + 3.5),
                fontsize=8.5, color=TEAL,
                arrowprops=dict(arrowstyle="->", color=TEAL, lw=1.0))

    ax.set_xticks(reps)
    ax.set_xlabel("Repetition number", fontsize=9, color="#777777")
    ax.set_ylabel("Recovery threshold (bpm)", fontsize=9, color="#777777")
    ax.set_title("CARDIAC DRIFT CORRECTION  ·  8×400M VO2MAX SESSION",
                 fontsize=9, color="#555555", pad=14, loc="left", fontweight="bold")
    ax.legend(fontsize=9, frameon=False, labelcolor="#999999")
    ax.set_ylim(base - 6, corrected[-1] + 14)
    ax.tick_params(labelsize=8)

    fig.tight_layout(pad=1.6)
    path = f"{OUT}/fig3_cardiac_drift.png"
    fig.savefig(path, dpi=160, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    print(f"  {path}")


# ═══════════════════════════════════════════════════════════════════════════
# Fig 4 — Karvonen vs %HRmax
# ═══════════════════════════════════════════════════════════════════════════
def fig4_karvonen_vs_pct():
    dark_style()
    fig, ax = plt.subplots(figsize=(9, 5))
    fig.patch.set_facecolor(BG)

    hr_rests = [38, 48, 58, 68]
    frac = 0.42
    raw = round(0.65 * HR_MAX)
    kv  = [round((HR_MAX - r) * frac + r) for r in hr_rests]
    labels = [f"HRrest\n{r} bpm" for r in hr_rests]

    x = np.arange(len(hr_rests))
    w = 0.32

    b1 = ax.bar(x - w/2, kv,      width=w, color=TEAL,   alpha=0.85, label="RecovHR (Karvonen × 0.42)")
    b2 = ax.bar(x + w/2, [raw]*4, width=w, color=DARK_R, alpha=0.5,  label=f"Fixed 65% HRmax = {raw}")

    for bar, val in zip(b1, kv):
        ax.text(bar.get_x() + bar.get_width()/2, val + 1,
                str(val), ha="center", fontsize=9.5, color=TEAL, fontweight="600")
    for bar in b2:
        ax.text(bar.get_x() + bar.get_width()/2, raw + 1,
                str(raw), ha="center", fontsize=9.5, color="#666666")

    ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=8.5)
    ax.set_ylabel("Recovery threshold (bpm)", fontsize=9, color="#777777")
    ax.set_title(f"KARVONEN VS FIXED %HRmax  ·  ALL ATHLETES: HRmax = {HR_MAX}",
                 fontsize=9, color="#555555", pad=14, loc="left", fontweight="bold")
    ax.legend(fontsize=9, frameon=False, labelcolor="#999999")
    ax.set_ylim(80, 140)
    ax.tick_params(labelsize=8)

    fig.tight_layout(pad=1.6)
    path = f"{OUT}/fig4_karvonen_vs_pct.png"
    fig.savefig(path, dpi=160, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    print(f"  {path}")


# ═══════════════════════════════════════════════════════════════════════════
# Fig 5 — PCr kinetics
# ═══════════════════════════════════════════════════════════════════════════
def fig5_pcr_kinetics():
    dark_style()
    fig, ax = plt.subplots(figsize=(9, 5))
    fig.patch.set_facecolor(BG)

    t = np.linspace(0, 210, 600)
    TAU_PCR = 43.7
    pcr = (1 - np.exp(-t / TAU_PCR)) * 100

    ax.fill_between(t, pcr, alpha=0.06, color=TEAL)
    ax.plot(t, pcr, color=TEAL, lw=2.5)
    ax.plot(t, pcr, color=TEAL, lw=9, alpha=0.07)

    milestones = [(60, 75), (90, 87), (120, 93), (180, 97)]
    for t_m, pct in milestones:
        ax.plot([t_m, t_m], [0, pct], color="#1f1f1f", lw=1, ls=":")
        ax.scatter([t_m], [pct], color=TEAL, s=50, zorder=6)
        ax.text(t_m + 3, pct - 5.5, f"{pct}%\n{t_m}s",
                fontsize=8, color="#8a8a8a", linespacing=1.3)

    ax.axvline(90,  color=TEAL_D, lw=1.4, ls="--", alpha=0.7)
    ax.axvline(120, color=TEAL,   lw=1.4, ls="--", alpha=0.5)
    ax.text(92,  5, "VO2max\nfloor", fontsize=7.5, color=TEAL_D, linespacing=1.3)
    ax.text(122, 5, "Speed\nfloor",  fontsize=7.5, color=TEAL,   linespacing=1.3)

    ax.set_xlim(0, 215)
    ax.set_ylim(0, 104)
    ax.set_xlabel("Seconds post-effort", fontsize=9, color="#777777")
    ax.set_ylabel("PCr restored (%)", fontsize=9, color="#777777")
    ax.set_title("PHOSPHOCREATINE RESYNTHESIS KINETICS  ·  BASIS FOR RECOVHR CLOCK FLOORS",
                 fontsize=9, color="#555555", pad=14, loc="left", fontweight="bold")
    ax.tick_params(labelsize=8)

    fig.tight_layout(pad=1.6)
    path = f"{OUT}/fig5_pcr_kinetics.png"
    fig.savefig(path, dpi=160, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    print(f"  {path}")


if __name__ == "__main__":
    print("Building RecovHR figures (dark telemetry mode)...")
    fig1_recovery_curve()
    fig2_workout_comparison()
    fig3_cardiac_drift()
    fig4_karvonen_vs_pct()
    fig5_pcr_kinetics()
    print("Done.")
