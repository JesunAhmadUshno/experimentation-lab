"""Question-headline labelling (frozen rule) and the label audit.

Frozen rule (prereg/PREREG.md section 6): a package is a question
package if its headline, after stripping leading and trailing
whitespace, ends with the character "?".

The audit samples 200 development-split packages (100 labelled question,
100 labelled non-question, seed 20261106) into
results/label_audit_sample.json. A human reviewer marks each sampled
headline correct or incorrect in results/label_audit_review.json
(a list of {"sample_index": i, "label_correct": true/false}).
`score_audit` turns the review into results/label_audit.json.
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

from . import SEED
from .data import DEFAULT_DATA, apply_exclusions, load_raw, load_split, restrict_to_split

RESULTS = Path("results")


def is_question(headline):
    if not isinstance(headline, str):
        return False
    return headline.strip().endswith("?")


def add_labels(df):
    out = df.copy()
    out["is_question"] = out["headline"].map(is_question)
    return out


def make_audit_sample(data_path=DEFAULT_DATA, split_path="prereg/split.json"):
    df = load_raw(data_path)
    kept, _ = apply_exclusions(df)
    split = load_split(split_path)
    dev = add_labels(restrict_to_split(kept, split["development"]))
    rng = np.random.default_rng(SEED)
    sample_rows = []
    for label_value, group_name in ((True, "question"), (False, "non_question")):
        group = dev[dev["is_question"] == label_value]
        take = min(100, len(group))
        idx = rng.choice(len(group), size=take, replace=False)
        for j in idx:
            row = group.iloc[int(j)]
            sample_rows.append(
                {
                    "sample_index": len(sample_rows),
                    "group": group_name,
                    "clickability_test_id": row["clickability_test_id"],
                    "headline": row["headline"],
                }
            )
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "label_audit_sample.json").write_text(
        json.dumps({"seed": SEED, "sample": sample_rows}, indent=1) + "\n",
        encoding="utf-8",
    )
    print(f"audit sample written: {len(sample_rows)} headlines")
    return sample_rows


def score_audit(sample_path=None, review_path=None):
    sample_path = sample_path or RESULTS / "label_audit_sample.json"
    review_path = review_path or RESULTS / "label_audit_review.json"
    sample = json.loads(Path(sample_path).read_text(encoding="utf-8"))["sample"]
    review = json.loads(Path(review_path).read_text(encoding="utf-8"))
    marks = {int(r["sample_index"]): bool(r["label_correct"]) for r in review}
    if set(marks) != set(range(len(sample))):
        raise ValueError("review must mark every sampled headline exactly once")
    errors_by_group = {}
    for group_name in ("question", "non_question"):
        members = [s for s in sample if s["group"] == group_name]
        errors = sum(1 for s in members if not marks[s["sample_index"]])
        errors_by_group[group_name] = {
            "n": len(members),
            "errors": int(errors),
            "error_rate": round(errors / len(members), 4) if members else None,
        }
    total_errors = sum(v["errors"] for v in errors_by_group.values())
    out = {
        "seed": SEED,
        "n_sampled": len(sample),
        "n_errors": int(total_errors),
        "error_rate": round(total_errors / len(sample), 4),
        "by_group": errors_by_group,
        "note": "Label rule is frozen; the audit measures its error rate and does not change it.",
    }
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "label_audit.json").write_text(
        json.dumps(out, indent=1, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(out, indent=1))
    return out


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "sample":
        make_audit_sample()
    elif len(sys.argv) > 1 and sys.argv[1] == "score":
        score_audit()
    else:
        raise SystemExit("usage: python -m explab.label [sample|score]")
