# Related work: question headlines and click behaviour

Purpose (programme upgrade item U2): list the primary sources that touch this study's exact question, with DOIs, and state what they change about the novelty claim. Search date: 2026-11-06. Sources were read at the level of the published abstract and, for item 1, the published study summaries. Anything not read in full is marked as such.

## Primary sources

1. Fang, D., and Wheeler, S. C. (2026). Titles framed as questions reduce reader engagement. Journal of Consumer Psychology. DOI 10.1002/jcpy.70031.
   - Directly on point. Four studies: Reddit posts (N = 53,030), academic articles (N = 3,078,791), online news headline A/B experiments (N = 22,743 experiments, from the Upworthy Research Archive confirmatory set), and a pre-registered lab study (N = 400). Finding: question-framed titles reduce engagement, mediated by lower expected informativeness; the Upworthy arm found lower click-through rates for question variants.
   - Effect on this study: the headline question (H1) already has a published answer on the archive's confirmatory split. This study's exploratory-split estimate is a replication under a different, pre-registered estimator (within-test random-effects pooling with a TOST verdict rule), not a first measurement. No novelty is claimed for the headline question.

2. Le Quere, M. A., and others (2025). When curiosity gaps backfire: effects of headline concreteness on information selection decisions. Scientific Reports 15, 994. DOI 10.1038/s41598-024-81575-9.
   - A registered report on the same archive: a meta-analysis of 8,977 headline experiments on headline concreteness and CTR, with a curvilinear (context-dependent) result. Shows the archive supports pooled cross-test estimation of headline-feature effects, and that feature effects interact with the surrounding test context. Read at abstract level for this file.
   - Effect on this study: the pooled estimator has precedent on this data; context dependence is a named threat to a single pooled number, recorded in METHODS.md.

3. Gligoric, K., Lifchits, G., West, R., and Anderson, A. (2021). Linguistic effects on news headline success: evidence from thousands of online field experiments (registered report protocol). PLoS ONE 16(9), e0257091. DOI 10.1371/journal.pone.0257091.
   - A registered report protocol for linguistic features of headlines on the same archive, including question-related features in its feature set. Read at abstract and protocol level for this file.
   - Effect on this study: pre-registration on this archive is established practice; this study follows the same pattern at repository scale.

4. Hagtvedt, H. (2015). Promotional phrases as questions versus statements: an influence of phrase style on product evaluation. Journal of Consumer Psychology 25(4), 635-641. DOI 10.1016/j.jcps.2014.12.005.
   - Lab and field experiments on question versus statement phrasing in advertising. The effect reverses with arousal: questions help under low arousal, statements help under high arousal. Read at abstract level for this file.
   - Effect on this study: prior evidence is mixed in advertising contexts, which is one reason the primary test here is two-sided.

5. Loewenstein, G. (1994). The psychology of curiosity: a review and reinterpretation. Psychological Bulletin 116(1), 75-98. DOI 10.1037/0033-2909.116.1.75.
   - The information-gap theory of curiosity that motivates question headlines in practice. Cited as the theory source, not as CTR evidence.

## Adjusted novelty claim (binding wording)

Prior work has already estimated the effect of question framing on clicks, including on this archive's confirmatory set (source 1). This study claims novelty only for: (a) a fully pre-registered, one-command-reproducible pipeline that pairs the randomized estimate with a within-study measurement of how far a cross-test observational estimate misses it on the same platform; (b) an always-valid sequential testing module calibrated to archive arm sizes, with the peeking inflation measured on the same streams; (c) a public audit trail (pre-registration, split lock, generated results) that a third party can re-run end to end. Any wording in this repository that implies the headline question itself is new is an error and should be corrected on sight.
