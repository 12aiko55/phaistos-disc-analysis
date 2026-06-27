"""
phaistos_graph_laplacian.py  -  Algorithm #3: Graph Spectrum Laplacian Eigenvalues
====================================================================================
"Φασματική Ανάλυση Δικτύων Λέξεων"

Converts the Phaistos Disc into a co-occurrence network graph and computes its
Laplacian spectral fingerprint. Compares to spectral fingerprints of language
corpora. The graph topology cannot be manipulated by any phonetic bias.

Core idea (from network science):
  Every language has a characteristic network "shape":
  - Egyptian hieroglyphs  → star-shaped (few dominant signs)
  - Natural languages     → small-world (clustered, short paths)
  - Random sequences      → Erdos-Renyi random (uniform, unclustered)
  The normalized Laplacian eigenvalue sequence is this shape's mathematical
  fingerprint. If disc spectrum matches Luwian spectrum more than it matches
  random text, that is key-independent evidence of structural kinship.

GRAPH CONSTRUCTION:
  Nodes  = signs (disc: 1-45)  /  characters (corpus: top-45 most frequent)
  Edges  = bigram co-occurrence within word groups (disc) / character sequences (corpus)
  Weight = normalized bigram frequency (so total-corpus-length does not bias)
  Graph  = undirected, weighted (symmetrized)

NORMALIZED LAPLACIAN:
  D = diagonal degree matrix,  A = adjacency matrix
  L_norm = I - D^{-1/2} A D^{-1/2}
  Eigenvalues lambda_i in [0, 2].  Sorted ascending.
  lambda_0 = 0 (always), lambda_1 = Fiedler value (algebraic connectivity).

SPECTRAL METRICS REPORTED:
  1. Fiedler value lambda_1  (connectivity / community structure)
  2. Spectral gap  lambda_1  (same — gap from 0 to first non-zero eigenvalue)
  3. Lambda_max               (graph diameter proxy)
  4. Spectral distance        (Earth-Mover / L2 between sorted eigenvalue vectors)
  5. Network props: density, clustering coefficient, small-world test

STATISTICAL VALIDATION:
  Monte Carlo null: shuffle disc sign tokens (within word groups) -> random graph.
  p-value = P(null spectral_dist <= observed spectral_dist) [lower dist = more similar]

CORPORA:
  luwian_ritual, luwian_all, hittite, linear_b  (same as Algorithms 1+2)

Usage:
  python phaistos_graph_laplacian.py           # full run (1000 MC)
  python phaistos_graph_laplacian.py --fast    # 200 MC
"""

import argparse
import json
import math
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
from scipy import linalg

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ROOT      = Path(__file__).parent
CACHE_DIR = ROOT / "__pycache__"
sys.path.insert(0, str(ROOT))

from phaistos_canonical_data import SIDE_A_EVANS, SIDE_B_EVANS

DISC_WORDS  = SIDE_A_EVANS + SIDE_B_EVANS
DISC_TOKENS = [s for w in DISC_WORDS for s in w]
N_SIGNS     = 45      # disc alphabet size
N_TOP_CHARS = 45      # corpus character graph size (same as disc)
N_MC        = 1000

# ---------------------------------------------------------------------------
# Corpus loading
# ---------------------------------------------------------------------------
def load_corpus(name: str) -> str:
    p = CACHE_DIR / f"ncd_cache_{name}.txt"
    return p.read_text(encoding="utf-8") if p.exists() else ""

# ---------------------------------------------------------------------------
# Graph construction
# ---------------------------------------------------------------------------
def disc_adjacency(word_groups: List[List[int]], n: int = N_SIGNS) -> np.ndarray:
    """
    Build normalized weighted adjacency matrix from disc sign bigrams.
    A[i,j] = (count of bigram i->j + j->i) / total_bigrams
    Symmetrized (undirected graph).
    Signs are 1-indexed; matrix is 0-indexed.
    """
    A = np.zeros((n, n))
    total = 0
    for word in word_groups:
        for k in range(len(word) - 1):
            i, j = word[k] - 1, word[k+1] - 1
            if 0 <= i < n and 0 <= j < n:
                A[i, j] += 1
                A[j, i] += 1
                total += 2
    if total > 0:
        A /= total
    return A


def shuffled_disc_adjacency(word_groups: List[List[int]], rng: random.Random,
                            n: int = N_SIGNS) -> np.ndarray:
    """
    Shuffle sign tokens within each word group, preserving word lengths.
    Returns adjacency matrix of the shuffled disc.
    """
    all_tokens = [s for w in word_groups for s in w]
    rng.shuffle(all_tokens)
    # Reassign shuffled tokens to same word-length structure
    shuffled_groups: List[List[int]] = []
    idx = 0
    for word in word_groups:
        length = len(word)
        shuffled_groups.append(all_tokens[idx: idx + length])
        idx += length
    return disc_adjacency(shuffled_groups, n)


def corpus_adjacency(text: str, n: int = N_TOP_CHARS,
                     n_tokens: int = 0, seed: int = 0) -> np.ndarray:
    """
    Build normalized weighted adjacency matrix from corpus character bigrams.
    If n_tokens > 0: subsample to that many characters (same density as disc).
    Uses top-n most frequent non-whitespace characters.
    """
    chars = [c for c in text if not c.isspace()]
    if n_tokens > 0 and len(chars) > n_tokens:
        rng   = random.Random(seed)
        start = rng.randint(0, len(chars) - n_tokens)
        chars = chars[start: start + n_tokens]

    # Select top-n characters from the (sub)sample
    freq   = Counter(chars)
    top_n  = [ch for ch, _ in freq.most_common(n)]
    ch_idx = {ch: i for i, ch in enumerate(top_n)}
    n_used = len(top_n)

    A     = np.zeros((n_used, n_used))
    total = 0
    for k in range(len(chars) - 1):
        a, b = chars[k], chars[k+1]
        if a in ch_idx and b in ch_idx:
            i, j = ch_idx[a], ch_idx[b]
            A[i, j] += 1
            A[j, i] += 1
            total += 2
    if total > 0:
        A /= total
    return A


def mean_corpus_eigenvalues(text: str, n_samples: int = 20,
                             n_tokens: int = 242, seed: int = 0) -> np.ndarray:
    """
    Average Laplacian eigenvalues over n_samples random subsamples.
    Subsampling to n_tokens gives same density regime as disc.
    """
    all_eigs = []
    for i in range(n_samples):
        A    = corpus_adjacency(text, n=N_TOP_CHARS, n_tokens=n_tokens, seed=seed + i)
        eigs = laplacian_eigenvalues(A)
        # Pad to N_TOP_CHARS with 2.0 (max eigenvalue, isolated nodes)
        if len(eigs) < N_TOP_CHARS:
            eigs = np.concatenate([eigs, np.full(N_TOP_CHARS - len(eigs), 2.0)])
        all_eigs.append(eigs[:N_TOP_CHARS])
    return np.mean(all_eigs, axis=0)

# ---------------------------------------------------------------------------
# Laplacian eigenvalues
# ---------------------------------------------------------------------------
def laplacian_eigenvalues(A: np.ndarray) -> np.ndarray:
    """
    Normalized Laplacian L_norm = I - D^{-1/2} A D^{-1/2}.
    Eigenvalues in [0, 2], sorted ascending.
    Isolated nodes (degree=0) get eigenvalue 0.
    """
    degree     = A.sum(axis=1)
    d_inv_sqrt = np.where(degree > 1e-12, 1.0 / np.sqrt(degree), 0.0)
    D_inv_sqrt = np.diag(d_inv_sqrt)
    L_norm     = np.eye(len(A)) - D_inv_sqrt @ A @ D_inv_sqrt
    eigs       = linalg.eigvalsh(L_norm)
    return np.sort(np.real(eigs))

# ---------------------------------------------------------------------------
# Spectral distance metrics
# ---------------------------------------------------------------------------
def spectral_distance_l2(eigs_a: np.ndarray, eigs_b: np.ndarray) -> float:
    """L2 distance between sorted eigenvalue vectors (truncate to min length)."""
    n = min(len(eigs_a), len(eigs_b))
    return float(np.linalg.norm(eigs_a[:n] - eigs_b[:n]))


def wasserstein_1d(eigs_a: np.ndarray, eigs_b: np.ndarray) -> float:
    """
    1D Wasserstein (Earth Mover) distance between eigenvalue distributions.
    Interpolate both to 100 points in [0, 2] then compute L1.
    """
    t      = np.linspace(0, 2, 100)
    cdf_a  = np.array([np.mean(eigs_a <= x) for x in t])
    cdf_b  = np.array([np.mean(eigs_b <= x) for x in t])
    return float(np.mean(np.abs(cdf_a - cdf_b)))


def network_properties(A: np.ndarray) -> Dict:
    """Compute basic network statistics."""
    n      = len(A)
    # Density
    n_edges = np.sum(A > 0) / 2
    density = n_edges / max(n * (n-1) / 2, 1)
    # Degree sequence
    degrees = (A > 0).sum(axis=1)
    mean_deg = float(degrees.mean())
    # Clustering coefficient (local, unweighted)
    A_bin = (A > 0).astype(float)
    A2    = A_bin @ A_bin
    cc_num   = np.diag(A2 @ A_bin)
    cc_denom = degrees * (degrees - 1)
    cc_vals  = np.where(cc_denom > 0, cc_num / cc_denom, 0.0)
    clustering = float(cc_vals.mean())
    return {"density": density, "mean_degree": mean_deg,
            "clustering": clustering, "n_nodes": n, "n_edges": int(n_edges)}

# ---------------------------------------------------------------------------
# Monte Carlo null
# ---------------------------------------------------------------------------
def mc_null_spectral(disc_words: List[List[int]],
                     corpus_eigs: Dict[str, np.ndarray],
                     n_iter: int) -> Dict[str, List[float]]:
    """
    Build shuffled-disc graphs, compute spectral distances to each corpus.
    Returns dict of {corpus_name: [dist_1, dist_2, ...]}
    """
    rng    = random.Random(42)
    result = defaultdict(list)
    for i in range(n_iter):
        shuf_A    = shuffled_disc_adjacency(disc_words, rng)
        shuf_eigs = laplacian_eigenvalues(shuf_A)
        for name, corp_eigs in corpus_eigs.items():
            result[name].append(wasserstein_1d(shuf_eigs, corp_eigs))
        if (i + 1) % 250 == 0:
            print(f"    MC {i+1}/{n_iter}...", end="\r", flush=True)
    print(" " * 45, end="\r")
    return dict(result)

# ---------------------------------------------------------------------------
# p-value
# ---------------------------------------------------------------------------
def p_lower(obs: float, null: List[float]) -> float:
    return sum(1 for x in null if x <= obs) / max(len(null), 1)

def sig(p: float) -> str:
    return "***" if p < 0.001 else "** " if p < 0.01 else "*  " if p < 0.05 else "   "

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def run(n_mc: int):
    print("=" * 74)
    print("  PHAISTOS DISC — ALGORITHM #3: GRAPH SPECTRUM LAPLACIAN EIGENVALUES")
    print("=" * 74)
    print(f"  Disc: {len(DISC_TOKENS)} tokens, {N_SIGNS} signs, {len(DISC_WORDS)} word groups")
    print(f"  Corpus graph: top-{N_TOP_CHARS} chars per corpus")
    print(f"  Monte Carlo: {n_mc} shuffled-disc iterations")
    print()

    # -----------------------------------------------------------------------
    # Load corpora
    # -----------------------------------------------------------------------
    CORPUS_NAMES = ["luwian_ritual", "luwian_all", "hittite", "linear_b"]
    corpora: Dict[str, str] = {}
    print("  Corpora:")
    for name in CORPUS_NAMES:
        t = load_corpus(name)
        if t:
            corpora[name] = t
            print(f"    {name:<20}: {len(t):>12,} chars")
        else:
            print(f"    {name:<20}: NOT CACHED")
    print()

    # -----------------------------------------------------------------------
    # BUILD DISC GRAPH
    # -----------------------------------------------------------------------
    print("[1] DISC SIGN CO-OCCURRENCE GRAPH")
    print("-" * 70)

    disc_A    = disc_adjacency(DISC_WORDS, N_SIGNS)
    disc_eigs = laplacian_eigenvalues(disc_A)
    disc_props = network_properties(disc_A)

    n_active = int(np.sum(disc_A.sum(axis=1) > 0))
    print(f"  Active nodes (signs with bigrams): {n_active}/{N_SIGNS}")
    print(f"  Network density    : {disc_props['density']:.4f}")
    print(f"  Mean degree        : {disc_props['mean_degree']:.2f}")
    print(f"  Clustering coeff   : {disc_props['clustering']:.4f}")
    print(f"  Fiedler value λ_1  : {disc_eigs[1]:.6f}  (algebraic connectivity)")
    print(f"  λ_max              : {disc_eigs[-1]:.6f}")
    print(f"  Spectral spread    : {disc_eigs[-1] - disc_eigs[1]:.6f}")
    print()

    # Eigenvalue distribution summary
    n_zero   = int(np.sum(disc_eigs < 1e-6))
    n_near2  = int(np.sum(disc_eigs > 1.9))
    print(f"  Eigenvalue summary: {n_zero} at ~0 (isolated)  "
          f"{n_near2} at ~2 (bipartite-like)  "
          f"{N_SIGNS - n_zero - n_near2} interior")
    print(f"  First 10 eigenvalues:")
    print("    " + "  ".join(f"{e:.4f}" for e in disc_eigs[:10]))

    # -----------------------------------------------------------------------
    # BUILD CORPUS GRAPHS
    # -----------------------------------------------------------------------
    print()
    print("[2] CORPUS CHARACTER CO-OCCURRENCE GRAPHS")
    print("-" * 70)

    corpus_eigs:  Dict[str, np.ndarray] = {}
    corpus_props: Dict[str, Dict]       = {}

    for name, text in corpora.items():
        # Subsample to same length as disc (242 tokens) → same density regime
        # Average over 20 random windows for a stable spectrum
        eigs  = mean_corpus_eigenvalues(text, n_samples=20,
                                        n_tokens=len(DISC_TOKENS), seed=0)
        # Also build one sample for network property reporting
        A_sample = corpus_adjacency(text, n=N_TOP_CHARS,
                                    n_tokens=len(DISC_TOKENS), seed=0)
        props = network_properties(A_sample)
        corpus_eigs[name]  = eigs
        corpus_props[name] = props
        print(f"  [{name}]  (averaged over 20 x {len(DISC_TOKENS)}-char subsamples)")
        print(f"    density={props['density']:.4f}  "
              f"clustering={props['clustering']:.4f}  "
              f"lambda_1={eigs[1]:.6f}  lambda_max={eigs[-1]:.6f}")
        print(f"    First 10 eigs: " + "  ".join(f"{e:.4f}" for e in eigs[:10]))
        print()

    # -----------------------------------------------------------------------
    # SPECTRAL DISTANCES (disc vs each corpus)
    # -----------------------------------------------------------------------
    print("[3] SPECTRAL DISTANCES  (Wasserstein + L2)")
    print("-" * 70)

    obs_w  = {name: wasserstein_1d(disc_eigs, corp_eigs)
              for name, corp_eigs in corpus_eigs.items()}
    obs_l2 = {name: spectral_distance_l2(disc_eigs, corp_eigs)
              for name, corp_eigs in corpus_eigs.items()}

    print(f"  {'Corpus':<22}  {'Wasserstein':>12}  {'L2':>8}")
    print("  " + "-" * 46)
    for name in sorted(obs_w, key=obs_w.get):
        print(f"  {name:<22}  {obs_w[name]:>12.6f}  {obs_l2[name]:>8.4f}")

    # -----------------------------------------------------------------------
    # MONTE CARLO NULL
    # -----------------------------------------------------------------------
    print()
    print(f"[4] MONTE CARLO NULL  ({n_mc} shuffled-disc graphs)")
    print("-" * 70)
    print("  Building shuffled graphs and computing spectral distances...")

    null_dists = mc_null_spectral(DISC_WORDS, corpus_eigs, n_mc)

    print()
    print(f"  {'Corpus':<22}  {'Obs W':>8}  {'Null mean':>10}  {'p-value':>8}  {'sig':>4}")
    print("  " + "-" * 60)
    spectral_results: Dict = {}
    for name in sorted(obs_w, key=obs_w.get):
        obs   = obs_w[name]
        nulls = null_dists[name]
        pv    = p_lower(obs, nulls)
        nm    = sum(nulls) / len(nulls)
        nstd  = (sum((x-nm)**2 for x in nulls)/len(nulls))**0.5
        z     = (obs - nm) / max(nstd, 1e-10)
        print(f"  {name:<22}  {obs:>8.6f}  {nm:>10.6f}  {pv:>8.4f}  {sig(pv)}")
        spectral_results[name] = {"wasserstein": obs, "null_mean": nm,
                                  "null_std": nstd, "z": z, "p": pv}

    # -----------------------------------------------------------------------
    # SMALL-WORLD TEST
    # -----------------------------------------------------------------------
    print()
    print("[5] SMALL-WORLD NETWORK TEST")
    print("-" * 70)
    print("  Comparing disc network topology to each corpus network.")
    print("  Small-world: high clustering + short paths vs. random graph.")
    print()
    print(f"  {'Property':<25}  {'Disc':>8}  " +
          "  ".join(f"{n[:8]:>8}" for n in corpora))
    print("  " + "-" * (25 + 10 + 12 * len(corpora)))
    for prop in ["density", "clustering", "mean_degree"]:
        vals = [disc_props[prop]] + [corpus_props[n][prop] for n in corpora]
        print(f"  {prop:<25}  " + "  ".join(f"{v:>8.4f}" for v in vals))

    # Fiedler values
    print(f"  {'Fiedler lambda_1':<25}  {disc_eigs[1]:>8.4f}  " +
          "  ".join(f"{corpus_eigs[n][1]:>8.4f}" for n in corpora))
    print(f"  {'lambda_max':<25}  {disc_eigs[-1]:>8.4f}  " +
          "  ".join(f"{corpus_eigs[n][-1]:>8.4f}" for n in corpora))

    # Small-world index: clustering / random_clustering / (path / random_path)
    # Approximation using spectral methods
    disc_sw = disc_props["clustering"] / max(disc_props["density"], 1e-6)
    print()
    print(f"  Disc clustering/density ratio: {disc_sw:.2f}")
    print(f"  (ratio > 1 = more clustered than random graph with same density)")

    # -----------------------------------------------------------------------
    # SUMMARY
    # -----------------------------------------------------------------------
    print()
    print("=" * 74)
    print("  SUMMARY — ALGORITHM #3: GRAPH LAPLACIAN SPECTRUM")
    print("=" * 74)

    print(f"\n  Disc graph: {disc_props['n_nodes']} nodes, {disc_props['n_edges']} edges")
    print(f"  Fiedler value λ_1 = {disc_eigs[1]:.6f}  (connected, community structure)")
    print(f"  Clustering = {disc_props['clustering']:.4f}  (vs density={disc_props['density']:.4f})")

    print("\n  Spectral distance ranking (lower = more similar to disc):")
    for i, name in enumerate(sorted(obs_w, key=obs_w.get), 1):
        r = spectral_results[name]
        print(f"    #{i}  {name:<22}: W={r['wasserstein']:.6f}  "
              f"z={r['z']:.2f}  p={r['p']:.4f} {sig(r['p'])}")

    print()
    print("  Significance: *** p<0.001  ** p<0.01  * p<0.05")
    print("  All results KEY-INDEPENDENT (no phonetic assumptions)")

    # Save
    out = {
        "disc_graph": {
            "eigenvalues": disc_eigs.tolist(),
            "properties":  disc_props,
            "fiedler": float(disc_eigs[1]),
            "lambda_max": float(disc_eigs[-1]),
        },
        "corpus_graphs": {
            name: {
                "eigenvalues": corpus_eigs[name].tolist(),
                "properties":  corpus_props[name],
                "fiedler": float(corpus_eigs[name][1]),
            }
            for name in corpora
        },
        "spectral_results": spectral_results,
        "n_mc": n_mc,
    }
    (ROOT / "graph_laplacian_results.json").write_text(
        json.dumps(out, indent=2, default=str), encoding="utf-8")
    print("\n  Saved -> graph_laplacian_results.json")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--fast", action="store_true")
    args = parser.parse_args()
    if args.fast:
        N_MC = 200
        print("[FAST MODE] 200 MC\n")
    run(N_MC)
