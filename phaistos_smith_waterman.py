#!/usr/bin/env python3
"""
phaistos_smith_waterman.py  -  Algorithm #4: Morphological Smith-Waterman
Local sequence alignment between disc structural/phonetic patterns and corpora.

Part A: Word-level structural tag alignment (KEY-INDEPENDENT)
  Each disc word-group → tag: {length}|{second_sign_role}|{tail_freq}
  Each corpus word     → tag: {length}|{second_char_rank}|{tail_char_rank}
  Smith-Waterman finds highest-scoring local alignment; MC null = shuffled disc.

Part B: G_LUWIAN phonetic syllable alignment (KEY-DEPENDENT)
  Disc: known G_LUWIAN syllables (za wa tar ha ti na an zi tiwa i)
  Corpus: syllables extracted by splitting on spaces and hyphens (TLHdig format)
  Scoring: exact=+3, same-onset=+1, mismatch=-1, gap=-2
"""
import sys, re, json, random, argparse
from collections import Counter
from pathlib import Path
from typing import List, Tuple, Dict

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ── Constants ──────────────────────────────────────────────────────────────────
ROOT       = Path(__file__).parent
CACHE_DIR  = ROOT / "__pycache__"
N_MC       = 1000
TARGET_N   = 1000   # words/syllables from corpus per alignment

# ── Disc data (Evans numbering) ────────────────────────────────────────────────
SIDE_A_EVANS = [
    [2,12,13,1,18],[2,12,13,10,1,18],[2,7,36,8,1,3],[2,6,12,3,24,1,4],
    [2,21,12,3,24,1,4],[2,34,12,3,24,1,4],[2,7,12,15,36,3],[2,12,3,24,1,4],
    [2,12,15,36,3],[2,12,3,24,1],[2,32,6,12,31],[2,6,12,31],
    [2,32,4,12,3,1,17],[2,12,3,1,17],[2,32,4,12,3,1,18],[2,4,12,3,1,18],
    [2,32,4,12,3,1,18,25],[2,12,3,1,18,25],[2,32,4,12,3,1,19],[2,12,3,1,19],
    [2,4,12,7,36,8],[2,12,7,36,8],[2,12,13,9,1,36],[2,12,13,9,1,36,8],
    [2,12,13,9,1,36,8,25],[2,12,22,7,7,23],[2,11,45,29,7],[2,29,7,7,10],
    [2,36,12,3,24,1],[2,29,23,26,15],[2,36,29,7,1]
]
SIDE_B_EVANS = [
    [2,12,13,1,11,45],[2,12,13,1,36,45],[2,12,13,1,18],[2,22,29,18],[2,22,7,1],
    [2,7,36,8,1,3],[2,12,15,36,3],[2,12,3,24,1,4],[2,12,3,24,1],[2,32,6,12,31],
    [2,6,12,31],[2,32,4,12,3,1,17],[2,12,3,1,17],[2,32,4,12,3,1,18],
    [2,4,12,3,1,18],[2,32,4,12,3,1,18,25],[2,12,3,1,18,25],
    [2,32,4,12,3,1,19],[2,12,3,1,19],[2,4,12,7,36,8],[2,12,7,36,8],
    [2,12,13,9,1,36],[2,12,13,9,1,36,8],[2,12,13,9,1,36,8,25],
    [2,12,22,7,7,23],[2,11,45,29,7],[2,29,7,7,10],[2,36,12,3,24,1],
    [2,29,23,26,15],[2,36,29,7,1]
]
DISC_WORDS  = SIDE_A_EVANS + SIDE_B_EVANS   # 61 word groups
DISC_TOKENS = [s for w in DISC_WORDS for s in w]  # 242 tokens

G_LUWIAN = {2:"za",36:"wa",11:"tar",22:"ha",7:"ti",29:"na",6:"an",12:"zi",
            45:"tiwa",1:"i"}

# ── Sign statistics ────────────────────────────────────────────────────────────
def _compute_stats():
    freq = Counter(DISC_TOKENS)
    pos_init, pos_final, pos_all = Counter(), Counter(), Counter()
    for word in DISC_WORDS:
        if not word: continue
        pos_all.update(word)
        pos_init[word[0]]  += 1
        pos_final[word[-1]] += 1
    rank = {s: r+1 for r,(s,_) in enumerate(freq.most_common())}
    return freq, rank, pos_init, pos_final, pos_all

_FREQ, _RANK, _POS_INIT, _POS_FINAL, _POS_ALL = _compute_stats()

def _freq_class(sign: int) -> str:
    r = _RANK.get(sign, 45)
    return "H" if r <= 10 else ("M" if r <= 25 else "L")

def second_sign_role(sign: int) -> str:
    """
    Classify the second sign of a disc word-group.
    This reflects the grammatical head after the DET (#02).
    """
    roles = {
        12: "HEAD",    # follows DET in 60%+ of words → phrase head
        7:  "VERB",    # ti  = verbal stem marker
        36: "PART",    # wa  = particle/verbal prefix
        6:  "CONN",    # an  = connective
        29: "CONN",    # na  = connective
        22: "MOD",     # ha  = affirm/modal
        11: "STEM",    # tar = common stem
        45: "DIV",     # tiwa= divine name
    }
    if sign in roles:
        return roles[sign]
    fc = _freq_class(sign)
    return f"ROOT_{fc}"


# ── Part A: Word-level structural tags ────────────────────────────────────────
def disc_word_tag(word: List[int]) -> str:
    """
    Structural tag for a disc word-group:  {len_class}|{second_role}|{tail_class}
    All disc words start with #02 (DET), so head is fixed; we use position [1].
    """
    n = len(word)
    lc  = "S" if n <= 3 else ("M" if n <= 5 else "L")
    sec = second_sign_role(word[1]) if len(word) > 1 else "ROOT_L"
    tc  = _freq_class(word[-1])
    return f"{lc}|{sec}|{tc}"

DISC_WORD_TAGS = [disc_word_tag(w) for w in DISC_WORDS]


# ── Part A (new): Sign-position sequence alignment ────────────────────────────
# Uses all 355 disc tokens (not just 61 word-level summaries).
# Each token gets tag: {word_position}_{sign_role_class}
# Word positions: INIT(pos=0), SEC(pos=1), MED(middle), FINAL(last)
# Role mapped to frequency class H/M/L for comparison with corpus chars.

_ROLE_TO_FC = {
    "DET": "H", "HEAD": "H", "VERB": "H", "PART": "H",
    "CONN": "M", "MOD": "M", "STEM": "M",
    "DIV": "L",
    "H": "H", "M": "M", "L": "L",
}

def disc_sign_pos_tags() -> List[str]:
    """
    Tag all 355 disc sign-tokens by (word_position, sign_role_class).
    INIT_H, SEC_H, MED_M, FINAL_L, etc.
    """
    tags = []
    for word in DISC_WORDS:
        n = len(word)
        for idx, sign in enumerate(word):
            if idx == 0:       pos = "INIT"
            elif idx == 1:     pos = "SEC"
            elif idx == n-1:   pos = "FINAL"
            else:              pos = "MED"

            if sign == 2:        role = "DET"
            elif sign == 12:     role = "HEAD"
            elif sign == 7:      role = "VERB"
            elif sign == 36:     role = "PART"
            elif sign in (6,29): role = "CONN"
            elif sign == 22:     role = "MOD"
            elif sign == 11:     role = "STEM"
            elif sign == 45:     role = "DIV"
            else:                role = _freq_class(sign)

            tags.append(f"{pos}_{_ROLE_TO_FC.get(role, 'M')}")
    return tags

DISC_SIGN_POS_TAGS = disc_sign_pos_tags()


def corpus_char_pos_tags(text: str, n: int = 5000) -> List[str]:
    """
    Tag each character in corpus text by position within its word and freq class.
    INIT/SEC/MED/FINAL × H/M/L — structurally analogous to disc sign-position tags.
    Splits words on hyphens first (TLHdig syllable boundaries = morpheme units).
    """
    words = re.split(r'\s+', text)
    # Flatten: treat each hyphenated-syllable as a sub-unit, keep word positions
    units: List[List[str]] = []
    for w in words:
        parts = [p for p in w.split("-") if re.search(r'[a-zA-Zāēīūšḫ]', p)]
        if parts:
            units.append(parts)

    # Character frequency from sample
    sample_chars = [c for unit in units[:500] for part in unit for c in part.lower() if c.isalpha()]
    all_cf = Counter(sample_chars)
    sorted_c = [c for c,_ in all_cf.most_common()]
    nc = max(len(sorted_c), 1)
    char_rank = {c: i/nc for i,c in enumerate(sorted_c)}

    def cfc(c: str) -> str:
        r = char_rank.get(c.lower(), 1.0)
        return "H" if r < 0.25 else ("M" if r < 0.60 else "L")

    tags = []
    for unit in units:
        nu = len(unit)
        for idx, syllable in enumerate(unit):
            if not syllable: continue
            if idx == 0:       pos = "INIT"
            elif idx == 1:     pos = "SEC"
            elif idx == nu-1:  pos = "FINAL"
            else:              pos = "MED"
            # Use first char of syllable as representative
            first = next((c for c in syllable if c.isalpha()), None)
            if first is None: continue
            tags.append(f"{pos}_{cfc(first)}")
            if len(tags) >= n:
                return tags
    return tags


def sign_pos_score(a: str, b: str) -> float:
    """
    Scoring for sign-position tag alignment.
    disc INIT_H ↔ corpus INIT_H: natural word-initial high-freq element.
    """
    if a == b:
        return 3.0
    pa = a.split("_")
    pb = b.split("_")
    if len(pa) < 2 or len(pb) < 2:
        return -1.0
    pos_a, fc_a = pa[0], pa[1]
    pos_b, fc_b = pb[0], pb[1]

    score = 0.0
    score += 2.0 if pos_a == pos_b else -1.0   # position match most critical
    score += 1.0 if fc_a  == fc_b  else  0.0   # freq-class match
    return score


# ── Part B: Phonetic syllable alignment ───────────────────────────────────────
def disc_phonetic_tokens() -> List[str]:
    """G_LUWIAN phonetic syllables from known disc signs (split tiwa→ti+wa)."""
    tokens = []
    for word in DISC_WORDS:
        for sign in word:
            if sign in G_LUWIAN:
                syl = G_LUWIAN[sign]
                if syl == "tiwa":
                    tokens += ["ti", "wa"]
                else:
                    tokens.append(syl)
    return tokens

DISC_PHON = disc_phonetic_tokens()


_NORM_MAP = str.maketrans("ḫšḥāēīūáéíóú", "hssaeiuaeiou")
_DIGIT_RE = re.compile(r'\d+')
_NONALPHA = re.compile(r'[^a-z]')

def _normalize_syl(s: str) -> str:
    s = s.lower().translate(_NORM_MAP)
    s = _DIGIT_RE.sub("", s)
    return _NONALPHA.sub("", s)


def corpus_syllables(text: str, n: int = TARGET_N) -> List[str]:
    """
    Syllable list from corpus text: split on whitespace and hyphens (TLHdig format).
    Normalizes cuneiform diacritics; drops Sumerograms (all-caps words).
    """
    raw_tokens = re.split(r'[\s\-]+', text)
    syls = []
    for tok in raw_tokens:
        # Skip Sumerograms (all uppercase, len>1)
        if tok == tok.upper() and len(tok) > 1 and tok.isalpha():
            continue
        s = _normalize_syl(tok)
        if len(s) >= 1:
            syls.append(s)
        if len(syls) >= n:
            break
    return syls


VOWELS = set("aeiou")

def phon_score(a: str, b: str) -> float:
    """
    Phonetic scoring for syllable alignment.
    Linguistically motivated: same onset consonant in Luwian = related morpheme.
    """
    if a == b:
        return 3.0
    # Same onset consonant (a[0]==b[0]) and both are consonant-initial syllables
    if (len(a) >= 2 and len(b) >= 2
            and a[0] == b[0] and a[0] not in VOWELS):
        return 1.0
    # One is a prefix of the other (partial match)
    if len(a) >= 2 and len(b) >= 2 and (a[:2] == b[:2]):
        return 0.5
    return -1.0


# ── Smith-Waterman (local alignment) ──────────────────────────────────────────
def smith_waterman(query: List, target: List, score_fn, gap: float = -2.0) -> float:
    """
    Standard Smith-Waterman local alignment.
    Returns normalised best score (raw / len(query)) for cross-length comparison.
    """
    n, m = len(query), len(target)
    prev = [0.0] * (m + 1)
    best = 0.0

    for i in range(n):
        curr    = [0.0] * (m + 1)
        qi      = query[i]
        for j in range(m):
            diag = prev[j]   + score_fn(qi, target[j])
            up   = prev[j+1] + gap
            left = curr[j]   + gap
            val  = max(0.0, diag, up, left)
            curr[j+1] = val
            if val > best:
                best = val
        prev = curr

    return best / max(n, 1)


def mc_pvalue(query: List, target: List, score_fn,
              n_mc: int = N_MC, seed: int = 42) -> Tuple[float, float, float]:
    """
    Observed SW score, null mean, and p-value.
    Null: shuffle query (preserves tag/syllable distribution, breaks order).
    """
    rng = random.Random(seed)
    observed = smith_waterman(query, target, score_fn)

    null_scores = []
    shuffled = list(query)
    for _ in range(n_mc):
        rng.shuffle(shuffled)
        null_scores.append(smith_waterman(shuffled, target, score_fn))

    null_mean = sum(null_scores) / len(null_scores)
    p_val = sum(1 for s in null_scores if s >= observed) / len(null_scores)
    return observed, null_mean, p_val


# ── Utilities ─────────────────────────────────────────────────────────────────
def _cache(name: str) -> str:
    p = CACHE_DIR / f"ncd_cache_{name}.txt"
    if p.exists():
        return p.read_text(encoding="utf-8")
    return ""

def _sig(p: float) -> str:
    if p < 0.001: return "***"
    if p < 0.01:  return "** "
    if p < 0.05:  return "*  "
    return "   "


# ── Main ───────────────────────────────────────────────────────────────────────
def run(n_mc: int = N_MC, target_n: int = TARGET_N):
    corpora = {
        "luwian_ritual": _cache("luwian_ritual"),
        "luwian_all":    _cache("luwian_all"),
        "hittite":       _cache("hittite"),
        "linear_b":      _cache("linear_b"),
    }

    print("=" * 74)
    print("  PHAISTOS DISC — ALGORITHM #4: MORPHOLOGICAL SMITH-WATERMAN")
    print("=" * 74)
    print(f"  Disc: {len(DISC_WORDS)} word groups, {len(DISC_TOKENS)} tokens")
    print(f"  G_LUWIAN phonetic tokens: {len(DISC_PHON)}  "
          f"(known signs only: {len(set(DISC_TOKENS) & set(G_LUWIAN))}/45)")
    print(f"  MC: {n_mc}  |  target corpus size: {target_n} words/syllables")
    print()
    print("  Corpora:")
    for name, text in corpora.items():
        print(f"    {name:<20}: {len(text):>10,} chars")
    print()

    results = {"part_a": {}, "part_b": {}}

    # ── Part A: sign-position sequence alignment ───────────────────────────────
    print("[A] SIGN-POSITION SEQUENCE ALIGNMENT  (key-independent)")
    print("-" * 74)
    print(f"  Disc sign-position tags ({len(DISC_SIGN_POS_TAGS)} tokens):")
    for i, (word, tags_slice) in enumerate(
        zip(DISC_WORDS,
            [DISC_SIGN_POS_TAGS[sum(len(w) for w in DISC_WORDS[:i]):
                                sum(len(w) for w in DISC_WORDS[:i+1])]
             for i in range(len(DISC_WORDS))])):
        print(f"    W{i+1:02d}: {' '.join(tags_slice)}")
    print()

    part_a = {}
    for name, text in corpora.items():
        if not text:
            print(f"  [{name}] SKIP (corpus not loaded)")
            continue
        target_pos = corpus_char_pos_tags(text, n=target_n * 5)
        print(f"  [{name}]: {len(target_pos)} target char-position tags "
              f"(first 6: {target_pos[:6]})")
        obs, null_mean, p = mc_pvalue(DISC_SIGN_POS_TAGS, target_pos,
                                      sign_pos_score, n_mc=n_mc)
        part_a[name] = {"obs": round(obs,4), "null_mean": round(null_mean,4), "p": round(p,4)}
        print(f"    obs={obs:.4f}  null={null_mean:.4f}  "
              f"excess={obs-null_mean:+.4f}  p={p:.4f} {_sig(p)}")
    print()

    # ── Part B: phonetic syllable alignment ───────────────────────────────────
    print("[B] G_LUWIAN PHONETIC SYLLABLE ALIGNMENT  [KEY-DEPENDENT]")
    print("-" * 74)
    print(f"  Disc syllables ({len(DISC_PHON)}): {' '.join(DISC_PHON[:25])} ...")
    print()

    part_b = {}
    for name, text in corpora.items():
        if not text:
            continue
        target_syls = corpus_syllables(text, n=target_n)
        print(f"  [{name}]: {len(target_syls)} syllables "
              f"(first 8: {target_syls[:8]})")
        obs, null_mean, p = mc_pvalue(DISC_PHON, target_syls,
                                      phon_score, n_mc=n_mc)
        part_b[name] = {"obs": round(obs,4), "null_mean": round(null_mean,4), "p": round(p,4)}
        print(f"    obs={obs:.4f}  null={null_mean:.4f}  "
              f"excess={obs-null_mean:+.4f}  p={p:.4f} {_sig(p)}")
    print()

    # ── Summary ───────────────────────────────────────────────────────────────
    print("=" * 74)
    print("  SUMMARY — ALGORITHM #4: MORPHOLOGICAL SMITH-WATERMAN")
    print("=" * 74)

    print("\n  [A] Sign-position alignment (higher obs = disc sign-position sequence")
    print("      matches corpus word-structure patterns better than random order):")
    print(f"  {'Corpus':<22} {'obs':>7} {'null':>7} {'excess':>8} {'p':>7}  sig")
    print("  " + "-" * 56)
    for name, r in sorted(part_a.items(), key=lambda x: -x[1]["obs"]):
        excess = r['obs'] - r['null_mean']
        print(f"  {name:<22} {r['obs']:>7.4f} {r['null_mean']:>7.4f} "
              f"{excess:>+8.4f} {r['p']:>7.4f}  {_sig(r['p'])}")

    print(f"\n  [B] Phonetic alignment [KEY-DEPENDENT: G_LUWIAN]")
    print(f"  {'Corpus':<22} {'obs':>7} {'null':>7} {'excess':>8} {'p':>7}  sig")
    print("  " + "-" * 56)
    for name, r in sorted(part_b.items(), key=lambda x: -x[1]["obs"]):
        excess = r['obs'] - r['null_mean']
        print(f"  {name:<22} {r['obs']:>7.4f} {r['null_mean']:>7.4f} "
              f"{excess:>+8.4f} {r['p']:>7.4f}  {_sig(r['p'])}")

    print("\n  Significance: *** p<0.001  ** p<0.01  * p<0.05")
    print("  [B] uses G_LUWIAN phonetic key — MUST be labeled KEY-DEPENDENT in paper")

    with open("smith_waterman_results.json", "w", encoding="utf-8") as f:
        json.dump({"part_a": part_a, "part_b": part_b,
                   "disc_sign_pos_tags": DISC_SIGN_POS_TAGS,
                   "disc_phon_tokens": DISC_PHON,
                   "n_mc": n_mc, "target_n": target_n}, f, indent=2)
    print("\n  Saved -> smith_waterman_results.json")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--fast", action="store_true",
                    help="200 MC, target=500 (quick test)")
    ap.add_argument("--phon-only", action="store_true",
                    help="1000 MC, target=2000 syllables")
    args = ap.parse_args()

    if args.fast:
        print("[FAST MODE] 200 MC, target=500\n")
        run(n_mc=200, target_n=500)
    elif args.phon_only:
        print("[PHONETIC ONLY] 1000 MC, target=2000 syllables\n")
        run(n_mc=1000, target_n=2000)
    else:
        run(n_mc=N_MC, target_n=TARGET_N)
