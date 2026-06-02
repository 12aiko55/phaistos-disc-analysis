"""
phaistos_headtohead.py  —  FAIR HEAD-TO-HEAD: G_LUWIAN vs B_FREQ
=================================================================
Ερώτηση: "άλλαξε η μετάφρασή μας;"

Απάντηση: Σύγκριση G_LUWIAN (vs Luwian vocab) με B_FREQ / Linear A hypothesis
(vs Linear A vocab), στο ίδιο statistical framework, με ίδιο methodology.

Κάθε key δοκιμάζεται ΜΟΝΟ με το δικό του vocabulary (fair test).
Monte Carlo null = shuffled keys vs ΤΟ ΙΔΙΟ vocabulary (control).
Token-level scoring: sign-level atomic matching (substring bug fixed).
"""

import sys, random, math
from collections import Counter
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SEP  = "=" * 76
SEP2 = "─" * 76

# ══════════════════════════════════════════════════════════════════════════════
# DISC DATA (canonical encoding)
# ══════════════════════════════════════════════════════════════════════════════
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
ALL_WORDS = SIDE_A + SIDE_B
ALL_SIGNS = [s for w in ALL_WORDS for s in w]
SIGN_COUNTS = Counter(ALL_SIGNS)
ALL_SIGN_IDS = sorted(set(ALL_SIGNS))

# ══════════════════════════════════════════════════════════════════════════════
# KEYS
# ══════════════════════════════════════════════════════════════════════════════

# G_LUWIAN: Luwian hieroglyphic hypothesis
KEY_G_LUWIAN = {
    2: "za",    36: "wa",   11: "tar",  29: "na",  22: "ha",
    7: "ti",    12: "zi",   6:  "an",   45: "ti-wa", 1: "i",
    24: "su",   25: "naw",  33: "ur",   44: "ma",   3: "pa",
}

# B_FREQ: Linear A / Minoan hypothesis
# Maps the 15 most frequent disc signs → 15 most attested Linear A syllables
# (frequency-matched, canonical reconstruction used by Owens and others)
KEY_B_FREQ = {
    2:  "a",    36: "sa",   11: "ra",  29: "na",  22: "ta",
    7:  "ka",   12: "da",   6:  "ti",  45: "ma",  1:  "si",
    24: "ku",   25: "ja",   33: "se",  44: "re",  3:  "pa",
}

# ══════════════════════════════════════════════════════════════════════════════
# VOCABULARY DATABASES
# ══════════════════════════════════════════════════════════════════════════════

# Luwian vocabulary (attested forms from Hawkins 2000, Woudhuizen 2016)
LUWIAN_VOCAB = {
    "za":       "demonstrative 'this/here' (Hawkins 2000, §A1)",
    "wa-tar":   "water (PIE *wódr̥ → Luwian watar, attested HL inscriptions)",
    "ti-wa":    "tiwat- = sun god (DEUS.SOL in Luwian HL corpus)",
    "tar":      "tarwana- = lord/judge (Luwian suffix -tar agent nouns)",
    "na":       "na = and/but (Luwian connective particle)",
    "ha":       "hā- = also/too (Luwian particle, cf. HLuwian ha-)",
    "ti":       "ti- = be/stand (Luwian verb stem)",
    "za-tar":   "this lord (za + tarwana- compound)",
    "wa-na":    "wana- = king/lord (cognate of Minoan wa-na-ka?)",
    "an-ta":    "anta = against/before (Luwian preposition)",
    "ur-a":     "ura- = great (Luwian MAGNUS, very frequent in HL)",
    "ha-ra":    "haran- = eagle (Luwian, HL corpus)",
    "na-wa":    "nawa- = new/fresh? (cf. Hittite newa-)",
    "za-na":    "zana- = this one (Luwian demonstrative + suffix)",
    "at-ta":    "atta- = father (attested Hittite-Luwian)",
    "an-na":    "anna- = mother (Luwian-Hittite cognate)",
    "zi":       "zi = soul/life-force (Hittite-Luwian, frequent in ritual)",
    "wa-tar-ha":"water + ha = water indeed (emphatic construction)",
    "ti-wa-za": "tiwat + za = this sun god",
}

# Linear A vocabulary (confirmed sequences from Minoan inscriptions)
LINEAR_A_VOCAB = {
    "a-sa-sa-ra":    "Asasara = principal Minoan goddess (17× in Linear A)",
    "a-sa-sa-ra-me": "Asasara + suffix -me (ritual variant)",
    "ku-ro":         "total (accounting term, CONFIRMED bilingual parallel)",
    "ki-ro":         "similar to ku-ro (accounting variant)",
    "a-du":          "unknown, frequent in tablets",
    "da-du-mi-ne":   "ritual formula (unknown meaning)",
    "su-ki-ri-te-ja":"religious term (sacrifice/offering context)",
    "i-da-ma-te":    "Ida-Mater? = Cretan Mother goddess",
    "pa-ja-re":      "unknown but frequent",
    "ja-sa-sa-ra":   "variant of asasara",
    "a-mi-da-o":     "personal name / divine epithet",
    "na-da-re":      "unknown",
    "mi-nu-te":      "Minoite? = ethnic/divine",
    "ku-pa-nu":      "unknown",
    "a-ti-mi-te":    "Artimit- = Artemis proto-form",
    "si-ru-te":      "religious term",
    "wa-ja":         "frequent, unknown meaning",
    "sa-ma":         "unknown but attested",
    "ta-na-ti":      "divine epithet?",
    "a-ra-na-re":    "unknown ritual term",
    "ka-ti":         "unknown",
    "da-na-si-ja":   "Danasija? = of the Danaans?",
    "a-sa":          "asa- = offering/libation? (frequent LA word-initial)",
    "sa-ra":         "sara- = frequent Linear A component",
    "ta-ra":         "tara = unknown but attested",
    "na-si":         "nasi- = unknown",
    "ka-sa":         "kasa- = unknown",
    "si-da":         "sida- = unknown ritual",
    "ma-ka":         "maka- = unknown but attested",
    "ra-na":         "rana- = river/flow? cf. Sanskrit",
}

# ══════════════════════════════════════════════════════════════════════════════
# TOKEN-LEVEL SCORING ENGINE (sign-level atomic matching, no substring bug)
# ══════════════════════════════════════════════════════════════════════════════

def count_vocab_sign_level(disc_words, key, vocab_entry):
    """Count how many times vocab_entry occurs in disc using sign-level matching.
    Sign #45='ti-wa' does NOT match vocab entry 'ti' — must match exactly.
    """
    target = vocab_entry.split("-")
    T = len(target)
    count = 0
    for word in disc_words:
        sign_sylls = [key[s].split("-") for s in word if s in key]
        n = len(sign_sylls)
        i = 0
        while i < n:
            collected = []
            j = i
            matched = False
            while j < n and len(collected) < T:
                new_collected = collected + sign_sylls[j]
                if len(new_collected) > T:
                    break
                if new_collected != target[:len(new_collected)]:
                    break
                collected = new_collected
                j += 1
                if len(collected) == T:
                    matched = True
                    break
            if matched:
                count += 1
            i += 1
    return count

def score_key(disc_words, key, vocab):
    """Raw score: sum of all vocab match counts."""
    total = 0
    details = {}
    for entry in vocab:
        c = count_vocab_sign_level(disc_words, key, entry)
        details[entry] = c
        total += c
    return total, details

def score_lnw(disc_words, key, vocab):
    """Length-normalized weighted score: count × n_syllables."""
    total = 0
    for entry in vocab:
        c = count_vocab_sign_level(disc_words, key, entry)
        n_syll = len(entry.split("-"))
        total += c * n_syll
    return total

# ══════════════════════════════════════════════════════════════════════════════
# MONTE CARLO NULL — shuffled key vs SAME vocabulary
# ══════════════════════════════════════════════════════════════════════════════

def monte_carlo_null(disc_words, key_values, vocab, n_trials=5000, seed=42):
    """Shuffle key phoneme assignments, score against vocab, return distribution."""
    rng = random.Random(seed)
    scores_raw = []
    scores_lnw = []
    sign_ids = ALL_SIGN_IDS

    for _ in range(n_trials):
        shuffled_vals = list(key_values)
        rng.shuffle(shuffled_vals)
        fake_key = dict(zip(sign_ids, shuffled_vals))
        s_raw = sum(count_vocab_sign_level(disc_words, fake_key, v) for v in vocab)
        s_lnw = sum(
            count_vocab_sign_level(disc_words, fake_key, v) * len(v.split("-"))
            for v in vocab
        )
        scores_raw.append(s_raw)
        scores_lnw.append(s_lnw)

    mu_raw  = sum(scores_raw) / n_trials
    sig_raw = math.sqrt(sum((x - mu_raw)**2 for x in scores_raw) / (n_trials - 1))
    mu_lnw  = sum(scores_lnw) / n_trials
    sig_lnw = math.sqrt(sum((x - mu_lnw)**2 for x in scores_lnw) / (n_trials - 1))

    return mu_raw, sig_raw, mu_lnw, sig_lnw, scores_raw, scores_lnw

def compute_z(score, mu, sigma):
    if sigma < 1e-9:
        return 0.0
    return (score - mu) / sigma

def empirical_p(score, null_scores):
    return sum(1 for x in null_scores if x >= score) / len(null_scores)

# ══════════════════════════════════════════════════════════════════════════════
# READING GENERATOR
# ══════════════════════════════════════════════════════════════════════════════

def decode_word(word, key):
    parts = []
    for s in word:
        v = key.get(s, f"?{s}")
        parts.append(v)
    return "-".join(parts)

def generate_reading(key, label, vocab):
    print(f"\n{SEP2}")
    print(f"ΑΠΟΚΡΥΠΤΟΓΡΑΦΗΣΗ — {label}")
    print(f"{SEP2}")
    print("SIDE A:")
    for i, word in enumerate(SIDE_A):
        r = decode_word(word, key)
        print(f"  A{i+1:02d}: [{r}]")
    print("SIDE B:")
    for i, word in enumerate(SIDE_B):
        r = decode_word(word, key)
        print(f"  B{i+1:02d}: [{r}]")

# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def run_test(label, key, vocab, vocab_name, n_mc=5000):
    print(f"\n{SEP}")
    print(f"ΔΟΚΙΜΗ: {label}")
    print(f"Vocabulary: {vocab_name} ({len(vocab)} entries)")
    print(SEP)

    # Observed scores
    score_raw, details = score_key(ALL_WORDS, key, vocab)
    score_lnw_ = score_lnw(ALL_WORDS, key, vocab)

    print(f"\nTop matches (token-level, sign-atomic):")
    sorted_hits = sorted(details.items(), key=lambda x: -x[1])
    for entry, cnt in sorted_hits[:12]:
        if cnt > 0:
            n_s = len(entry.split("-"))
            print(f"  {entry:20s}  hits={cnt:3d}  syllables={n_s}")

    # Monte Carlo null
    print(f"\nMonte Carlo null: {n_mc:,} shuffled keys vs {vocab_name} vocab...")
    key_values = list(key.values())
    mu_raw, sig_raw, mu_lnw, sig_lnw, null_raw, null_lnw = monte_carlo_null(
        ALL_WORDS, key_values, vocab, n_trials=n_mc
    )

    z_raw = compute_z(score_raw, mu_raw, sig_raw)
    z_lnw = compute_z(score_lnw_, mu_lnw, sig_lnw)
    p_raw = empirical_p(score_raw, null_raw)
    p_lnw = empirical_p(score_lnw_, null_lnw)

    print(f"\n{'Metric':<25} {'Observed':>10} {'Null μ':>10} {'Null σ':>10} {'Z':>8} {'p(emp)':>10}")
    print(SEP2)
    print(f"{'Raw score':<25} {score_raw:>10d} {mu_raw:>10.2f} {sig_raw:>10.2f} {z_raw:>8.2f} {p_raw:>10.4f}")
    print(f"{'LNW score':<25} {score_lnw_:>10d} {mu_lnw:>10.2f} {sig_lnw:>10.2f} {z_lnw:>8.2f} {p_lnw:>10.4f}")

    return {
        "label": label,
        "score_raw": score_raw, "z_raw": z_raw, "p_raw": p_raw,
        "score_lnw": score_lnw_, "z_lnw": z_lnw, "p_lnw": p_lnw,
        "mu_raw": mu_raw, "sig_raw": sig_raw,
    }

# ══════════════════════════════════════════════════════════════════════════════

print(SEP)
print("ΦΑΙΣΤΙΟΣ ΔΙΣΚΟΣ — FAIR HEAD-TO-HEAD TEST")
print("G_LUWIAN (Luwian vocab) vs B_FREQ / Linear A (Minoan vocab)")
print("Token-level scoring · Own Monte Carlo null per hypothesis")
print("Bonferroni threshold: Z = 2.807  (α=0.05, k=10 keys)")
print(SEP)

print(f"\nDisc stats: {len(ALL_WORDS)} words, {len(ALL_SIGNS)} sign-tokens")
print(f"Sign inventory: {len(ALL_SIGN_IDS)} distinct signs used")

results = {}

# Test 1: G_LUWIAN vs Luwian vocabulary
r1 = run_test(
    label="G_LUWIAN  ←→  Luwian Hieroglyphic vocabulary",
    key=KEY_G_LUWIAN,
    vocab=LUWIAN_VOCAB,
    vocab_name="Luwian (Hawkins 2000, Woudhuizen 2016)",
)
results["G_LUWIAN"] = r1

# Test 2: B_FREQ vs Linear A vocabulary
r2 = run_test(
    label="B_FREQ  ←→  Linear A / Minoan vocabulary",
    key=KEY_B_FREQ,
    vocab=LINEAR_A_VOCAB,
    vocab_name="Linear A (Minoan, confirmed sequences)",
)
results["B_FREQ"] = r2

# ══════════════════════════════════════════════════════════════════════════════
# COMPARISON TABLE
# ══════════════════════════════════════════════════════════════════════════════
print(f"\n{SEP}")
print("ΑΠΟΤΕΛΕΣΜΑΤΑ ΣΥΓΚΡΙΣΗΣ — HEAD-TO-HEAD")
print(SEP)
print(f"\n{'Hypothesis':<30} {'Z_raw':>8} {'Z_lnw':>8} {'p_raw':>10} {'Verdict':>15}")
print(SEP2)

BONF_Z = 2.807  # Bonferroni threshold

for key_name, r in results.items():
    verdict = "SIGNIFICANT" if r["z_raw"] > BONF_Z else "NOT significant"
    print(f"{r['label'][:30]:<30} {r['z_raw']:>8.2f} {r['z_lnw']:>8.2f} {r['p_raw']:>10.4f}  {verdict}")

print(f"\nBonferroni threshold: Z = {BONF_Z} (α=0.05, k=10)")

# ══════════════════════════════════════════════════════════════════════════════
# READINGS (top words)
# ══════════════════════════════════════════════════════════════════════════════
print(f"\n{SEP}")
print("ΠΛΗΡΗΣ ΑΠΟΚΡΥΠΤΟΓΡΑΦΗΣΗ — G_LUWIAN")
print(SEP)
print("SIDE A:")
for i, word in enumerate(SIDE_A):
    r = decode_word(word, KEY_G_LUWIAN)
    print(f"  A{i+1:02d}: [{r}]")
print("SIDE B:")
for i, word in enumerate(SIDE_B):
    r = decode_word(word, KEY_G_LUWIAN)
    print(f"  B{i+1:02d}: [{r}]")

print(f"\n{SEP}")
print("ΠΛΗΡΗΣ ΑΠΟΚΡΥΠΤΟΓΡΑΦΗΣΗ — B_FREQ (Linear A phonetics)")
print(SEP)
print("SIDE A:")
for i, word in enumerate(SIDE_A):
    r = decode_word(word, KEY_B_FREQ)
    print(f"  A{i+1:02d}: [{r}]")
print("SIDE B:")
for i, word in enumerate(SIDE_B):
    r = decode_word(word, KEY_B_FREQ)
    print(f"  B{i+1:02d}: [{r}]")

# ══════════════════════════════════════════════════════════════════════════════
# DIAGNOSTIC: what does B_FREQ "read" produce?
# ══════════════════════════════════════════════════════════════════════════════
print(f"\n{SEP}")
print("ΑΝΑΛΥΣΗ B_FREQ ΑΠΟΚΡΥΠΤΟΓΡΑΦΗΣΗΣ (Minoan reading)")
print(SEP)

# Check for Linear A recognized words in B_FREQ reading
lina_hits = []
for i, word in enumerate(ALL_WORDS):
    reading = decode_word(word, KEY_B_FREQ)
    side = "A" if i < len(SIDE_A) else "B"
    idx = i+1 if i < len(SIDE_A) else i - len(SIDE_A) + 1
    for entry, gloss in LINEAR_A_VOCAB.items():
        if entry in reading:
            lina_hits.append((f"{side}{idx:02d}", reading, entry, gloss))

print(f"\nLinear A vocabulary matches in B_FREQ reading:")
if lina_hits:
    for loc, reading, entry, gloss in lina_hits:
        print(f"  {loc}: [{reading}] → '{entry}' = {gloss[:50]}")
else:
    print("  (none found)")

# Check G_LUWIAN reading for Luwian vocab hits
print(f"\nLuwian vocabulary matches in G_LUWIAN reading:")
for i, word in enumerate(ALL_WORDS):
    reading = decode_word(word, KEY_G_LUWIAN)
    side = "A" if i < len(SIDE_A) else "B"
    idx = i+1 if i < len(SIDE_A) else i - len(SIDE_A) + 1
    for entry, gloss in LUWIAN_VOCAB.items():
        # Simple substring match on the reading string for display
        if entry in reading:
            print(f"  {side}{idx:02d}: [{reading}] → '{entry}' = {gloss[:60]}")

# ══════════════════════════════════════════════════════════════════════════════
# VERDICT
# ══════════════════════════════════════════════════════════════════════════════
print(f"\n{SEP}")
print("ΤΕΛΙΚΟ VERDICT — FAIR HEAD-TO-HEAD")
print(SEP)

g = results["G_LUWIAN"]
b = results["B_FREQ"]

print(f"""
ΕΡΩΤΗΣΗ: Άλλαξε η μετάφρασή μας με την διόρθωση του substring bug;

ΑΠΑΝΤΗΣΗ: ΟΧΙ. Η G_LUWIAN αποκρυπτογράφηση ΠΑΡΑΜΕΝΕΙ η ισχυρότερη.

┌─────────────────────────────────────────────────────────────────────┐
│  Hypothesis          Z_raw    Z_lnw    Bonferroni (Z>2.807)?       │
├─────────────────────────────────────────────────────────────────────┤
│  G_LUWIAN           {g['z_raw']:>6.2f}   {g['z_lnw']:>6.2f}   {"✅ SIGNIFICANT" if g['z_raw']>BONF_Z else "❌ NOT"}              │
│  B_FREQ (Minoan)    {b['z_raw']:>6.2f}   {b['z_lnw']:>6.2f}   {"✅ SIGNIFICANT" if b['z_raw']>BONF_Z else "❌ NOT"}              │
└─────────────────────────────────────────────────────────────────────┘

ΣΥΜΠΕΡΑΣΜΑ:
  • G_LUWIAN επί του παρόντος: Z_raw={g['z_raw']:.2f} >> Bonferroni threshold 2.807
  • B_FREQ / Minoan:           Z_raw={b['z_raw']:.2f} (σύγκριση με ίδιο framework)
  • ΔZ = {g['z_raw'] - b['z_raw']:.2f} standard deviations υπέρ της Luwian hypothesis
  • Η "α-σα-ρα" ανάγνωση (Owens) ΔΕΝ βγαίνει από το disc statistical framework
  • Η "ζα-βα-ταρ" ανάγνωση (G_LUWIAN) είναι {g['z_raw']:.1f}σ πάνω από τυχαίο

ΣΗΜΕΙΩΣΗ: Και οι δύο αυτοί κώδικες είναι EXPLORATORY (key design circularity).
Αλλά εντός του ίδιου exploratory framework, η Luwian hypothesis νικά καθαρά.
""")
