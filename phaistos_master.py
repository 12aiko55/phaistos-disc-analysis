"""
phaistos_master.py
══════════════════════════════════════════════════════════════════════════════
MASTER RUNNER — Arena + Hybrid Arena + MDL + IG  (one script)
Chavadakis 2026

  §1  Build corpora (once, shared across all judges)
  §2  Arena          — MCTS, 7 pure languages, vocab=200 each
  §3  Hybrid Arena   — 7 pure + 21 pairs + 7 triples, NORMALIZED vocab=200
  §4  MDL Judge      — Bigram LM compression score
  §5  IG Judge       — Expected information gain over 20k keys
  §6  Master scoreboard

NORMALIZATION (key fix):
  Every entity (pure AND hybrid) gets exactly 200 bigrams.
  Hybrid corpus = concatenated raw syllables of both parents → top-200.
  Eliminates the vocabulary-size advantage hybrids had before.

python phaistos_master.py
"""

import json, re, csv, zipfile, sys, time
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict
from itertools import combinations
from math import log, log2, sqrt
import multiprocessing as mp
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SEP  = "═" * 70
SEP2 = "─" * 70
VOCAB_SIZE = 200
N_ASSIGN   = 9
T_IG       = 1.0

# ══════════════════════════════════════════════════════════════════════════════
# §0  DISC DATA
# ══════════════════════════════════════════════════════════════════════════════
DATA_PATH = Path("hp4k1h5_phaistos_disc/src/phaistos_disc/data/phaistos-disc_outside-in.json")
with open(DATA_PATH, encoding="utf-8") as f:
    _raw = json.load(f)

SIDE_A    = [[int(s) for s in w if s != "??"] for w in _raw["side_a"]]
SIDE_B    = [[int(s) for s in w if s != "??"] for w in _raw["side_b"]]
ALL_WORDS = SIDE_A + SIDE_B
ALL_SIGNS = sorted(set(s for w in ALL_WORDS for s in w if s != 46))

# ══════════════════════════════════════════════════════════════════════════════
# §1  CORPUS HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def _gdl_syls(gdl):
    out = []
    for g in gdl:
        if g.get("det"): continue
        v = g.get("v", "")
        if v:
            c = re.sub(r'[₀₁₂₃₄₅₆₇₈₉\d]', '', str(v))
            c = re.sub(r'[^a-zāīūšḫṭqḥŋ]', '', c.lower())
            if c and 1 <= len(c) <= 6: out.append(c)
        if "seq" in g: out.extend(_gdl_syls(g["seq"]))
    return out

def _walk_cdl(obj, lp, out):
    if isinstance(obj, list):
        for x in obj: _walk_cdl(x, lp, out)
    elif isinstance(obj, dict):
        if obj.get("node") == "l" and "f" in obj:
            f = obj["f"]
            if lp is None or f.get("lang", "").startswith(lp):
                out.extend(_gdl_syls(f.get("gdl", [])))
        elif "cdl" in obj: _walk_cdl(obj["cdl"], lp, out)

def cdl_from_zip(zp, lp=None, mf=2000):
    syls = []
    try:
        with zipfile.ZipFile(zp) as zf:
            for nm in [n for n in zf.namelist()
                       if re.search(r'[PQ]\d+\.json$', n)][:mf]:
                try:
                    with zf.open(nm) as f: data = json.load(f)
                    _walk_cdl(data.get("cdl", []), lp, syls)
                except Exception: continue
    except Exception as e: print(f"    [warn] {zp}: {e}")
    return syls

def gloss_from_zip(zp, gnames):
    syls = []
    try:
        with zipfile.ZipFile(zp) as zf:
            for gn in gnames:
                try:
                    with zf.open(gn) as f: data = json.load(f)
                    for e in data.get("entries", []):
                        for part in e.get("cf", "").split("-"):
                            part = re.sub(r"[₀₁₂₃₄₅₆₇₈₉\d']", "", part)
                            part = re.sub(r"[^a-zāīūšḫṭqḥŋ]", "", part.lower())
                            if part and 1 <= len(part) <= 6: syls.append(part)
                except Exception: continue
    except Exception as e: print(f"    [warn] {zp}: {e}")
    return syls

def _make_vocab(syls):
    bgs = [f"{syls[i]}-{syls[i+1]}" for i in range(len(syls) - 1)]
    return frozenset(tuple(v.split("-"))
                     for v, _ in Counter(bgs).most_common(VOCAB_SIZE))

def _make_pool(syls, n=50):
    return [s for s, _ in Counter(syls).most_common(n)]

def _make_bigram_lm(syls, eps=1e-6):
    uni = Counter(syls); V = len(uni); tot = sum(uni.values())
    uni_lp = {s: log2((c + eps) / (tot + eps * V)) for s, c in uni.items()}
    bi = defaultdict(Counter)
    for i in range(len(syls) - 1): bi[syls[i]][syls[i+1]] += 1
    bi_lp = {}
    for s1 in uni:
        rt = sum(bi[s1].values()) + eps * V
        bi_lp[s1] = {s2: log2((bi[s1][s2] + eps) / rt) for s2 in uni}
    return uni_lp, bi_lp

def build_corpora():
    print(f"\n{SEP}\n  §1  BUILDING CORPORA\n{SEP}")
    C = {}

    print("  Luwian/Hittite…")
    syls = []
    with zipfile.ZipFile("TLHdig_0.2.0-beta.zip") as zf:
        for nm in [n for n in zf.namelist() if n.endswith(".xml")][:500]:
            with zf.open(nm) as f:
                tx = re.sub(r'<[^>]+>', ' ', f.read().decode("utf-8", "replace"))
                for t in re.split(r'[\s\-]+', tx):
                    t = re.sub(r'[^a-zāīūšḥḫṭ]', '', t.lower())
                    if t and 1 <= len(t) <= 5: syls.append(t)
    C["Luwian/Hittite"] = syls; print(f"    {len(syls):,} tokens")

    print("  Linear B…")
    syls = []
    with open("corpora/linearb/words.csv", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            w = row.get("word", "").strip().lower()
            if not w or w.startswith("*"): continue
            for s in w.split("-"):
                s = re.sub(r'[^a-z]', '', s)
                if s: syls.append(s)
    C["Linear B"] = syls; print(f"    {len(syls):,} tokens")

    print("  Akkadian…")
    syls  = gloss_from_zip("corpora/akkadian/saao.zip", [
        "saao/gloss-akk.json", "saao/gloss-akk-x-neoass.json",
        "saao/gloss-akk-x-midass.json", "saao/gloss-akk-x-stdbab.json",
        "saao/gloss-akk-x-neobab.json"])
    syls += gloss_from_zip("corpora/akkadian/rinap.zip", ["rinap/gloss-akk.json"])
    syls += gloss_from_zip("corpora/akkadian/ribo.zip",  ["ribo/gloss-akk.json"])
    C["Akkadian"] = syls; print(f"    {len(syls):,} tokens")

    print("  Egyptian…")
    syls = []
    aes = Path("corpora/egyptian/aes/files/aes")
    for fn in ["_aes_bbawpyramidentexte.json", "_aes_sawlit.json",
               "_aes_bbawtotenlit.json"]:
        fp = aes / fn
        if not fp.exists(): continue
        try:
            with open(fp, encoding="utf-8") as f: data = json.load(f)
            for sent in data.values():
                if not isinstance(sent, dict): continue
                for tok in sent.get("token", []):
                    wf = tok.get("written_form", "")
                    for seg in re.split(r'[-,.\s{}/\\]', wf):
                        seg = re.sub(r'[\d₀-₉]', '', seg)
                        seg = re.sub(r'[^a-zāīūšḥḫṭꜣꜥ]', '', seg.lower())
                        if seg and 1 <= len(seg) <= 6: syls.append(seg)
            if len(syls) > 300_000: break
        except Exception as e: print(f"    [warn] {fn}: {e}")
    C["Egyptian"] = syls; print(f"    {len(syls):,} tokens")

    print("  Sumerian…")
    syls = cdl_from_zip("corpora/sumerian/etcsri.zip", "sux", 500)
    C["Sumerian"] = syls; print(f"    {len(syls):,} tokens")

    print("  Late Babylonian (HBTIN)…")
    syls = cdl_from_zip("corpora/hurrian/hbtin.zip", "akk", 487)
    C["Late Babylonian"] = syls; print(f"    {len(syls):,} tokens")

    print("  Ugaritic…")
    syls = []
    for tsv in sorted(Path("corpora/ugaritic/cuc/auto_parsing").rglob("*.tsv")):
        try:
            with open(tsv, encoding="utf-8") as f:
                for line in f:
                    if line.startswith("#") or line.startswith("id\t"): continue
                    parts = line.split("\t")
                    if len(parts) < 2: continue
                    w = re.sub(r'[!\[\]~{}/\d]', '', parts[1].strip())
                    w = re.sub(r'[^a-zġṭṣẓḥḫšθʿ]', '', w.lower())
                    if w and 1 <= len(w) <= 8: syls.append(w)
        except Exception: continue
    C["Ugaritic"] = syls; print(f"    {len(syls):,} tokens")

    return C

# ══════════════════════════════════════════════════════════════════════════════
# §2  SCORING FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════
def score_key(key, vocab_set):
    if not vocab_set: return 0
    mvl = max(len(v) for v in vocab_set)
    hits = 0
    for word in ALL_WORDS:
        parts = tuple(key.get(s) for s in word if s in key and s != 46)
        n = len(parts)
        if n < 2: continue
        matched = False
        for vl in range(2, min(mvl, n) + 1):
            for i in range(n - vl + 1):
                if parts[i:i+vl] in vocab_set:
                    matched = True; break
            if matched: break
        if matched: hits += 1
    return hits

_UNK_LP = -15.0

def mdl_cost(key, uni_lp, bi_lp):
    cost = 0.0
    for word in ALL_WORDS:
        phones = [key[s] for s in word if s in key and s != 46]
        if not phones: continue
        cost -= uni_lp.get(phones[0], _UNK_LP)
        for i in range(1, len(phones)):
            cost -= bi_lp.get(phones[i-1], {}).get(phones[i], _UNK_LP)
    return cost

def _entropy(probs):
    return sum(-p * log2(p) for p in probs if p > 1e-15)

def ig_posterior(key, vocab_sets, temp=T_IG):
    n = len(vocab_sets)
    sc = np.array([score_key(key, vs) for vs in vocab_sets], dtype=float)
    lg = sc / temp; lg -= lg.max()
    post = np.exp(lg); post /= post.sum()
    return log2(n) - _entropy(post), post

# ══════════════════════════════════════════════════════════════════════════════
# §3  MODULE-LEVEL WORKERS
# ══════════════════════════════════════════════════════════════════════════════
def _mcts_worker(args):
    pool, vt, n_sim, seed = args
    vs  = frozenset(tuple(v) for v in vt)
    rng = np.random.default_rng(seed)
    Q   = defaultdict(lambda: defaultdict(lambda: [0, 0.0]))
    Np  = defaultdict(int)
    C_UCB = 1.41; NC = 30
    best, bk = 0, {}
    for _ in range(n_sim):
        path, us, up, key = [], set(), set(), {}
        for d in range(N_ASSIGN):
            avs = [s for s in ALL_SIGNS if s not in us]
            avp = [p for p in pool if p not in up] or list(pool)
            if not avs: break
            cands = set()
            for _ in range(NC):
                cands.add((int(rng.choice(avs)), str(rng.choice(avp))))
            pn = Np[d] + 1
            ba, bu = None, -1.0
            for a in cands:
                v, tv = Q[d][a]
                u = tv/v + C_UCB*sqrt(log(pn)/v) if v > 0 else 1e9+rng.random()
                if u > bu: bu, ba = u, a
            s, p = ba; key[s]=p; us.add(s); up.add(p); path.append((d,s,p))
        sc = score_key(key, vs)
        if sc > best: best, bk = sc, dict(key)
        for d, s, p in path:
            Q[d][(s,p)][0]+=1; Q[d][(s,p)][1]+=sc; Np[d]+=1
    key = dict(bk); cur = best
    for _ in range(500):
        k2 = dict(key); mv = int(rng.integers(3))
        if mv == 0:
            s = int(rng.choice(list(k2.keys())))
            av = [p for p in pool if p not in set(k2.values())]
            if not av: continue
            k2[s] = str(rng.choice(av))
        elif mv == 1:
            old = int(rng.choice(list(k2.keys())))
            cd  = [s for s in ALL_SIGNS if s not in k2]
            if not cd: continue
            k2[int(rng.choice(cd))] = k2.pop(old)
        else:
            if len(k2) < 2: continue
            s1, s2 = [int(x) for x in rng.choice(list(k2.keys()), 2, replace=False)]
            k2[s1], k2[s2] = k2[s2], k2[s1]
        sc2 = score_key(k2, vs)
        if sc2 >= cur: key, cur = k2, sc2
    if cur > best: best, bk = cur, dict(key)
    return best, bk

def _null_worker(args):
    pool, vt, n, seed = args
    vs  = frozenset(tuple(v) for v in vt)
    rng = np.random.default_rng(seed)
    pa  = np.array(pool)
    scores = []
    for _ in range(n):
        sg = rng.choice(ALL_SIGNS, N_ASSIGN, replace=False).tolist()
        ph = rng.choice(pa, min(N_ASSIGN, len(pa)), replace=False).tolist()
        scores.append(score_key(dict(zip(sg, ph)), vs))
    return scores

def _mdl_null_worker(args):
    pool, ui, bi_it, n, seed = args
    uni = dict(ui); bi = {k: dict(v) for k, v in bi_it}
    rng = np.random.default_rng(seed); pa = np.array(pool)
    scores = []
    for _ in range(n):
        sg = rng.choice(ALL_SIGNS, N_ASSIGN, replace=False).tolist()
        ph = rng.choice(pa, min(N_ASSIGN, len(pa)), replace=False).tolist()
        scores.append(-mdl_cost(dict(zip(sg, ph)), uni, bi))
    return scores

def _mdl_opt_worker(args):
    pool, ui, bi_it, n_steps, seed = args
    uni = dict(ui); bi = {k: dict(v) for k, v in bi_it}
    rng = np.random.default_rng(seed); pa = np.array(pool)
    bs, bk = -1e18, {}
    for _ in range(max(1, n_steps // 500)):
        sg = rng.choice(ALL_SIGNS, N_ASSIGN, replace=False).tolist()
        ph = rng.choice(pa, min(N_ASSIGN, len(pa)), replace=False).tolist()
        key = dict(zip(sg, ph)); cur = -mdl_cost(key, uni, bi)
        for _ in range(500):
            k2 = dict(key); mv = int(rng.integers(3))
            if mv == 0:
                s = int(rng.choice(list(k2.keys())))
                av = [p for p in pool if p not in set(k2.values())]
                if not av: continue
                k2[s] = str(rng.choice(av))
            elif mv == 1:
                old = int(rng.choice(list(k2.keys())))
                cd  = [s for s in ALL_SIGNS if s not in k2]
                if not cd: continue
                k2[int(rng.choice(cd))] = k2.pop(old)
            else:
                if len(k2) < 2: continue
                s1, s2 = [int(x) for x in rng.choice(list(k2.keys()), 2, replace=False)]
                k2[s1], k2[s2] = k2[s2], k2[s1]
            sc2 = -mdl_cost(k2, uni, bi)
            if sc2 >= cur: key, cur = k2, sc2
        if cur > bs: bs, bk = cur, dict(key)
    return bs, bk

def _ig_worker(args):
    cpool, vtl, n, seed, temp = args
    vsets = [frozenset(tuple(v) for v in vt) for vt in vtl]
    rng   = np.random.default_rng(seed); pa = np.array(cpool)
    nl    = len(vsets)
    sig, sp, ni = 0.0, np.zeros(nl), 0
    big, bpost  = -1.0, np.zeros(nl)
    for _ in range(n):
        sg = rng.choice(ALL_SIGNS, N_ASSIGN, replace=False).tolist()
        ph = rng.choice(pa, min(N_ASSIGN, len(pa)), replace=False).tolist()
        key = dict(zip(sg, ph))
        ig, post = ig_posterior(key, vsets, temp)
        sig += ig; sp += post; ni += 1
        if ig > big: big, bpost = ig, post.copy()
    return sig, sp.tolist(), ni, big, bpost.tolist()

# ══════════════════════════════════════════════════════════════════════════════
# §4  ARENA RUNNER
# ══════════════════════════════════════════════════════════════════════════════
def run_lang(name, pool, vocab_set, n_workers, n_null, n_sim):
    if not vocab_set:
        return dict(name=name, Z=0, p=1.0, opt=0, nm=0, ns=1,
                    null_arr=np.zeros(50), key={}, vn=0, etype="pure")
    vt = [list(v) for v in vocab_set]
    batch = n_null // n_workers; rem = n_null % n_workers
    with mp.Pool(n_workers) as p:
        nb = p.map(_null_worker,
                   [(pool, vt, batch+(1 if i<rem else 0), 99+i)
                    for i in range(n_workers)])
    na = np.array([s for b in nb for s in b])
    nm, ns = na.mean(), na.std(ddof=1)
    per = max(1, n_sim // n_workers); rem2 = n_sim % n_workers
    with mp.Pool(n_workers) as p:
        or_ = p.map(_mcts_worker,
                    [(pool, vt, per+(1 if i<rem2 else 0), 42+i*1000)
                     for i in range(n_workers)])
    opt, key = max(or_, key=lambda x: x[0])
    Z  = (opt - nm) / ns if ns > 0 else 0.0
    pv = float((na >= opt).sum()) / n_null
    return dict(name=name, Z=Z, p=pv, opt=opt, nm=nm, ns=ns,
                null_arr=na, key=key, vn=len(vocab_set))

# ══════════════════════════════════════════════════════════════════════════════
# §5  HYBRID NAMES
# ══════════════════════════════════════════════════════════════════════════════
PAIR_NAMES = {
    ("Luwian/Hittite", "Linear B"):        "Aegeo-Anatolian",
    ("Luwian/Hittite", "Akkadian"):         "Anatolio-Akkadian",
    ("Luwian/Hittite", "Egyptian"):         "Anatolio-Egyptian",
    ("Luwian/Hittite", "Sumerian"):         "Anatolio-Sumerian",
    ("Luwian/Hittite", "Late Babylonian"):  "Anatolio-Babylonian",
    ("Luwian/Hittite", "Ugaritic"):         "Levanto-Anatolian",
    ("Linear B",       "Akkadian"):         "Aegean-Akkadian",
    ("Linear B",       "Egyptian"):         "Aegean-Egyptian",
    ("Linear B",       "Sumerian"):         "Aegean-Sumerian",
    ("Linear B",       "Late Babylonian"):  "Aegean-Babylonian",
    ("Linear B",       "Ugaritic"):         "Aegean Trade Lingua",
    ("Akkadian",       "Egyptian"):         "Egypto-Akkadian",
    ("Akkadian",       "Sumerian"):         "Sumero-Akkadian",
    ("Akkadian",       "Late Babylonian"):  "Akkadian Dialects",
    ("Akkadian",       "Ugaritic"):         "Levanto-Akkadian",
    ("Egyptian",       "Sumerian"):         "Egypto-Sumerian",
    ("Egyptian",       "Late Babylonian"):  "Egypto-Babylonian",
    ("Egyptian",       "Ugaritic"):         "Egypto-Levantine",
    ("Sumerian",       "Late Babylonian"):  "Classic Babylonian",
    ("Sumerian",       "Ugaritic"):         "Sumer-Levantine",
    ("Late Babylonian","Ugaritic"):         "Levanto-Babylonian",
}
TRIPLE_NAMES = {
    ("Luwian/Hittite", "Linear B",    "Ugaritic"):        "Bronze Age Koine",
    ("Luwian/Hittite", "Akkadian",    "Sumerian"):        "Anatolian Scribal Mix",
    ("Akkadian",       "Sumerian",    "Late Babylonian"): "Mesopotamian Continuum",
    ("Luwian/Hittite", "Linear B",    "Egyptian"):        "Eastern Mediterranean",
    ("Linear B",       "Egyptian",    "Ugaritic"):        "Levantine Sea Peoples",
    ("Akkadian",       "Egyptian",    "Ugaritic"):        "Mitanni Court",
    ("Luwian/Hittite", "Akkadian",    "Ugaritic"):        "West Asiatic",
}

# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    t0 = time.time()
    N_WORKERS = max(1, mp.cpu_count() - 1)
    print(f"{SEP}\n  PHAISTOS MASTER ANALYSIS\n  Workers: {N_WORKERS}\n{SEP}")

    # ── §1 Build corpora ──────────────────────────────────────────────────────
    RAW = build_corpora()
    LANGS = list(RAW.keys())
    POOLS  = {l: _make_pool(RAW[l])  for l in LANGS}
    VOCABS = {l: _make_vocab(RAW[l]) for l in LANGS}
    LMAPS  = {l: _make_bigram_lm(RAW[l]) for l in LANGS}

    # ── §2 Pure language arena ────────────────────────────────────────────────
    print(f"\n{SEP}\n  §2  PURE LANGUAGE ARENA\n"
          f"  MCTS+Hill-Climb | 10k null | vocab=200\n{SEP}")
    arena_r = []
    for l in LANGS:
        print(f"  [{l}] …", end=" ", flush=True)
        r = run_lang(l, POOLS[l], VOCABS[l], N_WORKERS, 10_000, 2_000)
        r["etype"] = "pure"
        print(f"Z={r['Z']:+.2f}  p={r['p']:.6f}")
        arena_r.append(r)
    arena_r.sort(key=lambda x: -x["Z"])

    print(f"\n  {'Rank':<4} {'Language':<22} {'MCTS':>5} {'Null μ':>7} "
          f"{'σ':>6} {'Z':>7} {'p':>10}  Pass")
    print(f"  {SEP2}")
    for i, r in enumerate(arena_r, 1):
        print(f"  {i:<4} {r['name']:<22} {r['opt']:>5} {r['nm']:>7.2f} "
              f"{r['ns']:>6.2f} {r['Z']:>+7.2f} {r['p']:>10.6f}  "
              f"{'✓' if r['Z']>=2 else '✗'}")

    # ── §3 Hybrid Arena (NORMALIZED vocab=200) ────────────────────────────────
    print(f"\n{SEP}\n  §3  HYBRID ARENA  —  vocab=200 for ALL entities\n{SEP}")

    # Build all entities with normalized vocab
    all_ents = {}  # name → (pool, vocab_set, etype)
    for l in LANGS:
        all_ents[l] = (POOLS[l], VOCABS[l], "pure")

    for (n1, n2) in combinations(LANGS, 2):
        hname = PAIR_NAMES.get((n1,n2)) or PAIR_NAMES.get((n2,n1)) or f"{n1[:5]}+{n2[:5]}"
        merged = RAW[n1] + RAW[n2]
        all_ents[hname] = (_make_pool(merged), _make_vocab(merged), "pair")

    for key_t, hname in TRIPLE_NAMES.items():
        merged = sum((RAW[n] for n in key_t), [])
        all_ents[hname] = (_make_pool(merged), _make_vocab(merged), "triple")

    print(f"  Entities: {len(all_ents)}  "
          f"({len(LANGS)} pure + {len(all_ents)-len(LANGS)} hybrids)\n")
    hybrid_r = []
    for ename, (pool, vocab_set, etype) in all_ents.items():
        tag = f" [{etype}]" if etype != "pure" else ""
        print(f"  {ename}{tag} …", end=" ", flush=True)
        r = run_lang(ename, pool, vocab_set, N_WORKERS, 5_000, 1_000)
        r["etype"] = etype
        print(f"Z={r['Z']:+.2f}  p={r['p']:.4f}")
        hybrid_r.append(r)
    hybrid_r.sort(key=lambda x: -x["Z"])

    print(f"\n  {'Rank':<4} {'Name':<28} {'Type':<7} {'Voc':>4} {'MCTS':>5} "
          f"{'Null μ':>7} {'σ':>6} {'Z':>7} {'p':>9}  Pass")
    print(f"  {SEP2}")
    for i, r in enumerate(hybrid_r, 1):
        print(f"  {i:<4} {r['name']:<28} {r['etype']:<7} {r['vn']:>4} "
              f"{r['opt']:>5} {r['nm']:>7.2f} {r['ns']:>6.2f} "
              f"{r['Z']:>+7.2f} {r['p']:>9.4f}  {'✓' if r['Z']>=2 else '✗'}")

    # ── §4 MDL Judge ──────────────────────────────────────────────────────────
    print(f"\n{SEP}\n  §4  MDL JUDGE — Bigram LM\n{SEP}")
    mdl_r = []
    for l in LANGS:
        uni_lp, bi_lp = LMAPS[l]
        if not uni_lp: continue
        pool = POOLS[l]
        ui = list(uni_lp.items()); bi = [(k, list(v.items())) for k, v in bi_lp.items()]
        print(f"  [{l}] …", end=" ", flush=True)
        batch = 10_000 // N_WORKERS; rem = 10_000 % N_WORKERS
        with mp.Pool(N_WORKERS) as p:
            nb = p.map(_mdl_null_worker,
                       [(pool, ui, bi, batch+(1 if i<rem else 0), 99+i)
                        for i in range(N_WORKERS)])
        na = np.array([s for b in nb for s in b])
        nm, ns = na.mean(), na.std(ddof=1)
        per = max(1, 2000 // N_WORKERS); rem2 = 2000 % N_WORKERS
        with mp.Pool(N_WORKERS) as p:
            or_ = p.map(_mdl_opt_worker,
                        [(pool, ui, bi, per+(1 if i<rem2 else 0), 42+i*1000)
                         for i in range(N_WORKERS)])
        opt, key = max(or_, key=lambda x: x[0])
        Z  = (opt - nm) / ns if ns > 0 else 0.0
        pv = float((na >= opt).sum()) / 10_000
        print(f"Z={Z:+.2f}  p={pv:.6f}")
        mdl_r.append(dict(name=l, Z=Z, p=pv, opt=opt, nm=nm, ns=ns))
    mdl_r.sort(key=lambda x: -x["Z"])
    print(f"\n  {'Rank':<4} {'Language':<22} {'MDL':>9} {'Null μ':>9} "
          f"{'σ':>7} {'Z':>7} {'p':>10}  Pass")
    print(f"  {SEP2}")
    for i, r in enumerate(mdl_r, 1):
        print(f"  {i:<4} {r['name']:<22} {r['opt']:>9.1f} {r['nm']:>9.1f} "
              f"{r['ns']:>7.1f} {r['Z']:>+7.2f} {r['p']:>10.6f}  "
              f"{'✓' if r['Z']>=2 else '✗'}")

    # ── §5 IG Judge ───────────────────────────────────────────────────────────
    print(f"\n{SEP}\n  §5  IG JUDGE — E[IG] over 20k keys\n{SEP}")
    vsets  = [VOCABS[l] for l in LANGS]
    cpool  = list(set(s for l in LANGS for s in POOLS[l]))
    vtl    = [[list(v) for v in vs] for vs in vsets]
    H_prior = log2(len(LANGS))
    batch = 20_000 // N_WORKERS; rem = 20_000 % N_WORKERS
    with mp.Pool(N_WORKERS) as p:
        ig_b = p.map(_ig_worker,
                     [(cpool, vtl, batch+(1 if i<rem else 0), 42+i*1000, T_IG)
                      for i in range(N_WORKERS)])
    tot_ig   = sum(r[0] for r in ig_b)
    tot_post = np.sum([r[1] for r in ig_b], axis=0)
    tot_n    = sum(r[2] for r in ig_b)
    mean_ig  = tot_ig / tot_n
    mean_post = tot_post / tot_n
    ig_ranked = sorted(zip(LANGS, mean_post), key=lambda x: -x[1])
    ig_winner = ig_ranked[0][0]

    print(f"  H(prior) = {H_prior:.4f} bits")
    print(f"  E[IG]    = {mean_ig:.4f} bits  ({mean_ig/H_prior*100:.1f}% of prior)")
    print(f"\n  Language pull (avg posterior over 20k keys):")
    for lname, prob in ig_ranked:
        bar = "█" * int(prob * 70)
        print(f"    {lname:<22} {prob:.4f}  {bar}")
    print(f"\n  IG Winner: {ig_winner}  (pull={ig_ranked[0][1]:.4f})")

    # ── §6 Master scoreboard ──────────────────────────────────────────────────
    print(f"\n{SEP}\n  §6  MASTER SCOREBOARD\n{SEP}")
    a_rank  = {r["name"]: i+1 for i, r in enumerate(arena_r)}
    h_rank  = {r["name"]: i+1 for i, r in enumerate(hybrid_r)}
    m_rank  = {r["name"]: i+1 for i, r in enumerate(mdl_r)}
    ig_rank = {n: i+1 for i, (n, _) in enumerate(ig_ranked)}

    print(f"  {'Language':<22} {'Arena':>6} {'Hybrid':>7} {'MDL':>5} "
          f"{'IG':>5}  {'AvgRank':>8}")
    print(f"  {SEP2}")
    summary = []
    for l in LANGS:
        ranks = [a_rank.get(l,99), h_rank.get(l,99),
                 m_rank.get(l,99), ig_rank.get(l,99)]
        avg = sum(ranks) / len(ranks)
        summary.append((l, *ranks, avg))
    for row in sorted(summary, key=lambda x: x[-1]):
        l, ar, hr, mr, ir, avg = row
        print(f"  {l:<22} {ar:>6} {hr:>7} {mr:>5} {ir:>5}  {avg:>8.1f}")

    elapsed = time.time() - t0
    print(f"\n{SEP}")
    print(f"  Completed in {elapsed/60:.1f} min")
    print(f"  Arena winner   : {arena_r[0]['name']}  Z={arena_r[0]['Z']:+.2f}")
    print(f"  Hybrid winner  : {hybrid_r[0]['name']}  Z={hybrid_r[0]['Z']:+.2f}")
    print(f"  MDL winner     : {mdl_r[0]['name']}  Z={mdl_r[0]['Z']:+.2f}")
    print(f"  IG winner      : {ig_winner}")
    print(SEP)

    # ── Figures ───────────────────────────────────────────────────────────────
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    fig.patch.set_facecolor("#0d1117")
    C8 = ["#3fb950","#58a6ff","#f0883e","#d2a8ff","#ffa657","#ff7b72","#79c0ff"]

    ax = axes[0]
    ax.set_facecolor("#161b22")
    for sp in ax.spines.values(): sp.set_color("#30363d")
    ax.tick_params(colors="#e6edf3")
    ax.xaxis.label.set_color("#e6edf3"); ax.yaxis.label.set_color("#e6edf3")
    ax.title.set_color("#e6edf3")
    bars = ax.barh([r["name"] for r in arena_r],
                   [r["Z"]    for r in arena_r],
                   color=[C8[i%len(C8)] for i in range(len(arena_r))],
                   edgecolor="#30363d")
    ax.axvline(2.0, color="#f85149", lw=1.5, ls="--")
    for bar, r in zip(bars, arena_r):
        ax.text(r["Z"]+0.1, bar.get_y()+bar.get_height()/2,
                f"{r['Z']:+.1f}", va="center", fontsize=9, color="#e6edf3")
    ax.set_xlabel("Z-score"); ax.set_title("Arena — Pure Languages")
    ax.invert_yaxis()

    ax = axes[1]
    ax.set_facecolor("#161b22")
    for sp in ax.spines.values(): sp.set_color("#30363d")
    ax.tick_params(colors="#e6edf3")
    ax.xaxis.label.set_color("#e6edf3"); ax.yaxis.label.set_color("#e6edf3")
    ax.title.set_color("#e6edf3")
    top20 = hybrid_r[:20]
    cmap  = {"pure": "#58a6ff", "pair": "#3fb950", "triple": "#f0883e"}
    bars2 = ax.barh([r["name"] for r in top20], [r["Z"] for r in top20],
                    color=[cmap[r["etype"]] for r in top20], edgecolor="#30363d")
    ax.axvline(2.0, color="#f85149", lw=1.5, ls="--")
    for bar, r in zip(bars2, top20):
        ax.text(r["Z"]+0.1, bar.get_y()+bar.get_height()/2,
                f"{r['Z']:+.1f}", va="center", fontsize=8, color="#e6edf3")
    ax.legend(handles=[Patch(color="#58a6ff", label="Pure"),
                        Patch(color="#3fb950", label="Pair"),
                        Patch(color="#f0883e", label="Triple")],
              fontsize=8, facecolor="#21262d", edgecolor="#30363d", labelcolor="#e6edf3")
    ax.set_xlabel("Z-score")
    ax.set_title("Hybrid Arena — Top 20  (normalized vocab=200)")
    ax.invert_yaxis()

    fig.suptitle("Phaistos Disc — Master Analysis",
                 color="#e6edf3", fontsize=13, y=1.01)
    fig.tight_layout()
    fig.savefig("master_output.png", dpi=150, bbox_inches="tight",
                facecolor="#0d1117")
    print("\nSaved: master_output.png")
