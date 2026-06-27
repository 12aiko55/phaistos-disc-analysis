"""
phaistos_ncd_phylogenetic.py  -  Algorithm #1: Phylogenetic NCD + C3
=====================================================================
Three compression-based metrics for structural language affinity,
ALL 100% phonetic-key-independent (except where explicitly labeled).

METRIC 1 - NCD (Normalized Compression Distance)
  Cilibrasi & Vitanyi 2005, IEEE Trans. Inf. Theory 51(4).
  NCD(X,Y) = [C(XY) - min(C(X),C(Y))] / max(C(X),C(Y))
  Lower = more similar. Works best for texts of comparable size.
  Limitation: disc (845 chars) << corpora -> statistical power is low.

METRIC 2 - C3 (Cross-Corpus Compression Score)  [PRIMARY]
  New metric, better suited for short probe vs long reference.
  C3(disc, corpus) = [C(context + disc) - C(context)] / C(disc)
  context = first CONTEXT_CHARS chars of corpus (50 KB default).
  Lower C3 = corpus model better predicts disc = more structural affinity.
  Equivalent to corpus cross-entropy of disc, approximated by LZMA.

METRIC 3 - NCD_phonetic  [LABELED: uses G_LUWIAN key]
  Same as NCD but disc is rendered in Achterberg/G_LUWIAN phonetic syllables.
  Directly tests whether the Luwian reading produces text structurally
  similar to real Luwian ritual corpora.
  ** This metric is KEY-DEPENDENT and must be labeled as such in the paper. **

Corpora:
  1. luwian_ritual  TLHdig CTH 758-763 (Kuwattalla/Puriyanni, Luwian lines)
  2. luwian_all     All Luwian-language lines in TLHdig
  3. hittite        All Hittite-language lines in TLHdig
  4. linear_b       Linear B tablet corpus

Usage:
  python phaistos_ncd_phylogenetic.py           # full run (1000 MC)
  python phaistos_ncd_phylogenetic.py --fast    # quick (200 MC)
  python phaistos_ncd_phylogenetic.py --rebuild # force TLHdig re-parse
"""

import argparse
import json
import lzma
import random
import re
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Tuple

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT       = Path(__file__).parent
CORPUS_DIR = ROOT / "corpora"
TLHDIG_DIR = ROOT / "TLHdig_corpus" / "TLHbasisONLINE25.1_ZENODO"
CACHE_DIR  = ROOT / "__pycache__"

RITUAL_CTH = {758, 759, 760, 761, 762, 763}

# ---------------------------------------------------------------------------
# Parameters
# ---------------------------------------------------------------------------
N_MC          = 1000   # Monte Carlo iterations
N_SAMPLES     = 10     # corpus windows per NCD measurement
NCD_CHARS     = 8000   # chars per NCD corpus window
CONTEXT_CHARS = 50000  # chars of corpus context for C3
LZMA_PRESET   = 6

# ---------------------------------------------------------------------------
# 1.  Phaistos Disc data + representations
# ---------------------------------------------------------------------------
sys.path.insert(0, str(ROOT))
from phaistos_canonical_data import SIDE_A_EVANS, SIDE_B_EVANS

# G_LUWIAN phonetic key (Achterberg/Best/Woudhuizen, as used in paper)
G_LUWIAN = {
    2:  "za",    # PLUMED HEAD - demonstrative
    36: "wa",    # BATON - water
    11: "tar",   # COMB - water
    22: "ha",    # HELMET - affirmative particle
    7:  "ti",    # FOOT - copula/Tiwat syllable
    29: "na",    # TROWEL - connective
    6:  "an",    # conjunction
    12: "zi",    # SHIELD - particle
    45: "tiwa",  # ROSETTE - Tiwat (sun deity)
    1:  "i",     # PEDESTRIAN - connective vowel
}

DISC_WORDS  = SIDE_A_EVANS + SIDE_B_EVANS
DISC_TOKENS = [s for w in DISC_WORDS for s in w]


def tokens_to_text(tokens: List[int]) -> str:
    """Numeric representation: '02 12 13 01 18'"""
    return " ".join(f"{t:02d}" for t in tokens)


def word_groups_to_text(groups: List[List[int]]) -> str:
    """Word-delimited numeric: '02 12 13 | 24 40 | ...'"""
    return " | ".join(" ".join(f"{s:02d}" for s in w) for w in groups)


def phonetic_text(groups: List[List[int]], key: Dict[int, str] = None) -> str:
    """
    Render disc using phonetic key.
    Unknown signs rendered as 'X<nn>' to preserve sequence length.
    """
    if key is None:
        key = G_LUWIAN
    words = []
    for w in groups:
        syls = [key.get(s, f"x{s:02d}") for s in w]
        words.append("-".join(syls))
    return " ".join(words)


DISC_TEXT_NUM   = word_groups_to_text(DISC_WORDS)   # key-independent
DISC_TEXT_PHO   = phonetic_text(DISC_WORDS)          # G_LUWIAN phonetic

# ---------------------------------------------------------------------------
# 2.  LZMA helpers
# ---------------------------------------------------------------------------
def _compress(data: bytes) -> int:
    return len(lzma.compress(data, preset=LZMA_PRESET))


def ncd(x: bytes, y: bytes) -> float:
    cx  = _compress(x)
    cy  = _compress(y)
    cxy = _compress(x + b" " + y)
    return (cxy - min(cx, cy)) / max(cx, cy)


def ncd_text(disc: str, corpus: str) -> float:
    return ncd(disc.encode("utf-8"), corpus.encode("utf-8"))


def c3_single(disc_text: str, context_text: str) -> float:
    """
    Cross-Corpus Compression score for a single context window.
    C3 = [C(context + disc) - C(context)] / C(disc)
    Lower = context provides better compression for disc.
    """
    disc_b    = disc_text.encode("utf-8")
    context_b = context_text.encode("utf-8")
    c_ctx     = _compress(context_b)
    c_ctx_d   = _compress(context_b + b" " + disc_b)
    c_disc    = _compress(disc_b)
    return (c_ctx_d - c_ctx) / max(c_disc, 1)


def mean_c3(disc_text: str, corpus_text: str,
            context_chars: int, n_samples: int,
            seed: int = 0) -> Tuple[float, float]:
    """
    Average C3 over n_samples random corpus windows.
    Eliminates bias from position within corpus.
    """
    rng    = random.Random(seed)
    scores = []
    for _ in range(n_samples):
        max_start = max(0, len(corpus_text) - context_chars)
        start     = rng.randint(0, max_start) if max_start > 0 else 0
        ctx       = corpus_text[start: start + context_chars]
        scores.append(c3_single(disc_text, ctx))
    mu  = sum(scores) / len(scores)
    std = (sum((s - mu) ** 2 for s in scores) / len(scores)) ** 0.5
    return mu, std


# ---------------------------------------------------------------------------
# 3.  TLHdig XML parser + disk cache
# ---------------------------------------------------------------------------
def _word_text(elem) -> str:
    """
    Extract transliteration from <w> element.
    Format A: <w trans="word" ...>  -> use trans= attribute
    Format B: <w>word</w>           -> use text content (ritual texts)
    """
    trans = (elem.get("trans") or "").strip()
    if trans and not trans.startswith("%"):
        return trans
    parts = [t.strip() for t in elem.itertext() if t.strip()]
    raw = " ".join(parts).strip()
    return raw if raw and not raw.startswith("%") else ""


def _parse_tlhdig_folder(folder: Path, lang_filter: str = None) -> List[str]:
    words = []
    for xml_file in folder.glob("*.xml"):
        try:
            content = xml_file.read_text(encoding="utf-8", errors="replace")
            root = ET.fromstring(content)
            current_lang = None
            for elem in root.iter():
                tag = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
                if tag == "lb":
                    lg = elem.get("lg")
                    if lg:
                        current_lang = lg
                elif tag == "w":
                    w_lg = elem.get("lg") or current_lang
                    if lang_filter is not None and w_lg != lang_filter:
                        continue
                    word = _word_text(elem)
                    if word:
                        words.append(word)
        except Exception:
            pass
    return words


def _cache_path(name: str) -> Path:
    CACHE_DIR.mkdir(exist_ok=True)
    return CACHE_DIR / f"ncd_cache_{name}.txt"


def load_or_build_tlhdig(name: str, cth_filter=None,
                         lang_filter=None, rebuild=False) -> str:
    cp = _cache_path(name)
    if cp.exists() and not rebuild:
        return cp.read_text(encoding="utf-8")

    print(f"  [TLHdig] Building '{name}' (may take a few minutes)...")
    all_words: List[str] = []
    folders = sorted(TLHDIG_DIR.iterdir())
    counted = [f for f in folders if f.is_dir()]
    total   = len(counted)
    done    = 0

    for folder in folders:
        if not folder.is_dir():
            continue
        m = re.match(r"CTH (\d+)_XML", folder.name)
        if not m:
            continue
        cth_num = int(m.group(1))
        if cth_filter is not None and cth_num not in cth_filter:
            continue
        all_words.extend(_parse_tlhdig_folder(folder, lang_filter))
        done += 1
        if done % 50 == 0:
            pct = 100 * done / max(total, 1)
            print(f"    {done}/{total} folders ({pct:.0f}%)  {len(all_words):,} words",
                  end="\r", flush=True)

    print()
    text = " ".join(all_words)
    cp.write_text(text, encoding="utf-8")
    print(f"  [TLHdig] '{name}': {len(all_words):,} words -> {len(text):,} chars (cached)")
    return text


# ---------------------------------------------------------------------------
# 4.  Embedded corpus loaders
# ---------------------------------------------------------------------------
def load_embedded(path: Path) -> str:
    if not path.exists():
        return ""
    lines = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            lines.append(line)
    return " ".join(lines)


def load_linearb() -> str:
    cp = _cache_path("linear_b")
    if cp.exists():
        return cp.read_text(encoding="utf-8")
    texts = []
    for p in [CORPUS_DIR / "linearb" / "linearb_embedded.txt",
              CORPUS_DIR / "linearb" / "tablets.csv"]:
        if p.exists():
            texts.append(load_embedded(p))
    text = " ".join(texts)
    if text:
        cp.write_text(text, encoding="utf-8")
    return text


# ---------------------------------------------------------------------------
# 5.  Sampling
# ---------------------------------------------------------------------------
def sample_corpus(text: str, n_chars: int, rng: random.Random) -> str:
    if len(text) <= n_chars:
        return text
    start = rng.randint(0, len(text) - n_chars)
    return text[start: start + n_chars]


# ---------------------------------------------------------------------------
# 6.  NCD with averaging
# ---------------------------------------------------------------------------
def mean_ncd(disc_text: str, corpus_text: str,
             n_samples: int, sample_chars: int,
             seed: int = 0) -> Tuple[float, float]:
    rng    = random.Random(seed)
    scores = [ncd_text(disc_text, sample_corpus(corpus_text, sample_chars, rng))
              for _ in range(n_samples)]
    mu  = sum(scores) / len(scores)
    std = (sum((s - mu) ** 2 for s in scores) / len(scores)) ** 0.5
    return mu, std


# ---------------------------------------------------------------------------
# 7.  Monte Carlo null (shuffled disc)
# ---------------------------------------------------------------------------
def monte_carlo_null_ncd(disc_tokens: List[int], corpus_text: str,
                         n_iter: int, sample_chars: int) -> List[float]:
    tokens = disc_tokens.copy()
    rng    = random.Random(42)
    nulls  = []
    for i in range(n_iter):
        rng.shuffle(tokens)
        shuffled = tokens_to_text(tokens)
        corpus_s = sample_corpus(corpus_text, sample_chars, rng)
        nulls.append(ncd_text(shuffled, corpus_s))
        if (i + 1) % 250 == 0:
            print(f"    MC {i+1}/{n_iter}...", end="\r", flush=True)
    print(" " * 40, end="\r")
    return nulls


def monte_carlo_null_c3(disc_tokens: List[int], corpus_text: str,
                        n_iter: int, context_chars: int,
                        n_samples: int = 3) -> List[float]:
    tokens = disc_tokens.copy()
    rng    = random.Random(42)
    nulls  = []
    for i in range(n_iter):
        rng.shuffle(tokens)
        shuffled = tokens_to_text(tokens)
        score, _ = mean_c3(shuffled, corpus_text, context_chars, n_samples,
                           seed=rng.randint(0, 99999))
        nulls.append(score)
        if (i + 1) % 250 == 0:
            print(f"    MC {i+1}/{n_iter}...", end="\r", flush=True)
    print(" " * 40, end="\r")
    return nulls


def p_value_lower(observed: float, null_dist: List[float]) -> float:
    """p = fraction of nulls <= observed (one-tailed: lower is better)."""
    return sum(1 for x in null_dist if x <= observed) / len(null_dist)


# ---------------------------------------------------------------------------
# 8.  Main
# ---------------------------------------------------------------------------
def build_corpora(rebuild: bool) -> Dict[str, str]:
    print("\n[1/2] Loading corpora...")
    c: Dict[str, str] = {}
    c["luwian_ritual"] = load_or_build_tlhdig(
        "luwian_ritual", cth_filter=RITUAL_CTH, lang_filter="Luw", rebuild=rebuild)
    c["luwian_all"]    = load_or_build_tlhdig(
        "luwian_all",    cth_filter=None,        lang_filter="Luw", rebuild=rebuild)
    c["hittite"]       = load_or_build_tlhdig(
        "hittite",       cth_filter=None,        lang_filter="Hit", rebuild=rebuild)
    c["linear_b"]      = load_linearb()

    print("\n  Corpus sizes:")
    for name, text in c.items():
        print(f"    {name:<20} {len(text):>12,} chars")
    return c


def run(n_mc: int, n_samples: int, ncd_chars: int,
        context_chars: int, rebuild: bool):

    print("=" * 68)
    print("  PHAISTOS DISC - COMPRESSION-BASED PHYLOGENETIC ANALYSIS")
    print("=" * 68)
    print(f"  Disc numeric    : {len(DISC_TEXT_NUM)} chars  ({len(DISC_TOKENS)} tokens)")
    print(f"  Disc phonetic   : {len(DISC_TEXT_PHO)} chars  (G_LUWIAN key)")
    print(f"  LZMA preset     : {LZMA_PRESET}")
    print(f"  NCD windows     : {n_samples} x {ncd_chars} chars")
    print(f"  C3 context      : {context_chars:,} chars (50 KB)")
    print(f"  Monte Carlo     : {n_mc} iterations per metric per corpus")

    corpora = build_corpora(rebuild)

    MIN_NCD = ncd_chars       # corpus must be >= window size for NCD
    MIN_C3  = context_chars   # corpus must be >= context for C3

    print("\n[2/2] Computing metrics + Monte Carlo p-values...\n")

    results = []
    for name, text in corpora.items():
        print(f"  [{name}]")
        t0 = time.time()

        # --- NCD (key-independent) ---
        ncd_ok = len(text) >= MIN_NCD
        if ncd_ok:
            print(f"    NCD...", end=" ", flush=True)
            ncd_mu, ncd_std = mean_ncd(DISC_TEXT_NUM, text, n_samples, ncd_chars)
            ncd_null = monte_carlo_null_ncd(DISC_TOKENS, text, n_mc, ncd_chars)
            ncd_pv   = p_value_lower(ncd_mu, ncd_null)
            print(f"NCD={ncd_mu:.4f}+/-{ncd_std:.4f} p={ncd_pv:.4f}")
        else:
            ncd_mu = ncd_std = ncd_pv = float("nan")
            print(f"    NCD: SKIP (corpus {len(text):,} < {MIN_NCD:,} chars)")

        # --- C3 (key-independent) ---
        c3_ok = len(text) >= MIN_C3
        if c3_ok:
            print(f"    C3...", end=" ", flush=True)
            c3_obs, c3_std = mean_c3(DISC_TEXT_NUM, text, context_chars, n_samples)
            c3_null  = monte_carlo_null_c3(DISC_TOKENS, text, n_mc,
                                           context_chars, n_samples=3)
            c3_pv    = p_value_lower(c3_obs, c3_null)
            c3_null_mu = sum(c3_null) / len(c3_null)
            print(f"C3={c3_obs:.4f}+/-{c3_std:.4f} (null={c3_null_mu:.4f}) p={c3_pv:.4f}")
        else:
            c3_obs = c3_std = c3_pv = c3_null_mu = float("nan")
            print(f"    C3: SKIP (corpus {len(text):,} < {MIN_C3:,} chars)")

        # --- NCD phonetic (key-dependent, G_LUWIAN) ---
        pho_ok = len(text) >= MIN_NCD
        if pho_ok:
            print(f"    NCD_pho...", end=" ", flush=True)
            pho_mu, pho_std = mean_ncd(DISC_TEXT_PHO, text, n_samples, ncd_chars)
            # Null: shuffle phonetic tokens
            pho_tokens = DISC_TEXT_PHO.split()
            def _pho_null(n_iter):
                toks = pho_tokens.copy()
                rng  = random.Random(42)
                out  = []
                for i in range(n_iter):
                    rng.shuffle(toks)
                    s = " ".join(toks)
                    cw = sample_corpus(text, ncd_chars, rng)
                    out.append(ncd_text(s, cw))
                    if (i + 1) % 250 == 0:
                        print(f"    MC {i+1}/{n_iter}...", end="\r", flush=True)
                print(" " * 40, end="\r")
                return out
            pho_null = _pho_null(n_mc)
            pho_pv   = p_value_lower(pho_mu, pho_null)
            print(f"NCD_pho={pho_mu:.4f}+/-{pho_std:.4f} p={pho_pv:.4f}")
        else:
            pho_mu = pho_std = pho_pv = float("nan")

        elapsed = time.time() - t0
        print(f"    done in {elapsed:.1f}s\n")

        results.append({
            "corpus":    name,
            "ncd_mu":    ncd_mu,   "ncd_std":  ncd_std,   "ncd_p":  ncd_pv,
            "c3":        c3_obs,   "c3_std":   c3_std,   "c3_p":     c3_pv,
            "pho_mu":    pho_mu,   "pho_std":  pho_std,   "pho_p":  pho_pv,
        })

    # -----------------------------------------------------------------------
    # Print ranked tables
    # -----------------------------------------------------------------------
    def sig(p):
        if p != p: return "   "   # nan
        return "***" if p < 0.001 else "** " if p < 0.01 else "*  " if p < 0.05 else "   "

    print("=" * 68)
    print("  TABLE 1 - NCD (key-independent, structural distance)")
    print("  Lower = more similar  |  p = P(null <= obs)")
    print("=" * 68)
    ranked = sorted(results, key=lambda r: r["ncd_mu"])
    print(f"  {'Rank':<5} {'Corpus':<20} {'NCD':>7} {'+-':>6} {'p':>8}")
    print("  " + "-" * 48)
    for i, r in enumerate(ranked, 1):
        if r["ncd_mu"] != r["ncd_mu"]: continue
        print(f"  {i:<5} {r['corpus']:<20} {r['ncd_mu']:>7.4f} {r['ncd_std']:>6.4f}"
              f" {r['ncd_p']:>8.4f} {sig(r['ncd_p'])}")

    print()
    print("=" * 68)
    print("  TABLE 2 - C3 (Cross-Corpus Compression, 50KB context)")
    print("  Lower = corpus better predicts disc  |  p = P(null <= obs)")
    print("=" * 68)
    ranked_c3 = sorted(results, key=lambda r: r["c3"] if r["c3"] == r["c3"] else 99)
    print(f"  {'Rank':<5} {'Corpus':<20} {'C3':>7} {'+-':>6} {'p':>8}")
    print("  " + "-" * 50)
    for i, r in enumerate(ranked_c3, 1):
        if r["c3"] != r["c3"]: continue
        print(f"  {i:<5} {r['corpus']:<20} {r['c3']:>7.4f} {r['c3_std']:>6.4f}"
              f" {r['c3_p']:>8.4f} {sig(r['c3_p'])}")

    print()
    print("=" * 68)
    print("  TABLE 3 - NCD_phonetic [KEY-DEPENDENT: uses G_LUWIAN]")
    print("  Tests: does G_LUWIAN reading look like real Luwian text?")
    print("=" * 68)
    ranked_p = sorted(results, key=lambda r: r["pho_mu"] if r["pho_mu"] == r["pho_mu"] else 99)
    print(f"  {'Rank':<5} {'Corpus':<20} {'NCD_pho':>8} {'+-':>6} {'p':>8}")
    print("  " + "-" * 50)
    for i, r in enumerate(ranked_p, 1):
        if r["pho_mu"] != r["pho_mu"]: continue
        print(f"  {i:<5} {r['corpus']:<20} {r['pho_mu']:>8.4f} {r['pho_std']:>6.4f}"
              f" {r['pho_p']:>8.4f} {sig(r['pho_p'])}")

    print()
    print("  Significance: *** p<0.001  ** p<0.01  * p<0.05")
    print("  p = fraction of shuffled-disc NCDs <= observed")
    print("  (small p -> disc IS more similar to this corpus than chance)")

    # Save JSON
    out = ROOT / "ncd_results.json"
    out.write_text(json.dumps({
        "params": {
            "n_mc": n_mc, "n_samples": n_samples,
            "ncd_chars": ncd_chars, "context_chars": context_chars,
            "lzma_preset": LZMA_PRESET,
            "disc_tokens": len(DISC_TOKENS),
        },
        "results": results,
    }, indent=2, default=str), encoding="utf-8")
    print(f"\n  Results saved -> ncd_results.json")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--fast",    action="store_true",
                        help="200 MC, 3 samples (quick test)")
    parser.add_argument("--rebuild", action="store_true",
                        help="Force TLHdig corpus re-parse")
    args = parser.parse_args()

    if args.fast:
        N_MC = 200; N_SAMPLES = 3; NCD_CHARS = 6000
        print("[FAST MODE] 200 MC, 3 samples")

    run(N_MC, N_SAMPLES, NCD_CHARS, CONTEXT_CHARS, args.rebuild)
