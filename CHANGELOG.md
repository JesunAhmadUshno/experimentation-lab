# Changelog

All notable changes to this project. Format: Keep a Changelog 1.1.
Versions follow Semantic Versioning; no release is tagged yet.

## [Unreleased]

### Changed
- 2026-11-08: The reproduction check (CI and `make reproduce`) now also
  diffs every file in results/ against the committed copies, so a drift
  in a result JSON or per-test CSV fails even when RESULTS.md is
  unchanged. The README claim now names exactly what is compared; the
  PNG figure is regenerated but not compared.
- 2026-11-08: Adopted the portfolio standard v2. README opens with the
  question, headline, field, job family and verdict (Evaluated), then
  reproduce commands, lifecycle and a layout table. AUDIT.md is the
  report; its build grade left the public repo (grades are internal)
  and its deductions stay as "Known weaknesses". ROADMAP.md moved into
  AUDIT.md "Future work" (DECISIONS.md D13). The lock is tagged
  proposal-v1 on 0847c53, and a test pins prereg/PREREG.md at the lock
  and after Amendment A1. CI gets read-only permissions; CodeQL and
  Dependabot added; main protected.

### Security
- 2026-11-07: Upgraded the dashboard's vite to 6.4.5 so npm audit
  reports no high or critical advisories.

### Added
- 2026-11-07: Live dashboard in site/ with in-browser simulators and a
  Pages deploy.
- 2026-11-06: Deterministic propensity matcher after the CI byte-check
  caught platform-dependent pair selection (DECISIONS.md D12).
- 2026-11-06: Audit, final README and roadmap.
- 2026-11-06: Locked confirmatory run: verdict CONFIRMED, odds ratio
  0.8645 (95% CI 0.8335 to 0.8966), 465 tests.
- 2026-11-06: Development-split results: fetch gate, power, sequential,
  guardrails, primary dev, label audit, causal arm, stress tests.
- 2026-11-06: Analysis package, unit tests and CI reproduction on
  Python 3.11 and 3.12.
- 2026-11-06: Split lock (seed 20261106; 974 development and 3,899
  locked tests), before any outcome column was read.
- 2026-11-06: Amendment A1 to the pre-registration (38023c3).
- 2026-11-06: Pre-registration (0847c53), before any code or data
  access.
