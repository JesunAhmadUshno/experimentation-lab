# Pre-registration: Question Headlines, Click-Through Rate, and Whether Observational Estimates Recover a Randomized Benchmark

Status: LOCKED at the commit that introduces this file. Any later change is an amendment. Amendments are dated, appended at the end of this file, and never applied silently to the locked analysis.
Study owner: Jesun Ahmad Ushno.
Registration type: self-registration in this git repository. This is not a peer-reviewed registered report, and it is never described as one. An OSF registration of this document is planned but held (see DECISIONS.md, item D4). Until it exists, this git commit is the only registration.

## 1. Background and gap

The owner's public record contains no A/B testing, hypothesis testing, or causal inference work. This study closes that gap with one pre-registered study on public data, run under the AI Platform Research Programme charter's ten gates. The dataset is the Upworthy Research Archive (Matias, Munger, Le Quere and Ebersole, Scientific Data 2021, DOI 10.1038/s41597-021-00934-7; dataset DOI 10.17605/OSF.IO/JD64P; licence CC BY 4.0).

## 2. Data scope decision (binding)

Only the exploratory file of the archive is used: `upworthy-archive-exploratory-packages-03.12.2020.csv`, published on the archive's OSF project. The confirmatory file is never downloaded and never read in this study. Its access terms are unresolved (the archive team describes it as shared after peer review of an analysis plan), and downloading it without that approval would compromise the study. The holdout and undeployed files are also out of scope.

Documented size of the exploratory set (archive documentation): 22,666 packages in 4,873 tests. The fetch step (U4) verifies the downloaded file against the OSF-published SHA-256 and reports the actual row and test counts. Any mismatch is reported, not repaired silently.

## 3. Split protocol (binding, executed before any outcome column is read)

The exploratory tests are split by `clickability_test_id` into a development split (20 percent) and a locked split (80 percent), using seed 20261106 and a recorded shuffle of the sorted unique test IDs. The seed, the split assignment rule, and the SHA-256 hashes of both test-ID lists are committed to `prereg/split.json` before any analysis code runs on outcome data (the `clicks` column). The split generator reads only the `clickability_test_id` column.

Rules for the locked split:
- The locked split is analysed by exactly one script, `src/explab/primary.py`, under the frozen analysis plan in section 6.
- No parameter, exclusion, label rule, or estimator choice may change after the locked run on the basis of the locked run.
- Reproduction runs of the frozen pipeline (section 10) re-execute the same script and must produce identical outputs. They are the same look, not new looks.
- All development, tuning, debugging, the causal arm, and the stress tests run on the development split only.

## 4. Research questions

Primary question (one, falsifiable): In randomized Upworthy headline tests, does phrasing a headline as a question change click-through rate (CTR), compared with non-question headlines shown in the same test?

Secondary question (causal arm, methods question): Can a cross-test observational comparison on the development split recover the randomized within-test estimate for the same contrast, after propensity adjustment on observed covariates?

Supporting question (methods): How large is the false-positive inflation from repeated peeking at a fixed-horizon test on archive-calibrated streams, and does an always-valid sequential test (mSPRT) hold its error rate on the same streams?

## 5. Hypotheses

H1 (primary): The pooled within-test log odds ratio of click for question versus non-question headlines is not equal to 0. Two-sided, alpha 0.05.
H0: the pooled log odds ratio equals 0.

H2 (equivalence): The pooled effect lies inside the smallest effect size of interest band, plus or minus 5 percent relative CTR. Tested by TOST on the log odds ratio scale with bounds log(0.95) and log(1.05) and a 90 percent confidence interval.

H3 (causal arm): The propensity-adjusted cross-test estimate on the development split differs from the randomized development-split benchmark. The size and direction of the gap, with a bootstrap interval, is the result. No direction is predicted.

H4 (sequential): On A/A streams calibrated to the archive baseline, seven fixed-horizon looks inflate the Type I error rate above 10 percent, while the mSPRT always-valid test keeps it at or below 5 percent plus Monte Carlo error.

## 6. Primary analysis plan (frozen)

Unit: one test (one `clickability_test_id`) in the locked split, after exclusions (section 7) and eligibility (section 8).
Within each test, clicks and impressions are summed over question packages and over non-question packages, giving one 2 by 2 table per test: (clicks_q, nonclicks_q, clicks_nq, nonclicks_nq), where nonclicks = impressions minus clicks.
Label rule (frozen): a package is a question package if its headline, after stripping leading and trailing whitespace, ends with the character "?". No other labelling is used in the primary analysis. The label audit (section 9) measures the error rate of this rule; it does not change the rule.
Per-test effect: log odds ratio, log((clicks_q * nonclicks_nq) / (nonclicks_q * clicks_nq)), with standard error sqrt(1/clicks_q + 1/nonclicks_q + 1/clicks_nq + 1/nonclicks_nq). If any cell is 0, 0.5 is added to all four cells of that test (continuity correction, applied per test, reported count included in the output).
Pooling: DerSimonian and Laird random-effects meta-analysis across tests. Outputs: number of tests, pooled log odds ratio, odds ratio, 95 percent confidence interval, 90 percent confidence interval, tau, tau squared, I squared.
One look: the locked analysis is run once under this plan. Its output file is `results/primary_locked.json`, generated by script.

Verdict rule (frozen), applied to the locked run in this order:
1. Sample size floor: if the number of eligible locked tests is below 190, the verdict is INCONCLUSIVE unless the 95 percent confidence interval lies fully outside the plus or minus 10 percent relative band (log(0.90), log(1.10)) on one side, in which case the verdict is CONFIRMED. (Reason: at the archive mean arm size, 190 tests is the pre-computed requirement for 80 percent power at a 5 percent relative effect under between-test SD tau = 0.15. See the power module.)
2. CONFIRMED: the 95 percent confidence interval excludes 0.
3. REFUTED: the 90 percent confidence interval lies fully inside (log(0.95), log(1.05)).
4. INCONCLUSIVE: anything else.

## 7. Exclusions (frozen, applied in this order)

E1. Rows with `problem` equal to 1 are dropped. The archive flags these tests for randomization problems (2024 documentation update).
E2. Tests whose first observed package date falls in the window 2013-06-25 to 2014-01-10 inclusive are dropped. The archive documentation discourages confirmatory use of tests from this window. The test date is the minimum `first_created_at_date` among the test's packages in the file. If the file's date column differs in name or form, the exact column used is recorded in RESULTS.md and the deviation is flagged in AUDIT.md.
E3. Packages with impressions equal to 0 carry no information and are dropped before aggregation. Tests left with no packages are dropped.
These exclusions apply identically to both splits and to every analysis in this study.

## 8. Eligibility (frozen)

A test is eligible for the primary analysis if, after exclusions, it contains at least one question package and at least one non-question package, and both groups have total impressions above 0.

## 9. Guardrails and label audit (frozen)

Data guardrails (integrity only; the archive holds no business metrics, and none are claimed):
G1. Problem-flag rate: share of exploratory rows and of tests dropped by E1, reported as counts.
G2. Balance check: across eligible tests, the pooled log ratio of impressions per package in question versus non-question groups, with a 95 percent interval. Under randomization this should be near 0. It is reported as a number, not a pass or fail stamp.
G3. Placebo: the same pooled comparison with impressions per package as the outcome (a quantity the headline text cannot cause within a randomized test). Reported as a number with an interval.

Label audit: a seeded random sample of 200 packages from the development split (100 labelled question, 100 labelled non-question, seed 20261106) is read by a human reviewer (the study owner or the building agent acting as reviewer; the reviewer is named in the audit output). Clear mislabels are counted. The measured error rate is reported. The label rule does not change.

## 10. Supporting modules (frozen designs)

Power module (no outcome data): reproduces the research pack's calculations C3 (single-test sample size at baseline CTR 1.54 percent, alpha 0.05 two-sided, power 0.80), C4 (tests needed for the pooled analysis across tau values 0, 0.05, 0.10, 0.15), and C5 (peeking simulation, section H4 design), with seed 20261106 and 200,000 simulation runs. Inputs C1 and C2 are estimates from published totals (5.7M clicks over 370M impressions; 538,272,878 assignments over 150,817 arms) and are labelled estimates everywhere they appear.

Sequential module: mSPRT after Johari, Pekelis and Walsh (arXiv 1512.04922; Operations Research 2022), on the difference in proportions scale with plug-in pooled variance and mixing standard deviation tau_mix = 0.001 (fixed here, roughly the size of a 6.5 percent relative effect at the archive baseline; the value affects power, not the error guarantee). Streams: Bernoulli draws at baseline 1.54 percent in both arms (A/A) and at a 5 percent relative lift (A/B), looks every 500 impressions per arm up to 3,500 per arm, 200,000 runs, seed 20261106. Outputs: naive peeking Type I rate, final-look Type I rate, mSPRT Type I rate, mSPRT power under the lift.

Causal arm (development split only): package-level cross-test contrast. Treatment: question label. Outcome: package clicks and impressions. Covariates: test week of the package's test, headline length in characters, headline sentiment score from the small documented lexicon in `src/explab/features.py`, and eyecatcher reuse (1 if the package's eyecatcher_id appears on more than one package in the development data, else 0). Estimators: (a) inverse propensity weighting with propensities from logistic regression on the covariates, weights trimmed to the [0.01, 0.99] propensity range (trimmed package count reported); (b) 1 to 1 nearest-neighbour matching on the logit propensity, caliper 0.2 standard deviations of the logit, without replacement. Effect scale: log odds ratio computed from adjusted aggregate click and impression totals. Balance: standardized mean differences for every covariate before and after adjustment, target below 0.1 in absolute value after adjustment; failures are reported as failures. Benchmark: the primary estimator of section 6 run on the development split. Gap: adjusted estimate minus benchmark, with a cluster bootstrap interval (resample tests with replacement, 2,000 resamples, seed 20261106). An overlap plot of propensities by group is saved to `reports/propensity_overlap.png`.

Stress tests (development split only): (a) placebo outcome of G3 computed by the primary estimator machinery; (b) negative control: the primary estimator applied to the label "headline starts with the word The", a feature with no registered hypothesis; (c) sensitivity: the E-value of the observational point estimate on the risk ratio scale, and the bias factor (in log odds units) that an unmeasured confounder would need to fully explain the observational gap to the benchmark. Each test reports a number.

## 11. Reproduction

One command, `make reproduce`, on a clean machine: installs pinned dependencies, downloads the exploratory file, verifies its SHA-256, regenerates every result file and both generated reports, and diffs them against the committed copies. Exit code is nonzero on any mismatch.

## 12. Overclaim guard (binding on all prose in this repository)

- Never claim that question headlines drive or cause clicks in general. Any effect statement covers Upworthy, 2013 to 2015, outside the excluded window only.
- Never claim any guardrail result beyond data integrity. No business guardrails exist in this data.
- Never claim the observational arm discovered anything. It measures method error against a known benchmark.
- Never call this study peer-reviewed pre-registered. It is a self-registration in git.
- Never claim production A/B testing experience. This is a reanalysis of archived experiments.
- Never present the pack's C1, C2, or C4 numbers as measured on the data. They are estimates until the fetch and primary modules run.
- The headline question has prior published work, including a direct estimate on the archive's confirmatory set (Fang and Wheeler 2026; see docs/related_work.md). Novelty is claimed only for the methods components: the within-study observational recovery measurement, the sequential module on archive-calibrated streams, and the fully reproducible pre-registered pipeline. The related work file governs the exact wording.

## 13. Amendments

None at lock time.

Amendment log (append-only):
- (empty)
