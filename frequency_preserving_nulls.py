"""
frequency_preserving_nulls.py
==============================
Library of frequency-preserving null models for the Phaistos Disc.

The Dirichlet-multinomial null in phaistos_canonical_dualpass.py draws
sign probabilities from a prior — it does NOT preserve exact sign frequencies.
These shuffles are MORE conservative: they fix the actual marginal counts.

Four shuffle strategies (each importable or run standalone):

  NULL_A  FreqShuffle      — shuffle all tokens, same word lengths
                             Preserves: sign freq, word-group lengths
                             Breaks: bigrams, positional distributions

  NULL_B  WordShuffle      — shuffle whole word groups (swap positions)
                             Preserves: sign freq, word-group lengths, bigrams
                             Breaks: word-position structure (which group is word 3?)

  NULL_C  PositionalShuffle — shuffle within positional slots (initial/medial/final)
                              Preserves: freq per positional class, word lengths
                              Breaks: adjacent sign structure within position class

  NULL_D  SideShuffle      — shuffle tokens within each side independently
                             Preserves: side-level freq, word lengths per side
                             Breaks: cross-side patterns (A/B correlations)

Each function returns a list of word groups (same structure as SIDE_A_EVANS +
SIDE_B_EVANS). All are seeded via the passed rng argument for reproducibility.

Standalone mode runs comparison of all 4 null types against the real disc's
formula grammar score and canonical dual-pass metrics.
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

# ---------------------------------------------------------------------------
# Disc structure constants
# ---------------------------------------------------------------------------
ALL_WORDS   = SIDE_A_EVANS + SIDE_B_EVANS
WORD_LENS   = [len(w) for w in ALL_WORDS]
ALL_TOKENS  = [s for w in ALL_WORDS for s in w]
N_WORDS     = len(ALL_WORDS)   # 61
N_TOKENS    = len(ALL_TOKENS)  # 242 (1 discrepancy with SIGN_FREQ 241)
N_A         = len(SIDE_A_EVANS)  # 31
N_B         = len(SIDE_B_EVANS)  # 30

TOKENS_A    = [s for w in SIDE_A_EVANS for s in w]
TOKENS_B    = [s for w in SIDE_B_EVANS for s in w]
LENS_A      = [len(w) for w in SIDE_A_EVANS]
LENS_B      = [len(w) for w in SIDE_B_EVANS]

# Positional slots: initial (word position 0), medial (1..n-2), final (n-1)
INITIAL_TOKENS = [w[0]         for w in ALL_WORDS]
FINAL_TOKENS   = [w[-1]        for w in ALL_WORDS if len(w) > 1]
MEDIAL_TOKENS  = [s for w in ALL_WORDS for i, s in enumerate(w)
                   if 0 < i < len(w) - 1]

# ---------------------------------------------------------------------------
# NULL_A: Full frequency shuffle — all tokens reordered randomly
# ---------------------------------------------------------------------------
def null_a_freq_shuffle(rng=None):
    """
    Shuffle all 242 tokens randomly, repack into original word-group lengths.
    Most basic conservative null: preserves total sign frequencies + word lengths.
    """
    if rng is None:
        rng = random
    tokens = ALL_TOKENS[:]
    rng.shuffle(tokens)
    result, idx = [], 0
    for ln in WORD_LENS:
        result.append(tokens[idx:idx + ln])
        idx += ln
    return result

# ---------------------------------------------------------------------------
# NULL_B: Word-group shuffle — swap entire word groups
# ---------------------------------------------------------------------------
def null_b_word_shuffle(rng=None):
    """
    Shuffle the order of entire word groups.
    Preserves: sign freq, all within-word bigrams and lengths.
    Breaks: which position in the spiral each word group occupies.
    """
    if rng is None:
        rng = random
    shuffled = ALL_WORDS[:]
    rng.shuffle(shuffled)
    return shuffled

# ---------------------------------------------------------------------------
# NULL_C: Positional shuffle — shuffle within initial/medial/final slots
# ---------------------------------------------------------------------------
def null_c_positional_shuffle(rng=None):
    """
    Shuffle tokens independently within three positional slots:
      initial : all word-initial positions (one per word group)
      medial  : all middle positions
      final   : all word-final positions (one per word group with len > 1)

    Preserves: total freq per positional class, word-group lengths.
    Breaks: specific sign at specific position, cross-position bigrams.
    """
    if rng is None:
        rng = random

    # Collect tokens per slot
    init_pool   = INITIAL_TOKENS[:]
    final_pool  = FINAL_TOKENS[:]
    medial_pool = MEDIAL_TOKENS[:]
    rng.shuffle(init_pool)
    rng.shuffle(final_pool)
    rng.shuffle(medial_pool)

    result = []
    init_idx = final_idx = medial_idx = 0
    for w in ALL_WORDS:
        ln = len(w)
        if ln == 1:
            result.append([init_pool[init_idx]])
            init_idx += 1
        elif ln == 2:
            result.append([init_pool[init_idx], final_pool[final_idx]])
            init_idx  += 1
            final_idx += 1
        else:
            mid = [medial_pool[medial_idx + k] for k in range(ln - 2)]
            result.append([init_pool[init_idx]] + mid + [final_pool[final_idx]])
            init_idx    += 1
            final_idx   += 1
            medial_idx  += (ln - 2)
    return result

# ---------------------------------------------------------------------------
# NULL_D: Side-independent shuffle — shuffle A and B tokens separately
# ---------------------------------------------------------------------------
def null_d_side_shuffle(rng=None):
    """
    Shuffle tokens within Side A independently of Side B.
    Preserves: per-side sign frequency, word-group lengths per side.
    Breaks: cross-side patterns (A31 ↔ B30 correlation, cross-side repeats).
    """
    if rng is None:
        rng = random

    tok_a = TOKENS_A[:]
    tok_b = TOKENS_B[:]
    rng.shuffle(tok_a)
    rng.shuffle(tok_b)

    result, idx = [], 0
    for ln in LENS_A:
        result.append(tok_a[idx:idx + ln])
        idx += ln

    result_b, idx = [], 0
    for ln in LENS_B:
        result_b.append(tok_b[idx:idx + ln])
        idx += ln

    return result + result_b

# ---------------------------------------------------------------------------
# Metric functions — same as in other scripts, redefined here for self-contained use
# ---------------------------------------------------------------------------

def count_bigram_in_words(word_list, bigram=(2, 12)):
    """Count consecutive bigram (default: PLUMED HEAD → SHIELD) within words."""
    return sum(
        1 for w in word_list
        for i in range(len(w) - 1)
        if w[i] == bigram[0] and w[i+1] == bigram[1]
    )

def count_repeated_groups(word_list):
    """Count distinct word-group sequences appearing ≥2 times."""
    c = Counter(tuple(w) for w in word_list)
    return sum(1 for v in c.values() if v >= 2)

def word_initial_exclusivity(word_list, sign=2):
    """
    Fraction of sign occurrences that are word-initial.
    Returns (n_initial, n_total).
    """
    n_total   = sum(s == sign for w in word_list for s in w)
    n_initial = sum(1 for w in word_list if w and w[0] == sign)
    return n_initial, n_total

# ---------------------------------------------------------------------------
# Run comparison when executed directly
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    N_SIM = 100_000
    SEED  = 42
    rng   = random.Random(SEED)

    SEP = "=" * 70

    # Real disc values
    DISC_BIGRAM  = count_bigram_in_words(ALL_WORDS)
    DISC_REPEATS = count_repeated_groups(ALL_WORDS)
    init_disc, tot_disc = word_initial_exclusivity(ALL_WORDS)

    print(SEP)
    print("FREQUENCY-PRESERVING NULL MODELS — PHAISTOS DISC")
    print("Four shuffle strategies | N=100,000 each | seed=42")
    print(SEP)
    print()
    print("DISC CANONICAL VALUES:")
    print(f"  PLUMED HEAD(#02)→SHIELD(#12) bigram : {DISC_BIGRAM}")
    print(f"  Distinct repeated word groups        : {DISC_REPEATS}")
    print(f"  PLUMED HEAD(#02) word-initial        : {init_disc}/{tot_disc}")
    print()

    nulls = [
        ("NULL_A FreqShuffle",     null_a_freq_shuffle),
        ("NULL_B WordShuffle",     null_b_word_shuffle),
        ("NULL_C PositionalShuf",  null_c_positional_shuffle),
        ("NULL_D SideShuf",        null_d_side_shuffle),
    ]

    print(f"{'Null model':<24}  {'Metric':<30}  {'Mean±SD':>14}  {'Z':>6}  p")
    print("-" * 90)

    for name, null_fn in nulls:
        bg_vals = []
        rp_vals = []
        init_vals = []

        for i in range(N_SIM):
            w = null_fn(rng)
            bg_vals.append(count_bigram_in_words(w))
            rp_vals.append(count_repeated_groups(w))
            ni, nt = word_initial_exclusivity(w)
            init_vals.append(ni / nt if nt > 0 else 0.0)

        for label, disc_val, vals in [
            ("bigram #02→#12", DISC_BIGRAM, bg_vals),
            ("repeated groups", DISC_REPEATS, rp_vals),
            ("init exclusivity", init_disc/tot_disc, init_vals),
        ]:
            mean_ = sum(vals) / N_SIM
            std_  = math.sqrt(sum((x-mean_)**2 for x in vals)/N_SIM) or 1e-9
            z_    = (disc_val - mean_) / std_
            p_    = sum(1 for v in vals if v >= disc_val) / N_SIM
            print(f"  {name:<22}  {label:<30}  {mean_:.3f} ± {std_:.3f}  {z_:+6.2f}  {p_:.4f}")
        print()

    print(SEP)
    print("INTERPRETATION")
    print(SEP)
    print()
    print("  All four null strategies preserve sign frequencies and word lengths.")
    print("  NULL_B (word-group shuffle) is the most conservative for bigram tests")
    print("  because it preserves ALL within-word structure (bigrams, trigrams).")
    print("  NULL_A is most conservative for word-level repeat tests.")
    print("  NULL_C tests positional structure independent of adjacency.")
    print("  NULL_D tests cross-side correlation.")
    print()
    print("  Import from this module in other scripts:")
    print("    from frequency_preserving_nulls import null_a_freq_shuffle, ...")
    print(SEP)
