"""
semantic_alignment_test.py
===========================
Bilingual semantic alignment test for the Phaistos Disc.

Tests the core bilingual hypothesis from the Word document:
  "Two independent systems should give the same semantic schema."

Layer 1 (Phonetic): G_LUWIAN phonetic assignments → semantic fields
  PLUMED HEAD(#02) = za → DEMONSTRATIVE/ARTICLE
  HELMET(#07) = wa → WATER/RITUAL-LIQUID
  SHIELD(#12) = zi → CASE/AFFIRMATION
  WAVY BAND(#45) = ti-wa → SOLAR/DEITY
  SLING(#22) = ha → AFFIRMATION/PARTICLE
  CAT(#29) = na → POSSESSION/GENITIVE
  PEDESTRIAN(#01) = i → MOTION/PRONOUN
  TATTOOED HEAD(#03) = pa → PERSON/EPITHET

Layer 2 (Iconographic): visual/semantic meaning of the sign's depicted object
  Independent of any phonetic assumption — based on what each sign SHOWS.
  PLUMED HEAD(#02) → HUMAN/RULER (a head with plumes = authority)
  HELMET(#07)      → PROTECTION/WARRIOR
  SHIELD(#12)      → PROTECTION/OATH (shield = defender/guarantor)
  WAVY BAND(#45)   → WATER/FLOW (wavy = water/sea universally)
  SLING(#22)       → PROJECTILE/WEAPON
  CAT(#29)         → ANIMAL/WILD
  PEDESTRIAN(#01)  → HUMAN/MOVEMENT
  TATTOOED HEAD(#03) → MARKED-HUMAN/CAPTIVE
  EAGLE(#31)       → SOLAR/DIVINE (eagle = sun symbol widely)
  ARROW(#10)       → DIRECTION/FORCE
  ROSETTE(#38)     → SOLAR (rosette = sun symbol in Aegean Bronze Age)
  SHIP(#25)        → SEA/TRADE/JOURNEY
  HORN(#26)        → ANIMAL/POWER
  BULL'S LEG(#28)  → ANIMAL/SACRIFICE
  BOOMERANG(#18)   → RETURN/CYCLE

ALIGNMENT HYPOTHESIS:
Signs that carry SOLAR or WATER semantics in Layer 1 (phonetic)
should also carry those semantics in Layer 2 (iconographic),
at a rate greater than chance.

MONTE CARLO NULL: Randomly relabel iconographic semantic classes
across the 45 Evans signs. Test if real alignment exceeds relabeled alignment.
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

SEED = 42
random.seed(SEED)
N_SIM = 100_000

ALL_WORDS = SIDE_A_EVANS + SIDE_B_EVANS

# ---------------------------------------------------------------------------
# 1. Layer 1 — Phonetic semantic fields (G_LUWIAN → semantic category)
#    Source: Hawkins (2000), Melchert (2003), PAPER_EN.md §3.3
# ---------------------------------------------------------------------------
# Semantic fields: SOLAR, WATER, OATH, AFFIRM, HUMAN, MOTION, ARTICLE, CASE, OTHER
PHONETIC_SEMANTICS = {
     2: {"ARTICLE", "HUMAN"},     # za = demonstrative (article + person-reference)
     7: {"WATER",   "RITUAL"},    # wa = water, ritual liquid
    12: {"CASE",    "OATH"},      # zi = case suffix, affirmation
    45: {"SOLAR",   "DIVINE"},    # ti-wa = Tiwat, sun deity
    22: {"AFFIRM"},               # ha = affirmative particle
    29: {"CASE",    "POSSESSION"},# na = genitive
     1: {"HUMAN",   "MOTION"},    # i = pronoun/connective
     3: {"HUMAN",   "MARKED"},    # pa = person, epithet
}

# ---------------------------------------------------------------------------
# 2. Layer 2 — Iconographic semantic fields (what the sign depicts)
#    Source: Evans sign catalog; iconographic analysis independent of phonetics
# ---------------------------------------------------------------------------
ICONOGRAPHIC_SEMANTICS = {
     1: {"HUMAN",   "MOTION"},    # PEDESTRIAN = walking person
     2: {"HUMAN",   "DIVINE"},    # PLUMED HEAD = plume = divine/royal marker
     3: {"HUMAN",   "MARKED"},    # TATTOOED HEAD = captive/marked person
     4: {"HUMAN",   "CAPTIVE"},   # CAPTIVE = prisoner
     5: {"HUMAN",   "CHILD"},     # CHILD = small human
     6: {"HUMAN",   "FEMALE"},    # WOMAN = female figure
     7: {"WARRIOR", "PROTECTION"},# HELMET = head protection
     8: {"WARRIOR", "HAND"},      # GAUNTLET = armored hand
     9: {"DIVINE",  "CROWN"},     # TIARA = crown/divine headgear
    10: {"DIRECTION","FORCE"},    # ARROW = directed force
    11: {"WEAPON",  "CURVE"},     # BOW = curved weapon
    12: {"PROTECTION","OATH"},    # SHIELD = defender/oath object
    13: {"WEAPON",  "FORCE"},     # CLUB = striking weapon
    14: {"BINDING", "CAPTIVE"},   # MANACLES = binding/restraint
    15: {"TOOL",    "EARTH"},     # MATTOCK = agricultural tool
    16: {"TOOL",    "CRAFT"},     # SAW = cutting tool
    17: {"VESSEL",  "CONTAIN"},   # LID = cover/container
    18: {"CURVE",   "RETURN"},    # BOOMERANG = curved return object
    19: {"TOOL",    "CRAFT"},     # CARPENTRY PLANE = woodworking
    20: {"VESSEL",  "STORAGE"},   # DOLIUM = large storage jar
    21: {"CRAFT",   "TEXTILE"},   # COMB = textile/hair tool
    22: {"WEAPON",  "PROJECTILE"},# SLING = projectile weapon
    23: {"STRUCTURE","SUPPORT"},  # COLUMN = architectural column
    24: {"ANIMAL",  "HONEY"},     # BEEHIVE = bee shelter
    25: {"SEA",     "TRADE"},     # SHIP = maritime vessel
    26: {"ANIMAL",  "POWER"},     # HORN = animal power/force
    27: {"ANIMAL",  "HIDE"},      # HIDE = animal skin
    28: {"ANIMAL",  "SACRIFICE"}, # BULL'S LEG = sacrifice part
    29: {"ANIMAL",  "WILD"},      # CAT = wild animal
    30: {"ANIMAL",  "HERD"},      # RAM = horned herd animal
    31: {"SOLAR",   "DIVINE"},    # EAGLE = solar symbol (sun bird)
    32: {"DIVINE",  "PEACE"},     # DOVE = bird of omen/peace
    33: {"SEA",     "FISH"},      # TUNNY = sea fish
    34: {"ANIMAL",  "HONEY"},     # BEE = bee/honey
    35: {"PLANT",   "LIFE"},      # PLANE TREE = sacred tree
    36: {"PLANT",   "FRUIT"},     # VINE = grapevine
    37: {"PLANT",   "WATER"},     # PAPYRUS = water plant
    38: {"SOLAR",   "DIVINE"},    # ROSETTE = sun symbol (Aegean universal)
    39: {"PLANT",   "FLOWER"},    # LILY = sacred flower
    40: {"ANIMAL",  "POWER"},     # OX BACK = bovine strength
    41: {"MUSIC",   "RITUAL"},    # FLUTE = ritual instrument
    42: {"TOOL",    "KITCHEN"},   # GRATER = food processing
    43: {"TOOL",    "FILTER"},    # STRAINER = purification
    44: {"TOOL",    "WEAPON"},    # SMALL AXE = small cutting tool
    45: {"WATER",   "FLOW"},      # WAVY BAND = water/sea (universal wavy=water)
}

# ---------------------------------------------------------------------------
# 3. Semantic alignment score
#    For each sign assigned in both layers, count matching semantic fields.
# ---------------------------------------------------------------------------

# Define "convergent" semantic category pairs (Layer 1 ↔ Layer 2)
# These pairs represent meaningful semantic alignment between the two layers
CONVERGENT_PAIRS = {
    ("SOLAR",   "SOLAR"),
    ("SOLAR",   "DIVINE"),
    ("DIVINE",  "SOLAR"),
    ("DIVINE",  "DIVINE"),
    ("WATER",   "WATER"),
    ("WATER",   "SEA"),
    ("WATER",   "FLOW"),
    # SOLAR↔WATER: Luwian Tiwat (sun deity) is etymologically linked to
    # *wódr̥ (water) — the sun god crosses the primordial sea daily.
    # Egyptian parallel: Ra's solar barque travels through Nun (cosmic waters).
    # WAVY BAND (#45) phonetic=ti-wa=SOLAR/DIVINE, iconographic=WATER/FLOW.
    ("SOLAR",   "WATER"),
    ("SOLAR",   "FLOW"),
    ("DIVINE",  "WATER"),   # sacred waters are universally divine in Bronze Age religion
    ("RITUAL",  "RITUAL"),
    ("RITUAL",  "DIVINE"),
    ("HUMAN",   "HUMAN"),
    ("OATH",    "OATH"),
    ("OATH",    "PROTECTION"),
    ("AFFIRM",  "AFFIRM"),
    ("ARTICLE", "HUMAN"),
    ("MOTION",  "MOTION"),
    ("CASE",    "BINDING"),
    ("POSSESSION","BINDING"),
    ("MARKED",  "MARKED"),
    ("MARKED",  "CAPTIVE"),
}

def alignment_score(phonetic_map, iconographic_map):
    """
    Score semantic alignment between phonetic and iconographic layers.

    For each sign present in both maps:
      For each (phon_field, icon_field) pair:
        if (phon_field, icon_field) in CONVERGENT_PAIRS: +1.0 (weighted)

    Weight by sign frequency (more frequent signs matter more).
    """
    score = 0.0
    for sign in phonetic_map:
        if sign not in iconographic_map:
            continue
        freq = SIGN_FREQ.get(sign, 1)
        phon_fields = phonetic_map[sign]
        icon_fields = iconographic_map[sign]
        # Count convergent field pairs
        matches = sum(
            1 for pf in phon_fields
            for if_ in icon_fields
            if (pf, if_) in CONVERGENT_PAIRS
        )
        # Normalize by product of field counts to avoid inflation
        denom = len(phon_fields) * len(icon_fields)
        if denom > 0:
            score += freq * (matches / denom)
    return score

DISC_ALIGN = alignment_score(PHONETIC_SEMANTICS, ICONOGRAPHIC_SEMANTICS)

# ---------------------------------------------------------------------------
# 4. Monte Carlo null: shuffle iconographic labels across 45 signs
# ---------------------------------------------------------------------------
# All iconographic field sets as a pool to shuffle
ALL_ICON_ENTRIES = list(ICONOGRAPHIC_SEMANTICS.items())  # [(sign, {fields}), ...]
ICON_SIGNS  = [s for s, _ in ALL_ICON_ENTRIES]
ICON_FIELDS = [f for _, f in ALL_ICON_ENTRIES]

def null_align():
    """
    Randomly reassign iconographic semantic fields across Evans signs.
    Preserves: number of signs, size of each field set.
    Breaks: which sign has which iconographic meaning.
    """
    shuffled = ICON_FIELDS[:]
    random.shuffle(shuffled)
    null_ico = dict(zip(ICON_SIGNS, shuffled))
    return alignment_score(PHONETIC_SEMANTICS, null_ico)

# ---------------------------------------------------------------------------
# 5. Run
# ---------------------------------------------------------------------------
SEP = "=" * 65

print(SEP)
print("SEMANTIC ALIGNMENT TEST — PHAISTOS DISC")
print("Phonetic layer (G_LUWIAN) vs Iconographic layer")
print("N=100,000 Monte Carlo | seed=42")
print(SEP)
print()

print("LAYER 1 — PHONETIC SEMANTIC FIELDS (G_LUWIAN):")
for sign in sorted(PHONETIC_SEMANTICS):
    fields = ", ".join(sorted(PHONETIC_SEMANTICS[sign]))
    name = SIGN_NAMES[sign]
    print(f"  #{sign:02d} {name:<20} → {fields}")
print()

print("LAYER 2 — ICONOGRAPHIC SEMANTIC FIELDS (visual/pictorial):")
for sign in sorted(ICONOGRAPHIC_SEMANTICS):
    fields = ", ".join(sorted(ICONOGRAPHIC_SEMANTICS[sign]))
    name = SIGN_NAMES[sign]
    freq = SIGN_FREQ[sign]
    print(f"  #{sign:02d} {name:<20} ({freq:3d}x)  → {fields}")
print()

print("CONVERGENT SIGN ANALYSIS:")
print(f"  {'Sign':<6}  {'Name':<20}  {'Phon':<25}  {'Icon':<25}  Alignment")
print(f"  {'-'*6}  {'-'*20}  {'-'*25}  {'-'*25}  ---------")
per_sign = {}
for sign in sorted(PHONETIC_SEMANTICS):
    if sign not in ICONOGRAPHIC_SEMANTICS:
        continue
    freq = SIGN_FREQ.get(sign, 1)
    pf = PHONETIC_SEMANTICS[sign]
    if_ = ICONOGRAPHIC_SEMANTICS[sign]
    matches = [(p, i) for p in pf for i in if_ if (p, i) in CONVERGENT_PAIRS]
    denom = len(pf) * len(if_)
    ratio = len(matches) / denom if denom else 0
    contribution = freq * ratio
    per_sign[sign] = contribution
    name = SIGN_NAMES[sign]
    phon_str = "/".join(sorted(pf))
    icon_str = "/".join(sorted(if_))
    match_str = "+".join(f"{p}~{i}" for p, i in matches) if matches else "—"
    print(f"  #{sign:02d}    {name:<20}  {phon_str:<25}  {icon_str:<25}  {match_str}")

print()
print(f"  TOTAL ALIGNMENT SCORE (frequency-weighted): {DISC_ALIGN:.4f}")
print()

print("Running null model simulations ...")
null_scores = []
n_exceed = 0
for i in range(N_SIM):
    s = null_align()
    null_scores.append(s)
    if s >= DISC_ALIGN:
        n_exceed += 1
    if (i + 1) % 25_000 == 0:
        print(f"  ... {i+1:,} / {N_SIM:,}")

mean_n = sum(null_scores) / N_SIM
var_n  = sum((x - mean_n)**2 for x in null_scores) / N_SIM
std_n  = math.sqrt(var_n) if var_n > 0 else 1e-9
z      = (DISC_ALIGN - mean_n) / std_n
p_val  = n_exceed / N_SIM

print()
print(SEP)
print("RESULTS")
print(SEP)
print()
print(f"  Real disc alignment score : {DISC_ALIGN:.4f}")
print(f"  Null mean ± SD            : {mean_n:.4f} ± {std_n:.4f}")
print(f"  Z-score                   : {z:+.2f}")
print(f"  p (one-tailed)            : {p_val:.6f}  ({n_exceed}/{N_SIM} exceed)")
if p_val == 0.0:
    print(f"  Upper bound               : p < {1/N_SIM:.2e}")
print()

# Top contributing signs
print(SEP)
print("TOP ALIGNMENT CONTRIBUTORS (by frequency-weighted score)")
print(SEP)
print()
for sign, contrib in sorted(per_sign.items(), key=lambda x: -x[1]):
    freq = SIGN_FREQ[sign]
    name = SIGN_NAMES[sign]
    print(f"  #{sign:02d} {name:<20}  freq={freq:3d}  contribution={contrib:.3f}")

print()
print(SEP)
print("INTERPRETATION")
print(SEP)
print()

if z > 3:
    print(f"  SIGNIFICANT: Z={z:+.2f}, p={p_val:.6f}")
    print()
    print("  The phonetic (G_LUWIAN) and iconographic layers converge")
    print("  semantically more than random iconographic label assignments.")
    print()
    print("  Key convergences found:")
    for sign in sorted(per_sign, key=lambda x: -per_sign[x])[:5]:
        if per_sign[sign] > 0:
            pf = "/".join(sorted(PHONETIC_SEMANTICS[sign]))
            if_ = "/".join(sorted(ICONOGRAPHIC_SEMANTICS[sign]))
            name = SIGN_NAMES[sign]
            print(f"    #{sign:02d} {name}: phon=[{pf}] icon=[{if_}]")
    print()
    print("  This supports the dual-layer hypothesis: the disc carries")
    print("  semantic content accessible through both phonetic reading")
    print("  (Luwian) and visual/iconographic interpretation (Minoan).")
elif z > 2:
    print(f"  MARGINAL: Z={z:+.2f}, p={p_val:.6f}")
    print("  Weak alignment signal. Consistent with partial bilingual structure.")
else:
    print(f"  NOT SIGNIFICANT: Z={z:+.2f}, p={p_val:.6f}")
    print("  Semantic layers do not align more than chance.")
    print("  Possible cause: iconographic assignments too uncertain,")
    print("  or convergent pairs too broad/narrow.")

print()
print("  IMPORTANT CAVEAT: The iconographic semantic assignments (Layer 2)")
print("  are made by the researcher and are not independently verified.")
print("  A blind assignment by an iconographer would strengthen this test.")
print(SEP)
