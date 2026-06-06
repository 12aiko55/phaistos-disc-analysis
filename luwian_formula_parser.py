"""
luwian_formula_parser.py
========================
Grammar-aware Luwian formula parser for the Phaistos Disc.

Assigns grammatical classes to G_LUWIAN signs (Evans/Godart canonical
numbering), defines formula templates derived from Luwian Hieroglyphic
text structure, and scores each word group by how well it matches
recognizable Luwian grammatical patterns.

Replaces substring scoring (score_vs_vocab) with a structure-aware scorer.

NULL MODEL: frequency-preserving shuffle (N=100,000 simulations).
Preserves exact sign frequencies AND word-group lengths simultaneously.
This is MORE conservative than the Dirichlet-multinomial null used in
phaistos_canonical_dualpass.py.

CONFIRMED Evans assignments used here:
  Evans #02 PLUMED HEAD = za  [DEM]  — paper §7, table §3.3
  Evans #07 HELMET      = wa  [NOUN] — confirmed via freq match (18x)
  Evans #12 SHIELD      = zi  [PTCL] — paper §7 "za-zi = DEM + GEN"
  Evans #45 WAVY BAND   = ti-wa [DEITY] — canonical spiral center B30
  Evans #22 SLING       = ha  [PTCL] — inferred: positional/freq analysis
  Evans #29 CAT         = na  [GEN]  — inferred: 11x freq candidate
  Evans #01 PEDESTRIAN  = i   [PRON] — inferred: number/positional match
  Evans #03 TATTOOED HEAD = pa [NOUN] — inferred: spiral center component

Sources: Hawkins (2000), Melchert (2003), PAPER_EN.md §3.3 + §7.
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
# 1. G_LUWIAN phonetic key — Evans/Godart sign numbering
#    Confidence: CONFIRMED = paper §7 explicit; INFERRED = freq/positional
# ---------------------------------------------------------------------------
G_LUWIAN_KEY = {
    #  sign : (syllable,   confidence)
     2: ("za",   "CONFIRMED"),   # PLUMED HEAD → demonstrative (§7, always word-initial)
     7: ("wa",   "CONFIRMED"),   # HELMET → wa- (wa-tar water; old #36 freq match)
    12: ("zi",   "CONFIRMED"),   # SHIELD → genitive/enclitic (§7 "za-zi pair")
    45: ("ti-wa","CONFIRMED"),   # WAVY BAND → Tiwat sun deity (spiral center B30)
    22: ("ha",   "INFERRED"),    # SLING → affirmative particle (Luwian ritual texts)
    29: ("na",   "INFERRED"),    # CAT → genitive particle (11x freq candidate)
     1: ("i",    "INFERRED"),    # PEDESTRIAN → connective pronoun (11x freq candidate)
     3: ("pa",   "INFERRED"),    # TATTOOED HEAD → noun/adjective (spiral center A31)
}

SYLLABLE_TO_SIGN = {syl: s for s, (syl, _) in G_LUWIAN_KEY.items()}

# ---------------------------------------------------------------------------
# 2. Grammatical class assignments
#    Derived from Luwian Hieroglyphic grammar (Hawkins 2000; Melchert 2003)
#
#  DEITY : divine theonym (subject of invocation)
#  DEM   : demonstrative pronoun/adjective (article-like, word-initial)
#  NOUN  : common noun or nominal element
#  PTCL  : particle (affirmative, enclitic, connective)
#  GEN   : genitive/possessive marker
#  PRON  : personal pronoun
#  UNK   : sign not assigned in this key
# ---------------------------------------------------------------------------
SYLLABLE_CLASS = {
    "ti-wa": "DEITY",
    "za":    "DEM",
    "wa":    "NOUN",    # wa-tar component — nominal root
    "zi":    "PTCL",    # enclitic particle (genitive/case marker)
    "ha":    "PTCL",    # affirmative particle
    "na":    "GEN",     # genitive marker
    "i":     "PRON",    # connective/pronoun
    "pa":    "NOUN",    # noun/adjective
}

def sign_class(sign):
    """Return grammatical class for an Evans sign number. UNK if not in key."""
    entry = G_LUWIAN_KEY.get(sign)
    if entry is None:
        return "UNK"
    return SYLLABLE_CLASS.get(entry[0], "UNK")

def sign_syllable(sign):
    """Return syllable reading for an Evans sign number."""
    entry = G_LUWIAN_KEY.get(sign)
    return entry[0] if entry else f"#{sign:02d}"

# ---------------------------------------------------------------------------
# 3. Luwian ritual formula templates
#    Source: attested patterns in Luwian Hieroglyphic ritual/votive texts
#    (Hawkins 2000 corpus; Melchert 2003 grammar)
#
#  Each entry: (weight, class_tuple)
#  weight 3 = major ritual formula (high confidence)
#  weight 2 = common syntactic phrase
#  weight 1 = minimal recognizable structure
# ---------------------------------------------------------------------------
FORMULAS = [
    # --- Major ritual formulae (weight 3) ---
    (3, ("DEITY", "DEM",  "NOUN",  "PTCL")),     # ti-wa za NOUN ha → "Tiwat, this X, yes"
    (3, ("DEM",   "NOUN", "GEN",   "PTCL")),     # za NOUN na ha → "this X's [affirmation]"
    (3, ("DEITY", "NOUN", "DEM",   "PTCL")),     # ti-wa NOUN za ha → variant order
    (3, ("DEM",   "GEN",  "NOUN",  "PTCL")),     # demonstrative genitival phrase
    (3, ("DEITY", "DEM",  "NOUN",  "GEN")),      # divine + demonstrative + noun + genitive
    (3, ("NOUN",  "GEN",  "DEITY", "PTCL")),     # noun + genitive + divine + particle

    # --- Common syntactic phrases (weight 2) ---
    (2, ("DEITY", "DEM",  "NOUN")),              # minimal invocation: Tiwat + demonstr + noun
    (2, ("DEM",   "NOUN", "PTCL")),              # demonstr + noun + particle
    (2, ("DEM",   "PTCL", "NOUN")),              # demonstr + particle + noun
    (2, ("NOUN",  "GEN",  "NOUN")),              # genitive chain: noun-of-noun
    (2, ("PRON",  "NOUN", "PTCL")),              # pronoun + noun + particle
    (2, ("DEM",   "NOUN", "GEN")),               # demonstr + noun + genitive
    (2, ("DEITY", "PTCL")),                      # deity + particle (invocation minimal)
    (2, ("DEITY", "NOUN")),                      # deity + noun (possession/identity)
    (2, ("NOUN",  "PTCL", "NOUN")),              # noun + connector + noun

    # --- Minimal structures (weight 1) ---
    (1, ("DEM",   "NOUN")),                      # minimal demonstrative phrase
    (1, ("NOUN",  "GEN")),                       # minimal genitive phrase
    (1, ("NOUN",  "PTCL")),                      # noun + particle (common Luwian)
    (1, ("DEM",   "PTCL")),                      # demonstr + particle
    (1, ("PRON",  "NOUN")),                      # pronoun + noun
    (1, ("GEN",   "NOUN")),                      # genitive + noun (head-final)
    (1, ("DEITY", "PRON")),                      # deity + pronoun
]

# ---------------------------------------------------------------------------
# 4. Scoring function
# ---------------------------------------------------------------------------
def word_classes(word):
    """Convert list of Evans sign numbers to tuple of grammatical classes."""
    return tuple(sign_class(s) for s in word)

def unk_fraction(class_seq):
    if not class_seq:
        return 1.0
    return class_seq.count("UNK") / len(class_seq)

def score_word(word):
    """
    Score a single word group against formula templates.

    Logic:
    - Exact full match → weight × 1.5 (bonus for perfect structural match)
    - Contiguous sub-match → weight × (template_len / word_len)
    - UNK signs reduce score proportionally
    - Returns best (highest) score across all templates
    """
    seq = word_classes(word)
    n = len(seq)
    unk = unk_fraction(seq)
    best = 0.0

    for weight, template in FORMULAS:
        t = len(template)

        if t > n:
            # Template longer than word — partial prefix match only
            if seq == template[:n]:
                s = weight * (n / t) * (1 - unk)
                if s > best:
                    best = s
            continue

        if n == t:
            # Exact length — check exact match (with bonus)
            if seq == template:
                s = weight * 1.5 * (1 - unk)
                if s > best:
                    best = s
                continue

        # Sliding window contiguous sub-match
        for start in range(n - t + 1):
            if seq[start:start + t] == template:
                coverage = t / n
                s = weight * coverage * (1 - unk)
                if s > best:
                    best = s

    return best

def total_score(word_list):
    """Sum grammar scores across all word groups."""
    return sum(score_word(w) for w in word_list)

# ---------------------------------------------------------------------------
# 5. Frequency-preserving shuffle null
#    Shuffles all 241 tokens, repacks into same word-group lengths.
#    Preserves: exact sign frequency, exact word-group length distribution.
# ---------------------------------------------------------------------------
_ALL_TOKENS = [s for w in SIDE_A_EVANS + SIDE_B_EVANS for s in w]
_WORD_LENS  = [len(w) for w in SIDE_A_EVANS + SIDE_B_EVANS]

def shuffle_null():
    """One shuffle-null trial: same tokens, same word lengths, random order."""
    tokens = _ALL_TOKENS[:]
    random.shuffle(tokens)
    result = []
    idx = 0
    for ln in _WORD_LENS:
        result.append(tokens[idx:idx + ln])
        idx += ln
    return result

# ---------------------------------------------------------------------------
# 6. Disc canonical score (module-level, usable by importers)
# ---------------------------------------------------------------------------
ALL_WORDS  = SIDE_A_EVANS + SIDE_B_EVANS
DISC_SCORE = total_score(ALL_WORDS)

# ---------------------------------------------------------------------------
# 7. Standalone output (only when run directly, not when imported)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    SEP = "=" * 70

    print(SEP)
    print("LUWIAN FORMULA PARSER — PHAISTOS DISC (CANONICAL EVANS DATA)")
    print("Grammar-aware scoring | Frequency-preserving null | N=100,000")
    print(SEP)
    print()

    print("G_LUWIAN KEY (Evans canonical numbering):")
    print(f"  {'Sign':>4}  {'Name':<20}  {'Syllable':<8}  {'Class':<8}  Confidence")
    print(f"  {'-'*4}  {'-'*20}  {'-'*8}  {'-'*8}  {'-'*10}")
    for s in sorted(G_LUWIAN_KEY):
        syl, conf = G_LUWIAN_KEY[s]
        cls = SYLLABLE_CLASS.get(syl, "UNK")
        name = SIGN_NAMES[s]
        print(f"  #{s:02d}   {name:<20}  {syl:<8}  {cls:<8}  {conf}")
    assigned = len(G_LUWIAN_KEY)
    print(f"  ({assigned} of 45 Evans signs assigned; {45-assigned} = UNK)")
    print()

    print("FORMULA TEMPLATES (Luwian ritual patterns):")
    for w, tmpl in FORMULAS:
        print(f"  w={w}  {' + '.join(tmpl)}")
    print()

    print(SEP)
    print(f"{'Word':<6}  {'Signs':>5}  {'Reading':<30}  {'Classes':<30}  Score")
    print("-" * 90)
    for i, word in enumerate(ALL_WORDS):
        side  = "A" if i < 31 else "B"
        num   = (i + 1) if i < 31 else (i - 30)
        label = f"{side}{num:02d}"
        seq   = word_classes(word)
        sc    = score_word(word)
        reading  = " ".join(sign_syllable(s) for s in word)
        cls_str  = "→".join(seq)
        print(f"  {label}  {str(word):<35}  {reading:<20}  {cls_str:<30}  {sc:.2f}")

    print("-" * 90)
    print(f"  {'TOTAL DISC GRAMMAR SCORE':<65}  {DISC_SCORE:.4f}")
    print()

    # Monte Carlo
    N_SIM    = 100_000
    null_sc  = []
    n_exceed = 0

    print(SEP)
    print(f"MONTE CARLO — FREQUENCY-PRESERVING NULL (N={N_SIM:,})")
    print(SEP)
    print()
    print("Running simulations ...")
    for i in range(N_SIM):
        s = total_score(shuffle_null())
        null_sc.append(s)
        if s >= DISC_SCORE:
            n_exceed += 1
        if (i + 1) % 25_000 == 0:
            print(f"  ... {i+1:,} / {N_SIM:,}")

    mean_n = sum(null_sc) / N_SIM
    var_n  = sum((x - mean_n) ** 2 for x in null_sc) / N_SIM
    std_n  = math.sqrt(var_n) if var_n > 0 else 1e-9
    z      = (DISC_SCORE - mean_n) / std_n
    p_val  = n_exceed / N_SIM

    print()
    print(SEP)
    print("RESULTS")
    print(SEP)
    print()
    print(f"  Disc grammar score   : {DISC_SCORE:.4f}")
    print(f"  Null mean ± SD       : {mean_n:.4f} ± {std_n:.4f}")
    print(f"  Z-score              : {z:+.2f}")
    print(f"  p (one-tailed)       : {p_val:.6f}  ({n_exceed}/{N_SIM} exceed)")
    if p_val == 0.0:
        print(f"  Upper bound          : p < {1/N_SIM:.2e}")
    print()

    print(SEP)
    print("TOP FORMULA-MATCHING WORD GROUPS")
    print(SEP)
    print()
    scored_words = []
    for i, word in enumerate(ALL_WORDS):
        side  = "A" if i < 31 else "B"
        num   = (i + 1) if i < 31 else (i - 30)
        label = f"{side}{num:02d}"
        sc    = score_word(word)
        reading = " ".join(sign_syllable(s) for s in word)
        seq     = word_classes(word)
        scored_words.append((sc, label, word, reading, "→".join(seq)))

    scored_words.sort(key=lambda x: -x[0])
    for sc, label, word, reading, cls_str in scored_words[:15]:
        print(f"  {label}  {reading:<30}  [{cls_str}]  score={sc:.2f}")

    print()
    print(SEP)
    print("ASSIGNMENT COVERAGE SUMMARY")
    print(SEP)
    print()
    total_tokens    = sum(len(w) for w in ALL_WORDS)
    assigned_tokens = sum(1 for w in ALL_WORDS for s in w if s in G_LUWIAN_KEY)
    print(f"  Total tokens      : {total_tokens}")
    print(f"  Assigned tokens   : {assigned_tokens}  ({100*assigned_tokens/total_tokens:.1f}%)")
    print(f"  UNK tokens        : {total_tokens - assigned_tokens}  ({100*(total_tokens-assigned_tokens)/total_tokens:.1f}%)")
    print()
    print("  GRAMMAR SCORES FOR THE 7 REPEATED WORD GROUPS:")
    repeated_groups = {
        "A16/A19/A22": [2, 12, 31, 26],
        "A14/A20":     [2, 27, 25, 10, 23, 18],
        "A15/A21":     [28, 1],
        "A17/A29":     [2, 12, 27, 27, 35, 37, 21],
        "A28/A31":     [10, 3, 38],
        "B21/B26":     [22, 29, 36, 7, 8],
        "A03/B20":     [29, 45, 7],
    }
    for label, word in repeated_groups.items():
        sc      = score_word(word)
        reading = " ".join(sign_syllable(s) for s in word)
        seq     = word_classes(word)
        print(f"  {label:<14}  {reading:<30}  [{' '.join(seq)}]  score={sc:.2f}")

    print()
    print(SEP)
    print("INTERPRETATION")
    print(SEP)
    print()
    if z > 3:
        print(f"  SIGNIFICANT: Z={z:+.2f}, p={p_val:.6f}")
        print()
        print("  The disc's word groups match Luwian grammatical formula templates")
        print("  significantly more often than frequency-preserving random shuffles.")
        print("  This is KEY-DEPENDENT: supports (does not prove) G_LUWIAN hypothesis.")
    elif z > 2:
        print(f"  MARGINAL: Z={z:+.2f}, p={p_val:.6f}")
    else:
        print(f"  NOT SIGNIFICANT: Z={z:+.2f}, p={p_val:.6f}")
    print()
    print(f"  Token coverage: {100*assigned_tokens/total_tokens:.1f}% assigned, "
          f"{100*(total_tokens-assigned_tokens)/total_tokens:.1f}% UNK.")
    print(SEP)
