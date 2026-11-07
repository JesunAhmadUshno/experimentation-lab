import { useMemo, useState, useEffect, useCallback } from 'react';
import primary from '../../results/primary_locked.json';
import seq from '../../results/sequential.json';
import power from '../../results/power.json';
import causal from '../../results/causal.json';
import stress from '../../results/stress.json';
import labelAudit from '../../results/label_audit.json';
import perTestCsv from '../../results/per_test_locked.csv?raw';
import { nPerArm, mde, simulatePeeking, wilson } from './stats.js';

const REPO = 'https://github.com/JesunAhmadUshno/experimentation-lab';
const blob = (p) => `${REPO}/blob/main/${p}`;
const pct = (x, d = 1) => `${(x * 100).toFixed(d)}%`;
const fmt = (n) => Math.round(n).toLocaleString('en-US');

const perTest = perTestCsv.trim().split('\n').slice(1).map((line) => {
  const c = line.split(',');
  const logor = +c[5], se = Math.sqrt(+c[6]);
  return { id: c[0], logor, lo: logor - 1.96 * se, hi: logor + 1.96 * se, n: +c[2] + +c[4] };
});

const SECTIONS = [['top', 'Overview', '◎'], ['effect', 'Effect', '▥'], ['peeking', 'Peeking', '◷'], ['power', 'Power', '⚡'], ['causal', 'Causal', '⇄'], ['robust', 'Robustness', '✓'], ['reproduce', 'Reproduce', '❯_']];

function useReveal() {
  useEffect(() => {
    const els = document.querySelectorAll('.reveal');
    if (!('IntersectionObserver' in window)) { els.forEach((e) => e.classList.add('in')); return; }
    const io = new IntersectionObserver((es) => es.forEach((e) => { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } }), { threshold: 0.08 });
    els.forEach((e) => io.observe(e));
    return () => io.disconnect();
  }, []);
}

function MenuBar() {
  const [now, setNow] = useState(() => new Date());
  useEffect(() => { const t = setInterval(() => setNow(new Date()), 30000); return () => clearInterval(t); }, []);
  return (
    <div className="menubar" role="banner">
      <span className="apple" aria-hidden="true">◆</span>
      <a className="app" href="#top">Experimentation Lab</a>
      <a className="m" href={blob("prereg/PREREG.md")}>Pre-registration</a>
      <a className="m" href={blob("METHODS.md")}>Methods</a>
      <a className="m" href={blob("RESULTS.md")}>Results</a>
      <span className="spacer" />
      <span className="status"><i /> CI reproducible</span>
      <a href={REPO}>GitHub ↗</a>
      <span className="clock">{now.toLocaleString('en-US', { weekday: 'short', hour: 'numeric', minute: '2-digit' })}</span>
    </div>
  );
}

function Dock() {
  const [active, setActive] = useState('top');
  useEffect(() => {
    const io = new IntersectionObserver((es) => es.forEach((e) => e.isIntersecting && setActive(e.target.id)), { rootMargin: '-45% 0px -50% 0px' });
    SECTIONS.forEach(([id]) => { const el = document.getElementById(id); if (el) io.observe(el); });
    return () => io.disconnect();
  }, []);
  return (
    <nav className="dock" aria-label="Sections">
      {SECTIONS.map(([id, label, icon]) => (
        <a key={id} href={`#${id}`} className={active === id ? 'on' : ''} aria-current={active === id ? 'true' : undefined}>
          <span className="ico" aria-hidden="true">{icon}</span><span className="lbl">{label}</span>
        </a>
      ))}
    </nav>
  );
}

export default function App() {
  useReveal();
  return (
    <div className="wrap">
      <MenuBar />
      <div className="glow" aria-hidden="true" />
      <Hero />
      <Effect />
      <Peeking />
      <Power />
      <Causal />
      <Robustness />
      <Reproduce />
      <Dock />
      <footer>
        Data: Upworthy Research Archive (Matias et al., 2021), CC BY 4.0. Code: Apache-2.0. Every number on this page is read from <code>results/</code> at build time; the simulators run in your browser.
      </footer>
    </div>
  );
}

function Hero() {
  const orDrop = 1 - primary.odds_ratio;
  return (
    <header className="card hero window" id="top" data-title="experimentation-lab — README">
      <div className="head">
        <p className="eyebrow">Pre-registered study · locked split</p>
        <span className={`pill ${primary.verdict === 'CONFIRMED' ? 'good' : 'warn'}`}>● {primary.verdict}</span>
      </div>
      <h1>Question headlines <em>cost clicks</em>: {pct(orDrop)} lower odds across {primary.n_tests} randomized tests.</h1>
      <p className="sub">
        A reanalysis of real A/B tests from the Upworthy Research Archive, registered and hashed before any outcome was read.
        It measures two ways product teams fool themselves: tests too small to see what they claim, and observational comparisons read as if they were randomized.
        Each claim below comes with its uncertainty, and the simulators let you rerun the logic yourself.
      </p>
      <div className="actions">
        <a className="btn primary" href="#peeking">Run the peeking simulator</a>
        <a className="btn ghost" href={blob('prereg/PREREG.md')}>Read the pre-registration</a>
        <span className="hint">Reproduce everything with <code>make reproduce</code></span>
      </div>
      <div className="tiles">
        <div className="tile"><div className="num">{primary.odds_ratio.toFixed(3)}</div><div className="cap">Pooled odds ratio, 95% CI {primary.ci95_odds_ratio[0].toFixed(3)} to {primary.ci95_odds_ratio[1].toFixed(3)}</div></div>
        <div className="tile"><div className="num">{seq.aa.naive_any_look_percent}%</div><div className="cap">False positives from peeking 7 times (should be 5%)</div></div>
        <div className="tile"><div className="num">{power.c3_min_detectable_effect_percent_at_mean_arm}%</div><div className="cap">Smallest lift a typical test here could detect</div></div>
        <div className="tile"><div className="num">{(labelAudit.error_rate * 100).toFixed(1)}%</div><div className="cap">Label-rule error in a 200-headline audit</div></div>
      </div>
    </header>
  );
}

function Effect() {
  const [sort, setSort] = useState('effect');
  const [hover, setHover] = useState(null);
  const rows = useMemo(() => {
    const r = [...perTest];
    if (sort === 'effect') r.sort((a, b) => a.logor - b.logor);
    if (sort === 'size') r.sort((a, b) => b.n - a.n);
    return r;
  }, [sort]);
  const W = 960, H = 300, pad = { l: 44, r: 12, t: 12, b: 28 };
  const lo = -1.6, hi = 1.6;
  const y = (v) => pad.t + (1 - (Math.max(lo, Math.min(hi, v)) - lo) / (hi - lo)) * (H - pad.t - pad.b);
  const x = (i) => pad.l + (i + 0.5) * ((W - pad.l - pad.r) / rows.length);
  const bw = Math.max(1, (W - pad.l - pad.r) / rows.length - 0.6);
  const negShare = perTest.filter((t) => t.logor < 0).length / perTest.length;
  return (
    <section id="effect" className="card window reveal" data-title="forest_plot.svg — 465 tests">
      <div className="head">
        <div>
          <p className="eyebrow">Primary result</p>
          <h2>Every test, one dot. The pooled effect sits clearly below zero.</h2>
          <p className="sub">
            Each bar is one randomized test: the log odds ratio of question versus non-question headlines, with its 95% interval.
            {' '}{pct(negShare, 0)} of tests point negative. The blue band is the random-effects pooled estimate, {primary.log_or} ({primary.ci95_log_or[0]} to {primary.ci95_log_or[1]}).
            Heterogeneity is high (I² {primary.i2_percent.toFixed(0)}%, τ {primary.tau}), so this is an average over contexts that differ.
          </p>
        </div>
        <div className="seg" role="group" aria-label="Sort tests">
          {[['effect', 'By effect'], ['size', 'By sample size'], ['none', 'Original order']].map(([k, l]) => (
            <button key={k} aria-pressed={sort === k} onClick={() => setSort(k)}>{l}</button>
          ))}
        </div>
      </div>
      <svg className="chart" viewBox={`0 0 ${W} ${H}`} role="img" aria-label={`Forest plot of ${perTest.length} per-test log odds ratios`} onMouseLeave={() => setHover(null)}>
        {[-1.5, -1, -0.5, 0, 0.5, 1, 1.5].map((t) => (
          <g key={t}><line className="axis" x1={pad.l} x2={W - pad.r} y1={y(t)} y2={y(t)} strokeWidth={t === 0 ? 1.5 : 1} /><text x={pad.l - 8} y={y(t) + 4} textAnchor="end">{t}</text></g>
        ))}
        <rect x={pad.l} width={W - pad.l - pad.r} y={y(primary.ci95_log_or[1])} height={y(primary.ci95_log_or[0]) - y(primary.ci95_log_or[1])} fill="var(--primary)" opacity="0.22" />
        <line x1={pad.l} x2={W - pad.r} y1={y(primary.log_or)} y2={y(primary.log_or)} stroke="var(--primary)" strokeWidth="2" />
        {rows.map((t, i) => (
          <g key={t.id} onMouseEnter={() => setHover(t)}>
            <line x1={x(i)} x2={x(i)} y1={y(t.lo)} y2={y(t.hi)} stroke={t.logor < 0 ? 'var(--bad)' : 'var(--good)'} strokeOpacity={hover && hover.id !== t.id ? 0.15 : 0.35} strokeWidth={bw} />
            <circle cx={x(i)} cy={y(t.logor)} r={hover?.id === t.id ? 4 : 1.6} fill={t.logor < 0 ? 'var(--bad)' : 'var(--good)'} />
          </g>
        ))}
        <text x={pad.l} y={H - 6}>{rows.length} tests ({sort === 'size' ? 'largest first' : sort === 'effect' ? 'sorted by effect' : 'archive order'})</text>
        <text x={W - pad.r} y={H - 6} textAnchor="end">log odds ratio, clipped to ±1.6</text>
      </svg>
      <div className="tip" aria-live="polite">
        {hover ? <>Test <span className="mono">{hover.id.slice(0, 10)}…</span>: log OR {hover.logor.toFixed(3)} (95% CI {hover.lo.toFixed(2)} to {hover.hi.toFixed(2)}), {fmt(hover.n)} impressions</> : 'Hover a bar to inspect a single test.'}
      </div>
    </section>
  );
}

function Peeking() {
  const [p, setP] = useState(power.c1_baseline_ctr_percent / 100);
  const [looks, setLooks] = useState(7);
  const [perLook, setPerLook] = useState(500);
  const [runs, setRuns] = useState(20000);
  const [lift, setLift] = useState(0);
  const [seed, setSeed] = useState(seq.seed);
  const [res, setRes] = useState(null);
  const [busy, setBusy] = useState(false);
  const run = useCallback(() => {
    setBusy(true);
    // Yield one frame so the button shows its busy state before the simulation blocks.
    requestAnimationFrame(() => setTimeout(() => {
      const t0 = performance.now();
      const r = simulatePeeking({ p, lift, looks, perLook, runs, seed, tauMix: seq.tau_mix });
      setRes({ ...r, ms: performance.now() - t0, looks });
      setBusy(false);
    }, 0));
  }, [p, lift, looks, perLook, runs, seed]);
  useEffect(() => { run(); }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const isDefault = looks === 7 && perLook === 500 && lift === 0;
  const W = 460, H = 240, pad = { l: 32, r: 8, t: 10, b: 24 };
  const zmax = 4;
  const sx = (k) => pad.l + (k / Math.max(1, (res?.looks ?? looks) - 1)) * (W - pad.l - pad.r);
  const sy = (z) => pad.t + (1 - (Math.max(-zmax, Math.min(zmax, z)) + zmax) / (2 * zmax)) * (H - pad.t - pad.b);
  const bars = res && [
    { k: 'Peek at every look (naive)', v: res.anyNaive, ref: isDefault ? seq.aa.naive_any_look_percent / 100 : null, c: 'var(--bad)' },
    { k: 'Look once at the end (fixed horizon)', v: res.finalNaive, ref: isDefault ? seq.aa.naive_final_look_type1_or_power_percent / 100 : null, c: 'var(--warn)' },
    { k: 'mSPRT, always-valid sequential test', v: res.msprt, ref: isDefault ? seq.aa.msprt_any_look_percent / 100 : null, c: 'var(--good)' },
  ];
  const scale = 0.4;
  return (
    <section id="peeking" className="card window reveal" data-title="peeking_simulator — live">
      <div className="head">
        <div>
          <p className="eyebrow">Live simulation</p>
          <h2>Peek at a test seven times and a 5% false-alarm rate becomes 16%.</h2>
          <p className="sub">
            This runs real Bernoulli A/B tests in your browser with no true difference (an A/A test, unless you add a lift).
            Checking the p-value after every batch and stopping at the first "win" inflates false positives. A mixture sequential test (mSPRT, Johari et al.) stays valid however often you look.
          </p>
        </div>
        <span className="pill info">{runs.toLocaleString()} runs in {res ? `${res.ms.toFixed(0)} ms` : '…'}</span>
      </div>
      <div className="controls">
        <Range label="Baseline click-through" value={p} min={0.005} max={0.1} step={0.0005} onChange={setP} show={pct(p, 2)} />
        <Range label="Number of looks" value={looks} min={1} max={20} step={1} onChange={setLooks} show={looks} />
        <Range label="Users per arm per look" value={perLook} min={100} max={5000} step={100} onChange={setPerLook} show={fmt(perLook)} />
        <Range label="True relative lift" value={lift} min={0} max={0.5} step={0.01} onChange={setLift} show={lift === 0 ? 'none (A/A)' : `+${pct(lift, 0)}`} />
        <div className="field"><label htmlFor="runs">Simulated tests</label>
          <select id="runs" value={runs} onChange={(e) => setRuns(+e.target.value)}>
            {[2000, 20000, 100000, 200000].map((n) => <option key={n} value={n}>{n.toLocaleString()}</option>)}
          </select>
        </div>
        <div className="field"><label htmlFor="seed">Seed</label><input id="seed" type="number" value={seed} onChange={(e) => setSeed(+e.target.value || 1)} /></div>
      </div>
      <div className="actions" style={{ marginTop: 0, marginBottom: 16 }}>
        <button className="btn primary" onClick={run} disabled={busy}>{busy ? 'Simulating…' : 'Run simulation'}</button>
        <span className="hint">{isDefault ? 'Black ticks mark the study’s 200,000-run results.' : 'Black ticks appear only at the study settings (7 looks, 500 per look, no lift).'}</span>
      </div>
      {res && (
        <div className="grid2">
          <div>
            <h3>{lift === 0 ? 'False-positive rate' : 'Rejection rate (power)'}</h3>
            <div className="bars" style={{ marginTop: 12 }}>
              {bars.map((b) => {
                const ci = wilson(b.v, res.runs);
                return (
                  <div className="bar-row" key={b.k}>
                    <div className="lab"><span>{b.k}</span><b>{pct(b.v, 2)}</b></div>
                    <div className="track">
                      <div className="fill" style={{ width: `${Math.min(100, (b.v / scale) * 100)}%`, background: b.c }} />
                      <div className="alpha" style={{ left: `${(0.05 / scale) * 100}%` }} />
                      {b.ref != null && <div className="ref" style={{ left: `${Math.min(100, (b.ref / scale) * 100)}%` }} title={`Study: ${pct(b.ref, 2)}`} />}
                    </div>
                    <div className="hint">95% CI {pct(ci[0], 2)} to {pct(ci[1], 2)}</div>
                  </div>
                );
              })}
            </div>
            <p className="hint" style={{ marginTop: 12 }}>Bar scale 0 to 40%. The dashed line marks the promised α = 5%.</p>
          </div>
          <div>
            <h3>z-statistic paths for the first 40 simulated tests</h3>
            <svg className="chart" viewBox={`0 0 ${W} ${H}`} role="img" aria-label="Z statistic paths across looks">
              <rect x={pad.l} width={W - pad.l - pad.r} y={sy(1.96)} height={sy(-1.96) - sy(1.96)} fill="var(--primary)" opacity="0.07" />
              {[-1.96, 0, 1.96].map((t) => <g key={t}><line className="axis" x1={pad.l} x2={W - pad.r} y1={sy(t)} y2={sy(t)} strokeDasharray={t ? '4 4' : ''} /><text x={pad.l - 6} y={sy(t) + 4} textAnchor="end">{t}</text></g>)}
              {res.paths.map((path, i) => {
                const crosses = path.some((z) => Math.abs(z) > 1.96);
                return <polyline key={i} fill="none" stroke={crosses ? 'var(--bad)' : 'var(--primary)'} strokeOpacity={crosses ? 0.9 : 0.28} strokeWidth={crosses ? 1.6 : 1} points={path.map((z, k) => `${sx(k)},${sy(z)}`).join(' ')} />;
              })}
              <text x={pad.l} y={H - 4}>look 1</text><text x={W - pad.r} y={H - 4} textAnchor="end">look {res.looks}</text>
            </svg>
            <p className="hint">Red paths cross ±1.96 at some look: a naive analyst would have called a winner.</p>
          </div>
        </div>
      )}
    </section>
  );
}

function Range({ label, value, min, max, step, onChange, show }) {
  const id = label.replace(/\W+/g, '-').toLowerCase();
  return (
    <div className="field">
      <label htmlFor={id}>{label} <span>{show}</span></label>
      <input id={id} type="range" min={min} max={max} step={step} value={value} onChange={(e) => onChange(+e.target.value)} />
    </div>
  );
}

function Power() {
  const [p, setP] = useState(power.c1_baseline_ctr_percent / 100);
  const [lift, setLift] = useState(0.1);
  const [n, setN] = useState(power.c2_mean_arm_size_rounded);
  const need = nPerArm(p, lift);
  const detect = mde(p, n);
  const curve = useMemo(() => Array.from({ length: 60 }, (_, i) => { const l = 0.02 + i * 0.01; return [l, nPerArm(p, l)]; }), [p]);
  const W = 460, H = 220, pad = { l: 52, r: 8, t: 10, b: 24 };
  const lx = (l) => pad.l + ((l - 0.02) / 0.59) * (W - pad.l - pad.r);
  const ly = (v) => pad.t + (1 - (Math.log10(Math.min(3e6, Math.max(300, v))) - 2.5) / 4) * (H - pad.t - pad.b);
  return (
    <section id="power" className="card window reveal" data-title="power_calculator">
      <p className="eyebrow">Power calculator</p>
      <h2>Most of these tests could only see huge effects.</h2>
      <p className="sub">
        At the archive’s mean arm size ({fmt(power.c2_mean_arm_size_rounded)} impressions) and {pct(power.c1_baseline_ctr_percent / 100, 2)} click-through, a test needs a {power.c3_min_detectable_effect_percent_at_mean_arm}% relative lift to reach 80% power.
        This calculator uses the same pooled two-proportion formula as <a href={blob('src/explab/power.py')}>power.py</a> and matches its tables to within 0.01% (the published baseline is rounded to four digits).
      </p>
      <div className="grid2" style={{ marginTop: 16 }}>
        <div>
          <div className="controls" style={{ gridTemplateColumns: '1fr' }}>
            <Range label="Baseline click-through" value={p} min={0.005} max={0.2} step={0.0005} onChange={setP} show={pct(p, 2)} />
            <Range label="Relative lift to detect" value={lift} min={0.01} max={0.6} step={0.01} onChange={setLift} show={`+${pct(lift, 0)}`} />
            <Range label="Users per arm you have" value={n} min={500} max={200000} step={500} onChange={setN} show={fmt(n)} />
          </div>
          <div className="tiles" style={{ gridTemplateColumns: '1fr 1fr', marginTop: 0 }}>
            <div className="tile"><div className="num">{fmt(need)}</div><div className="cap">users per arm to detect +{pct(lift, 0)} (α 0.05, power 0.80)</div></div>
            <div className="tile"><div className="num">{detect ? `+${pct(detect, 1)}` : 'n/a'}</div><div className="cap">smallest detectable lift with {fmt(n)} per arm</div></div>
          </div>
        </div>
        <div>
          <h3>Required users per arm by lift (log scale)</h3>
          <svg className="chart" viewBox={`0 0 ${W} ${H}`} role="img" aria-label="Sample size curve">
            {[3, 4, 5, 6].map((e) => <g key={e}><line className="axis" x1={pad.l} x2={W - pad.r} y1={ly(10 ** e)} y2={ly(10 ** e)} /><text x={pad.l - 6} y={ly(10 ** e) + 4} textAnchor="end">{e === 3 ? '1k' : e === 4 ? '10k' : e === 5 ? '100k' : '1M'}</text></g>)}
            <polyline fill="none" stroke="var(--primary)" strokeWidth="2.5" points={curve.map(([l, v]) => `${lx(l)},${ly(v)}`).join(' ')} />
            <line x1={pad.l} x2={W - pad.r} y1={ly(n)} y2={ly(n)} stroke="var(--warn)" strokeDasharray="5 4" />
            <text x={W - pad.r} y={ly(n) - 6} textAnchor="end" style={{ fill: 'var(--warn)' }}>you have {fmt(n)}</text>
            {lift <= 0.61 && <circle cx={lx(lift)} cy={ly(need)} r="5" fill="var(--primary)" stroke="var(--surface-strong)" strokeWidth="2" />}
            <text x={pad.l} y={H - 4}>+2%</text><text x={W - pad.r} y={H - 4} textAnchor="end">+61% relative lift</text>
          </svg>
        </div>
      </div>
    </section>
  );
}

function Causal() {
  const rows = [
    { k: 'Randomized benchmark (within test)', v: causal.benchmark_log_or, ci: causal.benchmark_bootstrap_ci95_log_or, c: 'var(--primary)' },
    { k: 'Naive cross-test comparison', v: causal.naive_log_or, ci: null, c: 'var(--muted)' },
    { k: 'Inverse probability weighting', v: causal.ipw.log_or, gap: causal.ipw.gap_to_benchmark, gapCi: causal.ipw.gap_bootstrap_ci95, c: 'var(--warn)' },
    { k: `Propensity matching (${causal.matching.n_pairs} pairs)`, v: causal.matching.log_or, gap: causal.matching.gap_to_benchmark, gapCi: causal.matching.gap_bootstrap_ci95, c: 'var(--bad)' },
  ];
  const W = 960, rowH = 44, H = rows.length * rowH + 30, l = 300, r = 20, lo = -0.45, hi = 0.45;
  const x = (v) => l + ((v - lo) / (hi - lo)) * (W - l - r);
  const bal = Object.entries(causal.balance);
  return (
    <section id="causal" className="card window reveal" data-title="causal_arm.py — IPW · matching">
      <p className="eyebrow">Causal arm</p>
      <h2>Can observational methods recover a randomized answer? Here, not precisely enough to tell.</h2>
      <p className="sub">
        The same question asked across tests instead of within them, adjusted for headline length, sentiment, reused images and week.
        IPW recovers part of the randomized effect and matching flips its sign, but both intervals include the benchmark, so the arm closes as a precision result. It’s published either way.
        Points are estimates; the blue band is the randomized benchmark’s cluster-bootstrap 95% CI. The table gives each method’s gap to the benchmark with its own bootstrap interval ({causal.bootstrap_runs.toLocaleString()} runs, <a href={blob('results/causal.json')}>causal.json</a>).
      </p>
      <svg className="chart" viewBox={`0 0 ${W} ${H}`} role="img" aria-label="Estimates of the question-headline effect by method" style={{ marginTop: 12 }}>
        {[-0.4, -0.2, 0, 0.2, 0.4].map((t) => <g key={t}><line className="axis" x1={x(t)} x2={x(t)} y1={0} y2={H - 22} strokeWidth={t === 0 ? 1.5 : 1} /><text x={x(t)} y={H - 6} textAnchor="middle">{t}</text></g>)}
        <rect x={x(causal.benchmark_bootstrap_ci95_log_or[0])} width={x(causal.benchmark_bootstrap_ci95_log_or[1]) - x(causal.benchmark_bootstrap_ci95_log_or[0])} y={0} height={H - 22} fill="var(--primary)" opacity="0.08" />
        {rows.map((row, i) => (
          <g key={row.k} transform={`translate(0 ${i * rowH + 22})`}>
            <text x={0} y={4} style={{ fill: 'var(--text)', fontSize: 13 }}>{row.k}</text>
            {row.ci && <line x1={x(row.ci[0])} x2={x(row.ci[1])} y1={0} y2={0} stroke={row.c} strokeWidth="3" strokeLinecap="round" opacity="0.6" />}
            <circle cx={x(row.v)} cy={0} r="6" fill={row.c} />
            <text x={x(row.v)} y={-10} textAnchor="middle" style={{ fill: 'var(--text)' }}>{row.v.toFixed(3)}</text>
          </g>
        ))}
      </svg>
      <div style={{ overflowX: 'auto', marginTop: 12 }}>
        <table>
          <thead><tr><th>Method</th><th>Estimate (log OR)</th><th>Gap to randomized benchmark</th><th>Gap 95% bootstrap CI</th><th>Reading</th></tr></thead>
          <tbody>
            {rows.filter((r) => r.gapCi).map((r) => (
              <tr key={r.k}><td>{r.k}</td><td>{r.v.toFixed(4)}</td><td>{r.gap.toFixed(4)}</td><td>{r.gapCi[0].toFixed(4)} to {r.gapCi[1].toFixed(4)}</td>
                <td><span className="pill warn">{r.gapCi[0] < 0 && r.gapCi[1] > 0 ? 'Indistinguishable' : 'Biased'}</span></td></tr>
            ))}
          </tbody>
        </table>
      </div>
      <h3 style={{ marginTop: 20 }}>Covariate balance (standardized mean difference, target |SMD| &lt; {causal.balance_target_abs_smd_below})</h3>
      <div style={{ overflowX: 'auto' }}>
        <table>
          <thead><tr><th>Covariate</th><th>Raw</th><th>After IPW</th><th>After matching</th></tr></thead>
          <tbody>
            {bal.map(([k, b]) => (
              <tr key={k}><td className="mono">{k}</td>
                {[b.smd_raw, b.smd_ipw, b.smd_matched].map((v, i) => <td key={i} className={Math.abs(v) < causal.balance_target_abs_smd_below ? 'ok' : 'no'}>{v.toFixed(3)}</td>)}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function Robustness() {
  const nc = stress.negative_control_starts_with_the, pl = stress.placebo_impressions_per_package, s = stress.sensitivity_ipw;
  const checks = [
    { t: 'Placebo: impressions per package', d: `Log ratio ${pl.log_ratio_impressions_per_package} (CI ${pl.ci95[0]} to ${pl.ci95[1]}). Randomization delivered balanced traffic, as it should.`, ok: pl.ci95[0] < 0 && pl.ci95[1] > 0 },
    { t: 'Negative control: headlines starting with “The”', d: `Log OR ${nc.log_or} (CI ${nc.ci95_log_or[0]} to ${nc.ci95_log_or[1]}, ${nc.n_tests} tests). An irrelevant feature shows no reliable effect.`, ok: nc.ci95_log_or[0] < 0 && nc.ci95_log_or[1] > 0 },
    { t: 'Sensitivity: E-value for the IPW gap', d: `E-value ${s.e_value}. An unmeasured confounder only this strong (risk ratio ${s.e_value} with both treatment and outcome) could explain the whole gap, so the causal arm is fragile, and the page says so.`, ok: null },
    { t: 'Label audit', d: `The question-mark rule mislabels ${(labelAudit.error_rate * 100).toFixed(1)}% of 200 hand-checked headlines, all misses. That dilutes the effect toward zero; it can’t create one.`, ok: true },
  ];
  return (
    <section id="robust" className="card window reveal" data-title="robustness_checks">
      <p className="eyebrow">Robustness and threats to validity</p>
      <h2>Checks designed to fail if the result were an artifact.</h2>
      <div className="grid2" style={{ marginTop: 16 }}>
        {checks.map((c) => (
          <div className="tile" key={c.t}>
            <div className="head" style={{ marginBottom: 6 }}><h3>{c.t}</h3><span className={`pill ${c.ok === null ? 'warn' : c.ok ? 'good' : 'bad'}`}>{c.ok === null ? 'Caveat' : c.ok ? 'Passes' : 'Fails'}</span></div>
            <p className="hint" style={{ margin: 0, fontSize: 13 }}>{c.d}</p>
          </div>
        ))}
      </div>
    </section>
  );
}

function Reproduce() {
  const docs = [
    ['prereg/PREREG.md', 'Pre-registration', 'Frozen plan, SHA-256 hashed'],
    ['HYPOTHESES.md', 'Hypotheses', 'Tests and falsification rules'],
    ['METHODS.md', 'Methods', 'Formulas, controls, threats'],
    ['RESULTS.md', 'Results', 'Generated, never hand-edited'],
    ['AUDIT.md', 'Audit', 'Claims, licence, data, grade'],
    ['docs/related_work.md', 'Related work', 'Prior answers and novelty claim'],
  ];
  return (
    <section id="reproduce" className="card window reveal" data-title="Terminal — make reproduce">
      <p className="eyebrow">Reproduce it</p>
      <h2>One command rebuilds every number, byte for byte.</h2>
      <ol className="steps" style={{ marginTop: 16 }}>
        <li><span className="n">1</span><div><b>Clone and run</b><div className="hint"><code>git clone {REPO}.git && cd experimentation-lab && make reproduce</code></div></div></li>
        <li><span className="n">2</span><div><b>Integrity gate</b><div className="hint">Downloads the exploratory archive file, checks its SHA-256, and reruns all modules with seed {seq.seed}.</div></div></li>
        <li><span className="n">3</span><div><b>Diff against the committed outputs</b><div className="hint">CI repeats this on Python 3.11 and 3.12. Any byte difference fails the build.</div></div></li>
      </ol>
      <div className="docs" style={{ marginTop: 20 }}>
        {docs.map(([p, t, d]) => <a key={p} href={blob(p)}><b>{t}</b><small>{d}</small></a>)}
      </div>
    </section>
  );
}
