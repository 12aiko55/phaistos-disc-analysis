"""
ablation_watar_test.py
======================
HONEST ABLATION: What happens if we remove wa-tar from everything?

CRITIQUE: "Almost all semantic content rests on wa-tar, Tiwat, za.
If these three fall, the hymn narrative collapses."

TEST: Systematically remove wa-tar (and za-wa-tar, ha-tar) from the
scoring vocabulary, then re-run:
  (A) G_LUWIAN score with/without wa-tar
  (B) Blind corpus key test WITHOUT wa-tar (200,000 trials)
  (C) What vocabulary IS left — is G_LUWIAN still significant?

If G_LUWIAN still beats the null without wa-tar → result is robust.
If it collapses → honest acknowledgment that wa-tar is load-bearing.
"""

import sys, os, re, math, random
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
random.seed(42)

CORPUS_BASE = r"C:\Users\Manos\Downloads\phaistos-disc-analysis\TLHdig_corpus\TLHbasisONLINE25.1_ZENODO"
SEP = "=" * 70

G_LUWIAN_KEY = {
    36:"wa", 11:"tar", 2:"za", 22:"ha", 7:"ti",
    29:"na", 6:"an", 12:"zi", 45:"ti-wa", 1:"i",
}

DISC_ACHTERBERG = [
    [2,12,13,1,18],   [2,6,29,14,25,22,22], [1,22,29,6,11,22],
    [29,6,2,22,7],    [36,2,12,7],           [2,36,12,22,11,22],
    [2,29,7,22],      [29,2,7,36,22,11],     [2,12,7,36],
    [29,7,22,2],      [12,2,36,7,22],        [2,7,29,36,22],
    [7,22,2,36,12],   [2,29,36,11],          [29,7,22,36],
    [2,36,7,11,22],   [29,2,22,7],           [36,7,22,2,11],
    [2,7,36,22],      [29,36,2,7,11,22],     [7,2,36,29],
    [22,2,36,11],     [29,7,36,2,22],        [2,7,22,29],
    [36,29,2,22,7],   [2,11,36],             [7,22,36,2],
    [29,2,36],        [2,7,22,36,11],        [36,2,11],
    [45,2,36,11,22],
    [2,12,22,40,7],   [27,45,7,35],          [2,37,23,5],
    [22,25,27],       [33,24,20,12],         [16,23,18,43],
    [13,1,39,33],     [15,7,13,1,18],        [22,37,42,25],
    [7,24,40,35],     [2,26,36,40],          [27,25,38,1],
    [29,24,24,20,35], [16,14,18],            [29,33,1],
    [6,35,32,39,33],  [2,9,27,1],            [29,36,7,8],
    [29,8,13],        [29,45,7],             [22,29,36,7,8],
    [27,34,23,25],    [7,18,35],             [7,45,7],
    [7,23,18,24],     [22,29,36,7,8],        [9,30,39,18,7],
    [2,6,35,23,7],    [29,34,23,25],         [45,36,11,2,22],
]

# ── FULL vocabulary (with wa-tar)
VOCAB_FULL = {
    "wa-tar":4, "tar-na":3, "za-wa-tar":5, "ti-wa":4, "wa-na":3,
    "na-wa":3,  "ha-tar":3, "za-na":2,     "za-an":2, "na-ha":2,
    "tar":2,    "wa":1,     "za":1,         "ha":1,    "ti":1,
    "na":1,     "an":1,     "zi":1,         "i":1,
}

# ── ABLATED vocabulary (wa-tar compounds REMOVED)
VOCAB_ABLATED = {
    k: v for k, v in VOCAB_FULL.items()
    if k not in ("wa-tar", "za-wa-tar", "ha-tar")
}

def score_key(key, words, vocab):
    total = 0
    for word in words:
        syls = [key.get(s) for s in word if key.get(s)]
        text = '-'.join(syls)
        for voc, w in vocab.items():
            if voc in text:
                total += w
    return total

# ─────────────────────────────────────────────────────────────────────────────
# STEP 1 — Score G_LUWIAN with and without wa-tar
# ─────────────────────────────────────────────────────────────────────────────
score_full    = score_key(G_LUWIAN_KEY, DISC_ACHTERBERG, VOCAB_FULL)
score_ablated = score_key(G_LUWIAN_KEY, DISC_ACHTERBERG, VOCAB_ABLATED)

print(SEP)
print("  ABLATION TEST: Remove wa-tar — does G_LUWIAN collapse?")
print(SEP)
print()
print(f"  Vocabulary REMOVED in ablation:")
for k in ("wa-tar", "za-wa-tar", "ha-tar"):
    print(f"    '{k}' (weight {VOCAB_FULL[k]}) — removed")
print()
print(f"  Vocabulary KEPT (non-wa-tar attested Luwian):")
for k, v in VOCAB_ABLATED.items():
    print(f"    '{k}' (weight {v})")
print()
print(f"  G_LUWIAN score FULL      : {score_full}")
print(f"  G_LUWIAN score ABLATED   : {score_ablated}")
print(f"  Score drop from ablation : -{score_full - score_ablated} ({100*(score_full-score_ablated)/score_full:.0f}% of total)")

# ── Show per-word contribution breakdown ─────────────────────────────────────
print(f"\n  Per-word score breakdown (FULL vs ABLATED):")
print(f"  {'Word':<5} {'Signs':<25} {'Reading':<30} {'Full':>5} {'Abl.':>5}")
print(f"  {'─'*75}")
for i, word in enumerate(DISC_ACHTERBERG[:31], 1):  # Side A
    syls = [G_LUWIAN_KEY.get(s) for s in word if G_LUWIAN_KEY.get(s)]
    text = '-'.join(syls)
    sf = sum(w for voc, w in VOCAB_FULL.items() if voc in text)
    sa = sum(w for voc, w in VOCAB_ABLATED.items() if voc in text)
    if sf > 0 or sa > 0:
        signs_str = str(word)[:24]
        print(f"  A{i:<4} {signs_str:<25} {text[:29]:<30} {sf:>5} {sa:>5}")

# ─────────────────────────────────────────────────────────────────────────────
# STEP 2 — Blind corpus test WITHOUT wa-tar (200,000 trials)
# ─────────────────────────────────────────────────────────────────────────────
print(f"\n{SEP}")
print(f"  BLIND CORPUS TEST — ABLATED VOCABULARY (no wa-tar)")
print(f"  Same 200,000 corpus-seeded random assignments, scored without wa-tar")
print(SEP)

# Extract corpus syllable pool
corp_freq = Counter()
word_re   = re.compile(r'<w>(.*?)</w>')
xml_tag   = re.compile(r'<[^>]+>')

print(f"\n  Extracting TLHdig corpus...")
for root, _, fnames in os.walk(CORPUS_BASE):
    for fn in fnames:
        if not fn.endswith('.xml'): continue
        try:
            txt = open(os.path.join(root, fn), encoding='utf-8', errors='replace').read()
        except: continue
        if 'lg="Luw"' not in txt: continue
        for raw in txt.split('\n'):
            if 'lg="Luw"' not in raw: continue
            for wr in word_re.findall(raw):
                w = xml_tag.sub('', wr).strip()
                for part in w.lower().split('-'):
                    part = part.strip()
                    if len(part) >= 2 and not part.startswith('x'):
                        corp_freq[part] += 1

pool = [m for m, _ in corp_freq.most_common(50) if len(m) >= 2]

all_tokens = [s for w in DISC_ACHTERBERG for s in w]
sign_freq  = Counter(all_tokens)
top10_signs = [s for s, _ in sign_freq.most_common(10)]

print(f"  Running 200,000 trials with ABLATED vocabulary...")
N_TRIALS = 200_000
scores_abl = []
n_ge_abl   = 0

for _ in range(N_TRIALS):
    sample     = random.sample(pool, 10)
    assignment = dict(zip(top10_signs, sample))
    s = score_key(assignment, DISC_ACHTERBERG, VOCAB_ABLATED)
    scores_abl.append(s)
    if s >= score_ablated:
        n_ge_abl += 1

scores_abl.sort()
mu_abl  = sum(scores_abl) / N_TRIALS
sd_abl  = math.sqrt(sum((s - mu_abl)**2 for s in scores_abl) / N_TRIALS)
p_abl   = n_ge_abl / N_TRIALS
z_abl   = (score_ablated - mu_abl) / max(sd_abl, 1e-9)
p95_abl = scores_abl[int(0.95*N_TRIALS)]
p99_abl = scores_abl[int(0.99*N_TRIALS)]

print(f"\n  ABLATED RESULTS (no wa-tar in scoring):")
print(f"  {'─'*50}")
print(f"  G_LUWIAN ablated score       : {score_ablated}")
print(f"  Null mean ± std              : {mu_abl:.1f} ± {sd_abl:.1f}")
print(f"  Null p95 / p99               : {p95_abl} / {p99_abl}")
print(f"  Z-score vs null              : {z_abl:+.2f}")
print(f"  Trials ≥ ablated score       : {n_ge_abl} / {N_TRIALS}")
print(f"  Empirical p (ablated)        : {p_abl:.6f}")

# ─────────────────────────────────────────────────────────────────────────────
# STEP 3 — Also test with ONLY wa-tar (what does wa-tar contribute alone?)
# ─────────────────────────────────────────────────────────────────────────────
VOCAB_ONLY_WATAR = {k: v for k, v in VOCAB_FULL.items()
                    if k in ("wa-tar", "za-wa-tar", "ha-tar")}

score_watar_only = score_key(G_LUWIAN_KEY, DISC_ACHTERBERG, VOCAB_ONLY_WATAR)
print(f"\n  Score from wa-tar compounds ONLY : {score_watar_only}")
print(f"  Score from everything ELSE       : {score_ablated}")
print(f"  Total (check = full score)       : {score_watar_only + score_ablated} (full={score_full})")

# ─────────────────────────────────────────────────────────────────────────────
# VERDICT
# ─────────────────────────────────────────────────────────────────────────────
print(f"\n{SEP}")
print(f"  HONEST VERDICT — wa-tar Ablation")
print(SEP)
print()
print(f"  FULL model:    score={score_full}, blind-corpus p<0.000005, Z=+8.53")
print(f"  ABLATED model: score={score_ablated}, blind-corpus p={p_abl:.6f}, Z={z_abl:+.2f}")
print()
watar_pct = 100*(score_full - score_ablated)/score_full
print(f"  wa-tar load-bearing fraction: {watar_pct:.0f}% of total score")
print()

if z_abl >= 3.0 and p_abl < 0.01:
    print(f"  ✓ ROBUST: G_LUWIAN remains significant WITHOUT wa-tar.")
    print(f"    Z={z_abl:+.2f} even after removing the wa-tar compounds.")
    print(f"    The result is NOT purely wa-tar driven.")
    print(f"    The non-water vocabulary (ti-wa, za, na, an, ti, zi) independently")
    print(f"    supports the Luwian hypothesis.")
elif z_abl >= 2.0:
    print(f"  ~ MARGINAL: G_LUWIAN weakens but remains above null without wa-tar.")
    print(f"    Z={z_abl:+.2f}. wa-tar is important but not the only signal.")
    print(f"    Honest framing: 'wa-tar strengthens the case; it does not make it.'")
else:
    print(f"  ✗ LOAD-BEARING: G_LUWIAN is NOT significant without wa-tar.")
    print(f"    Z={z_abl:+.2f}. The Luwian signal depends critically on wa-tar.")
    print(f"    Honest framing: 'The wa-tar assignment is the single most important")
    print(f"    claim. If #36≠wa or #11≠tar, the case weakens substantially.'")
    print(f"    This is a genuine vulnerability that independent replication must address.")

print()
print(f"  ─── What remains without wa-tar ───────────────────────────────────")
print(f"  Non-water Luwian vocabulary still present in disc (ablated scoring):")
for k, v in sorted(VOCAB_ABLATED.items(), key=lambda x: -x[1]):
    count = sum(1 for word in DISC_ACHTERBERG
                for i in range(len(word))
                if '-'.join(G_LUWIAN_KEY.get(s,'') for s in word[i:] if G_LUWIAN_KEY.get(s,'')).startswith(k))
    if count > 0:
        print(f"    '{k}' (wt={v}) — appears in disc text")
print(SEP)
