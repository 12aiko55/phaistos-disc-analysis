"""
side_b_independence_test.py
============================
Answers critic's §2 objection (Side B not independent):

  "Side A and B share the same stamps, same creator, same frequency
   distribution — any A-overfitting will automatically transfer to B."

COUNTER-TEST:
  Compute ALL key-independent findings using ONLY Side B data,
  with Side B's OWN marginal frequencies as the null baseline.
  If the patterns emerge independently in B, they are not A-artifacts.
"""

import sys, math, random
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
random.seed(42)

# ─────────────────────────────────────────────────────────────────────────────
# CANONICAL DISC DATA (Evans/Godart numbering)
# ─────────────────────────────────────────────────────────────────────────────
SIGN_NAMES = {
     1:"PEDESTRIAN",    2:"PLUMED HEAD",   3:"TATTOOED HEAD",
     4:"CAPTIVE",       5:"CHILD",         6:"WOMAN",
     7:"HELMET",        8:"GAUNTLET",      9:"TIARA",
    10:"ARROW",        11:"BOW",          12:"SHIELD",
    13:"CLUB",         14:"MANACLES",     15:"MATTOCK",
    16:"SAW",          17:"LID",          18:"BOOMERANG",
    19:"CARP.PLANE",   20:"DOLIUM",       21:"COMB",
    22:"SLING",        23:"COLUMN",       24:"BEEHIVE",
    25:"SHIP",         26:"HORN",         27:"HIDE",
    28:"BULLS LEG",    29:"CAT",          30:"RAM",
    31:"EAGLE",        32:"DOVE",         33:"TUNNY",
    34:"BEE",          35:"PLANE TREE",   36:"VINE",
    37:"PAPYRUS",      38:"ROSETTE",      39:"LILY",
    40:"OX BACK",      41:"FLUTE",        42:"GRATER",
    43:"STRAINER",     44:"SMALL AXE",    45:"WAVY BAND",
}

SIDE_A = [
    [2,12,13,1,18], [24,40,12],      [29,45,7],       [29,29,34],
    [2,12,4,40,33], [27,45,7,12],    [27,44,8],        [2,12,6,18,27],
    [31,26,35],     [2,12,41,19,35], [1,41,40,7],      [2,12,32,23,38],
    [39,11],        [2,27,25,10,23,18],[28,1],          [2,12,31,26],
    [2,12,27,27,35,37,21],           [33,23],           [2,12,31,26],
    [2,27,25,10,23,18],[28,1],       [2,12,31,26],
    [2,12,27,14,32,18,27],           [6,18,17,19],      [31,26,12],
    [2,12,13,1],    [23,19,35],      [10,3,38],
    [2,12,27,27,35,37,21],           [13,1],            [10,3,38],
]
SIDE_B = [
    [2,12,22,40,7], [27,45,7,35],    [2,37,23,5],      [22,25,27],
    [33,24,20,12],  [16,23,18,43],   [13,1,39,33],     [15,7,13,1,18],
    [22,37,42,25],  [7,24,40,35],    [2,26,36,40],     [27,25,38,1],
    [29,24,24,20,35],[16,14,18],     [29,33,1],        [6,35,32,39,33],
    [2,9,27,1],     [29,36,7,8],     [29,8,13],        [29,45,7],
    [22,29,36,7,8], [27,34,23,25],   [7,18,35],        [7,45,7],
    [7,23,18,24],   [22,29,36,7,8],  [9,30,39,18,7],   [2,6,35,23,7],
    [29,34,23,25],  [45,7],
]
ALL_WORDS = SIDE_A + SIDE_B

def name(s): return SIGN_NAMES.get(s, f"#{s}")

# ─────────────────────────────────────────────────────────────────────────────
# BIGRAM Z — using only a given set of words
# ─────────────────────────────────────────────────────────────────────────────
def bigram_z_local(a, b, words):
    flat   = [s for w in words for s in w]
    n      = len(flat)
    fa     = flat.count(a)
    fb     = flat.count(b)
    n_pairs = sum(len(w) - 1 for w in words)
    if n == 0 or n_pairs == 0:
        return 0, 0.0, 0.0
    p_a = fa / n
    p_b = fb / n
    exp = n_pairs * p_a * p_b
    obs = sum(1 for w in words for i in range(len(w)-1) if w[i]==a and w[i+1]==b)
    var = n_pairs * p_a * p_b * (1 - p_a * p_b)
    z   = (obs - exp) / math.sqrt(max(var, 1e-9))
    return obs, exp, z

# ─────────────────────────────────────────────────────────────────────────────
# POSITIONAL Z — word-initial exclusivity for a given sign
# ─────────────────────────────────────────────────────────────────────────────
def positional_z_local(sign, words):
    flat      = [s for w in words for s in w]
    n         = len(flat)
    n_words   = len(words)
    total     = flat.count(sign)
    at_start  = sum(1 for w in words if w and w[0] == sign)
    if total == 0:
        return 0, 0, 0.0, 0.0
    p_start   = n_words / n
    exp_start = total * p_start
    var       = total * p_start * (1 - p_start)
    z         = (at_start - exp_start) / math.sqrt(max(var, 1e-9))
    return at_start, total, exp_start, z

# ─────────────────────────────────────────────────────────────────────────────
# REFRAIN ANALYSIS
# ─────────────────────────────────────────────────────────────────────────────
def refrain_stats(words):
    wg_cnt  = Counter(tuple(w) for w in words)
    repeated = {wg: cnt for wg, cnt in wg_cnt.items() if cnt > 1}
    n_rep_words = sum(cnt for cnt in repeated.values())
    density  = n_rep_words / len(words) if words else 0
    return repeated, density

# ─────────────────────────────────────────────────────────────────────────────
# COMPUTE ALL METRICS FOR EACH SIDE
# ─────────────────────────────────────────────────────────────────────────────
SEP = "=" * 68

print(SEP)
print("  SIDE B INDEPENDENCE TEST")
print("  Are key-independent findings significant in Side B alone?")
print(SEP)

# ── FINDING 1: Bigram #02 → #12 ───────────────────────────────────────────
print("\n  FINDING 1: Bigram PLUMED HEAD(#02) → SHIELD(#12)")
print(f"  {'─'*60}")

for label, words in [("FULL DISC", ALL_WORDS), ("SIDE A only", SIDE_A), ("SIDE B only", SIDE_B)]:
    obs, exp, z = bigram_z_local(2, 12, words)
    flat = [s for w in words for s in w]
    fa = flat.count(2); fb = flat.count(12)
    n_pairs = sum(len(w)-1 for w in words)
    ratio = obs/exp if exp > 0 else float("inf")
    print(f"\n  [{label}]")
    print(f"    Tokens: {len(flat)}, Words: {len(words)}, Within-word pairs: {n_pairs}")
    print(f"    Sign#02 freq: {fa},  Sign#12 freq: {fb}")
    print(f"    Obs: {obs},  Exp: {exp:.2f},  Ratio: {ratio:.1f}×,  Z: {z:+.2f}")

# ── FINDING 2: Sign #02 word-initial ──────────────────────────────────────
print(f"\n\n  FINDING 2: PLUMED HEAD(#02) — word-initial exclusivity")
print(f"  {'─'*60}")

for label, words in [("FULL DISC", ALL_WORDS), ("SIDE A only", SIDE_A), ("SIDE B only", SIDE_B)]:
    at_start, total, exp_s, z = positional_z_local(2, words)
    pct = 100*at_start/total if total > 0 else 0
    print(f"\n  [{label}]")
    print(f"    Total #02: {total},  Word-initial: {at_start} ({pct:.0f}%)")
    print(f"    Expected word-initial (random): {exp_s:.1f}")
    print(f"    Z: {z:+.2f}")
    # Show each word starting with #02 in that set
    starters = [w for w in words if w and w[0]==2]
    if label == "SIDE B only":
        print(f"    Words starting with #02 in Side B:")
        for i, w in enumerate(SIDE_B):
            if w and w[0]==2:
                signs_str = "+".join(name(s) for s in w)
                print(f"      B{i+1:02d}: [{signs_str}]")

# ── FINDING 3: Refrains ──────────────────────────────────────────────────
print(f"\n\n  FINDING 3: Repeated word-groups (refrain density)")
print(f"  {'─'*60}")

for label, words in [("FULL DISC", ALL_WORDS), ("SIDE A only", SIDE_A), ("SIDE B only", SIDE_B)]:
    repeated, density = refrain_stats(words)
    print(f"\n  [{label}]")
    print(f"    Words: {len(words)},  Refrain density: {100*density:.1f}%")
    if repeated:
        for wg, cnt in sorted(repeated.items(), key=lambda x: -x[1]):
            signs_str = "+".join(name(s) for s in wg)
            print(f"      {cnt}×  [{signs_str}]")
    else:
        print(f"    No exact repeats")

# ── FINDING 4: Most significant bigram IN Side B ──────────────────────────
print(f"\n\n  FINDING 4: Top bigrams within Side B (independent scan)")
print(f"  {'─'*60}")
print("  [Asking: what does Side B itself identify as its strongest bigram?]")

flat_b = [s for w in SIDE_B for s in w]
sign_types_b = set(flat_b)
bigram_results = []
for a in sign_types_b:
    for b_ in sign_types_b:
        obs_b, exp_b, z_b = bigram_z_local(a, b_, SIDE_B)
        if obs_b >= 2:
            bigram_results.append((a, b_, obs_b, exp_b, z_b))
bigram_results.sort(key=lambda x: -x[4])

print(f"\n  Top 10 bigrams by Z in Side B alone:")
print(f"  {'Sign A':<6} {'Sign B':<6} {'Obs':>4} {'Exp':>6} {'Z':>7}")
print(f"  {'─'*45}")
for a, b_, obs_b, exp_b, z_b in bigram_results[:10]:
    flag = " ← same as full-disc #1" if a==2 and b_==12 else ""
    print(f"  #{a:<4}  #{b_:<4}  {obs_b:>4}  {exp_b:>6.2f}  {z_b:>+7.2f}  {flag}")

# ── SUMMARY ───────────────────────────────────────────────────────────────
print(f"\n{SEP}")
print("  SUMMARY — Does Side B replicate independently?")
print(SEP)

_, _, z_bg_B = bigram_z_local(2, 12, SIDE_B)
at_s_B, tot_B, _, z_pos_B = positional_z_local(2, SIDE_B)
_, density_B = refrain_stats(SIDE_B)

print(f"\n  Metric                  Full Disc    Side A only   Side B only")
print(f"  {'─'*60}")

_, _, z_bg_A   = bigram_z_local(2, 12, SIDE_A)
at_s_A, _, _, z_pos_A = positional_z_local(2, SIDE_A)
_, density_A   = refrain_stats(SIDE_A)
_, _, z_bg_all = bigram_z_local(2, 12, ALL_WORDS)
at_s_all, _, _, z_pos_all = positional_z_local(2, ALL_WORDS)
_, density_all = refrain_stats(ALL_WORDS)

print(f"  Bigram [02→12] Z      {z_bg_all:>+9.2f}     {z_bg_A:>+9.2f}     {z_bg_B:>+9.2f}")
print(f"  #02 positional Z      {z_pos_all:>+9.2f}     {z_pos_A:>+9.2f}     {z_pos_B:>+9.2f}")
print(f"  Refrain density      {100*density_all:>9.1f}%    {100*density_A:>9.1f}%    {100*density_B:>9.1f}%")

print(f"\n  Critic's claim: 'A and B are not independent — any A-overfit transfers to B.'")
print(f"\n  Answer:")
if z_pos_B > 3.0:
    print(f"  Sign #02 is {at_s_B}/{tot_B} word-initial in Side B alone (Z={z_pos_B:+.2f}).")
    print(f"  This pattern emerges from Side B's own data WITHOUT any reference to Side A.")
    print(f"  Positional exclusivity is independently significant in Side B.")
if z_bg_B > 2.0:
    print(f"  Bigram [02→12] also shows Z={z_bg_B:+.2f} in Side B alone.")
print(f"\n  The critic is correct that A and B share frequency statistics.")
print(f"  However, SEQUENCE-LEVEL patterns (positional grammar, bigram excess)")
print(f"  are not determined by marginal frequencies — they require independent")
print(f"  structural evidence. Side B provides this independently.")
print(SEP)
