"""
phaistos_matched_filter.py
==========================
LIGO-style matched filter applied to the Phaistos Disc token sequence.

Encodes the 241-token disc as a 1D information-content (IC) signal, then
cross-correlates against five Luwian grammatical templates.  Significance
is assessed via 10 000 Monte Carlo surrogates (random permutations of the
IC signal), producing an SNR analogous to the LIGO gravitational-wave
detection statistic.

G_LUWIAN phoneme assignments (anchor set):
  Sign  2  PLUMED HEAD  → za   (demonstrative, rank-1)
  Sign  7  HELMET       → wa   (connective clitic, rank-2)
  Sign 12  SHIELD       → tar  (water construct, rank-3)
  Sign 27  HIDE         → na   (particle, rank-4)
  Sign 18  BOOMERANG    → ha   (affirmative particle, rank-5)
  Sign 45  WAVY BAND    → ti-wa (water deity Tiwat)
  Sign 25  SHIP         → naw
  Sign 44  SMALL AXE    → ma
  Sign  1  PEDESTRIAN   → i

Reference: Evans/Godart canonical sign numbering.
"""

import sys
import math
import random
import numpy as np
import scipy.signal
import matplotlib
matplotlib.use("Agg")          # non-interactive backend for headless runs
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ── Canonical disc data ────────────────────────────────────────────────────────
SIDE_A_EVANS = [
    [2,12,13,1,18],[24,40,12],[29,45,7],[29,29,34],[2,12,4,40,33],
    [27,45,7,12],[27,44,8],[2,12,6,18,27],[31,26,35],[2,12,41,19,35],
    [1,41,40,7],[2,12,32,23,38],[39,11],[2,27,25,10,23,18],[28,1],
    [2,12,31,26],[2,12,27,27,35,37,21],[33,23],[2,12,31,26],
    [2,27,25,10,23,18],[28,1],[2,12,31,26],[2,12,27,14,32,18,27],
    [6,18,17,19],[31,26,12],[2,12,13,1],[23,19,35],[10,3,38],
    [2,12,27,27,35,37,21],[13,1],[10,3,38],
]
SIDE_B_EVANS = [
    [2,12,22,40,7],[27,45,7,35],[2,37,23,5],[22,25,27],[33,24,20,12],
    [16,23,18,43],[13,1,39,33],[15,7,13,1,18],[22,37,42,25],[7,24,40,35],
    [2,26,36,40],[27,25,38,1],[29,24,24,20,35],[16,14,18],[29,33,1],
    [6,35,32,39,33],[2,9,27,1],[29,36,7,8],[29,8,13],[29,45,7],
    [22,29,36,7,8],[27,34,23,25],[7,18,35],[7,45,7],[7,23,18,24],
    [22,29,36,7,8],[9,30,39,18,7],[2,6,35,23,7],[29,34,23,25],[45,7],
]

SIGN_NAMES = {
     1:"PEDESTRIAN",    2:"PLUMED HEAD",    3:"TATTOOED HEAD",  4:"CAPTIVE",
     5:"CHILD",         6:"WOMAN",          7:"HELMET",          8:"GAUNTLET",
     9:"TIARA",        10:"ARROW",         11:"BOW",            12:"SHIELD",
    13:"CLUB",         14:"MANACLES",      15:"MATTOCK",        16:"SAW",
    17:"LID",          18:"BOOMERANG",     19:"CARP. PLANE",    20:"DOLIUM",
    21:"COMB",         22:"SLING",         23:"COLUMN",         24:"BEEHIVE",
    25:"SHIP",         26:"HORN",          27:"HIDE",           28:"BULL'S LEG",
    29:"CAT",          30:"RAM",           31:"EAGLE",          32:"DOVE",
    33:"TUNNY",        34:"BEE",           35:"PLANE TREE",     36:"VINE",
    37:"PAPYRUS",      38:"ROSETTE",       39:"LILY",           40:"OX BACK",
    41:"FLUTE",        42:"GRATER",        43:"STRAINER",       44:"SMALL AXE",
    45:"WAVY BAND",
}

PHONEMES = {
     1: "i",   2: "za",   7: "wa",  12: "tar",
    18: "ha",  25: "naw", 27: "na",  44: "ma",  45: "ti-wa",
}

# ── Flatten disc to token sequence ────────────────────────────────────────────
def flatten_disc():
    """Return (tokens, position_map) where position_map[i] = (side, group_idx, pos_in_group)."""
    tokens = []
    pos_map = []
    for side_label, side_data in [("A", SIDE_A_EVANS), ("B", SIDE_B_EVANS)]:
        for g_idx, group in enumerate(side_data):
            for p_idx, sign in enumerate(group):
                tokens.append(sign)
                pos_map.append((side_label, g_idx + 1, p_idx + 1))
    return tokens, pos_map


# ── Disc position decoder ──────────────────────────────────────────────────────
def decode_position(flat_index, pos_map):
    """Map flat token index → human-readable disc position string."""
    if flat_index < 0 or flat_index >= len(pos_map):
        return "OUT_OF_RANGE"
    side, grp, pos = pos_map[flat_index]
    return f"Side {side}, Group {grp}, Token {pos}"


# ── Build IC signal ────────────────────────────────────────────────────────────
def build_ic_signal(tokens):
    """
    Compute information content (IC) for each token position.

    IC[i] = -log2(freq(sign_i) / N)

    Returns the raw IC array and the standardised (zero-mean, unit-variance)
    version used for cross-correlation.
    """
    n = len(tokens)
    from collections import Counter
    freq = Counter(tokens)
    ic_raw = np.array([-math.log2(freq[t] / n) for t in tokens], dtype=float)
    ic_std = (ic_raw - ic_raw.mean()) / ic_raw.std()
    return ic_raw, ic_std


# ── Template definitions ───────────────────────────────────────────────────────
TEMPLATES = {
    "CLITIC_CHAIN": {
        "pattern": np.array([-1.2, -1.0, -0.8,  0.5]),
        "description": (
            "za+wa+particle+content  (Wackernagel 2nd-position clitic cluster).\n"
            "  Low-IC clitics pile up early; single content word terminates."
        ),
    },
    "INVOCATION": {
        "pattern": np.array([-1.0,  1.5,  1.2, -0.8]),
        "description": (
            "particle+name+name+particle  (divine invocation structure).\n"
            "  Ritual opening: PLUMED HEAD + two content signs + closing particle."
        ),
    },
    "REFRAIN": {
        "pattern": np.array([-1.2, -1.1, -1.0, -0.9]),
        "description": (
            "All-function-word sequence  [2,12,31,26] = za-tar-EAGLE-HORN.\n"
            "  Should peak at known refrain positions A16, A19, A22."
        ),
    },
    "BIPARTITE": {
        "pattern": np.array([ 1.2, -0.8,  1.0, -0.7,  0.9]),
        "description": (
            "content+particle+content+particle+content  (bilateral covenant).\n"
            "  Maritime covenant formula alternates parties."
        ),
    },
    "TIWAT_FORMULA": {
        "pattern": np.array([-0.8,  1.8, -1.0, -0.9]),
        "description": (
            "particle+water-deity+particle+clitic  (Tiwat theological formula).\n"
            "  Sign 45 (ti-wa) should score high at centre."
        ),
    },
}

# Normalise each template to unit energy (analogous to LIGO matched filter norm)
for tname, tdata in TEMPLATES.items():
    p = tdata["pattern"].astype(float)
    tdata["pattern_norm"] = p / np.linalg.norm(p)


# ── Matched filter + surrogate significance ───────────────────────────────────
def matched_filter(signal, template_norm, n_surrogates=10_000, rng_seed=42):
    """
    Cross-correlate signal with template_norm (mode='full', valid range).

    Returns
    -------
    corr_valid : np.ndarray  — cross-correlation in valid range
    peak_val   : float       — observed maximum correlation
    peak_idx   : int         — index of peak in corr_valid (0-based, maps to
                               flat token position of the template's first token)
    snr        : float
    pvalue     : float
    surrogate_max_mean : float
    surrogate_max_std  : float
    """
    rng = np.random.default_rng(rng_seed)
    L = len(template_norm)
    N = len(signal)

    # Full cross-correlation; valid range = positions where template fits entirely
    corr_full = scipy.signal.correlate(signal, template_norm, mode="full")
    # valid range: indices (L-1) to (L-1 + N - L) inclusive = (L-1) to (N-1)
    corr_valid = corr_full[L - 1 : N]

    peak_val = corr_valid.max()
    peak_idx = int(corr_valid.argmax())

    # Surrogate distribution
    surrogate_max = np.empty(n_surrogates)
    for k in range(n_surrogates):
        shuffled = rng.permutation(signal)
        c_full = scipy.signal.correlate(shuffled, template_norm, mode="full")
        surrogate_max[k] = c_full[L - 1 : N].max()

    mu = surrogate_max.mean()
    sigma = surrogate_max.std(ddof=1)
    snr = (peak_val - mu) / sigma if sigma > 0 else 0.0
    pvalue = float((surrogate_max >= peak_val).sum()) / n_surrogates

    return corr_valid, peak_val, peak_idx, snr, pvalue, mu, sigma


# ── Known refrain positions ───────────────────────────────────────────────────
def find_refrain_positions(pos_map):
    """
    Return flat indices where groups A16, A19, A22 start.
    (These are 1-indexed group numbers on Side A.)
    """
    refrain_groups = {("A", 16), ("A", 19), ("A", 22)}
    hits = []
    for i, (side, grp, pos_in_grp) in enumerate(pos_map):
        if (side, grp) in refrain_groups and pos_in_grp == 1:
            hits.append(i)
    return hits


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    SEP  = "=" * 72
    SEP2 = "-" * 72

    print(SEP)
    print("  PHAISTOS DISC — LIGO-STYLE MATCHED FILTER ANALYSIS")
    print("  G_LUWIAN hypothesis | Evans/Godart canonical sign numbering")
    print(SEP)

    tokens, pos_map = flatten_disc()
    N = len(tokens)
    print(f"\nTotal tokens (N): {N}")

    ic_raw, ic_std = build_ic_signal(tokens)

    from collections import Counter
    freq = Counter(tokens)
    print(f"\nTop-10 signs by frequency:")
    print(f"  {'Sign':>4}  {'Name':<18}  {'Freq':>4}  {'IC (bits)':>9}  {'Phoneme'}")
    print(f"  {'-'*4}  {'-'*18}  {'-'*4}  {'-'*9}  {'-'*10}")
    for sign, cnt in freq.most_common(10):
        ic_val = -math.log2(cnt / N)
        ph = PHONEMES.get(sign, "—")
        print(f"  {sign:>4}  {SIGN_NAMES.get(sign,'?'):<18}  {cnt:>4}  {ic_val:>9.3f}  {ph}")

    # ── Run matched filters ───────────────────────────────────────────────────
    print(f"\n{SEP}")
    print("  MATCHED FILTER RESULTS  (10 000 Monte Carlo surrogates)")
    print(SEP)

    results = {}
    header = f"  {'Template':<16}  {'Peak pos':>8}  {'Disc location':<28}  {'Sign':>4}  {'SNR':>6}  {'p-value':>8}"
    print(header)
    print(f"  {'-'*16}  {'-'*8}  {'-'*28}  {'-'*4}  {'-'*6}  {'-'*8}")

    for tname, tdata in TEMPLATES.items():
        tmpl = tdata["pattern_norm"]
        corr_valid, peak_val, peak_idx, snr, pvalue, mu, sigma = \
            matched_filter(ic_std, tmpl, n_surrogates=10_000)

        disc_loc = decode_position(peak_idx, pos_map)
        sign_at_peak = tokens[peak_idx]
        discovery = "*** ABOVE 3-sigma ***" if snr >= 3.0 else ""

        results[tname] = {
            "corr_valid": corr_valid,
            "peak_val": peak_val,
            "peak_idx": peak_idx,
            "snr": snr,
            "pvalue": pvalue,
            "mu": mu,
            "sigma": sigma,
            "sign_at_peak": sign_at_peak,
            "disc_loc": disc_loc,
            "discovery": discovery,
        }
        print(f"  {tname:<16}  {peak_idx:>8}  {disc_loc:<28}  {sign_at_peak:>4}  {snr:>6.2f}  {pvalue:>8.5f}  {discovery}")

    # ── 3 most significant hits per template ─────────────────────────────────
    print(f"\n{SEP}")
    print("  TOP-3 CORRELATION PEAKS PER TEMPLATE")
    print(SEP)

    for tname, tdata in TEMPLATES.items():
        tmpl = tdata["pattern_norm"]
        corr_valid = results[tname]["corr_valid"]
        mu   = results[tname]["mu"]
        sigma = results[tname]["sigma"]
        print(f"\n  [{tname}]")
        print(f"  {tdata['description']}")
        print(f"  {'Rank':>4}  {'Flat idx':>8}  {'Disc location':<28}  {'Sign':>4}  {'Name':<18}  {'Corr':>7}  {'Local SNR':>9}")
        print(f"  {'-'*4}  {'-'*8}  {'-'*28}  {'-'*4}  {'-'*18}  {'-'*7}  {'-'*9}")

        # Find top-3 non-overlapping peaks (min separation = template length)
        L = len(tmpl)
        corr_copy = corr_valid.copy()
        found = 0
        rank = 1
        while found < 3 and corr_copy.max() > -np.inf:
            idx = int(corr_copy.argmax())
            val = corr_copy[idx]
            local_snr = (val - mu) / sigma if sigma > 0 else 0.0
            disc_loc = decode_position(idx, pos_map)
            sign_id = tokens[idx]
            sign_name = SIGN_NAMES.get(sign_id, "?")
            print(f"  {rank:>4}  {idx:>8}  {disc_loc:<28}  {sign_id:>4}  {sign_name:<18}  {val:>7.3f}  {local_snr:>9.2f}")
            # Suppress neighbourhood
            lo = max(0, idx - L + 1)
            hi = min(len(corr_copy), idx + L)
            corr_copy[lo:hi] = -np.inf
            found += 1
            rank += 1

    # ── Refrain verification ──────────────────────────────────────────────────
    print(f"\n{SEP}")
    print("  REFRAIN TEMPLATE — VERIFICATION AT KNOWN POSITIONS A16, A19, A22")
    print(SEP)

    refrain_starts = find_refrain_positions(pos_map)
    tmpl_refrain = TEMPLATES["REFRAIN"]["pattern_norm"]
    corr_refrain  = results["REFRAIN"]["corr_valid"]
    mu_r  = results["REFRAIN"]["mu"]
    sig_r = results["REFRAIN"]["sigma"]

    print(f"\n  Known refrain groups [2,12,31,26] start at flat indices: {refrain_starts}")
    print(f"  {'Group':<10}  {'Flat idx':>8}  {'Corr':>7}  {'Local SNR':>9}  {'Note'}")
    print(f"  {'-'*10}  {'-'*8}  {'-'*7}  {'-'*9}  {'-'*30}")
    for fi in refrain_starts:
        side, grp, _ = pos_map[fi]
        label = f"A{grp}"
        corr_val = corr_refrain[fi] if fi < len(corr_refrain) else float("nan")
        local_snr = (corr_val - mu_r) / sig_r if sig_r > 0 else 0.0
        is_global_peak = (fi == results["REFRAIN"]["peak_idx"])
        note = "<-- GLOBAL PEAK" if is_global_peak else ""
        print(f"  {label:<10}  {fi:>8}  {corr_val:>7.3f}  {local_snr:>9.2f}  {note}")

    # ── Discovery summary ─────────────────────────────────────────────────────
    print(f"\n{SEP}")
    print("  DISCOVERY SUMMARY  (3-sigma threshold, analogous to LIGO criterion)")
    print(SEP)
    any_discovery = False
    for tname, r in results.items():
        flag = "ABOVE 3-sigma  [CANDIDATE]" if r["snr"] >= 3.0 else "below threshold"
        print(f"  {tname:<16}  SNR = {r['snr']:6.2f}  p = {r['pvalue']:.5f}  {flag}")
        if r["snr"] >= 3.0:
            any_discovery = True
    if not any_discovery:
        print("\n  No template reached the 3-sigma discovery threshold.")
    print()

    # ── Figure ────────────────────────────────────────────────────────────────
    fig = plt.figure(figsize=(16, 14))
    fig.patch.set_facecolor("#0d0d1a")

    # Colour palette
    C_BG    = "#0d0d1a"
    C_AX    = "#1a1a2e"
    C_GRID  = "#2a2a4a"
    C_SIGNAL= "#00ccff"
    C_NOISE = "#ff6633"
    C_PEAK  = "#ffdd00"
    C_BAR   = "#44ff88"
    C_THOLD = "#ff3333"
    C_TEXT  = "#e0e0e0"

    def style_ax(ax, title):
        ax.set_facecolor(C_AX)
        ax.set_title(title, color=C_TEXT, fontsize=9, pad=4)
        ax.tick_params(colors=C_TEXT, labelsize=7)
        for spine in ax.spines.values():
            spine.set_edgecolor(C_GRID)
        ax.yaxis.label.set_color(C_TEXT)
        ax.xaxis.label.set_color(C_TEXT)
        ax.grid(color=C_GRID, linewidth=0.4, linestyle="--", alpha=0.6)

    gs = fig.add_gridspec(3, 3, hspace=0.55, wspace=0.38,
                          left=0.07, right=0.97, top=0.93, bottom=0.06)

    # Panel 1: IC signal (spans full top row)
    ax_ic = fig.add_subplot(gs[0, :])
    ax_ic.plot(ic_std, color=C_SIGNAL, linewidth=0.8, alpha=0.9, label="IC signal (standardised)")
    ax_ic.axhline(0, color=C_GRID, linewidth=0.5)

    # Annotate top-8 IC positions
    top8 = np.argsort(ic_raw)[-8:][::-1]
    for fi in top8:
        sign_id = tokens[fi]
        label_str = f"{sign_id}"
        ph = PHONEMES.get(sign_id, "")
        if ph:
            label_str += f"\n({ph})"
        ax_ic.annotate(label_str,
                       xy=(fi, ic_std[fi]),
                       xytext=(fi, ic_std[fi] + 0.55),
                       fontsize=5.5, color=C_PEAK,
                       ha="center", va="bottom",
                       arrowprops=dict(arrowstyle="-", color=C_PEAK, lw=0.6))

    # Mark refrain groups
    for fi in refrain_starts:
        ax_ic.axvline(fi, color="#aa44ff", linewidth=0.7, linestyle=":", alpha=0.8)

    refrain_patch = mpatches.Patch(color="#aa44ff", label="Refrain start (A16/19/22)")
    ax_ic.legend(handles=[
        mpatches.Patch(color=C_SIGNAL, label="IC signal"),
        refrain_patch,
    ], fontsize=7, loc="upper right",
       facecolor=C_AX, edgecolor=C_GRID, labelcolor=C_TEXT)

    ax_ic.set_xlabel("Token index (0 = start of Side A)", fontsize=7)
    ax_ic.set_ylabel("Standardised IC", fontsize=7)
    style_ax(ax_ic, "Panel 1 — Information Content Signal (241 tokens, sign IDs annotated at top-8 IC positions)")

    # Panels 2-4: cross-correlation for templates 1, 3, 5
    panel_templates = ["CLITIC_CHAIN", "REFRAIN", "TIWAT_FORMULA"]
    panel_positions  = [(1, 0), (1, 1), (1, 2)]
    panel_colors     = ["#33ddff", "#44ff88", "#ffaa33"]

    for (row, col), tname, pcol in zip(panel_positions, panel_templates, panel_colors):
        ax = fig.add_subplot(gs[row, col])
        r  = results[tname]
        cv = r["corr_valid"]
        mu = r["mu"]
        sg = r["sigma"]

        xs = np.arange(len(cv))
        ax.plot(xs, cv, color=pcol, linewidth=0.7, alpha=0.9)

        # Noise floor shaded band (mu ± 2*sigma)
        ax.fill_between(xs, mu - 2*sg, mu + 2*sg,
                        color=C_NOISE, alpha=0.18, label="Noise ±2σ")
        ax.axhline(mu, color=C_NOISE, linewidth=0.6, linestyle="--", alpha=0.7)

        # Peak marker
        ax.axvline(r["peak_idx"], color=C_PEAK, linewidth=1.0, linestyle="-", alpha=0.85)
        ax.scatter([r["peak_idx"]], [r["peak_val"]], color=C_PEAK, s=22, zorder=5,
                   label=f"Peak idx={r['peak_idx']}")

        # Mark refrain starts on REFRAIN panel
        if tname == "REFRAIN":
            for fi in refrain_starts:
                ax.axvline(fi, color="#aa44ff", linewidth=0.8, linestyle=":", alpha=0.9)

        ax.set_xlabel("Start token index", fontsize=6)
        ax.set_ylabel("Cross-correlation", fontsize=6)
        snr_str = f"SNR={r['snr']:.2f}  p={r['pvalue']:.4f}"
        style_ax(ax, f"Panel — {tname}\n{snr_str}")
        ax.legend(fontsize=5.5, loc="upper right",
                  facecolor=C_AX, edgecolor=C_GRID, labelcolor=C_TEXT)

    # Panel 5: SNR bar chart (spans bottom row)
    ax_snr = fig.add_subplot(gs[2, :])
    tnames  = list(results.keys())
    snr_vals = [results[t]["snr"] for t in tnames]
    pvals    = [results[t]["pvalue"] for t in tnames]
    bar_cols = [C_THOLD if s >= 3.0 else C_BAR for s in snr_vals]

    bars = ax_snr.bar(tnames, snr_vals, color=bar_cols, edgecolor=C_GRID, linewidth=0.6)
    ax_snr.axhline(3.0, color=C_THOLD, linewidth=1.2, linestyle="--",
                   label="3σ discovery threshold")

    for bar, snr, pv in zip(bars, snr_vals, pvals):
        ax_snr.text(bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + 0.05,
                    f"SNR={snr:.2f}\np={pv:.4f}",
                    ha="center", va="bottom", fontsize=6, color=C_TEXT)

    ax_snr.set_ylabel("SNR  (signal − noise mean) / noise σ", fontsize=7)
    ax_snr.set_ylim(bottom=0)
    ax_snr.legend(fontsize=7, loc="upper right",
                  facecolor=C_AX, edgecolor=C_GRID, labelcolor=C_TEXT)
    style_ax(ax_snr, "Panel 5 — SNR Bar Chart (all 5 templates; red dashed = LIGO-style 3σ discovery threshold)")

    fig.suptitle(
        "Phaistos Disc — LIGO-Style Matched Filter  |  G_LUWIAN Hypothesis  |  10 000 MC Surrogates",
        color=C_TEXT, fontsize=11, y=0.975
    )

    out_path = r"C:\Users\Manos\Downloads\phaistos-disc-analysis\matched_filter_output.png"
    fig.savefig(out_path, dpi=150, facecolor=C_BG, bbox_inches="tight")
    print(f"  Figure saved → {out_path}")
    plt.close(fig)

    print(f"\n{SEP}")
    print("  ANALYSIS COMPLETE")
    print(SEP)


if __name__ == "__main__":
    main()
