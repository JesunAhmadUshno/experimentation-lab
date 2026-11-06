# Research base

This file records the literature work behind the study design: what was searched, what was included, and how the evidence splits into past, present, and future horizons. The claim-level detail for the headline question lives in `docs/related_work.md`. The design calculations live in the research pack (programme verdict pack 07) and are reproduced from code by the power module.

## Search record

Searches run on 2026-11-06 (design phase) and during the verdict pack's own research (2026-11-06, Claude Project "AI Platform Research Programme", chat 07):
- "Upworthy Research Archive OSF exploratory dataset download" and the archive's Scientific Data descriptor.
- "question headlines click-through rate curiosity gap study DOI".
- "Fang Wheeler question titles Journal of Consumer Psychology".
- Dataset candidates assessed in the verdict pack: Upworthy Research Archive (chosen), Hillstrom email dataset (rejected, no explicit data licence), Criteo uplift dataset (not chosen, dataset licence unverified), LaLonde NSW and PSID files (optional secondary, no open licence stated).

Inclusion rules: primary sources only for effect claims (peer-reviewed papers and the dataset descriptor); the archive's own documentation for data facts (splits, problem flag, window warning); canonical methods references for the statistics (DerSimonian and Laird for random-effects pooling; Johari, Pekelis and Walsh for always-valid inference). Vendor or blog material is never used as evidence for an effect.

## Past horizon (what is established)

- The Upworthy Research Archive holds every A/B test Upworthy fielded from 2013-01-24 to 2015-04-30: 32,487 experiments, 150,817 arms, 538,272,878 assignments (Matias et al. 2021). It ships exploratory, confirmatory, and holdout splits under CC BY 4.0.
- Question framing and engagement has direct published evidence, including on this archive's confirmatory set: Fang and Wheeler (2026) find question titles reduce engagement. Le Quere et al. (2025) show headline feature effects on this archive are context dependent. Hagtvedt (2015) found the question-versus-statement effect reverses with arousal in advertising. Full detail and DOIs: `docs/related_work.md`.
- The archive's confirmatory protocol is registered-report based: the negativity study (Robertson et al., Nature Human Behaviour 2023) received its confirmatory data only after Stage 1 acceptance. This is why this study does not touch the confirmatory file.
- A 2024 archive update flagged randomization problems in about 22 percent of tests, concentrated in 2013-06-25 to 2014-01-10, with a `problem` column in the data. Both the flag and the window are frozen exclusions here.
- Repeated peeking at fixed-horizon tests inflates false positives; mixture sequential probability ratio tests give always-valid p-values (Johari, Pekelis and Walsh, arXiv 1512.04922; Operations Research 70(3), 1806-1821, 2022).

## Present horizon (what this study adds)

- A pre-registered estimate of the question-headline contrast on the exploratory split, with a TOST equivalence rule and a sample size floor fixed before outcomes were read.
- A within-study comparison: the same contrast estimated observationally across tests on the development split, propensity adjusted, against the randomized benchmark from the same split. Within-study comparisons in the LaLonde tradition measure method error against a known answer; the size of the miss on real platform data is the result.
- A sequential testing module whose error rates are measured on streams calibrated to archive arm sizes, next to the naive peeking rate on identical streams.
- An end-to-end reproducible pipeline: split lock in git, generated results, one-command reproduction with byte-identical outputs.

## Future horizon (not claimed, listed so the boundary is visible)

- A confirmatory-split run under a peer-reviewed registered report (requires the archive team's process; see ROADMAP.md).
- User-level experimentation data, which the archive does not contain; nothing here speaks to within-user effects, novelty decay, or long-term retention.
- Modern platform replication (2013 to 2015 advocacy headlines do not transfer to current feeds or marketplace surfaces).

## Baseline numbers used at design time (estimates, labelled)

From published totals, not from the data: baseline CTR about 1.54 percent (5.7M clicks over 370M impressions, Robertson et al. 2023 totals, both rounded); mean arm size 3,569 impressions (538,272,878 assignments over 150,817 arms, Matias et al. 2021 totals). These feed the power module only. Measured replacements come from the fetch and primary modules.
