#!/usr/bin/env python3
"""
ANCHORED FULL ASSIGNMENT — 7-Judge Tied Theory Builder
=======================================================
Attempts to assign phonetic values to all 45 disc signs using:
  - 11 anchor assignments (G_LUWIAN + sign #46)
  - 7 independent judges scoring each candidate value
  - Corpus statistics from TLHdig water-ritual contexts
  - Luwian phonotactic constraints

OUTPUT:
  - Complete 61-word-group reading with confidence tiers
  - 7-judge scorecard per sign
  - Failure map: what cannot be assigned and why
  - Coherence score for the full theory

USAGE: python phaistos_tied_theory.py
"""

import json, os, re, math
from collections import Counter, defaultdict

DISC_JSON = r"hp4k1h5_phaistos_disc\src\phaistos_disc\data\phaistos-disc_outside-in.json"

# ─────────────────────────────────────────────────────────────────────────────
# ANCHOR ASSIGNMENTS (confirmed / strongly supported)
# Sign numbers = Achterberg (= numbers in the disc JSON)
# ─────────────────────────────────────────────────────────────────────────────

ANCHORS = {
    "36": ("wa",    "STRONG",  "G_LUWIAN — blind corpus p<0.000005, ablation robust"),
    "11": ("tar",   "STRONG",  "G_LUWIAN — za-wa-tar triple confirmed"),
    "02": ("za",    "STRONG",  "G_LUWIAN — za demonstrative Z=+3.59, TLHdig phrase-initial"),
    "22": ("ha",    "STRONG",  "G_LUWIAN — affirm particle, TLHdig attested"),
    "07": ("ti",    "STRONG",  "G_LUWIAN — copula/Tiwat, grammatical Z=+3.17"),
    "29": ("na",    "MEDIUM",  "G_LUWIAN revised — connective biclitic Z=+3.26"),
    "06": ("an",    "MEDIUM",  "G_LUWIAN — conjunction"),
    "12": ("zi",    "MEDIUM",  "G_LUWIAN — particle"),
    "45": ("ti-wa", "STRONG",  "G_LUWIAN — Tiwat rosette, center A31+B30"),
    "01": ("i",     "MEDIUM",  "G_LUWIAN — connective vowel"),
    "46": ("[HA]",  "STRONG",  "T-B: Z=+7.64, p=2e-14 — 100% word-final, terminal particle"),
}

# ─────────────────────────────────────────────────────────────────────────────
# CANDIDATE POOL: Luwian/Hittite syllables attested in water-ritual corpus
# Source: TLHdig CTH 325/444/459/470/694 water-formula context analysis
# Format: syllable → (frequency_rank, semantic_domain, phonotactic_class)
# ─────────────────────────────────────────────────────────────────────────────

LUWIAN_SYLLABLES = {
    # Water/purity domain (CTH 325, 444, 459, 470)
    "ku":   (1,  "PURITY",    "CV",  "parkui=pure — primary sign #8 candidate"),
    "pu":   (2,  "PURITY",    "CV",  "parkui alt. syllable"),
    "pa":   (3,  "PURITY",    "CV",  "parkuwan- stem variant"),
    "pi":   (4,  "PURITY",    "CV",  "parkui allomorph"),
    # Flowing/water domain
    "he":   (5,  "WATER",     "CV",  "waHEšnant- = flowing"),
    "hu":   (6,  "WATER",     "CV",  "ḫuiya- = life/living (water)"),
    "ha":   (7,  "WATER",     "CV",  "ḫani = draws water — NB: 'ha' taken by anchor #22"),
    # Sun/divine domain
    "tI":   (8,  "SOLAR",     "CV",  "tiwat variant — dist. from anchor ti=#7"),
    "sa":   (9,  "RITUAL",    "CV",  "šarri- = king; šaššu- = queen"),
    "ma":   (10, "RITUAL",    "CV",  "mālia- = grace, favor; also maliaš"),
    "mi":   (11, "RITUAL",    "CV",  "common Luwian syllable"),
    "tu":   (12, "RITUAL",    "CV",  "tuwali- = only, alone"),
    "ta":   (13, "RITUAL",    "CV",  "common; tata- = father"),
    "ri":   (14, "RITUAL",    "CV",  "common suffix/root"),
    "ra":   (15, "RITUAL",    "CV",  "common; rama- = free"),
    "la":   (16, "RITUAL",    "CV",  "lala- = tongue/word"),
    "li":   (17, "RITUAL",    "CV",  "lili- = common"),
    "lu":   (18, "RITUAL",    "CV",  "lu- = or; luwi- = Luwian ethnic"),
    "nu":   (19, "CONNECTIVE","CV",  "nu = and/then — most common Hittite connective"),
    "ni":   (20, "CONNECTIVE","CV",  "ni- connective"),
    "su":   (21, "RITUAL",    "CV",  "šuna- = to fill"),
    "si":   (22, "RITUAL",    "CV",  "šiya- = to seal/stamp"),
    "ka":   (23, "RITUAL",    "CV",  "ka- demonstrative stem"),
    "ki":   (24, "RITUAL",    "CV",  "kī = this (neuter)"),
    "ya":   (25, "LOCATIVE",  "CV",  "ḫaniyaš locative -ya — sign #8 candidate"),
    "mu":   (26, "RITUAL",    "CV",  "mu- pronoun"),
    "pe":   (27, "RITUAL",    "CV",  "pēda- = place"),
    "ne":   (28, "CONNECTIVE","CV",  "connective"),
    "re":   (29, "RITUAL",    "CV",  "rē- stem"),
    "te":   (30, "RITUAL",    "CV",  "tē- = say"),
    "ke":   (31, "RITUAL",    "CV",  "kē- = this"),
    "le":   (32, "RITUAL",    "CV",  "lē = not (prohibitive)"),
    "pal":  (33, "OBJECT",    "CVC", "palhi- = broad/flat (MATTOCK acrophony, confirmed)"),
    "tar":  (34, "WATER",     "CVC", "NB: already anchor #11"),
    "kar":  (35, "RITUAL",    "CVC", "karu- = formerly"),
    "wal":  (36, "RITUAL",    "CVC", "walḫ- = to strike"),
    "sar":  (37, "RITUAL",    "CVC", "šar- = over, above"),
    "tal":  (38, "RITUAL",    "CVC", "tali- = "),
    "par":  (39, "RITUAL",    "CVC", "par- = to drive out"),
    "ḫa":   (40, "EMPHATIC",  "CV",  "ḫa- emphatic particle (alt. to ha=#22)"),
}

# Exclude anchors from candidate pool
ANCHOR_SYLLABLES = {v[0] for v in ANCHORS.values()}
CANDIDATES = {k: v for k, v in LUWIAN_SYLLABLES.items()
              if k not in ANCHOR_SYLLABLES}

# ─────────────────────────────────────────────────────────────────────────────
# POSITIONAL STATISTICS FROM TLHdig WATER-RITUAL CONTEXTS
# (pre-computed from phaistos_sign8.py and TLHdig searches)
# ─────────────────────────────────────────────────────────────────────────────

# Syllables attested in word-FINAL position in water-ritual lines
RITUAL_WORD_FINAL = {
    "parkui", "laḫuai", "laḫui", "ḫani", "memai", "akuanzi", "pianzi",
    "papparašzi", "ḫarzi", "laḫuanzi", "petanzi", "utanzi",
}

# Syllables attested directly AFTER watar in CTH water formulas
POST_WATER_TOKENS = {
    "parkui": 3, "ḫani": 9, "pianzi": 20, "akuanzi": 9,
    "laḫuai": 8, "ḫarzi": 8, "para": 13, "kuit": 6,
}

# Attested word-INITIAL syllables in Luwian ritual texts
LUWIAN_WORD_INITIAL = {
    "za", "na", "ti", "wa", "ha", "nu", "ku", "pa", "ma", "ta", "ka",
    "sa", "tu", "la", "li", "an", "si", "pi", "ra", "pe",
}

# ─────────────────────────────────────────────────────────────────────────────
# SIGN METADATA (Evans/Godart names where known)
# ─────────────────────────────────────────────────────────────────────────────

SIGN_NAMES = {
    "02": "PLUMED-HEAD", "12": "SHIELD",    "07": "FOOT",
    "27": "EAGLE",       "29": "TROWEL",    "45": "ROSETTE",
    "46": "UNK-46",      "01": "PEDESTRIAN","22": "HELMET",
    "35": "DOVE",        "36": "BATON",     "08": "GAUNTLET",
    "11": "COMB",        "02": "PLUMED-HEAD","25": "SHIP",
    "15": "MATTOCK",     "13": "CLUB",      "10": "ARROW",
    "03": "TATTOOED-HEAD","38": "ROSETTE-2",
}

# ─────────────────────────────────────────────────────────────────────────────
# 7 JUDGES
# ─────────────────────────────────────────────────────────────────────────────

def judge_statistical(sign, candidate, disc_stats):
    """
    J1: Is the candidate consistent with the sign's positional statistics?
    Checks: word-initial rate, word-final rate vs. known Luwian patterns.
    """
    score = 0.0
    notes = []
    wf_rate = disc_stats[sign]["wf_rate"]
    wi_rate = disc_stats[sign]["wi_rate"]

    # High word-final → prefer suffixes/particles
    if wf_rate > 0.6:
        if candidate in {"ku","pa","pu","ya","ma","ha","ta","ra","la"}:
            score += 2.0; notes.append("wf-compatible")
    # High word-initial → prefer demonstratives/conjunctions
    if wi_rate > 0.5:
        if candidate in LUWIAN_WORD_INITIAL:
            score += 2.0; notes.append("wi-compatible")
        else:
            score -= 1.0; notes.append("wi-violation")
    # Post-water context bonus
    if disc_stats[sign].get("post_water", False):
        if candidate in POST_WATER_TOKENS:
            score += 3.0; notes.append("post-water attested")
    # Baseline: common syllable bonus
    syl_info = CANDIDATES.get(candidate)
    if syl_info:
        rank = syl_info[0]
        score += max(0, (40 - rank) / 20)  # higher rank → higher score
    return score, "; ".join(notes) if notes else "baseline"

def judge_linguistic(sign, candidate, disc_stats, context_signs):
    """
    J2: Is the candidate phonotactically valid in Luwian?
    Checks CV structure, morpheme plausibility, neighbor compatibility.
    """
    score = 0.0
    notes = []
    syl_info = CANDIDATES.get(candidate)
    if not syl_info:
        return 0, "not in pool"

    # CV syllables preferred in Luwian core vocabulary
    if syl_info[2] == "CV":
        score += 1.5; notes.append("CV-canonical")
    else:
        score += 0.5; notes.append("CVC-marginal")

    # Check neighbor compatibility with anchors
    prev_anchor = None
    next_anchor = None
    for i, s in enumerate(context_signs):
        if s == sign:
            if i > 0 and context_signs[i-1] in ANCHORS:
                prev_anchor = ANCHORS[context_signs[i-1]][0]
            if i < len(context_signs)-1 and context_signs[i+1] in ANCHORS:
                next_anchor = ANCHORS[context_signs[i+1]][0]

    # Common valid Luwian bigrams
    valid_bigrams = {
        ("wa", "ku"), ("wa", "ti"), ("na", "wa"), ("za", "wa"),
        ("ha", "na"), ("ti", "ku"), ("ti", "ya"), ("ku", "ha"),
        ("na", "ku"), ("za", "ti"), ("ma", "na"), ("pa", "ku"),
    }
    if prev_anchor and (prev_anchor, candidate) in valid_bigrams:
        score += 2.0; notes.append(f"valid bigram {prev_anchor}-{candidate}")
    if next_anchor and (candidate, next_anchor) in valid_bigrams:
        score += 2.0; notes.append(f"valid bigram {candidate}-{next_anchor}")

    return score, "; ".join(notes) if notes else "phonotactically neutral"

def judge_archaeological(sign, candidate, disc_stats):
    """
    J3: Is the candidate semantically compatible with a water-oath ritual
    from Kizzuwatna ~1700 BCE?
    Uses the CTH 325/444/470/694 semantic domain classifications.
    """
    score = 0.0
    notes = []
    syl_info = CANDIDATES.get(candidate)
    if not syl_info:
        return 0, "not in pool"

    domain = syl_info[1]
    if domain == "PURITY":
        score += 3.0; notes.append("purity domain — CTH 325/444")
    elif domain == "WATER":
        score += 2.5; notes.append("water domain")
    elif domain == "SOLAR":
        score += 2.0; notes.append("solar domain")
    elif domain == "RITUAL":
        score += 1.5; notes.append("ritual compatible")
    elif domain == "CONNECTIVE":
        score += 1.0; notes.append("grammatical — domain-neutral")
    elif domain == "LOCATIVE":
        score += 2.0; notes.append("locative — Karatepe parallel")

    # Bonus: sign #8 (GAUNTLET) in predicate slot → purity/locative preferred
    if sign == "08":
        if domain in {"PURITY", "LOCATIVE", "WATER"}:
            score += 2.0; notes.append("sign #8 predicate-slot bonus")

    return score, "; ".join(notes) if notes else "no domain match"

def judge_comparative(sign, candidate, current_assignment, all_groups):
    """
    J4: Does this assignment increase bigram overlap with attested Luwian?
    Checks if sign's syllable appears in known Luwian ritual bigrams.
    """
    score = 0.0
    notes = []

    # Full assignment (anchors + current candidate)
    test_key = dict(ANCHORS)
    for s, (val, _, _) in ANCHORS.items():
        test_key[s] = val
    test_key[sign] = candidate
    for s, val in current_assignment.items():
        test_key[s] = val

    # Count how many word-groups become "more readable" with this assignment
    readable_gain = 0
    for wg in all_groups:
        assigned = [test_key.get(s, None) for s in wg if s != "??"]
        if all(v is not None for v in assigned):
            readable_gain += 1

    score += readable_gain * 0.1
    if readable_gain > 0:
        notes.append(f"+{readable_gain} fully-readable groups")

    # Known Luwian trigrams — bonus if candidate completes one
    luwian_trigrams = [
        ["za", "wa", "tar"], ["ha", "na", "wa"], ["na", "wa", "ti"],
        ["ti", "wa", "za"], ["wa", "tar", "za"], ["za", "ti", "wa"],
        ["na", "ti", "[HA]"], ["wa", "ti", "ku"],
    ]
    for wg in all_groups:
        vals = [test_key.get(s, None) for s in wg]
        for i in range(len(vals)-2):
            tri = vals[i:i+3]
            if tri in luwian_trigrams and candidate in tri:
                score += 1.5; notes.append(f"completes trigram {tri}")
                break

    return score, "; ".join(notes) if notes else "no notable gain"

def judge_falsification(sign, candidate, current_assignment):
    """
    J5: Does this assignment create any contradiction?
    Instantly zeros score if: duplicate value, phonotactic impossibility,
    or contradiction with anchor.
    """
    # Check duplicate
    all_values = {v[0] for s, v in ANCHORS.items() if s != sign}
    all_values.update(current_assignment.values())
    if candidate in all_values:
        return -999, f"DUPLICATE: '{candidate}' already assigned"

    # Check phonotactic impossibility (placeholder — no impossible CV in Luwian)
    if len(candidate) > 4:
        return -5, "overlong — unlikely Luwian syllable"

    # Check: don't assign 'ha' (already anchor #22) or 'ti' (anchor #7)
    if candidate in ANCHOR_SYLLABLES:
        return -999, f"DUPLICATE of anchor: '{candidate}'"

    return 1.0, "no contradiction"

def judge_mdl(sign, candidate, disc_stats):
    """
    J6: MDL/Compression — prefers assignments that reduce description length.
    Shorter, more common syllables are preferred (Occam's razor).
    Higher frequency in Luwian → lower description cost.
    """
    score = 0.0
    notes = []
    syl_info = CANDIDATES.get(candidate)
    if not syl_info:
        return 0, "not in pool"

    rank = syl_info[0]
    # Prefer lower rank (= more common)
    score += max(0, (40 - rank) / 10)
    notes.append(f"rank={rank}")

    # CV preferred over CVC (shorter description)
    if syl_info[2] == "CV":
        score += 1.0; notes.append("CV=shorter")
    else:
        score -= 0.5; notes.append("CVC=longer")

    # Frequency: how often does this sign appear? More frequent = higher compression gain
    freq = disc_stats[sign]["total"]
    score += min(3.0, freq * 0.3)
    notes.append(f"freq={freq}")

    return score, "; ".join(notes)

def judge_information_gain(sign, candidate, current_assignment, all_groups):
    """
    J7: Information Gain — does this assignment enable new predictions?
    Rewards: completing previously unreadable word-groups,
    enabling new Luwian morpheme identifications,
    reducing entropy of neighboring unassigned signs.
    """
    score = 0.0
    notes = []

    # How many word-groups become NEWLY fully readable?
    test_key = {}
    for s, (val, _, _) in ANCHORS.items():
        test_key[s] = val
    for s, val in current_assignment.items():
        test_key[s] = val

    before_readable = sum(
        1 for wg in all_groups
        if all(test_key.get(s) is not None for s in wg if s != "??")
    )
    test_key[sign] = candidate
    after_readable = sum(
        1 for wg in all_groups
        if all(test_key.get(s) is not None for s in wg if s != "??")
    )

    new_readable = after_readable - before_readable
    if new_readable > 0:
        score += new_readable * 2.0
        notes.append(f"unlocks {new_readable} new word-groups")

    # Does this assignment enable a known Luwian word to be read?
    known_luwian_words = [
        ["wa", "tar"], ["za", "wa", "tar"], ["ha", "na", "wa"],
        ["ti", "wa"], ["na", "wa"], ["ku", "[HA]"], ["pa", "ku"],
        ["ma", "na"], ["ta", "na"], ["za", "ti"],
    ]
    for wg in all_groups:
        vals = [test_key.get(s, "?") for s in wg if s != "??"]
        for word in known_luwian_words:
            # Check if word is a subsequence
            w_len = len(word)
            for i in range(len(vals) - w_len + 1):
                if vals[i:i+w_len] == word and candidate in word:
                    score += 1.0; notes.append(f"enables '{'-'.join(word)}'")

    return score, "; ".join(notes) if notes else "marginal gain"

# ─────────────────────────────────────────────────────────────────────────────
# COMPUTE DISC STATISTICS
# ─────────────────────────────────────────────────────────────────────────────

def compute_disc_stats(disc):
    all_groups = disc["side_a"] + disc["side_b"]
    stats = defaultdict(lambda: {
        "total": 0, "word_initial": 0, "word_final": 0,
        "word_medial": 0, "wi_rate": 0.0, "wf_rate": 0.0,
        "post_water": False
    })

    water_signs = {"36", "11"}  # wa, tar in G_LUWIAN

    for wg in all_groups:
        clean = [s for s in wg if s != "??"]
        for i, s in enumerate(clean):
            stats[s]["total"] += 1
            if i == 0:
                stats[s]["word_initial"] += 1
            elif i == len(clean) - 1:
                stats[s]["word_final"] += 1
            else:
                stats[s]["word_medial"] += 1
            # Check if sign follows water signs
            if i > 0 and clean[i-1] in water_signs:
                stats[s]["post_water"] = True

    for s in stats:
        t = stats[s]["total"]
        if t > 0:
            stats[s]["wi_rate"] = stats[s]["word_initial"] / t
            stats[s]["wf_rate"] = stats[s]["word_final"] / t
    return stats

# ─────────────────────────────────────────────────────────────────────────────
# MAIN ASSIGNMENT ENGINE
# ─────────────────────────────────────────────────────────────────────────────

def score_candidate(sign, candidate, disc_stats, current_assignment, all_groups):
    context_signs = [s for wg in all_groups for s in wg if s != "??"]

    scores = {}
    notes  = {}

    s, n = judge_statistical(sign, candidate, disc_stats)
    scores["J1_Statistical"] = s; notes["J1"] = n

    s, n = judge_linguistic(sign, candidate, disc_stats, context_signs)
    scores["J2_Linguistic"] = s; notes["J2"] = n

    s, n = judge_archaeological(sign, candidate, disc_stats)
    scores["J3_Archaeological"] = s; notes["J3"] = n

    s, n = judge_comparative(sign, candidate, current_assignment, all_groups)
    scores["J4_Comparative"] = s; notes["J4"] = n

    s, n = judge_falsification(sign, candidate, current_assignment)
    scores["J5_Falsification"] = s; notes["J5"] = n

    s, n = judge_mdl(sign, candidate, disc_stats)
    scores["J6_MDL"] = s; notes["J6"] = n

    s, n = judge_information_gain(sign, candidate, current_assignment, all_groups)
    scores["J7_InfoGain"] = s; notes["J7"] = n

    # Falsification veto
    if scores["J5_Falsification"] < -100:
        return -999, scores, notes

    total = sum(scores.values())
    return total, scores, notes

def assign_all_signs(disc):
    all_groups = disc["side_a"] + disc["side_b"]
    disc_stats = compute_disc_stats(disc)

    # All signs present in disc
    all_signs = sorted(set(
        s for wg in all_groups for s in wg if s != "??"
    ), key=lambda x: -disc_stats[x]["total"])

    # Start with anchors
    assignment = {}  # sign → phonetic value
    for s, (val, tier, _) in ANCHORS.items():
        assignment[s] = val

    unassigned = [s for s in all_signs if s not in assignment]

    results = {}  # sign → {value, total_score, tier, judge_scores, notes, runner_up}

    # Register anchors
    for s, (val, tier, reason) in ANCHORS.items():
        results[s] = {
            "value": val, "tier": tier,
            "score": 999, "reason": reason,
            "judge_scores": {}, "notes": {},
            "runner_up": None, "runner_up_score": None,
            "constraint": "ANCHOR"
        }

    print(f"\n  Scoring {len(unassigned)} unassigned signs against "
          f"{len(CANDIDATES)} candidates...")

    for sign in unassigned:
        best_val   = None
        best_score = -999
        best_judges = {}
        best_notes  = {}
        runner_up   = None
        runner_up_s = -999

        freq = disc_stats[sign]["total"]

        for candidate in sorted(CANDIDATES.keys()):
            total, judge_scores, notes = score_candidate(
                sign, candidate, disc_stats, assignment, all_groups
            )
            if total > best_score:
                runner_up   = best_val
                runner_up_s = best_score
                best_score  = total
                best_val    = candidate
                best_judges = judge_scores
                best_notes  = notes
            elif total > runner_up_s and total != best_score:
                runner_up   = candidate
                runner_up_s = total

        # Determine confidence tier
        gap = best_score - runner_up_s if runner_up_s > -999 else best_score
        if best_score <= 0:
            tier = "UNCONSTRAINED"
        elif gap >= 4.0 and best_score >= 8.0 and freq >= 3:
            tier = "TIER-1"
        elif gap >= 2.0 and best_score >= 5.0:
            tier = "TIER-2"
        elif freq <= 1:
            tier = "HAPAX"
        else:
            tier = "WEAK"

        results[sign] = {
            "value": best_val if tier not in {"UNCONSTRAINED", "HAPAX"} else "?",
            "tier": tier,
            "score": best_score,
            "gap": gap,
            "freq": freq,
            "judge_scores": best_judges,
            "notes": best_notes,
            "runner_up": runner_up,
            "runner_up_score": runner_up_s,
            "constraint": "ASSIGNED"
        }

        # Add to assignment if confident enough
        if tier in {"TIER-1", "TIER-2"}:
            assignment[sign] = best_val

    return results, assignment, all_groups, disc_stats

# ─────────────────────────────────────────────────────────────────────────────
# GENERATE COMPLETE READING
# ─────────────────────────────────────────────────────────────────────────────

def generate_reading(disc, assignment, results):
    side_a = disc["side_a"]
    side_b = disc["side_b"]

    def read_group(wg, idx, side):
        phonetic = []
        all_assigned = True
        tiers = []
        for s in wg:
            if s == "??":
                phonetic.append("[??]"); all_assigned = False; tiers.append("?")
                continue
            if s in assignment:
                val = assignment[s]
                t = results[s]["tier"]
                phonetic.append(val)
                tiers.append(t)
            else:
                phonetic.append(f"[#{s}]")
                all_assigned = False
                tiers.append("?")

        reading = "-".join(phonetic)
        worst_tier = "UNCONSTRAINED" if "?" in tiers else \
                     "HAPAX" if "HAPAX" in tiers else \
                     "WEAK" if "WEAK" in tiers else \
                     "TIER-2" if "TIER-2" in tiers else \
                     "TIER-1" if all(t in {"TIER-1","MEDIUM","STRONG"} for t in tiers) else \
                     "MIXED"
        return reading, worst_tier

    lines = []
    lines.append("\n  SIDE A — outside → center")
    lines.append(f"  {'#':<5} {'Reading':<35} {'Confidence'}")
    lines.append(f"  {'-'*55}")
    for i, wg in enumerate(side_a):
        reading, tier = read_group(wg, i, "A")
        marker = "◄ CENTER" if i == len(side_a)-1 else ""
        icon = "✅" if tier in {"TIER-1","STRONG","MEDIUM"} else \
               "⚠" if tier in {"TIER-2","MIXED"} else \
               "❓" if tier in {"UNCONSTRAINED","HAPAX","WEAK"} else "~"
        lines.append(f"  A{i+1:02d}  {reading:<35} {icon} {tier} {marker}")

    lines.append("\n  SIDE B — center → outside")
    lines.append(f"  {'#':<5} {'Reading':<35} {'Confidence'}")
    lines.append(f"  {'-'*55}")
    for i, wg in enumerate(side_b):
        reading, tier = read_group(wg, i, "B")
        marker = "◄ CENTER" if i == 0 else \
                 "◄ OUTER" if i == len(side_b)-1 else ""
        icon = "✅" if tier in {"TIER-1","STRONG","MEDIUM"} else \
               "⚠" if tier in {"TIER-2","MIXED"} else \
               "❓" if tier in {"UNCONSTRAINED","HAPAX","WEAK"} else "~"
        lines.append(f"  B{i+1:02d}  {reading:<35} {icon} {tier} {marker}")

    return "\n".join(lines)

# ─────────────────────────────────────────────────────────────────────────────
# COHERENCE SCORE + SUMMARY
# ─────────────────────────────────────────────────────────────────────────────

def compute_coherence(results, assignment, all_groups):
    total_signs = len(results)
    anchors     = sum(1 for r in results.values() if r["constraint"] == "ANCHOR")
    tier1       = sum(1 for r in results.values() if r["tier"] == "TIER-1")
    tier2       = sum(1 for r in results.values() if r["tier"] == "TIER-2")
    weak        = sum(1 for r in results.values() if r["tier"] == "WEAK")
    hapax       = sum(1 for r in results.values() if r["tier"] == "HAPAX")
    unconstrained = sum(1 for r in results.values()
                        if r["tier"] in {"UNCONSTRAINED", "WEAK", "HAPAX"})

    assigned_total = anchors + tier1 + tier2

    # % of token positions readable
    total_tokens = sum(len([s for s in wg if s != "??"]) for wg in all_groups)
    readable_tokens = sum(
        1 for wg in all_groups
        for s in wg
        if s != "??" and s in assignment
    )

    # % of word-groups fully readable
    fully_readable = sum(
        1 for wg in all_groups
        if all(s == "??" or s in assignment for s in wg)
    )
    total_groups = len(all_groups)

    coherence = (assigned_total / total_signs) * 100

    return {
        "total_signs": total_signs,
        "anchors": anchors,
        "tier1": tier1,
        "tier2": tier2,
        "weak": weak,
        "hapax": hapax,
        "unconstrained": unconstrained,
        "assigned_total": assigned_total,
        "coherence_pct": coherence,
        "token_coverage": readable_tokens / total_tokens * 100,
        "group_coverage": fully_readable / total_groups * 100,
        "fully_readable": fully_readable,
        "total_groups": total_groups,
    }

# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import time
    t0 = time.time()

    print("╔" + "═"*70 + "╗")
    print("║  ANCHORED FULL ASSIGNMENT — 7-Judge Tied Theory Builder" + " "*14 + "║")
    print("║  Phaistos Disc v24.0" + " "*49 + "║")
    print("╚" + "═"*70 + "╝")

    with open(DISC_JSON, encoding="utf-8") as f:
        disc = json.load(f)

    results, assignment, all_groups, disc_stats = assign_all_signs(disc)

    # ── Sign-by-sign report ───────────────────────────────────────────────────
    print("\n" + "═"*72)
    print("  SIGN ASSIGNMENT REPORT")
    print("═"*72)
    print(f"  {'Sign':<6} {'Name':<16} {'Freq':>5} {'Value':<10} "
          f"{'Tier':<14} {'Score':>6} {'Gap':>6} {'Runner-up':<10}")
    print(f"  {'-'*80}")

    tier_order = {"STRONG":0,"MEDIUM":1,"TIER-1":2,"TIER-2":3,
                  "WEAK":4,"HAPAX":5,"UNCONSTRAINED":6}
    sorted_signs = sorted(results.keys(),
                          key=lambda s: (tier_order.get(results[s]["tier"],9),
                                         -disc_stats[s]["total"]))

    for sign in sorted_signs:
        r = results[sign]
        freq   = disc_stats[sign]["total"]
        val    = r["value"]
        tier   = r["tier"]
        score  = r.get("score", 0)
        gap    = r.get("gap", 0)
        name   = SIGN_NAMES.get(sign, f"sign-{sign}")
        ru     = r.get("runner_up") or "-"
        icon   = "✅" if tier in {"STRONG","MEDIUM","TIER-1"} else \
                 "⚠" if tier == "TIER-2" else \
                 "❓" if tier in {"UNCONSTRAINED","WEAK","HAPAX"} else "~"
        print(f"  {icon}{sign:<5} {name:<16} {freq:>5} {str(val):<10} "
              f"{tier:<14} {score:>6.1f} {gap:>6.1f} {ru:<10}")

    # ── 7-judge detail for key unassigned signs ───────────────────────────────
    print("\n" + "═"*72)
    print("  7-JUDGE DETAIL — Key unassigned signs")
    print("═"*72)
    for sign in sorted_signs:
        r = results[sign]
        if r["tier"] not in {"TIER-1","TIER-2"} and r["constraint"] != "ANCHOR":
            if disc_stats[sign]["total"] >= 3:
                print(f"\n  Sign #{sign} ({SIGN_NAMES.get(sign,'?')})"
                      f"  freq={disc_stats[sign]['total']}  best='{r['value']}'  "
                      f"score={r.get('score',0):.1f}  gap={r.get('gap',0):.1f}")
                for jname, jscore in r.get("judge_scores",{}).items():
                    note = r.get("notes",{}).get(jname.split("_")[0],"")
                    print(f"    {jname:<25} {jscore:>+6.1f}  {note}")

    # ── Complete reading ──────────────────────────────────────────────────────
    print("\n" + "═"*72)
    print("  COMPLETE READING (61 word-groups)")
    print("═"*72)
    reading_text = generate_reading(disc, assignment, results)
    print(reading_text)

    # ── Coherence score ───────────────────────────────────────────────────────
    coh = compute_coherence(results, assignment, all_groups)
    print("\n" + "═"*72)
    print("  COHERENCE SCORE — TIED THEORY STATUS")
    print("═"*72)
    print(f"\n  Total unique signs:        {coh['total_signs']}")
    print(f"  Anchor assignments:        {coh['anchors']}  (G_LUWIAN + sign #46)")
    print(f"  Tier-1 new assignments:    {coh['tier1']}  (high confidence)")
    print(f"  Tier-2 new assignments:    {coh['tier2']}  (medium confidence)")
    print(f"  Weak / ambiguous:          {coh['weak']}")
    print(f"  Hapax (1× — unconstrained):{coh['hapax']}")
    print(f"  Unconstrained:             {coh['unconstrained']}")
    print()
    print(f"  Sign coverage:             {coh['assigned_total']}/{coh['total_signs']} "
          f"= {coh['coherence_pct']:.1f}%")
    print(f"  Token coverage:            {coh['token_coverage']:.1f}% "
          f"of 259 disc tokens readable")
    print(f"  Group coverage:            {coh['fully_readable']}/{coh['total_groups']} "
          f"word-groups fully readable ({coh['group_coverage']:.1f}%)")

    print()
    if coh["coherence_pct"] >= 70 and coh["group_coverage"] >= 60:
        verdict = "✅ TIED THEORY VIABLE — sufficient coverage for publication claim"
    elif coh["coherence_pct"] >= 50 and coh["group_coverage"] >= 40:
        verdict = "⚠  PARTIAL THEORY — strong core, significant gaps remain"
    else:
        verdict = "❌ INSUFFICIENT COVERAGE — theory needs more anchors"

    print(f"  VERDICT: {verdict}")

    # ── Failure map ───────────────────────────────────────────────────────────
    print("\n" + "═"*72)
    print("  FAILURE MAP — What cannot be assigned and why")
    print("═"*72)
    for sign in sorted_signs:
        r = results[sign]
        if r["tier"] in {"UNCONSTRAINED","HAPAX"} and r["constraint"] != "ANCHOR":
            freq = disc_stats[sign]["total"]
            print(f"  Sign #{sign} ({SIGN_NAMES.get(sign,'?')}) — "
                  f"freq={freq}  best_score={r.get('score',0):.1f}")
            if freq == 1:
                print(f"    Reason: HAPAX — single occurrence, insufficient context")
            elif r.get("score",0) <= 0:
                print(f"    Reason: All candidates score ≤0 — no discriminating feature")
            else:
                print(f"    Reason: Low confidence (gap={r.get('gap',0):.1f} < threshold)")
                if r.get("runner_up"):
                    print(f"    Top candidates: {r['value']} vs {r['runner_up']} "
                          f"(score diff = {r.get('gap',0):.1f})")

    print(f"\n  Elapsed: {time.time()-t0:.1f}s")
    print("═"*72)
