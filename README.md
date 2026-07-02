# RecovHR

**Know when to go again.** A heart-rate reserve algorithm for individualized interval recovery.

Between hard reps, most runners guess. RecovHR converts four biometrics into one number per rep — the heart rate at which you're recovered enough to go hard again.

📄 **Paper:** [RecovHR (Popler, 2026)](docs/RecovHR_Paper_Popler_2026.pdf)
🌐 **Site:** open `index.html` in a browser (no build step)

## The problem

Recovery between reps is the least-measured variable in interval training, and getting it wrong costs in both directions:

- **Go too soon** — with phosphocreatine only ~50% restored, session quality collapses by rep 3–4.
- **Wait too long** — a full reset wastes 45–75 seconds per rep re-ramping to target intensity, diluting the training stimulus.

RecovHR targets the window in between.

## The algorithm

All thresholds scale from heart-rate reserve (Karvonen), so the same session prescribes different numbers for different athletes.

```
HRR  = HRmax − HRrest              usable cardiac range
T    = HRR × f + HRrest            recovery threshold for the workout type
T(n) = T + (n − 1) × 1.5           cardiac-drift correction, from rep 3
```

Worked example — HRmax 188, HRrest 48, VO2max session: `HRR = 140`, `T = 140 × 0.42 + 48 = 107 bpm`.

| Workout | HRR fraction *f* | Clock floor | Rationale |
|---------|-----------------|-------------|-----------|
| VO2max  | 0.42 | 90 s  | Incomplete recovery preserves cardiac stress (4×4 Norwegian protocol) |
| LT      | 0.50 | 60 s  | HR didn't peak; partial rest preserves the lactate signal |
| Speed   | 0.35 | 120 s | HR lags sprints 30–60 s; PCr resynthesis (93% at 120 s) governs |
| Easy    | 0.38 | 30 s  | Monitors the work interval against surges into threshold territory |

Inputs: `HRmax` (measured, or Tanaka `208 − 0.7 × age`), `HRrest`, `LTHR` (30-min field test, or ~87% HRmax), and age if HRmax is estimated.

## Repository

```
index.html   single-page site with a live threshold calculator
src/         hrRecovery.ts — reference TypeScript implementation
figures/     charts used in the paper and site
docs/        the paper (PDF + Markdown source)
```

To view the site locally with the figures loading, serve the folder:

```bash
python3 -m http.server 8000
# → http://localhost:8000
```

## Method & limitations

Every parameter has a named source (Karvonen 1957; Helgerud 2007; Buchheit & Laursen 2013; Harris 1976; Glaister 2005; Rampinini 2015; Tanaka 2001) — no proprietary data, no black box. Known limitations: HR lags sub-30s sprints (the clock floor governs), the drift constant is a single-study mean, LTHR estimates vary 80–92% across the literature, and the index has not yet been tested in a controlled trial. Full bibliography in the paper.

## Author

Luke Popler · Sequoia High School, Redwood City, CA · catlover125r@gmail.com · April 2026
