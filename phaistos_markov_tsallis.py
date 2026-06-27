"""
phaistos_markov_tsallis.py  -  Algorithm #2: High-Order Markov + Tsallis Entropy
===================================================================================
"Εντροπία Κβαντικής Μετάβασης / Markov υψηλής τάξης"

Tests whether the Phaistos Disc's statistical memory (long-range correlations)
matches natural language corpora — specifically Luwian ritual texts.

Core insight: Random text has NO memory beyond lag-1. Natural language retains
statistical dependencies at lag 3-4 tokens (morphological/syntactic memory).
Tsallis non-extensive entropy detects this even for very short sequences.

METRIC A — Entropy Decay Profile (key-independent)
  Compute r_k = H(k)/H(0) for k=0..4. (H = conditional Shannon entropy at order k)
  Disc r_k vs shuffled-disc null → proves disc has non-random memory depth.
  Disc r_k vs corpus char-sequence r_k → measures structural match per corpus.

METRIC B — Tsallis Non-Extensive Entropy (key-independent)
  S_q = (1 - sum p_i^q) / (q - 1)  [q≠1]; S_1 = -sum p_i log p_i [Shannon]
  Compare disc SIGN distribution vs corpus CHARACTER distribution (both are
  "elementary symbol frequency distributions" at respective granularity).
  Jensen-Tsallis distance across q values measures distribution shape similarity.

METRIC C — Mutual Information Decay (key-independent)
  I_k = I(s_t ; s_{t+k}) for k=1..8.
  Natural language: slow decay (power-law) up to lag 4+.
  Random text: I_k → 0 for k > 1.
  Excess MI = disc MI - null mean MI, p = P(null >= obs).

METRIC D — Character Bigram Cross-Entropy [KEY-DEPENDENT: G_LUWIAN]
  Build Laplace-smoothed character bigram model from corpus.
  Evaluate ONLY G_LUWIAN-KNOWN sign phonetic sequences (skip unknown signs).
  H_x = -1/N * sum log2 P(c_i | c_{i-1})
  Lower H_x = phonetic reading fits corpus character patterns better.

Usage:
  python phaistos_markov_tsallis.py           # full run (1000 MC)
  python phaistos_markov_tsallis.py --fast    # 200 MC (quick)
"""

import argparse
import json
import math
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ROOT      = Path(__file__).parent
CACHE_DIR = ROOT / "__pycache__"
sys.path.insert(0, str(ROOT))

from phaistos_canonical_data import SIDE_A_EVANS, SIDE_B_EVANS

# G_LUWIAN phonetic key (Achterberg/Best/Woudhuizen)
G_LUWIAN: Dict[int, str] = {
    2: "za", 36: "wa", 11: "tar", 22: "ha", 7: "ti",
    29: "na", 6: "an", 12: "zi", 45: "tiwa", 1: "i",
}

DISC_WORDS  = SIDE_A_EVANS + SIDE_B_EVANS
DISC_TOKENS = [s for w in DISC_WORDS for s in w]  # 242 sign tokens

# Phonetic text — FULL (with x-placeholders for unknown signs)
DISC_PHON_FULL = " ".join(
    "-".join(G_LUWIAN.get(s, f"x{s:02d}") for s in w)
    for w in DISC_WORDS
)

# Phonetic text — KNOWN ONLY (only signs with G_LUWIAN mapping, space-separated)
# Used for cross-entropy so unknown signs don't pollute the model evaluation
DISC_PHON_KNOWN = " ".join(
    G_LUWIAN[s]
    for w in DISC_WORDS
    for s in w
    if s in G_LUWIAN
)

# Word-level known phonetic (for word-order shuffling in MC)
DISC_PHON_WORDS_KNOWN: List[str] = [
    " ".join(G_LUWIAN[s] for s in w if s in G_LUWIAN)
    for w in DISC_WORDS
    if any(s in G_LUWIAN for s in w)
]

N_MC          = 1000
LAPLACE_ALPHA = 0.5

# ---------------------------------------------------------------------------
# Corpus loading
# ---------------------------------------------------------------------------
def load_corpus(name: str) -> str:
    p = CACHE_DIR / f"ncd_cache_{name}.txt"
    if not p.exists():
        return ""
    return p.read_text(encoding="utf-8")

# ---------------------------------------------------------------------------
# A.  Entropy utilities
# ---------------------------------------------------------------------------
def _freq(seq: List) -> Dict:
    c = Counter(seq)
    n = sum(c.values())
    return {k: v / n for k, v in c.items()}

def shannon_h(dist: Dict) -> float:
    return -sum(p * math.log2(p) for p in dist.values() if p > 0)

def conditional_entropy(seq: List, order: int) -> float:
    """H(X_t | X_{t-order}...X_{t-1}) via plug-in estimator."""
    if order == 0:
        return shannon_h(_freq(seq))
    ctx_next: Dict = defaultdict(Counter)
    for i in range(order, len(seq)):
        ctx_next[tuple(seq[i - order: i])][seq[i]] += 1
    n_total = len(seq) - order
    h = 0.0
    for ctx, nxt in ctx_next.items():
        w = sum(nxt.values()) / n_total
        p_nxt = {k: v / sum(nxt.values()) for k, v in nxt.items()}
        h -= w * sum(p * math.log2(p) for p in p_nxt.values() if p > 0)
    return h

def entropy_decay(seq: List, max_k: int = 4) -> List[float]:
    """r_k = H(k) / H(0) for k=0..max_k. r_0 = 1.0 by definition."""
    h0 = conditional_entropy(seq, 0)
    if h0 < 1e-10:
        return [1.0] * (max_k + 1)
    return [conditional_entropy(seq, k) / h0 for k in range(max_k + 1)]

def corpus_to_char_seq(text: str, n: int = 6000, seed: int = 0) -> List[str]:
    """Random character-level sample from corpus (non-whitespace chars)."""
    chars = [c for c in text if not c.isspace()]
    if len(chars) <= n:
        return chars
    start = random.Random(seed).randint(0, len(chars) - n)
    return chars[start: start + n]

# ---------------------------------------------------------------------------
# B.  Tsallis entropy
# ---------------------------------------------------------------------------
def tsallis(dist: Dict, q: float) -> float:
    probs = [p for p in dist.values() if p > 0]
    if abs(q - 1.0) < 1e-9:
        return -sum(p * math.log(p) for p in probs)
    return (1.0 - sum(p ** q for p in probs)) / (q - 1.0)

Q_VALUES = (0.5, 0.75, 1.0, 1.5, 2.0, 3.0)

def jensen_tsallis_dist(dist_a: Dict, dist_b: Dict) -> float:
    """
    Mean normalized |S_q(a) - S_q(b)| / max(S_q(a), S_q(b), 1e-10)
    across Q_VALUES. Range [0, 1]: 0 = identical profile, 1 = maximally different.
    """
    total = 0.0
    for q in Q_VALUES:
        sa = tsallis(dist_a, q)
        sb = tsallis(dist_b, q)
        denom = max(abs(sa), abs(sb), 1e-10)
        total += abs(sa - sb) / denom
    return total / len(Q_VALUES)

def corpus_char_freq(text: str) -> Dict[str, float]:
    chars = [c for c in text if not c.isspace()]
    n     = len(chars)
    if n == 0:
        return {}
    cnt = Counter(chars)
    return {c: v / n for c, v in cnt.items()}

# ---------------------------------------------------------------------------
# C.  Mutual Information
# ---------------------------------------------------------------------------
def mi_at_lag(seq: List, lag: int) -> float:
    n = len(seq) - lag
    if n < 10:
        return 0.0
    pairs  = [(seq[i], seq[i + lag]) for i in range(n)]
    pcnt   = Counter(pairs)
    lcnt   = Counter(a for a, _ in pairs)
    rcnt   = Counter(b for _, b in pairs)
    mi = 0.0
    for (a, b), c in pcnt.items():
        p_ab = c / n
        p_a  = lcnt[a] / n
        p_b  = rcnt[b] / n
        mi  += p_ab * math.log2(p_ab / (p_a * p_b))
    return max(mi, 0.0)

def mi_profile(seq: List, max_lag: int = 8) -> List[float]:
    return [mi_at_lag(seq, k) for k in range(1, max_lag + 1)]

# ---------------------------------------------------------------------------
# D.  Character bigram language model
# ---------------------------------------------------------------------------
def build_char_lm(text: str, alpha: float = LAPLACE_ALPHA) -> Tuple[Dict, set]:
    chars    = list(text)
    alphabet = set(chars)
    cnt: Dict[str, Counter] = defaultdict(Counter)
    for i in range(1, len(chars)):
        cnt[chars[i-1]][chars[i]] += 1
    V = len(alphabet)
    lm: Dict[str, Dict[str, float]] = {}
    for prev in alphabet:
        total = sum(cnt[prev].values()) + alpha * V
        lm[prev] = {ch: math.log2((cnt[prev].get(ch, 0) + alpha) / total)
                    for ch in alphabet}
    return lm, alphabet

def cross_entropy_lm(text: str, lm: Dict, alphabet: set,
                     alpha: float = LAPLACE_ALPHA) -> float:
    chars = list(text)
    if len(chars) < 2:
        return float("nan")
    V      = len(alphabet)
    eps    = math.log2(alpha / (alpha * V + 1))
    total  = 0.0
    n      = 0
    for i in range(1, len(chars)):
        prev, curr = chars[i-1], chars[i]
        total += lm.get(prev, {}).get(curr, eps)
        n     += 1
    return -total / max(n, 1)

# ---------------------------------------------------------------------------
# MC helpers
# ---------------------------------------------------------------------------
def _shuffle(tokens: List, rng: random.Random) -> List:
    t = tokens.copy()
    rng.shuffle(t)
    return t

def _print_progress(i: int, n: int):
    if (i + 1) % 250 == 0:
        print(f"    MC {i+1}/{n}...", end="\r", flush=True)

def _clear():
    print(" " * 45, end="\r")

def p_lower(obs: float, null: List[float]) -> float:
    return sum(1 for x in null if x <= obs) / len(null)

def p_upper(obs: float, null: List[float]) -> float:
    return sum(1 for x in null if x >= obs) / len(null)

def sig(p: float) -> str:
    if p != p:  return "   "
    return "***" if p < 0.001 else "** " if p < 0.01 else "*  " if p < 0.05 else "   "

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def run(n_mc: int):
    print("=" * 74)
    print("  PHAISTOS DISC — ALGORITHM #2: HIGH-ORDER MARKOV + TSALLIS ENTROPY")
    print("=" * 74)
    print(f"  Disc: {len(DISC_TOKENS)} tokens  |  alphabet: 45 signs  |  MC: {n_mc}")
    print(f"  Known G_LUWIAN signs: {len(G_LUWIAN)}/45  ({len(DISC_PHON_KNOWN.split())} known tokens in disc)")
    print()

    # ------------------------------------------------------------------
    # Load corpora
    # ------------------------------------------------------------------
    CORPUS_NAMES = ["luwian_ritual", "luwian_all", "hittite", "linear_b"]
    corpora: Dict[str, str] = {}
    print("  Corpora:")
    for name in CORPUS_NAMES:
        t = load_corpus(name)
        if t:
            corpora[name] = t
            print(f"    {name:<20}: {len(t):>12,} chars")
        else:
            print(f"    {name:<20}: NOT CACHED — run Algorithm #1 first")
    print()

    results: Dict = {}

    # ==================================================================
    # A. ENTROPY DECAY
    # ==================================================================
    print("[A] ENTROPY DECAY PROFILE (key-independent)")
    print("    Measures 'memory depth': how much knowing k previous signs")
    print("    reduces uncertainty about the next sign.")
    print("-" * 70)

    disc_r = entropy_decay(DISC_TOKENS, max_k=4)
    print(f"  Disc:  " + "  ".join(f"r_{k}={disc_r[k]:.4f}" for k in range(5)))

    # MC null for disc-own entropy decay
    rng = random.Random(42)
    decay_nulls: List[List[float]] = []
    for i in range(n_mc):
        decay_nulls.append(entropy_decay(_shuffle(DISC_TOKENS, rng), max_k=4))
        _print_progress(i, n_mc)
    _clear()

    print()
    for k in range(1, 4):
        obs_k  = disc_r[k]
        null_k = [d[k] for d in decay_nulls]
        null_mu = sum(null_k) / len(null_k)
        pv      = p_lower(obs_k, null_k)
        pct_red = (1 - obs_k) * 100
        print(f"  k={k}: disc r={obs_k:.4f} (context reduces H by {pct_red:.1f}%)"
              f"  null={null_mu:.4f}  p={pv:.4f} {sig(pv)}")
    results["entropy_decay_disc"] = disc_r

    # Corpus entropy decay comparison (corpus char sequences)
    print()
    print("  Entropy decay distance: disc vs each corpus character sequence")
    decay_dist = {}
    for name, text in corpora.items():
        corp_seq = corpus_to_char_seq(text, n=6000, seed=0)
        corp_r   = entropy_decay(corp_seq, max_k=4)
        dist     = sum(abs(disc_r[k] - corp_r[k]) for k in range(1, 5))
        decay_dist[name] = dist
        print(f"    {name:<20}: corpus r_1={corp_r[1]:.4f}  dist={dist:.4f}")

    # MC null for corpus distance
    decay_dist_nulls: Dict[str, List[float]] = defaultdict(list)
    for i in range(n_mc):
        shuf = _shuffle(DISC_TOKENS, rng)
        shuf_r = entropy_decay(shuf, max_k=4)
        for name, text in corpora.items():
            corp_seq = corpus_to_char_seq(text, n=6000, seed=i)
            corp_r   = entropy_decay(corp_seq, max_k=4)
            dist     = sum(abs(shuf_r[k] - corp_r[k]) for k in range(1, 5))
            decay_dist_nulls[name].append(dist)
        _print_progress(i, n_mc)
    _clear()

    print()
    print("  p-values (lower dist = disc more similar to corpus):")
    for name in sorted(decay_dist, key=decay_dist.get):
        obs   = decay_dist[name]
        nulls = decay_dist_nulls[name]
        pv    = p_lower(obs, nulls)
        nm    = sum(nulls) / len(nulls)
        print(f"    #{list(sorted(decay_dist, key=decay_dist.get)).index(name)+1}"
              f"  {name:<20}: dist={obs:.4f}  null={nm:.4f}  p={pv:.4f} {sig(pv)}")
    results["entropy_decay_dist"] = {n: {"dist": v, "p": p_lower(v, decay_dist_nulls[n])}
                                     for n, v in decay_dist.items()}

    # ==================================================================
    # B. TSALLIS NON-EXTENSIVE ENTROPY
    # ==================================================================
    print()
    print("[B] TSALLIS NON-EXTENSIVE ENTROPY (key-independent)")
    print("    Compares SHAPE of disc sign-frequency distribution vs")
    print("    corpus character-frequency distribution across q-values.")
    print("-" * 70)

    disc_freq     = _freq(DISC_TOKENS)
    disc_tsallis  = {q: tsallis(disc_freq, q) for q in Q_VALUES}
    print(f"  Disc Tsallis S_q:")
    print("    q  : " + "  ".join(f"{q:.2f}" for q in Q_VALUES))
    print("    S_q: " + "  ".join(f"{disc_tsallis[q]:5.3f}" for q in Q_VALUES))
    print()

    # Pre-compute corpus char frequencies once (expensive for large corpora)
    corp_char_freqs = {name: corpus_char_freq(text) for name, text in corpora.items()}

    tsallis_dist: Dict[str, float] = {}
    for name, ccf in corp_char_freqs.items():
        d = jensen_tsallis_dist(disc_freq, ccf)
        tsallis_dist[name] = d
        print(f"    Jensen-Tsallis dist(disc, {name}): {d:.5f}")

    # Bootstrap null: resample DISC tokens with replacement -> slightly different frequencies.
    # Shuffling is NOT valid here (shuffling preserves frequencies identically).
    # Bootstrap tests: "Is the disc's specific sign distribution closer to each corpus
    # than a resampled version would be?" — i.e., is the pattern specific, not just
    # an artifact of the overall frequency mix.
    print(f"\n  Bootstrap null ({n_mc} resamples with replacement)...")
    tsallis_nulls: Dict[str, List[float]] = defaultdict(list)
    for i in range(n_mc):
        boot      = [rng.choice(DISC_TOKENS) for _ in range(len(DISC_TOKENS))]
        boot_freq = _freq(boot)
        for name, ccf in corp_char_freqs.items():
            tsallis_nulls[name].append(jensen_tsallis_dist(boot_freq, ccf))
        _print_progress(i, n_mc)
    _clear()

    print()
    print("  Bootstrap p-values (lower dist = disc more concentrated than resampled):")
    for name in sorted(tsallis_dist, key=tsallis_dist.get):
        obs   = tsallis_dist[name]
        nulls = tsallis_nulls[name]
        pv    = p_lower(obs, nulls)
        nm    = sum(nulls) / len(nulls)
        print(f"    #{list(sorted(tsallis_dist, key=tsallis_dist.get)).index(name)+1}"
              f"  {name:<20}: dist={obs:.5f}  boot_null={nm:.5f}  p={pv:.4f} {sig(pv)}")
    results["tsallis"] = {n: {"dist": v, "p": p_lower(v, tsallis_nulls[n])}
                          for n, v in tsallis_dist.items()}

    # ==================================================================
    # C. MUTUAL INFORMATION DECAY
    # ==================================================================
    MAX_LAG = 8
    print()
    print(f"[C] MUTUAL INFORMATION DECAY  lag k=1..{MAX_LAG}  (key-independent)")
    print("    I_k = I(s_t ; s_{t+k}): statistical dependency at distance k.")
    print("    Natural language: slow decay. Random text: I_k -> 0 for k>1.")
    print("-" * 70)

    disc_mi = mi_profile(DISC_TOKENS, MAX_LAG)
    print(f"  Disc MI:")
    print("    lag : " + "  ".join(f"k={k}" for k in range(1, MAX_LAG + 1)))
    print("    MI  : " + "  ".join(f"{v:.3f}" for v in disc_mi))

    mi_nulls: List[List[float]] = []
    for i in range(n_mc):
        mi_nulls.append(mi_profile(_shuffle(DISC_TOKENS, rng), MAX_LAG))
        _print_progress(i, n_mc)
    _clear()

    print()
    print("  Lag   | Disc MI | Null mean | Excess MI | p-value  | sig")
    print("  " + "-" * 58)
    mi_pvs = []
    for k in range(MAX_LAG):
        obs     = disc_mi[k]
        null_k  = [r[k] for r in mi_nulls]
        nm      = sum(null_k) / len(null_k)
        excess  = obs - nm
        pv      = p_upper(obs, null_k)
        mi_pvs.append(pv)
        print(f"  k={k+1:<4} | {obs:7.4f} | {nm:9.4f} | {excess:+9.4f} | {pv:7.4f}  | {sig(pv)}")

    n_sig = sum(1 for p in mi_pvs if p < 0.05)
    print(f"\n  {n_sig}/{MAX_LAG} lags with p<0.05. Disc maintains long-range MI up to lag "
          f"k={max(k+1 for k, p in enumerate(mi_pvs) if p < 0.05)}"
          if n_sig else "  No lags significant.")
    results["mi_decay"] = {"profile": disc_mi, "p_values": mi_pvs}

    # ==================================================================
    # D. CROSS-ENTROPY LANGUAGE MODEL  [KEY-DEPENDENT]
    # ==================================================================
    print()
    print("[D] CHARACTER BIGRAM CROSS-ENTROPY  [KEY-DEPENDENT: G_LUWIAN]")
    print("    Tests whether G_LUWIAN phonetic reading fits each corpus's")
    print("    character patterns. Only KNOWN signs used (skips unknowns).")
    print(f"    Known phonetic text ({len(DISC_PHON_KNOWN.split())} tokens): "
          f"'{DISC_PHON_KNOWN[:60]}...'")
    print("-" * 70)

    ce_results: Dict = {}
    for name, text in corpora.items():
        if len(text) < 1000:
            continue
        lm, alpha_set = build_char_lm(text[:500_000])
        obs_ce = cross_entropy_lm(DISC_PHON_KNOWN, lm, alpha_set)

        # MC: shuffle word order in disc phonetic (known-sign words only)
        ce_nulls: List[float] = []
        words = DISC_PHON_WORDS_KNOWN.copy()
        mc_rng = random.Random(7)
        for i in range(n_mc):
            mc_rng.shuffle(words)
            shuffled = " ".join(words)
            ce_nulls.append(cross_entropy_lm(shuffled, lm, alpha_set))
            _print_progress(i, n_mc)
        _clear()

        nm   = sum(ce_nulls) / len(ce_nulls)
        std  = (sum((x - nm)**2 for x in ce_nulls) / len(ce_nulls)) ** 0.5
        pv   = p_lower(obs_ce, ce_nulls)
        z    = (obs_ce - nm) / max(std, 1e-10)
        print(f"  {name:<20}: H_x={obs_ce:.4f} bits/char  "
              f"null={nm:.4f}+/-{std:.4f}  z={z:.2f}  p={pv:.4f} {sig(pv)}")
        ce_results[name] = {"obs": obs_ce, "null_mu": nm, "null_std": std,
                            "z": z, "p": pv}
    results["cross_entropy"] = ce_results

    # ==================================================================
    # SUMMARY
    # ==================================================================
    print()
    print("=" * 74)
    print("  SUMMARY — ALGORITHM #2 RESULTS")
    print("=" * 74)

    print("\n  [A] Entropy Decay (disc internal structure, key-independent):")
    for k in range(1, 4):
        obs  = disc_r[k]
        null = [d[k] for d in decay_nulls]
        nm   = sum(null) / len(null)
        pv   = p_lower(obs, null)
        print(f"      k={k}: r={obs:.4f}  null={nm:.4f}  p={pv:.4f} {sig(pv)}")

    print("\n  [A] Entropy Decay profile distance (disc vs corpus):")
    for name, d in sorted(results["entropy_decay_dist"].items(),
                          key=lambda x: x[1]["dist"]):
        print(f"      {name:<22}: dist={d['dist']:.4f}  p={d['p']:.4f} {sig(d['p'])}")

    print("\n  [B] Tsallis profile distance (disc signs vs corpus chars):")
    for name, d in sorted(results["tsallis"].items(),
                          key=lambda x: x[1]["dist"]):
        print(f"      {name:<22}: dist={d['dist']:.5f}  p={d['p']:.4f} {sig(d['p'])}")

    print(f"\n  [C] MI Decay: {n_sig}/{MAX_LAG} lags significant (p<0.05)")
    n_001 = sum(1 for p in mi_pvs if p < 0.001)
    print(f"      {n_001}/{MAX_LAG} lags significant at p<0.001")

    if ce_results:
        print("\n  [D] Cross-entropy G_LUWIAN phonetic [KEY-DEPENDENT]:")
        for name, r in sorted(ce_results.items(), key=lambda x: x[1]["obs"]):
            print(f"      {name:<22}: H_x={r['obs']:.4f}  z={r['z']:.2f}  "
                  f"p={r['p']:.4f} {sig(r['p'])}")

    print()
    print("  Significance: *** p<0.001  ** p<0.01  * p<0.05")
    print("  [D] uses G_LUWIAN phonetic key — MUST be labeled KEY-DEPENDENT in paper")

    # Save
    out = ROOT / "markov_tsallis_results.json"
    out.write_text(json.dumps(results, indent=2, default=str), encoding="utf-8")
    print(f"\n  Saved -> markov_tsallis_results.json")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--fast", action="store_true")
    args = parser.parse_args()
    if args.fast:
        N_MC = 200
        print("[FAST MODE] 200 MC\n")
    run(N_MC)
