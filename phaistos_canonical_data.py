"""
phaistos_canonical_data.py
==========================
CANONICAL Phaistos Disc data using Evans/Godart numbering (01-45).

Sources:
  - Evans, A. (1909). Scripta Minoa I. Oxford.
  - Godart, L. (1995). Le Disque de Phaistos. Heraklion.
  - Wikipedia: Phaistos Disc (sign catalog, frequencies verified)
  - Omniglot: https://www.omniglot.com/writing/phaistos.htm

VALIDATION STATUS:
  words_total    : 61  (31 Side A + 30 Side B) -- CONFIRMED
  tokens_total   : 241                          -- CONFIRMED (Evans canonical)
  distinct_signs : 45                           -- CONFIRMED

WHAT WAS WRONG IN OLD DATA:
  - phaistos_dualpass_v2.py used DISC_FREQ with 175 tokens (not 241)
  - DISC_FREQ had 49 sign types (not 45) with wrong numbering
  - SIDE_A/SIDE_B arrays had only 15 of 45 sign types
  - Missing entirely: Evans #12 (SHIELD, 17x), #27 (HIDE, 15x), #18 (BOOMERANG, 12x)
  - SIDE_A+B token count: 281 (inflated by fabricated word groups)

MAPPING FROM OLD CUSTOM NUMBERING -> EVANS:
  Old sign 11 (19x, 'tar') = Evans 02 (PLUMED HEAD, 19x)  -- CONFIRMED
  Old sign 36 (18x, 'wa')  = Evans 07 (HELMET, 18x)       -- CONFIRMED
  Old sign 2  (11x, 'za')  = Evans ?? (11x) -- UNCONFIRMED
                              Candidates: Evans 01 (PEDESTRIAN), 23 (COLUMN),
                                          29 (CAT), 35 (PLANE TREE)
  NOTE: The za-wa-tar trigram count (x8) must be RE-VERIFIED in canonical data.
"""

# ---------------------------------------------------------------------------
# 1. Sign catalog: Evans numbers 01-45, names, frequencies
#    Source: Wikipedia Phaistos Disc article (verified total = 241)
# ---------------------------------------------------------------------------
SIGN_NAMES = {
     1: "PEDESTRIAN",       2: "PLUMED HEAD",      3: "TATTOOED HEAD",
     4: "CAPTIVE",          5: "CHILD",             6: "WOMAN",
     7: "HELMET",           8: "GAUNTLET",          9: "TIARA",
    10: "ARROW",           11: "BOW",              12: "SHIELD",
    13: "CLUB",            14: "MANACLES",         15: "MATTOCK",
    16: "SAW",             17: "LID",              18: "BOOMERANG",
    19: "CARPENTRY PLANE", 20: "DOLIUM",           21: "COMB",
    22: "SLING",           23: "COLUMN",           24: "BEEHIVE",
    25: "SHIP",            26: "HORN",             27: "HIDE",
    28: "BULL'S LEG",      29: "CAT",              30: "RAM",
    31: "EAGLE",           32: "DOVE",             33: "TUNNY",
    34: "BEE",             35: "PLANE TREE",       36: "VINE",
    37: "PAPYRUS",         38: "ROSETTE",          39: "LILY",
    40: "OX BACK",         41: "FLUTE",            42: "GRATER",
    43: "STRAINER",        44: "SMALL AXE",        45: "WAVY BAND",
}

# Frequencies (Side A count, Side B count, total)
# Source: Wikipedia — verified sum = 241
SIGN_FREQ_A = {
     1: 6,   2:14,   3: 2,   4: 1,   5: 0,   6: 2,   7: 3,   8: 1,   9: 0,
    10: 4,  11: 1,  12:15,  13: 3,  14: 1,  15: 0,  16: 0,  17: 1,  18: 6,
    19: 3,  20: 0,  21: 2,  22: 0,  23: 5,  24: 1,  25: 2,  26: 5,  27:10,
    28: 2,  29: 3,  30: 0,  31: 5,  32: 2,  33: 2,  34: 1,  35: 5,  36: 0,
    37: 2,  38: 3,  39: 1,  40: 3,  41: 2,  42: 0,  43: 0,  44: 1,  45: 2,
}
SIGN_FREQ_B = {
     1: 5,   2: 5,   3: 0,   4: 0,   5: 1,   6: 2,   7:15,   8: 4,   9: 2,
    10: 0,  11: 0,  12: 2,  13: 3,  14: 1,  15: 1,  16: 2,  17: 0,  18: 6,
    19: 0,  20: 2,  21: 0,  22: 5,  23: 6,  24: 5,  25: 5,  26: 1,  27: 5,
    28: 0,  29: 8,  30: 1,  31: 0,  32: 1,  33: 4,  34: 2,  35: 6,  36: 4,
    37: 2,  38: 1,  39: 3,  40: 3,  41: 0,  42: 1,  43: 1,  44: 0,  45: 4,
}
SIGN_FREQ = {s: SIGN_FREQ_A[s] + SIGN_FREQ_B[s] for s in SIGN_NAMES}

# Verify
assert sum(SIGN_FREQ.values()) == 241, f"FATAL: total = {sum(SIGN_FREQ.values())}, expected 241"
assert len(SIGN_FREQ) == 45, f"FATAL: {len(SIGN_FREQ)} distinct signs, expected 45"

# ---------------------------------------------------------------------------
# 2. Sorted frequency ranking
# ---------------------------------------------------------------------------
FREQ_RANKED = sorted(SIGN_FREQ.items(), key=lambda x: -x[1])

# ---------------------------------------------------------------------------
# 3. Mapping from old custom sign numbers to Evans numbers
#    Status: only the top 2 are confirmed. Others are UNCONFIRMED hypotheses.
# ---------------------------------------------------------------------------
# Custom -> Evans (CONFIRMED only where frequency is unambiguous)
OLD_TO_EVANS = {
    11: 2,   # 19x -> Evans 02 PLUMED HEAD  (CONFIRMED, unique frequency)
    36: 7,   # 18x -> Evans 07 HELMET       (CONFIRMED, unique frequency)
    # All others UNCONFIRMED — 4 signs tie at 11x, multiple ties at lower freqs
}
EVANS_TO_OLD = {v: k for k, v in OLD_TO_EVANS.items()}

# ---------------------------------------------------------------------------
# 4. Word group sequences (Evans numbering)
#    STATUS: *** NEEDS VERIFICATION against Godart 1995 ***
#    The sequences below are from Wikipedia/public sources.
#    Token count must be validated against SIGN_FREQ before use.
#
#    CRITICAL: za-wa-tar refrain count (x8 in old data) must be re-verified
#    using the CORRECT Evans-numbered sequences below.
# ---------------------------------------------------------------------------

# Side A: 31 word groups (A01-A31), outside -> center
# Each list = Evans sign numbers in sequence order
SIDE_A_EVANS = [
    # A01-A10
    [2, 12, 13, 1, 18],      # A01
    [24, 40, 12],             # A02
    [29, 45, 7],              # A03
    [29, 29, 34],             # A04
    [2, 12, 4, 40, 33],       # A05
    [27, 45, 7, 12],          # A06
    [27, 44, 8],              # A07
    [2, 12, 6, 18, 27],       # A08  (note: sign 27 uncertain here)
    [31, 26, 35],             # A09
    [2, 12, 41, 19, 35],      # A10
    # A11-A20
    [1, 41, 40, 7],           # A11
    [2, 12, 32, 23, 38],      # A12
    [39, 11],                 # A13
    [2, 27, 25, 10, 23, 18],  # A14
    [28, 1],                  # A15
    [2, 12, 31, 26],          # A16
    [2, 12, 27, 27, 35, 37, 21],  # A17
    [33, 23],                 # A18
    [2, 12, 31, 26],          # A19  (repeated pattern)
    [2, 27, 25, 10, 23, 18],  # A20  (repeated pattern)
    # A21-A31
    [28, 1],                  # A21  (repeated pattern)
    [2, 12, 31, 26],          # A22  (repeated pattern)
    [2, 12, 27, 14, 32, 18, 27],  # A23
    [6, 18, 17, 19],          # A24
    [31, 26, 12],             # A25
    [2, 12, 13, 1],           # A26
    [23, 19, 35],             # A27
    [10, 3, 38],              # A28
    [2, 12, 27, 27, 35, 37, 21],  # A29  (repeated pattern)
    [13, 1],                  # A30
    [10, 3, 38],              # A31  *** SPIRAL CENTER Side A ***
]

# Side B: 30 word groups (B01-B30), outside -> center
SIDE_B_EVANS = [
    # B01-B10
    [2, 12, 22, 40, 7],       # B01
    [27, 45, 7, 35],          # B02
    [2, 37, 23, 5],           # B03
    [22, 25, 27],             # B04
    [33, 24, 20, 12],         # B05
    [16, 23, 18, 43],         # B06
    [13, 1, 39, 33],          # B07
    [15, 7, 13, 1, 18],       # B08
    [22, 37, 42, 25],         # B09
    [7, 24, 40, 35],          # B10
    # B11-B20
    [2, 26, 36, 40],          # B11
    [27, 25, 38, 1],          # B12
    [29, 24, 24, 20, 35],     # B13
    [16, 14, 18],             # B14
    [29, 33, 1],              # B15
    [6, 35, 32, 39, 33],      # B16
    [2, 9, 27, 1],            # B17
    [29, 36, 7, 8],           # B18
    [29, 8, 13],              # B19
    [29, 45, 7],              # B20  (same as A03)
    # B21-B30
    [22, 29, 36, 7, 8],       # B21
    [27, 34, 23, 25],         # B22
    [7, 18, 35],              # B23
    [7, 45, 7],               # B24
    [7, 23, 18, 24],          # B25
    [22, 29, 36, 7, 8],       # B26  (same as B21)
    [9, 30, 39, 18, 7],       # B27
    [2, 6, 35, 23, 7],        # B28
    [29, 34, 23, 25],         # B29  (same as B22)
    [45, 7],                  # B30  *** SPIRAL CENTER Side B ***
]

# ---------------------------------------------------------------------------
# 5. Validation of word group data
# ---------------------------------------------------------------------------
def validate_word_groups():
    all_words = SIDE_A_EVANS + SIDE_B_EVANS
    all_tokens = [s for w in all_words for s in w]
    from collections import Counter
    seq_counts = Counter(all_tokens)
    errors = []

    if len(SIDE_A_EVANS) != 31:
        errors.append(f"Side A: {len(SIDE_A_EVANS)} groups, expected 31")
    if len(SIDE_B_EVANS) != 30:
        errors.append(f"Side B: {len(SIDE_B_EVANS)} groups, expected 30")

    # Check token counts vs canonical SIGN_FREQ
    for sign in set(list(seq_counts.keys()) + list(SIGN_FREQ.keys())):
        seq_c = seq_counts.get(sign, 0)
        canon_c = SIGN_FREQ.get(sign, 0)
        if seq_c != canon_c:
            name = SIGN_NAMES.get(sign, f"#{sign}")
            errors.append(f"Sign {sign:2d} ({name}): word_groups={seq_c}, SIGN_FREQ={canon_c}, diff={seq_c-canon_c:+d}")

    return errors

# ---------------------------------------------------------------------------
# 6. Quick trigram counter (for za-wa-tar style searches)
# ---------------------------------------------------------------------------
def count_trigram_in_words(word_list, trigram):
    """Count consecutive trigram occurrences within word boundaries."""
    count = 0
    for word in word_list:
        for i in range(len(word) - 2):
            if word[i] == trigram[0] and word[i+1] == trigram[1] and word[i+2] == trigram[2]:
                count += 1
    return count

def count_trigram_flat(word_list, trigram):
    """Count consecutive trigram in flat sequence (crosses word boundaries)."""
    flat = [s for w in word_list for s in w]
    count = 0
    for i in range(len(flat) - 2):
        if flat[i] == trigram[0] and flat[i+1] == trigram[1] and flat[i+2] == trigram[2]:
            count += 1
    return count

# ---------------------------------------------------------------------------
# If run directly: print validation report
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 65)
    print("PHAISTOS DISC — CANONICAL DATA VALIDATION")
    print("=" * 65)
    print()
    print(f"Sign types   : {len(SIGN_FREQ)} (expected 45)")
    print(f"Total tokens : {sum(SIGN_FREQ.values())} (expected 241)")
    print(f"Word groups  : {len(SIDE_A_EVANS)+len(SIDE_B_EVANS)} = {len(SIDE_A_EVANS)}A + {len(SIDE_B_EVANS)}B (expected 61 = 31+30)")
    all_tokens = [s for w in SIDE_A_EVANS+SIDE_B_EVANS for s in w]
    print(f"Tokens in word groups: {len(all_tokens)}")
    print()

    print("--- Top 10 signs by frequency ---")
    for rank, (sign, freq) in enumerate(FREQ_RANKED[:10], 1):
        name = SIGN_NAMES[sign]
        print(f"  {rank:2d}. Evans #{sign:2d} ({name:20s}) : {freq}x")

    print()
    print("--- Word group validation (vs SIGN_FREQ) ---")
    errors = validate_word_groups()
    if not errors:
        print("  ALL MATCH -- word groups are consistent with SIGN_FREQ")
    else:
        print(f"  {len(errors)} discrepancies found:")
        for e in errors[:20]:
            print(f"  ! {e}")

    print()
    print("--- Searching for high-frequency trigrams ---")
    from collections import Counter
    all_words = SIDE_A_EVANS + SIDE_B_EVANS
    trigram_counts = Counter()
    for word in all_words:
        for i in range(len(word) - 2):
            t = tuple(word[i:i+3])
            trigram_counts[t] += 1
    print("  Top trigrams (within word boundaries):")
    for trig, cnt in trigram_counts.most_common(10):
        names = [SIGN_NAMES.get(s, f"#{s}") for s in trig]
        print(f"  {cnt}x  {trig}  [{' + '.join(names)}]")

    print()
    print("--- Old za-wa-tar mapping ---")
    print("  Old custom [2,36,11] (za-wa-tar):")
    print("  Evans equiv = [?,7,2] (UNKNOWN + HELMET + PLUMED HEAD)")
    print("  Searching all Evans [?,07,02] trigrams in canonical data:")
    for lead_sign in [1, 23, 29, 35]:
        trigram = (lead_sign, 7, 2)
        cnt_words = count_trigram_in_words(all_words, trigram)
        cnt_flat  = count_trigram_flat(all_words, trigram)
        name = SIGN_NAMES[lead_sign]
        print(f"  [{lead_sign:2d},7,2] ({name}+HELMET+PLUMED HEAD): {cnt_words}x in words, {cnt_flat}x flat")
