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

## D13. Portfolio standard v2 adopted (2026-11-08)

Options: (a) rename files into the standard's names (PROPOSAL.md, REPORT.md); (b) keep every file the locked pre-registration names and map each to its role in the README layout table.
Choice: (b). The standard's own rule is that locked names win: prereg/PREREG.md names DECISIONS.md, RESULTS.md, AUDIT.md, docs/related_work.md, prereg/split.json and reports/propensity_overlap.png, and renaming them would break the lock's references.
Consequences: prereg/PREREG.md is the proposal, locked at 0847c53 (tag proposal-v1) with Amendment A1 at 38023c3, both before any code or outcome read; tests/test_layout.py pins both versions by SHA-256. AUDIT.md is the report. ROADMAP.md is retired and its text moved verbatim into AUDIT.md, section "Future work"; the references to ROADMAP.md in D8, D11 and RESEARCH.md now resolve there. The build grade left the public repository (grades are internal under the standard); its itemized deductions stay in AUDIT.md as "Known weaknesses", without point values. The tracked src/explab.egg-info/ build output is no longer committed (pip regenerates it on every install).
## D13. Gap-closure amendment (2026-11-17): label-rule sensitivity, registered and stopped

Post-registration amendment, registered before any computation under it. The AUDIT.md grade deducts 400 points because the frozen label rule (headline ends with "?") misses non-final questions: audit error 3.0 percent overall, 6 percent in the non-question group, diluting the contrast toward zero.
Options: (a) recompute the locked-split headline pooled odds ratio under corrected labels; (b) stop if the corrected labels cannot be derived from committed materials.
Choice: (a) is attempted only if the corrected labels exist in, or are derivable from, committed materials; otherwise (b), with the reason reported and no correction invented.
Reason: the only corrected labels in the committed record are the six flips in the label audit (results/label_audit_sample.json, results/label_audit_review.json, results/label_audit_review_notes.json), all in the development split by construction of the audit sample, and the reviewer's criterion recorded there is a semantic judgment (a direct question anywhere in the headline counts; indirect wh-clause topic headlines count as statements), not a mechanical rule that could be applied to the locked packages. No committed file carries corrected labels for any locked-split package, and results/per_test_locked.csv is aggregated under the frozen rule. Deriving locked labels would require inventing a new labelling rule and applying it to the locked split, which PREREG section 3 and the frozen design forbid. The wider-definition re-runs named in ROADMAP.md Deep item 6 are a separate item and are not this amendment.

## D14. Gap-closure amendment (2026-11-17): mSPRT mixing-scale sensitivity map

Post-registration amendment, registered before any computation under it. This is ROADMAP.md Deep item 3 and answers the AUDIT.md deduction (minus 300) that the sequential module, at the frozen mixing scale tau_mix = 0.001, demonstrates the cost of validity (Type I 0.00 percent, power 0.00 percent at a 5 percent lift) without mapping the validity-versus-power trade-off.
Choice: re-run the frozen sequential simulation design of PREREG section 10 unchanged (Bernoulli streams at the archive baseline CTR, looks every 500 impressions per arm to 3,500 per arm, 200,000 runs, seed 20261106, the same seeded streams), computing the mSPRT likelihood ratio on a grid of mixing scales tau_mix in {0.0005, 0.001, 0.002, 0.003, 0.005, 0.0075, 0.01}, spanning the ROADMAP range 0.0005 to 0.01 and including the frozen 0.001. Report, per tau, the any-look rejection rate under the null (A/A) and under a 5 percent relative lift (A/B), each with a Wilson 95 percent interval. The frozen value's row must reproduce results/sequential.json exactly; that reproduction is the check that the streams are the frozen ones.
Reason: the simulation uses no outcome data, and D11 already refused to re-tune the frozen value after seeing its behaviour. This amendment does not change tau_mix or any verdict; it maps the trade-off the frozen point sits on, which is what the audit asked for. Outputs go to new files only; results/sequential.json is not touched.

## D15. Gap-closure amendment (2026-11-17): moderator analysis of the locked-split heterogeneity, exploratory

Post-registration amendment, registered before any computation under it. This is ROADMAP.md Deep item 4, which requires the moderator analysis to be pre-registered as its own amendment before any locked-split re-use. The AUDIT.md grade deducts 350 points because heterogeneity is high (tau 0.3325, I squared 75.8 percent in the locked split) and unexplained.
Choice: an explicitly post hoc, exploratory decomposition of the locked-split heterogeneity in results/per_test_locked.csv, using the frozen per-test log odds ratios and variances and the repository's own DerSimonian and Laird pooling (src/explab/primary.py pool_dl). Three moderator splits, all derivable from the committed per-test file: (M1) question share of a test's impressions (impressions_q over total impressions), split at 0.5 into question-dominant and non-question-dominant tests; (M2) baseline CTR band, the test's non-question-arm CTR (clicks_nq over impressions_nq), in tertiles; (M3) test size, total impressions, split at the median. Packages per test, named in ROADMAP item 4, is not in the committed per-test file, so total impressions stands in as the size moderator and that substitution is stated wherever M3 is reported. Per moderator: per-group pooled log odds ratio, odds ratio, 95 percent interval, tau, I squared, and test count; the Cochran Q decomposition (Q total, Q within groups, Q between groups, degrees of freedom, chi-square p); and the share of heterogeneity explained, as Q between over Q total and as the DerSimonian and Laird tau squared reduction against a group-mean residual model.
Reason and multiple-look cost, stated as ROADMAP item 4 requires: this is a second, post hoc look at the locked split beyond the frozen one look of PREREG section 3. It is exploratory only. No verdict in RESULTS.md or reports/VERDICT.md changes, no hypothesis is tested, and the three splits above are the only ones run under this amendment. Outputs go to new files only; no frozen results file is touched.

## D16. Gap-closure amendment (2026-11-17): label-rule sensitivity by fresh labelling of the locked split under the reviewer's criterion, AI labellers, blanket permission

Post-registration amendment, registered before any labelling or computation under it. This reopens the item D13 stopped. D13 stopped because corrected labels existed only for six development-split audit flips and deriving locked labels would have required inventing a new labelling rule, which the frozen design forbids. This amendment does not invent a rule: the labelling criterion is the reviewer's criterion recorded verbatim in results/label_audit_review_notes.json, applied to the locked split's headlines by fresh labelling. What changed is the authorisation and the labeller identity, both recorded here.

Authorisation: the study owner (Jesun) ruled the eight gap-closure decisions to their defaults on 2026-11-17, ordered all remaining work resolved the same evening ("resolve everything, finish all the work rigorously", 21:54 EST), and at 21:59 EST granted blanket permission in writing: "i give you every permission do everything anyhow possible". The coordinator dispatch of 22:00 EST names this item for closure under that permission, with a deadline of 06:00 EST.

Choice: recompute the locked-split headline pooled odds ratio under corrected labels, where the corrected labels are produced as follows.
(a) Labellers: two independent AI labeller agents (large language model agents, not human reviewers). Each applies the reviewer's criterion exactly as written in results/label_audit_review_notes.json. The two passes are blind: neither labeller sees the frozen labels, the frozen outcomes, any effect size, or the other labeller's labels. The labellers receive only the criterion verbatim and the headlines with neutral identifiers.
(b) Adjudication: every headline where the two labellers disagree goes to a third AI agent, the adjudicator, which receives the same criterion verbatim, the headline, and the two labels, and issues the final label under the same criterion.
(c) Disclosure: the labellers and the adjudicator are AI agents. That identity must be disclosed wherever the corrected figure is reported, including any paper version. The corrected labels are not human labels and are never described as such.
(d) Labelling unit: the unique headline text. The locked split holds 14,701 packages (post-exclusion) carrying 8,120 unique headline texts. The criterion judges headline phrasing only, so one label per unique text is determined once and mapped back to every locked package carrying that text. The full unique set is labelled; no subset is taken.
(e) Recompute: the corrected figure is computed with the repository's own pooling code (src/explab/primary.py, analyse) on the locked package rows with the corrected labels substituted for the frozen ones. Before any corrected computation, the same code path on the frozen labels must reproduce the frozen headline (odds ratio 0.8645, 465 tests, results/primary_locked.json); that check is part of this amendment's record.
(f) Frozen record: the frozen 0.8645, results/primary_locked.json, results/per_test_locked.csv, and every other frozen file stay untouched. The corrected figure is a new sensitivity result in new files only (results/label_corrected_locked.json, results/per_test_locked_corrected.csv, reports/label-correction-2026-11-17.md). No verdict in RESULTS.md or reports/VERDICT.md changes; the frozen verdict stands as the study's headline, and the corrected figure is reported beside it as a sensitivity analysis.
Reason: the AUDIT.md deduction (minus 400) is that the frozen rule's roughly 3 percent label error, concentrated in the non-question group, dilutes the contrast toward zero. The only way to price that dilution on the locked split is corrected labels for the locked packages. The criterion already exists in the record; the owner's blanket permission covers the AI-labeller route that D13's stop rule anticipated as a human-labelling decision; and the disclosure condition in (c) keeps the substitution of AI for human labellers on the record rather than hidden.

## D16 outcome (recorded 2026-11-17, after the run)

The labelling and recompute registered in D16 are complete. Two independent AI labeller agents labelled all 8,120 unique locked-split headline texts under the reviewer's criterion verbatim; raw inter-labeller agreement was 8,099 of 8,120 (99.74 percent); the 21 disagreements were decided by the AI adjudicator (7 question, 14 statement). Against the frozen rule, 642 unique headlines changed label (638 to question, 4 to statement), moving 1,089 of 14,701 locked packages (1,078 to question, 11 to statement). The pre-computation check passed: the repository's pooling code on the frozen labels reproduces the frozen headline exactly (odds ratio 0.8645, 465 tests). Under the corrected labels the same code pools 720 tests (correcting labels creates both-group tests the frozen rule had left single-group) and gives a pooled odds ratio of 0.8842 (95 percent CI 0.8593 to 0.9099; log OR -0.1230, SE 0.0146; tau 0.3253; I squared 76.09 percent), which the frozen verdict rule also reads as CONFIRMED. The frozen headline (0.8645, 465 tests) is unchanged and remains the study's headline; the corrected figure is a sensitivity result on a larger pool, reported in reports/label-correction-2026-11-17.md with the AI-labeller disclosure D16 requires. Machine record: results/label_corrected_locked.json and results/per_test_locked_corrected.csv; label sets in labelling-2026-11-17/. Test suite: 15 passed before the run and 15 passed after. Nothing was pushed.
