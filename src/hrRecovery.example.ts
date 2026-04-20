import {
  recoveryTarget,
  sessionPlan,
  classifyHRR60,
  estimateHRmax,
  type AthleteProfile,
  type WorkoutType,
} from "./hrRecovery";

// Example: 32-year-old runner, measured HRmax 188, resting HR 48, LTHR 163
const athlete: AthleteProfile = {
  age: 32,
  hrMax: 188,
  hrRest: 48,
  lthr: 163,
};

console.log("=== Athlete Profile ===");
console.log(`  HRmax: ${athlete.hrMax}  |  HRrest: ${athlete.hrRest}  |  LTHR: ${athlete.lthr}`);
console.log(`  HRR (usable range): ${athlete.hrMax! - athlete.hrRest} bpm\n`);

// Single rep targets
const workouts: WorkoutType[] = ["VO2MAX", "LT", "SPEED", "EASY"];
console.log("=== Recovery Targets (Rep 1) ===");
for (const w of workouts) {
  const { targetHR, minRestSeconds, notes } = recoveryTarget(athlete, w, 1);
  console.log(`  ${w.padEnd(8)} → Start next rep when HR ≤ ${targetHR} bpm  (min ${minRestSeconds}s)`);
  console.log(`           ${notes}\n`);
}

// Full session plan: 8x400m at VO2max
console.log("=== Session Plan: 8x VO2MAX intervals ===");
const plan = sessionPlan(athlete, "VO2MAX", 8);
console.log("  Rep  |  Start when HR ≤  |  Min rest");
console.log("  -----|-------------------|----------");
for (const { rep, targetHR, minRestSeconds } of plan) {
  const drift = rep >= 3 ? `  (+${((rep - 1) * 1.5).toFixed(1)} drift)` : "";
  console.log(`  ${String(rep).padEnd(4)} |  ${targetHR} bpm${" ".repeat(10)}|  ${minRestSeconds}s${drift}`);
}

// HRR60 calibration check
console.log("\n=== HRR60 Calibration (post warm-up effort) ===");
const samples = [
  { stop: 178, at60: 138 }, // elite
  { stop: 178, at60: 150 }, // fit
  { stop: 178, at60: 163 }, // average
];
for (const s of samples) {
  const { drop, category } = classifyHRR60(s.stop, s.at60);
  console.log(`  HR ${s.stop} → ${s.at60} bpm  |  Drop: ${drop} bpm  |  Category: ${category}`);
}

// Show what changes if HRmax is not measured (estimated)
console.log("\n=== Without measured HRmax (age-estimated) ===");
const noMeasured: AthleteProfile = { age: 32, hrRest: 48 };
console.log(`  Tanaka estimate: ${estimateHRmax(32)} bpm`);
const { targetHR } = recoveryTarget(noMeasured, "VO2MAX", 1);
console.log(`  VO2MAX recovery target: ${targetHR} bpm`);
