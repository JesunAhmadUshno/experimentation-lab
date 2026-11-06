# Hypotheses

Pre-registered before any outcome data was read. The frozen source of these hypotheses is `prereg/PREREG.md`, sections 5 and 6. This file restates them in the programme charter's format. If the two disagree, PREREG.md governs. Verdicts are filled in from generated result files after the locked run; the verdict words allowed are those of charter gate 9: Supported, Partially supported, Refuted, Inconclusive, Not yet measured. The primary verdict words CONFIRMED, REFUTED, INCONCLUSIVE come from the frozen rule in PREREG.md section 6.

## H1. Question headlines change CTR within randomized tests

- Statement: the pooled within-test log odds ratio of click, question versus non-question packages, is not 0.
- Test: DerSimonian and Laird random-effects pooling of per-test log odds ratios on the locked split. 95 percent confidence interval, two-sided alpha 0.05.
- Falsified if: the 95 percent interval includes 0 (then H2 decides between REFUTED and INCONCLUSIVE).
- Sample size floor: 190 eligible locked tests, from the power module (C4). Below the floor, the capped verdict rule of PREREG.md section 6 applies.
- Status at registration: Not yet measured.

## H2. Any question-headline effect is smaller than the smallest effect of interest

- Statement: the pooled effect lies inside plus or minus 5 percent relative CTR.
- Test: TOST. The 90 percent confidence interval must lie fully inside (log(0.95), log(1.05)).
- Falsified if: any part of the 90 percent interval lies outside the band.
- Status at registration: Not yet measured.

## H3. A cross-test observational estimate does not recover the randomized benchmark

- Statement: the propensity-adjusted cross-test estimate on the development split differs from the randomized development-split benchmark. The signed gap and its cluster bootstrap interval are the result; no direction is predicted.
- Test: inverse propensity weighting and 1 to 1 propensity matching, covariates and rules frozen in PREREG.md section 10. Balance target: all standardized mean differences below 0.1 in absolute value after adjustment.
- Falsified if: both adjusted estimates' gaps have bootstrap intervals that include 0 and balance is achieved. (That outcome would mean recovery worked within measurement error.)
- Status at registration: Not yet measured.

## H4. Peeking inflates false positives; an always-valid test does not

- Statement: on A/A Bernoulli streams at the archive baseline (CTR 1.54 percent, looks every 500 impressions per arm up to 3,500), seven fixed-horizon looks push the Type I error rate above 10 percent, while mSPRT keeps it at or below 5 percent plus Monte Carlo error.
- Test: Monte Carlo, 200,000 runs, seed 20261106.
- Falsified if: the naive any-look rate is at or below 10 percent, or the mSPRT rate exceeds 5 percent by more than Monte Carlo error.
- Status at registration: Not yet measured.
