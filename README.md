# Experimentation Lab

A pre-registered A/B testing and causal inference study on the Upworthy Research Archive.

## Problem

Product teams decide from A/B tests every day, and two failure modes are common: tests too small to detect the effects they claim to measure, and observational comparisons (across time, across stories, across audiences) read as if they were randomized. Both failure modes produce confident wrong decisions. This repository measures both, on real randomized data, against a known benchmark.

## Purpose

Close a verified gap in the owner's public record (no experimentation or causal inference work) with one study that is pre-registered before outcomes are read, locked by a committed data split, and reproducible with one command.

## Verdict

**CONFIRMED.** In the locked confirmatory split (465 eligible randomized tests), question headlines were associated with lower click-through than non-question headlines in the same tests: pooled odds ratio 0.8645 (95% CI 0.8335 to 0.8966). The effect is larger than the pre-registered smallest effect of interest (plus or minus 5 percent relative), in the negative direction. This replicates, on the exploratory split and under a different estimator, the direction Fang and Wheeler (2026) reported on the archive's confirmatory set. Full generated results: `RESULTS.md`. Verdict file: `reports/VERDICT.md`.

## Key measured results

| Quantity | Value | Source file |
| --- | --- | --- |
| Primary pooled log odds ratio (locked) | -0.1456 (95% CI -0.1821 to -0.1091) | results/primary_locked.json |
| Primary odds ratio (locked) | 0.8645 (95% CI 0.8335 to 0.8966) | results/primary_locked.json |
| Between-test SD tau (locked) | 0.3325 | results/primary_locked.json |
| Development split estimate (same estimator) | log OR -0.1494, 113 tests | results/primary_dev.json |
| Naive peeking false-positive rate (7 looks, A/A) | 16.32% (fixed-horizon: 5.03%) | results/sequential.json |
| mSPRT always-valid false-positive rate (A/A) | 0.00% | results/sequential.json |
| Observational miss, IPW (dev, log odds) | gap 0.1010 (bootstrap CI -0.0992 to 0.2978) | results/causal.json |
| Observational miss, matching (dev, log odds) | gap 0.1937 (bootstrap CI -0.0608 to 0.3372) | results/causal.json |
| Label rule error rate (200-headline audit) | 3.0% (all misses) | results/label_audit.json |
| Placebo (impressions per package, log ratio) | 0.0014 (CI -0.0022 to 0.0049) | results/guardrails.json |

Reading of the causal arm: the adjusted cross-test point estimates recover only part of the randomized effect (IPW) or flip its sign (matching), but the intervals are wide and include a zero gap, so the arm closes as a precision result: at development-split size, an observational miss of this size cannot be distinguished from recovery. The numbers are published either way.

## Architecture

- `prereg/`: the frozen pre-registration, its SHA-256, and the split lock (seed, both test-ID lists, list hashes, and the generator script).
- `src/explab/`: fetch (integrity gate), power, peeking (naive and mSPRT simulations), guardrails, label (rule plus audit), features (causal covariates), primary (the only script that analyses the locked split), causal (IPW, matching, cluster bootstrap), stress (placebo, negative control, sensitivity), report (generates RESULTS.md and reports/VERDICT.md from the JSON result files).
- `tests/`: unit tests, including known-answer tests that reproduce the research pack's power tables exactly.
- `results/`: every generated result file. No number in any document is hand-typed.
- CI: unit tests plus a full byte-identical reproduction on Python 3.11 and 3.12.

## Reproduction

```
make reproduce
```

Installs pinned dependencies, downloads the exploratory file, verifies its SHA-256, reruns every module, regenerates the split lock, `RESULTS.md`, and `reports/VERDICT.md`, and diffs them against the committed copies. Any byte difference fails.

## Limitations

- One publisher (Upworthy), 2013 to 2015, advocacy headlines, exploratory split only. Nothing here transfers by assumption to current platforms.
- This is a reanalysis of archived experiments, not production A/B testing experience, and the registration is a self-registration in git, not a peer-reviewed registered report.
- The headline question already had a published answer on the confirmatory set (Fang and Wheeler 2026). Novelty is claimed only for the methods components; see `docs/related_work.md`.
- The label rule sees only sentence-final question marks; the audit measures the cost (3.0 percent) and the dilution is real.
- Heterogeneity is high (tau 0.33): the pooled value is an average over contexts that differ.
- The archive holds no business guardrail metrics; guardrails here are data-integrity checks only.
- Full deduction list: `AUDIT.md` (build grade 6,600 of 10,000).

## Data and licence

Data: The Upworthy Research Archive (Matias et al., Scientific Data 2021, DOI 10.1038/s41597-021-00934-7; dataset DOI 10.17605/OSF.IO/JD64P), CC BY 4.0. Only the exploratory file is used; the confirmatory file is never downloaded (see `DECISIONS.md`). Code: Apache-2.0 (see `LICENSE`).

## Documents

- `prereg/PREREG.md`: the frozen pre-registration, with Amendment A1.
- `HYPOTHESES.md`: hypotheses, tests, falsification rules.
- `RESEARCH.md`: literature search record and horizons.
- `docs/related_work.md`: primary sources on the exact question, with the adjusted novelty claim.
- `METHODS.md`: datasets, controls, formulas, statistical plan, threats to validity.
- `RESULTS.md`: generated results. Never hand-edited.
- `reports/VERDICT.md`: generated primary verdict. Never hand-edited.
- `AUDIT.md`: security, cost, licence, data, and claim audit, with the build grade.
- `DECISIONS.md`: options, choices, reasons. Includes the two held items (archive team email, OSF registration).
- `ROADMAP.md`: what remains, in evidence order.
