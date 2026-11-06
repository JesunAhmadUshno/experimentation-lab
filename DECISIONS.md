# Decisions

Append-only. Each decision names the options, the choice, and the reason. Dates are 2026-11-06 unless stated.

## D1. Dataset: Upworthy Research Archive, exploratory file only

Options: (a) Upworthy exploratory file; (b) Upworthy confirmatory file; (c) Hillstrom email data; (d) Criteo uplift data.
Choice: (a).
Reason: one licence (CC BY 4.0) covers a randomized primary arm and an observational arm on the same platform; access is public and ungated. (b) is excluded by the binding adoption decision in the research pack: its access is unresolved and described by the archive team as gated behind peer review of an analysis plan. (c) has no explicit data licence. (d) has an unverified dataset licence.

## D2. Confirmatory access route: fallback adopted, email held

The research pack's upgrade U1 offers two routes: a written reply from the archive team, or the exploratory-split fallback. The email to the archive team is an external send and is HELD for the study owner's tap. It has not been sent. The fallback is adopted: the exploratory set is split 20 percent development and 80 percent locked, with the seed and test-ID hashes committed before any outcome column is read (see PREREG.md section 3).

## D3. OSF registration: held

Upgrade U3 asks for the pre-registration hash to be recorded in an OSF registration. Creating that registration needs the study owner's own OSF account action. It is HELD. The git-committed pre-registration in this repository proceeds now and is described honestly as self-registration.

## D4. Estimator: per-test aggregated 2 by 2 tables, DerSimonian and Laird pooling

Options: (a) aggregate clicks and impressions per group within each test, then pool per-test log odds ratios; (b) pair individual question and non-question packages inside each test.
Choice: (a).
Reason: (b) has no unique pairing when group sizes differ, and any pairing rule chosen after seeing the data is a researcher degree of freedom. (a) is deterministic, matches the meta-analytic design the power calculation assumes, and is frozen in PREREG.md section 6.

## D5. SESOI bounds on the odds ratio scale

The smallest effect of interest is plus or minus 5 percent relative CTR. The TOST bounds are applied to the odds ratio as log(0.95) and log(1.05). At the archive baseline (CTR near 1.5 percent) the odds ratio and the risk ratio differ by about 0.1 percent relative, far inside the band. Recorded here so the approximation is explicit, not hidden.

## D6. Novelty claim narrowed after the literature check (U2)

Fang and Wheeler (2026, DOI 10.1002/jcpy.70031) already estimated the question-framing contrast on this archive's confirmatory set. The novelty claim is therefore limited to the methods components listed in docs/related_work.md. The primary estimate on the exploratory split is reported as a replication under a different estimator.

## D7. Toolchain pins

Python with numpy 2.2.6, scipy 1.15.3, pandas 2.3.3, matplotlib 3.10.7, pytest 8.4.2. Chosen because the same pins install on Python 3.11 and 3.12 (the CI matrix), and numpy's PCG64 stream for a fixed seed is stable across these versions. All reported numbers are rounded at generation time (estimates to 4 decimal places, rates to 2 decimal places as percents) so that reproduction diffs test substance, not platform noise.

## D8. mSPRT mixing scale

tau_mix = 0.001 on the difference-in-proportions scale, fixed in PREREG.md section 10 before any simulation ran. The value sets the alternative the mixture averages over (roughly a 6.5 percent relative effect at baseline). It changes power, not the error control. Sensitivity to this choice is a Deep pass item (ROADMAP.md).

## D9. Sentiment covariate: small built-in lexicon

The causal arm needs a headline sentiment covariate (pack assumption set, PREREG.md section 10). Options: (a) an external lexicon download (for example VADER's lexicon via nltk); (b) a small word list shipped in the repo.
Choice: (b), in `src/explab/features.py`, about 120 common English sentiment words with fixed scores.
Reason: one-command reproduction must not depend on a second dataset download whose version can drift. The lexicon is crude and is named as a limitation in METHODS.md and AUDIT.md. Swapping in a validated lexicon is a Deep pass item.

## D10. Initial data retrieval route

The exploratory file was first retrieved directly from its OSF download endpoint (`https://osf.io/download/3vqmp/`) to generate the split lock. `src/explab/fetch.py` encodes the same endpoint and verifies the SHA-256 against the OSF-published value; `make reproduce` re-runs it. The confirmatory file's endpoint was listed in the OSF folder metadata during discovery and was never requested.

## D11. mSPRT mixing scale: frozen value kept after the simulation ran

After the sequential module ran, its mSPRT arm showed Type I 0.00 percent and power 0.00 percent at a 5 percent lift, because at archive arm sizes (at most 3,500 impressions per arm) the estimator variance stays far above the frozen mixing variance, so the likelihood ratio cannot reach the rejection threshold. Options: (a) amend tau_mix upward after seeing the simulation; (b) keep the frozen value and report the module as designed.
Choice: (b).
Reason: the value was frozen in PREREG section 10 before any run, and the simulation uses no outcome data, but changing a frozen design parameter after observing its behaviour is still post-hoc tuning. The honest finding stands: at these arm sizes no method detects a 5 percent lift (the fixed-horizon test has 5.76 percent power), peeking manufactures false positives (16.32 percent), and the always-valid test refuses. The mixing-scale sensitivity is recorded as Deep item 3 in ROADMAP.md.

## D12. Matching implementation replaced after a CI reproducibility failure

The first matcher (KD-tree candidates, unstable argsort processing order) produced different matched sets on the two CI legs: matching log OR 0.0443 (gap 0.1937) on Python 3.12 and 0.0385 (gap 0.1879) on Python 3.11, same 292 pairs, everything else byte-identical. A byte-identical reproduction guarantee cannot rest on a search tree's tie ordering or an unstable sort.
Choice: rewrite the matcher to be deterministic by construction. Logits are rounded to 8 decimals; all within-caliper candidate pairs are ordered by one total order (distance, treated row, control row) and assigned greedily. The estimator class is unchanged (1 to 1 nearest-neighbour matching on the logit propensity, caliper 0.2 SD, without replacement, as frozen in PREREG section 9); only the under-specified ordering mechanics changed.
Reason: the failure was measured in CI on development-split code, the locked primary does not use matching, and an estimator whose answer depends on the platform's sort internals is not reproducible science. The superseded numbers stay visible in this entry and in git history.
