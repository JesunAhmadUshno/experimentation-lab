// Statistics that run live in the browser. Formulas mirror src/explab/power.py
// and src/explab/peeking.py so the page reproduces the study's numbers.

// Acklam's inverse normal CDF (relative error < 1.2e-9).
export function qnorm(p) {
  const a = [-39.6968302866538, 220.946098424521, -275.928510446969, 138.357751867269, -30.6647980661472, 2.50662827745924];
  const b = [-54.4760987982241, 161.585836858041, -155.698979859887, 66.8013118877197, -13.2806815528857];
  const c = [-0.00778489400243029, -0.322396458041136, -2.40075827716184, -2.54973253934373, 4.37466414146497, 2.93816398269878];
  const d = [0.00778469570904146, 0.32246712907004, 2.445134137143, 3.75440866190742];
  const lo = 0.02425, hi = 1 - lo;
  if (p < lo) { const q = Math.sqrt(-2 * Math.log(p)); return (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1); }
  if (p > hi) return -qnorm(1 - p);
  const q = p - 0.5, r = q * q;
  return (((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q / (((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1);
}

// Users per arm for a two-sided pooled-variance two-proportion z test.
export function nPerArm(p1, relLift, alpha = 0.05, power = 0.8) {
  const za = qnorm(1 - alpha / 2), zb = qnorm(power);
  const p2 = p1 * (1 + relLift), pbar = (p1 + p2) / 2;
  const num = (za * Math.sqrt(2 * pbar * (1 - pbar)) + zb * Math.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2;
  return num / (p2 - p1) ** 2;
}

// Smallest relative lift detectable at nArm users per arm (bisection).
export function mde(p1, nArm, alpha = 0.05, power = 0.8) {
  let lo = 1e-6, hi = Math.min(5, 1 / p1 - 1 - 1e-9);
  if (nPerArm(p1, hi, alpha, power) > nArm) return null;
  for (let i = 0; i < 80; i++) { const m = (lo + hi) / 2; nPerArm(p1, m, alpha, power) > nArm ? (lo = m) : (hi = m); }
  return hi;
}

// Seeded PRNG so a given seed always gives the same simulation.
export function mulberry32(seed) {
  return () => { seed |= 0; seed = (seed + 0x6d2b79f5) | 0; let t = Math.imul(seed ^ (seed >>> 15), 1 | seed); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
}

// Binomial draw by CDF inversion: O(n*p) per draw, fast at click-through rates.
export function rbinom(n, p, rand) {
  const q = 1 - p, s = p / q, a = (n + 1) * s;
  let r = q ** n, u = rand(), x = 0;
  while (u > r) { u -= r; x++; if (x > n) return n; r *= a / x - s; }
  return x;
}

const Z_CRIT = qnorm(0.975);

// Peeking simulation. Returns rejection rates and the z path of the first `keepPaths` runs.
export function simulatePeeking({ p, lift = 0, looks = 7, perLook = 500, runs = 20000, tauMix = 0.001, alpha = 0.05, seed = 20261106, keepPaths = 40 }) {
  const rand = mulberry32(seed), pt = p * (1 + lift), thresh = 1 / alpha;
  let anyNaive = 0, finalNaive = 0, msprt = 0;
  const paths = [];
  for (let i = 0; i < runs; i++) {
    let ct = 0, cc = 0, hitNaive = false, hitM = false, z = 0;
    const path = i < keepPaths ? [] : null;
    for (let k = 1; k <= looks; k++) {
      ct += rbinom(perLook, pt, rand); cc += rbinom(perLook, p, rand);
      const n = k * perLook, pool = (ct + cc) / (2 * n), v = pool * (1 - pool) * (2 / n);
      z = v > 0 ? (ct / n - cc / n) / Math.sqrt(v) : 0;
      if (Math.abs(z) > Z_CRIT) hitNaive = true;
      const lam = Math.sqrt(v / (v + tauMix ** 2)) * Math.exp((z * z / 2) * (tauMix ** 2 / (v + tauMix ** 2)));
      if (lam >= thresh) hitM = true;
      if (path) path.push(z);
    }
    if (hitNaive) anyNaive++;
    if (Math.abs(z) > Z_CRIT) finalNaive++;
    if (hitM) msprt++;
    if (path) paths.push(path);
  }
  return { anyNaive: anyNaive / runs, finalNaive: finalNaive / runs, msprt: msprt / runs, paths, runs };
}

// Wilson 95% interval for a proportion.
export function wilson(phat, n, z = 1.959964) {
  const den = 1 + z * z / n, c = (phat + z * z / (2 * n)) / den;
  const h = (z / den) * Math.sqrt(phat * (1 - phat) / n + z * z / (4 * n * n));
  return [c - h, c + h];
}
