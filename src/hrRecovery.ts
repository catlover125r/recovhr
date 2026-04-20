/**
 * Heart rate-based interval recovery algorithm.
 *
 * Formula foundation: Karvonen Heart Rate Reserve (HRR)
 * Recovery_target = (HRR × fraction) + HRrest
 * where HRR = HRmax - HRrest
 *
 * Sources:
 *   Buchheit & Laursen, Sports Medicine 2013 (Parts I & II)
 *   Harris et al. 1976 / Glaister 2005 (PCr resynthesis kinetics)
 *   JSSM 2015 PMID 25983598 (cardiac drift)
 *   Cole et al. NEJM 1999 (HRR60 norms)
 */

export type WorkoutType = "VO2MAX" | "LT" | "SPEED" | "EASY";

export interface AthleteProfile {
  age: number;
  /** Measured or estimated. If omitted, estimated via Tanaka formula: 208 - 0.7 * age */
  hrMax?: number;
  /** Resting HR (seated, morning) */
  hrRest: number;
  /**
   * Lactate threshold HR.
   * If omitted, estimated as 87% of HRmax (trained runner default).
   */
  lthr?: number;
}

export interface RecoveryTarget {
  /** Heart rate at which to start the next interval */
  targetHR: number;
  /** Minimum clock rest in seconds regardless of HR */
  minRestSeconds: number;
  /** Notes about HR lag or special considerations */
  notes: string;
}

// HRR fractions derived from published HIIT recovery research
const HRR_FRACTIONS: Record<WorkoutType, number> = {
  VO2MAX: 0.42,
  LT: 0.50,
  SPEED: 0.35,
  EASY: 0.38,
};

// Minimum rest floors based on PCr resynthesis kinetics
const MIN_REST_SECONDS: Record<WorkoutType, number> = {
  VO2MAX: 90,
  LT: 60,
  SPEED: 120,
  EASY: 30,
};

const NOTES: Record<WorkoutType, string> = {
  VO2MAX:
    "Incomplete recovery is intentional — preserves cardiac stress across the session.",
  LT: "Partial recovery maintains the lactate accumulation signal for mitochondrial adaptation.",
  SPEED:
    "HR lags reality for sub-30s reps (peaks 30-60s after stop). Clock floor is primary; HR is confirmation only.",
  EASY:
    "HR rarely reaches maximal levels. Monitor to prevent work intervals drifting too high, not recovery.",
};

/**
 * Estimate HRmax using the Tanaka formula (more accurate than 220-age for adults).
 */
export function estimateHRmax(age: number): number {
  return Math.round(208 - 0.7 * age);
}

/**
 * Resolve full profile, filling in estimated values where measured ones are absent.
 */
function resolveProfile(profile: AthleteProfile): Required<AthleteProfile> {
  const hrMax = profile.hrMax ?? estimateHRmax(profile.age);
  const lthr = profile.lthr ?? Math.round(hrMax * 0.87);
  return { ...profile, hrMax, lthr };
}

/**
 * Compute the base recovery target HR for a given workout type and rep number.
 *
 * @param profile   - Athlete biometric inputs
 * @param workout   - Type of interval workout
 * @param repNumber - Current rep (1-indexed). Cardiac drift correction applies from rep 3.
 */
export function recoveryTarget(
  profile: AthleteProfile,
  workout: WorkoutType,
  repNumber: number = 1
): RecoveryTarget {
  const { hrMax, hrRest } = resolveProfile(profile);
  const hrr = hrMax - hrRest;
  const fraction = HRR_FRACTIONS[workout];

  const baseTarget = Math.round(hrr * fraction + hrRest);

  // Cardiac drift: +1.5 bpm per completed rep, starting at rep 3
  // Prevents the threshold from effectively lengthening rest in late reps
  const driftBpm = repNumber >= 3 ? (repNumber - 1) * 1.5 : 0;
  const targetHR = Math.round(baseTarget + driftBpm);

  return {
    targetHR,
    minRestSeconds: MIN_REST_SECONDS[workout],
    notes: NOTES[workout],
  };
}

/**
 * Infer workout type from the target effort HR relative to LTHR.
 *
 * Useful when the user provides a target pace/HR and you need to auto-classify.
 */
export function classifyWorkout(
  effortHR: number,
  profile: AthleteProfile
): WorkoutType {
  const { hrMax, lthr } = resolveProfile(profile);

  if (effortHR >= lthr * 0.97) return "VO2MAX";   // at/above LTHR → VO2max zone
  if (effortHR >= lthr * 0.88) return "LT";        // 88–97% LTHR → threshold zone
  if (effortHR >= hrMax * 0.65) return "EASY";     // aerobic zone
  return "EASY";
}

/**
 * Return a human-readable summary of the full session recovery plan.
 *
 * @param profile   - Athlete profile
 * @param workout   - Workout type
 * @param totalReps - Number of reps planned
 */
export function sessionPlan(
  profile: AthleteProfile,
  workout: WorkoutType,
  totalReps: number
): { rep: number; targetHR: number; minRestSeconds: number }[] {
  return Array.from({ length: totalReps }, (_, i) => {
    const repNum = i + 1;
    const { targetHR, minRestSeconds } = recoveryTarget(profile, workout, repNum);
    return { rep: repNum, targetHR, minRestSeconds };
  });
}

/**
 * Classify an athlete's HRR60 (HR drop in first 60 seconds post-effort).
 * Used as a session-start calibration to confirm thresholds are appropriate.
 *
 * Reference: Cole et al. NEJM 1999
 */
export function classifyHRR60(
  hrAtStop: number,
  hrAt60Seconds: number
): { drop: number; category: "elite" | "fit" | "average" | "concern" } {
  const drop = hrAtStop - hrAt60Seconds;
  if (drop >= 40) return { drop, category: "elite" };
  if (drop >= 25) return { drop, category: "fit" };
  if (drop >= 12) return { drop, category: "average" };
  return { drop, category: "concern" };
}
