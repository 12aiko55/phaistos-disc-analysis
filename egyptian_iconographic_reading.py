"""
egyptian_iconographic_reading.py
===================================
Egyptian iconographic reading test for the Phaistos Disc.

HYPOTHESIS (no phonetic assumptions):
  If the Disc borrows Egyptian cosmological grammar, signs at
  RITUAL FOCAL positions (spiral centers + cross-side refrains)
  should carry higher cosmological loading than peripheral signs.

METHOD:
  1. Map Evans signs → Egyptian Gardiner-category analogues (visual only)
  2. Assign cosmological weight: 0=mundane, 1=ritual, 2=cosmic/solar/divine
  3. Egyptian "readings" of spiral centers and refrain groups
  4. Monte Carlo: shuffle all tokens (preserve word lengths) → Z-score
"""

import random
import math
import sys
import os

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from phaistos_canonical_data import (
    SIDE_A_EVANS, SIDE_B_EVANS, SIGN_FREQ, SIGN_NAMES
)

SEED = 42
random.seed(SEED)
N_SIM = 100_000

ALL_WORDS  = SIDE_A_EVANS + SIDE_B_EVANS
ALL_TOKENS = [s for w in ALL_WORDS for s in w]
WORD_LENS  = [len(w) for w in ALL_WORDS]
N_SIDE_A   = len(SIDE_A_EVANS)   # 31

# ---------------------------------------------------------------------------
# 1.  Egyptian iconographic key
#     Evans sign# → (category_label, cosmo_weight, note)
#     cosmo_weight:
#       2 = cosmic / solar / primordial / divine  (SOLAR, WATER, DIVINE, REBIRTH)
#       1 = ritual / protective / martial / sacred (OFFERING, WARRIOR, JOURNEY)
#       0 = mundane  (TOOL, CRAFT, CAPTIVE, KITCHEN)
# ---------------------------------------------------------------------------

EGYPTIAN_KEY = {
     1: ("JOURNEY",         1, "walking man A1 — human motion, Nile journey"),
     2: ("DIVINE-RULER",    2, "plumed pharaoh — Osiris/Ra king, divine authority"),
     3: ("CAPTIVE",         0, "tattooed prisoner — bound enemy, marked captive"),
     4: ("CAPTIVE",         0, "bound prisoner — war captive, Execration text"),
     5: ("HEIR",            1, "child figure — Horus-child, royal renewal"),
     6: ("FERTILE",         1, "woman — Isis/Hathor aspect, divine mother"),
     7: ("GUARDIAN",        1, "helmet — military sentinel, protective force"),
     8: ("WARRIOR",         1, "gauntlet — armored hand, battle"),
     9: ("DIVINE-CROWN",    2, "tiara — Atum/Osiris divine crown, kingship"),
    10: ("FORCE",           1, "arrow — directed force, Sekhmet's arrows"),
    11: ("WEAPON",          1, "bow — war bow, Neith's symbol"),
    12: ("OATH",            1, "shield — protective oath, covenant, Ma'at"),
    13: ("SMITE",           1, "club — pharaoh smite pose, royal domination"),
    14: ("BOUND",           0, "manacles — prisoner binding, Execration"),
    15: ("EARTH",           0, "mattock — agricultural toil, Osiris plough"),
    16: ("CRAFT",           0, "saw — woodworking craft"),
    17: ("CONTAIN",         0, "lid — vessel cover, storage"),
    18: ("CYCLE",           1, "boomerang — cyclical return, Ma'at time"),
    19: ("CRAFT",           0, "plane — carpentry"),
    20: ("OFFERING-JAR",    1, "dolium — canopic/offering jar, funerary vessel"),
    21: ("LINEN",           0, "comb — linen textile, mummy wrapping (process)"),
    22: ("PROJECTILE",      1, "sling — projectile, battle"),
    23: ("PILLAR",          1, "column — djed pillar, sacred architecture"),
    24: ("ROYAL-BEE",       2, "bee (bit) — Lower Egypt kingship, royal cartouche"),
    25: ("SOLAR-BARQUE",    2, "ship — Ra's solar barque, nightly journey through Nun"),
    26: ("BULL-POWER",      1, "horn — Amun's ram/bull horn, divine strength"),
    27: ("SACRIFICE",       1, "animal hide — offering skin, temple sacrifice"),
    28: ("BULL-OFFERING",   2, "bull haunch Xpd — Heb-Sed royal sacrifice, power"),
    29: ("SOLAR-CAT",       2, "cat — Ra-as-cat / Bastet, solar slayer of Apophis"),
    30: ("AMUN-RAM",        2, "ram — Amun, divine hidden father, cosmic breath"),
    31: ("HORUS",           2, "eagle/falcon — Horus, Ra, royal solar bird"),
    32: ("DIVINE-BIRD",     2, "dove/bird — Ba soul, divine messenger, omen"),
    33: ("ABUNDANCE",       1, "tunny fish — Nile fish, abundance, Hathor gift"),
    34: ("ROYAL-BEE",       2, "bee (bit) — Lower Egypt royalty, divine sweetness"),
    35: ("SACRED-TREE",     2, "plane tree — sacred persea, Osiris / djed pillar"),
    36: ("HATHOR",          1, "vine — Hathor's grape, festival offering, fertility"),
    37: ("NUN-WATER",       2, "papyrus — primordial Nile, Nun waters, Lower Egypt"),
    38: ("SOLAR-DISK",      2, "rosette — Ra / Aten solar disk, divine radiance"),
    39: ("REBIRTH",         2, "lotus — sunrise / rebirth, Nefertem emerges from lotus"),
    40: ("APIS-BULL",       1, "ox back — Apis bull, sacrifice, bovine strength"),
    41: ("RITUAL-MUSIC",    2, "flute — Hathor's divine music, ritual ecstasy"),
    42: ("MUNDANE",         0, "grater — kitchen / food preparation"),
    43: ("PURIFICATION",    1, "strainer — ritual cleansing, sem-priest"),
    44: ("AXE",             1, "axe — Canaanite battle axe, royal exchange"),
    45: ("PRIMORDIAL-SEA",  2, "wavy band — Nun, the primordial cosmic ocean"),
}

# ---------------------------------------------------------------------------
# 2.  Focal positions  (0-indexed within each side)
#
#     Seven canonical refrain groups and their disc positions:
#       [2,12,31,26]          → A16(15), A19(18), A22(21)
#       [2,27,25,10,23,18]    → A14(13), A20(19)
#       [28,1]                → A15(14), A21(20)
#       [2,12,27,27,35,37,21] → A17(16), A29(28)
#       [10,3,38]             → A28(27), A31(30)  ← spiral center A
#       [22,29,36,7,8]        → B21(20), B26(25)
#       [29,45,7]             → A03(2),  B20(19)
#     Spiral center B:  B30(29) = [45,7]  (unique, not a repeat)
# ---------------------------------------------------------------------------

FOCAL_A = frozenset({2, 13, 14, 15, 16, 18, 19, 20, 21, 27, 28, 30})
FOCAL_B = frozenset({19, 20, 25, 29})

# ---------------------------------------------------------------------------
# 3.  Helper functions
# ---------------------------------------------------------------------------

def cosmo(sign):
    return EGYPTIAN_KEY[sign][1] if sign in EGYPTIAN_KEY else 0

def eg_label(sign):
    return EGYPTIAN_KEY[sign][0] if sign in EGYPTIAN_KEY else f"#{sign}?"

def eg_note(sign):
    return EGYPTIAN_KEY[sign][2] if sign in EGYPTIAN_KEY else "unknown sign"

def group_cosmo(word):
    if not word:
        return 0.0
    return sum(cosmo(s) for s in word) / len(word)

def fmt_word(word, label=""):
    parts = [f"#{s}({eg_label(s)})" for s in word]
    score = group_cosmo(word)
    tag = f" [{label}]" if label else ""
    return " + ".join(parts) + f"  →  cosmo={score:.2f}{tag}"

# ---------------------------------------------------------------------------
# 4.  Egyptian readings of the spiral centers
# ---------------------------------------------------------------------------

SEP  = "=" * 72
SEP2 = "-" * 72

# Named group definitions for display
NAMED_GROUPS = {
    "A31 [spiral center, Side A]":     SIDE_A_EVANS[30],
    "A28 [center repeated — penult.]": SIDE_A_EVANS[27],
    "B30 [spiral center, Side B]":     SIDE_B_EVANS[29],
}

# Named refrains
NAMED_REFRAINS = {
    "[2,12,31,26]  — A16·A19·A22":          [2, 12, 31, 26],
    "[2,27,25,10,23,18] — A14·A20":          [2, 27, 25, 10, 23, 18],
    "[28,1]        — A15·A21":               [28, 1],
    "[2,12,27,27,35,37,21] — A17·A29":       [2, 12, 27, 27, 35, 37, 21],
    "[10,3,38]     — A28·A31 (centers)":     [10, 3, 38],
    "[22,29,36,7,8] — B21·B26":              [22, 29, 36, 7, 8],
    "[29,45,7]     — A03·B20 (cross-side)":  [29, 45, 7],
}

# Qualitative Egyptian interpretations (manually composed from iconographic logic)
INTERPRETATION = {
    "A31":  (
        "Solar force subdues the marked captive",
        "FORCE(arrow) + CAPTIVE + SOLAR-DISK(rosette) = pharaoh smiting enemies under Ra.\n"
        "  Core Egyptian royal formula: Sekhmet's arrows strike down the bound enemy\n"
        "  as the solar disk witnesses. Found on every pharaonic victory stele."
    ),
    "B30":  (
        "Guardian of the primordial ocean",
        "PRIMORDIAL-SEA(Nun) + GUARDIAN(helmet) = sentinel at the cosmic boundary.\n"
        "  In Egyptian cosmology Nun (the primordial waters) must be guarded at dawn\n"
        "  so Ra's barque can emerge. This is a boundary/threshold protection formula."
    ),
    "[29,45,7]": (
        "The solar cat slays Apophis in the primordial ocean",
        "SOLAR-CAT(Ra-cat/Bastet) + PRIMORDIAL-SEA(Nun) + GUARDIAN(helmet).\n"
        "  Direct parallel to Book of the Dead / Papyrus of Ani: Ra as the Great Cat\n"
        "  cuts the serpent of chaos (Apophis) in the Nun each night → sunrise.\n"
        "  This is one of the most canonical Egyptian cosmological scenes."
    ),
    "[2,12,31,26]": (
        "The divine ruler swears by Horus and the bull's power",
        "DIVINE-RULER + OATH(shield) + HORUS(falcon) + BULL-POWER(horn).\n"
        "  Royal coronation oath: the pharaoh swears by Horus (his divine form)\n"
        "  and the bull's might (Apis/Amun). Standard coronation seal formula."
    ),
    "[2,27,25,10,23,18]": (
        "The divine king offers on the solar barque at the sacred pillar, in cyclical return",
        "DIVINE-RULER + SACRIFICE(hide) + SOLAR-BARQUE + FORCE + PILLAR(djed) + CYCLE.\n"
        "  Egyptian Amduat / solar barque ritual: pharaoh accompanies Ra on the\n"
        "  nightly barque through Duat, offering at each sacred pillar-gate.\n"
        "  'Cyclical return' = the guaranteed sunrise after each nightly passage."
    ),
    "[28,1]": (
        "The bull sacrifice begins the journey",
        "BULL-OFFERING(Xpd haunch) + JOURNEY(walking man).\n"
        "  Heb-Sed festival: bull sacrifice initiates the royal renewal procession.\n"
        "  Minimal formula — may serve as a processional marker between longer ones."
    ),
    "[2,12,27,27,35,37,21]": (
        "The divine ruler swears double sacrifice [by] the sacred tree and primordial water [wrapped in] linen",
        "DIVINE-RULER + OATH + SACRIFICE + SACRIFICE + SACRED-TREE + NUN-WATER + LINEN.\n"
        "  Double-sacrifice oath formula with sacred persea tree (Osiris symbol)\n"
        "  and Nun water — funerary/Osirian context. Linen = mummy wrapping.\n"
        "  Possibly: the pharaoh's funerary oath, sealed by tree + water + linen."
    ),
    "[22,29,36,7,8]": (
        "Bastet's claws guard Hathor's abundance, armored warrior",
        "PROJECTILE + SOLAR-CAT(Bastet) + HATHOR(vine/grape) + GUARDIAN + WARRIOR(gauntlet).\n"
        "  Sekhmet-Bastet protective formula over the harvest/abundance (Hathor's domain).\n"
        "  'The sacred cat launches [her] projectile, guarding the vineyard, armored.'\n"
        "  Parallels the Bastet-as-protector-of-harvest motif in Late Period texts."
    ),
}

# ---------------------------------------------------------------------------
# 5.  Print full Egyptian reading
# ---------------------------------------------------------------------------

print(SEP)
print("EGYPTIAN ICONOGRAPHIC READING — PHAISTOS DISC")
print("Visual parallels only  |  No phonetic assumptions")
print("Cosmological weights: 0=mundane  1=ritual  2=cosmic/solar/divine")
print(SEP)
print()

# -- Sign inventory
print("EGYPTIAN SIGN TABLE (all 45 Evans signs, by cosmological weight):")
print()
for w_level in (2, 1, 0):
    label = {2: "COSMIC  (weight=2)", 1: "RITUAL  (weight=1)", 0: "MUNDANE (weight=0)"}[w_level]
    signs = [s for s in range(1, 46) if cosmo(s) == w_level]
    print(f"  {label}:")
    for s in signs:
        name = SIGN_NAMES.get(s, f"#{s}")
        freq = SIGN_FREQ.get(s, 0)
        cat  = eg_label(s)
        print(f"    #{s:02d} {name:<22} {freq:3d}x  →  {cat}")
    print()

# -- Spiral centers
print(SEP)
print("SPIRAL CENTERS — EGYPTIAN READING")
print(SEP)
print()

center_data = [
    ("A31", "spiral center Side A", SIDE_A_EVANS[30]),
    ("A28", "center repeated (penult.)", SIDE_A_EVANS[27]),
    ("B30", "spiral center Side B", SIDE_B_EVANS[29]),
]

for code, desc, word in center_data:
    score = group_cosmo(word)
    print(f"  {code} [{desc}]  →  cosmo={score:.2f}")
    for s in word:
        name = SIGN_NAMES.get(s, f"#{s}")
        print(f"    #{s:02d} {name:<22} weight={cosmo(s)}  [{eg_label(s)}]")
        print(f"         {eg_note(s)}")
    if code in INTERPRETATION:
        title, body = INTERPRETATION[code]
        print(f"  READING: \"{title}\"")
        for line in body.split("\n"):
            print(f"  {line}")
    print()

# -- Refrain groups
print(SEP)
print("REFRAIN GROUPS — EGYPTIAN READING (7 canonical refrains)")
print(SEP)
print()

refrain_items = [
    ("[2,12,31,26]",           "A16·A19·A22 (×3)",     [2, 12, 31, 26]),
    ("[2,27,25,10,23,18]",     "A14·A20",               [2, 27, 25, 10, 23, 18]),
    ("[28,1]",                 "A15·A21",               [28, 1]),
    ("[2,12,27,27,35,37,21]",  "A17·A29",               [2, 12, 27, 27, 35, 37, 21]),
    ("[10,3,38]",              "A28·A31 (centers)",     [10, 3, 38]),
    ("[22,29,36,7,8]",         "B21·B26",               [22, 29, 36, 7, 8]),
    ("[29,45,7]",              "A03·B20 (cross-side)",  [29, 45, 7]),
]

for gkey, positions, word in refrain_items:
    score = group_cosmo(word)
    print(f"  {gkey}  at {positions}  →  cosmo={score:.2f}")
    for s in word:
        name = SIGN_NAMES.get(s, f"#{s}")
        print(f"    #{s:02d} {name:<22} weight={cosmo(s)}  [{eg_label(s)}]")
    key_lookup = gkey.strip("[]").replace(",", ",")
    match = None
    for k in INTERPRETATION:
        if k in gkey or gkey in k:
            match = k
            break
    if not match:
        # Try refrain-specific lookup
        for k in INTERPRETATION:
            if k.startswith("[") and k.split("]")[0][1:] in gkey:
                match = k
                break
    if match and match in INTERPRETATION:
        title, body = INTERPRETATION[match]
        print(f"  READING: \"{title}\"")
        for line in body.split("\n"):
            print(f"  {line}")
    print()

# ---------------------------------------------------------------------------
# 6.  Cosmological loading: focal vs peripheral
# ---------------------------------------------------------------------------

def split_focal_peri(side_words, focal_idx):
    focal, peri = [], []
    for i, w in enumerate(side_words):
        (focal if i in focal_idx else peri).append(group_cosmo(w))
    return focal, peri

fa, pa = split_focal_peri(SIDE_A_EVANS, FOCAL_A)
fb, pb = split_focal_peri(SIDE_B_EVANS, FOCAL_B)

all_focal = fa + fb
all_peri  = pa + pb

real_focal_mean = sum(all_focal) / len(all_focal)
real_peri_mean  = sum(all_peri)  / len(all_peri)
real_diff       = real_focal_mean - real_peri_mean

print(SEP)
print("COSMOLOGICAL LOADING: FOCAL vs PERIPHERAL")
print(SEP)
print()
print(f"  Focal positions  : {len(all_focal):2d} word groups "
      f"(A-side: {len(fa)}/31, B-side: {len(fb)}/30)")
print(f"  Peripheral       : {len(all_peri):2d} word groups")
print(f"  Focal cosmo mean : {real_focal_mean:.4f}")
print(f"  Peri  cosmo mean : {real_peri_mean:.4f}")
print(f"  Difference       : {real_diff:+.4f}")
print()

print("  Focal word groups (cosmo scores):")
for i, s in enumerate(all_focal):
    print(f"    {i+1:2d}. {s:.4f}")
print()
print("  Peripheral word groups (cosmo scores):")
for i, s in enumerate(all_peri):
    print(f"    {i+1:2d}. {s:.4f}")
print()

# ---------------------------------------------------------------------------
# 7.  Monte Carlo null: shuffle all tokens, preserve word lengths
# ---------------------------------------------------------------------------

print("Running Monte Carlo null (N=100,000) ...")

null_diffs = []
n_exceed   = 0

for sim in range(N_SIM):
    tokens = ALL_TOKENS[:]
    random.shuffle(tokens)
    words, idx = [], 0
    for ln in WORD_LENS:
        words.append(tokens[idx:idx+ln])
        idx += ln
    sa = words[:N_SIDE_A]
    sb = words[N_SIDE_A:]
    nfa, npa = split_focal_peri(sa, FOCAL_A)
    nfb, npb = split_focal_peri(sb, FOCAL_B)
    nf = nfa + nfb
    np_ = npa + npb
    fm = sum(nf) / len(nf) if nf else 0.0
    pm = sum(np_) / len(np_) if np_ else 0.0
    d = fm - pm
    null_diffs.append(d)
    if d >= real_diff:
        n_exceed += 1
    if (sim + 1) % 25_000 == 0:
        print(f"  ... {sim+1:,} / {N_SIM:,}")

null_mean = sum(null_diffs) / N_SIM
null_var  = sum((x - null_mean) ** 2 for x in null_diffs) / N_SIM
null_std  = math.sqrt(null_var) if null_var > 0 else 1e-9
z_score   = (real_diff - null_mean) / null_std
p_val     = n_exceed / N_SIM

print()
print(SEP)
print("RESULTS — FOCAL vs PERIPHERAL COSMOLOGICAL LOADING")
print(SEP)
print()
print(f"  Real focal−peri diff  : {real_diff:+.4f}")
print(f"  Null mean ± SD        : {null_mean:+.4f} ± {null_std:.4f}")
print(f"  Z-score               : {z_score:+.2f}")
print(f"  p (one-tailed)        : {p_val:.6f}  ({n_exceed}/{N_SIM} exceed)")
if p_val == 0.0:
    print(f"  Upper bound           : p < {1/N_SIM:.1e}")
print()

# ---------------------------------------------------------------------------
# 8.  Interpretation
# ---------------------------------------------------------------------------

print(SEP)
print("INTERPRETATION")
print(SEP)
print()

if z_score >= 3.0:
    verdict = f"SIGNIFICANT  (Z={z_score:+.2f}, p={p_val:.6f})"
elif z_score >= 2.0:
    verdict = f"MARGINAL     (Z={z_score:+.2f}, p={p_val:.6f})"
else:
    verdict = f"NOT SIGNIFICANT (Z={z_score:+.2f}, p={p_val:.6f})"

print(f"  {verdict}")
print()
print("  Focal positions = spiral centers (A31, A28, B30) +")
print("  all 7 canonical refrain groups.")
print()
print("  If significant: spiral centers and refrains specifically")
print("  concentrate Egyptian-cosmologically-loaded signs (SOLAR,")
print("  DIVINE, PRIMORDIAL-WATER, ROYAL, REBIRTH), while peripheral")
print("  groups contain more MUNDANE/RITUAL signs. This matches the")
print("  Egyptian practice of placing the highest-register divine names")
print("  (Ra, Atum, Osiris) at structural focal points of ritual texts.")
print()
print("  KEY NARRATIVE PARALLELS (qualitative):")
print()
print("  1. [10,3,38] at A31/A28 (center):")
print("     FORCE + CAPTIVE + SOLAR-DISK")
print("     = 'Solar force subdues the captive enemy'")
print("     = Pharaonic smite formula (on every victory stele of Egypt)")
print()
print("  2. [45,7] at B30 (center):")
print("     PRIMORDIAL-SEA + GUARDIAN")
print("     = 'Guardian at the primordial ocean boundary'")
print("     = Boundary of Nun, threshold of Ra's barque emergence")
print()
print("  3. [29,45,7] at A03·B20 (cross-side refrain):")
print("     SOLAR-CAT + PRIMORDIAL-SEA + GUARDIAN")
print("     = 'The solar cat protects the primordial ocean'")
print("     = Ra-as-Great-Cat cutting Apophis in the Nun (Book of the Dead)")
print("     = One of the most canonical Egyptian cosmological scenes")
print()
print("  4. [2,12,31,26] × 3 (most repeated group):")
print("     DIVINE-RULER + OATH + HORUS + BULL-POWER")
print("     = 'The divine king swears by Horus and the bull-god'")
print("     = Royal coronation formula, repeated 3× as emphasis")
print()
print("  IMPORTANT CAVEATS:")
print("  - Egyptian categories are assigned by the researcher (not blind)")
print("  - Cosmological weights are subjective (0/1/2 scale)")
print("  - 'Coherence' of reading is qualitative and susceptible to")
print("    confirmation bias — needs independent iconographic validation")
print("  - The disc MAY borrow Egyptian MOTIFS without Egyptian GRAMMAR")
print(SEP)
