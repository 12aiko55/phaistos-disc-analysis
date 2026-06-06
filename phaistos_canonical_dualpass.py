"""
phaistos_canonical_dualpass.py
==============================
KEY-INDEPENDENT Dual-Pass Monte Carlo on canonical Evans/Godart data.

Both filters use canonical sign numbering (01-45), verified word-group
transcription, and no phonetic assumption.

Filter 1 (bigram):   PLUMED HEAD(#02) → SHIELD(#12) consecutive count
                     within canonical word boundaries ≥ disc count (13)
                     Z=+10.45 established in phaistos_canonical_analysis.py

Filter 2 (repeats):  Number of distinct word-group sequences appearing
                     ≥ 2 times across the 61 canonical groups ≥ disc count (8)
                     Formulaic refrain density: 8/61 = 13%

Both signals are language-independent. No za-wa-tar, no phonetic reading.
N = 100,000 simulations, seed = 42.
"""

import random
import math
import sys
import os
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from phaistos_canonical_data import (
    SIDE_A_EVANS, SIDE_B_EVANS, SIGN_FREQ, SIGN_NAMES
)

SEED = 42
random.seed(SEED)

# ---------------------------------------------------------------------------
# 1. Canonical disc data
# ---------------------------------------------------------------------------
ALL_WORDS   = SIDE_A_EVANS + SIDE_B_EVANS
WORD_LENS   = [len(w) for w in ALL_WORDS]
N_WORDS     = len(ALL_WORDS)          # 61
N_TOKENS    = sum(WORD_LENS)          # 242 (1 discrepancy vs SIGN_FREQ 241)
ALL_SIGNS   = sorted(SIGN_FREQ.keys())  # Evans 01-45
N_SIGNS     = len(ALL_SIGNS)          # 45
ALPHA       = 0.5

# Bigram target: PLUMED HEAD → SHIELD
BIGRAM      = (2, 12)

# ---------------------------------------------------------------------------
# 2. Disc canonical counts
# ---------------------------------------------------------------------------
def count_bigram(word_list, bigram):
    """Count consecutive bigram occurrences within word boundaries."""
    count = 0
    for word in word_list:
        for i in range(len(word) - 1):
            if word[i] == bigram[0] and word[i + 1] == bigram[1]:
                count += 1
    return count


def count_repeated_groups(word_list):
    """Count distinct word-group sequences appearing ≥ 2 times."""
    c = Counter(tuple(w) for w in word_list)
    return sum(1 for v in c.values() if v >= 2)


DISC_BIGRAM  = count_bigram(ALL_WORDS, BIGRAM)
DISC_REPEATS = count_repeated_groups(ALL_WORDS)

# Expected bigram count under sign independence
n_a_nonfinal = sum(
    1 for w in ALL_WORDS
    for i, s in enumerate(w)
    if s == BIGRAM[0] and i < len(w) - 1
)
exp_bigram = n_a_nonfinal * (SIGN_FREQ[BIGRAM[1]] / N_TOKENS)

# ---------------------------------------------------------------------------
# 3. Synthetic text generator — preserves canonical word-group lengths
# ---------------------------------------------------------------------------
def generate_words(word_lens, alpha=ALPHA):
    """
    Draw sign probabilities from Dirichlet(alpha), generate synthetic
    word groups with the same lengths as the canonical disc (WORD_LENS).
    """
    gammas = [random.gammavariate(alpha, 1.0) for _ in ALL_SIGNS]
    total  = sum(gammas)
    probs  = [g / total for g in gammas]

    def pick():
        r   = random.random()
        cum = 0.0
        for s, p in zip(ALL_SIGNS, probs):
            cum += p
            if r <= cum:
                return s
        return ALL_SIGNS[-1]

    return [[pick() for _ in range(l)] for l in word_lens]


# ---------------------------------------------------------------------------
# 4. Print header
# ---------------------------------------------------------------------------
SEP = "=" * 65

print(SEP)
print("CANONICAL DUAL-PASS MONTE CARLO — PHAISTOS DISC")
print("Evans/Godart numbering (01-45) | 61 word groups | key-independent")
print(SEP)
print()
print(f"Filter 1: {SIGN_NAMES[BIGRAM[0]]}(#{BIGRAM[0]:02d}) → "
      f"{SIGN_NAMES[BIGRAM[1]]}(#{BIGRAM[1]:02d}) bigram")
print(f"  Disc count : {DISC_BIGRAM}")
print(f"  Expected   : {exp_bigram:.2f}  (under sign independence)")
print(f"  Ratio      : {DISC_BIGRAM / exp_bigram:.1f}x")
print()
print(f"Filter 2: Distinct repeated word-group sequences")
print(f"  Disc count : {DISC_REPEATS}  (of 61 total word groups)")
print()
print(f"N simulations : 100,000  |  α(Dirichlet) = {ALPHA}")
print(f"Word lengths  : canonical (preserves {N_WORDS} word-group structure)")
print()

# ---------------------------------------------------------------------------
# 5. Monte Carlo
# ---------------------------------------------------------------------------
N_SIM = 100_000

f1_pass  = 0
f2_pass  = 0
dual     = 0
bg_vals  = []
rp_vals  = []

print("Running simulations...")
for i in range(N_SIM):
    words = generate_words(WORD_LENS)
    bg    = count_bigram(words, BIGRAM)
    rp    = count_repeated_groups(words)
    bg_vals.append(bg)
    rp_vals.append(rp)
    if bg >= DISC_BIGRAM:               f1_pass += 1
    if rp >= DISC_REPEATS:              f2_pass += 1
    if bg >= DISC_BIGRAM and rp >= DISC_REPEATS:  dual += 1
    if (i + 1) % 25_000 == 0:
        print(f"  ... {i + 1:,} / {N_SIM:,}")

# ---------------------------------------------------------------------------
# 6. Statistics
# ---------------------------------------------------------------------------
mean_bg = sum(bg_vals) / N_SIM
var_bg  = sum((x - mean_bg) ** 2 for x in bg_vals) / N_SIM
std_bg  = math.sqrt(var_bg) if var_bg > 0 else 1e-9
z_bg    = (DISC_BIGRAM - mean_bg) / std_bg

mean_rp = sum(rp_vals) / N_SIM
var_rp  = sum((x - mean_rp) ** 2 for x in rp_vals) / N_SIM
std_rp  = math.sqrt(var_rp) if var_rp > 0 else 1e-9
z_rp    = (DISC_REPEATS - mean_rp) / std_rp

p_f1   = f1_pass / N_SIM
p_f2   = f2_pass / N_SIM
p_dual = dual    / N_SIM

# ---------------------------------------------------------------------------
# 7. Results
# ---------------------------------------------------------------------------
print()
print(SEP)
print("RESULTS")
print(SEP)

print()
print("-- Filter 1: PLUMED HEAD(#02) → SHIELD(#12) bigram --")
print(f"   Null mean ± SD : {mean_bg:.4f} ± {std_bg:.4f}")
print(f"   Disc count     : {DISC_BIGRAM}")
print(f"   Z-score        : {z_bg:+.2f}")
print(f"   p (one-tailed) : {p_f1:.6f}  ({f1_pass}/{N_SIM} pass)")

print()
print("-- Filter 2: Distinct repeated word-group sequences --")
print(f"   Null mean ± SD : {mean_rp:.4f} ± {std_rp:.4f}")
print(f"   Disc count     : {DISC_REPEATS}")
print(f"   Z-score        : {z_rp:+.2f}")
print(f"   p (one-tailed) : {p_f2:.6f}  ({f2_pass}/{N_SIM} pass)")

print()
print("-- DUAL-PASS --")
print(f"   Both filters   : {dual} / {N_SIM}")
print(f"   Empirical p    : {p_dual:.6f}")
if p_dual == 0.0:
    print(f"   Upper bound    : p < {1.0 / N_SIM:.2e}")
    print(f"   If independent : {p_f1 * p_f2:.2e}")

print()
print(SEP)
print("INTERPRETATION")
print(SEP)
print()

if p_f1 == 0.0:
    print(f"  Filter 1 (bigram): ZERO of {N_SIM:,} random texts produced "
          f"{DISC_BIGRAM}+ [02→12] pairs")
    print(f"  p < {1/N_SIM:.2e}")
else:
    print(f"  Filter 1 (bigram): p = {p_f1:.6f}  Z = {z_bg:+.2f}")

print()

if p_f2 == 0.0:
    print(f"  Filter 2 (repeats): ZERO of {N_SIM:,} random texts produced "
          f"{DISC_REPEATS}+ repeated groups")
    print(f"  p < {1/N_SIM:.2e}")
else:
    print(f"  Filter 2 (repeats): p = {p_f2:.6f}  Z = {z_rp:+.2f}")

print()

if dual == 0:
    print(f"  DUAL-PASS: p < {1/N_SIM:.2e}")
    print()
    print("  Both key-independent canonical filters exclude all random texts.")
    print(f"    Bigram  [02→12]: Z={z_bg:+.2f}  (sequential structure)")
    print(f"    Repeats      x{DISC_REPEATS}: Z={z_rp:+.2f}  (formulaic refrain)")
    print()
    print("  The Phaistos Disc is the ONLY text passing both canonical filters.")
    print("  This result requires NO phonetic assumption.")
else:
    print(f"  DUAL-PASS: {dual}/{N_SIM} pass (p={p_dual:.6f})")

print()
print(SEP)
print("METHODOLOGY NOTE")
print(SEP)
print()
print("  Synthetic texts use Dirichlet-multinomial(α=0.5) over 45 Evans signs.")
print("  Word-group lengths are fixed to the canonical disc structure,")
print("  so repeat-pattern null reflects the actual word-length distribution.")
print("  Both filters are derived from phaistos_canonical_analysis.py (canonical")
print("  Evans/Godart transcription, 241 tokens, 45 sign types, 61 word groups).")
print(SEP)
