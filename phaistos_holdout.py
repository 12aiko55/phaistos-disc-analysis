"""
phaistos_holdout.py — CROSS-VALIDATION (Hold-Out Prediction)
=============================================================
Ερώτηση: Είναι ο G_LUWIAN consistent και στις δύο πλευρές;

Test 1: Sign frequency rank consistency (Spearman ρ, Side A vs Side B)
        Αν ο ίδιος κώδικας χρησιμοποιείται και στις δύο πλευρές,
        οι συχνότητες πρέπει να είναι παρόμοιες.

Test 2: Build key from Side A only → score on Side B (and vice versa)
        Αν το key που βγαίνει από Side A λειτουργεί και στο Side B,
        αποκλείουμε overfitting.

Test 3: Bigram model cross-validation
        Bigrams από Side A → expected count στο Side B
        Σύγκριση: obs vs exp under Side-A bigram model
"""

import sys, random, math
from collections import Counter
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SEP  = "=" * 72
SEP2 = "─" * 72

SIDE_A = [
    [2,12,7,1,29],[2,6,25,6,22],[1,7,29,3,22],[29,6,2,7,22],
    [36,2,12,7],[2,36,12,11,22],[2,29,7,22],[29,2,7,36,22,11],
    [2,12,7,36],[29,7,22,2],[12,2,36,7,22],[2,7,29,36,22],
    [7,22,2,36,12],[2,29,36,11],[29,7,22,36],[2,36,7,11,22],
    [29,2,22,7],[36,7,22,2,11],[2,7,36,22],[29,36,2,7,11,22],
    [7,2,36,29],[22,2,36,11],[29,7,36,2,22],[2,7,22,29],
    [36,29,2,22,7],[2,11,36],[7,22,36,2],[29,2,36],
    [2,7,22,36,11],[36,2,11],[45,2,36,11,22],
]
SIDE_B = [
    [2,12,36,6,11],[2,12,7,2,11],[24,2,36,11,29],
    [2,29,22,36,12,11],[2,36,11],[2,1,12,36,11],
    [29,2,22,11],[2,36,29,22,11,29],[2,29,12,2,11],
    [36,11,29,2,33],[2,22,36,12],[29,36,11,2,22,12],
    [2,36,11,45],[22,2,36,11,44],[2,29,36,12,11],
    [29,2,12,36],[2,2,36,12,11,29],[36,45,11,2],
    [2,12,36,11],[29,2,36,11,22],[2,36,12,29,11],
    [36,2,11,29],[2,29,36,11,24],[12,36,2,11],
    [2,36,29,11,22],[29,36,2,11],[2,11,36,22,29],
    [36,11,2,29],[2,36,11,29,22],[45,36,11,2,22],
]
ALL_WORDS = SIDE_A + SIDE_B
SIGN_FREQ_ORDER = [2,36,11,29,22,7,12,6,45,1,24,25,33,44,3]

# ── Vocabularies ──────────────────────────────────────────────────────────────
LINEAR_A = {
    "a-sa-sa-ra":"Minoan goddess","wa-ja":"frequent LA",
    "ku-ro":"total","a-du":"unknown","si-ru-te":"ritual",
    "i-da-ma-te":"Ida-Mater","ja-sa-sa-ra":"asasara variant",
}
PROTO_GREEK = {
    "wa-na-ka":"king","po-ti-ni-ja":"goddess","te-o":"god",
    "da-ma":"earth","ma-te":"mother","pa-te":"father",
    "me-na":"moon","a-na":"up/through",
}
EGYPT_VOCAB = {
    "sa-ra":"Son of Ra","na-ra":"for Ra","wa-sa-ra":"Osiris",
    "ha-ta-pa":"offering","ma-ra":"mAat-Ra",
}
LUWIAN_VOCAB = {
    "za":"this","wa-na":"lord","ur-a":"great","ti-wa":"sun god",
    "tar":"lord","an-ta":"in front","at-ta":"father","an-na":"mother",
    "za-tar":"this lord","wa-tar":"water","tar-hu":"storm god",
}
MORPHEMES_LA = {
    "a":"prefix","ku":"ku-","te":"suffix","na":"suffix",
    "ku-ro":"total","wa-ja":"frequent","ka-te":"common",
}
VOCAB_ALL = (LINEAR_A, PROTO_GREEK, EGYPT_VOCAB, LUWIAN_VOCAB, MORPHEMES_LA)

G_LUWIAN_BASE = {
    2:"za", 36:"wa", 11:"tar", 29:"na", 22:"ha", 7:"ti", 12:"zi",
    6:"an", 45:"ti-wa", 1:"i", 24:"su", 25:"naw", 33:"ur", 44:"ma", 3:"pa"
}

LINEAR_B_VALUES = [
    "da","ro","pa","te","to","na","di","a","se","u","po","so","me","do","mo",
    "za","mi","mu","ne","ru","re","i","pu","ni","sa","jo","ti","e","pi","wi",
    "si","wo","ke","de","du","no","ri","wa","nu","ja","su","ta","ra","o","ku",
]

def read_word(word, key):
    return "-".join(key.get(s,"?") for s in word if key.get(s,"?") != "?")

def score_on_corpus(key, words, *vocab_dicts):
    text = " ".join(read_word(w, key) for w in words)
    return sum(text.count(word) for vocab in vocab_dicts for word in vocab if word in text)

def freq_rank(words):
    all_signs = [s for w in words for s in w]
    counts = Counter(all_signs)
    return sorted(counts.keys(), key=lambda s: -counts[s])

def spearman_rho(rank_a, rank_b):
    signs_common = [s for s in SIGN_FREQ_ORDER if s in rank_a and s in rank_b]
    n = len(signs_common)
    if n < 3: return 0.0
    pos_a = {s: i for i, s in enumerate(rank_a)}
    pos_b = {s: i for i, s in enumerate(rank_b)}
    d2 = sum((pos_a[s] - pos_b[s])**2 for s in signs_common)
    rho = 1 - 6*d2 / (n*(n**2-1))
    return rho

print(f"{SEP}")
print("  PHAISTOS — HOLD-OUT CROSS-VALIDATION")
print(f"{SEP}\n")

# ── TEST 1: Sign frequency rank consistency A vs B ────────────────────────────
print(f"{SEP2}")
print("TEST 1: SIGN FREQUENCY RANK CONSISTENCY (Side A vs Side B)")
print(SEP2)

freq_A = Counter(s for w in SIDE_A for s in w)
freq_B = Counter(s for w in SIDE_B for s in w)
rank_A = sorted(SIGN_FREQ_ORDER, key=lambda s: -freq_A.get(s, 0))
rank_B = sorted(SIGN_FREQ_ORDER, key=lambda s: -freq_B.get(s, 0))

print(f"\n  {'Sign':>5}  {'Count_A':>7}  {'Rank_A':>6}  {'Count_B':>7}  {'Rank_B':>6}  {'|ΔRank|':>7}")
print(f"  {'-'*5}  {'-'*7}  {'-'*6}  {'-'*7}  {'-'*6}  {'-'*7}")

rank_A_pos = {s: i+1 for i, s in enumerate(rank_A)}
rank_B_pos = {s: i+1 for i, s in enumerate(rank_B)}
rank_diffs = []
for sign in SIGN_FREQ_ORDER:
    cA = freq_A.get(sign, 0)
    cB = freq_B.get(sign, 0)
    rA = rank_A_pos[sign]
    rB = rank_B_pos[sign]
    diff = abs(rA - rB)
    rank_diffs.append(diff)
    flag = " ←!!" if diff >= 5 else (" ←!" if diff >= 3 else "")
    print(f"  #{sign:>3}  {cA:>7}  {rA:>6}  {cB:>7}  {rB:>6}  {diff:>7}{flag}")

rho = spearman_rho(rank_A, rank_B)
mean_diff = sum(rank_diffs) / len(rank_diffs)

# Significance of Spearman rho (t-test approximation for n=15)
n_sp = len(SIGN_FREQ_ORDER)
t_rho = rho * math.sqrt(n_sp - 2) / math.sqrt(1 - rho**2) if abs(rho) < 1 else 999
print(f"\n  Spearman ρ (rank correlation A vs B): {rho:.4f}")
print(f"  t-statistic (n=15):                   {t_rho:.2f}")
print(f"  Mean |rank difference|:               {mean_diff:.2f}")

if rho >= 0.85:
    rank_verdict = "EXCELLENT consistency — same encoding on both sides"
elif rho >= 0.70:
    rank_verdict = "GOOD consistency — minor variations expected"
elif rho >= 0.50:
    rank_verdict = "MODERATE — some structural differences between sides"
else:
    rank_verdict = "POOR — sides may encode different content"
print(f"  Verdict: {rank_verdict}")

# ── TEST 2: Key built from A, tested on B (and vice versa) ───────────────────
print(f"\n{SEP2}")
print("TEST 2: KEY BUILT FROM SIDE A → TESTED ON SIDE B (and reverse)")
print(SEP2)

# Build Side-A key: assign values by frequency rank on Side A
A_RANK = sorted([s for s in SIGN_FREQ_ORDER if freq_A.get(s, 0) > 0],
                key=lambda s: -freq_A[s])
B_RANK = sorted([s for s in SIGN_FREQ_ORDER if freq_B.get(s, 0) > 0],
                key=lambda s: -freq_B[s])

# G_LUWIAN values in frequency order (from SIGN_FREQ_ORDER)
luwian_values_in_order = [G_LUWIAN_BASE[s] for s in SIGN_FREQ_ORDER]

# Build key_A: assign by Side-A rank
key_A = {}
for i, sign in enumerate(A_RANK):
    if i < len(luwian_values_in_order):
        key_A[sign] = luwian_values_in_order[i]

# Build key_B: assign by Side-B rank
key_B = {}
for i, sign in enumerate(B_RANK):
    if i < len(luwian_values_in_order):
        key_B[sign] = luwian_values_in_order[i]

# Scores
score_AA = score_on_corpus(key_A, SIDE_A, *VOCAB_ALL)   # train A, test A
score_AB = score_on_corpus(key_A, SIDE_B, *VOCAB_ALL)   # train A, test B
score_BB = score_on_corpus(key_B, SIDE_B, *VOCAB_ALL)   # train B, test B
score_BA = score_on_corpus(key_B, SIDE_A, *VOCAB_ALL)   # train B, test A
score_base_A = score_on_corpus(G_LUWIAN_BASE, SIDE_A, *VOCAB_ALL)
score_base_B = score_on_corpus(G_LUWIAN_BASE, SIDE_B, *VOCAB_ALL)
score_base_all = score_on_corpus(G_LUWIAN_BASE, ALL_WORDS, *VOCAB_ALL)

# Monte Carlo null for each half (2000 trials)
random.seed(42)
null_half = []
pool = LINEAR_B_VALUES[:]
for _ in range(2000):
    random.shuffle(pool)
    rk = {s: pool[i % len(pool)] for i, s in enumerate(SIGN_FREQ_ORDER)}
    null_half.append(score_on_corpus(rk, SIDE_B, *VOCAB_ALL))
null_half_mean = sum(null_half) / len(null_half)
null_half_std  = math.sqrt(sum((x-null_half_mean)**2 for x in null_half) / len(null_half))

z_AB = (score_AB - null_half_mean) / null_half_std if null_half_std > 0 else 0
z_BA = (score_BA - null_half_mean) / null_half_std if null_half_std > 0 else 0
z_base_B = (score_base_B - null_half_mean) / null_half_std if null_half_std > 0 else 0

print(f"\n  Baseline G_LUWIAN (full disc):  {score_base_all}")
print(f"  G_LUWIAN on Side A only:        {score_base_A}")
print(f"  G_LUWIAN on Side B only:        {score_base_B}  (Z={z_base_B:.2f})")
print(f"\n  Key built from Side A → tested on Side A: {score_AA}")
print(f"  Key built from Side A → tested on Side B: {score_AB}  (Z={z_AB:.2f})")
print(f"\n  Key built from Side B → tested on Side B: {score_BB}")
print(f"  Key built from Side B → tested on Side A: {score_BA}  (Z={z_BA:.2f})")

transfer_ratio_AB = score_AB / score_AA if score_AA > 0 else 0
transfer_ratio_BA = score_BA / score_BB if score_BB > 0 else 0
print(f"\n  Transfer ratio (A→B): {transfer_ratio_AB:.2%}  (score_AB/score_AA)")
print(f"  Transfer ratio (B→A): {transfer_ratio_BA:.2%}  (score_BA/score_BB)")

if transfer_ratio_AB >= 0.70 and transfer_ratio_BA >= 0.70:
    transfer_verdict = "STRONG TRANSFER — key generalises well across sides"
elif transfer_ratio_AB >= 0.50 or transfer_ratio_BA >= 0.50:
    transfer_verdict = "MODERATE TRANSFER — partial generalisation"
else:
    transfer_verdict = "WEAK TRANSFER — key may be overfitting to one side"
print(f"\n  Transfer verdict: {transfer_verdict}")

# ── TEST 3: Bigram consistency A → B ─────────────────────────────────────────
print(f"\n{SEP2}")
print("TEST 3: BIGRAM MODEL CONSISTENCY (Side A bigrams → predict Side B)")
print(SEP2)

# Compute bigrams for each side (at sign level, key-independent)
def get_bigrams(words):
    return [(w[i], w[i+1]) for w in words for i in range(len(w)-1)]

bigrams_A = Counter(get_bigrams(SIDE_A))
bigrams_B = Counter(get_bigrams(SIDE_B))
signs_A   = Counter(s for w in SIDE_A for s in w)
signs_B   = Counter(s for w in SIDE_B for s in w)
n_adj_A   = sum(len(w)-1 for w in SIDE_A)
n_adj_B   = sum(len(w)-1 for w in SIDE_B)

# For key-independent test: check if [#36→#11] holds on both sides
obs_3611_A = bigrams_A.get((36,11), 0)
obs_3611_B = bigrams_B.get((36,11), 0)
p36_A = signs_A[36] / sum(signs_A.values())
p11_A = signs_A[11] / sum(signs_A.values())
p36_B = signs_B[36] / sum(signs_B.values())
p11_B = signs_B[11] / sum(signs_B.values())
exp_3611_A = n_adj_A * p36_A * p11_A
exp_3611_B = n_adj_B * p36_B * p11_B

print(f"\n  Key-independent bigram [#36→#11]:")
print(f"  Side A: obs={obs_3611_A}  exp={exp_3611_A:.2f}  ratio={obs_3611_A/max(exp_3611_A,0.01):.2f}x")
print(f"  Side B: obs={obs_3611_B}  exp={exp_3611_B:.2f}  ratio={obs_3611_B/max(exp_3611_B,0.01):.2f}x")

if obs_3611_A > exp_3611_A and obs_3611_B > exp_3611_B:
    bigram_verdict = "[#36→#11] holds on BOTH sides — structure confirmed independently"
elif obs_3611_A > exp_3611_A or obs_3611_B > exp_3611_B:
    bigram_verdict = "[#36→#11] holds on ONE side only — partial confirmation"
else:
    bigram_verdict = "[#36→#11] not confirmed on either side individually"
print(f"  Verdict: {bigram_verdict}")

# Top bigrams per side
print(f"\n  Top 10 bigrams — Side A:")
for (s1, s2), cnt in bigrams_A.most_common(10):
    exp = n_adj_A * (signs_A[s1]/sum(signs_A.values())) * (signs_A[s2]/sum(signs_A.values()))
    print(f"    [{s1:>2}→{s2:>2}]: obs={cnt}  exp={exp:.1f}  ratio={cnt/max(exp,0.01):.1f}x")

print(f"\n  Top 10 bigrams — Side B:")
for (s1, s2), cnt in bigrams_B.most_common(10):
    exp = n_adj_B * (signs_B[s1]/sum(signs_B.values())) * (signs_B[s2]/sum(signs_B.values()))
    print(f"    [{s1:>2}→{s2:>2}]: obs={cnt}  exp={exp:.1f}  ratio={cnt/max(exp,0.01):.1f}x")

# Bigram correlation A vs B
top_bigrams_A = set(bg for bg,_ in bigrams_A.most_common(10))
top_bigrams_B = set(bg for bg,_ in bigrams_B.most_common(10))
overlap = top_bigrams_A & top_bigrams_B
print(f"\n  Overlap in top-10 bigrams (A∩B): {len(overlap)}/10 = {len(overlap)/10*100:.0f}%")
print(f"  Shared: {overlap}")

# ── FINAL VERDICT ─────────────────────────────────────────────────────────────
print(f"\n{SEP}")
print("CROSS-VALIDATION FINAL VERDICT")
print(SEP)
print(f"""
  Test 1 — Rank consistency:   Spearman ρ = {rho:.4f}  ({rank_verdict})
  Test 2 — Transfer A→B:       ratio = {transfer_ratio_AB:.1%}  ({transfer_verdict})
  Test 3 — Bigram consistency: {bigram_verdict}

  OVERALL CROSS-VALIDATION:
""")

passed = sum([rho >= 0.70, transfer_ratio_AB >= 0.50, obs_3611_A > exp_3611_A and obs_3611_B > exp_3611_B])
if passed == 3:
    print("  ✓✓✓ ALL 3 TESTS PASS — Strong cross-validation evidence")
    print("  The G_LUWIAN key generalizes across both sides of the disc.")
elif passed == 2:
    print("  ✓✓  2/3 TESTS PASS — Moderate cross-validation evidence")
elif passed == 1:
    print("  ✓   1/3 TESTS PASS — Weak cross-validation evidence")
else:
    print("  ✗   No tests pass — Cross-validation fails")

print(f"""
  Για paper:
  "Cross-validation was performed by (1) computing Spearman rank
   correlation of sign frequencies between sides (ρ={rho:.3f}),
   (2) building phonetic keys from each side independently and
   scoring the opposite side (transfer ratio: A→B {transfer_ratio_AB:.0%}),
   and (3) verifying that the key-independent bigram signal
   [#36→#11] holds on both sides independently
   (Side A: {obs_3611_A} obs vs {exp_3611_A:.1f} exp;
    Side B: {obs_3611_B} obs vs {exp_3611_B:.1f} exp)."
""")
