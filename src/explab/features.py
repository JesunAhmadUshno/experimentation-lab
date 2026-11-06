"""Covariate features for the causal arm (frozen in PREREG section 10).

Covariates per package:
- test_week_num: weeks since the earliest test_week in the data given.
- headline_len: headline length in characters.
- sentiment: mean score of lexicon words in the headline (0 if none).
- eyecatcher_reused: 1 if the package's eyecatcher_id appears on more
  than one package in the data given, else 0.

The sentiment lexicon is a small built-in word list (DECISIONS.md D9).
It is crude by design trade-off: reproduction must not depend on a
second downloadable dataset. Scores are +1/-1, with +2/-2 for the
strong words marked in STRONG_POSITIVE / STRONG_NEGATIVE.
"""

import re

import numpy as np
import pandas as pd

STRONG_POSITIVE = {
    "amazing", "incredible", "love", "loves", "fantastic", "miracle",
    "heartwarming", "brilliant", "stunning", "perfect",
}
STRONG_NEGATIVE = {
    "terrible", "horrible", "hate", "hates", "awful", "devastating",
    "heartbreaking", "nightmare", "disgusting", "brutal",
}
POSITIVE = {
    "great", "beautiful", "best", "good", "happy", "wonderful", "awesome",
    "inspiring", "powerful", "funny", "adorable", "sweet", "win", "wins",
    "winning", "victory", "success", "successful", "hope", "hopeful",
    "dream", "magic", "hero", "heroes", "brave", "strong", "free",
    "freedom", "joy", "joyful", "smile", "smiles", "laugh", "laughs",
    "exciting", "excited", "thrilled", "proud", "cute", "lovely",
    "delicious", "favorite", "favourite", "inspire", "inspires", "uplifting",
    "generous", "kind", "kindness", "amazing", "incredible", "love",
    "fantastic", "miracle", "heartwarming", "brilliant", "stunning",
    "perfect",
}
NEGATIVE = {
    "bad", "sad", "death", "dead", "die", "dies", "died", "killed",
    "killing", "war", "worst", "scary", "fear", "fears", "dangerous",
    "wrong", "fail", "fails", "failed", "failure", "crisis", "shocking",
    "disturbing", "tragic", "pain", "painful", "sick", "angry", "anger",
    "furious", "outrage", "scandal", "corrupt", "lies", "lying", "cheat",
    "stolen", "attack", "attacks", "attacked", "victim", "victims",
    "suffer", "suffers", "suffering", "poor", "homeless", "hungry",
    "disease", "cancer", "abuse", "violent", "violence", "crime",
    "prison", "guilty", "shame", "embarrassing", "embarrassed", "stupid",
    "ridiculous", "insane", "crazy", "weird", "gross", "heartbroken",
    "disaster", "emergency", "warning", "banned", "illegal", "arrest",
    "arrested", "murder", "murdered", "depression", "anxiety", "stress",
    "broke", "broken", "lost", "losing", "hell", "evil", "cruel",
    "terrified", "panic", "sadness", "grief", "lonely", "alone", "dark",
    "terrible", "horrible", "hate", "awful", "devastating",
    "heartbreaking", "nightmare", "disgusting", "brutal",
}

_TOKEN = re.compile(r"[a-z']+")


def _word_score(word):
    if word in STRONG_POSITIVE:
        return 2
    if word in STRONG_NEGATIVE:
        return -2
    if word in POSITIVE:
        return 1
    if word in NEGATIVE:
        return -1
    return 0


def sentiment_score(headline):
    if not isinstance(headline, str):
        return 0.0
    tokens = _TOKEN.findall(headline.lower())
    if not tokens:
        return 0.0
    return float(sum(_word_score(t) for t in tokens)) / len(tokens)


def build_covariates(df):
    """df: package rows (one split, exclusions applied, labels added)."""
    out = df.copy()
    weeks = pd.to_datetime(out["test_week"])
    out["test_week_num"] = (weeks - weeks.min()).dt.days / 7.0
    out["headline_len"] = out["headline"].fillna("").str.len().astype(float)
    out["sentiment"] = out["headline"].map(sentiment_score)
    counts = out["eyecatcher_id"].value_counts(dropna=False)
    out["eyecatcher_reused"] = out["eyecatcher_id"].map(counts).gt(1).astype(float)
    return out


COVARIATES = ["test_week_num", "headline_len", "sentiment", "eyecatcher_reused"]
