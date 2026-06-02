# Phaistos Disc — Statistical & Computational Analysis

**Author:** Manolis Chavadakis  
**Version:** 3.3 (June 2026)  
**License:** CC-BY 4.0  

## Overview

A rigorous computational framework for evaluating competing phonetic key hypotheses for the **Phaistos Disc** (~1700 BCE) — one of archaeology's most debated undeciphered objects.

This is a **methodology paper**, not a definitive decipherment. All findings are presented as exploratory hypotheses requiring independent replication.

## Key Findings

### Three Key-Independent Pillars (do not depend on any phonetic assumption)

| Finding | Value | Significance |
|---------|-------|--------------|
| [Sign#36→Sign#11] bigram adjacency | Z=10, obs/exp=7.69× | p≈0, cannot be random |
| Corpus-domain control (theological vs admin) | Z=27.16 vs Z=−0.40 | Ritual text, independently confirmed |
| Sign #45 (solar rosette) at centers A31+B30 ONLY | — | Geometric, key-free observation |

### Phonetic Key Results (Bonferroni-corrected, 10 keys tested)

| Key | Score | Z | p-value | Refrain |
|-----|-------|---|---------|---------|
| G_LUWIAN (Luwian Hieroglyphic) ★ | 523 | 4.82 | <0.0001 | za-wa-tar |
| E1_EGYPT (Egyptian TLA) | 491 | 4.40 | 0.0001 | n-m-r |
| B_FREQ (Linear A frequency) | 430 | 3.61 | 0.0009 | a-sa-ra |
| H_ABJAD (pure consonantal) | 0 | — | — | EXCLUDED |

**Bonferroni threshold:** Z > 2.807 (p < 0.005, corrected for 10 keys)

### Primary Interpretation (G_LUWIAN)

Luwian Hieroglyphic reading produces a **solar-water cosmological hymn**:
- Refrain `za-wa-tar` = PIE *wódr̥ = "this water" (independently attested)
- Center A31: `ti-wa-za-wa-tar-ha` = "TIWAT! this water — yes!" (descent climax)
- Center B30: `ti-wa-wa-tar-za-an` = "TIWAT! water-judge — here!" (ascent climax)
- Side A = descent (Tiwat enters primordial waters)
- Side B = ascent (Tiwat reborn) — parallel to Egyptian Amduat (Ra+Osiris)

### Critical Limitation (v3.3)

**Negative control test:** G_LUWIAN on synthetic disc (same frequencies, random adjacency) → Z=1.99 (not significant). Token score is ~94% frequency-driven. **Token score Z=8.58 is withdrawn as primary argument.** Only the three key-independent pillars are primary claims.

## Repository Structure

```
phaistos_master.py          — Main analysis: 10 keys, Bonferroni, Monte Carlo
phaistos_negative_control.py — Critical v3.3 self-test (frequency vs structure)
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
phaistos_final_reading.py   — Complete disc reading

PHAISTOS_ΕΡΕΥΝΑ_ΠΛΗΡΗΣ.txt — Full research report v3.3 (Greek, 22 sections)
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
# Main analysis (10 keys, Bonferroni, Monte Carlo)
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

> Chavadakis, M. (2026). *Statistical Analysis of the Phaistos Disc: A Computational Methodology for Phonetic Key Evaluation*. Zenodo. https://doi.org/[DOI_PENDING]

## Next Steps / Open Questions

1. **Independent replication** by a Luwianologist (SOAS, Oriental Institute Chicago)
2. **Blind replication:** provide disc statistics to Luwianologist without the key
3. **Hittite corpus comparison:** Boğazkoy ritual texts (EDITH/HETHITER.NET)
4. **Second text discovery:** any new Minoan inscription with shared signs

## License

Code: MIT  
Documents and findings: CC-BY 4.0  
AED-TEI corpus data: CC-BY-SA 4.0 (Akademie der Wissenschaften, Berlin)
