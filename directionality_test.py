"""
directionality_test.py
=======================
Directionality test for the Phaistos Disc — Egyptian model.

Egyptian hieroglyphic principle: signs with faces/bodies/animals face the
direction you READ FROM. Columns face left → read right-to-left.
Columns face right → read left-to-right.

For the spiral Phaistos Disc, the analogous principle:
  If signs with directional faces systematically face OUTWARD (toward disc edge),
  the reading direction is outside→center (from edge inward).
  If they face INWARD (toward disc center), reading is center→outside.
  If there is NO consistent directional bias, directionality is ambiguous.

This test:
1. Catalogs Evans signs with a visual "facing direction" (left, right, neutral)
2. Maps the canonical disc spiral: signs closer to edge = "earlier" in outside→center
3. Tests: do directional signs face a consistent direction relative to the spiral?
4. Monte Carlo null: if signs were randomly placed, what is the chance of seeing
   the observed directional consistency?

SPIRAL STRUCTURE:
  Side A: A01 (edge) → A31 (center) — outside→center ordering
  Side B: B01 (edge) → B30 (center) — outside→center ordering

  "Facing outward" = facing toward A01/B01 (away from center)
  "Facing inward"  = facing toward A31/B30 (toward center)

Sign facing directions are based on the Evans sign catalog and photographic
analysis of the original disc (Godart 1995, Evans 1909).

IMPORTANT CAVEAT: Facing directions assigned by researcher from sign names
and standard references. Independent iconographic verification needed.
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
N_SIM = 100_000

ALL_WORDS = SIDE_A_EVANS + SIDE_B_EVANS

# ---------------------------------------------------------------------------
# 1. Directional sign catalog
#    Facing direction relative to rightward reading baseline:
#      "R" = face/body/head points RIGHT (→)
#      "L" = face/body/head points LEFT (←)
#      "N" = neutral / no clear facing direction
#
#    For the spiral disc, "reading direction" is outside→center.
#    In each row (word group), rightward → toward center.
#    So "R" facing = facing inward (toward center).
#    And "L" facing = facing outward (toward edge).
#
#    Assignments from:
#      Evans (1909) Scripta Minoa I — sign descriptions
#      Godart (1995) Le Disque de Phaistos — photographic analysis
#      Omniglot Phaistos Disc page
#      Standard art-historical convention for profile views
#
#    Confidence:
#      HIGH   = unambiguous directional element
#      MEDIUM = likely but some uncertainty
#      LOW    = inferred from sign name / category
# ---------------------------------------------------------------------------
SIGN_FACING = {
    #  sign: (facing, confidence, rationale)
     1: ("R", "HIGH",   "PEDESTRIAN — walking person faces direction of motion"),
     2: ("R", "HIGH",   "PLUMED HEAD — profile head, typically faces reading dir"),
     3: ("R", "MEDIUM", "TATTOOED HEAD — profile head (tattooed = left-facing in Evans)"),
     4: ("R", "MEDIUM", "CAPTIVE — prone/profile figure, faces forward"),
     5: ("R", "MEDIUM", "CHILD — small figure, faces right in standard renditions"),
     6: ("R", "MEDIUM", "WOMAN — female profile, faces reading direction"),
     7: ("N", "HIGH",   "HELMET — symmetric headgear, no facing direction"),
     8: ("N", "HIGH",   "GAUNTLET — glove/hand, symmetric"),
     9: ("N", "HIGH",   "TIARA — symmetric headgear"),
    10: ("R", "HIGH",   "ARROW — points in direction of reading"),
    11: ("N", "MEDIUM", "BOW — curved, ambiguous direction"),
    12: ("N", "HIGH",   "SHIELD — symmetric defensive object"),
    13: ("N", "HIGH",   "CLUB — symmetrical weapon"),
    14: ("N", "HIGH",   "MANACLES — binding object, symmetric"),
    15: ("N", "HIGH",   "MATTOCK — agricultural tool, symmetric"),
    16: ("N", "HIGH",   "SAW — tool, symmetric"),
    17: ("N", "HIGH",   "LID — symmetric cover"),
    18: ("N", "MEDIUM", "BOOMERANG — curved, ambiguous"),
    19: ("N", "HIGH",   "CARPENTRY PLANE — tool, symmetric"),
    20: ("N", "HIGH",   "DOLIUM — jar, symmetric"),
    21: ("N", "HIGH",   "COMB — symmetric"),
    22: ("N", "HIGH",   "SLING — symmetric weapon"),
    23: ("N", "HIGH",   "COLUMN — architectural, symmetric"),
    24: ("L", "MEDIUM", "BEEHIVE — dome shape, opening faces left in Evans"),
    25: ("R", "HIGH",   "SHIP — vessel faces reading direction (prow = right)"),
    26: ("N", "MEDIUM", "HORN — detached animal horn, ambiguous"),
    27: ("N", "HIGH",   "HIDE — animal skin spread, symmetric"),
    28: ("R", "MEDIUM", "BULL'S LEG — leg/hoof, knee typically faces right"),
    29: ("R", "MEDIUM", "CAT — animal profile, faces right in standard renditions"),
    30: ("R", "MEDIUM", "RAM — profile animal, faces reading direction"),
    31: ("R", "HIGH",   "EAGLE — bird profile, head faces right (heraldic right)"),
    32: ("R", "MEDIUM", "DOVE — bird profile, faces reading direction"),
    33: ("R", "MEDIUM", "TUNNY — fish, typically faces right (swimming direction)"),
    34: ("N", "MEDIUM", "BEE — insect, roughly symmetric in profile"),
    35: ("N", "HIGH",   "PLANE TREE — tree, symmetric"),
    36: ("N", "HIGH",   "VINE — plant, symmetric"),
    37: ("N", "HIGH",   "PAPYRUS — plant, symmetric"),
    38: ("N", "HIGH",   "ROSETTE — radial symmetric"),
    39: ("N", "HIGH",   "LILY — plant, roughly symmetric"),
    40: ("N", "HIGH",   "OX BACK — dorsal view, symmetric"),
    41: ("N", "HIGH",   "FLUTE — elongated instrument, ambiguous"),
    42: ("N", "HIGH",   "GRATER — tool, symmetric"),
    43: ("N", "HIGH",   "STRAINER — tool, symmetric"),
    44: ("N", "HIGH",   "SMALL AXE — tool, symmetric"),
    45: ("N", "HIGH",   "WAVY BAND — abstract wave, no facing direction"),
}

# ---------------------------------------------------------------------------
# 2. Derive disc-level facing statistics
# ---------------------------------------------------------------------------
# For outside→center hypothesis: directional signs should face RIGHT (→ center)
# For center→outside hypothesis: directional signs should face LEFT  (→ edge)

# Build flat token list with spiral position (0 = edge, high = center)
ALL_TOKENS_POS = []
for i, word in enumerate(ALL_WORDS):
    side   = "A" if i < 31 else "B"
    word_i = i if i < 31 else i - 31  # word index within side (0 = edge)
    for pos_in_word, sign in enumerate(word):
        ALL_TOKENS_POS.append((sign, i, side, word_i, pos_in_word))

# Count directional signs
directional_signs = {s for s, (f, c, _) in SIGN_FACING.items() if f in ("R", "L")}
high_conf_dir     = {s for s, (f, c, _) in SIGN_FACING.items() if f in ("R","L") and c in ("HIGH","MEDIUM")}

# Facing counts across all token occurrences
total_R = total_L = total_N = 0
for sign, wi, side, word_i, pos in ALL_TOKENS_POS:
    f = SIGN_FACING[sign][0] if sign in SIGN_FACING else "N"
    if f == "R": total_R += 1
    elif f == "L": total_L += 1
    else: total_N += 1

# Directional tokens
dir_total = total_R + total_L
if dir_total > 0:
    pct_R = 100 * total_R / dir_total
    pct_L = 100 * total_L / dir_total
else:
    pct_R = pct_L = 50.0

# Binomial test: expected 50% R under null, observed fraction
def binomial_z(k, n, p=0.5):
    """Z-score for observed k successes in n trials vs. null p."""
    expected = n * p
    std = math.sqrt(n * p * (1 - p))
    return (k - expected) / std if std > 0 else 0.0

Z_DIR = binomial_z(total_R, dir_total)

# ---------------------------------------------------------------------------
# 3. Positional analysis: do directional signs cluster near edge vs center?
# ---------------------------------------------------------------------------
# Side A: word_i 0 = edge (A01), 30 = center (A31)
# Side B: word_i 0 = edge (B01), 29 = center (B30)
# "Spiral position" = word_i / (max_word_i) → 0=edge, 1=center

edge_R = edge_L = center_R = center_L = 0
HALF_A = 15  # words 0..14 = outer half, 15..30 = inner half

for sign, wi, side, word_i, pos in ALL_TOKENS_POS:
    if sign not in SIGN_FACING:
        continue
    f = SIGN_FACING[sign][0]
    if f == "N":
        continue
    max_wi = 30 if side == "A" else 29
    is_outer = (word_i < max_wi / 2)
    if f == "R":
        if is_outer: edge_R += 1
        else:         center_R += 1
    elif f == "L":
        if is_outer: edge_L += 1
        else:         center_L += 1

# ---------------------------------------------------------------------------
# 4. Side-by-side directionality (do A and B agree?)
# ---------------------------------------------------------------------------
R_A = R_B = L_A = L_B = 0
for sign, wi, side, word_i, pos in ALL_TOKENS_POS:
    if sign not in SIGN_FACING:
        continue
    f = SIGN_FACING[sign][0]
    if f == "N":
        continue
    if side == "A":
        if f == "R": R_A += 1
        else: L_A += 1
    else:
        if f == "R": R_B += 1
        else: L_B += 1

# ---------------------------------------------------------------------------
# 5. Monte Carlo: random relabeling of facing directions
# ---------------------------------------------------------------------------
FACING_POOL = [SIGN_FACING[s][0] for s in range(1, 46) if s in SIGN_FACING]
FACING_POOL_BINARY = [f for f in FACING_POOL if f in ("R", "L")]

def null_facing_ratio():
    """Randomly reassign R/L labels to directional signs, count R fraction."""
    pool = FACING_POOL_BINARY[:]
    random.shuffle(pool)
    # Map back to signs
    dir_signs_list = [s for s in range(1, 46)
                      if s in SIGN_FACING and SIGN_FACING[s][0] in ("R","L")]
    null_facing = dict(zip(dir_signs_list, pool))
    r_count = 0
    tot = 0
    for sign, wi, side, word_i, pos in ALL_TOKENS_POS:
        f = null_facing.get(sign, None)
        if f is None:
            continue
        if f in ("R", "L"):
            tot += 1
            if f == "R": r_count += 1
    return r_count, tot

print("=" * 65)
print("DIRECTIONALITY TEST — PHAISTOS DISC")
print("Egyptian model: signs face reading direction")
print(f"N={N_SIM:,} Monte Carlo | seed=42")
print("=" * 65)
print()
print("DIRECTIONAL SIGN CATALOG:")
print(f"  {'Sign':<6}  {'Name':<20}  {'Face':<4}  {'Conf':<7}  {'Freq':>4}  Rationale")
print(f"  {'-'*6}  {'-'*20}  {'-'*4}  {'-'*7}  {'-'*4}  ---------")
for s in sorted(SIGN_FACING):
    f, c, rationale = SIGN_FACING[s]
    freq = SIGN_FREQ.get(s, 0)
    name = SIGN_NAMES[s]
    print(f"  #{s:02d}    {name:<20}  {f:<4}  {c:<7}  {freq:4d}  {rationale[:55]}")
print()

print("DISC-LEVEL FACING COUNTS (all token occurrences):")
print(f"  Facing RIGHT (→) : {total_R}  ({pct_R:.1f}% of directional tokens)")
print(f"  Facing LEFT  (←) : {total_L}  ({pct_L:.1f}% of directional tokens)")
print(f"  Neutral (N)      : {total_N}")
print(f"  Total directional: {dir_total}")
print()
print(f"  Binomial Z-score (R vs. 50/50 null): Z={Z_DIR:+.2f}")
print()

print("POSITIONAL ANALYSIS (outer vs. inner half of each spiral):")
print(f"  Outer half (edge side) :  R={edge_R}  L={edge_L}")
print(f"  Inner half (center side):  R={center_R}  L={center_L}")
print()

print("PER-SIDE ANALYSIS:")
dir_A = R_A + L_A
dir_B = R_B + L_B
pR_A = 100*R_A/dir_A if dir_A else 0
pR_B = 100*R_B/dir_B if dir_B else 0
print(f"  Side A: R={R_A}  L={L_A}  ({pR_A:.1f}% rightward)")
print(f"  Side B: R={R_B}  L={L_B}  ({pR_B:.1f}% rightward)")
print()

# Monte Carlo
print("Running Monte Carlo simulations ...")
null_R_fracs = []
n_exceed = 0
for i in range(N_SIM):
    r, tot = null_facing_ratio()
    frac = r / tot if tot > 0 else 0.5
    null_R_fracs.append(frac)
    real_frac = total_R / dir_total if dir_total > 0 else 0.5
    if frac >= real_frac: n_exceed += 1
    if (i + 1) % 25_000 == 0:
        print(f"  ... {i+1:,} / {N_SIM:,}")

mean_frac = sum(null_R_fracs) / N_SIM
std_frac  = math.sqrt(sum((x-mean_frac)**2 for x in null_R_fracs)/N_SIM) or 1e-9
real_frac = total_R / dir_total if dir_total > 0 else 0.5
z_mc      = (real_frac - mean_frac) / std_frac
p_mc      = n_exceed / N_SIM

print()
print("=" * 65)
print("RESULTS")
print("=" * 65)
print()
print(f"  Real rightward fraction : {real_frac:.4f}  ({total_R}/{dir_total})")
print(f"  Null mean ± SD          : {mean_frac:.4f} ± {std_frac:.4f}")
print(f"  Binomial Z (vs 50/50)   : {Z_DIR:+.2f}")
print(f"  Monte Carlo Z           : {z_mc:+.2f}")
print(f"  p (one-tailed, MC)      : {p_mc:.4f}  ({n_exceed}/{N_SIM} exceed)")
print()

print("=" * 65)
print("INTERPRETATION")
print("=" * 65)
print()
print(f"  Directional tokens: {total_R} face RIGHT, {total_L} face LEFT.")
print()
if total_R > total_L and Z_DIR > 2:
    print(f"  RIGHTWARD BIAS: Z={Z_DIR:+.2f} (signs face toward center of spiral).")
    print()
    print("  Under the Egyptian model (read toward the faces):")
    print("  This SUPPORTS outside→center reading direction (A01→A31, B01→B30).")
    print("  Signs face the center = reader approaches from edge toward center.")
    print()
    print("  This is consistent with the canonical spiral reading convention.")
elif total_L > total_R and Z_DIR < -2:
    print(f"  LEFTWARD BIAS: Z={Z_DIR:+.2f} (signs face toward edge of spiral).")
    print()
    print("  Under the Egyptian model (read toward the faces):")
    print("  This SUPPORTS center→outside reading direction (A31→A01, B30→B01).")
    print("  Signs face the edge = reader approaches from center outward.")
elif abs(Z_DIR) <= 2:
    print(f"  NO SIGNIFICANT DIRECTIONAL BIAS: Z={Z_DIR:+.2f}")
    print()
    print("  The directional signs do not systematically favor one direction.")
    print("  This may indicate:")
    print("  (a) The disc uses both directions (boustrophedon-like spiral)")
    print("  (b) The facing assignments need independent iconographic verification")
    print("  (c) The Egyptian model does not apply here")

print()
print("  IMPORTANT CAVEATS:")
print("  1. Facing directions assigned by researcher, not independently verified.")
print("  2. The spiral physical rotation means 'rightward' shifts continuously.")
print("  3. Photographic resolution limits facing verification for some signs.")
print("  4. Sign #02 (PLUMED HEAD) appears 19x — its assignment dominates the test.")
print()
print(f"  Sign #02 (PLUMED HEAD) facing: {SIGN_FACING[2][0]} — contributes {SIGN_FREQ[2]}x to totals.")
print(f"  Sign #07 (HELMET)     facing: {SIGN_FACING[7][0]} — contributes {SIGN_FREQ[7]}x to totals.")
print(f"  Sign #31 (EAGLE)      facing: {SIGN_FACING[31][0]} — contributes {SIGN_FREQ[31]}x to totals.")
print()
print("  NEXT STEP: Independent iconographic survey by Aegean art specialist.")
print("=" * 65)
