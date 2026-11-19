"""Portfolio standard checks: the lock holds, required files exist, no public grade."""
import hashlib
import os
import re
import subprocess

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PREREG = "prereg/PREREG.md"
# prereg/PREREG.md as committed in 0847c53 (tag proposal-v1), before any code or data access.
LOCK_COMMIT = "0847c53"
LOCKED_SHA256 = "0a046e05f47a29e95669be0a9627017359bbf1fbb23b0d5b50b879eab18da2d2"
# After Amendment A1 (38023c3), before any outcome column was read; also recorded in prereg/hash.txt.
AMENDED_SHA256 = "a51c3a4a5591c86d2a6796c2b7d58666e4489dfd070bbcba3348577b955844b0"


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def test_prereg_is_unchanged_since_amendment_a1():
    with open(os.path.join(ROOT, PREREG), "rb") as f:
        assert _sha(f.read()) == AMENDED_SHA256, \
            "prereg/PREREG.md changed after its lock; record a dated amendment in DECISIONS.md instead"
    with open(os.path.join(ROOT, "prereg/hash.txt")) as f:
        assert f.read().strip() == AMENDED_SHA256


def test_lock_commit_holds_the_original_prereg():
    if not os.path.isdir(os.path.join(ROOT, ".git")):
        pytest.skip("not a git checkout")
    blob = subprocess.run(["git", "show", f"{LOCK_COMMIT}:{PREREG}"], cwd=ROOT,
                          capture_output=True, check=True).stdout
    assert _sha(blob) == LOCKED_SHA256


def test_required_files_exist():
    need = ["README.md", PREREG, "prereg/split.json", "AUDIT.md", "RESULTS.md", "reports/VERDICT.md",
            "DECISIONS.md", "CHANGELOG.md", "CITATION.cff", "SECURITY.md", "LICENSE",
            "results/primary_locked.json", "results/per_test_locked.csv"]
    missing = [p for p in need if not os.path.exists(os.path.join(ROOT, p))]
    assert not missing, "missing: " + ", ".join(missing)


GRADE = re.compile(r"\d[\d,]*\s*(of|/)\s*10,?000|10,?000 scale|\bGrade:|\*\*Grade", re.I)
PUBLIC = ["README.md", "AUDIT.md", "RESULTS.md", "reports/VERDICT.md", "METHODS.md", "HYPOTHESES.md",
          "RESEARCH.md", "DECISIONS.md", "CHANGELOG.md", "docs/related_work.md", "data/README.md",
          "site/src/App.jsx", "site/index.html"]


def test_no_public_grade():
    for name in PUBLIC:
        with open(os.path.join(ROOT, name)) as f:
            hit = GRADE.search(f.read())
        assert hit is None, f"{name} carries a grade ({hit.group(0)!r}); grades are internal"


def test_grade_pattern_catches_a_grade():
    assert GRADE.search("build grade 6,500 of 10,000")
    assert GRADE.search("Grade: 10,000 minus 3,500")
    assert not GRADE.search("200,000 simulation runs")
