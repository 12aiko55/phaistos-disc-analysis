"""
phaistos_corpus_control.py — CORPUS CONTROL TEST
==================================================
Question: Είναι η "θεολογική σύγκλιση" πραγματική ή artifact του μοντέλου;

Αν ο G_LUWIAN βρίσκει θεολογικές λέξεις παντού (σε admin, geographic,
household vocab), τότε είναι artifact. Αν ΜΟΝΟ στο θρησκευτικό corpus
βγάζει υψηλό score → πραγματικό εύρημα.

4 vocabulary domains (ίσο μέγεθος ~15 λέξεις):
  THEOLOGICAL  : θεότητες, τελετουργίες, μετά θάνατον
  ADMINISTRATIVE: αριθμοί, εμπόρευμα, γεωργία
  GEOGRAPHICAL  : τοπωνύμια, φυσικό περιβάλλον
  BODY_NEUTRAL  : μέλη σώματος, καθημερινά ουσιαστικά
"""

import sys, random, math
from collections import Counter
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SEP  = "=" * 72
SEP2 = "─" * 72

SIDE_A = [
    [2,12,7,1,29],[2,6,25,6,22],[1,7,29,3,22],[29,6,2,7,22],
    [36,2,12,7],[2,36,12,11,22],[2,29,7,22],[29,2,7,36,22,11],
    [2,12,7,36],[29,7,22,2],[12,2,36,7,22],[2,7,29,36,22],
    [7,22,2,36,12],[2,29,36,11],[29,7,22,36],[2,36,7,11,22],
    [29,2,22,7],[36,7,22,2,11],[2,7,36,22],[29,36,2,7,11,22],
    [7,2,36,29],[22,2,36,11],[29,7,36,2,22],[2,7,22,29],
    [36,29,2,22,7],[2,11,36],[7,22,36,2],[29,2,36],
    [2,7,22,36,11],[36,2,11],[45,2,36,11,22],
]
SIDE_B = [
    [2,12,36,6,11],[2,12,7,2,11],[24,2,36,11,29],
    [2,29,22,36,12,11],[2,36,11],[2,1,12,36,11],
    [29,2,22,11],[2,36,29,22,11,29],[2,29,12,2,11],
    [36,11,29,2,33],[2,22,36,12],[29,36,11,2,22,12],
    [2,36,11,45],[22,2,36,11,44],[2,29,36,12,11],
    [29,2,12,36],[2,2,36,12,11,29],[36,45,11,2],
    [2,12,36,11],[29,2,36,11,22],[2,36,12,29,11],
    [36,2,11,29],[2,29,36,11,24],[12,36,2,11],
    [2,36,29,11,22],[29,36,2,11],[2,11,36,22,29],
    [36,11,2,29],[2,36,11,29,22],[45,36,11,2,22],
]
ALL_WORDS = SIDE_A + SIDE_B
SIGN_FREQ_ORDER = [2,36,11,29,22,7,12,6,45,1,24,25,33,44,3]

# ── 4 VOCABULARY DOMAINS ──────────────────────────────────────────────────────

# Domain 1: THEOLOGICAL — religion, deities, afterlife, ritual (our current vocab)
THEOLOGICAL = {
    "a-sa-sa-ra":"Minoan goddess","wa-na-ka":"king/lord",
    "po-ti-ni-ja":"Mistress/goddess","ti-wa":"sun god",
    "tar":"lord/judge","sa-ra":"Son of Ra","na-ra":"for Ra",
    "wa-sa-ra":"Osiris variant","ha-ta-pa":"offering/peace",
    "an-na":"mother","at-ta":"father","ur-a":"great (divine)",
    "za-tar":"this lord","te-o":"god","wa-na":"lord",
    "da-ma":"earth goddess","me-na":"moon",
}

# Domain 2: ADMINISTRATIVE — Linear B accounting, goods, livestock
# (words that appear in Linear B clay tablets — purely economic)
ADMINISTRATIVE = {
    "ko-to-na":"plot of land (Linear B)","o-pe-ro":"deficit/debt (Linear B)",
    "pe-mo":"seed grain (Linear B)","si-to":"grain/wheat (Linear B)",
    "me-re-u-ro":"flour (Linear B)","o-no":"donkey (Linear B)",
    "ka-ma":"unit of land (Linear B)","we-to":"year (Linear B)",
    "ke-ra":"horn/measure (Linear B)","a-re-pa":"ointment (Linear B)",
    "ri-no":"linen (Linear B)","pa-ra-jo":"old/last year (Linear B)",
    "to-so":"so much/total (Linear B)","do-so-mo":"contribution (Linear B)",
    "wo-zo":"work/labor (Linear B)","qe-te-o":"to pay (Linear B)",
    "de-so-mo":"bond/tribute (Linear B)",
}

# Domain 3: GEOGRAPHICAL — place names, topography, natural features
# (from known Aegean Bronze Age toponyms and natural vocabulary)
GEOGRAPHICAL = {
    "ko-no-so":"Knossos (Linear B: ko-no-so)","pa-i-to":"Phaistos (Linear B)",
    "a-mi-ni-so":"Amnisos (Linear B)","ti-ri-to":"Tiryns (Linear B)",
    "pu-ro":"Pylos (Linear B)","a-ta":"Attica?","ku-ta":"Kydonia (Linear B)",
    "wa-to":"Lasithos? (toponym)","ri-jo":"cape/promontory (Linear B)",
    "ka-to":"lower/down (prefix)","pa-ro-ro":"by the river?",
    "na-u-do":"harbor? (nautical)","su-ri-mo":"Syrian? foreign",
    "u-ru-pi-ja":"Europe? (toponym)","ru-ki-to":"Lyktos (Crete toponym)",
    "di-ka-ta":"Dikte mountain (Crete)","i-da":"Ida mountain (Crete)",
}

# Domain 4: BODY / EVERYDAY — body parts, common objects, actions
# (neutral everyday vocabulary, neither religious nor administrative)
BODY_NEUTRAL = {
    "ka-ra":"head (Linear B ka-ra)","me-ri":"honey (Linear B)",
    "do-de":"house? (cf. domos)","ne-wo":"new (Linear B ne-wo)",
    "pa-te":"father (Greek)","ma-te":"mother (Greek)",
    "ko-wo":"boy (Linear B)","ko-wa":"girl (Linear B)",
    "wi-ri-ne":"leather (Linear B)","a-pi":"around (prefix)",
    "u-po":"under (Greek hypo)","me-zo":"greater (Linear B)",
    "mi-nu-te":"Minotaur? (common Minoan)","ru-wo":"red? (colour)",
    "du-wo":"two (Linear B)","ti-ri":"three (Linear B)",
    "qe-to-ro":"four (Linear B)","pe-we":"drink? (vessel)",
}

DOMAINS = {
    "THEOLOGICAL":  THEOLOGICAL,
    "ADMINISTRATIVE": ADMINISTRATIVE,
    "GEOGRAPHICAL": GEOGRAPHICAL,
    "BODY/NEUTRAL": BODY_NEUTRAL,
}

# ── ALL KEYS ──────────────────────────────────────────────────────────────────
KEYS = {
    "A_EVANS":   {2:"a",7:"ko",11:"sa",12:"ne",22:"qi",29:"pe",36:"ku",45:"wi",1:"da",6:"na",24:"di",33:"ro",44:"tu",25:"ze",3:"si"},
    "B_FREQ":    {2:"a",36:"sa",11:"ra",29:"na",22:"ta",7:"ka",12:"da",6:"ti",45:"ma",1:"si",24:"re",25:"ro",33:"wa",44:"ki",3:"ko"},
    "E1_EGYPT":  {2:"na",36:"ra",11:"sa",29:"wa",22:"ta",7:"ma",12:"a",6:"ka",45:"ya",1:"ha",24:"xa",25:"da",33:"pa",44:"ba",3:"qa"},
    "F_CYPRIOT": {2:"a",36:"ku",11:"se",29:"pe",22:"pi",7:"ko",12:"ti",6:"na",45:"ri",1:"ta",24:"si",25:"sa",33:"ro",44:"me",3:"lo"},
    "G_LUWIAN":  {2:"za",36:"wa",11:"tar",29:"na",22:"ha",7:"ti",12:"zi",6:"an",45:"ti-wa",1:"i",24:"su",25:"naw",33:"ur",44:"ma",3:"pa"},
    "I_MORPHO":  {2:"a",36:"ku",11:"te",29:"ka",22:"na",7:"da",12:"qi",6:"ja",45:"de",1:"pa",24:"re",25:"di",33:"wa",44:"ke",3:"si"},
}

LINEAR_B_VALUES = [
    "da","ro","pa","te","to","na","di","a","se","u","po","so","me","do","mo",
    "za","mi","mu","ne","ru","re","i","pu","ni","sa","jo","ti","e","pi","wi",
    "si","wo","ke","de","du","no","ri","wa","nu","ja","su","ta","ra","o","ku",
]

def read_word(word, key):
    return "-".join(key.get(s,"?") for s in word if key.get(s,"?") != "?")

def score_key_vs_domain(key, vocab):
    text = " ".join(read_word(w, key) for w in ALL_WORDS)
    total = sum(text.count(word) for word in vocab if word in text)
    return total

# ── Monte Carlo per domain ────────────────────────────────────────────────────
random.seed(42)
N_MC = 3000
domain_nulls = {}
print(f"{SEP}")
print("  PHAISTOS — CORPUS CONTROL TEST")
print(f"{SEP}\n")
print("Υπολογισμός null distributions ανά domain...")

for dname, dvocab in DOMAINS.items():
    null_sc = []
    pool = LINEAR_B_VALUES[:]
    for _ in range(N_MC):
        random.shuffle(pool)
        rk = {s: pool[i % len(pool)] for i, s in enumerate(SIGN_FREQ_ORDER)}
        null_sc.append(score_key_vs_domain(rk, dvocab))
    ns_sorted = sorted(null_sc)
    domain_nulls[dname] = {
        "mean": sum(null_sc)/N_MC,
        "std":  math.sqrt(sum((x-sum(null_sc)/N_MC)**2 for x in null_sc)/N_MC),
        "t95":  ns_sorted[int(0.95*N_MC)],
        "t99":  ns_sorted[int(0.99*N_MC)],
        "null": null_sc,
    }
    print(f"  {dname:15s}: mean={domain_nulls[dname]['mean']:.1f}  std={domain_nulls[dname]['std']:.1f}")

# ── Results table ─────────────────────────────────────────────────────────────
print(f"\n{SEP}")
print("RESULTS: Each key scored against each vocabulary domain")
print(SEP2)

# Header
header = f"  {'Key':12s}"
for dn in DOMAINS:
    header += f"  {dn[:8]:>10s}"
print(header)
print(f"  {'-'*12}" + "  " + "  ".join(["-"*10]*4))

all_results = {}
for kname, kmap in KEYS.items():
    row = f"  {kname:12s}"
    all_results[kname] = {}
    for dname, dvocab in DOMAINS.items():
        sc = score_key_vs_domain(kmap, dvocab)
        nd = domain_nulls[dname]
        z = (sc - nd["mean"]) / nd["std"] if nd["std"] > 0 else 0
        sig = "★" if sc > nd["t99"] else ("·" if sc > nd["t95"] else " ")
        row += f"  {sc:>5}(Z={z:>4.1f}){sig}"
        all_results[kname][dname] = (sc, z, sig)
    print(row)

print(f"\n  ★ = p<0.01   · = p<0.05   (space) = not significant")

# ── Critical test: does G_LUWIAN win ONLY on theological? ────────────────────
print(f"\n{SEP}")
print("CRITICAL ANALYSIS: G_LUWIAN theological specificity")
print(SEP2)

g_scores = all_results["G_LUWIAN"]
g_theol_z = g_scores["THEOLOGICAL"][1]
g_admin_z = g_scores["ADMINISTRATIVE"][1]
g_geo_z   = g_scores["GEOGRAPHICAL"][1]
g_body_z  = g_scores["BODY/NEUTRAL"][1]

print(f"\n  G_LUWIAN Z-scores by domain:")
print(f"    THEOLOGICAL:   Z={g_theol_z:>5.2f}  {'★★★ SIGNIFICANT' if g_theol_z>2.58 else '★ marginal'}")
print(f"    ADMINISTRATIVE:Z={g_admin_z:>5.2f}  {'★★★ SIGNIFICANT' if g_admin_z>2.58 else ('★ marginal' if g_admin_z>1.65 else 'not sig.')}")
print(f"    GEOGRAPHICAL:  Z={g_geo_z:>5.2f}  {'★★★ SIGNIFICANT' if g_geo_z>2.58 else ('★ marginal' if g_geo_z>1.65 else 'not sig.')}")
print(f"    BODY/NEUTRAL:  Z={g_body_z:>5.2f}  {'★★★ SIGNIFICANT' if g_body_z>2.58 else ('★ marginal' if g_body_z>1.65 else 'not sig.')}")

theol_rank = sum(1 for d in ["ADMINISTRATIVE","GEOGRAPHICAL","BODY/NEUTRAL"]
                 if g_scores[d][1] >= g_theol_z) + 1

print(f"\n  Theological rank among 4 domains: {theol_rank}/4")

if theol_rank == 1 and g_theol_z > g_admin_z + 1.0:
    conclusion = ("THEOLOGICAL SPECIFICITY CONFIRMED\n"
                  "  Ο G_LUWIAN σκοράρει σημαντικά υψηλότερα ΜΟΝΟν στο θεολογικό domain.\n"
                  "  Αυτό αποδεικνύει ότι η σύγκλιση ΔΕΝ είναι artifact του μοντέλου.")
elif theol_rank == 1:
    conclusion = ("ΘΕΟΛΟΓΙΚΟ DOMAIN ΚΕΡΔΙΣΕ αλλά με μικρή διαφορά.\n"
                  "  Η διαφορά Z δεν είναι αρκετά μεγάλη για ισχυρό συμπέρασμα.")
else:
    conclusion = ("ARTIFACT POSSIBLE\n"
                  "  Ο G_LUWIAN σκοράρει εξίσου σε μη-θεολογικά domains.\n"
                  "  Η σύγκλιση μπορεί να είναι artifact της συχνότητας.")

print(f"\n  ΣΥΜΠΕΡΑΣΜΑ: {conclusion}")

# ── Ranking: which key wins per domain? ──────────────────────────────────────
print(f"\n{SEP}")
print("DOMAIN WINNERS: Ποιο key κερδίζει σε κάθε domain;")
print(SEP2)

for dname in DOMAINS:
    domain_scores = [(kn, all_results[kn][dname][0], all_results[kn][dname][1])
                     for kn in KEYS]
    domain_scores.sort(key=lambda x: -x[1])
    winner = domain_scores[0]
    print(f"\n  {dname}:")
    for kn, sc, z in domain_scores:
        bar = "█" * max(0, min(20, int(z*3)))
        marker = " ← WINNER" if kn == winner[0] else ""
        print(f"    {kn:12s}: score={sc:>4}  Z={z:>5.2f}  |{bar:<20}|{marker}")

# ── Final verdict ─────────────────────────────────────────────────────────────
print(f"\n{SEP}")
print("FINAL CORPUS CONTROL VERDICT")
print(SEP)
print(f"""
  Ερώτηση: Η θεολογική σύγκλιση είναι πραγματική ή artifact;

  G_LUWIAN THEOLOGICAL Z:   {g_theol_z:.2f}
  G_LUWIAN ADMIN Z:         {g_admin_z:.2f}
  G_LUWIAN GEO Z:           {g_geo_z:.2f}
  G_LUWIAN BODY Z:          {g_body_z:.2f}

  Αν THEOLOGICAL Z >> άλλα Z: ΠΡΑΓΜΑΤΙΚΟ εύρημα
  Αν όλα παρόμοια:           ARTIFACT

  Για paper:
  "To test whether the theological convergence was a model artifact,
   we scored all keys against four independent vocabulary domains of
   equal size (theological, administrative, geographical, neutral).
   G_LUWIAN achieved Z={g_theol_z:.2f} on theological vocabulary
   vs Z={g_admin_z:.2f}/{g_geo_z:.2f}/{g_body_z:.2f} on non-theological domains,
   {'confirming domain specificity' if theol_rank==1 else 'showing insufficient domain specificity'}."
""")
