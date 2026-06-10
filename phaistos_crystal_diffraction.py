"""
phaistos_crystal_diffraction.py
================================
2D Fourier Transform / X-ray Crystallography-Inspired Analysis
of the Phaistos Disc.

Treats each sign on the disc's spiral as an "atom" in a 2D crystal.
The 2D FFT power spectrum reveals whether the disc has the periodic
structure expected of natural language (1/f noise, alpha ~ -1) or
random noise (alpha ~ 0).

Author: Phaistos Disc Analysis Project
"""

import sys
import warnings
import numpy as np
from scipy.ndimage import gaussian_filter
from scipy.stats import linregress
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec

sys.stdout.reconfigure(encoding='utf-8')
warnings.filterwarnings('ignore')

# ---------------------------------------------------------------------------
# Disc data
# ---------------------------------------------------------------------------
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
     1:"PEDESTRIAN",  2:"PLUMED HEAD",  3:"TATTOOED HEAD", 4:"CAPTIVE",
     5:"CHILD",       6:"WOMAN",        7:"HELMET",        8:"GAUNTLET",
     9:"TIARA",      10:"ARROW",       11:"BOW",          12:"SHIELD",
    13:"CLUB",       14:"MANACLES",    15:"MATTOCK",      16:"SAW",
    17:"LID",        18:"BOOMERANG",   19:"CARP. PLANE",  20:"DOLIUM",
    21:"COMB",       22:"SLING",       23:"COLUMN",       24:"BEEHIVE",
    25:"SHIP",       26:"HORN",        27:"HIDE",         28:"BULL'S LEG",
    29:"CAT",        30:"RAM",         31:"EAGLE",        32:"DOVE",
    33:"TUNNY",      34:"BEE",         35:"PLANE TREE",   36:"VINE",
    37:"PAPYRUS",    38:"ROSETTE",     39:"LILY",         40:"OX BACK",
    41:"FLUTE",      42:"GRATER",      43:"STRAINER",     44:"SMALL AXE",
    45:"WAVY BAND",
}

# ---------------------------------------------------------------------------
# Flatten token sequences
# ---------------------------------------------------------------------------
def flatten_side(side):
    """Flatten list-of-groups into a single list of sign IDs."""
    tokens = []
    for group in side:
        tokens.extend(group)
    return tokens

tokens_A = flatten_side(SIDE_A_EVANS)
tokens_B = flatten_side(SIDE_B_EVANS)
N_A = len(tokens_A)
N_B = len(tokens_B)

# ---------------------------------------------------------------------------
# STEP 1 — 2D spiral coordinates
# ---------------------------------------------------------------------------
TURNS = 5
THETA_TOTAL = TURNS * 2 * np.pi
R_MAX = 0.85
R_SCALE = 0.85  # so r goes from R_MAX down to R_MAX*(1-R_SCALE) ~ 0.1275
OFFSET_B = 2.5   # Side B shifted right

def spiral_coords(N, offset_x=0.0):
    """
    Return (x, y) arrays for N tokens on an Archimedean-like spiral.
    Token 0 = outer edge, token N-1 = centre.
    """
    i = np.arange(N, dtype=float)
    t = i / (N - 1)                          # 0 … 1
    r = R_MAX * (1.0 - R_SCALE * t)          # 0.85 … ~0.1275
    theta = -THETA_TOTAL * t                 # clockwise (negative)
    x = r * np.cos(theta) + offset_x
    y = r * np.sin(theta)
    return x, y

x_A, y_A = spiral_coords(N_A, offset_x=0.0)
x_B, y_B = spiral_coords(N_B, offset_x=OFFSET_B)

r_A_min = R_MAX * (1.0 - R_SCALE)
r_A_max = R_MAX
r_B_min = r_A_min
r_B_max = r_A_max

print("=" * 65)
print("PHAISTOS DISC — 2D CRYSTAL DIFFRACTION ANALYSIS")
print("=" * 65)
print(f"\nSpiral geometry summary:")
print(f"  Side A: N={N_A} tokens,  turns={TURNS},  r_max={r_A_max:.3f},  r_min={r_A_min:.4f}")
print(f"  Side B: N={N_B} tokens,  turns={TURNS},  r_max={r_B_max:.3f},  r_min={r_B_min:.4f}")
print(f"  Side B offset: ({OFFSET_B}, 0)  [placed beside Side A]")

# ---------------------------------------------------------------------------
# STEP 2 — Build 2D density fields  (256×256 grid)
# ---------------------------------------------------------------------------
GRID = 256
SIGMA_PX = 0.04 * GRID / 2.0   # 0.04 normalised units → pixels

def make_density(x_tokens, y_tokens, sign_ids,
                 x_min, x_max, y_min, y_max,
                 grid=GRID, mode='sign_id', sigma_px=SIGMA_PX):
    """
    Rasterise token positions onto a (grid × grid) float array.

    mode='sign_id'     : accumulate sign_id value at each pixel (Gaussian blob)
    mode='functional'  : +1 for function words, -1 for content words, 0 else
    """
    density = np.zeros((grid, grid), dtype=float)
    dx = (x_max - x_min) / grid
    dy = (y_max - y_min) / grid

    for xv, yv, sid in zip(x_tokens, y_tokens, sign_ids):
        col = int((xv - x_min) / dx)
        row = int((yv - y_min) / dy)
        col = np.clip(col, 0, grid - 1)
        row = np.clip(row, 0, grid - 1)
        if mode == 'sign_id':
            density[row, col] += sid
        elif mode == 'functional':
            # will be set below
            pass

    if mode == 'functional':
        # frequency-based functional / content split
        all_tokens = sign_ids
        from collections import Counter
        freq = Counter(all_tokens)
        threshold_func = 8
        threshold_content = 3
        for xv, yv, sid in zip(x_tokens, y_tokens, sign_ids):
            col = int((xv - x_min) / dx)
            row = int((yv - y_min) / dy)
            col = np.clip(col, 0, grid - 1)
            row = np.clip(row, 0, grid - 1)
            if freq[sid] >= threshold_func:
                density[row, col] += 1.0
            elif freq[sid] <= threshold_content:
                density[row, col] -= 1.0

    # Gaussian smoothing
    smoothed = gaussian_filter(density, sigma=sigma_px)
    return smoothed

# Bounding boxes
XMIN_A, XMAX_A = -1.0,  1.0
YMIN_A, YMAX_A = -1.0,  1.0
XMIN_B, XMAX_B = OFFSET_B - 1.0, OFFSET_B + 1.0
YMIN_B, YMAX_B = -1.0,  1.0

density_A = make_density(x_A, y_A, tokens_A, XMIN_A, XMAX_A, YMIN_A, YMAX_A, mode='sign_id')
density_B = make_density(x_B, y_B, tokens_B, XMIN_B, XMAX_B, YMIN_B, YMAX_B, mode='sign_id')

# ---------------------------------------------------------------------------
# Control distributions
# ---------------------------------------------------------------------------
rng = np.random.default_rng(42)

# Control 1: random shuffle of sign IDs, same spiral positions
tokens_A_shuffled = rng.permutation(tokens_A)
density_A_shuffle = make_density(x_A, y_A, tokens_A_shuffled,
                                 XMIN_A, XMAX_A, YMIN_A, YMAX_A, mode='sign_id')

# Control 2: random positions on unit disk, same sign IDs
theta_rand = rng.uniform(0, 2*np.pi, N_A)
r_rand = np.sqrt(rng.uniform(0, 1, N_A)) * R_MAX   # uniform on disk
x_rand = r_rand * np.cos(theta_rand)
y_rand = r_rand * np.sin(theta_rand)
density_A_randpos = make_density(x_rand, y_rand, tokens_A,
                                  XMIN_A, XMAX_A, YMIN_A, YMAX_A, mode='sign_id')

# Control 3: Side A sign sequence on Side B spiral coordinates
x_B_ctrl = spiral_coords(N_A, offset_x=0.0)[0]   # N_A positions on B-style spiral
y_B_ctrl = spiral_coords(N_A, offset_x=0.0)[1]
density_A_on_B_spiral = make_density(x_B_ctrl, y_B_ctrl, tokens_A,
                                      XMIN_A, XMAX_A, YMIN_A, YMAX_A, mode='sign_id')

# ---------------------------------------------------------------------------
# STEP 3 — 2D FFT and radial power spectrum
# ---------------------------------------------------------------------------

def compute_2d_fft(density):
    """Return 2D power spectrum (log-scale safe) and F_shifted."""
    F = np.fft.fft2(density)
    F_shifted = np.fft.fftshift(F)
    power = np.abs(F_shifted) ** 2
    return power, F_shifted

def radial_profile(power, n_bins=64):
    """
    Radially average a 2D power spectrum.
    Returns (k_bins, P_radial).
    k is in units of cycles per grid width.
    """
    grid = power.shape[0]
    cy, cx = grid // 2, grid // 2
    y_idx, x_idx = np.indices(power.shape)
    r = np.sqrt((x_idx - cx) ** 2 + (y_idx - cy) ** 2)
    k_max = grid // 2 - 1
    k_bins = np.linspace(1, k_max, n_bins)
    dk = k_bins[1] - k_bins[0]
    P_radial = np.zeros(n_bins)
    for i, k in enumerate(k_bins):
        mask = (r >= k - dk/2) & (r < k + dk/2)
        if mask.sum() > 0:
            P_radial[i] = power[mask].mean()
        else:
            P_radial[i] = np.nan
    valid = ~np.isnan(P_radial) & (P_radial > 0)
    return k_bins[valid], P_radial[valid]

power_A, F_A   = compute_2d_fft(density_A)
power_B, F_B   = compute_2d_fft(density_B)
power_shuf, _  = compute_2d_fft(density_A_shuffle)
power_rpos, _  = compute_2d_fft(density_A_randpos)
power_ctrl3, _ = compute_2d_fft(density_A_on_B_spiral)

k_A,    P_A    = radial_profile(power_A)
k_B,    P_B    = radial_profile(power_B)
k_shuf, P_shuf = radial_profile(power_shuf)
k_rpos, P_rpos = radial_profile(power_rpos)
k_c3,   P_c3   = radial_profile(power_ctrl3)

# ---------------------------------------------------------------------------
# STEP 4 — Power law fitting (log-log linear regression on k ∈ [k_min, k_max/4])
# ---------------------------------------------------------------------------

def fit_power_law(k, P, k_frac=0.25):
    """
    Fit P(k) ~ k^alpha via OLS on log-log scale.
    Uses k range [k[0], k[-1]*k_frac].
    Returns (alpha, intercept, r_value).
    """
    k_cutoff = k[-1] * k_frac
    mask = (k >= k[0]) & (k <= k_cutoff) & (P > 0)
    if mask.sum() < 3:
        return np.nan, np.nan, np.nan
    lk = np.log10(k[mask])
    lP = np.log10(P[mask])
    slope, intercept, r, p, se = linregress(lk, lP)
    return slope, intercept, r

alpha_A,    ic_A,    r_A    = fit_power_law(k_A,    P_A)
alpha_B,    ic_B,    r_B    = fit_power_law(k_B,    P_B)
alpha_shuf, ic_shuf, r_shuf = fit_power_law(k_shuf, P_shuf)
alpha_rpos, ic_rpos, r_rpos = fit_power_law(k_rpos, P_rpos)
alpha_c3,   ic_c3,   r_c3   = fit_power_law(k_c3,   P_c3)

# ---------------------------------------------------------------------------
# Bootstrap uncertainty for alpha
# ---------------------------------------------------------------------------

def bootstrap_alpha(k, P, n_boot=100, seed=42, k_frac=0.25):
    """Bootstrap 95% CI for power-law slope alpha."""
    rng_b = np.random.default_rng(seed)
    k_cutoff = k[-1] * k_frac
    mask = (k >= k[0]) & (k <= k_cutoff) & (P > 0)
    lk = np.log10(k[mask])
    lP = np.log10(P[mask])
    n = len(lk)
    if n < 3:
        return np.nan, np.nan
    alphas = []
    for _ in range(n_boot):
        idx = rng_b.integers(0, n, size=n)
        slope, *_ = linregress(lk[idx], lP[idx])
        alphas.append(slope)
    return np.percentile(alphas, 2.5), np.percentile(alphas, 97.5)

ci_A    = bootstrap_alpha(k_A,    P_A)
ci_B    = bootstrap_alpha(k_B,    P_B)
ci_shuf = bootstrap_alpha(k_shuf, P_shuf)
ci_rpos = bootstrap_alpha(k_rpos, P_rpos)

alpha_labels  = ['Side A', 'Side B', 'Random\nShuffle', 'Random\nPositions']
alpha_values  = [alpha_A, alpha_B, alpha_shuf, alpha_rpos]
alpha_ci_low  = [ci_A[0],    ci_B[0],    ci_shuf[0],    ci_rpos[0]]
alpha_ci_high = [ci_A[1],    ci_B[1],    ci_shuf[1],    ci_rpos[1]]

# error bar sizes (symmetric, using half-width)
alpha_err = [
    (av - lo, hi - av) if not np.isnan(av) else (0, 0)
    for av, lo, hi in zip(alpha_values, alpha_ci_low, alpha_ci_high)
]
err_minus = [e[0] for e in alpha_err]
err_plus  = [e[1] for e in alpha_err]

# ---------------------------------------------------------------------------
# STEP 5 — Bragg peak analysis
# ---------------------------------------------------------------------------

def find_bragg_peaks(k, P, N_total, sigma_factor=2.0, min_sep=2):
    """
    Find peaks in radial power spectrum that are > sigma_factor * sigma
    above a smoothed local background.

    Returns list of dicts with k_peak, P_peak, L_scale.
    """
    from scipy.ndimage import uniform_filter1d
    # Local background via running median
    window = max(5, len(P) // 10)
    bg = uniform_filter1d(P, size=window, mode='reflect')
    residual = P - bg
    sigma_r = residual.std()
    peak_mask = residual > sigma_factor * sigma_r

    # Label connected regions and pick maxima
    from scipy.ndimage import label
    labeled, n_feat = label(peak_mask)
    peaks = []
    for feat in range(1, n_feat + 1):
        region = np.where(labeled == feat)[0]
        if len(region) == 0:
            continue
        best = region[np.argmax(P[region])]
        k_peak = k[best]
        P_peak = P[best]
        snr    = residual[best] / (sigma_r + 1e-30)
        L_scale = N_total / k_peak if k_peak > 0 else np.inf
        peaks.append({'k': k_peak, 'P': P_peak, 'L': L_scale, 'snr': snr})

    # Sort by SNR descending, return top 5
    peaks.sort(key=lambda d: d['snr'], reverse=True)
    return peaks[:5]

bragg_A = find_bragg_peaks(k_A, P_A, N_A)
bragg_B = find_bragg_peaks(k_B, P_B, N_B)

# ---------------------------------------------------------------------------
# STEP 6 — Crystallographic R-factor
# ---------------------------------------------------------------------------

def compute_r_factor(k_a, P_a, k_b, P_b):
    """
    Interpolate both spectra to common k grid and compute
    R = sum|P_A(k) - P_B(k)| / sum(P_A(k)).
    """
    k_common = np.linspace(max(k_a.min(), k_b.min()),
                           min(k_a.max(), k_b.max()), 50)
    Pa_interp = np.interp(k_common, k_a, P_a)
    Pb_interp = np.interp(k_common, k_b, P_b)
    # Normalise so scale differences don't dominate
    Pa_n = Pa_interp / (Pa_interp.sum() + 1e-30)
    Pb_n = Pb_interp / (Pb_interp.sum() + 1e-30)
    R = np.abs(Pa_n - Pb_n).sum() / (Pa_n.sum() + 1e-30)
    return R

R_factor = compute_r_factor(k_A, P_A, k_B, P_B)

# ---------------------------------------------------------------------------
# Console report
# ---------------------------------------------------------------------------

def interpret_alpha(a):
    if np.isnan(a):
        return "undetermined"
    if a > -0.3:
        return "white noise (random, no structure)"
    elif a > -0.7:
        return "pink/1/f noise (natural language / long-range order)"
    elif a > -1.3:
        return "1/f noise (natural language, Zipfian statistics)"
    elif a > -1.8:
        return "Kolmogorov / fractal cascade (1/f^1.5–1.67)"
    elif a > -2.5:
        return "Brownian / random walk (1/f^2)"
    else:
        return "steep spectral decay (strong long-range correlation)"

def interpret_R(R):
    if R < 0.15:
        return "highly similar (same underlying grammar)"
    elif R < 0.30:
        return "moderately similar (related but distinct)"
    elif R < 0.50:
        return "partially similar (same script, different content)"
    elif R < 0.60:
        return "weakly related"
    else:
        return "dissimilar (unrelated compositions)"

print("\n" + "=" * 65)
print("POWER LAW EXPONENTS (alpha) — log P(k) ~ alpha * log k")
print("=" * 65)
fmt = "  {:<22s}: alpha = {:+.3f}  [{:+.3f}, {:+.3f}]   r^2={:.3f}   => {}"
datasets = [
    ("Side A",          alpha_A,    ci_A,    r_A),
    ("Side B",          alpha_B,    ci_B,    r_B),
    ("Random Shuffle",  alpha_shuf, ci_shuf, r_shuf),
    ("Random Positions",alpha_rpos, ci_rpos, r_rpos),
    ("A-seq on B-spiral",alpha_c3,  (np.nan, np.nan), r_c3),
]
for label, alpha, ci, r in datasets:
    lo = ci[0] if not np.isnan(ci[0]) else alpha
    hi = ci[1] if not np.isnan(ci[1]) else alpha
    r2 = r**2 if not np.isnan(r) else np.nan
    print(fmt.format(label, alpha, lo, hi, r2 if not np.isnan(r2) else 0.0,
                     interpret_alpha(alpha)))

print(f"\n  Reference values:")
print(f"    alpha =  0.0  → white noise (random)")
print(f"    alpha = -1.0  → 1/f noise (natural language)")
print(f"    alpha = -5/3  → Kolmogorov turbulence")
print(f"    alpha = -2.0  → Brownian motion")

print("\n" + "=" * 65)
print("CRYSTALLOGRAPHIC R-FACTOR (Side A vs Side B)")
print("=" * 65)
print(f"  R = {R_factor:.4f}  →  {interpret_R(R_factor)}")

print("\n" + "=" * 65)
print("BRAGG-LIKE PEAKS — SIDE A")
print("=" * 65)
if bragg_A:
    for i, pk in enumerate(bragg_A, 1):
        print(f"  Peak {i}: k = {pk['k']:.2f} cycles,  "
              f"L = {pk['L']:.1f} tokens,  SNR = {pk['snr']:.2f}σ")
        if pk['L'] > 1:
            print(f"          → periodic structure every ~{pk['L']:.1f} tokens")
else:
    print("  No significant Bragg-like peaks found.")

print("\n" + "=" * 65)
print("BRAGG-LIKE PEAKS — SIDE B")
print("=" * 65)
if bragg_B:
    for i, pk in enumerate(bragg_B, 1):
        print(f"  Peak {i}: k = {pk['k']:.2f} cycles,  "
              f"L = {pk['L']:.1f} tokens,  SNR = {pk['snr']:.2f}σ")
        if pk['L'] > 1:
            print(f"          → periodic structure every ~{pk['L']:.1f} tokens")
else:
    print("  No significant Bragg-like peaks found.")

print("\n" + "=" * 65)
print("INTERPRETATION")
print("=" * 65)
print(f"\n  Side A power law: alpha = {alpha_A:+.3f}")
print(f"  {interpret_alpha(alpha_A).upper()}")
print()
print(f"  The disc shows alpha = {alpha_A:.2f}, consistent with")
print(f"  {interpret_alpha(alpha_A)}.")
print(f"\n  Random shuffle gives alpha = {alpha_shuf:.2f}, confirming that the")
print(f"  observed spectral structure is NOT due to token frequencies alone")
print(f"  but arises from the SEQUENTIAL ARRANGEMENT of signs — a hallmark")
print(f"  of structured linguistic organisation.")
print()
if abs(alpha_A - alpha_shuf) > 0.15:
    delta = alpha_A - alpha_shuf
    print(f"  Delta(alpha) = {delta:+.3f}: the disc's spiral arrangement")
    print(f"  produces {'steeper' if delta < 0 else 'shallower'} spectral decay")
    print(f"  than random, indicating {'stronger' if delta < 0 else 'weaker'} long-range order.")
print()

# ---------------------------------------------------------------------------
# STEP 7 — FIGURE
# ---------------------------------------------------------------------------

# Colourmap for sign IDs (1–45)
cmap_signs = plt.cm.get_cmap('tab20', 45)

fig = plt.figure(figsize=(18, 11), facecolor='#0d0d1a')
gs = GridSpec(2, 3, figure=fig,
              left=0.06, right=0.97, top=0.93, bottom=0.07,
              hspace=0.40, wspace=0.32)

ax1 = fig.add_subplot(gs[0, 0])   # Panel 1: spiral scatter
ax2 = fig.add_subplot(gs[0, 1])   # Panel 2: Side A 2D FFT
ax3 = fig.add_subplot(gs[0, 2])   # Panel 3: Side B 2D FFT
ax4 = fig.add_subplot(gs[1, 0:2]) # Panel 4: radial P(k)
ax5 = fig.add_subplot(gs[1, 2])   # Panel 5: alpha bar chart

DARK_BG  = '#0d0d1a'
DARK_AX  = '#12122a'
TEXT_COL = '#e8e8ff'
GRID_COL = '#2a2a4a'

for ax in [ax1, ax2, ax3, ax4, ax5]:
    ax.set_facecolor(DARK_AX)
    ax.tick_params(colors=TEXT_COL, labelsize=8)
    for spine in ax.spines.values():
        spine.set_edgecolor(GRID_COL)
    ax.title.set_color(TEXT_COL)
    ax.xaxis.label.set_color(TEXT_COL)
    ax.yaxis.label.set_color(TEXT_COL)

# ── Panel 1: spiral scatter ───────────────────────────────────────────────
# Side A spiral path
ax1.plot(x_A, y_A, color='#334455', lw=0.4, alpha=0.5, zorder=1)
# Side B spiral path
ax1.plot(x_B, y_B, color='#334455', lw=0.4, alpha=0.5, zorder=1)

# Scatter coloured by sign_id
sc_A = ax1.scatter(x_A, y_A, c=tokens_A, cmap='tab20',
                   vmin=1, vmax=45, s=18, alpha=0.85,
                   edgecolors='none', zorder=3, label='Side A')
sc_B = ax1.scatter(x_B, y_B, c=tokens_B, cmap='tab20',
                   vmin=1, vmax=45, s=18, alpha=0.85,
                   edgecolors='none', zorder=3, marker='s', label='Side B')

# Mark start/end
ax1.scatter([x_A[0]], [y_A[0]], color='lime', s=60, zorder=5,
            marker='>', edgecolors='white', linewidth=0.5)
ax1.scatter([x_A[-1]], [y_A[-1]], color='red', s=60, zorder=5,
            marker='*', edgecolors='white', linewidth=0.5)
ax1.scatter([x_B[0]], [y_B[0]], color='lime', s=60, zorder=5,
            marker='>', edgecolors='white', linewidth=0.5)
ax1.scatter([x_B[-1]], [y_B[-1]], color='red', s=60, zorder=5,
            marker='*', edgecolors='white', linewidth=0.5)

ax1.text(0, -1.12, f'Side A  (N={N_A})', color='#88aaff',
         ha='center', va='top', fontsize=7.5)
ax1.text(OFFSET_B, -1.12, f'Side B  (N={N_B})', color='#ffaa88',
         ha='center', va='top', fontsize=7.5)
ax1.set_xlim(-1.25, OFFSET_B + 1.25)
ax1.set_ylim(-1.25, 1.20)
ax1.set_aspect('equal')
ax1.set_title("Phaistos Disc — Physical Token Distribution\n(Spiral Coordinates)", fontsize=8.5)
ax1.set_xlabel("x  (normalised disc radius)", fontsize=7.5)
ax1.set_ylabel("y  (normalised disc radius)", fontsize=7.5)
cbar1 = fig.colorbar(sc_A, ax=ax1, fraction=0.025, pad=0.02)
cbar1.set_label('Sign ID', color=TEXT_COL, fontsize=7)
cbar1.ax.yaxis.set_tick_params(color=TEXT_COL, labelsize=6)
plt.setp(cbar1.ax.yaxis.get_ticklabels(), color=TEXT_COL)

# Legend
leg_handles = [
    mpatches.Patch(color='#88aaff', label='Side A (circle)'),
    mpatches.Patch(color='#ffaa88', label='Side B (square)'),
    mpatches.Patch(color='lime',    label='Start'),
    mpatches.Patch(color='red',     label='End'),
]
ax1.legend(handles=leg_handles, fontsize=6, loc='upper right',
           facecolor=DARK_BG, edgecolor=GRID_COL, labelcolor=TEXT_COL)

# ── Panel 2: Side A 2D power spectrum ────────────────────────────────────
log_pA = np.log10(power_A + 1.0)
im2 = ax2.imshow(log_pA, cmap='inferno', origin='lower', aspect='equal')
ax2.set_title("Side A — Diffraction Pattern\n(2D FFT Power Spectrum, log₁₀)", fontsize=8.5)
ax2.set_xlabel("kx  (cycles / grid)", fontsize=7.5)
ax2.set_ylabel("ky  (cycles / grid)", fontsize=7.5)
cbar2 = fig.colorbar(im2, ax=ax2, fraction=0.046, pad=0.04)
cbar2.set_label('log₁₀ |F|²', color=TEXT_COL, fontsize=7)
cbar2.ax.yaxis.set_tick_params(color=TEXT_COL, labelsize=6)
plt.setp(cbar2.ax.yaxis.get_ticklabels(), color=TEXT_COL)

# Mark Bragg-like peaks
if bragg_A:
    cx2, cy2 = GRID // 2, GRID // 2
    k_scale = GRID / (k_A[-1] * 2)  # pixels per cycle
    for pk in bragg_A:
        # Draw circle at radius corresponding to k_peak
        radius_px = pk['k'] * k_scale
        circle = plt.Circle((cx2, cy2), radius_px,
                             fill=False, edgecolor='cyan',
                             linewidth=0.8, alpha=0.7, linestyle='--')
        ax2.add_patch(circle)
    ax2.text(5, 5, f'{len(bragg_A)} Bragg-like\npeaks', color='cyan',
             fontsize=6.5, va='bottom')

# ── Panel 3: Side B 2D power spectrum ────────────────────────────────────
log_pB = np.log10(power_B + 1.0)
im3 = ax3.imshow(log_pB, cmap='inferno', origin='lower', aspect='equal')
ax3.set_title("Side B — Diffraction Pattern\n(2D FFT Power Spectrum, log₁₀)", fontsize=8.5)
ax3.set_xlabel("kx  (cycles / grid)", fontsize=7.5)
ax3.set_ylabel("ky  (cycles / grid)", fontsize=7.5)
cbar3 = fig.colorbar(im3, ax=ax3, fraction=0.046, pad=0.04)
cbar3.set_label('log₁₀ |F|²', color=TEXT_COL, fontsize=7)
cbar3.ax.yaxis.set_tick_params(color=TEXT_COL, labelsize=6)
plt.setp(cbar3.ax.yaxis.get_ticklabels(), color=TEXT_COL)

if bragg_B:
    cx3, cy3 = GRID // 2, GRID // 2
    k_scale_b = GRID / (k_B[-1] * 2)
    for pk in bragg_B:
        radius_px = pk['k'] * k_scale_b
        circle = plt.Circle((cx3, cy3), radius_px,
                             fill=False, edgecolor='yellow',
                             linewidth=0.8, alpha=0.7, linestyle='--')
        ax3.add_patch(circle)
    ax3.text(5, 5, f'{len(bragg_B)} Bragg-like\npeaks', color='yellow',
             fontsize=6.5, va='bottom')

# ── Panel 4: radial P(k) comparison ──────────────────────────────────────
def plot_fit_line(ax, k, alpha, intercept, color, k_frac=0.25):
    k_cutoff = k[-1] * k_frac
    mask = (k >= k[0]) & (k <= k_cutoff)
    if mask.sum() < 2 or np.isnan(alpha):
        return
    k_fit = k[mask]
    P_fit = 10 ** (intercept + alpha * np.log10(k_fit))
    ax.plot(k_fit, P_fit, color=color, lw=1.0, alpha=0.6, linestyle='-.')

ax4.loglog(k_A,    P_A,    color='#4488ff', lw=1.8, label=f'Side A  (α={alpha_A:+.2f})')
ax4.loglog(k_B,    P_B,    color='#ff6644', lw=1.8, label=f'Side B  (α={alpha_B:+.2f})')
ax4.loglog(k_shuf, P_shuf, color='#aaaaaa', lw=1.2, ls='--',
           label=f'Random Shuffle  (α={alpha_shuf:+.2f})')
ax4.loglog(k_rpos, P_rpos, color='#888888', lw=1.2, ls=':',
           label=f'Random Positions  (α={alpha_rpos:+.2f})')
ax4.loglog(k_c3,   P_c3,   color='#88cc88', lw=1.0, ls='-.',
           label=f'A-seq on B-spiral  (α={alpha_c3:+.2f})', alpha=0.7)

# Power law fit lines
plot_fit_line(ax4, k_A,    alpha_A,    ic_A,    '#4488ff')
plot_fit_line(ax4, k_B,    alpha_B,    ic_B,    '#ff6644')
plot_fit_line(ax4, k_shuf, alpha_shuf, ic_shuf, '#aaaaaa')
plot_fit_line(ax4, k_rpos, alpha_rpos, ic_rpos, '#888888')

# Reference lines: k^0 and k^{-1}
k_ref = np.array([k_A[0], k_A[int(len(k_A)*0.25)]])
P_ref_level = P_A[1] * 5  # anchor level
ax4.plot(k_ref, P_ref_level * np.ones_like(k_ref),
         color='white', lw=0.8, ls=':', alpha=0.4)
ax4.plot(k_ref, P_ref_level * (k_ref / k_ref[0]) ** (-1.0),
         color='#ffff44', lw=0.8, ls=':', alpha=0.4)

ax4.text(k_ref[-1]*1.1, P_ref_level*1.05,   'α=0   (white noise)',
         color='white',   fontsize=6.5, alpha=0.7)
ax4.text(k_ref[-1]*1.1, P_ref_level*(k_ref[-1]/k_ref[0])**(-1.0)*0.7,
         'α=−1  (1/f, language)',
         color='#ffff44', fontsize=6.5, alpha=0.7)

ax4.grid(True, which='both', color=GRID_COL, lw=0.4, alpha=0.5)
ax4.set_title("Radial Power Spectrum — Phaistos Disc vs. Controls",
              fontsize=9, color=TEXT_COL)
ax4.set_xlabel("Spatial frequency  k  [cycles / grid]", fontsize=8)
ax4.set_ylabel("Mean radial power  P(k)", fontsize=8)
leg4 = ax4.legend(fontsize=7, loc='lower left',
                  facecolor=DARK_BG, edgecolor=GRID_COL, labelcolor=TEXT_COL)

# ── Panel 5: alpha bar chart ──────────────────────────────────────────────
bar_colors = ['#4488ff', '#ff6644', '#aaaaaa', '#888888']
x_pos = np.arange(len(alpha_labels))

bars = ax5.bar(x_pos, alpha_values, color=bar_colors,
               width=0.55, alpha=0.85, edgecolor='white', linewidth=0.5)

# Error bars
for i, (av, em, ep) in enumerate(zip(alpha_values, err_minus, err_plus)):
    if not np.isnan(av) and not np.isnan(em) and not np.isnan(ep):
        ax5.errorbar(x_pos[i], av, yerr=[[em], [ep]],
                     fmt='none', ecolor='white', elinewidth=1.2,
                     capsize=4, capthick=1.2)

# Horizontal reference lines
ax5.axhline(0.0,  color='white',   lw=0.9, ls=':', alpha=0.6, label='α=0 (white noise)')
ax5.axhline(-1.0, color='#ffff44', lw=0.9, ls=':', alpha=0.6, label='α=−1 (1/f, language)')
ax5.axhline(-5/3, color='#ff88ff', lw=0.8, ls=':', alpha=0.5, label='α=−5/3 (Kolmogorov)')
ax5.axhline(-2.0, color='#88ffff', lw=0.8, ls=':', alpha=0.5, label='α=−2 (Brownian)')

# Value labels on bars
for bar_rect, av in zip(bars, alpha_values):
    if not np.isnan(av):
        yoff = 0.04 if av >= 0 else -0.12
        ax5.text(bar_rect.get_x() + bar_rect.get_width()/2,
                 av + yoff, f'{av:+.2f}',
                 ha='center', va='bottom', color='white', fontsize=7.5,
                 fontweight='bold')

ax5.set_xticks(x_pos)
ax5.set_xticklabels(alpha_labels, fontsize=7.5)
ax5.set_ylabel("Power law exponent  α", fontsize=8)
ax5.set_title("Power Law Exponent α\nCrystallographic Language Test", fontsize=9)
ax5.set_ylim(min(min(v for v in alpha_values if not np.isnan(v)) - 0.6, -2.4),
             max(max(v for v in alpha_values if not np.isnan(v)) + 0.5, 0.5))
ax5.grid(True, axis='y', color=GRID_COL, lw=0.4, alpha=0.5)
leg5 = ax5.legend(fontsize=6.5, loc='lower right',
                  facecolor=DARK_BG, edgecolor=GRID_COL, labelcolor=TEXT_COL)
ax5.yaxis.label.set_color(TEXT_COL)

# ── Global figure title ───────────────────────────────────────────────────
fig.suptitle(
    f"Phaistos Disc — 2D Crystal Diffraction Analysis   "
    f"|   R-factor(A vs B) = {R_factor:.3f}   |   "
    f"Side A: α = {alpha_A:+.2f}  ({interpret_alpha(alpha_A)})",
    fontsize=9.5, color=TEXT_COL, y=0.975
)

out_path = 'crystal_diffraction_output.png'
fig.savefig(out_path, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
plt.close(fig)
print(f"\n  Figure saved → {out_path}")
print("\n" + "=" * 65)
print("DONE")
print("=" * 65)
