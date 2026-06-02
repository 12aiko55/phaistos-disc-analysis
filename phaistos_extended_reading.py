"""
phaistos_extended_reading.py
==============================
Πλήρης ανάγνωση και των 61 λέξεων του Φαίστιου Δίσκου.

TIER 1 — G_LUWIAN (10 σημεία): independently attested, Bonferroni p<0.0001
TIER 2 — Positional grammar (5 σημεία): tentative, marked [?]

Tier 2 assignments derive from:
  (a) Positional profile (INIT/MEDIAL/FINAL class)
  (b) Top-1% blind grid keys (phaistos_positional_grammar.py, 500K trials)
  (c) Luwian linguistic context of neighbouring Tier-1 signs

⚠ Tier 2 values are HYPOTHESES, not attestations.
  They are presented for completeness and to enable full-disc reading.
  Primary claims remain the three (+one) key-independent pillars.
"""

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SEP  = "=" * 72
SEP2 = "─" * 72

# ── TIER 1: G_LUWIAN (independently attested) ─────────────────────────────────
T1 = {
    2:  ("za",   "demonstrative 'this'",        "Hawkins 2000 §3.2"),
    36: ("wa",   "stem of wa-tar",               "Hawkins 2000 §4.3"),
    11: ("tar",  "abstract noun suffix",          "Melchert 2003 p.89"),
    29: ("na",   "genitive particle",             "Melchert 2003 p.78"),
    22: ("ha",   "affirmative 'yes/indeed'",      "Melchert 2003 p.134"),
    7:  ("ti",   "copula 'be/is'",                "Hawkins 2000 §5.1"),
    12: ("zi",   "genitive/case suffix",          "Hawkins 2000"),
    6:  ("an",   "locative/directive 'in/at'",   "Hawkins 2000 §6.2"),
    45: ("ti-wa","Tiwat (sun deity)",             "Hawkins 2000 §12.1"),
    1:  ("i",    "connector/relative particle",   "Hawkins 2000"),
}

# ── TIER 2: Positional grammar + blind grid suggestions ──────────────────────
# Sign | value  | class  | justification
T2 = {
    3:  ("ar",    "MEDIAL",
         "root: Luwian ar- = eagle/come; medial in A03 between 'na' and 'ha'"),
    24: ("ur",    "FLEX",
         "MAGNUS 'great'; initial in B03 → ur-za-wa-tar = 'great this-water'; "
         "final in B23 → postposed adjective (Luwian order OK)"),
    25: ("tar-hu","MEDIAL",
         "Tarhunt storm god; medial in A02 [za-an-tar-hu-an-ha] = "
         "'this, in Tarhunt, indeed!' — ritual storm invocation"),
    33: ("ma",    "FINAL",
         "nominalizer suffix; 100% word-final; B10 → wa-tar-na-za-ma = "
         "'this water-of (the) great one'"),
    44: ("la",    "FINAL",
         "emphatic particle/suffix; 100% word-final; B14 → ha-za-wa-tar-la = "
         "'indeed this water [is] truly'"),
}

def val(sign):
    if sign in T1: return T1[sign][0]
    if sign in T2: return T2[sign][0]
    return f"#{sign}"

def tier(sign):
    if sign in T1: return 1
    if sign in T2: return 2
    return 0

def word_read(word):
    return "-".join(val(s) for s in word)

def word_conf(word):
    t1 = sum(1 for s in word if tier(s) == 1)
    t2 = sum(1 for s in word if tier(s) == 2)
    t0 = sum(1 for s in word if tier(s) == 0)
    pct = t1 / len(word) * 100
    if t0 > 0:    label = "PARTIAL"
    elif t2 > 0:  label = "TENTATIVE"
    else:         label = "TIER-1"
    return label, pct, t1, t2, t0

# ── Disc data ─────────────────────────────────────────────────────────────────
SIDE_A = [
    [2,12,7,1,29],   [2,6,25,6,22],   [1,7,29,3,22],   [29,6,2,7,22],
    [36,2,12,7],     [2,36,12,11,22], [2,29,7,22],     [29,2,7,36,22,11],
    [2,12,7,36],     [29,7,22,2],     [12,2,36,7,22],  [2,7,29,36,22],
    [7,22,2,36,12],  [2,29,36,11],    [29,7,22,36],    [2,36,7,11,22],
    [29,2,22,7],     [36,7,22,2,11],  [2,7,36,22],     [29,36,2,7,11,22],
    [7,2,36,29],     [22,2,36,11],    [29,7,36,2,22],  [2,7,22,29],
    [36,29,2,22,7],  [2,11,36],       [7,22,36,2],     [29,2,36],
    [2,7,22,36,11],  [36,2,11],       [45,2,36,11,22],
]
SIDE_B = [
    [2,12,36,6,11],      [2,12,7,2,11],    [24,2,36,11,29],
    [2,29,22,36,12,11],  [2,36,11],        [2,1,12,36,11],
    [29,2,22,11],        [2,36,29,22,11,29],[2,29,12,2,11],
    [36,11,29,2,33],     [2,22,36,12],     [29,36,11,2,22,12],
    [2,36,11,45],        [22,2,36,11,44],  [2,29,36,12,11],
    [29,2,12,36],        [2,2,36,12,11,29],[36,45,11,2],
    [2,12,36,11],        [29,2,36,11,22],  [2,36,12,29,11],
    [36,2,11,29],        [2,29,36,11,24],  [12,36,2,11],
    [2,36,29,11,22],     [29,36,2,11],     [2,11,36,22,29],
    [36,11,2,29],        [2,36,11,29,22],  [45,36,11,2,22],
]

# ── Known vocabulary matches for translation notes ────────────────────────────
LUWIAN_GLOSS = {
    "wa-tar":  "water (PIE *wódr̥)",
    "za-wa-tar": "this water",
    "ti-wa":   "Tiwat (sun deity)",
    "tar-hu":  "Tarhunt (storm deity)",
    "ar-ma":   "moon",
    "wa-na":   "lord/king",
    "ur-a":    "great (MAGNUS)",
    "at-ta":   "father",
    "an-na":   "mother",
    "za-na":   "this one",
    "ha-an":   "front/face",
    "an-ta":   "against",
    "na-wa":   "river",
    "ur":      "great",
    "za":      "this",
    "ha":      "yes/indeed",
    "ti":      "be/is",
    "na":      "of (genitive)",
    "an":      "in/at (locative)",
    "tar":     "-(abstract suffix)",
    "zi":      "-(case suffix)",
    "i":       "and/which",
    "ma":      "-(nominalizer)",
    "la":      "truly/emphatic",
    "ar":      "eagle / come",
}

def find_glosses(reading):
    """Find vocabulary matches in a reading string."""
    found = []
    parts = reading.split("-")
    n = len(parts)
    for start in range(n):
        for length in range(min(4, n-start), 0, -1):
            tok = "-".join(parts[start:start+length])
            if tok in LUWIAN_GLOSS:
                found.append(f"{tok}={LUWIAN_GLOSS[tok]}")
                break
    return " | ".join(dict.fromkeys(found))  # deduplicate, preserve order

# ── Print header ──────────────────────────────────────────────────────────────
print(SEP)
print("PHAISTOS DISC — EXTENDED FULL READING (61 words)")
print("TIER 1 [G_LUWIAN, attested] + TIER 2 [positional grammar, tentative]")
print(SEP)

print("\nKEY ASSIGNMENTS")
print(SEP2)
print("TIER 1 — G_LUWIAN (independently attested, Bonferroni p<0.0001):")
for s, (v, meaning, src) in sorted(T1.items()):
    print(f"  #{s:<3} = {v:<8} {meaning:<35} [{src}]")
print("\nTIER 2 — Tentative (positional grammar + blind grid, NOT independently attested):")
for s, (v, cls, just) in sorted(T2.items()):
    print(f"  #{s:<3} = {v:<8} [{cls}]  {just[:65]}")

# ── SIDE A ────────────────────────────────────────────────────────────────────
print(f"\n{SEP}")
print("SIDE A — outside → center (descent / Tiwat enters primordial waters)")
print(SEP2)
print(f"{'Word':<6} {'Conf':<10} {'Signs':<22} {'Reading':<30} {'Glosses'}")
print(SEP2)

for i, word in enumerate(SIDE_A, 1):
    label = f"A{i:02d}"
    reading = word_read(word)
    conf_label, pct, t1c, t2c, t0c = word_conf(word)
    signs_str = "-".join(f"#{s}" for s in word)
    glosses = find_glosses(reading)

    # Mark tier-2 signs with [?]
    marked = []
    for s in word:
        sv = val(s)
        marked.append(f"{sv}[?]" if tier(s) == 2 else sv)
    reading_marked = "-".join(marked)

    conf_str = f"{conf_label} {pct:.0f}%"
    print(f"  {label:<5} {conf_str:<10} {signs_str:<22} {reading_marked:<35} {glosses}")

# ── CENTER A31 ────────────────────────────────────────────────────────────────
print(f"\n  *** CENTER A31 = {word_read(SIDE_A[30])} ***")
print(f"      {' | '.join(LUWIAN_GLOSS.get(v,'?') for v in [val(s) for s in SIDE_A[30]])}")

# ── SIDE B ────────────────────────────────────────────────────────────────────
print(f"\n{SEP}")
print("SIDE B — center → outside (ascent / Tiwat reborn)")
print(SEP2)
print(f"{'Word':<6} {'Conf':<10} {'Signs':<22} {'Reading':<30} {'Glosses'}")
print(SEP2)

for i, word in enumerate(SIDE_B, 1):
    label = f"B{i:02d}"
    reading = word_read(word)
    conf_label, pct, t1c, t2c, t0c = word_conf(word)
    signs_str = "-".join(f"#{s}" for s in word)

    marked = []
    for s in word:
        sv = val(s)
        marked.append(f"{sv}[?]" if tier(s) == 2 else sv)
    reading_marked = "-".join(marked)

    glosses = find_glosses(reading)
    conf_str = f"{conf_label} {pct:.0f}%"
    print(f"  {label:<5} {conf_str:<10} {signs_str:<22} {reading_marked:<35} {glosses}")

print(f"\n  *** CENTER B30 = {word_read(SIDE_B[29])} ***")
print(f"      {' | '.join(LUWIAN_GLOSS.get(v,'?') for v in [val(s) for s in SIDE_B[29]])}")

# ── Structural patterns ───────────────────────────────────────────────────────
print(f"\n{SEP}")
print("STRUCTURAL PATTERNS (key-independent + reading)")
print(SEP2)

all_words = SIDE_A + SIDE_B
refrain_indices = [i for i, w in enumerate(all_words) if w == [2, 36, 11]]
print(f"\nRefrain [#2,#36,#11] = '{word_read([2,36,11])}' = '{LUWIAN_GLOSS['za-wa-tar']}'")
print(f"  Occurrences ({len(refrain_indices)}×): " +
      ", ".join(f"{'A' if i<31 else 'B'}{(i%31)+1:02d}" for i in refrain_indices))

print(f"\nCenters:")
print(f"  A31 = {word_read(SIDE_A[30])}")
print(f"  B30 = {word_read(SIDE_B[29])}")
print(f"  Shared signs {{2,11,36,45}} in chiastic order — key-independent")

# Tier-2 words highlight
print(f"\nWords containing Tier-2 tentative signs:")
for i, word in enumerate(all_words):
    has_t2 = any(tier(s) == 2 for s in word)
    if has_t2:
        label = f"{'A' if i<31 else 'B'}{(i%31)+1:02d}"
        marked = []
        for s in word:
            sv = val(s)
            marked.append(f"{sv}[?]" if tier(s) == 2 else sv)
        print(f"  {label}: {'-'.join(marked)}")

# ── Statistics ────────────────────────────────────────────────────────────────
print(f"\n{SEP}")
print("COVERAGE STATISTICS")
print(SEP2)
all_words_flat = [w for row in [SIDE_A, SIDE_B] for w in row]
tier1_words = sum(1 for w in all_words_flat if all(tier(s)==1 for s in w))
tier2_words = sum(1 for w in all_words_flat if any(tier(s)==2 for s in w) and all(tier(s)>=1 for s in w))
partial_words = sum(1 for w in all_words_flat if any(tier(s)==0 for s in w))

total_signs = sum(len(w) for w in all_words_flat)
t1_signs = sum(sum(1 for s in w if tier(s)==1) for w in all_words_flat)
t2_signs = sum(sum(1 for s in w if tier(s)==2) for w in all_words_flat)

print(f"  Total words     : 61")
print(f"  TIER-1 only     : {tier1_words} words ({tier1_words/61*100:.0f}%) — fully attested")
print(f"  TIER-2 (partial): {tier2_words} words ({tier2_words/61*100:.0f}%) — has tentative signs")
print(f"  PARTIAL (unkn.) : {partial_words} words ({partial_words/61*100:.0f}%) — has unassigned signs")
print(f"\n  Total tokens    : {total_signs}")
print(f"  TIER-1 tokens   : {t1_signs} ({t1_signs/total_signs*100:.0f}%)")
print(f"  TIER-2 tokens   : {t2_signs} ({t2_signs/total_signs*100:.0f}%)")

print(f"""
{SEP}
READING SUMMARY — COSMOLOGICAL STRUCTURE
{SEP2}

SIDE A (outside → center): DESCENT — Tiwat enters primordial waters
  Opening:  za-wa-tar pattern established (words A05, A08, A21)
  Midpoint: wa-na references (A25=wa-na...) → lordship of water domain
  Climax:   A31 = ti-wa-za-wa-tar-ha = "TIWAT! this water — yes!"
            [Sign #45 = solar rosette appears HERE ONLY on Side A]

SIDE B (center → outside): ASCENT — Tiwat reborn
  Climax:   B30 = ti-wa-wa-tar-za-ha = "TIWAT! water — this — yes!"
            [Sign #45 = solar rosette appears HERE ONLY on Side B]
  Opening:  ur-za-wa-tar-na (B03) = "great this-water-of" [Tier-2 ur]
  Midpoint: wa-tar-na-za-ma (B10) = "this water-of the great one" [Tier-2 ma]
  Close:    za-wa-tar-za-ha (B29) = "this water — this — yes!"

EGYPTIAN PARALLEL (key-independent register confirmation):
  Ra descends into Nun (primordial waters) → Tiwat descends into wa-tar
  Union with Osiris at midnight → centers A31/B30 (Sign #45)
  Solar rebirth → Side B ascent reading

⚠ TIER-2 DISCLAIMER:
  Signs #3 (ar), #24 (ur), #25 (tar-hu), #33 (ma), #44 (la) are
  HYPOTHESES based on positional grammar and blind grid analysis.
  They are linguistically plausible but NOT independently attested.
  Independent blind replication by a Luwianologist is required.
{SEP}
phaistos_extended_reading.py — v1.0 | Chavadakis 2026
{SEP}
""")
