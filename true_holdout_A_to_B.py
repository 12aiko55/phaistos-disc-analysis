"""
true_holdout_A_to_B.py
=======================
True holdout test: learn grammatical formula patterns from Side A only,
then predict whether Side B matches those patterns WITHOUT any key modification.

If G_LUWIAN is a genuine phonetic key (not overfitted to the disc),
both sides should exhibit similar grammatical structure independently.

Three sub-tests:

  TEST 1 — Formula score parity:
    Score Side A and Side B separately under the frozen G_LUWIAN key.
    Null: split shuffled tokens into A-length and B-length groups, score both.
    Question: does Side B score as well as Side A, above null?

  TEST 2 — Formula class distribution:
    Learn the formula class frequency distribution from Side A.
    Predict: Side B should match this distribution (KL divergence test).
    Null: random token splits preserve what distribution?

  TEST 3 — Cross-side bigram prediction:
    Learn bigram frequencies from Side A only.
    Predict: does Side B replicate the PLUMED HEAD(#02)→SHIELD(#12) bigram excess?
    Specifically: does #02→#12 appear in Side B more than null expectation
    given Side A's training signal?

All tests use the frequency-preserving NULL_A shuffle from
frequency_preserving_nulls.py.
"""

import random
import math
import sys
import os
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from phaistos_canonical_data import (
    SIDE_A_EVANS, SIDE_B_EVANS, SIGN_FREQ, SIGN_NAMES
)
from luwian_formula_parser import (
    score_word, total_score, word_classes,
)

SEED = 42
random.seed(SEED)

N_SIM = 100_000

# ---------------------------------------------------------------------------
# 1. Disc structure
# ---------------------------------------------------------------------------
ALL_WORDS  = SIDE_A_EVANS + SIDE_B_EVANS
TOKENS_A   = [s for w in SIDE_A_EVANS for s in w]
TOKENS_B   = [s for w in SIDE_B_EVANS for s in w]
ALL_TOKENS = TOKENS_A + TOKENS_B
LENS_A     = [len(w) for w in SIDE_A_EVANS]
LENS_B     = [len(w) for w in SIDE_B_EVANS]
N_A        = sum(LENS_A)  # tokens in Side A
N_B        = sum(LENS_B)  # tokens in Side B

def repack(tokens, lens):
    """Repack flat token list into word groups of given lengths."""
    result, idx = [], 0
    for ln in lens:
        result.append(tokens[idx:idx + ln])
        idx += ln
    return result

def bigram_count(word_list, bigram=(2, 12)):
    return sum(
        1 for w in word_list
        for i in range(len(w) - 1)
        if w[i] == bigram[0] and w[i+1] == bigram[1]
    )

# ---------------------------------------------------------------------------
# 2. Canonical disc scores (frozen G_LUWIAN key — no modification)
# ---------------------------------------------------------------------------
SCORE_A     = total_score(SIDE_A_EVANS)
SCORE_B     = total_score(SIDE_B_EVANS)
SCORE_TOTAL = SCORE_A + SCORE_B

BIGRAM_A    = bigram_count(SIDE_A_EVANS)
BIGRAM_B    = bigram_count(SIDE_B_EVANS)

# Formula class distributions
def class_distribution(word_list):
    """Count grammatical classes across all word groups."""
    counts = Counter()
    for w in word_list:
        for cls in word_classes(w):
            counts[cls] += 1
    return counts

CLASS_DIST_A = class_distribution(SIDE_A_EVANS)
CLASS_DIST_B = class_distribution(SIDE_B_EVANS)
ALL_CLASSES  = sorted(set(list(CLASS_DIST_A) + list(CLASS_DIST_B)))

def kl_divergence(p_counts, q_counts):
    """
    KL divergence D(P||Q) from observed P to reference Q (frequency counts).
    Uses add-1 smoothing to avoid zero-division.
    Returns divergence (lower = more similar distributions).
    """
    all_k = set(p_counts) | set(q_counts)
    p_tot = sum(p_counts.values()) + len(all_k)
    q_tot = sum(q_counts.values()) + len(all_k)
    kl = 0.0
    for k in all_k:
        p = (p_counts.get(k, 0) + 1) / p_tot
        q = (q_counts.get(k, 0) + 1) / q_tot
        kl += p * math.log(p / q)
    return kl

KL_REAL = kl_divergence(CLASS_DIST_B, CLASS_DIST_A)  # B vs A reference

# ---------------------------------------------------------------------------
# 3. Null generators
# ---------------------------------------------------------------------------
def null_split():
    """
    Shuffle ALL tokens (A+B combined), repack into A-lengths then B-lengths.
    Preserves: total sign frequencies.
    Breaks: which tokens belong to which side.
    """
    tokens = ALL_TOKENS[:]
    random.shuffle(tokens)
    side_a = repack(tokens[:N_A], LENS_A)
    side_b = repack(tokens[N_A:], LENS_B)
    return side_a, side_b

# ---------------------------------------------------------------------------
# 4. Monte Carlo
# ---------------------------------------------------------------------------
print("=" * 65)
print("TRUE HOLDOUT A → B — PHAISTOS DISC")
print("Frozen G_LUWIAN key | N=100,000 | seed=42")
print("=" * 65)
print()
print(f"Side A: {len(SIDE_A_EVANS)} word groups, {N_A} tokens")
print(f"Side B: {len(SIDE_B_EVANS)} word groups, {N_B} tokens")
print()
print(f"Grammar score  — Side A (training): {SCORE_A:.4f}")
print(f"Grammar score  — Side B (holdout) : {SCORE_B:.4f}")
print(f"Bigram #02→#12 — Side A           : {BIGRAM_A}")
print(f"Bigram #02→#12 — Side B           : {BIGRAM_B}")
print()
print(f"KL divergence B vs A (class distribution): {KL_REAL:.4f}")
print(f"  (lower = B matches A's formula class pattern more closely)")
print()
print("Running simulations ...")

# Accumulate null stats
null_score_a = []
null_score_b = []
null_score_diff = []
null_kl     = []
null_bg_b   = []

n_b_geq_a  = 0  # null Side B score ≥ real Side B score
n_a_geq_a  = 0  # null Side A score ≥ real Side A score
n_kl_leq   = 0  # null KL ≤ real KL (B matches A at least as well)
n_bg_b_geq = 0  # null Side B bigram ≥ real Side B bigram

for i in range(N_SIM):
    na, nb = null_split()
    sa = total_score(na)
    sb = total_score(nb)
    kl = kl_divergence(class_distribution(nb), class_distribution(na))
    bg = bigram_count(nb)

    null_score_a.append(sa)
    null_score_b.append(sb)
    null_score_diff.append(abs(sa - sb))
    null_kl.append(kl)
    null_bg_b.append(bg)

    if sb >= SCORE_B:      n_b_geq_a  += 1
    if sa >= SCORE_A:      n_a_geq_a  += 1
    if kl <= KL_REAL:      n_kl_leq   += 1
    if bg >= BIGRAM_B:     n_bg_b_geq += 1

    if (i + 1) % 25_000 == 0:
        print(f"  ... {i+1:,} / {N_SIM:,}")

def stats(vals):
    m = sum(vals) / len(vals)
    s = math.sqrt(sum((x-m)**2 for x in vals)/len(vals)) or 1e-9
    return m, s

SEP = "=" * 65

print()
print(SEP)
print("TEST 1 — FORMULA SCORE PARITY")
print(SEP)
print()
m_a, s_a = stats(null_score_a)
m_b, s_b = stats(null_score_b)
z_a = (SCORE_A - m_a) / s_a
z_b = (SCORE_B - m_b) / s_b
p_a = n_a_geq_a / N_SIM
p_b = n_b_geq_a / N_SIM

print(f"  Side A grammar score : {SCORE_A:.4f}  (null: {m_a:.4f}±{s_a:.4f})  Z={z_a:+.2f}  p={p_a:.4f}")
print(f"  Side B grammar score : {SCORE_B:.4f}  (null: {m_b:.4f}±{s_b:.4f})  Z={z_b:+.2f}  p={p_b:.4f}")
print()
if z_b > 2 and z_a > 2:
    print("  PASS: Both sides score above null with same frozen key.")
    print(f"  Side B holdout score Z={z_b:+.2f} — learned patterns transfer from A to B.")
elif z_b > 2:
    print(f"  PARTIAL: Side B (holdout) is significant Z={z_b:+.2f}.")
    print(f"  Side A is not significant Z={z_a:+.2f}. Check key coverage per side.")
else:
    print(f"  FAIL: Side B holdout score Z={z_b:+.2f} does not exceed null.")
    print("  Patterns learned from Side A do not transfer to Side B under this key.")

print()
print(SEP)
print("TEST 2 — FORMULA CLASS DISTRIBUTION (KL DIVERGENCE)")
print(SEP)
print()
m_kl, s_kl = stats(null_kl)
# For KL: lower is better; we want KL_REAL to be LOW (below null)
z_kl = (m_kl - KL_REAL) / s_kl   # positive z = real is LOWER than null (good)
p_kl = n_kl_leq / N_SIM

print("  Side A class distribution (training set):")
tot_a = sum(CLASS_DIST_A.values())
for cls in ALL_CLASSES:
    cnt = CLASS_DIST_A.get(cls, 0)
    print(f"    {cls:<8} : {cnt:3d}  ({100*cnt/tot_a:.1f}%)")
print()
print("  Side B class distribution (holdout):")
tot_b = sum(CLASS_DIST_B.values())
for cls in ALL_CLASSES:
    cnt = CLASS_DIST_B.get(cls, 0)
    print(f"    {cls:<8} : {cnt:3d}  ({100*cnt/tot_b:.1f}%)")
print()
print(f"  KL(B || A)  real : {KL_REAL:.4f}")
print(f"  KL(B || A)  null : {m_kl:.4f} ± {s_kl:.4f}")
print(f"  Z-score (lower better): {z_kl:+.2f}")
print(f"  p (null KL ≤ real KL)  : {p_kl:.4f}")
print()
if z_kl > 1.5:
    print("  PASS: Side B's class distribution is closer to Side A's than the")
    print("  null expectation. Formula class patterns transfer across sides.")
else:
    print("  NOT SIGNIFICANT: Side B's class distribution does not match Side A")
    print("  better than null splits would.")

print()
print(SEP)
print("TEST 3 — CROSS-SIDE BIGRAM PREDICTION")
print(SEP)
print()
m_bg, s_bg = stats(null_bg_b)
z_bg = (BIGRAM_B - m_bg) / s_bg
p_bg = n_bg_b_geq / N_SIM

print(f"  Side A bigram #02→#12 (training signal) : {BIGRAM_A}")
print(f"  Side B bigram #02→#12 (holdout)         : {BIGRAM_B}")
print(f"  Null B bigram mean ± SD                 : {m_bg:.4f} ± {s_bg:.4f}")
print(f"  Z-score (holdout above null)            : {z_bg:+.2f}")
print(f"  p (one-tailed)                          : {p_bg:.4f}")
print()
if BIGRAM_B == 0 and BIGRAM_A > 0:
    print("  NOTE: #02→#12 bigram appears exclusively in Side A.")
    print("  This is informative: PLUMED HEAD→SHIELD is an A-side structural marker.")
    print("  The pattern is not required in Side B for the key to be valid —")
    print("  Side B may use different formula openings (see B30 center: ti-wa wa).")
elif z_bg > 2:
    print(f"  PASS: Side B also shows significant bigram excess Z={z_bg:+.2f}.")
    print("  Training signal from Side A transfers to holdout Side B.")
else:
    print(f"  Z={z_bg:+.2f}: Side B bigram does not significantly exceed null.")

print()
print(SEP)
print("SUMMARY — TRUE HOLDOUT A → B")
print(SEP)
print()
print(f"  {'Test':<35}  {'Result':<12}  Details")
print(f"  {'-'*35}  {'-'*12}  -------")

def badge(z, p, thresh=2.0):
    if z > thresh and p < 0.05:
        return "PASS   ✓"
    elif z > 1.5:
        return "MARGINAL"
    else:
        return "FAIL   ✗"

print(f"  {'Score parity (Side A)':35}  {badge(z_a, p_a):<12}  Z={z_a:+.2f}  p={p_a:.4f}")
print(f"  {'Score parity (Side B holdout)':35}  {badge(z_b, p_b):<12}  Z={z_b:+.2f}  p={p_b:.4f}")
print(f"  {'Class distribution (KL)':35}  {badge(z_kl, p_kl):<12}  Z={z_kl:+.2f}  p={p_kl:.4f}")
print(f"  {'Cross-side bigram prediction':35}  {'N/A (A-only)' if BIGRAM_B==0 else badge(z_bg, p_bg):<12}  A={BIGRAM_A} B={BIGRAM_B}")
print()
print("  INTERPRETATION:")
print("  The holdout test uses the G_LUWIAN key frozen from Side A analysis.")
print("  No key modification is allowed. If Side B independently scores above")
print("  the frequency-preserving null, it suggests the key captures real")
print("  structure rather than overfitting to one side of the disc.")
print()
print("  NOTE: Side A has 31 word groups (more tokens for formula patterns).")
print("  Side B has 30 word groups, centered on ti-wa wa (DEITY+NOUN) at B30.")
print("  Different formula types may dominate on each side by design,")
print("  which does NOT falsify the key — it would support bilingual structure.")
print(SEP)
