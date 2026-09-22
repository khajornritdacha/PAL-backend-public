"""Recompute Table II and the Section V.B statistics from the raw judge scores.

Usage:  python reproduce_table2.py            (run from the evaluation/ directory)
Needs:  Python 3.9+, numpy, scipy
"""
import json
from pathlib import Path

import numpy as np
from scipy.stats import wilcoxon

ROOT = Path(__file__).resolve().parent / "lessons"
DIMS = ["Multimedia", "Spatial Contiguity", "Modality", "Redundancy", "Signaling", "Coherence"]
QUALITY = ["Modality", "Redundancy", "Signaling", "Coherence"]  # presence-driven dims excluded
LESSONS = sorted(p.name for p in ROOT.iterdir() if p.is_dir())
RUNS = (1, 2, 3)


def load(cond):
    """scores[lesson][run][dim] and the d-weights carried in the score files."""
    scores, weights = {}, {}
    for les in LESSONS:
        scores[les] = {}
        for r in RUNS:
            d = json.loads((ROOT / les / cond / f"score{r}.json").read_text(encoding="utf-8"))
            scores[les][r] = {p["principle"]: p["score"] for p in d["principles"]}
            weights.update({p["principle"]: p["d_weight"] for p in d["principles"]})
    return scores, weights


def composite(run_scores, weights, dims):
    w = np.array([weights[k] for k in dims])
    s = np.array([run_scores[k] for k in dims])
    return float((w * s).sum() / w.sum())


def icc_1_1(x):
    """One-way random, single measure. x: lessons x runs."""
    n, k = x.shape
    msb = k * ((x.mean(1) - x.mean()) ** 2).sum() / (n - 1)
    msw = ((x - x.mean(1, keepdims=True)) ** 2).sum() / (n * (k - 1))
    return (msb - msw) / (msb + (k - 1) * msw)


s1, w = load("v1")
s2, _ = load("v2")
unit = {k: 1.0 for k in DIMS}


def lesson_means(s, fn):
    return np.array([np.mean([fn(s[les][r]) for r in RUNS]) for les in LESSONS])


print(f"Lessons: {len(LESSONS)}  ({', '.join(LESSONS)})\n")
print(f"{'Dimension':<20}{'V1':>14}{'V2':>14}{'Delta':>9}{'Range':>15}{'Improved':>10}")
rows = [(k, lambda r, k=k: r[k]) for k in DIMS]
rows.append(("Weighted composite", lambda r: composite(r, w, DIMS)))
for name, fn in rows:
    a, b = lesson_means(s1, fn), lesson_means(s2, fn)
    d = b - a
    print(f"{name:<20}{a.mean():>7.2f} ± {a.std(ddof=1):.2f}{b.mean():>7.2f} ± {b.std(ddof=1):.2f}"
          f"{d.mean():>+9.2f}{d.min():>9.2f}–{d.max():.2f}{(d > 0).sum():>7}/{len(d)}")

a = lesson_means(s1, lambda r: composite(r, w, DIMS))
b = lesson_means(s2, lambda r: composite(r, w, DIMS))
res = wilcoxon(b, a, alternative="two-sided", method="exact")
w_plus = int(sum(i + 1 for i, v in enumerate(np.argsort(np.abs(b - a))) if (b - a)[v] > 0))
print(f"\nExact two-sided Wilcoxon signed-rank on the weighted composite: W+ = {w_plus}, p = {res.pvalue:.4f}")

print("\nSensitivity composites")
for label, fn in [
    ("Quality-driven only (weighted)", lambda r: composite(r, w, QUALITY)),
    ("Unweighted, six dimensions", lambda r: composite(r, unit, DIMS)),
]:
    a, b = lesson_means(s1, fn), lesson_means(s2, fn)
    print(f"  {label:<32}{a.mean():.2f} -> {b.mean():.2f}  (Delta = {b.mean() - a.mean():+.2f})")

print("\nJudge run-to-run consistency (weighted composite)")
for cond, s in (("V1", s1), ("V2", s2)):
    x = np.array([[composite(s[les][r], w, DIMS) for r in RUNS] for les in LESSONS])
    rng = (x.max(1) - x.min(1)).mean()
    cells = [max(s[les][r][k] for r in RUNS) - min(s[les][r][k] for r in RUNS) <= 1
             for les in LESSONS for k in DIMS]
    print(f"  {cond}: ICC(1,1) = {icc_1_1(x):.2f}, mean range = {rng:.2f}, "
          f"cells within one point = {100 * np.mean(cells):.0f}%")
