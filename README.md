# Phaistos Disc — Statistical & Computational Analysis

**Author:** Manolis Chavadakis  
**Version:** 26.0 (June 2026)  
**License:** CC-BY 4.0  

## Overview

A rigorous computational framework for evaluating competing phonetic key hypotheses for the **Phaistos Disc** (~1700 BCE) — one of archaeology's most debated undeciphered objects.

This is a **methodology paper**, not a definitive decipherment. All findings are presented as exploratory hypotheses requiring independent replication.

## Key Findings

### Three Key-Independent Pillars (do not depend on any phonetic assumption)

All three computed from the **Evans/Godart canonical transcription** (45 signs, 241 tokens, 61 word-groups). Sign numbers below are Evans/Godart canonical — not Achterberg.

| Finding | Value | Significance |
|---------|-------|--------------|
| PLUMED HEAD(#02)→SHIELD(#12) bigram (canonical) | Z=+12.05, obs/exp=9.7× | p<0.0001, MC n=20,000; cannot be random |
| PLUMED HEAD(#02) word-initial in 19/19 occurrences (canonical) | Z=+7.51 | p<0.0001; consistent with determinative/article function |
| Seven exact word-group repetitions across 61 groups (canonical) | 24.6% refrain density | Z vs null=+45.60, p<0.0001; diagnostic of ritual texts |

### Phonetic Key Results (Bonferroni-corrected, 9 keys tested)

Scored on the **Achterberg phonetic transcription** (different sign numbering from Evans/Godart). Refrain labels use Achterberg values.

| Key | Score | Z | p-value | Bonferroni | Refrain (Achterberg) |
|-----|-------|---|---------|-----------|----------------------|
| G_LUWIAN (Luwian Hieroglyphic) ★ | 523 | 4.82 | <0.0001 | ✓✓✓ (pub.-grade) | za-wa-tar |
| E1_EGYPT (Egyptian TLA) | 491 | 4.40 | 0.0001 | ✓✓ | n-m-r |
| B_FREQ (Linear A frequency) | 430 | 3.61 | 0.0009 | ✓✓ | a-sa-ra |
| I_MORPHO (Linear A morphological) | 426 | 3.56 | 0.0009 | ✓✓ | a-ku-te |
| H_ABJAD (pure consonantal) | 0 | — | — | EXCLUDED | — |

**Bonferroni threshold:** Score > 379 (p < 0.005, corrected for 9 real keys; J_NULL is the reference null distribution, not a tested hypothesis)

### Pre-Registered Vocabulary Test (§6.12)

| Vocabulary | Size | Z | p-value | Bonferroni |
|------------|------|---|---------|-----------|
| Original ad hoc LUWIAN_VOCAB | 19 words | +8.95 | <0.000001 | PASS ✓ |
| Hawkins 2000 CHLI top-50 (pre-registered) | 52 words | **+11.18** | <0.000001 | PASS ✓✓ |

G_LUWIAN passes Bonferroni with a pre-registered vocabulary drawn from the standard Luwian Hieroglyphic reference corpus — addresses the C2 (vocabulary selection bias) critique.

### Primary Interpretation (G_LUWIAN)

Luwian Hieroglyphic reading (G_LUWIAN key on **Achterberg phonetic transcription**) produces a **solar-water cosmological hymn**:
- Refrain `za-wa-tar` = PIE *wódr̥ = "this water" (independently attested in Luwian)
- Center A31 (Achterberg): `ti-wa-za-wa-tar-ha` = "TIWAT! this water — yes!" (descent climax)
- Center B30 (Achterberg): `ti-wa-wa-tar-za-ha` = "TIWAT! water — this — YES!" (ascent climax)
- Side A = descent (Tiwat enters primordial waters)
- Side B = ascent (Tiwat reborn) — structural parallel to Egyptian Amduat (Ra+Osiris)

*Note: canonical Evans/Godart centers are A31=[10,3,38] and B30=[45,7]; Achterberg phonetic centers are A31=[45,2,36,11,22] and B30=[45,36,11,2,22]. These use different sign numbering.*

### Critical Self-Critique (v14.0)

**Negative control test (§6.1):** G_LUWIAN on synthetic disc (same frequencies, random adjacency) → Z=1.99 (not significant). Token score is ~94% frequency-driven. **Token score is withdrawn as primary argument.** All primary claims rest on the three key-independent pillars above (key-independent bigram, positional exclusivity, refrain density).

## Repository Structure

```
phaistos_master.py          — Main analysis: 9 keys, Bonferroni, Monte Carlo
phaistos_negative_control.py — Negative control self-test (frequency vs structure; token score withdrawn)
phaistos_corpus_control.py  — Domain control: theological Z=27 vs admin Z=-0.4
phaistos_sensitivity.py     — Perturbation analysis: 105/105 above Bonferroni
phaistos_headtohead.py      — Fair G_LUWIAN vs B_FREQ comparison
phaistos_holdout.py         — Cross-validation: Spearman ρ=0.779
phaistos_length_norm.py     — Length-normalized scoring (bias removal)
phaistos_token_scoring.py   — Sign-level token matching (substring bug fixed)
phaistos_egypt_v3.py        — AED-TEI corpus analysis (675,773 tokens)
phaistos_tla_corpus.py      — TLA corpus parser
phaistos_comprehensive_grid.py — 6-level evidence grid
phaistos_scoring_doc.py     — Formal mathematical scoring definition
phaistos_literature.py      — Literature synthesis + bibliography
phaistos_hawkins_vocab_test.py — Pre-registered Hawkins 2000 CHLI top-50 vocabulary test
phaistos_final_reading.py   — Complete disc reading

PHAISTOS_ΕΡΕΥΝΑ_ΠΛΗΡΗΣ.txt — Full research report v14.0 (Greek, 22 sections)
INDEPENDENT_REVIEW.txt      — Honest independent review of all weaknesses
OWENS_REFUTATION.txt        — Point-by-point refutation of Owens/photonet.gr

tla_corpus.json             — Parsed AED-TEI corpus data
ritual_ids.json             — Ritual text IDs from AED-TEI
.zenodo.json                — Zenodo metadata for DOI archiving
```

## Requirements

```bash
pip install numpy scipy pandas matplotlib
```

The AED-TEI corpus (`aed_tei_master.zip`, 167MB) is available at:  
https://github.com/simondschweitzer/aed-tei (CC-BY-SA 4.0)

## How to Run

```bash
# Main analysis (9 keys, Bonferroni, Monte Carlo)
python phaistos_master.py

# Critical self-test — negative control
python phaistos_negative_control.py

# Corpus domain control
python phaistos_corpus_control.py

# Fair head-to-head comparison
python phaistos_headtohead.py
```

## Citation

If you use this code or findings, please cite:

> Chavadakis, M. (2026). *Statistical Analysis of the Phaistos Disc: A Computational Methodology for Phonetic Key Evaluation*. Zenodo. https://doi.org/10.5281/zenodo.20517462

## Next Steps / Open Questions

1. **Independent replication** by a Luwianologist (SOAS, Oriental Institute Chicago)
2. **Blind replication:** provide disc statistics to Luwianologist without the key
3. **Hittite corpus comparison:** Boğazkoy ritual texts (EDITH/HETHITER.NET)
4. **Second text discovery:** any new Minoan inscription with shared signs

## License

Code: MIT  
Documents and findings: CC-BY 4.0  
AED-TEI corpus data: CC-BY-SA 4.0 (Akademie der Wissenschaften, Berlin)
