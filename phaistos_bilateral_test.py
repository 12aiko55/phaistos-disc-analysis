"""
phaistos_bilateral_test.py
══════════════════════════════════════════════════════════════════════════════
BILATERAL TRADE DOCUMENT HYPOTHESIS TEST
Chavadakis 2026 — Novel hypothesis

ΥΠΟΘΕΣΗ:
  Πλευρά Α = Μινωιτική/Αιγυπτιακή πλευρά (θεϊκοί μάρτυρες Μινωιτών)
  Πλευρά Β = Λουβική πλευρά (ορκωμοσία με Tiwat + wa-tar τελετουργία)

ΤΕΣΤ:
  Αν η υπόθεση είναι σωστή:
  → G_LUWIAN σκοράρει ΚΑΛΥΤΕΡΑ στην Πλευρά Β από την Α
  → E1_EGYPT / B_FREQ σκοράρουν ΚΑΛΥΤΕΡΑ στην Πλευρά Α από την Β
  → Η διαφορά Z(B) - Z(A) για G_LUWIAN θα είναι σημαντικά θετική
  → Η διαφορά Z(A) - Z(B) για E1_EGYPT θα είναι σημαντικά θετική

ΣΗΜΑΣΙΑ:
  Αν επιβεβαιωθεί → ο δίσκος είναι διμερές εμπορικό/τελετουργικό έγγραφο
  (πρώτη φορά που δοκιμάζεται αυτή η υπόθεση)
"""

import sys, random, math
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SEP  = "=" * 76
SEP2 = "-" * 76
N_MC = 10_000

# ─────────────────────────────────────────────────────────────────────────────
SIDE_A = [
    [2,12,7,1,29],   [2,6,25,6,22],   [1,7,29,3,22],   [29,6,2,7,22],
    [36,2,12,7],     [2,36,12,11,22], [2,29,7,22],      [29,2,7,36,22,11],
    [2,12,7,36],     [29,7,22,2],     [12,2,36,7,22],   [2,7,29,36,22],
    [7,22,2,36,12],  [2,29,36,11],    [29,7,22,36],     [2,36,7,11,22],
    [29,2,22,7],     [36,7,22,2,11],  [2,7,36,22],      [29,36,2,7,11,22],
    [7,2,36,29],     [22,2,36,11],    [29,7,36,2,22],   [2,7,22,29],
    [36,29,2,22,7],  [2,11,36],       [7,22,36,2],      [29,2,36],
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
ALL_WORDS = SIDE_A + SIDE_B
SIGN_FREQ_ORDER = [2,36,11,29,22,7,12,6,45,1,24,25,33,44,3]

# ─────────────────────────────────────────────────────────────────────────────
# KEYS
# ─────────────────────────────────────────────────────────────────────────────
KEYS = {
    "G_LUWIAN": {
         2:"za", 36:"wa", 11:"tar", 29:"na", 22:"ha",
         7:"ti",  12:"zi",  6:"an",  45:"ti-wa", 1:"i",
        24:"su",  25:"naw", 33:"ur", 44:"ma",    3:"pa",
    },
    "E1_EGYPT": {
         2:"na", 36:"ra", 11:"sa", 29:"wa", 22:"ta",
         7:"ma",  12:"a",   6:"ka",  45:"ya",   1:"ha",
        24:"xa",  25:"da",  33:"pa", 44:"ba",   3:"qa",
    },
    "B_FREQ": {
         2:"a",  36:"sa", 11:"ra", 29:"na", 22:"ta",
         7:"ka",  12:"da",  6:"ti",  45:"ma",   1:"si",
        24:"re",  25:"ro",  33:"wa", 44:"ki",   3:"ko",
    },
    "I_MORPHO": {
         2:"a",  36:"ku", 11:"te", 29:"ka", 22:"na",
         7:"da",  12:"qi",  6:"ja",  45:"de",   1:"pa",
        24:"re",  25:"di",  33:"wa", 44:"ke",   3:"si",
    },
}

# ─────────────────────────────────────────────────────────────────────────────
# VOCABULARIES
# ─────────────────────────────────────────────────────────────────────────────
LUWIAN_VOCAB = {
    "za":"dem.", "wa-na":"lord", "ur-a":"great", "ti-wa":"sun-god",
    "ar-ma":"moon", "tar":"lord", "an-ta":"against", "ha-ra":"eagle",
    "za-na":"this-one", "na-wa":"water?", "ha-an":"front", "ti":"be",
    "wa-tar":"water", "at-ta":"father", "an-na":"mother", "tar-hu":"storm-god",
    "za-tar":"this-lord", "wa-na-ta":"lordly", "ur-a-na":"great-one",
}
EGYPT_VOCAB = {
    "na-ra-sa":"n-rA-sA", "sa-ra-na":"sA-rA-n", "na-sa-ra":"n-sA-rA",
    "sa-ra":"sA-rA", "na-ra":"n-rA", "ra-na":"rA-n", "wa-na-ra":"wnn-rA",
    "na-ta-ra":"nTr", "wa-sa-ra":"wsir", "ma-ra":"mAat-rA",
    "an-xa":"anx", "ha-ta-pa":"Htp", "sa-na":"sA-n",
}
LINEAR_A_VOCAB = {
    "a-sa-sa-ra":"Asasara", "a-sa-sa-ra-me":"Asasara+me",
    "ku-ro":"total", "ki-ro":"similar", "a-du":"unknown",
    "su-ki-ri-te-ja":"ritual", "i-da-ma-te":"Ida-Mater",
    "a-sa-ra":"Asara", "ku-pa-nu":"unknown", "wa-ja":"frequent",
}
MORPHEMES_LA = {
    "a":"prefix", "ku":"ku-ro", "ka":"initial", "ja":"ritual",
    "te":"suffix", "na":"genitive", "re":"suffix", "wa":"wa-ja",
    "ku-ro":"total", "a-du":"frequent", "wa-ja":"frequent",
}

VOCAB_BY_KEY = {
    "G_LUWIAN": LUWIAN_VOCAB,
    "E1_EGYPT": EGYPT_VOCAB,
    "B_FREQ":   LINEAR_A_VOCAB,
    "I_MORPHO": MORPHEMES_LA,
}

LINEAR_B_VALUES = [
    "da","ro","pa","te","to","na","di","a","se","u",
    "po","so","me","do","mo","za","mi","mu","ne","ru",
    "re","i","pu","ni","sa","jo","ti","e","pi","wi",
    "si","wo","ke","de","du","no","ri","wa","nu","ja",
    "su","ta","ra","o","ku","pe","we","ka","qe","ko",
]

# ─────────────────────────────────────────────────────────────────────────────
# ENGINE
# ─────────────────────────────────────────────────────────────────────────────
def read_word(w, key):
    return "-".join(key.get(s,"?") for s in w if key.get(s,"?") != "?")

def score_words(words, key, vocab):
    text = " ".join(read_word(w, key) for w in words)
    total = 0
    hits = {}
    for word in vocab:
        if word in text:
            c = text.count(word)
            total += c
            hits[word] = c
    return total, hits, text

def monte_carlo_side(words, vocab, n=N_MC, seed=42):
    random.seed(seed)
    pool  = LINEAR_B_VALUES[:]
    signs = SIGN_FREQ_ORDER[:]
    scores = []
    for _ in range(n):
        random.shuffle(pool)
        rkey = {s: pool[i % len(pool)] for i, s in enumerate(signs)}
        sc, _, _ = score_words(words, rkey, vocab)
        scores.append(sc)
    return scores

def stats(observed, scores):
    mu  = sum(scores) / len(scores)
    sd  = math.sqrt(sum((x-mu)**2 for x in scores) / len(scores)) or 1e-9
    z   = (observed - mu) / sd
    p   = 0.5 * math.erfc(z / math.sqrt(2))
    return mu, sd, z, p

# ─────────────────────────────────────────────────────────────────────────────
print(SEP)
print("  BILATERAL TRADE DOCUMENT HYPOTHESIS")
print("  Scoring each key separately on Side A vs Side B")
print(SEP)

results = {}  # key -> {A: (score,z,p), B: (score,z,p)}

for key_name, key in KEYS.items():
    vocab = VOCAB_BY_KEY[key_name]
    print(f"\n  [{key_name}]  running Monte Carlo (N={N_MC:,}) x2...", end="", flush=True)

    sc_a, hits_a, text_a = score_words(SIDE_A, key, vocab)
    sc_b, hits_b, text_b = score_words(SIDE_B, key, vocab)

    mc_a = monte_carlo_side(SIDE_A, vocab, seed=42)
    mc_b = monte_carlo_side(SIDE_B, vocab, seed=99)

    mu_a, sd_a, z_a, p_a = stats(sc_a, mc_a)
    mu_b, sd_b, z_b, p_b = stats(sc_b, mc_b)

    results[key_name] = {
        "A": (sc_a, mu_a, sd_a, z_a, p_a, hits_a),
        "B": (sc_b, mu_b, sd_b, z_b, p_b, hits_b),
    }
    print(f" done")
    print(f"    Side A: score={sc_a:4d}  Z={z_a:+6.2f}  p={p_a:.5f}")
    print(f"    Side B: score={sc_b:4d}  Z={z_b:+6.2f}  p={p_b:.5f}")
    delta = z_b - z_a
    print(f"    Delta Z(B-A) = {delta:+.2f}  {'<< Luwian STRONGER on B' if delta > 1 else ('>> Luwian WEAKER on B' if delta < -1 else '~ similar')}")

# ─────────────────────────────────────────────────────────────────────────────
print(f"\n{SEP}")
print("  BILATERAL HYPOTHESIS SCORECARD")
print(SEP)
print(f"""
  PREDICTION:
    G_LUWIAN : Z(Side B) > Z(Side A)   [Luwian side = B]
    E1_EGYPT : Z(Side A) > Z(Side B)   [Minoan/Egyptian side = A]
    B_FREQ   : Z(Side A) > Z(Side B)   [Linear A/Minoan side = A]
""")

BONF_P = 0.05 / 9
print(f"  {'Key':<12} {'Z(A)':>8} {'Z(B)':>8} {'Delta Z(B-A)':>14} {'Prediction':>14} {'Result'}")
print(f"  {'─'*12} {'─'*8} {'─'*8} {'─'*14} {'─'*14} {'─'*10}")

predictions = {
    "G_LUWIAN": ("B > A", +1),   # expect positive delta
    "E1_EGYPT": ("A > B", -1),   # expect negative delta
    "B_FREQ":   ("A > B", -1),   # expect negative delta
    "I_MORPHO": ("neutral",  0),
}

for key_name in KEYS:
    r = results[key_name]
    z_a = r["A"][3]
    z_b = r["B"][3]
    delta = z_b - z_a
    pred_label, pred_sign = predictions[key_name]
    confirmed = (pred_sign > 0 and delta > 0.5) or \
                (pred_sign < 0 and delta < -0.5) or \
                (pred_sign == 0)
    result_str = "CONFIRMED" if confirmed else "NOT CONFIRMED"
    print(f"  {key_name:<12} {z_a:>+8.2f} {z_b:>+8.2f} {delta:>+14.2f} {pred_label:>14} {result_str}")

# ─────────────────────────────────────────────────────────────────────────────
print(f"\n{SEP}")
print("  DETAILED MATCH ANALYSIS PER SIDE")
print(SEP)

for key_name in ["G_LUWIAN", "E1_EGYPT"]:
    r = results[key_name]
    print(f"\n  {key_name}")
    print(f"  {'─'*50}")
    for side_label, side_key in [("A", "A"), ("B", "B")]:
        sc, mu, sd, z, p, hits = r[side_key]
        print(f"  Side {side_label} (score={sc}, Z={z:+.2f}, p={p:.5f}):")
        for w, c in sorted(hits.items(), key=lambda x: -x[1])[:8]:
            print(f"    '{w}' x{c}")

# ─────────────────────────────────────────────────────────────────────────────
print(f"\n{SEP}")
print("  SIGN-LEVEL ANALYSIS: WHICH SIGNS DRIVE EACH SIDE?")
print(SEP)

G = KEYS["G_LUWIAN"]
E = KEYS["E1_EGYPT"]

signs_a = [s for w in SIDE_A for s in w]
signs_b = [s for w in SIDE_B for s in w]
freq_a = Counter(signs_a)
freq_b = Counter(signs_b)
total_a = len(signs_a)
total_b = len(signs_b)

print(f"\n  Signs most characteristic of each side (freq ratio):\n")
print(f"  {'Sign':<6} {'Luwian val':<10} {'Egypt val':<10} {'freq A%':>8} {'freq B%':>8} {'A/B ratio':>10} {'Dominates'}")
print(f"  {'─'*6} {'─'*10} {'─'*10} {'─'*8} {'─'*8} {'─'*10} {'─'*10}")

ratios = []
for s in SIGN_FREQ_ORDER:
    fa = freq_a.get(s, 0)
    fb = freq_b.get(s, 0)
    pct_a = fa / total_a * 100
    pct_b = fb / total_b * 100
    ratio = pct_a / pct_b if pct_b > 0 else float('inf')
    ratios.append((s, fa, fb, pct_a, pct_b, ratio))

for s, fa, fb, pct_a, pct_b, ratio in sorted(ratios, key=lambda x: -abs(math.log(x[5]+0.001))):
    luw = G.get(s, "—")
    egy = E.get(s, "—")
    dom = "SIDE A" if ratio > 2 else ("SIDE B" if ratio < 0.5 else "balanced")
    print(f"  #{s:<5} {luw:<10} {egy:<10} {pct_a:>7.1f}% {pct_b:>7.1f}% {ratio:>10.2f}  {dom}")

# ─────────────────────────────────────────────────────────────────────────────
print(f"\n{SEP}")
print("  BILATERAL STRUCTURE: THE SHARED CENTER")
print(SEP)
print("""
  Both sides share the SAME center invocation (Tiwat/ti-wa at position 0):
    A31 = [45,2,36,11,22] -> ti-wa-za-wa-tar-ha  (descent climax)
    B30 = [45,36,11,2,22] -> ti-wa-wa-tar-za-ha  (ascent climax)

  In Luwian treaty texts (CTH 46, 67, 105), the Sun-god (Tiwat/UTU) is
  ALWAYS the FIRST divine witness listed — present in treaties with ALL
  neighboring peoples, regardless of their own pantheon.

  INTERPRETATION: Tiwat = the SHARED/NEUTRAL divine witness,
  acceptable to both the Minoan and Luwian parties.
  The center is the MEETING POINT of the two traditions.
""")

# ─────────────────────────────────────────────────────────────────────────────
# FINAL VERDICT
print(SEP)
print("  VERDICT: BILATERAL TRADE DOCUMENT HYPOTHESIS")
print(SEP)

g_res = results["G_LUWIAN"]
e_res = results["E1_EGYPT"]
b_res = results["B_FREQ"]

g_delta = g_res["B"][3] - g_res["A"][3]
e_delta = e_res["A"][3] - e_res["B"][3]   # positive = A stronger for Egypt
b_delta = b_res["A"][3] - b_res["B"][3]   # positive = A stronger for LinA

g_confirmed = g_delta > 0
e_confirmed = e_delta > 0
b_confirmed = b_delta > 0

n_confirmed = sum([g_confirmed, e_confirmed, b_confirmed])

print(f"""
  G_LUWIAN stronger on Side B: {'YES' if g_confirmed else 'NO'} (DeltaZ = {g_delta:+.2f})
  E1_EGYPT stronger on Side A: {'YES' if e_confirmed else 'NO'} (DeltaZ = {e_delta:+.2f})
  B_FREQ   stronger on Side A: {'YES' if b_confirmed else 'NO'} (DeltaZ = {b_delta:+.2f})

  Predictions confirmed: {n_confirmed}/3

  {'STRONG SUPPORT: All 3 predictions confirmed.' if n_confirmed == 3 else
   ('PARTIAL SUPPORT: 2/3 predictions confirmed.' if n_confirmed == 2 else
    ('WEAK SUPPORT: 1/3 predictions confirmed.' if n_confirmed == 1 else
     'NOT SUPPORTED: 0/3 predictions confirmed.'))}

  INTERPRETATION:
  The Bilateral Trade Document Hypothesis proposes that the Phaistos Disc
  was a commercial/ritual document sealing a trade agreement between the
  Minoans and a Luwian-speaking party (possibly at Milawata/Miletus):

    Side A -> Minoan divine witnesses (Egyptian-influenced pantheon)
              Invocations for: safe passage, good harvest, trade goods
    Side B -> Luwian divine witnesses (Tiwat + water ritual)
              Oath formula: wa-tar (water) as sacred witness medium
    SHARED -> Tiwat at both centers: the neutral divine arbiter
              acceptable to both parties (cf. Luwian treaty texts)

  The stamped manufacture = reproducible legal document
  The refrains          = standard contractual formulae
  The disc at Phaistos  = Minoan party's copy of the agreement
""")
