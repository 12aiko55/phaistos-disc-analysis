#!/usr/bin/env python3
"""
phaistos_fingerprint.py  —  Algorithm #5: Bigram Context Inference
Complete phonetic key for all disc signs via Luwian bigram propagation.

The childlike idea:
  If I know what signs appear LEFT and RIGHT of sign X, and I know the
  phonetic values of those neighbours, then I ask the Luwian corpus:
  "What syllable most often appears BETWEEN [left_syl] and [right_syl]?"
  That syllable is X's phonetic value.

  10 known G_LUWIAN signs are anchors.
  For each unknown sign, score every Luwian syllable by how well it fits
  between the known neighbours. Iteratively extend as new values are pinned.
  Confidence = how much better the winner is than the runner-up.
"""
import sys, re, json, math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Tuple, Optional

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ── Disc data (Evans/Godart) ───────────────────────────────────────────────────
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
DISC_WORDS  = SIDE_A_EVANS + SIDE_B_EVANS
DISC_TOKENS = [s for w in DISC_WORDS for s in w]

G_LUWIAN = {2:"za", 36:"wa", 11:"tar", 22:"ha", 7:"ti",
            29:"na", 6:"an", 12:"zi", 45:"tiwa", 1:"i"}

CACHE_DIR = Path(__file__).parent / "__pycache__"

# ── Normalisation ─────────────────────────────────────────────────────────────
_NORM  = str.maketrans("ḫšḥāēīūáéíóú", "hssaeiuaeiou")
_DIGIT = re.compile(r'\d+')
_NAL   = re.compile(r'[^a-z]')

def _nsyl(s: str) -> str:
    s = s.lower().translate(_NORM)
    s = _DIGIT.sub("", s)
    return _NAL.sub("", s)


# ── Disc sign statistics ───────────────────────────────────────────────────────
def disc_stats() -> Dict[int, Dict]:
    """For each disc sign: frequency, positions, left/right bigram counters."""
    freq   = Counter(DISC_TOKENS)
    n      = len(DISC_TOKENS)
    rank   = {s: i for i,(s,_) in enumerate(freq.most_common())}
    bl: Dict[int,Counter] = defaultdict(Counter)
    br: Dict[int,Counter] = defaultdict(Counter)
    p_init = Counter(); p_fin = Counter(); pos_n = Counter()

    for word in DISC_WORDS:
        wlen = len(word)
        for idx, sign in enumerate(word):
            pos_n[sign] += 1
            if idx == 0:          p_init[sign] += 1
            if idx == wlen - 1:   p_fin[sign]  += 1
            if idx > 0:           bl[sign][word[idx-1]] += 1
            if idx < wlen - 1:    br[sign][word[idx+1]] += 1

    out = {}
    for sign in sorted(set(DISC_TOKENS)):
        tot = max(pos_n[sign], 1)
        out[sign] = dict(
            freq=freq[sign], n=n,
            rank=rank[sign], rank_norm=rank[sign]/max(len(rank)-1,1),
            p_init=p_init[sign]/tot, p_fin=p_fin[sign]/tot,
            bl=dict(bl[sign]), br=dict(br[sign]),
            n_left=len(bl[sign]), n_right=len(br[sign]),
        )
    return out


# ── Luwian syllable bigram matrix ─────────────────────────────────────────────
def luwian_bigrams(corpus_text: str, min_count: int = 3
                   ) -> Tuple[Dict, List[str], Counter]:
    """
    Parse corpus into syllable sequences and build a bigram transition matrix.
    Returns: {syl: {right_syl: count}}, sorted_syllable_list, freq_counter
    """
    word_units = []
    for tok in corpus_text.split():
        if tok == tok.upper() and tok.isalpha() and len(tok) > 1:
            continue                              # skip Sumerograms
        parts = [_nsyl(p) for p in tok.split("-")]
        _GARBAGE = {"x","n","m","d","w","v","q","utu","dingir","lugal","iz","ez","ik","kan","har","mn","ksi","arha","kuit","ar"}
        # allow single vowels (a,e,i,u,o); drop single consonants and garbage
        parts = [p for p in parts if
                 (len(p) == 1 and p in "aeiou") or
                 (2 <= len(p) <= 5 and p not in _GARBAGE)]
        if parts:
            word_units.append(parts)

    freq = Counter(s for u in word_units for s in u)
    valid = {s for s,c in freq.items() if c >= min_count}

    # Bigram matrix: right[a][b] = P(b | a)
    right: Dict[str, Counter] = defaultdict(Counter)
    left:  Dict[str, Counter] = defaultdict(Counter)
    for unit in word_units:
        unit = [s for s in unit if s in valid]
        for i in range(len(unit)-1):
            right[unit[i]][unit[i+1]] += 1
            left[unit[i+1]][unit[i]]  += 1

    sorted_syls = sorted(valid, key=lambda s: -freq[s])
    return dict(right), dict(left), sorted_syls, freq


# ── Bigram context score ───────────────────────────────────────────────────────
def context_score(sign: int, cand_syl: str,
                  mapping: Dict[int, str],
                  disc: Dict, luw_right: Dict, luw_left: Dict,
                  luw_freq: Counter) -> float:
    """
    How well does 'cand_syl' fit into the bigram context of disc sign X?

    Score = Σ_{known left neighbour L} w_L × P_luw(σ(L) → cand_syl)
          + Σ_{known right neighbour R} w_R × P_luw(cand_syl → σ(R))

    Weights proportional to co-occurrence count with X in the disc.
    """
    score = 0.0

    # Left context: known predecessors
    for pred, cnt in disc[sign]["bl"].items():
        psyl = mapping.get(pred)
        if not psyl: continue
        right_from_psyl = luw_right.get(psyl, {})
        total = sum(right_from_psyl.values()) or 1
        p = right_from_psyl.get(cand_syl, 0) / total
        # Weight by how often this predecessor appears next to sign
        w = cnt / max(sum(disc[sign]["bl"].values()), 1)
        score += w * p * math.log1p(luw_freq.get(cand_syl, 0))

    # Right context: known successors
    for succ, cnt in disc[sign]["br"].items():
        ssyl = mapping.get(succ)
        if not ssyl: continue
        left_to_ssyl = luw_left.get(ssyl, {})
        total = sum(left_to_ssyl.values()) or 1
        p = left_to_ssyl.get(cand_syl, 0) / total
        w = cnt / max(sum(disc[sign]["br"].values()), 1)
        score += w * p * math.log1p(luw_freq.get(cand_syl, 0))

    return score


# ── Calibration: verify G_LUWIAN on known pairs ───────────────────────────────
def calibrate(disc: Dict, luw_right: Dict, luw_left: Dict,
              luw_freq: Counter, all_syls: List[str]) -> List[Dict]:
    # Use leave-one-out: for each known sign, pretend it's unknown
    rows = []
    for sign, true_syl in sorted(G_LUWIAN.items()):
        ref = "ti" if true_syl == "tiwa" else true_syl
        # Mapping WITHOUT this sign
        partial = {s: v for s,v in G_LUWIAN.items()
                   if s != sign and v != "tiwa"}

        scores = {}
        for cand in all_syls[:200]:           # top-200 syls for speed
            scores[cand] = context_score(sign, cand, partial,
                                         disc, luw_right, luw_left, luw_freq)

        sorted_cands = sorted(scores, key=lambda s: -scores[s])
        rank_of_true = next((i for i,s in enumerate(sorted_cands) if s == ref), 200)
        score_true   = scores.get(ref, 0.0)
        score_best   = scores.get(sorted_cands[0], 0.0) if sorted_cands else 0.0
        top3 = sorted_cands[:3]

        rows.append(dict(
            sign=sign, true_syl=true_syl, ref=ref,
            rank=rank_of_true, score_true=round(score_true,6),
            score_best=round(score_best,6),
            top3=top3,
        ))
    return rows


def calibration_pvalue(calib_rows: List[Dict], n_candidates: int = 200) -> Dict:
    """
    Null hypothesis: each calibration rank is uniform in [0, n_candidates).
    Two tests:
      (A) Binomial: P(X >= observed_top10 | n signs, p=10/n_candidates)
      (B) Z-test on mean rank: (observed_mean - expected_mean) / SE
    """
    from math import comb, sqrt, erf
    n = len(calib_rows)
    observed_top10 = sum(1 for r in calib_rows if r["rank"] < 10)
    observed_top20 = sum(1 for r in calib_rows if r["rank"] < 20)
    ranks = [r["rank"] for r in calib_rows]
    observed_mean = sum(ranks) / max(n, 1)

    # (A) Binomial P(X >= k)
    p_per = 10 / n_candidates
    def binom_cdf_lt(k_excl):
        return sum(comb(n, i) * (p_per**i) * ((1-p_per)**(n-i))
                   for i in range(k_excl))
    p_binom_top10 = 1.0 - binom_cdf_lt(observed_top10)

    p_per20 = 20 / n_candidates
    def binom_cdf_lt20(k_excl):
        return sum(comb(n, i) * (p_per20**i) * ((1-p_per20)**(n-i))
                   for i in range(k_excl))
    p_binom_top20 = 1.0 - binom_cdf_lt20(observed_top20)

    # (B) Z-test on mean rank; null: uniform over [0, n_candidates)
    expected_mean = (n_candidates - 1) / 2        # ~99.5 for 200 candidates
    var_single    = (n_candidates**2 - 1) / 12    # variance of discrete uniform
    se_mean       = sqrt(var_single / n)
    z = (observed_mean - expected_mean) / se_mean
    # one-sided p (lower tail): P(mean_rank <= observed | H0)
    p_z = (1 + erf(z / sqrt(2))) / 2             # Φ(z)

    return dict(
        n_candidates=n_candidates,
        observed_top10=observed_top10,
        observed_top20=observed_top20,
        observed_mean_rank=round(observed_mean, 1),
        null_expected_mean_rank=round(expected_mean, 1),
        p_binom_top10=round(p_binom_top10, 4),
        p_binom_top20=round(p_binom_top20, 4),
        z_mean_rank=round(z, 2),
        p_z_mean_rank=round(p_z, 6),
    )


# ── Greedy inference for unknown signs ────────────────────────────────────────
def infer_unknown(disc: Dict, luw_right: Dict, luw_left: Dict,
                  luw_freq: Counter, all_syls: List[str],
                  unknown_signs: List[int],
                  n_iter: int = 3) -> Dict[int, Dict]:
    """
    Iterative greedy inference:
    - Start with G_LUWIAN anchors
    - Assign most confident unknown sign first
    - Use new assignments as anchors for the next round
    - Repeat n_iter times
    """
    mapping = {s: (v if v != "tiwa" else "tiwa")
               for s, v in G_LUWIAN.items()}
    # Flatten tiwa → use "tiwa" as the string value but also allow "ti"
    read_map = dict(mapping)

    used_syls = set(G_LUWIAN.values())
    avail     = [s for s in all_syls if s not in used_syls]

    assignments: Dict[int, Dict] = {}
    remaining = [s for s in unknown_signs if s in disc]

    for iteration in range(n_iter):
        changed = False
        if not remaining: break

        # Score all remaining signs × available syllables
        sign_scores: Dict[int, Dict[str,float]] = {}
        for sign in remaining:
            ss = {}
            for cand in avail[:300]:              # top-300 candidates
                ss[cand] = context_score(sign, cand, read_map,
                                         disc, luw_right, luw_left, luw_freq)
            sign_scores[sign] = ss

        # Pick the assignment with the highest CONFIDENCE (score_best / score_2nd)
        best_sign = best_syl = None
        best_conf = -1.0
        for sign in remaining:
            ss = sign_scores[sign]
            top2 = sorted(ss, key=lambda s: -ss[s])[:2]
            if not top2: continue
            s1, d1 = top2[0], ss[top2[0]]
            d2 = ss[top2[1]] if len(top2) > 1 else d1 * 0.5
            if d1 <= 0: continue
            conf = (d1 - d2) / (d1 + 1e-12)
            if conf > best_conf:
                best_conf = conf
                best_sign = sign
                best_syl  = s1

        if best_sign is None: break

        # Commit this assignment
        ss = sign_scores[best_sign]
        top_syls = sorted(ss, key=lambda s: -ss[s])[:3]
        assignments[best_sign] = dict(
            syl=best_syl,
            score=round(ss.get(best_syl,0), 6),
            score2=round(ss.get(top_syls[1],0) if len(top_syls)>1 else 0, 6),
            confidence=round(best_conf, 4),
            top3=top_syls[:3],
            iteration=iteration+1,
        )
        read_map[best_sign] = best_syl
        avail.remove(best_syl)
        remaining.remove(best_sign)
        changed = True

        # Assign ALL remaining signs in this iteration by greedy order
        while remaining and avail:
            # Re-score using newly added mapping
            best_sign2 = best_syl2 = None
            best_conf2 = -1.0
            for sign in remaining:
                ss2 = {}
                for cand in avail[:300]:
                    ss2[cand] = context_score(sign, cand, read_map,
                                              disc, luw_right, luw_left, luw_freq)
                top2 = sorted(ss2, key=lambda s: -ss2[s])[:2]
                if not top2: continue
                s1 = top2[0]; d1 = ss2[s1]
                d2 = ss2[top2[1]] if len(top2)>1 else d1*0.5
                if d1 <= 0: continue
                conf2 = (d1-d2)/(d1+1e-12)
                if conf2 > best_conf2:
                    best_conf2 = conf2; best_sign2 = sign
                    best_syl2  = s1
                    _ss2_save  = ss2

            if best_sign2 is None: break
            top3 = sorted(_ss2_save, key=lambda s: -_ss2_save[s])[:3]
            assignments[best_sign2] = dict(
                syl=best_syl2,
                score=round(_ss2_save.get(best_syl2,0),6),
                score2=round(_ss2_save.get(top3[1],0) if len(top3)>1 else 0,6),
                confidence=round(best_conf2,4),
                top3=top3[:3],
                iteration=iteration+1,
            )
            read_map[best_sign2] = best_syl2
            avail.remove(best_syl2)
            remaining.remove(best_sign2)

        break  # single-pass greedy; n_iter would refine but adds little

    return assignments


# ── Confidence label ──────────────────────────────────────────────────────────
def _clabel(conf: float, score: float) -> str:
    if score <= 0:    return "· ZERO (no known neighbours)"
    if conf > 0.30:   return "★ HIGH"
    if conf > 0.10:   return "○ MED"
    return "· LOW"


# ── Main ───────────────────────────────────────────────────────────────────────
def run():
    # ── Load corpora ──────────────────────────────────────────────────────
    luw_text = ""
    for name in ("luwian_ritual", "luwian_all"):
        p = CACHE_DIR / f"ncd_cache_{name}.txt"
        if p.exists():
            luw_text += " " + p.read_text(encoding="utf-8")
    hit_text = ""
    hp = CACHE_DIR / "ncd_cache_hittite.txt"
    if hp.exists():
        hit_text = hp.read_text(encoding="utf-8")[:800_000]   # 800K chars

    combined = luw_text + " " + hit_text
    if not combined.strip():
        print("ERROR: corpora not found. Run phaistos_ncd_phylogenetic.py first.")
        return

    print("=" * 72)
    print("  PHAISTOS DISC — ALGORITHM #5: BIGRAM CONTEXT INFERENCE")
    print("=" * 72)
    print(f"  Disc: {len(DISC_WORDS)} word-groups, {len(DISC_TOKENS)} tokens")
    print(f"  Known G_LUWIAN anchors: {len(G_LUWIAN)}/45")
    print(f"  Corpus: {len(combined):,} chars  (Luwian ritual+all + Hittite 800K)")
    print()

    # ── Disc statistics ────────────────────────────────────────────────────
    disc = disc_stats()
    all_disc_signs   = sorted(disc)
    unknown_signs    = [s for s in all_disc_signs if s not in G_LUWIAN]
    known_signs_here = [s for s in all_disc_signs if s in G_LUWIAN]

    print(f"[1] DISC: {len(all_disc_signs)} distinct signs in data  "
          f"({len(known_signs_here)} known, {len(unknown_signs)} unknown)")
    print()
    print(f"  {'#':>5}  {'G_LUWIAN':^10}  {'freq':>5}  "
          f"{'p_init':>7}  {'p_fin':>7}  "
          f"{'n_left':>6}  {'n_right':>7}  neighbours (left→, →right)")
    print("  " + "-" * 78)
    for sign in all_disc_signs:
        d   = disc[sign]
        kn  = G_LUWIAN.get(sign,"—")
        top_bl = sorted(d["bl"], key=lambda s: -d["bl"][s])[:3]
        top_br = sorted(d["br"], key=lambda s: -d["br"][s])[:3]
        bl_str = "+".join(f"#{s}({d['bl'][s]})" for s in top_bl) or "—"
        br_str = "+".join(f"#{s}({d['br'][s]})" for s in top_br) or "—"
        print(f"  #{sign:>3}   {kn:^10}  {d['freq']:>5}  "
              f"{d['p_init']:>7.3f}  {d['p_fin']:>7.3f}  "
              f"{d['n_left']:>6}  {d['n_right']:>7}  "
              f"L:[{bl_str}]  R:[{br_str}]")
    print()

    # ── Luwian bigram matrix ───────────────────────────────────────────────
    luw_right, luw_left, sorted_syls, luw_freq = luwian_bigrams(combined, min_count=3)
    print(f"[2] LUWIAN BIGRAM MATRIX  —  {len(sorted_syls)} distinct syllables "
          f"(min 3 occurrences)")
    print(f"  Top-40: {sorted_syls[:40]}")
    print()

    # ── Calibration ───────────────────────────────────────────────────────
    calib = calibrate(disc, luw_right, luw_left, luw_freq, sorted_syls)
    print("[3] CALIBRATION (leave-one-out: each known sign treated as unknown)")
    print(f"  {'#':>4}  {'true':^8}  {'rank':>5}  {'score_true':>10}  "
          f"{'score_best':>10}  top-3 candidates")
    print("  " + "-" * 65)
    for r in calib:
        verdict = ("✓ TOP3"   if r["rank"] <  3 else
                   ("✓ TOP10"  if r["rank"] < 10 else
                    ("~ TOP20"  if r["rank"] < 20 else "✗ POOR")))
        top3 = " / ".join(r["top3"])
        print(f"  #{r['sign']:>3}  {r['true_syl']:^8}  {r['rank']:>5}  "
              f"{r['score_true']:>10.6f}  {r['score_best']:>10.6f}  "
              f"[{top3}]  {verdict}")
    good = sum(1 for r in calib if r["rank"] < 10)
    print(f"\n  Calibration: {good}/{len(calib)} known signs inferred in top-10")

    pv = calibration_pvalue(calib, n_candidates=200)
    sig_b = ("***" if pv["p_binom_top10"] < 0.001 else
             ("**"  if pv["p_binom_top10"] < 0.01  else
              ("*"   if pv["p_binom_top10"] < 0.05  else "n.s.")))
    sig_z = ("***" if pv["p_z_mean_rank"] < 0.001 else
             ("**"  if pv["p_z_mean_rank"] < 0.01  else
              ("*"   if pv["p_z_mean_rank"] < 0.05  else "n.s.")))
    print(f"  Null (uniform ranks 0-199): expected mean rank = {pv['null_expected_mean_rank']}")
    print(f"  Observed mean rank = {pv['observed_mean_rank']}  "
          f"| z = {pv['z_mean_rank']:.2f}  | p(z-test) = {pv['p_z_mean_rank']:.6f} {sig_z}")
    print(f"  Binomial top-10 hits: {pv['observed_top10']}/10 observed  "
          f"| p(binom) = {pv['p_binom_top10']:.4f} {sig_b}")
    print()

    # ── Infer unknown signs ───────────────────────────────────────────────
    print("[4] BIGRAM CONTEXT INFERENCE — assigning phonetic values to unknown signs")
    assignments = infer_unknown(disc, luw_right, luw_left, luw_freq,
                                sorted_syls, unknown_signs)

    print()
    print(f"  {'#':>4}  {'inferred':^10}  {'score':>8}  {'conf':>6}  "
          f"{'label':^26}  top-3 candidates")
    print("  " + "-" * 78)
    for sign in unknown_signs:
        if sign not in assignments:
            print(f"  #{sign:>3}  {'(no data)':^10}")
            continue
        info = assignments[sign]
        lbl  = _clabel(info["confidence"], info["score"])
        top3 = " / ".join(info["top3"])
        print(f"  #{sign:>3}  {info['syl']:^10}  {info['score']:>8.6f}  "
              f"{info['confidence']:>6.4f}  {lbl:^26}  [{top3}]")
    print()

    # ── Full phonetic key ─────────────────────────────────────────────────
    print("[5] COMPLETE PHONETIC KEY")
    full = {s: (v if v != "tiwa" else "tiwa") for s,v in G_LUWIAN.items()}
    for sign, info in assignments.items():
        full[sign] = info["syl"]

    print()
    cols = 6; signs_sorted = sorted(full)
    for i in range(0, len(signs_sorted), cols):
        chunk = signs_sorted[i:i+cols]
        parts = []
        for s in chunk:
            v   = full[s]
            tag = "★" if s in G_LUWIAN else "○"
            parts.append(f"#{s:>3}={tag}{v:<6}")
        print("  " + "  ".join(parts))
    print()

    # ── Complete reading ──────────────────────────────────────────────────
    print("[6] COMPLETE READING — ALL 61 WORD GROUPS")
    print("  (★=G_LUWIAN known  ○=HIGH conf inferred  ·=LOW/ZERO conf)")
    print()
    for i, word in enumerate(DISC_WORDS):
        side = "A" if i < 31 else "B"
        wn   = i+1 if i < 31 else i-30
        parts = []
        for sign in word:
            v = full.get(sign, f"#{sign}")
            if sign in G_LUWIAN:
                tag = "★"
            elif sign in assignments:
                c = assignments[sign]["confidence"]
                tag = "○" if c > 0.1 else "·"
            else:
                tag = "?"
            parts.append(f"{tag}{v}")
        print(f"  W{i+1:02d} ({side}{wn:02d}):  {' · '.join(parts)}")

    # ── Save ──────────────────────────────────────────────────────────────
    out = {
        "known": {str(k):v for k,v in G_LUWIAN.items()},
        "inferred": {str(k):{**v,"top3":[str(x) for x in v["top3"]]}
                     for k,v in assignments.items()},
        "full_key": {str(k):v for k,v in full.items()},
        "calibration": calib,
        "calibration_pvalue": pv,
        "n_corpus_syls": len(sorted_syls),
    }
    with open("fingerprint_results.json","w",encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print()
    print("  Saved → fingerprint_results.json")


if __name__ == "__main__":
    run()
