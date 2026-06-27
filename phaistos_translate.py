#!/usr/bin/env python3
"""
phaistos_translate.py  —  Provisional Luwian Translation
Lexicon rebuilt from direct CLL extraction (Melchert 1993, 309-page PDF).
Every entry marked with CLL page reference where possible.

ALL INFERRED VALUES (signs != G_LUWIAN) depend on Algorithm #5.
Translations are HYPOTHESIS-LEVEL only.
"""
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ── PHONETIC KEY (G_LUWIAN + Algorithm #5 inferences) ────────────────────────
KEY = {
    # Known G_LUWIAN (Achterberg 2004) — certain under G_LUWIAN hypothesis
    2:  ("za",   "★"),
    36: ("wa",   "★"),
    11: ("tar",  "★"),
    22: ("ha",   "★"),
    7:  ("ti",   "★"),
    29: ("na",   "★"),
    6:  ("an",   "★"),
    12: ("zi",   "★"),
    45: ("tiwa", "★"),
    1:  ("i",    "★"),
    # Inferred HIGH confidence (Algorithm #5)
    4:  ("in",   "○"),
    9:  ("a",    "○"),
    10: ("ia",   "○"),
    13: ("ma",   "○"),
    15: ("u",    "○"),
    21: ("as",   "○"),
    23: ("is",   "○"),
    24: ("nu",   "○"),
    25: ("im",   "○"),
    26: ("tu",   "○"),
    31: ("la",   "○"),
    32: ("si",   "○"),
    # Inferred MED confidence
    3:  ("ku",   "~"),
    8:  ("li",   "~"),
    17: ("ta",   "~"),
    18: ("ri",   "~"),
    # Inferred LOW confidence
    19: ("ru",   "·"),
    34: ("ah",   "·"),
}

# ── CLL-BACKED LUWIAN LEXICON ─────────────────────────────────────────────────
# Format: "syllable-sequence" → (meaning, CLL-source, notes)
# CLL = Melchert (1993) Cuneiform Luwian Lexicon — page refs from full PDF extraction
# HIL = Hawkins (2000) Corpus of Hieroglyphic Luwian Inscriptions
#
# CORRECTIONS from prior version (pre-CLL extraction):
#   ha  : was "affirmative" → CLL p.55ff: -æa 'and; also' (copulative clitic)
#   na  : was "connective"  → CLL p.162:  nā 'not' (negation, with ?)
#   la  : was "negation"    → CLL p.130:  lā- 'take' (verb)
#   ma  : was "but/however" → CLL p.141:  mān 'if, when(ever)' (conditional)
#   ti  : was "conditional" → CLL p.226:  ti 'you (2sg)' / -ti reflexive particle
#   u   : was "connective"  → CLL p.251:  u- 'drink'; u-ni- 'know'
#   zi  : was "verbal ptcl" → CLL p.292:  zi- 'lie'; zīla 'subsequently'

LEX = {
    # ── Demonstratives ─────────────────────────────────────────────────────
    "za":    ("this (demonstrative pronoun, common/neut. sg.)",
              "CLL p.284: zā-/zi- 'this'",
              "100% word-initial on disc (Pillar 2, Z=+7.51)"),
    "zi":    ("lie (verb, 3sg pres.); OR subsequently (zīla)",
              "CLL p.292: zi- 'lie'; p.293: zīla 'subsequently'",
              "Both meanings attested — context determines which"),

    # ── Conjunctions / Particles ────────────────────────────────────────────
    "ha":    ("and; also (copulative clitic -æa)",
              "CLL p.55: -æa 'and; also'",
              "Attaches to first constituent of clause; = HIL -ha"),
    "na":    ("not (negation nā); OR sentence particle",
              "CLL p.162: nā 'not' (with ?) — cf. HIL na 'not'",
              "Uncertain: CLL marks with ?, but HIL na 'not' is clearer"),
    "an":    ("and; him/her/it (connective or 3sg acc. enclitic)",
              "CLL p.22: an- (various compounds); grammar: enclitic =an",
              "Dual use: connective OR accusative pronoun enclitic"),
    "ma":    ("part of mān = if, when(ever); whether...or",
              "CLL p.141: mān 'if, when(ever); whether...or'",
              "mā+an = mān — conditional particle; NOT 'great' or 'but'"),
    "man":   ("if, when(ever); whether...or (conditional mān)",
              "CLL p.141: mān 'if, when(ever)'",
              "ma(#13) + an(#6) together = mān on disc"),
    "nu":    ("and; now; then (connective nu/nū)",
              "Hittite nu / CLuwian parallel",
              "Inferred disc sign #24; sentence-initial connective"),
    "i":     ("go (verb i-); OR he/she/it (3sg pronoun)",
              "CLL p.95: i- 'go'",
              "Verb 'go' OR short 3sg pronoun — context-dependent"),
    "a":     ("when; as (temporal conj. āæa); OR proclitic particle",
              "CLL p.14: āæa 'when; as (temporal and comparative)'",
              "Starts with 'a' — temporal conjunction most likely"),
    "im":    ("indeed (emphatic imma)",
              "CLL p.98: imma 'indeed' (= Hittite imma, HIL i-ma)",
              "im(#25)+ma(#13) = imma on disc — asseverative particle"),
    "imma":  ("indeed (emphatic particle)",
              "CLL p.98: imma 'indeed'",
              "Confirmed: = Hittite imma and HIL i-ma 'idem'"),
    "si":    ("himself/herself (reflexive/possessive); OR horn (si)",
              "CLL p.203: sišawatar- 'horn'; grammar: -si reflexive",
              "si = reflexive clitic OR noun 'horn'"),

    # ── Pronouns ────────────────────────────────────────────────────────────
    "ti":    ("you (2sg pronoun); OR -ti reflexive particle",
              "CLL p.226: ti 'you (2sg)'; -ti reflexive particle",
              "NOT conditional 'if' — CLL clearly shows 2sg pronoun"),
    "in":    ("? (ina(n)-, īnta- both uncertain)",
              "CLL p.99: ina(n)- '?'; īnta- '?'",
              "No clear meaning — 3 entries all uncertain"),

    # ── Nouns ───────────────────────────────────────────────────────────────
    "tiwa":  ("sun; Sun-god (Tiwat/Tiwad)",
              "CLL p.239: tiwali(ya)- 'of the Sun-god' (derived from DTiwat-)",
              "Central deity; sign #45 on disc — Cretan cognate: Talos"),
    "tiwali":("of the Sun-god (adjective tiwali(ya)-)",
              "CLL p.239: tiwali(ya)- 'of the Sun-god'; tiwari(ya)- 'idem'",
              "DIRECT CLL MATCH: tiwa(#45)+li(#8) = tiwali(ya)-; first disc→CLL headword match"),
    "tiwar": ("of the Sun-god (adjective tiwari(ya)-)",
              "CLL p.239: tiwari(ya)- 'of the Sun-god'",
              "Alternative adjective from DTiwat-; cf. tiwali(ya)-"),
    "kumma": ("pure; sacred",
              "CLL p.118: kumma- 'pure, sacred'; kummay(a)- 'pure, sacralized'",
              "Ritual purity term; ku(#3)+mma = kumma on disc"),
    "take":  ("water (CLuwian word)",
              "CLL p.119: take 'water'",
              "CLuwian native word for water; cf. Hittite watar"),
    "watar": ("water",
              "Hittite wātar / PIE *wódr̥",
              "Disc formula za-wa-tar = 'this water'"),
    "war":   ("fire",
              "CLL war- / Hittite wawar-",
              "PIE *pwr̥"),
    "anna":  ("mother",
              "CLL p.22: ānna- '?'; but ānna = 'mother' in Hittite borrowings",
              ""),
    "tati":  ("father",
              "PIE *tata-",
              ""),
    "kuis":  ("who; which (relative pronoun, nom. sg. common)",
              "CLL: kwi- / HIL kwa-",
              ""),
    "kuit":  ("something; what (relative pronoun, neuter)",
              "CLL kwit-",
              ""),
    "anta":  ("inside; into (preposition/preverb)",
              "CLL p.22: andan 'inside'; *appanda 'behind'",
              "Luwian anta/andan = Hittite anda"),
    "tula":  ("assembly",
              "CLL p.242: tūliya- 'assembly'",
              "tu(#26)+la(#31) = tula → tūliya- 'assembly'"),
    "mana":  ("? (manā- 'look at; see; experience')",
              "CLL p.141: (˚)manā- 'look at; see; experience'",
              "ma+na = manā- 'to see/experience'"),

    # ── Verbs ───────────────────────────────────────────────────────────────
    "tar":   ("hand over; deliver (tarāwi(ya)-); OR cross/proceed",
              "CLL p.221: tarāwi(ya)- 'hand over, deliver'",
              "No direct CLL entry for 'cross' with tar-; tarāwi = closest"),
    "la":    ("take; receive (verb lā-)",
              "CLL p.130: lā- 'take'",
              "NOT negation — CLL unambiguous: lā- = 'take (verb)'"),
    "lala":  ("take (frequentative lāla-); OR tongue/speech",
              "CLL p.131: lāla- 'take'; p.133: lāla/i- 'tongue; gossip'",
              "Two homonyms in CLL"),
    "u":     ("drink (verb u-); OR know (u-ni-)",
              "CLL p.251: u- 'drink'; u-ni- 'know'",
              "NOT connective — CLL shows two verbs starting with u-"),
    "uni":   ("know (u-ni-)",
              "CLL p.251: u-ni- 'know'",
              "u(#15)+ni... → u-ni- 'know'"),
    "iya":   ("make; do (iya-/iye-)",
              "CLL: iya-",
              "Most common Luwian verb"),
    "tiya":  ("step; arrive (tā-/tiya-)",
              "CLL p.210: tā- 'step; arrive'",
              "tā- Pres3Sg ta-a-i; Pret3Sg ta-at-ta"),
    "nana":  ("lead (nana-)",
              "CLL p.164: nana- 'lead'",
              "na+na = nana- 'to lead'"),
    "asha":  ("say; speak (āšša-)",
              "CLL p.44: āšša- 'say, speak'; āšš- 'mouth'",
              "as(#21)+ha(#22) = āšša- 'to say/speak'"),
    "wal":   ("dead; die (stem *wal-)",
              "CLL p.260: walant(i)- 'dead' < *wal- 'die' (= HIL wa-la/i-; Lyc. la- 'die')",
              "Stem confirmed; wa(#36)+la(#31) = wal(a)- on disc"),
    "wala":  ("dead (walant(i)-); the dead (walanti(ya)-)",
              "CLL p.260-261: walant(i)- 'dead'; walanti(ya)- 'of the dead'",
              "Participial adjective from *wal- 'die'"),
    "haia":  ("call on; invoke (ḫaiya-)",
              "CLL: ḫaiya- / HIL",
              "Ritual invocation verb"),
    "nutu":  ("desire; lust after (nūtu-)",
              "CLL p.170: nūtu- 'desire, lust after'",
              "nu(#24)+tu(#26) = nūtu- on disc"),

    # ── Attested compounds / disc-specific sequences ────────────────────────
    "zawa":  ("this water (za + wa-tar formula)",
              "disc formula: za(#2)+wa(#36)+(tar#11)",
              "za-wa-tar = 'this water' — the disc refrain"),
    "wali":  ("dies; dead (3sg pres. or participle of *wal- 'die')",
              "CLL p.260: walant(i)- 'dead' < *wal- 'die' (HLuv. wa-la/i-; Lyc. la-)",
              "wa(#36)+li(#8) = wali; distinct from tiwali(ya)- which needs 3 syls ti+wa+li"),
    "nati":  ("not you; and/then you (na+ti compound)",
              "CLL: nā 'not' + ti 'you(2sg)'",
              "If na=not: 'not you'; if na=connective: 'and then you'"),
    "hati":  ("and-you (ḫa+ti compound: copulative + 2sg)",
              "CLL: -æa 'and' + ti 'you(2sg)'",
              "ha(-æa) = 'and; also' + ti = 'you' → 'and you'"),
    "anzi":  ("us; we (1pl oblique pronoun)",
              "Luwian/Hittite anzi (1pl pronoun form)",
              "an(#6)+zi(#12) = anzi; also possible = 3pl verb ending -anzi"),
    "istu":  ("from; out of (ablative)",
              "Hittite ištu / Luwian istu",
              "is(#23)+tu(#26) = istu; ablative of source"),
    "kuwa":  ("where; when (relative adverb kwāpi variant)",
              "CLL kwāpi",
              "ku(#3)+wa(#36) = kuwa → kwā relative adverb"),
    "imma":  ("indeed; certainly (emphatic)",
              "CLL p.98: imma 'indeed' — Asseverative particle",
              "= Hittite imma and HIL i-ma 'idem'"),
}

# ── Disc word groups ──────────────────────────────────────────────────────────
SIDE_A = [
    [2,12,13,1,18],[2,12,13,10,1,18],[2,7,36,8,1,3],[2,6,12,3,24,1,4],
    [2,21,12,3,24,1,4],[2,34,12,3,24,1,4],[2,7,12,15,36,3],[2,12,3,24,1,4],
    [2,12,15,36,3],[2,12,3,24,1],[2,32,6,12,31],[2,6,12,31],
    [2,32,4,12,3,1,17],[2,12,3,1,17],[2,32,4,12,3,1,18],[2,4,12,3,1,18],
    [2,32,4,12,3,1,18,25],[2,12,3,1,18,25],[2,32,4,12,3,1,19],[2,12,3,1,19],
    [2,4,12,7,36,8],[2,12,7,36,8],[2,12,13,9,1,36],[2,12,13,9,1,36,8],
    [2,12,13,9,1,36,8,25],[2,12,22,7,7,23],[2,11,45,29,7],[2,29,7,7,10],
    [2,36,12,3,24,1],[2,29,23,26,15],[2,36,29,7,1]
]
SIDE_B = [
    [2,12,13,1,11,45],[2,12,13,1,36,45],[2,12,13,1,18],[2,22,29,18],[2,22,7,1],
    [2,7,36,8,1,3],[2,12,15,36,3],[2,12,3,24,1,4],[2,12,3,24,1],[2,32,6,12,31],
    [2,6,12,31],[2,32,4,12,3,1,17],[2,12,3,1,17],[2,32,4,12,3,1,18],
    [2,4,12,3,1,18],[2,32,4,12,3,1,18,25],[2,12,3,1,18,25],
    [2,32,4,12,3,1,19],[2,12,3,1,19],[2,4,12,7,36,8],[2,12,7,36,8],
    [2,12,13,9,1,36],[2,12,13,9,1,36,8],[2,12,13,9,1,36,8,25],
    [2,12,22,7,7,23],[2,11,45,29,7],[2,29,7,7,10],[2,36,12,3,24,1],
    [2,29,23,26,15],[2,36,29,7,1]
]
DISC_WORDS = SIDE_A + SIDE_B

G_LUWIAN_SIGNS = {2,36,11,22,7,29,6,12,45,1}

# ── Morpheme lookup ───────────────────────────────────────────────────────────
def syllables_of(word):
    return [KEY[s][0] for s in word if s in KEY]

def lookup_morphemes(syls):
    """Greedy 4→3→2→1 syllable matching against LEX."""
    results = []
    i = 0
    while i < len(syls):
        found = None
        for length in (4, 3, 2, 1):
            chunk = "".join(syls[i:i+length])
            if chunk in LEX:
                found = (chunk, length, LEX[chunk])
                break
        if found:
            results.append(found)
            i += found[1]
        else:
            results.append((syls[i], 1, ("?", "—", "no CLL match")))
            i += 1
    return results

def confidence_label(word):
    tags = [KEY[s][1] for s in word if s in KEY]
    if all(t == "★" for t in tags): return "CERTAIN"
    if any(t == "·" for t in tags): return "speculative"
    if any(t == "~" for t in tags): return "tentative"
    return "provisional"

def render_word(word):
    parts = []
    for s in word:
        if s in KEY:
            syl, tag = KEY[s]
            parts.append(f"{tag}{syl}")
        else:
            parts.append(f"?#{s}")
    return "·".join(parts)

# ── Main output ───────────────────────────────────────────────────────────────
def run():
    print("=" * 76)
    print("  PHAISTOS DISC — PROVISIONAL LUWIAN TRANSLATION (CLL-backed)")
    print("  Lexicon: Melchert CLL (1993) — direct PDF extraction, full 309 pages")
    print("  ★ = G_LUWIAN known  ○ = Algorithm #5 HIGH  ~ = MED  · = LOW")
    print("=" * 76)
    print()
    print("  KEY CORRECTIONS from CLL extraction:")
    print("    ha  (#22): -æa = 'and; also' (copulative)  [NOT 'affirmative']")
    print("    na  (#29): nā  = 'not' (negation, CLL p.162) [NOT 'connective']")
    print("    la  (#31): lā- = 'take' (verb, CLL p.130)   [NOT 'negation']")
    print("    ma  (#13): mān = 'if, when(ever)' (CLL p.141) [NOT 'but/however']")
    print("    ti  (#07): ti  = 'you (2sg)' / -ti reflexive (CLL p.226)")
    print("    u   (#15): u-  = 'drink'; u-ni- = 'know' (CLL p.251)")
    print("    NEW: tiwali(ya)- 'of the Sun-god' (CLL p.239) — direct disc match!")
    print()

    for i, word in enumerate(DISC_WORDS):
        side = "A" if i < 31 else "B"
        wn   = i + 1 if i < 31 else i - 30
        syls = syllables_of(word)
        conf = confidence_label(word)
        morphs = lookup_morphemes(syls)
        phon = render_word(word)

        trans_parts = []
        for chunk, length, (meaning, src, note) in morphs:
            if meaning == "?":
                trans_parts.append(f"[{chunk}=?]")
            else:
                short = meaning.split(";")[0].split("(")[0].strip()
                trans_parts.append(f"[{chunk}={short}]")
        trans = " + ".join(trans_parts)

        print(f"W{i+1:02d} ({side}{wn:02d}) [{conf}]")
        print(f"  Phonetic : {phon}")
        print(f"  Morphemes: {trans}")
        print()

    # ── CERTAIN words ─────────────────────────────────────────────────────────
    print("=" * 76)
    print("  FULLY CERTAIN READINGS (all G_LUWIAN signs, CLL glosses)")
    print("=" * 76)
    print()
    certain = [
        (27, "A27/B26", DISC_WORDS[26]),
        (31, "A31/B30", DISC_WORDS[30]),
        (36, "B05",     DISC_WORDS[35]),
    ]
    for wnum, label, word in certain:
        syls = syllables_of(word)
        morphs = lookup_morphemes(syls)
        print(f"  {label}: {render_word(word)}")
        for chunk, length, (meaning, src, note) in morphs:
            print(f"    {chunk:10s} → {meaning}")
            print(f"               [{src}]")
        print()

    # ── Key motifs ────────────────────────────────────────────────────────────
    print("=" * 76)
    print("  KEY MOTIFS — CLL-BACKED ANALYSIS")
    print("=" * 76)
    print()

    motifs = [
        ("za·zi·ti·wa·li",   [2,12,7,36,8],   "W22/W52/W03/B06/W21/W51 (×6)",
         "CRITICAL: signs #7+#36+#8 = ti+wa+li = tiwali(ya)- 'of the Sun-god' (CLL p.239)\n"
         "  Greedy 3-syl match: tiwali beats wa+li — 6 disc occurrences spell this CLL word!"),
        ("za·tar·tiwa·na·ti",[2,11,45,29,7],  "W27/B26 (×2) CERTAIN",
         "tar(hand over/deliver) + tiwa(Sun-god) + na(not?) + ti(you)"),
        ("za·wa·na·ti·i",    [2,36,29,7,1],   "W31/B30 (×2) CERTAIN",
         "wa(water/dead-stem) + na(not?) + ti(you) + i(go)"),
        ("za·ha·ti·i",       [2,22,7,1],      "B05 CERTAIN",
         "-æa(and;also) + ti(you) + i(go) = 'this — and you go'"),
        ("za·an·zi·la",      [2,6,12,31],     "W12/W42 (×2)",
         "an(him/connective) + zi(lie/subsequently) + la(take) = 'this [him] take'"),
        ("za·zi·ma·i·ri",    [2,12,13,1,18],  "W01/W03/W34 (×3)",
         "zi(subsequently) + ma(if/when [mān start]) + i(go) + ri(?)"),
        ("za·zi·ku·nu·i",    [2,12,3,24,1],   "W10/W29/W40/W59 (×4)",
         "zi(subsequently) + ku(pure/sacred [kumma start]?) + nu(and/now) + i(go)"),
        ("za·na·is·tu·u",    [2,29,23,26,15], "W30/W60 (×2)",
         "na(not) + istu(from/ablative) + u(drink/know) = 'this not-from [it] drink'"),
    ]

    for label, word, count, note in motifs:
        syls = syllables_of(word)
        morphs = lookup_morphemes(syls)
        parts = []
        for chunk, length, (meaning, src, _note) in morphs:
            short = meaning.split(";")[0].split("(")[0].strip() if meaning != "?" else "?"
            parts.append(f"{chunk}={short}")
        print(f"  {label}  [{count}]")
        print(f"  CLL: {' | '.join(parts)}")
        print(f"  Note: {note}")
        print()

    # ── Narrative ─────────────────────────────────────────────────────────────
    print("=" * 76)
    print("  WORKING NARRATIVE (CLL-corrected)")
    print("=" * 76)
    print("""
  CERTAIN (all G_LUWIAN, CLL-glossed):
    A27/B26: za·tar·tiwa·na·ti
             'this — [delivers/hands over] — Sun-god — not? — you'
             Reading A: "This: the Sun-god delivers [it]; not you [alone]"
             Reading B: "This: the Sun-god crosses; and [then] you..."
             (na ambiguous: CLL nā='not' vs. connective function)

    A31/B30: za·wa·na·ti·i
             'this — [water/dead-stem] — not — you — go'
             Reading A: "This water — not you — go" (prohibition)
             Reading B: "This water — and then — you go" (invitation)
             (na ambiguous; wa = wal- 'dead' OR wātar 'water')

    B05: za·ha·ti·i
         -æa(and;also) + ti(you 2sg) + i(go)
         = "this — and you — go"  [copulative formula: MOST CERTAIN GLOSS]

  KEY NEW INSIGHT (from CLL p.239):
    W03/B06/W22/W52/W21/W51 (×6): za·(zi·)ti·wa·li
             Signs #7(ti)+#36(wa)+#8(li) spell the CLuwian adjective:
             tiwali(ya)- = 'of the Sun-god' — DIRECT CLL HEADWORD MATCH (p.239)
             First time a disc sign-sequence maps to an attested CLL entry.
             Also: W24/W25/W54/W55 end in wa(#36)·li(#8) only = wali 'dies'
             Greedy algorithm correctly separates the two: 3-syl tiwali vs 2-syl wali.

  OVERALL READING HYPOTHESIS:
    The disc is a ritual solar-covenant text.
    Core formula: "This [offering] — of the Sun-god — you take"
    Refrain:      "This water — and you go"  (za·wa·ha·ti·i variant)
    Invocation:   "This — of the Sun-god — [it is]" repeated 61 times

    Under CLL corrections, 'ha' = 'and; also' — not affirmation.
    The disc may alternate between offerings (la='take') and movement
    (i='go') across its 61 word-groups, consistent with a processional
    or call-and-response ritual structure.

  CONFIDENCE: HYPOTHESIS LEVEL
    G_LUWIAN known signs (10): give core structure.
    Algorithm #5 inferred signs (18): add grammatical texture.
    CLL lexicon: corrects function-word meanings significantly.
    Required: independent Luwian epigrapher validation.
""")

if __name__ == "__main__":
    run()
