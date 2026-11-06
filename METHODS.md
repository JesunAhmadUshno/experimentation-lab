# Methods

The frozen plan is `prereg/PREREG.md`. This file explains the methods in the programme charter's format. If the two disagree, PREREG.md governs.

## Dataset

The Upworthy Research Archive, exploratory file only (`upworthy-archive-exploratory-packages-03.12.2020.csv`, 22,666 packages, 4,873 tests, CC BY 4.0). Each row is one package (arm) of one headline test: headline text, image id, impressions, clicks, dates. There is no user-level data. The confirmatory, holdout, and undeployed files are never downloaded (DECISIONS.md D1, D2).

Before any outcome column was read, the exploratory tests were split by `clickability_test_id` into a development split (974 tests) and a locked split (3,899 tests), seed 20261106, with both ID lists and their SHA-256 hashes committed in `prereg/split.json`.

## Exclusions

Test level: tests whose first package was created between 2013-06-25 and 2014-01-10 are dropped. This is the archive team's randomization-problem window (Author Correction, DOI 10.1038/s41597-024-03600-w; Amendment A1 explains why the window implements the problem-flag exclusion E1 in this file version). Row level: rows with zero impressions are dropped. Both apply to every analysis and both splits.

## Primary analysis

Unit: one test. Within a test, clicks and impressions are summed over question packages (headline ends with "?") and over non-question packages. Per-test log odds ratio:

log OR = log( (clicks_q x nonclicks_nq) / (nonclicks_q x clicks_nq) ), with variance 1/clicks_q + 1/nonclicks_q + 1/clicks_nq + 1/nonclicks_nq. If any cell is 0, 0.5 is added to all four cells of that test; the number of corrected tests is reported.

Pooling: DerSimonian and Laird random-effects meta-analysis. tau squared = max(0, (Q - (k - 1)) / C) with the standard Q and C. Reported: pooled log OR and odds ratio, 95 and 90 percent intervals, tau, I squared.

Verdict (frozen, PREREG section 6): with at least 190 eligible tests, CONFIRMED if the 95 percent interval excludes 0; REFUTED if the 90 percent interval lies inside (log 0.95, log 1.05); INCONCLUSIVE otherwise. Below 190 tests the verdict is INCONCLUSIVE unless the 95 percent interval lies fully outside the plus or minus 10 percent band.

## Power and sequential modules (simulations, no outcome data)

Baseline CTR 1.54 percent and mean arm size 3,569 are estimates from published totals (labelled wherever used). C3 uses the pooled-variance two-proportion z formula at alpha 0.05 (two-sided) and power 0.80. C4 derives the per-test log OR variance, 2 x (1/clicks + 1/nonclicks) at the mean arm size, and solves for the test count that gives 80 percent power at the 5 percent relative odds ratio under between-test SD tau.

Peeking: Bernoulli streams, 200,000 runs, seed 20261106, looks every 500 impressions per arm to 3,500. The naive test is the pooled two-proportion z test. The sequential test is the mixture sequential probability ratio test of Johari, Pekelis and Walsh, on the difference scale with plug-in pooled variance and mixing SD 0.001 (DECISIONS.md D8); rejection when the likelihood ratio first reaches 20.

## Causal arm (development split only)

Treatment: question label. Unit: package. Covariates: test week (weeks since the first test week in the split), headline length in characters, headline sentiment (small built-in lexicon, `src/explab/features.py`; DECISIONS.md D9), and eyecatcher reuse (the package's eyecatcher_id appears on more than one package in the split).

Propensities: logistic regression (Newton iterations, L2 penalty 1e-6) on the four covariates, continuous covariates standardized. IPW: Hajek-style weighted click rates with weights 1/e and 1/(1-e), propensities trimmed to [0.01, 0.99], trimmed count reported. Matching: 1 to 1 greedy nearest neighbour on the logit propensity, caliper 0.2 standard deviations of the logit, without replacement, most-constrained-first order. Effects are log odds ratios from the adjusted aggregate click and impression totals.

Balance: standardized mean differences per covariate, raw, after IPW weighting, and in the matched sample. Target: all adjusted values below 0.1 in absolute value. Failures are reported as failures.

Benchmark and gap: the primary estimator run on the same development split. Gaps (adjusted estimate minus benchmark) get cluster bootstrap intervals: tests resampled with replacement, 2,000 resamples, seed 20261106, all three estimators recomputed per resample, percentile intervals.

## Stress tests (development split only)

Placebo: the pooled log ratio of impressions per package (question over non-question), a quantity headline text cannot cause inside a randomized test. Negative control: the primary estimator with the label "headline starts with the word The". Sensitivity: the E-value of the IPW risk ratio, and the bias in log odds units that would be needed to explain the full IPW gap to the benchmark.

## Threats to validity

- One publisher, one period (2013 to 2015), advocacy content. Nothing transfers by assumption to current platforms.
- Aggregate data only: no user-level randomization checks are possible beyond the archive's own validation and the balance statistic.
- The label rule is a proxy: rhetorical questions without a final "?" are missed, and quoted questions are counted. The label audit measures the visible error rate on a sample; it does not fix the rule.
- Headline feature effects on this archive are context dependent (Le Quere et al. 2025): a single pooled number averages over contexts and can hide sign changes. tau and I squared are reported so the spread is visible.
- The causal arm's covariates are few and two are crude (lexicon sentiment; week). Unmeasured confounding is expected; the arm measures the miss, it does not claim adjustment success.
- Self-registration is weaker than a peer-reviewed registered report. The git history is the evidence offered, and its limits are stated wherever the study is described.
