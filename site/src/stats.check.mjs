// Known-answer self-check: node src/stats.check.mjs (numbers from results/*.json)
import assert from 'node:assert/strict';
import { nPerArm, mde, simulatePeeking } from './stats.js';
const p = 0.015405;
for (const [lift, want] of [[0.05, 411183], [0.10, 105261], [0.20, 27546], [0.50, 4996]])
  // results store the baseline CTR rounded to 6 digits, so allow 0.01% relative drift
  assert.ok(Math.abs(nPerArm(p, lift) / want - 1) < 1e-4, `n at ${lift}: ${nPerArm(p, lift)} vs ${want}`);
assert.equal(Math.round(mde(p, 3569) * 1000) / 10, 60.3);
const s = simulatePeeking({ p, runs: 20000 });
assert.ok(Math.abs(s.anyNaive - 0.1632) < 0.012, `naive any-look ${s.anyNaive}`);
assert.ok(Math.abs(s.finalNaive - 0.0503) < 0.007, `fixed horizon ${s.finalNaive}`);
assert.ok(s.msprt < 0.002, `msprt ${s.msprt}`);
console.log('stats ok', { anyNaive: s.anyNaive, finalNaive: s.finalNaive, msprt: s.msprt });
