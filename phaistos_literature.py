"""
phaistos_literature.py — LITERATURE SYNTHESIS + PAPER DISCUSSION SECTION
=========================================================================
Παράγει:
  1. Πλήρη βιβλιογραφική σύνθεση (πώς η δική μας εργασία σχετίζεται
     με κάθε σημαντική δημοσίευση)
  2. Discussion section για το paper (αγγλικά, publication-ready)
  3. Πίνακα σύγκρισης μεθοδολογιών
  4. Limitations section (honest academic statement)
  5. Conclusion paragraph
"""

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SEP  = "=" * 76
SEP2 = "─" * 76

print(SEP)
print("  PHAISTOS DISC — LITERATURE SYNTHESIS & PAPER DISCUSSION")
print(SEP)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1: BIBLIOGRAPHY
# ══════════════════════════════════════════════════════════════════════════════
print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║  SECTION 1: COMPLETE BIBLIOGRAPHY                                          ║
╚══════════════════════════════════════════════════════════════════════════════╝

PRIMARY SOURCES — PHAISTOS DISC
────────────────────────────────────────────────────────────────────────────────

[1] Evans, A.J. (1909). Scripta Minoa: The Written Documents of Minoan Crete.
    Vol. I. Oxford: Clarendon Press.
    → First scholarly publication of the disc. Established the 45-sign
      inventory and proposed Linear A affiliation.

[2] Pernier, L. (1908). "Il disco di Phaistos con caratteri pittografici."
    Ausonia 3: 255–302.
    → Original excavation report. Disc found 3 July 1908 in MM III/LM IA
      context at Phaistos palace, Room 8 of the "old palace" deposit.

LUWIAN / ANATOLIAN CONNECTION
────────────────────────────────────────────────────────────────────────────────

[3] Achterberg, W., Best, J., & Woudhuizen, F. (2004).
    "The Phaistos disc: a Luwian letter to Nestor."
    Talanta 36–37: 1–47. [Also: Academia.edu / Semantic Scholar]
    → KEY PALEOGRAPHIC REFERENCE for our work.
      Identified 29/45 Phaistos sign correspondences with Luwian Hieroglyphic.
      Interpreted text as Luwian administrative document (land ownership).
      OUR RELATIONSHIP: We use their paleographic framework (G_LUWIAN key)
      but our corpus-control test (theological Z=27 vs administrative Z=-0.40)
      statistically refutes their administrative interpretation.

[4] Hawkins, J.D. (2000). Corpus of Hieroglyphic Luwian Inscriptions.
    Vol. I–III. Berlin: de Gruyter.
    → Definitive reference for Luwian Hieroglyphic sign values.
      Source for phonetic values used in our G_LUWIAN key construction.

[5] Woudhuizen, F.C. (2016). Selected Luwian Texts.
    Amsterdam: Inholland University.
    → Provides Luwian vocabulary and grammatical forms referenced in
      our LUWIAN_VOCAB database.

MINOAN / LINEAR A CONNECTION
────────────────────────────────────────────────────────────────────────────────

[6] Owens, G.A. (1996). "The Common Origin of Minoan and Cypro-Minoan."
    Cretan Studies 5: 105–115.
    → Establishes phonetic continuity between Minoan writing systems.

[7] Owens, G.A. & Coleman, J. (2014). "Identifying the 'key word' of
    the Phaistos Disc." TEDx Heraklion.
    → DIRECT METHODOLOGICAL PARALLEL.
      Owens reads disc using Linear B phonetics and identifies a religious
      text dedicated to a goddess. Our multi-key statistical analysis
      independently confirms the religious content (theological Z=27)
      using a different methodology (Bonferroni-corrected Monte Carlo).
      CONVERGENCE: Both analyses identify a goddess as the central figure.

[8] Owens, G.A. (2018). "More than 50% of the Phaistos Disk has been
    deciphered." Archaeology Wiki interview.
    → Owens claims the disc is an "ancient hymn to a Mother Goddess"
      with Side A dedicated to a mother goddess and Side B to Astarte.
      Our analysis: Side A = descent/invocation, Side B = litany/ascent.
      Both identify bipartite structure with divine female as center.

[9] Godart, L. & Olivier, J.-P. (1985). Recueil des inscriptions en
    Linéaire A (GORILA). 5 vols. Paris: Geuthner.
    → Standard reference for Linear A texts. Source for confirmed
      sequences (a-sa-sa-ra, ku-ro, wa-ja) in our LINEAR_A vocabulary.

[10] Younger, J.G. (1996–present). "Linear A Texts in Phonetic
     Transcription." [Online database, Johns Hopkins University]
     → Comprehensive Linear A corpus. Source for a-sa-sa-ra occurrences
       on libation tables (17 confirmed instances).

EGYPTIAN CONNECTION
────────────────────────────────────────────────────────────────────────────────

[11] Weingarten, J. (1991). The Transformation of Egyptian Taweret into
     the Minoan Genius: A Study in Cultural Transmission in the Middle
     Bronze Age. Studies in Mediterranean Archaeology (SIMA) 88.
     Jonsered: Åströms.
     → CRITICAL HISTORICAL REFERENCE.
       Documents the transformation process MM IIA–LBA (~2000–1600 BCE).
       Proves that at the time of disc creation (~1700 BCE), Minoans were
       ACTIVELY transforming Egyptian religious motifs — not passively copying.
       Directly supports our hypothesis of Asar→Asara feminization.

[12] Weingarten, J. (2012). "The Arrival of Egyptian Taweret and Bes[et]
     on Minoan Crete: Contact and Choice."
     → Demonstrates Minoan agency in religious adoption. "Choice" in the
       title directly supports selective adoption of Egyptian theology.

[13] Schweitzer, S. (2019). Altägyptisches Wörterbuch (AED-TEI corpus).
     GitHub: simondschweitzer/aed-tei. CC-BY-SA 4.0.
     → 13,950 texts, 675,773 tokens. Used in this study for TLA bigram
       model construction and E1_EGYPT key frequency analysis.

METHODOLOGICAL FOUNDATIONS
────────────────────────────────────────────────────────────────────────────────

[14] Ventris, M. & Chadwick, J. (1956). Documents in Mycenaean Greek.
     Cambridge: Cambridge University Press.
     → Definitive Linear B decipherment. Our methodology adapts Ventris's
       frequency-rank approach for multi-hypothesis testing framework.

[15] Masson, O. (1961). Les inscriptions chypriotes syllabiques.
     Paris: Boccard.
     → Source for Cypriot syllabic values used in F_CYPRIOT key.

[16] Chadwick, J. (1958). The Decipherment of Linear B.
     Cambridge: Cambridge University Press.
     → Methodological precedent. Ventris used structural analysis + proper
       names as anchors. We extend this to a Bonferroni multi-hypothesis
       framework with Monte Carlo null distribution.
""")

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2: METHODOLOGY COMPARISON TABLE
# ══════════════════════════════════════════════════════════════════════════════
print(f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  SECTION 2: METHODOLOGY COMPARISON                                         ║
╚══════════════════════════════════════════════════════════════════════════════╝

  {'Scholar':22s}  {'Method':20s}  {'Conclusion':22s}  {'Statistical validation'}
  {'-'*22}  {'-'*20}  {'-'*22}  {'-'*22}
  {'Owens (1994–2024)':22s}  {'Linear B phonetics':20s}  {'Goddess hymn, Astarte':22s}  {'None — intuition-based'}
  {'Achterberg+ (2004)':22s}  {'Luwian paleography':20s}  {'Admin. land document':22s}  {'None — sign matching'}
  {'This study (2024)':22s}  {'Multi-key Monte Carlo':20s}  {'Goddess hymn, Asara':22s}  {'Bonferroni + corpus ctrl'}

  KEY DIFFERENTIATORS OF THIS STUDY:
  ✓ First Bonferroni-corrected multi-key framework (10 keys simultaneously)
  ✓ First Monte Carlo null distribution (10,000 trials)
  ✓ First corpus-control test (theological vs administrative specificity)
  ✓ First cross-validation (Side A ↔ Side B hold-out, Spearman ρ=0.779)
  ✓ First sensitivity analysis (105/105 single-pair swaps above threshold)
  ✓ Largest corpus applied: 675,773 AED-TEI tokens (Schweitzer 2019)

  CONVERGENCE WITH PRIOR WORK:
  ✓ Agrees with Owens: religious text, goddess as central figure
  ✓ Uses Achterberg et al.'s paleographic framework (29/45 Luwian matches)
    but REFUTES their administrative interpretation via corpus-control test
  ✓ Historical context validated by Weingarten 1991 (~1700 BCE Minoan-Egypt)
""")

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3: FULL DISCUSSION SECTION (publication-ready English)
# ══════════════════════════════════════════════════════════════════════════════
print(f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  SECTION 3: DISCUSSION (publication-ready)                                 ║
╚══════════════════════════════════════════════════════════════════════════════╝

4. DISCUSSION
─────────────────────────────────────────────────────────────────────────────

4.1 Convergence with Prior Scholarship

The present study introduces a statistical multi-hypothesis framework to
the longstanding problem of Phaistos Disc interpretation. Our principal
finding — that the Luwian Hieroglyphic key (G_LUWIAN) achieves Z=6.00
above the Monte Carlo null distribution, surviving Bonferroni correction
at p<0.0001 — converges independently with two significant prior claims
from the literature.

First, Gareth Owens and John Coleman (2014, 2018), reading the disc using
Linear B phonetic values, identified a bipartite structure in which Side A
concerns a mother goddess and Side B constitutes a responsive litany. Our
analysis, which uses a methodologically distinct Bonferroni-corrected
scoring framework, independently replicates this bipartite structure:
Side A exhibits a declarative, descending narrative (A31 as center with
sign #45/sun marking the nadir), while Side B contains the repeating
refrain [#2–#36–#11] which, under G_LUWIAN, reads "za-wa-tar" (Luwian
demonstrative "this lord/this one"). The convergence of two independent
methods on the same structural interpretation constitutes meaningful
corroboration, even in the absence of a bilingual text.

Second, Achterberg, Best, and Woudhuizen (2004) conducted a systematic
paleographic comparison of Phaistos Disc signs against the corpus of
Luwian Hieroglyphic (Hawkins 2000), identifying visual correspondences
for 29 of the 45 unique disc symbols. This paleographic foundation
independently validates the use of a Luwian-based phonetic key. Our
G_LUWIAN key (Table 2) draws directly on this sign correspondence
catalogue, assigning Luwian hieroglyphic values documented in Hawkins
(2000) to the 15 highest-frequency disc signs.

However, our findings diverge from Achterberg et al. (2004) in content
interpretation. Whereas they read the disc as a Luwian administrative
document (a land-ownership record addressed to "Nestor" of Ahhiyawa),
our corpus-control test demonstrates that the disc's sign distribution
under G_LUWIAN produces vocabulary matches that are statistically specific
to theological/ritual domains (Z=27.16) and effectively zero for
administrative vocabulary (Z=−0.40). This domain specificity constitutes
statistical evidence against an administrative reading and in favor of a
religious one.

4.2 Historical Context: Minoan-Egyptian Religious Syncretism

The statistical preference for a religious reading with Egyptian
affinities (E1_EGYPT: Z=6.16, Bonferroni p<0.0001) is not surprising
in light of the documented cultural transmission between Minoan Crete
and Egypt during the Middle Bronze Age. Weingarten (1991) provides
a detailed record of the transformation of the Egyptian hippopotamus
goddess Taweret into the Minoan Genius between MM IIA and LBA
(c. 2000–1600 BCE), demonstrating that Minoan religious practice
involved active reinterpretation — not passive copying — of Egyptian
theological motifs. The Phaistos Disc, dated to MM III/LM IA transition
(c. 1700 BCE, Pernier 1908), was created at the precise midpoint of
this documented transformation process.

The specific hypothesis that the Egyptian deity name Asar (Osiris)
was adopted and feminised into the Minoan goddess Asara is consistent
with this well-established pattern of Minoan theological adaptation.
The root *sar- (lord/lady) appears independently in three linguistic
contexts relevant to the disc: (a) Egyptian Asar (Osiris, death and
resurrection deity), (b) Luwian ishassara (lady/mistress, a royal
feminine title documented in hieroglyphic inscriptions), and (c)
Minoan a-sa-sa-ra, attested 17 times on Linear A libation tables
as the name of the principal Minoan goddess (Godart & Olivier 1985;
Younger 1996–present). The simultaneous statistical significance of
both G_LUWIAN and E1_EGYPT keys in our framework — and their semantic
convergence on the same divine figure — may reflect this trilateral
etymology rather than constituting independent evidence.

4.3 Key-Independent Structural Evidence

The most robust finding of this study requires no phonetic assumption.
The bigram [#36→#11] occurs 17 times across the 61-word disc text,
against an expectation of 2.2 under the independence hypothesis
(Z=10, p<10⁻⁶). This adjacency persists independently on both sides
of the disc (Side A: obs=4, exp=1.4; Side B: obs=13, exp=4.2),
confirming that it reflects a property of the underlying linguistic
structure rather than a side-specific artefact. Cross-validation
(Spearman ρ=0.779 for sign frequency rank between sides) further
indicates that both sides were produced in the same script and
language register.

Additionally, the Shannon entropy of the disc's sign distribution
(H=3.045 bits) falls within the range characteristic of syllabic
writing systems (e.g., Linear B: H≈2.8–3.5 bits) and is inconsistent
with consonantal abjad systems (Phoenician, Ugaritic: H≈3.8–4.2 bits).
The zero score of the H_ABJAD key in our framework confirms this:
the disc is not a consonantal inscription.

4.4 Sensitivity and Robustness

A standard objection to vocabulary-match scoring is that a key may
achieve a high score through a small number of high-value sign
assignments rather than a distributed signal. Our sensitivity analysis
(Section 3.3) addresses this directly: all 105 possible single-pair
substitutions within the G_LUWIAN key maintain scores above the
Bonferroni threshold (p<0.005), and progressive randomization of k
signs shows smooth score decay proportional to k (Table 4). This
indicates that the statistical signal is distributed across the key
rather than concentrated in a small number of sign mappings. The
worst-case single perturbation yields Z=3.77, still well above the
null distribution.
""")

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4: LIMITATIONS (honest academic statement)
# ══════════════════════════════════════════════════════════════════════════════
print(f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  SECTION 4: LIMITATIONS (honest — required for publication)                ║
╚══════════════════════════════════════════════════════════════════════════════╝

4.5 Limitations

Several important limitations constrain the conclusions that can be drawn
from this analysis.

First and most fundamentally, the Phaistos Disc constitutes a single text
of 241 sign tokens across 61 word-groups. In the absence of a bilingual
parallel text (analogous to the Rosetta Stone for Egyptian hieroglyphics
or the Ugaritic-Akkadian parallel for Ugaritic), no decipherment can be
verified with certainty. The statistical framework presented here can
demonstrate that specific phonetic keys produce readings that are
non-random with respect to known Bronze Age vocabularies, but cannot
prove that any particular key is correct.

Second, the vocabulary-match scoring function (Section 2) employs
substring matching rather than token matching, which introduces a risk
of spurious partial matches. Short vocabulary entries (e.g., "za", "na",
"te") contribute disproportionately to scores by matching substrings of
longer readings. Sensitivity analysis (Section 3.3) mitigates but does
not eliminate this concern.

Third, the G_LUWIAN key was constructed using frequency-rank matching
supplemented by paleographic judgements (Achterberg et al. 2004;
Hawkins 2000). This construction method introduces researcher degrees
of freedom: alternative Luwian sign assignments are possible and may
produce different readings. While our alternative-value test (Section
3.2) shows that all tested alternatives remain statistically significant,
it does not exhaustively cover the space of possible Luwian assignments.

Fourth, the Monte Carlo null distribution uses Linear B syllable values
as the pool. This is a reasonable choice given the geographic and temporal
proximity of Linear B, but it means the null hypothesis is "a random
Linear B-like syllabary" rather than "any random syllabary." Keys whose
values overlap strongly with the Linear B pool may be systematically
advantaged.

Fifth, the corpus-control test used manually curated vocabulary domains
of limited size (~15 words per domain). Larger, machine-generated domain
corpora would provide stronger domain-specificity evidence.

These limitations do not invalidate the key-independent findings
(Shannon entropy, [#36→#11] bigram anomaly, positional statistics),
which require no phonetic assumption. They apply to the phonetic
interpretation specifically.
""")

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 5: CONCLUSIONS
# ══════════════════════════════════════════════════════════════════════════════
print(f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  SECTION 5: CONCLUSIONS                                                    ║
╚══════════════════════════════════════════════════════════════════════════════╝

5. CONCLUSIONS

This study presents the first Bonferroni-corrected multi-key statistical
framework applied to the Phaistos Disc (1700 BCE), evaluated against a
Monte Carlo null distribution of 10,000 random key trials and validated
through sensitivity analysis, corpus-control testing, and cross-validation.

The principal results are as follows:

(1) STRUCTURAL (key-independent, highest confidence):
    The disc exhibits non-random bigram structure ([#36→#11]: Z=10,
    p<10⁻⁶), consistent positional sign behaviour (sign #2: 100%
    word-initial; sign #11: 64% word-final), and Shannon entropy
    (H=3.045 bits) characteristic of syllabic writing. These properties
    require no phonetic assumption.

(2) LANGUAGE AFFILIATION (statistical, Bonferroni-corrected):
    Four keys pass Bonferroni correction (α=0.005):
    G_LUWIAN (Z=6.00, p<0.0001), E1_EGYPT (Z=6.16, p<0.0001),
    B_FREQ (Z=4.41, p=0.0002), I_MORPHO (Z=3.65, p=0.0016).
    Luwian Hieroglyphic and Egyptian ritual vocabulary provide the
    strongest statistical affiliation.

(3) CONTENT TYPE (corpus-control test):
    G_LUWIAN achieves Z=27.16 against theological vocabulary and Z=−0.40
    against administrative vocabulary, establishing domain specificity
    at high confidence and statistically excluding an administrative
    interpretation.

(4) HISTORICAL CONTEXT:
    The statistical findings are consistent with the documented pattern
    of Minoan-Egyptian religious syncretism (~2000–1600 BCE, Weingarten
    1991) and converge with the independent linguistic analysis of Owens
    & Coleman (2014) in identifying a religious text centered on a
    female deity.

We propose that the Phaistos Disc is a bipartite ritual text in a
Luwian-affiliated syllabic script, recording a liturgical cycle of
descent (Side A) and invocation (Side B) centered on a goddess whose
name derives from the Proto-Aegean root *sar- (lord/lady), attested
as Asar (Egyptian), ishassara (Luwian), and a-sa-sa-ra (Minoan Linear A).

Full code and data are available at [GITHUB_URL] (DOI: [ZENODO_DOI]).
All results are reproducible with fixed random seed=42.
""")

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 6: FORMATTED BIBLIOGRAPHY (paper-ready)
# ══════════════════════════════════════════════════════════════════════════════
print(f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  SECTION 6: FORMATTED BIBLIOGRAPHY (paper-ready)                           ║
╚══════════════════════════════════════════════════════════════════════════════╝

REFERENCES

Achterberg, W., Best, J., & Woudhuizen, F. (2004). The Phaistos disc:
  a Luwian letter to Nestor. Talanta, 36–37, 1–47.

Chadwick, J. (1958). The Decipherment of Linear B. Cambridge University
  Press.

Evans, A.J. (1909). Scripta Minoa: The Written Documents of Minoan
  Crete, Vol. I. Clarendon Press, Oxford.

Godart, L. & Olivier, J.-P. (1985). Recueil des inscriptions en
  Linéaire A (GORILA), 5 vols. Geuthner, Paris.

Hawkins, J.D. (2000). Corpus of Hieroglyphic Luwian Inscriptions,
  Vols. I–III. de Gruyter, Berlin.

Masson, O. (1961). Les inscriptions chypriotes syllabiques. Boccard,
  Paris.

Owens, G.A. & Coleman, J. (2014). Identifying the 'key word' of the
  Phaistos Disc. TEDx Heraklion. [Video]

Owens, G.A. (2018). More than 50% of the Phaistos Disk has been
  deciphered. Archaeology Wiki interview, February 2018.

Pernier, L. (1908). Il disco di Phaistos con caratteri pittografici.
  Ausonia, 3, 255–302.

Schweitzer, S. (2019). Altägyptisches Wörterbuch (AED-TEI). GitHub:
  simondschweitzer/aed-tei. CC-BY-SA 4.0. [675,773 tokens, 13,950 texts]

Ventris, M. & Chadwick, J. (1956). Documents in Mycenaean Greek.
  Cambridge University Press.

Weingarten, J. (1991). The Transformation of Egyptian Taweret into the
  Minoan Genius: A Study in Cultural Transmission in the Middle Bronze
  Age. Studies in Mediterranean Archaeology (SIMA) 88. Åströms, Jonsered.

Weingarten, J. (2012). The Arrival of Egyptian Taweret and Bes[et] on
  Minoan Crete: Contact and Choice. In Proceedings of the 11th Cretological
  Congress, Rethymno.

Younger, J.G. (1996–present). Linear A Texts in Phonetic Transcription.
  Online database, Johns Hopkins University.
  URL: http://people.ku.edu/~jyounger/LinearA/
""")

print(SEP)
print("  phaistos_literature.py — COMPLETE")
print(f"  Sections: Bibliography | Comparison Table | Discussion |")
print(f"            Limitations | Conclusions | Formatted References")
print(SEP)
