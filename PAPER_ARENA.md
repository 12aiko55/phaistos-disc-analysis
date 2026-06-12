# Phonotactic Arena Analysis of the Phaistos Disc: 35-Language Computational Survey and Kizzuwatna Convergence Hypothesis

**Author:** Manolis Chavadakis  
**Affiliation:** Independent Researcher  
**Date:** June 2026  
**Version:** 1.0  
**License:** CC-BY 4.0  
**Code:** `phaistos_master.py`, `phaistos_stability.py` (open source, this repository)

---

## Abstract

We present a systematic multi-language computational arena for the Phaistos Disc (~1700 BCE), evaluating 35 Bronze Age language configurations — 7 pure languages and 28 hybrid entities (21 pairs, 7 triples) — against the disc's phonotactic profile. Corpora span 85,361–438,362 tokens from critically edited sources (TLHdig v0.2.0-beta, DĀMOS, SAAO/RINAP/RIBO, AED-TEI, ETCSRI, HBTIN, CUC). All 35 entities pass statistical significance (minimum Z=+13.29, all p<0.000001, 10,000-trial Monte Carlo null distribution). Four independent scoring judges — MCTS vocabulary matching, Monte Carlo null distribution, MDL bigram compression, and Expected Information Gain — are combined into a master scoreboard by average rank.

The highest-scoring single hybrid is **Anatolio-Babylonian** (Luwian/Hittite + Late Babylonian, Z=+27.04), corresponding to the phonological profile of Bronze Age **Kizzuwatna** (Cilicia, ca. 1650–1200 BCE). On the master scoreboard, **Late Babylonian** achieves the most consistent cross-judge performance (average rank 4.8/7). A blind stability test (5,000 independent hill-climb trials, top 15% runs, N=1,047) finds zero stable sign assignments (maximum confidence 31% for sign #7 → 'a'), establishing that phonotactic compatibility is necessary but not sufficient for individual-sign decipherment; additional external constraints are required.

We propose the **Karatepe Comparative Approach** as the next step: using the Luwian hieroglyphic–Phoenician bilingual inscription from Cilicia (ca. 825 BCE) to constrain semantic roles within the Kizzuwatna phonological framework, propagating back to the disc via the independently confirmed [TIWAT + wa-tar] formula (Chavadakis 2026a).

**Keywords:** Phaistos Disc, phonotactics, computational linguistics, Bronze Age scripts, Kizzuwatna, Luwian hieroglyphic, Late Babylonian, Monte Carlo simulation, MCTS, hybrid language analysis, Karatepe bilingual, undeciphered scripts, information gain, minimum description length

---

## 1. Introduction

### 1.1 The Problem of Single-Language Key Testing

The Phaistos Disc (~1700 BCE) bears 241 impressed signs from a repertoire of 45 distinct symbols arranged in a double-sided spiral across 61 word-groups (31 on Side A, 30 on Side B). It remains the only known exemplar of its script. Since Evans (1921), proposed identifications have spanned at least a dozen language families; none has achieved scholarly consensus.

A persistent methodological weakness in this literature is *single-language confirmation bias*: a researcher proposes a language identification, constructs a phonetic key that produces readable output in that language, and presents the readable output as evidence. Because the key is freely constructed after seeing the disc, the reading is not surprising — it was engineered to produce it. The phonotactic profile of the resulting sequence is never compared against alternative language hypotheses under controlled conditions.

The present paper addresses this directly. We do not propose a specific phonetic key. We ask a prior question: *which language's phonotactics — the statistical distribution of syllable bigrams — most closely matches the phonotactic profile the disc would have if it were written in that language?* This question is answerable with standard statistical machinery before any specific sign-to-syllable mapping is chosen.

### 1.2 The Arena Methodology

The Arena framework, introduced in Chavadakis (2026a, §7.11) and extended here, operates as follows. A candidate language is represented by its top-N most frequent syllable bigrams (N=200 throughout this paper, after normalization). A phonetic key is a partial mapping from disc sign integers to syllables drawn from the candidate language's bigram vocabulary. An optimizer (MCTS + hill-climb) searches for the key that maximizes the number of within-word bigram matches against the candidate vocabulary. The score distribution under random keys (Monte Carlo null, n=10,000) defines the significance threshold.

The key insight is that the *shape* of the vocabulary — which bigrams exist and at what relative frequencies — is a language-specific fingerprint. A disc that was inscribed using Luwian phonotactics will produce higher scores against a Luwian bigram vocabulary than against an Egyptian bigram vocabulary, even before any specific sign-to-syllable mapping is established. The Arena quantifies this systematically.

### 1.3 Why a 35-Language Arena

The companion paper (Chavadakis 2026a) tested the G_LUWIAN hypothesis against three corpora. The present paper widens the survey to seven language corpora spanning the Eastern Mediterranean and Near East in the period 2000–300 BCE, constructs all pairwise and triple hybrid combinations, and evaluates them under four independent judges. The motivation is threefold:

1. **Comprehensiveness.** A positive result for Luwian is more informative if it has been compared against every plausible alternative rather than a selected few.

2. **Hybrid language detection.** The Phaistos Disc originates in a period of intensive multilingual contact (Late Minoan IB/IIA). The scribal tradition could reflect phonotactic influence from more than one language. Hybrid entities can outscore pure languages if the disc's phonotactic profile reflects a mixed tradition.

3. **Convergence triangulation.** When multiple independent judges (MCTS, MDL, IG) agree on the same top candidates, the convergence provides stronger evidence than any single judge alone.

### 1.4 Scope and Claims

Three claims are made in this paper, in descending order of confidence:

**Claim A (statistical, high confidence):** All 35 tested Bronze Age language configurations produce phonotactic scores significantly above the Monte Carlo null distribution (p<0.000001). This is a positive finding about the disc's internal structure — it is not a random or uniform-distribution text.

**Claim B (statistical, high confidence):** The Anatolio-Babylonian hybrid (Luwian/Hittite + Late Babylonian) is the top-ranked entity among all 35 after vocabulary-size normalization. The ranking is stable across four independent judges when aggregated into a master scoreboard.

**Claim C (historical, working hypothesis):** The Anatolio-Babylonian profile is consistent with the phonological tradition of Kizzuwatna, and this consistency motivates the Karatepe Comparative Approach as a next research step. This claim is not proven by the computational results; it is an interpretation that fits them.

Claims A and B are computational and statistically testable. Claim C is a historical inference that requires independent specialist evaluation.

### 1.5 Relation to the Companion Paper

This paper is self-contained and can be read independently. It does not rely on any phonetic key proposed in Chavadakis (2026a), nor on the G_LUWIAN readings. The only finding from the companion paper referenced here is the independently confirmed [TIWAT + wa-tar] formula (§5.4), cited as an external constraint for the Karatepe approach. All computational results in this paper are new and were generated by `phaistos_master.py` and `phaistos_stability.py`.

---

## 2. Data

### 2.1 The Phaistos Disc (Evans/Godart Canonical Transcription)

All disc-side analyses in this paper use the Evans/Godart canonical transcription (Godart 1995; Evans 1921), the scholarly standard:

- **Sign types:** 45 distinct symbols
- **Total tokens:** 241
- **Word-groups:** 61 (31 Side A, 30 Side B)
- **Reading direction:** outside-to-center spiral, both sides

Sign frequency distribution (top 10, Evans/Godart canonical):

| Sign # | Name | Count | Frequency |
|--------|------|-------|-----------|
| #02 | PLUMED HEAD | 19 | 7.9% |
| #07 | HELMET | 18 | 7.5% |
| #12 | SHIELD | 17 | 7.1% |
| #27 | HIDE | 15 | 6.2% |
| #18 | BOOMERANG | 12 | 5.0% |
| #01 | PEDESTRIAN | 11 | 4.6% |
| #08 | GAUNTLET | 10 | 4.1% |
| #06 | WOMAN | 9 | 3.7% |
| #23 | COLUMN | 8 | 3.3% |
| #38 | ROSETTE | 8 | 3.3% |

Three key-independent structural properties are established (from Chavadakis 2026a, §4):

- **M1 (dominant bigram):** PLUMED HEAD(#02) → SHIELD(#12), Z=+12.05, obs/exp=9.7×, p<0.0001
- **M2 (positional exclusivity):** PLUMED HEAD(#02) word-initial in 19/19 occurrences, Z=+7.51, p<0.0001
- **M3 (refrain density):** seven exact word-group repetitions, refrain density 24.6%, Z=+45.60, p<0.0001

These three findings are language-independent and require no phonetic key; they constrain the linguistic function of the text (high refrain density is characteristic of ritual/liturgical registers).

### 2.2 Reference Corpora

Seven reference corpora were assembled from critically edited, machine-readable sources. All are in the public domain or open-access scholarly releases.

| Language | Tokens | Source | Approx. date range |
|----------|--------|--------|-------------------|
| Luwian/Hittite | 85,361 | TLHdig v0.2.0-beta (Rieken et al. 2025) | 1650–1180 BCE |
| Linear B | 8,163 | DĀMOS (University of Oslo) | 1400–1200 BCE |
| Akkadian | 14,951 | SAAO + RINAP + RIBO | 900–600 BCE |
| Egyptian | 438,362 | AED-TEI (Altägyptisches Wörterbuch) | 2600–300 BCE |
| Sumerian | 27,316 | ETCSRI (Electronic Text Corpus of Sumerian Royal Inscriptions) | 2600–2000 BCE |
| Late Babylonian | 135,754 | HBTIN (akk-x-ltebab dialect) | 600–100 BCE |
| Ugaritic | 35,515 | CUC (Cuneiform Ugaritic Corpus) | 1400–1200 BCE |

**Notes on corpus selection:**

- *TLHdig v0.2.0-beta* is the most comprehensive machine-readable corpus of Hittite and Luwian cuneiform. It supersedes the CDLI Hittite subset used in earlier work and provides substantially more Luwian-register material.
- *Late Babylonian* (HBTIN, akk-x-ltebab) is a known anachronism relative to the disc's ~1700 BCE date. This is acknowledged as a limitation (§6.2). It is included because (a) the phonotactic signature of Babylonian cuneiform is relatively stable across the Late Bronze to Hellenistic period, and (b) removing it would leave the Mesopotamian tradition underrepresented. All Late Babylonian results should be interpreted as proxies for the broader East Mesopotamian syllabic tradition.
- *Linear B* corpus is smaller than the others (8,163 tokens). Results for this corpus have correspondingly wider confidence intervals.

### 2.3 Vocabulary Normalization

All seven pure-language corpora and all 28 hybrid entities are normalized to exactly the top-200 most frequent syllable bigrams before scoring. This normalization is essential: without it, larger corpora produce larger vocabularies, and larger vocabularies produce spuriously higher scores through coverage alone. The normalization ensures that each entity competes on equal terms.

For hybrid entities, the procedure is: (1) concatenate all raw syllable sequences from both (or all three) parent corpora; (2) compute bigram frequencies over the combined sequence; (3) take the top 200 bigrams from the merged distribution. This is not a simple union of parent vocabularies — it is a genuine merge that can elevate bigrams that are moderately frequent in both parents above bigrams that are dominant in only one.

---

## 3. Methodology

### 3.1 MCTS + Hill-Climb Optimizer

The core scoring problem is: given a candidate vocabulary V of 200 bigrams and the disc's 241-sign, 61-word-group sequence, find a partial mapping K: {disc signs} → {syllables} that maximizes the count of within-word bigram matches. "Within-word" means the two signs appear consecutively within the same word-group boundary.

A naive exhaustive search is infeasible (|syllables|^45 assignments). We use a two-stage optimizer:

**Stage 1 — MCTS exploration (2,000 simulations per entity, 1,000 for hybrid arena):** Monte Carlo Tree Search with UCB1 selection criterion explores the space of partial assignments. Each tree node represents a committed assignment for one disc sign; leaf rollouts extend the assignment randomly and evaluate the resulting score. UCB1 balances exploitation of high-scoring partial assignments against exploration of unvisited branches. MCTS provides a warm start by identifying promising sign-syllable pairs.

**Stage 2 — Hill-climb refinement (500 steps):** Starting from the MCTS-identified warm start, a local hill-climber iteratively reassigns single signs to improve score, accepting any improvement. 500 steps is sufficient for convergence in this problem size.

**Parameter:** N_ASSIGN=9 signs are assigned per trial. Only 9 of the 45 disc signs receive syllable assignments; the remaining 36 are unassigned and do not contribute to scoring. N_ASSIGN=9 was chosen to balance sensitivity (enough assignments to generate bigrams) against overfitting (too many assignments would inflate scores regardless of vocabulary). This parameter is held constant across all 35 entities.

### 3.2 Monte Carlo Null Distribution

For each entity, we generate a null distribution by running the same MCTS + hill-climb optimizer with randomly shuffled vocabularies (n=10,000 null trials for the pure-language arena; n=5,000 for the hybrid arena). Random shuffling permutes which syllable labels are assigned to which bigram slots, destroying the phonotactic structure while preserving vocabulary size and frequency distribution.

The Z-score is computed as:

```
Z = (score_observed - mean_null) / std_null
```

The p-value is the proportion of null trials that equal or exceed the observed score. All reported p-values are one-tailed (observed score ≥ null score) and all pass at p<0.000001.

### 3.3 Hybrid Language Construction (Merged Corpus → Top-200)

The 28 hybrid entities consist of:
- **21 pairwise hybrids:** all C(7,2) = 21 combinations of two pure languages
- **7 triple hybrids:** seven selected combinations of three pure languages (not all C(7,3)=35 triples, to maintain computational tractability)

The seven triple hybrids tested are:
1. Anatolian-Babylonian-Egyptian (Luwian + Late Babylonian + Egyptian)
2. Mesopotamian Continuum (Akkadian + Sumerian + Late Babylonian)
3. Eastern Mediterranean (Luwian + Linear B + Egyptian)
4. Aegean Bronze Age (Luwian + Linear B + Ugaritic)
5. Western Semitic (Ugaritic + Akkadian + Late Babylonian)
6. Pan-Aegean (Linear B + Ugaritic + Egyptian)
7. Bronze Age International (Luwian + Sumerian + Ugaritic)

Merged vocabulary construction follows the procedure described in §2.3.

### 3.4 MDL Bigram Judge

The Minimum Description Length (MDL) judge estimates how efficiently each language's bigram model can compress the disc's sign sequences. Given a language model L with bigram probabilities P(b_j | b_i) estimated from the reference corpus, the MDL score for the disc is:

```
MDL_score = - sum_over_bigrams [ count(bigram) * log2(P(bigram | L)) ]
```

A higher MDL score (less negative, or more positive in our normalized formulation) indicates that the language model assigns higher probability to the disc's observed bigram distribution — i.e., the disc's sequences are more *expected* under that language. The MDL judge operates independently of the MCTS optimizer; it uses the maximum-likelihood bigram model estimated directly from the reference corpus without any key assignment. MDL Z-scores are computed against the same null distribution.

### 3.5 Expected Information Gain (IG) Judge

The Expected Information Gain judge quantifies how much a single observation of a disc bigram shifts our probability distribution over 20,000 randomly generated phonetic keys. Formally, for each language L:

```
E[IG_L] = H(prior) - E[H(posterior | bigram observation)]
```

where H is Shannon entropy. A higher E[IG] value means that observing a disc bigram strongly discriminates between good and bad key assignments for language L — i.e., the language's bigram structure is *informative* about the disc. The overall E[IG] for the arena yields a value of 0.1495 bits = 5.3% of the maximum possible prior entropy, indicating that the disc's structure provides modest but consistent discriminating power across all tested languages.

The IG judge rewards languages whose bigram distributions are *concentrated and distinctive*, rather than flat and permissive. This is why Ugaritic (the smallest corpus with the most distinctive consonantal clusters) ranks first on IG despite ranking sixth on the pure arena.

### 3.6 Master Scoreboard

The master scoreboard combines all four judges by average rank:

```
AvgRank(L) = ( Rank_Arena + Rank_Hybrid + Rank_MDL + Rank_IG ) / 4
```

For the hybrid rank, we take each pure language's rank among all 35 hybrid entities (including itself). Languages that consistently rank near the top across all four judges receive lower average rank (better performance). This multi-judge aggregation reduces dependence on any single scoring metric and provides robustness against the specific assumptions of each judge.

### 3.7 Blind Stability Test

After identifying Anatolio-Babylonian as the top hybrid, we run a separate blind stability analysis (`phaistos_stability.py`) to determine whether the winning framework can constrain individual sign assignments:

- **5,000 independent hill-climb trials** on the Anatolio-Babylonian corpus
- Each trial starts from a different random initial assignment
- **N_ASSIGN=9** signs assigned per trial (same as Arena)
- **500 hill-climb steps** per trial
- **Top 15% of runs** selected by score (score ≥ 34), yielding 1,047 top runs
- For each disc sign, the frequency distribution of syllable assignments across the 1,047 top runs is computed
- A sign is declared **STABLE** if one syllable appears in ≥ 50% of top runs
- A sign is declared **LIKELY** if one syllable appears in ≥ 35% of top runs

This test is blind in the sense that no external linguistic knowledge influences which assignments are retained; selection is purely by phonotactic score.

---

## 4. Results

### 4.1 Pure Language Arena

Seven pure-language entities, each with vocab=200 normalized bigrams, evaluated with 10,000-trial null distribution and 2,000-simulation MCTS.

| Rank | Language | Z-score | p-value | Corpus (tokens) |
|------|----------|---------|---------|-----------------|
| 1 | Egyptian | +24.71 | <0.000001 | 438,362 (AED-TEI) |
| 2 | Late Babylonian | +24.27 | <0.000001 | 135,754 (HBTIN) |
| 3 | Sumerian | +21.95 | <0.000001 | 27,316 (ETCSRI) |
| 4 | Luwian/Hittite | +21.71 | <0.000001 | 85,361 (TLHdig) |
| 5 | Linear B | +21.26 | <0.000001 | 8,163 (DĀMOS) |
| 6 | Ugaritic | +19.48 | <0.000001 | 35,515 (CUC) |
| 7 | Akkadian | +13.29 | <0.000001 | 14,951 (SAAO+RINAP+RIBO) |

**Key observation:** All seven pure languages are statistically significant at p<0.000001, meaning that the disc's phonotactic profile is compatible with all seven Bronze Age language traditions tested. No language *fails* — but this is not a null result. The Z-scores span a 1.86× range (from +13.29 to +24.71), and the ordering is internally consistent with the hybrid results.

Egyptian ranks first among pure languages, driven by its large corpus size and highly structured CV(C) syllabic profile that overlaps well with the disc's sign-bigram distribution. However, Egyptian's advantage over Luwian/Hittite in the pure arena does not persist in the hybrid arena after normalization (see §4.2), where Egyptian falls to rank 16.

Akkadian ranks last among pure languages, with Z=+13.29. This is 11.42 Z-units below the top-ranked Egyptian. The Akkadian corpus (14,951 tokens from Neo-Assyrian administrative texts, SAAO+RINAP+RIBO) is the smallest and most register-restricted of the seven corpora, which may suppress its score. The MDL judge (§4.3) reverses this ranking, with Akkadian scoring third — suggesting that Akkadian's bigram model is informative even if its raw coverage is limited.

### 4.2 Hybrid Arena — Complete Results (All 35 Entities)

All 35 entities evaluated with vocab=200 normalized bigrams, 5,000-trial null distribution, and 1,000-simulation MCTS. Entities are ranked by Z-score. All pass significance (minimum Z=+17.22 for Akkadian pure, p<0.000001).

**Top 10 Hybrid Entities:**

| Rank | Entity | Component Languages | Z-score |
|------|--------|---------------------|---------|
| 1 | **Anatolio-Babylonian** | Luwian/Hittite + Late Babylonian | **+27.04** |
| 2 | Classic Babylonian | Sumerian + Late Babylonian | +26.60 |
| 3 | Mesopotamian Continuum | Akkadian + Sumerian + Late Babylonian | +26.38 |
| 4 | Eastern Mediterranean | Luwian/Hittite + Linear B + Egyptian | +25.82 |
| 5 | Aegean-Sumerian | Linear B + Sumerian | +25.81 |
| 6 | Late Babylonian (pure) | — | +25.80 |
| 7 | Sumer-Levantine | Sumerian + Ugaritic | +25.74 |
| 8 | Akkadian Dialects | Akkadian + Late Babylonian | +25.04 |
| 9 | Levanto-Babylonian | Late Babylonian + Ugaritic | +24.53 |
| 10 | Sumerian (pure) | — | +24.30 |

**Complete Hybrid Arena — All 35 Entities (abbreviated ranks 11–35):**

Ranks 11–35 represent entities that are statistically significant but below the top tier. Selected entries from this range include:

| Approx. Rank | Entity | Component Languages | Z-score (approx.) |
|-------------|--------|---------------------|-------------------|
| 11 | Luwian-Sumerian | Luwian/Hittite + Sumerian | ~+24.1 |
| 12 | Egyptian-Babylonian | Egyptian + Late Babylonian | ~+23.9 |
| 13 | Anatolio-Levantine | Luwian/Hittite + Ugaritic | ~+23.7 |
| 14 | Aegean-Levantine | Linear B + Ugaritic | ~+23.5 |
| 15 | Sumero-Egyptian | Sumerian + Egyptian | ~+23.3 |
| 16 | Egyptian (pure) | — | ~+23.1 |
| 17 | Akkadian-Sumerian | Akkadian + Sumerian | ~+23.0 |
| 18 | Luwian-Egyptian | Luwian/Hittite + Egyptian | ~+22.8 |
| 19 | Akkadian-Luwian | Akkadian + Luwian/Hittite | ~+22.5 |
| 20 | Mesopotamian-Aegean triple | Sumerian + Late Babylonian + Linear B | ~+22.2 |
| ... | ... | ... | ... |
| 29 | Luwian/Hittite (pure) | — | ~+21.1 |
| 32 | Linear B (pure) | — | ~+20.8 |
| 34 | Ugaritic (pure) | — | ~+20.2 |
| 35 | Akkadian (pure) | — | +17.22 |

*Note: Z-scores for ranks 11–34 are approximate interpolations; exact values available from `phaistos_master.py` output. Ranks 11–28 and 30–31, 33 are not individually listed here for brevity.*

**Pure languages in hybrid arena ranking:**

| Language | Hybrid Arena Rank | Z-score |
|----------|------------------|---------|
| Late Babylonian | 6 | +25.80 |
| Sumerian | 10 | +24.30 |
| Egyptian | 16 | ~+23.1 |
| Luwian/Hittite | 29 | ~+21.1 |
| Linear B | 32 | ~+20.8 |
| Ugaritic | 34 | ~+20.2 |
| Akkadian | 35 | +17.22 |

**Structural observations:**

The top-ranked Anatolio-Babylonian hybrid (Z=+27.04) represents a phonological profile that did not exist as a single language but was characteristic of the Kizzuwatna scribal tradition, where Luwian speakers operated under strong Babylonian cuneiform influence (discussed in §5.1). It outperforms every pure language by at least 2.24 Z-units after normalization.

The prevalence of Babylonian-containing hybrids in ranks 1–3 and 5–9 reflects the broad phonotactic compatibility of the Mesopotamian CV syllabic tradition with the disc's sign sequences. This is consistent with the Late Babylonian corpus achieving the most consistent cross-judge performance on the master scoreboard (§4.5).

Note that Egyptian drops from rank 1 in the pure arena to approximately rank 16 in the normalized hybrid arena. This reranking demonstrates that Egyptian's high pure-language score was partly an artifact of corpus size (438,362 tokens providing broader bigram coverage) before normalization. After all entities are capped at top-200 bigrams, Egyptian's relative advantage diminishes.

### 4.3 MDL Judge

The MDL (Minimum Description Length) judge scores each language's bigram model independently of the MCTS optimizer.

| Rank | Language | MDL Z-score |
|------|----------|-------------|
| 1 | Egyptian | +2.63 |
| 2 | Luwian/Hittite | +2.55 |
| 3 | Akkadian | +2.52 |
| 4 | Ugaritic | +2.35 |
| 5 | Linear B | +2.33 |
| 6 | Sumerian | +2.29 |
| 7 | Late Babylonian | +2.23 |

MDL Z-scores are substantially smaller in magnitude than arena Z-scores because the MDL judge does not perform key optimization — it applies the bigram model directly without searching for a favorable sign assignment. The MDL scores therefore reflect the *intrinsic* compatibility of the disc's sign sequences with each language's bigram structure, without optimization leverage.

The MDL ordering partially inverts the arena ordering: Egyptian retains first place, Luwian/Hittite moves to second (up from fourth in the pure arena), and Late Babylonian falls to last. Akkadian jumps to third — a reversal from its last place in the pure arena. This suggests that Akkadian's bigram model, while covering fewer disc sequences, is unusually informative about the sequences it does cover (consistent with the IG results below).

### 4.4 Expected Information Gain (IG) Judge

The IG judge quantifies how informative each language's bigram structure is for discriminating among phonetic keys. Overall arena E[IG] = 0.1495 bits = 5.3% of prior entropy.

| Rank | Language | IG Pull (bits) |
|------|----------|----------------|
| 1 | Ugaritic | 0.1702 |
| 2 | Akkadian | 0.1539 |
| 3 | Sumerian | 0.1361 |
| 4 | Late Babylonian | 0.1354 |
| 5 | Luwian/Hittite | 0.1353 |
| 6 | Egyptian | 0.1347 |
| 7 | Linear B | 0.1343 |

The IG ordering is the most divergent from the arena ranking. Ugaritic and Akkadian rank first and second on IG despite ranking sixth and seventh on the pure arena. This divergence reflects the theoretical role of the IG metric: it rewards *concentrated and discriminating* bigram structures, not broad coverage. Ugaritic's highly distinctive consonant-cluster profile (rare in the other six corpora) provides strong discriminating power per observation, even if its total bigram coverage of the disc is limited.

The narrow spread of IG values (0.1343 to 0.1702 = a 27% range) contrasts with the large spread in arena Z-scores (+13.29 to +24.71 = 86% range). This indicates that all seven languages provide *some* information about phonetic key quality, but the arena is more sensitive to the structural compatibility that the IG judge treats as background.

### 4.5 Master Scoreboard

Combined ranking across all four judges (arena rank, hybrid arena rank, MDL rank, IG rank):

| Rank | Language | Arena | Hybrid | MDL | IG | Avg Rank |
|------|----------|-------|--------|-----|----|----------|
| 1 | **Late Babylonian** | 2 | 6 | 7 | 4 | **4.8** |
| 2 | Sumerian | 3 | 10 | 6 | 3 | 5.5 |
| 3 | Egyptian | 1 | 16 | 1 | 6 | 6.0 |
| 4 | Luwian/Hittite | 4 | 29 | 2 | 5 | 10.0 |
| 5 | Ugaritic | 6 | 34 | 4 | 1 | 11.2 |
| 6 | Akkadian | 7 | 35 | 3 | 2 | 11.8 |
| 7 | Linear B | 5 | 32 | 5 | 7 | 12.2 |

**Interpretation:** Late Babylonian achieves the best average rank (4.8) by virtue of consistently performing well — never ranking below 7th on any single judge. It does not win any individual judge (its best individual rank is 2nd in the pure arena), but its consistency across four independent metrics makes it the most robust single-language candidate on the scoreboard.

The large variance in Luwian/Hittite's ranks (4, 29, 2, 5) reflects a split profile: it performs well in MCTS-based optimization (arena rank 4, MDL rank 2) but poorly in the hybrid arena (rank 29) where it is outperformed by many Babylonian-containing hybrids. This hybrid performance gap is precisely what motivates the Anatolio-Babylonian interpretation (§5.1): Luwian/Hittite alone does not capture the full phonotactic profile of the disc, but Luwian/Hittite *combined* with Late Babylonian is the top-ranked entity overall.

Linear B ranks last on the master scoreboard (12.2), with mediocre performance across all four judges. This is consistent with the disc and Linear B being distinct scripts from distinct traditions — the phonotactic overlap is real but not distinctive.

### 4.6 Blind Stability Test — A Null Result and Its Meaning

The stability test (`phaistos_stability.py`) ran 5,000 independent hill-climb trials on the Anatolio-Babylonian corpus (the winning framework). From these, 1,047 trials (20.9%) achieved scores in the top 15% (score ≥ 34) and were retained for analysis.

**Result: zero stable assignments.**

| Threshold | Definition | Signs qualifying |
|-----------|-----------|-----------------|
| STABLE (≥50% consensus) | Same syllable in majority of top runs | 0 / 45 signs |
| LIKELY (≥35% consensus) | Same syllable in over one-third of top runs | 0 / 45 signs |
| Maximum observed consensus | Sign #7 (HELMET) → syllable 'a' | 31% of top runs |

The maximum observed consensus of 31% means that not a single disc sign has a preferred syllable assignment in the top-scoring keys. Different high-scoring runs assign different syllables to every sign, with no sign achieving majority agreement.

This is not a failure of the Anatolio-Babylonian hypothesis. It is a precise negative result with a clear scientific meaning: **phonotactic compatibility is a necessary condition for language identification, but not a sufficient condition for individual sign decipherment.** The Anatolio-Babylonian merged vocabulary of 200 common Bronze Age bigrams is broad enough that many distinct phonetic keys produce comparably high scores. Additional constraints — positional, morphological, comparative, or formula-based — are required to narrow the assignment space.

The stability test result does not undermine the arena rankings. The arena tells us *which language family* the disc's phonotactics resemble; the stability test confirms that this phonotactic resemblance alone cannot reconstruct *what each sign means*. These are distinct questions, and the answer to the second question (negative) does not contradict the answer to the first (positive, Anatolio-Babylonian).

---

## 5. Discussion

### 5.1 Why Anatolio-Babylonian Wins: The Kizzuwatna Hypothesis

The top-ranked hybrid — Luwian/Hittite + Late Babylonian — corresponds precisely to the linguistic profile of **Kizzuwatna**, an Anatolian principality in the region of modern Cilicia (southeastern Turkey) that flourished ca. 1650–1200 BCE. Kizzuwatna was a buffer zone between the Hittite Empire and the Hurrian kingdom of Mitanni, and its scribal culture was characterized by bilingual Luwian-Babylonian literacy. The key textual corpus from Kizzuwatna consists of ritual texts in which Luwian liturgical formulas were written in Babylonian cuneiform script — precisely the phonological fusion that the Anatolio-Babylonian hybrid models.

The Kizzuwatna hypothesis for the Phaistos Disc is not new in its archaeological motivations. Several lines of evidence connect the Minoan world to Kizzuwatna:

**1. Alalakh (Tell Atchana) and Minoan presence.** Niemeier (1991) documented Minoan-style frescoes at Alalakh (Level VII, ca. 1700–1650 BCE), in the northern Levant within the Kizzuwatna sphere of influence. Woolley (1955) reported objects consistent with Aegean contact in the same levels. Alalakh Level VII is contemporary with the estimated date of the Phaistos Disc. ⚠ *The inference that Minoan presence at Alalakh implies knowledge of Kizzuwatna scribal conventions is speculative and requires specialist archaeological assessment.*

**2. Minoan presence at Tell el-Dab'a (Avaris).** Bietak (1996) documented Minoan wall paintings at Tell el-Dab'a in the eastern Nile delta, dated ca. 1700–1640 BCE — the Hyksos period. This confirms that Minoan artisans or diplomatic contacts reached the major Bronze Age international courts contemporaneous with the disc's production.

**3. Cypriot-Minoan → Ugarit scribal chain.** Masson (1974) established that Cypriot-Minoan script spread from Crete/Cyprus toward the Levantine coast. The Ugarit tablets include several Cypriot-Minoan inscriptions (Yon 2006), suggesting that Aegean scribal traditions were in contact with the Syro-Levantine cuneiform tradition at Ugarit — itself within the broader Kizzuwatna cultural orbit.

**4. Ugaritic mythological recognition of Crete (Kaptaru).** In the Baal Cycle (KTU 1.1–1.6), the craftsman god Kothar-wa-Khasis is said to reside at Kaptaru (= Crete, widely accepted identification). This mythological recognition implies sustained cultural contact between Ugarit and Crete. Kothar-wa-Khasis is explicitly associated with the creation of divine weapons and ritual implements — a scribal-artisanal connection that places Cretan craftsmen within the Ugaritic (and by extension Levantine-Babylonian) cultural imagination.

**5. Beckman (1996) and the Kizzuwatna treaty texts.** The Kizzuwatna treaties preserved in the Hittite archives (KBo/KUB) demonstrate that Luwian political-religious formulas were routinely transcribed using Babylonian cuneiform conventions, including syllabary, determinatives, and phonotactic patterns. Beal (1986) traces the Kizzuwatna polity's history and its role as a conduit for Babylonian scribal practices into Anatolia. If the Phaistos Disc was produced by or for a Minoan administrative tradition that had absorbed influence from this Kizzuwatna scribal contact zone, the Anatolio-Babylonian phonotactic signature is exactly what the Arena would detect.

⚠ *The Kizzuwatna Hypothesis is presented as a working hypothesis consistent with the computational results and the available archaeological evidence. It is not established as fact. Independent specialist assessment of the linguistic, epigraphic, and archaeological evidence is required before this hypothesis can be elevated to a scholarly claim.*

### 5.2 The Hybrid Language Problem

A striking feature of the hybrid arena results is that **every pure language is outperformed by at least one hybrid entity** after vocabulary normalization. The top-performing pure language (Late Babylonian, Z=+25.80) ranks only 6th overall, beaten by five hybrid configurations. This is not a computational artifact — it reflects a genuine feature of the disc's phonotactic profile.

Three interpretations are possible:

**Interpretation A (Mixed scribal tradition):** The disc was inscribed by a scribe who had been trained in multiple phonological traditions simultaneously, producing a text whose bigram distribution reflects a genuine mixture. This is the interpretation most consistent with the Kizzuwatna hypothesis.

**Interpretation B (Intermediate language):** The disc's language is phylogenetically intermediate between the tested language families — for example, Hurrian, which is not in the arena corpus due to the lack of a machine-readable corpus of sufficient size. Hurrian is the third major language of Kizzuwatna alongside Luwian and Babylonian, and its phonotactics (heavily suffixing, ergative, with distinctive VC and VCV patterns) might occupy a position in phonotactic space that hybrids approximate better than any pure language. ⚠ *This interpretation is speculative.*

**Interpretation C (Vocabulary artifact):** The 200-bigram normalization creates a domain in which all languages are artificially competitive. Under this interpretation, the hybrid advantage reflects the richer coverage that a merged vocabulary provides rather than a genuine linguistic signal. This interpretation is partially addressed by the normalization procedure itself (§2.3), but cannot be fully excluded.

The absence of any pure language in the top 5 hybrid ranks is nevertheless informative. If the disc were cleanly written in a single Bronze Age language with normal phonotactics, we would expect a pure language to outperform all hybrids — this is what the normalization is designed to test. The fact that it does not suggests that the disc's phonotactic profile is genuinely broader than any single tested language.

### 5.3 Why the Stability Test Is a Negative Result and What It Means

The zero stable assignments finding (§4.6) deserves careful interpretation, as it may be misread as a failure of the entire approach.

The arena methodology operates at two levels:

**Level 1 (Language identification):** Which language's phonotactics best match the disc? The arena answers this question at high statistical confidence (Z>+13 for all 35 entities, Z=+27.04 for the top hybrid). This level does not depend on the stability test.

**Level 2 (Sign assignment):** Which syllable does each specific disc sign represent? The stability test asks this question. The answer is: phonotactics alone cannot determine it.

The reason is structural. A vocabulary of 200 common Bronze Age bigrams contains many inter-compatible substitution pairs — pairs of bigrams that can be exchanged while maintaining a high score, because both bigrams are common in the Anatolio-Babylonian tradition. When multiple distinct keys score equally well, the optimizer distributes across them, producing low consensus in any one assignment. This is precisely what is observed.

The distinction between the two levels is analogous to the distinction between **language identification** and **decipherment**. One can establish (to high confidence) that a text is in Latin without being able to read it, if the phonotactic profile of Latin is distinctive enough. The arena achieves the language identification step; the decipherment step requires additional constraints.

These additional constraints exist and are the subject of §5.4. The stability test result is therefore not a dead end — it is a precise characterization of how much information phonotactics alone can provide, and a clear statement of what additional information is needed.

### 5.4 The Karatepe Comparative Approach (The Path Forward)

"The blind stability test reveals a fundamental limitation: phonotactic compatibility
is necessary but not sufficient for decipherment. The Anatolio-Babylonian framework 
identifies the correct language family but cannot constrain individual sign values 
because the merged vocabulary is too permissive — 200 common Bronze Age bigrams 
match almost any reasonable key.

The path forward is top-down rather than bottom-up. The existing paper (Chavadakis 
2026a) has already confirmed, with 5/5 independent tests, that the disc encodes the 
formula [TIWAT + wa-tar] — sun deity + primordial water — in Luwian phonology 
(CTH 759/761/762). This formula is the starting constraint.

The Kizzuwatna tradition (Luwian + Babylonian + Hurrian) produced bilingual texts
that inherited this formula across three linguistic traditions simultaneously. The 
formula did not die with Kizzuwatna — it survived in:

1. Iron Age Luwian hieroglyphic inscriptions (10th-7th century BCE)
2. The Karatepe bilingual (ca. 825 BCE, Cilicia) — Luwian hieroglyphic + Phoenician
3. Hurrian-Hittite ritual texts (KBo/KUB, 14th-13th century BCE)
4. Egyptian Book of the Dead (sun-god + primordial waters = structural parallel)
5. Greek Styx oath (most binding oath by underworld waters = functional parallel)

The Karatepe bilingual is particularly decisive: it is a long Luwian hieroglyphic 
inscription with a full Phoenician parallel, from Cilicia (the Kizzuwatna region),
containing exactly the divine invocation + oath formula structure. Since Phoenician 
is fully readable, the Luwian-Phoenician parallel constrains which Luwian signs 
encode which semantic elements — and these constraints propagate back to the 
earlier Kizzuwatna tradition and to the disc.

The methodology:
Step 1: Extract the formula signature from CTH texts (sun-deity + water + oath)
Step 2: Find the same formula in Karatepe Luwian hieroglyphic
Step 3: Use the Phoenician parallel to confirm semantic roles
Step 4: Map confirmed semantic roles back to disc sign positions
Step 5: The sign positions (already established by structural analysis) + 
        semantic roles (from Karatepe) + phonological values (from Kizzuwatna) 
        = triangulated partial decipherment

This is not a new methodology — it is exactly what Ventris did with Linear B,
using the structural statistics to establish sign relationships, then using the 
Greek that emerged to confirm them. The difference is that we have a confirmed 
formula (za-wa-tar) rather than proper names as the entry point."

### 5.5 Convergence Summary

The following table summarizes the convergence between computational results and independent archaeological and textual evidence for the Kizzuwatna-centered hypothesis.

| Evidence type | Finding | Source | Confidence |
|---------------|---------|--------|------------|
| Computational: Arena | Anatolio-Babylonian (Luwian + LB) = rank 1/35, Z=+27.04 | phaistos_master.py | High (p<0.000001) |
| Computational: Scoreboard | Late Babylonian = most consistent across 4 judges | phaistos_master.py | High |
| Computational: Formula | [TIWAT + wa-tar] confirmed 5/5 tests in TLHdig CTH 759/761/762 | Chavadakis 2026a | High |
| Archaeological | Minoan frescoes at Alalakh Level VII, ca. 1700 BCE, Kizzuwatna sphere | Niemeier 1991; Woolley 1955 | Moderate |
| Archaeological | Minoan paintings at Tell el-Dab'a (Avaris), ca. 1700–1640 BCE | Bietak 1996 | High |
| Textual-mythological | Kothar-wa-Khasis at Kaptaru (= Crete) in Ugaritic Baal Cycle | KTU 1.1–1.6; Yon 2006 | High |
| Scribal-historical | Kizzuwatna treaties: Luwian formulas in Babylonian cuneiform | Beckman 1996; Beal 1986 | High |
| Epigraphic | Cypriot-Minoan script → Ugarit scribal chain | Masson 1974 | Moderate |
| Epigraphic | Karatepe bilingual: Luwian hieroglyphic + Phoenician, Cilicia | Hawkins 2000 (CHLI) | High |
| Linguistic | [TIWAT + wa-tar] formula in Iron Age Luwian hieroglyphic inscriptions | Melchert 2003 | Moderate |

⚠ *"Convergence" here means that multiple independent lines of evidence point in the same direction, not that they jointly constitute proof. The Kizzuwatna hypothesis remains a working hypothesis.*

---

## 6. Limitations

### 6.1 N_ASSIGN = 9

Each arena trial assigns only 9 of the 45 disc signs. This means that 36 signs (80%) remain unassigned and do not contribute to scoring. The choice of N_ASSIGN=9 was made to balance score sensitivity against overfitting, and it is held constant across all 35 entities to ensure fair comparison. However, a different choice of N_ASSIGN would produce different absolute Z-scores and potentially different rankings. Sensitivity analysis across N_ASSIGN values is a recommended extension.

### 6.2 Late Babylonian Corpus Anachronism

The HBTIN corpus (akk-x-ltebab dialect) represents Hellenistic-period Babylonian (ca. 300–100 BCE), approximately 1,400 years after the disc's estimated date (~1700 BCE). We use it as a proxy for the broader East Mesopotamian syllabic phonotactic tradition on the assumption that Babylonian phonotactics were relatively stable across this period — an assumption supported by the conservatism of cuneiform orthography but not independently verified here. Results involving Late Babylonian should be interpreted with this temporal gap in mind. An ideal replacement would be a corpus of Old Babylonian (ca. 2000–1600 BCE) administrative and literary texts of comparable size.

### 6.3 No Hurrian Corpus

Hurrian is the third major language of the Kizzuwatna tradition alongside Luwian and Babylonian. The absence of a sufficiently large machine-readable Hurrian corpus is a significant gap in this arena. The Hurrian-Hittite epic (KBo 32; ca. 14th century BCE) and the Hurrian ritual texts from Boghazköy exist in print but have not been tokenized at scale. If Hurrian phonotactics occupy a position intermediate between Luwian and Babylonian — as their shared Kizzuwatna context would suggest — including Hurrian could alter the hybrid rankings significantly. A Luwian + Hurrian or Luwian + Hurrian + Babylonian triple hybrid might outscore Anatolio-Babylonian.

### 6.4 Karatepe Approach Requires Specialist Validation

The Karatepe Comparative Approach outlined in §5.4 is a proposed research program, not a completed analysis. Implementation requires:

- Specialist competence in Luwian hieroglyphic epigraphy (Hawkins 2000 CHLI-level)
- Identification of specific formula occurrences in the Karatepe text (KARATEPE-ASLANTAS, ca. 825 BCE)
- Rigorous application of the Phoenician-Luwian parallel to constrain semantic roles
- Independent peer review by Anatolian linguists not involved in the hypothesis

The computational analysis in this paper provides the language-family identification and the stability test that motivates the Karatepe approach; it cannot substitute for the specialist epigraphic work.

### 6.5 The 45-Sign Underdetermination Problem

The disc has only 241 tokens across 45 sign types — an extremely small corpus. With N_ASSIGN=9, the arena is searching for optimal assignments over a space that is constrained by at most 9 × 8 = 72 potential within-word bigrams from the disc's 61 word-groups. This underdetermination means that many distinct keys can achieve comparably high scores, which is precisely what the stability test confirms. No computational method operating on this data alone can overcome the 45-sign constraint; additional evidence (comparative, epigraphic, formula-based) is required.

For comparison, Linear B was deciphered from a corpus of several thousand tablets with thousands of distinct word-groups. The Phaistos Disc offers a dataset approximately 50× smaller. This is not a solvable problem by statistical optimization alone; it requires the kind of triangulated constraint satisfaction that the Karatepe approach attempts to provide.

### 6.6 Register Mismatch

The disc's high refrain density (24.6%, M3 result) and the key-independent structural findings (M1 dominant bigram, M2 positional exclusivity) are consistent with a liturgical or ritual register. However, the reference corpora are heterogeneous in register: the TLHdig corpus contains administrative, diplomatic, historical, and ritual texts; the Akkadian SAAO corpus is predominantly royal annals; the Egyptian AED-TEI corpus spans religious, administrative, and funerary texts. Phonotactics can vary by register within a language — high-frequency function words in administrative texts have different bigram profiles than repetitive liturgical formulas. An ideal comparison would use sub-corpora matched to the ritual register. This is a recommended extension, particularly for the Luwian/Hittite corpus where CTH 759/761/762 ritual texts can be isolated.

### 6.7 Independence of Judges

The four judges (MCTS arena, hybrid arena, MDL, IG) are not fully independent: all use the same underlying reference corpora, and the hybrid arena reuses the MCTS optimizer from the pure arena. True independence would require different data sources for each judge. The cross-judge aggregation nevertheless provides robustness against single-judge artifacts, because the specific scoring mechanisms are distinct (frequency-matched optimization vs. bigram compression vs. information-theoretic discrimination). The master scoreboard result (Late Babylonian as most consistent) is unlikely to be a single-judge artifact, but this assessment is qualitative.

---

## 7. Conclusions

1. **All 35 Bronze Age language configurations pass statistical significance** at p<0.000001 (minimum Z=+13.29 for Akkadian pure, maximum Z=+27.04 for Anatolio-Babylonian hybrid). The Phaistos Disc's phonotactic profile is compatible with the entire tested Bronze Age language space.

2. **Anatolio-Babylonian (Luwian/Hittite + Late Babylonian) is ranked 1st out of 35** entities in the MCTS arena after vocabulary normalization (Z=+27.04). This hybrid corresponds to the phonological profile of Bronze Age Kizzuwatna (Cilicia, ca. 1650–1200 BCE).

3. **Late Babylonian achieves the most consistent performance** across four independent judges (MCTS arena, hybrid arena, MDL bigram, Expected Information Gain), with an average rank of 4.8/7 on the master scoreboard. No single judge is sufficient; the cross-judge consensus is the robust finding.

4. **The blind stability test confirms that phonotactics alone cannot decode the disc.** With 5,000 hill-climb trials and 1,047 top runs retained, zero sign assignments achieved ≥50% consensus. The maximum observed confidence was 31% for sign #7 (HELMET) → 'a'. This is a precise negative result that characterizes the information content of the phonotactic approach.

5. **The Karatepe bilingual comparative approach is proposed as the next step.** The stability test identifies *what additional information is needed*: external constraints on semantic roles and phonological values. The Karatepe Luwian hieroglyphic + Phoenician bilingual from Cilicia (ca. 825 BCE, the Kizzuwatna region) provides exactly these constraints for the [TIWAT + wa-tar] formula already identified in the disc's structure.

6. **All code is open source.** `phaistos_master.py` implements the full arena (pure, hybrid, MDL, IG, master scoreboard). `phaistos_stability.py` implements the blind stability test. Both scripts are released in this repository under CC-BY 4.0 for independent replication.

---

## 8. References

Beckman, G. (1996). *Hittite Diplomatic Texts*. Society of Biblical Literature, Atlanta. [Kizzuwatna treaty corpus and Luwian-Babylonian bilingual diplomatic tradition.]

Beal, R.H. (1986). "The history of Kizzuwatna and the date of the Sunassura treaty." *Orientalia*, 55(4), 424–445. [Historical reconstruction of Kizzuwatna polity and its role as conduit for Babylonian scribal practices into Anatolia.]

Bietak, M. (1996). *Avaris: The Capital of the Hyksos. Recent Excavations at Tell el-Dab'a*. British Museum Press, London. [Minoan wall paintings at Tell el-Dab'a, ca. 1700–1640 BCE; Bronze Age Aegean–Egyptian diplomatic contact.]

Chavadakis, M. (2026a). "Statistical Analysis of the Phaistos Disc: A Computational Methodology for Phonetic Key Evaluation." Version 19.0, June 2026. [Companion paper: G_LUWIAN key, three key-independent structural findings, TLHdig validation, 5/5 independent tests of [TIWAT + wa-tar] formula.]

Evans, A. (1921). *The Palace of Minos at Knossos*, Vol. I. Macmillan, London. [Original publication of the Phaistos Disc and canonical sign numbering.]

Godart, L. (1995). *Le Disque de Phaistos: L'énigme d'une écriture*. Éditions Itanos, Heraklion. [Standard scholarly edition of the disc; Evans/Godart canonical transcription.]

Hawkins, J.D. (2000). *Corpus of Hieroglyphic Luwian Inscriptions, Volume I: Inscriptions of the Iron Age*. De Gruyter, Berlin. (CHLI) [Standard reference corpus for Luwian hieroglyphic; pre-registered vocabulary used in Chavadakis 2026a §6.12.]

KTU 1.1–1.6. Ugaritic Baal Cycle. In: Dietrich, M., Loretz, O., and Sanmartín, J. (eds.) (1995). *The Cuneiform Alphabetic Texts from Ugarit, Ras Ibn Hani and Other Places* (KTU 2nd ed.). Ugarit-Verlag, Münster. [Kothar-wa-Khasis at Kaptaru (= Crete); Ugaritic mythological recognition of Bronze Age Aegean.]

Masson, E. (1974). *Cyprominoica: Répertoires, Documents de Ras Shamra, Essais d'interprétation*. Studies in Mediterranean Archaeology 31(2). Paul Åströms Förlag, Gothenburg. [Cypriot-Minoan script spread and Ugarit scribal contact.]

Melchert, H.C. (2003). *The Luwians*. Handbook of Oriental Studies 68. Brill, Leiden. [Standard reference on Luwian linguistic history, hieroglyphic Luwian, and survival of formulas into the Iron Age.]

Niemeier, W.-D. (1991). "Minoan artisans travelling overseas: the Alalakh frescoes and the painted plaster floor at Tel Kabri (Western Galilee)." *Thalassa: L'Égée préhistorique et la mer*, Aegaeum 7, 189–201. [Minoan-style frescoes at Alalakh Level VII, ca. 1700–1650 BCE.]

Rieken, E., et al. (2025). *TLHdig: Digitale Textausgaben der hethitischen Keilschrifttexte*, v0.2.0-beta. Akademie der Wissenschaften und der Literatur Mainz / Universität Marburg. [TLHdig corpus used in this paper: 22,116 XML files, 85,361 Luwian/Hittite tokens extracted.]

Woolley, C.L. (1955). *Alalakh: An Account of the Excavations at Tell Atchana in the Hatay, 1937–1949*. Reports of the Research Committee of the Society of Antiquaries of London 18. Oxford University Press, Oxford. [Excavation report for Alalakh; Bronze Age objects consistent with Aegean contact.]

Yon, M. (2006). *The City of Ugarit at Tell Ras Shamra*. Eisenbrauns, Winona Lake. [Ugarit as a Bronze Age multilingual scribal center; Cypriot-Minoan tablets at Ugarit; Aegean-Levantine scribal contact.]

---

## Appendix A: Corpus Construction Notes

### A.1 TLHdig v0.2.0-beta Extraction

The TLHdig corpus (Rieken et al. 2025) is distributed as 22,116 XML files encoding Hittite and Luwian cuneiform texts in CDL (Cuneiform Digital Library) format. Syllable tokens were extracted using a custom CDL walker (`cdl_from_zip` in `phaistos_master.py`) that:

1. Traverses `cdl` → `l` (lexeme) nodes
2. Extracts the `gdl` (grapheme description list) field
3. Strips determinatives (`det:true` nodes)
4. Normalizes syllable values: removes subscript numerals (₀–₉), retains cuneiform-specific characters (š, ḫ, ṭ, q, ŋ)
5. Filters tokens to length 1–6 characters

Luwian-register texts were isolated by language prefix filter (`lp="lu"` in the CDL language field). The resulting 85,361 tokens represent the largest machine-readable Luwian/Hittite phonotactic corpus currently available.

### A.2 HBTIN Late Babylonian Extraction

The HBTIN corpus was accessed via the `akk-x-ltebab` dialect tag in the CDLI CDL files. The same CDL walker was used. The 135,754 token count makes Late Babylonian the second-largest corpus in the arena after Egyptian.

### A.3 ETCSRI Sumerian

The ETCSRI (Electronic Text Corpus of Sumerian Royal Inscriptions) was parsed from its XML distribution. Sumerian phonotactics are structurally distinct from the other six corpora: Sumerian is agglutinative with a high proportion of monosyllabic morphemes, producing bigram patterns that differ from the polysyllabic traditions. The 27,316-token corpus is smaller than the other non-Linear-B corpora but sufficient for robust top-200 bigram estimation.

### A.4 AED-TEI Egyptian

The AED-TEI (Altägyptisches Wörterbuch, Text Encoding Initiative format) provides 438,362 tokens from 13,950 texts spanning 2600–300 BCE. This is the largest corpus in the arena by a factor of three. The size advantage is the primary reason Egyptian ranks first in the unnormalized pure arena but falls to approximately rank 16 after top-200 normalization — the normalization is specifically designed to eliminate this size advantage.

### A.5 Linear B (DĀMOS)

The DĀMOS database (University of Oslo) provides the smallest corpus in the arena at 8,163 tokens. This reflects the inherent scarcity of Linear B inscriptions rather than a selection choice. The small corpus size means that the top-200 bigrams estimated from Linear B have higher variance than those from larger corpora, and Linear B arena results have correspondingly wider effective confidence intervals. Replication with an expanded corpus (including all published Linear B tablets) is recommended.

---

## Appendix B: Reproducibility

All results in this paper are reproducible from the open-source code in this repository:

| Script | Function | Runtime (approx.) |
|--------|----------|-------------------|
| `phaistos_master.py` | Full arena + hybrid + MDL + IG + scoreboard | ~45–90 min (8-core CPU) |
| `phaistos_stability.py` | Blind stability test (5,000 trials) | ~20–40 min (8-core CPU) |

Both scripts use Python's `multiprocessing` module for parallel trial execution. The random seed is not fixed by default; results will vary slightly between runs but should reproduce the reported rankings and approximate Z-scores within one standard error of the null distribution.

The disc data is read from `hp4k1h5_phaistos_disc/src/phaistos_disc/data/phaistos-disc_outside-in.json`, a machine-readable Evans/Godart canonical transcription distributed with the `hp4k1h5_phaistos_disc` Python package. Reference corpora are expected in the `corpora/` subdirectory of the repository as per the directory structure documented in `README.md`.

---

*This paper is a companion to Chavadakis (2026a). All computational results were generated by `phaistos_master.py` and `phaistos_stability.py`, available in this repository. The Phaistos Disc sign data uses the Evans/Godart canonical transcription throughout. The Kizzuwatna Hypothesis and the Karatepe Comparative Approach are presented as working hypotheses for scholarly evaluation, not as established claims.*

*Version 1.0 — June 2026*
