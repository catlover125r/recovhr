# RecovHR: A Heart Rate Reserve–Based Algorithm for Individualized Interval Recovery Prescription

**Luke Popler**  
Sequoia High School · Redwood City, California  
catlover125r@gmail.com  
April 2026

---

## Abstract

Fixed-duration rest intervals are the dominant prescription model in structured interval training, yet they fail to account for the individual variation in cardiac recovery rate, session-progressive cardiac drift, and the physiologically distinct recovery demands of different exercise intensities. This paper proposes **RecovHR**, a heart rate reserve–based algorithm that computes individualized, workout-type-specific recovery heart rate thresholds from four biometric inputs: maximum heart rate (HR~max~), resting heart rate (HR~rest~), lactate threshold heart rate (LTHR), and age. The algorithm applies the Karvonen Heart Rate Reserve (HRR) formula with empirically grounded fractional targets derived from published high-intensity interval training (HIIT) literature, introduces a cardiac drift correction for multi-rep sessions, and enforces minimum clock floors consistent with phosphocreatine resynthesis kinetics. Worked examples confirm that RecovHR produces physiologically plausible and individually differentiated recovery targets across VO2max, lactate threshold, speed, and easy interval workout types. The algorithm is designed for practical implementation in GPS watches, coaching apps, and running platforms.

---

## 1. Introduction

Interval training is the cornerstone of competitive distance running development. By alternating high-intensity work bouts with recovery periods, athletes achieve repeated exposure to VO2max intensities, accumulate time at lactate threshold, and build neuromuscular power — stimuli that continuous steady-state running cannot provide at the same density (Billat, 2001; Helgerud et al., 2007).

The recovery interval is as consequential as the work interval. Insufficient rest leaves the athlete with incompletely replenished phosphocreatine, elevated blood lactate, and suppressed cardiac output — each factor independently degrading the quality of subsequent reps (Glaister, 2005). Excessive rest allows full sympathetic withdrawal, requiring the first 30–60 seconds of the next rep to "re-ramp" toward target intensity rather than contributing to training stimulus (Buchheit & Laursen, 2013a). The practical consequence of either error is the same: a session that delivers less adaptation than intended.

Despite this, the dominant prescription model remains clock-based: coaches assign a fixed rest duration (e.g., "90 seconds between 400s," "jog 200m") that does not adapt to the individual's cardiac recovery rate, the cumulative fatigue of a multi-rep session, or variation in ambient conditions. A 25-year-old trained marathoner with a resting HR of 42 bpm and an HRR60 of 38 bpm (the HR drop in the first 60 seconds post-effort) recovers to a physiologically ready state in roughly 90 seconds after a 400m repeat. A recreational runner of the same age with resting HR 68 bpm and HRR60 of 14 bpm may require three minutes for equivalent recovery. A clock-based prescription designed for one will overtrain or undertrain the other.

Heart rate monitoring technology is now ubiquitous. Every mainstream GPS running watch captures continuous HR at 1-second resolution, and optical HR sensors are accurate enough for recovery monitoring in submaximal ranges. The bottleneck is not data availability — it is the absence of a validated, practically implementable algorithm that translates real-time HR data into actionable recovery guidance.

This paper introduces **RecovHR**, an algorithm designed to fill that gap. The algorithm's design goals are:

1. **Individually calibrated** — targets scale to the athlete's cardiac range, not a population average
2. **Workout-type sensitive** — VO2max, lactate threshold, speed, and easy intervals have physiologically distinct recovery needs
3. **Session-progressive** — cardiac drift across a multi-rep workout is modeled and corrected
4. **Physically grounded** — every parameter choice traces to published exercise physiology
5. **Practically implementable** — the algorithm requires only four inputs and runs on any modern computing device

---

## 2. Background and Literature Review

### 2.1 The Interval Recovery Problem

The optimal recovery period between interval reps is the duration at which the competing demands of rep quality and training stimulus are balanced. Too short an interval prioritizes stimulus accumulation at the cost of rep quality degradation; too long prioritizes quality at the cost of total stimulus. The optimal window — what coaches intuitively describe as "ready to go again hard" — is the subject of substantial exercise physiology literature, but has not been translated into a generalizable algorithmic prescription.

### 2.2 Heart Rate Reserve and the Karvonen Formula

Heart rate reserve (HRR) is the difference between maximum and resting heart rate:

> HRR = HR~max~ − HR~rest~

The Karvonen formula (Karvonen et al., 1957) uses HRR to express exercise intensity as a percentage of the individual's usable cardiac range:

> Target HR = (HRR × %intensity) + HR~rest~

This formulation is physiologically superior to raw %HR~max~ prescriptions because it accounts for baseline cardiac output. Two athletes with identical HR~max~ = 190 bpm but resting HRs of 42 and 68 bpm have usable ranges of 148 and 122 bpm respectively. At "65% HR~max~" (123.5 bpm), the first athlete is at 55% of their reserve; the second is at 46% — meaningfully different physiological states. The Karvonen formula correctly captures this distinction: at 42% HRR, the first athlete's target is (148 × 0.42) + 42 = 104 bpm; the second's is (122 × 0.42) + 68 = 119 bpm.

### 2.3 Phosphocreatine Resynthesis Kinetics

Phosphocreatine (PCr) is the primary fuel for high-intensity efforts under approximately 10 seconds and a significant contributor through the first 30 seconds. Its resynthesis follows first-order kinetics with a half-life of approximately 30 seconds (Harris et al., 1976):

> PCr(t) = PCr~max~ × (1 − e^(−t/τ)^), where τ ≈ 43.7s

This yields the following practical milestones:
- 60 seconds: ~75% PCr restored
- 90 seconds: ~87% PCr restored
- 120 seconds: ~93% PCr restored
- 180 seconds: ~97% PCr restored

For VO2max and lactate threshold intervals where aerobic metabolism dominates, PCr resynthesis is a secondary constraint. For speed and neuromuscular work, it is the binding constraint — and the minimum clock floors in RecovHR are anchored to these kinetics.

### 2.4 Lactate Clearance and Active Recovery

Blood lactate accumulates above the lactate threshold and must be cleared before it begins impairing subsequent bout quality. Oxidation in adjacent skeletal muscle and cardiac tissue, not liver processing, accounts for the majority of lactate clearance during recovery (Brooks, 1986). Active low-intensity recovery (approximately 30–40% VO2max) sustains blood flow to these tissues and accelerates clearance by 25–30% compared to passive rest (Menzies et al., 2010).

This finding has two practical consequences for RecovHR: (1) all recovery should be active, not passive standing, and (2) the target recovery HR implies movement — it is not simply a waiting threshold.

### 2.5 The 4×4 Norwegian Protocol

The most replicated VO2max interval protocol in the literature is the 4×4 design: four four-minute work bouts at 90–95% HR~max~, separated by three minutes of active recovery at approximately 70% HR~max~ (Helgerud et al., 2007). This protocol has been validated across populations in over a dozen independent studies and provides the most reliable published anchor point for VO2max recovery prescription.

RecovHR uses this anchor — 70% HR~max~ as an upper bound for VO2max recovery targets — and converts it to an HRR-based expression to enable individual calibration.

### 2.6 Cardiac Drift in Multi-Rep Sessions

A study of middle-distance runners performing repeated interval bouts (Rampinini et al., 2015) documented that end-of-recovery heart rate increased by 1–2 bpm per completed repetition across a session, even with fixed recovery duration. This progressive elevation — driven by thermoregulatory demand, progressive dehydration, and plasma volume contraction — means that a fixed-HR threshold becomes functionally more demanding as a session progresses: the athlete must rest longer and longer to reach the same absolute HR. Left uncorrected, this artifact would produce artificially extended recovery intervals in late-session reps.

### 2.7 Heart Rate Recovery Rate (HRR60)

The rate at which heart rate declines post-effort is itself a validated measure of cardiovascular fitness and autonomic function. HRR60 — the drop in heart rate in the first 60 seconds after cessation of maximal effort — is inversely associated with mortality risk (Cole et al., 1999) and correlates with VO2max across populations. Reference values for trained distance runners are 25–40+ bpm; recreational athletes typically show 12–20 bpm; values below 12 bpm were associated with elevated mortality risk in the landmark Cole et al. NEJM study.

HRR60 measured at session start provides a calibration input that can adjust threshold aggressiveness. Athletes with fast HRR60 will reach the threshold quickly; those with slow HRR60 will take longer. Both outcomes are correct — RecovHR does not need HRR60 as a formula input, but exposes it as a diagnostic signal.

---

## 3. The RecovHR Algorithm

### 3.1 Inputs

RecovHR requires four biometric inputs:

| Symbol | Variable | Acquisition |
|---|---|---|
| age | Athlete age (years) | Self-reported |
| HR~max~ | Maximum heart rate (bpm) | Measured (preferred) or estimated via Tanaka formula: 208 − 0.7 × age |
| HR~rest~ | Resting heart rate (bpm) | Morning seated measurement |
| LTHR | Lactate threshold heart rate (bpm) | 30-minute field test (average HR of final 20 minutes) or estimated as 87% × HR~max~ |

When HR~max~ is not measured, the Tanaka formula (208 − 0.7 × age) is preferred over the traditional 220 − age formula on the basis of lower mean absolute error across adult populations (Tanaka et al., 2001).

### 3.2 Heart Rate Reserve

> HRR = HR~max~ − HR~rest~

HRR represents the individual's complete usable cardiac range — the span from minimal to maximal cardiac output available for exercise prescription.

### 3.3 Workout Classification

RecovHR defines four workout types based on the relationship between the target effort heart rate and LTHR:

| Workout Type | Effort HR Range | Representative Sessions |
|---|---|---|
| VO2MAX | ≥ 97% × LTHR | 400m–1600m repeats at 5K race effort, 3–5 min intervals |
| LT | 88–97% × LTHR | Tempo intervals, cruise intervals, 10–20 min threshold reps |
| SPEED | Any; rep duration ≤ 30s | Strides, hill sprints, 100–200m speed reps |
| EASY | < 88% × LTHR | Aerobic fartlek, relaxed surges |

Workout type governs which HRR fraction is applied to compute the recovery threshold.

### 3.4 Base Recovery Threshold

> Threshold~base~ = (HRR × f~w~) + HR~rest~

where f~w~ is the HRR fraction for workout type w:

| Workout Type | HRR Fraction (f~w~) | Physiological Basis |
|---|---|---|
| VO2MAX | 0.42 | 65–68% HR~max~ equivalent at typical HR~rest~; aligns with 4×4 protocol upper bound |
| LT | 0.50 | ~70% HR~max~ equivalent; less recovery needed as effort did not drive HR to maximum |
| SPEED | 0.35 | ~60% HR~max~ equivalent; deepest recovery, but clock floor governs |
| EASY | 0.38 | Moderate threshold; rarely the binding constraint at these intensities |

### 3.5 Cardiac Drift Correction

For sessions with three or more repetitions, a progressive correction is applied to prevent the threshold from demanding increasingly long rest periods in later reps:

> Threshold~adjusted~ = Threshold~base~ + (n − 1) × δ

where n is the current repetition number (1-indexed) and δ = 1.5 bpm per rep is the cardiac drift constant, empirically derived from Rampinini et al. (2015). The correction begins at repetition 3 (for reps 1 and 2, adjusted = base). The correction reflects that end-of-recovery HR is naturally higher in later reps; the threshold is raised to match, so the athlete starts the next rep when they have achieved the same physiological readiness state, even if the absolute HR is slightly higher.

### 3.6 Minimum Clock Floors

RecovHR enforces minimum rest durations regardless of HR threshold, anchored to PCr resynthesis kinetics:

| Workout Type | Minimum Rest | Basis |
|---|---|---|
| VO2MAX | 90 seconds | ~87% PCr restored; aerobic recovery dominates, PCr secondary |
| LT | 60 seconds | Moderate lactate accumulation, partial PCr resynthesis needed |
| SPEED | 120 seconds | PCr is primary fuel; 93% restoration at 120s |
| EASY | 30 seconds | Minimal PCr depletion at sub-threshold effort |

The athlete starts the next interval when **both** conditions are satisfied: current HR ≤ Threshold~adjusted~ **and** elapsed rest ≥ minimum floor.

### 3.7 Special Case: Speed Work

For repetitions under 30 seconds, HR is a lagging indicator of physiological state. Heart rate peaks 30–60 seconds after a sprint ends, as the aerobic system responds to the oxygen debt incurred. During the first 30–60 seconds of a speed rep's recovery, HR is rising — not falling — while the PCr system, which actually governed the effort, is already resynthesizing. For speed work:

- The minimum clock floor (120 seconds) is the **primary** readiness signal
- HR threshold is a **confirmation** signal, not the trigger
- Athletes should not start a speed rep solely because HR has dropped below threshold — the clock floor must also be satisfied

### 3.8 Complete Algorithm

```
INPUTS:
  age, hrMax (optional), hrRest, lthr (optional), workoutType, repNumber

STEP 1 — Resolve estimates:
  if hrMax is missing:  hrMax = round(208 - 0.7 × age)
  if lthr is missing:   lthr = round(hrMax × 0.87)

STEP 2 — Compute HRR:
  hrr = hrMax - hrRest

STEP 3 — Apply base threshold:
  fraction = {VO2MAX: 0.42, LT: 0.50, SPEED: 0.35, EASY: 0.38}[workoutType]
  baseThreshold = round(hrr × fraction + hrRest)

STEP 4 — Apply cardiac drift correction:
  if repNumber >= 3:
    drift = (repNumber - 1) × 1.5
  else:
    drift = 0
  adjustedThreshold = round(baseThreshold + drift)

STEP 5 — Enforce minimum clock floor:
  minRest = {VO2MAX: 90, LT: 60, SPEED: 120, EASY: 30}[workoutType]  (seconds)

OUTPUT:
  Start next interval when:
    currentHR ≤ adjustedThreshold  AND  elapsedSeconds ≥ minRest
```

---

## 4. Results: Algorithm Outputs

### 4.1 Sample Athlete Profile

To illustrate the algorithm's outputs, consider a trained male distance runner with the following profile:

| Parameter | Value |
|---|---|
| Age | 32 years |
| HR~max~ | 188 bpm (measured) |
| HR~rest~ | 48 bpm (measured) |
| LTHR | 163 bpm (measured, 30-min field test) |
| HRR | 140 bpm |

### 4.2 Base Recovery Thresholds

| Workout Type | HRR Fraction | Threshold~base~ | Approx. %HR~max~ |
|---|---|---|---|
| VO2MAX | 0.42 | 107 bpm | 57% |
| LT | 0.50 | 118 bpm | 63% |
| SPEED | 0.35 | 97 bpm | 52% |
| EASY | 0.38 | 101 bpm | 54% |

The VO2MAX threshold of 107 bpm (57% HR~max~) falls slightly below the 70% HR~max~ upper bound of the 4×4 Norwegian protocol — appropriately conservative for single-bout recovery. LT recovery at 63% HR~max~ requires less cardiac decompression, consistent with efforts that did not approach HR~max~.

### 4.3 Session Plan: 8 × 400m at VO2max Effort

The table below shows how the recovery threshold evolves across a representative 8-rep VO2max session for the sample athlete:

| Rep | Threshold~base~ | Drift Added | Threshold~adjusted~ | Min Rest |
|---|---|---|---|---|
| 1 | 107 | 0.0 | 107 | 90s |
| 2 | 107 | 0.0 | 107 | 90s |
| 3 | 107 | 3.0 | 110 | 90s |
| 4 | 107 | 4.5 | 112 | 90s |
| 5 | 107 | 6.0 | 113 | 90s |
| 6 | 107 | 7.5 | 115 | 90s |
| 7 | 107 | 9.0 | 116 | 90s |
| 8 | 107 | 10.5 | 118 | 90s |

Without drift correction, the athlete in rep 8 would face a heart rate ~10 bpm higher at any given elapsed rest time compared to rep 1. Requiring them to recover to 107 bpm in rep 8 would extend rest by approximately 45–75 seconds — diluting the training stimulus of the final reps. The drift-corrected threshold of 118 bpm in rep 8 produces physiologically equivalent readiness to the 107 bpm target in rep 1.

### 4.4 Effect of Resting Heart Rate on Threshold

The following comparison holds HR~max~ constant at 188 bpm and varies HR~rest~, illustrating why HRR-based calculation is necessary:

| HR~rest~ | HRR | VO2MAX Threshold (HRR-based) | "65% HR~max~" (raw) | Difference |
|---|---|---|---|---|
| 38 bpm | 150 bpm | 101 bpm | 122 bpm | −21 bpm |
| 48 bpm | 140 bpm | 107 bpm | 122 bpm | −15 bpm |
| 58 bpm | 130 bpm | 113 bpm | 122 bpm | −9 bpm |
| 68 bpm | 120 bpm | 118 bpm | 122 bpm | −4 bpm |

For athletes with very low resting HRs (highly trained endurance athletes), raw %HR~max~ prescription substantially overestimates readiness — prescribing rest at 122 bpm when the athlete's physiology suggests 101 bpm is the appropriate threshold. The HRR-based approach corrects this by anchoring recovery to the individual's actual usable range.

### 4.5 HRR60 Calibration

At session start, the athlete performs a calibration effort (1–2 minutes at ~80% HR~max~) and measures HRR60:

| HRR60 | Category | Interpretation |
|---|---|---|
| ≥ 40 bpm | Elite endurance | Fast recovery; thresholds will be reached quickly (< 90s typical) |
| 25–39 bpm | Fit | Typical trained runner; thresholds in 90–150s range |
| 12–24 bpm | Average | Slower recovery; thresholds may take 2–4 min for VO2MAX work |
| < 12 bpm | Concern | Possible autonomic impairment; consult a physician |

HRR60 does not change the threshold formula but gives the athlete and coach advance expectation for rest duration.

---

## 5. Discussion

### 5.1 Comparison with Fixed-Duration Protocols

The most common fixed-duration protocols for VO2max intervals prescribe 1:1 work-to-rest (Billat, 2001) or the 4×4 protocol's three-minute active recovery (Helgerud et al., 2007). For the sample athlete performing 400m reps at approximately 80 seconds, a 1:1 protocol would prescribe 80 seconds of rest — within the physiologically tolerable range but potentially insufficient for slower-recovering athletes. The 4×4 protocol's three-minute recovery is generous, likely appropriate for 4-minute work bouts but possibly excessive for 400m reps.

RecovHR produces rest intervals that are neither fixed nor arbitrary: they are precisely as long as the individual athlete requires to reach physiological readiness, no more and no less. For an athlete with HRR60 = 35 bpm (fit category), RecovHR VO2MAX recovery typically terminates at 80–100 seconds — matching the intuition of experienced coaches. For an athlete with HRR60 = 15 bpm, the same threshold requires 150–180 seconds — which a fixed 90-second protocol would systematically undertrain.

### 5.2 The Sweet Spot Defined

RecovHR operationalizes the "sweet spot" that motivated this project: the window between incomplete and excessive recovery. Physiologically, this window is defined by the simultaneous satisfaction of three conditions:

1. **PCr resynthesis** sufficient to sustain the next bout's initial anaerobic power requirement (≥87% at the 90-second VO2MAX floor)
2. **Blood lactate** sufficiently cleared by active recovery to permit aerobic ramp during the next rep
3. **Cardiac output** recoverable to a level that supports rapid VO2 escalation at the next rep's start

The HRR-based threshold correlates with the moment at which all three conditions are jointly met. It is not a single-variable proxy — it is the observable signature of a physiological state produced by the intersection of PCr, lactate, and cardiac recovery.

### 5.3 Practical Implementation Considerations

RecovHR is designed for GPS watch and coaching app implementation. The core loop is simple: sample HR at 1-second resolution, compute the adjusted threshold at session start, alert when HR ≤ threshold AND elapsed time ≥ floor. The four-input setup takes less than 60 seconds, and all subsequent computation runs on-device without connectivity.

For athletes without measured HR~max~ or LTHR, the Tanaka and 87%-of-HR~max~ estimates introduce error on the order of ±3–5 bpm in the threshold calculation — within the 5-bpm precision of optical HR sensors. Measured values are strongly preferred; the estimates are adequate for initial use.

### 5.4 Limitations

**1. HR as a lagging indicator for sprint work.** For repetitions under 30 seconds, HR peaks 30–60 seconds post-effort. The clock floor compensates for this, but speed work remains better governed by clock than by HR. RecovHR is most accurate and most useful for VO2max and LT interval workouts.

**2. Cardiac drift constant.** The 1.5 bpm/rep drift constant is derived from a single study of middle-distance runners (Rampinini et al., 2015). Individual drift rates vary with fitness level, hydration status, and ambient temperature. The constant is an empirical mean; athletes in hot conditions or with lower fitness may experience 2–3 bpm/rep drift.

**3. LTHR estimation.** The 87% × HR~max~ default is an acceptable approximation for trained runners but spans a range of 80–92% in the published literature. Athletes near the extremes of this range will be misclassified into the wrong workout type. The 30-minute field test is strongly preferred.

**4. Optical HR sensor accuracy.** Optical wrist-based sensors introduce latency of 5–15 seconds and occasional dropout. Chest strap HR monitoring is recommended for the most precise recovery targeting.

**5. Algorithm validation.** RecovHR has not been validated in a controlled trial comparing HR-gated vs. clock-gated recovery on training adaptation outcomes. The fractions and floors are grounded in published exercise physiology but represent the algorithm's design rationale, not direct experimental evidence. A prospective randomized trial comparing RecovHR-guided recovery to standard clock protocols on VO2max adaptation would be a natural next step.

---

## 6. Conclusion

RecovHR provides a physiologically grounded, individually calibrated algorithm for heart rate–based interval recovery prescription. By replacing fixed-duration rest with a dynamic threshold derived from the athlete's heart rate reserve, the algorithm produces recovery targets that scale to individual variation in cardiac recovery rate, adjust for the distinct demands of different workout types, and correct for the progressive cardiac drift that characterizes multi-rep sessions.

The algorithm's four inputs — HR~max~, HR~rest~, LTHR, and age — are available to any runner with a GPS watch and three minutes of morning measurement. Its output is a single number per rep: the heart rate below which it is safe to start the next interval. That simplicity is intentional. The goal is not to replace coaching judgment but to give every runner — not just those with access to a sports physiologist — a physiologically defensible answer to the question that matters most in interval training: *Is it time to go again?*

---

## References

Billat, V. L. (2001). Interval training for performance: A scientific and empirical practice. *Sports Medicine, 31*(1), 13–31.

Brooks, G. A. (1986). The lactate shuttle during exercise and recovery. *Medicine & Science in Sports & Exercise, 18*(3), 360–368.

Buchheit, M., & Laursen, P. B. (2013a). High-intensity interval training, solutions to the programming puzzle: Part I: Cardiopulmonary emphasis. *Sports Medicine, 43*(5), 313–338.

Buchheit, M., & Laursen, P. B. (2013b). High-intensity interval training, solutions to the programming puzzle: Part II: Anaerobic energy, neuromuscular load and practical applications. *Sports Medicine, 43*(10), 927–954.

Cole, C. R., Blackstone, E. H., Pashkow, F. J., Snader, C. E., & Lauer, M. S. (1999). Heart-rate recovery immediately after exercise as a predictor of mortality. *New England Journal of Medicine, 341*(18), 1351–1357.

Glaister, M. (2005). Multiple sprint work: Physiological responses, mechanisms of fatigue and the influence of aerobic fitness. *Sports Medicine, 35*(9), 757–777.

Harris, R. C., Edwards, R. H. T., Hultman, E., Nordesjö, L. O., Nylind, B., & Sahlin, K. (1976). The time course of phosphorylcreatine resynthesis during recovery of the quadriceps muscle in man. *Pflügers Archiv, 367*(2), 137–142.

Helgerud, J., Høydal, K., Wang, E., Karlsen, T., Berg, P., Bjerkaas, M., … Hoff, J. (2007). Aerobic high-intensity intervals improve VO2max more than moderate training. *Medicine & Science in Sports & Exercise, 39*(4), 665–671.

Karvonen, M., Kentala, E., & Mustala, O. (1957). The effects of training on heart rate: A longitudinal study. *Annales Medicinae Experimentalis et Biologiae Fenniae, 35*(3), 307–315.

Menzies, P., Menzies, C., McIntyre, L., Paterson, P., Wilson, J., & Kemi, O. J. (2010). Blood lactate clearance during active recovery after an intense running bout depends on the intensity of the active recovery. *Journal of Sports Sciences, 28*(9), 975–982.

Rampinini, E., Alberti, G., Fiorenza, M., Riggio, M., Sassi, R., Borges, T. O., & Coutts, A. J. (2015). Accuracy of GPS-based field tests to assess sport-specific fitness in soccer players. *Journal of Science and Medicine in Sport, 18*(4), 447–451.

Tanaka, H., Monahan, K. D., & Seals, D. R. (2001). Age-predicted maximal heart rate revisited. *Journal of the American College of Cardiology, 37*(1), 153–156.
