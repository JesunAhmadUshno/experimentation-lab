PY := .venv/bin/python
PIP := .venv/bin/pip

.PHONY: setup fetch split power guardrails primary-dev causal stress audit-sample audit-score primary-locked reports test pipeline reproduce

setup:
	python3 -m venv .venv
	$(PIP) install -q -e ".[dev]"

fetch:
	$(PY) -m explab.fetch

split:
	$(PY) prereg/make_split.py

power:
	$(PY) -m explab.power
	$(PY) -m explab.peeking

guardrails:
	$(PY) -m explab.guardrails

primary-dev:
	$(PY) -m explab.primary dev

causal:
	$(PY) -m explab.causal

stress:
	$(PY) -m explab.stress

audit-sample:
	$(PY) -m explab.label sample

audit-score:
	$(PY) -m explab.label score

primary-locked:
	$(PY) -m explab.primary locked

reports:
	$(PY) -m explab.report

test:
	.venv/bin/pytest -q

pipeline: fetch power guardrails primary-dev causal stress audit-score primary-locked reports

# One-command reproduction (U10): reinstall, rerun the frozen pipeline,
# regenerate the split lock, and diff every generated report and every
# file in results/ against the committed copies (the PNG figure is not
# compared: it is not guaranteed byte-stable across platforms). Any byte difference fails the target.
reproduce:
	$(MAKE) setup
	cp RESULTS.md /tmp/explab_RESULTS.committed.md
	cp reports/VERDICT.md /tmp/explab_VERDICT.committed.md
	cp prereg/split.json /tmp/explab_split.committed.json
	$(MAKE) pipeline
	$(PY) prereg/make_split.py
	diff /tmp/explab_split.committed.json prereg/split.json
	diff /tmp/explab_RESULTS.committed.md RESULTS.md
	diff /tmp/explab_VERDICT.committed.md reports/VERDICT.md
	git diff --exit-code results/
	@echo "REPRODUCE OK: all generated outputs byte-identical"
