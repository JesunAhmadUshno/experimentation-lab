# Label-rule sensitivity: locked split under corrected labels (DECISIONS.md D16)

Date: 2026-11-17. Status: sensitivity analysis. The frozen headline stands;
this report prices the frozen label rule's error on the locked split and
changes no verdict in RESULTS.md or reports/VERDICT.md.

## Disclosure

The corrected labels were produced by AI agents, not human reviewers: two
independent AI labeller agents, blind to the frozen labels, the frozen
outcomes, and each other, plus one AI adjudicator agent for disagreements.
Each applied the reviewer's criterion recorded verbatim in
results/label_audit_review_notes.json. Any paper version reporting the
corrected figure must carry this disclosure (DECISIONS.md D16, condition (c)).

## Method

- Labelling unit: the unique headline text. The locked split (post-exclusion)
  holds 14,701 packages carrying 8,120 unique headline texts; the full unique
  set was labelled, no subset.
- Inter-labeller agreement: 8,099 of 8,120 headlines (99.74 percent). The 21
  disagreements were adjudicated under the same criterion (7 finally
  QUESTION, 14 finally STATEMENT).
- Recompute: the repository's own pooling code (src/explab/primary.py,
  analyse) on the locked package rows with corrected labels substituted.
  Verification first: the same code path on the frozen labels reproduces the
  frozen headline exactly (odds ratio 0.8645, 465 tests;
  results/primary_locked.json).

## Label changes against the frozen rule

- Unique headlines changed: 642 of 8,120 (638 statement to question, 4
  question to statement). Final question headlines: 1,354; frozen: 720.
- Packages changed: 1,089 of 14,701 (1,078 to question, 11 to statement).

## Result

| | Frozen labels | Corrected labels |
| --- | --- | --- |
| Tests pooled | 465 | 720 |
| Pooled odds ratio | 0.8645 | 0.8842 |
| 95 percent CI (OR) | 0.8335 to 0.8966 | 0.8593 to 0.9099 |
| log OR (SE) | -0.1456 (0.0186) | -0.1230 (0.0146) |
| tau | 0.3325 | 0.3253 |
| I squared | 75.76 percent | 76.09 percent |
| Frozen verdict rule | CONFIRMED | CONFIRMED (ci95 excludes 0) |

Caveat on comparability: the two figures do not pool the same tests.
Correcting the labels moves packages between groups, so tests the frozen rule
left with a single group (and therefore outside the frozen table) enter the
corrected pool: 465 tests become 720. The corrected figure is therefore a
sensitivity result on a larger pool, not a re-estimate of the frozen pool.
On direction: the audit expected the frozen rule's error to dilute the
contrast toward zero. On the corrected pool the pooled odds ratio sits
slightly closer to one (0.8842 against 0.8645), with a narrower interval; the
dilution expectation is not borne out as a simple shift, because the pool
composition changed at the same time as the labels.

## Files

- labelling-2026-11-17/: chunk files, both labellers' raw labels
  (labelsA_chunk_1..8.json, labelsB_chunk_1..8.json), disagreements.json,
  adjudicated.json, labels_final.json (the adjudicated final label set).
- results/label_corrected_locked.json: the corrected result record.
- results/per_test_locked_corrected.csv: the corrected per-test table.
- DECISIONS.md D16: the amendment and its outcome entry.
