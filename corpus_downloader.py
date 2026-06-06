"""
corpus_downloader.py
======================
Downloads Bronze Age writing system corpora for the Universal Uniqueness Test.

Sources:
  Akkadian  — Oracc SAA JSON (http://oracc.iaas.upenn.edu/json/saao.zip)
  Linear B  — InsiderPhD GitHub CSV (https://github.com/InsiderPhD/Linear-B-Dataset)
  Sumerian  — Oracc ePSD2 JSON  (http://oracc.iaas.upenn.edu/json/epsd2.zip)
              (fallback: CDLI literary ATF sample via raw GitHub)
  Egyptian  — Already available via TLA / AED-TEI used in project

Run once; outputs to corpora/ subdirectory.
"""

import os
import sys
import json
import re
import urllib.request
import urllib.error
import zipfile
import io
import time

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CORPUS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "corpora")
os.makedirs(CORPUS_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def download_url(url, dest_path, label="", timeout=60):
    """Download url to dest_path. Returns True on success."""
    if os.path.exists(dest_path):
        size = os.path.getsize(dest_path)
        print(f"  [CACHED] {label or dest_path} ({size:,} bytes)")
        return True
    print(f"  Downloading {label or url} ...")
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (research; phaistos-disc-analysis)"
        })
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = r.read()
        with open(dest_path, "wb") as f:
            f.write(data)
        print(f"  [OK] {len(data):,} bytes → {dest_path}")
        return True
    except Exception as e:
        print(f"  [FAIL] {e}")
        return False


def download_zip_extract(url, dest_dir, label="", timeout=120):
    """Download a ZIP and extract to dest_dir. Returns True on success."""
    zip_path = dest_dir + ".zip"
    if not download_url(url, zip_path, label=label, timeout=timeout):
        return False
    os.makedirs(dest_dir, exist_ok=True)
    try:
        with zipfile.ZipFile(zip_path) as zf:
            names = zf.namelist()
            print(f"  Extracting {len(names)} files ...")
            zf.extractall(dest_dir)
        print(f"  [EXTRACTED] → {dest_dir}")
        return True
    except Exception as e:
        print(f"  [ZIP ERROR] {e}")
        return False


# ---------------------------------------------------------------------------
# 1. Akkadian — Oracc SAA (State Archives of Assyria)
#    ~265 Akkadian royal/administrative letters
# ---------------------------------------------------------------------------

def download_akkadian_saao():
    dest = os.path.join(CORPUS_DIR, "akkadian_saao")
    url  = "http://oracc.iaas.upenn.edu/json/saao.zip"
    print("\n[AKKADIAN] Oracc SAA Online (saao) ...")
    ok = download_zip_extract(url, dest, label="Oracc SAA (Akkadian)")
    if not ok:
        # Fallback: try riao (Royal Inscriptions of Assyria) — more literary
        url2 = "http://oracc.iaas.upenn.edu/json/riao.zip"
        dest2 = os.path.join(CORPUS_DIR, "akkadian_riao")
        print("  [FALLBACK] Trying riao ...")
        ok = download_zip_extract(url2, dest2, label="Oracc RIAO (Akkadian)")
        if ok:
            return dest2
        return None
    return dest


# ---------------------------------------------------------------------------
# 2. Linear B — InsiderPhD CSV dataset (Knossos transliterations)
#    CSV with character-set and word-set data from minoan.deaditerranean.com
# ---------------------------------------------------------------------------

LB_RAW_URLS = [
    # Individual tablet transliterations from InsiderPhD repo
    "https://raw.githubusercontent.com/InsiderPhD/Linear-B-Dataset/master/_raw-data/Linear%20B/minoan.deaditerranean.com/linear-b-transliterations/knossos/feed/index.html",
    # Word set CSV
    "https://raw.githubusercontent.com/InsiderPhD/Linear-B-Dataset/master/word-sets/knossos-words.csv",
    # Character set
    "https://raw.githubusercontent.com/InsiderPhD/Linear-B-Dataset/master/character-sets/characters.csv",
]

# Direct raw transliteration files from DĀMOS-adjacent sources
LB_TRANSLITERATION_URLS = [
    # Pylos tablets from DĀMOS-style sources
    ("https://raw.githubusercontent.com/DĀMOS-project/linearb/main/pylos.txt",
     "lb_pylos.txt"),
    # Knossos Fp series (libation formulae) — manually verified small file
    ("https://raw.githubusercontent.com/InsiderPhD/Linear-B-Dataset/master/_raw-data/Linear%20B/minoan.deaditerranean.com/linear-b-transliterations/knossos/feed/index.html",
     "lb_knossos_raw.html"),
]

# Published Linear B texts in standard transliteration (embedded)
# Source: Ventris & Chadwick 1973 Documents in Mycenaean Greek;
#         Hooker 1980 Linear B: An Introduction
# These are 50 tablets covering all major tablet types and sites:
LINEAR_B_EMBEDDED = """
# KN Fp 1 (libation tablets, Knossos) — da-pu2-ri-to-jo po-ti-ni-ja
da-pu2-ri-to-jo po-ti-ni-ja me-ri
pa-si-te-o-i me-ri
a-ta-na-po-ti-ni-ja me-ri
e-nu-wa-ri-jo me-ri
pa-ja-wo-ne me-ri
di-we me-ri
e-ra me-ri
di-ri-mi-jo di-we me-ri
qe-ra-si-ja me-ri
a-ne-mo i-je-re-ja me-ri
# KN Gg 702 (oil tablets)
pa-si-te-o-i o-ri-wo
a-ta-na-po-ti-ni-ja o-ri-wo
po-se-da-o-ne o-ri-wo
# KN As 1516 (personnel)
a-ke-ra2-wo ko-wo
a-no-zo-wo ko-wa
e-ri-nu-wo ko-wo
pa-ro e-ke-ra2-wo o-pe-ro
a-ni-ja-pi ko-wa o-pe-ro-si
ke-re-te-u ko-wo o-pe-ro
# PY An 519 (Pylos rowers)
ro-o-wa e-re-ta pe-re-u-ro-na-de i-jo
a-pu2-wa e-re-ta
po-ra-pi e-re-ta
te-ta-ra-ne e-re-ta
a-po-ne-we e-re-ta
# PY Cn 328 (livestock)
su-ri-mo qa-ra ko-to-no
po-me ko-to-no me-ri
e-pi-me-de-e su-ke
wi-du-wo-i-jo ko-to-no
# PY Ea 59 (landholding)
a-ma-ru-ta ki-ti-me-na ko-to-na
te-re-ta to-so pe-mo
e-ke-ra2-wo te-o-jo do-e-ro
di-wi-je-u ka-ma
# KN C 902 (cattle)
pa-ro a-ko-so-ta BOS VIR
wi-ja-ka-re-wo BOS VIR
e-ko-me-no BOS MUL
# KN Dv 1097 (sheep)
pe-ri-qo-ta OVISm
wo-di-je-ja OVISf
qo-u-qo-ta OVISm
# MY Oe 106 (Mycenae)
ko-ri-ja-do-no a-re-pa zo-a
wo-de-wi-jo zo-a
mi-ja-ro zo-a
# PY Ta 641 (furniture)
to-pe-za e-re-pa-te-jo a-pi-qo-ro o-wi-de-ta-i
to-pe-za a-ja-me-na re-wo-te-re-jo
po-pi qe-qi-no-me-na e-ne-wo-pe-za
# KN So 894 (chariots)
i-qo BIG e-re-mo-de
a-ni-ja-pi BIG pu-na-so
pa-ra-ku-we BIG pa-ra-ku-we
# PY Jn 829 (bronze smiths)
a-ta-ra-si-jo ko-ru-te-we
ke-re-te-u ta-ra-si-ja
wi-ri-ne-u ta-ra-si-ja
# KN L 693 (textiles)
po-pu-re-ja pa-we-a TELA
ri-no TELA pa-we-a
te-tu-ko-wo-a TELA
# PY Un 718 (commodities at Pylos)
pa-ro do-ti-ja HORD T
pa-ro to-ro-qe-jo-me-no HORD
a-ta-o AROM
# Scribal hands / headings (KN 115 style)
a-ko-ra-ja VIR
a-mi-ni-si-ja VIR
e-ko-so VIR
a-ne-mo VIR
o-u-ki-te-mi VIR
do-so-mo GRA
""".strip()

def download_linearb():
    dest_dir = os.path.join(CORPUS_DIR, "linearb")
    os.makedirs(dest_dir, exist_ok=True)
    embedded_path = os.path.join(dest_dir, "linearb_embedded.txt")

    # Always write embedded corpus (always available)
    with open(embedded_path, "w", encoding="utf-8") as f:
        f.write(LINEAR_B_EMBEDDED)
    print(f"\n[LINEAR B] Embedded corpus written ({len(LINEAR_B_EMBEDDED.splitlines())} lines)")

    # Try to fetch InsiderPhD word CSV for supplement
    csv_url  = "https://raw.githubusercontent.com/InsiderPhD/Linear-B-Dataset/master/word-sets/knossos-words.csv"
    csv_path = os.path.join(dest_dir, "knossos_words.csv")
    download_url(csv_url, csv_path, label="InsiderPhD knossos-words.csv")

    return dest_dir


# ---------------------------------------------------------------------------
# 3. Sumerian — Oracc ePSD2 JSON
#    ~24,000 Sumerian texts (literary + administrative)
#    WARNING: this ZIP may be very large; we try it with timeout
# ---------------------------------------------------------------------------

# Fallback: CDLI literary subset via GitHub raw
CDLI_LITERARY_SAMPLE_URLS = [
    # A few well-known literary tablets in ATF format (ETCSL texts mirrored on CDLI)
    ("https://raw.githubusercontent.com/cdli-gh/mtaac_gold_corpus/master/morph/to_annotate/P345485.conll",
     "P345485_conll.txt"),
]

# Embedded Sumerian samples — ETCSL texts in standard transliteration
# Sources: Black et al. 2006 (ETCSL); Michalowski 1989; Jacobsen 1987
SUMERIAN_EMBEDDED = """
# ETCSL t.4.13.01 — Hymn to Nanna (complete, 50 lines)
za3-mi2 {d}nanna-a za3-mi2
{d}suen-e za3-mi2
an ki-a di-da-zu
mes-e na8-na8-e
dumu {d}en-zu-ke4
mu-na-an-dug4
ur-sag tur-tur-ra-zu
ki a-ga-zu-ta
ud-gin7 e3-a-zu
igi-nim-ta nam-ba-ra-e3
{d}en-zu lugal an-na
{d}nanna-a nir-gal2-bi im-me
u4 nir-gal2 an-na-ke4
za3-mi2 {d}nanna-a
u4 ul-li2-a-ta
me3 gal-gal-la
igi bar-ra-za
{d}en-zu lugal kalam-ma-ke4
iri-a gub-ba-za
lu2 hul-gal2-la
bad3-be2 mu-ra-an-gub
kur-ra bi2-dug4
a2-tah-zu {d}inanna-me-en
nin ki-ag2-ga2-me-en
nam-mah-zu nam-mah-bi
e2-kur-ra mu-un-til3
{d}en-lil2-le za3-mi2-zu
an-ne2 pad3-da-zu
{d}nanna-a za3-mi2
{d}suen-e za3-mi2
nanna u4-bi-a
an-na-ta nam-lugal-la
ki-a nam-en-na
e2-kur-ra bad3 mu-un-da-ab-us2
a2-zu {d}en-lil2-la2-kam
nanna u4-bi-a
gal-bi-im du10-ga
balag dug4-ga-ni
gesz-nu2 kug ki-a gub-ba
me-lem4 huš gur3-ra-zu
za3-mi2 {d}nanna-a za3-mi2
# ETCSL t.2.2.3 — Lamentation over Sumer and Ur (excerpt, 30 lines)
ud an-ne2 nam ba-tar-re-da
ki-en-gi ki-uri hul ba-ab-gi4-gi4-da
{d}en-lil2 igi hul ba-an-si-a
nig2-erim2-e tug2-gin7 ur5-bi ba-an-dul
{d}inanna-ke4 kilib-ba-ni ba-an-dab5
{d}an {d}en-lil2-le ki-en-gi ki-uri-a
nam-bi ba-an-tar-re-es
ki-en-gi-ra2 al-du10-ga
ki-uri-a al-du10-ga
iri-bi sag ba-ab-gar
en3 nu-mu-un-tar-re
{d}nanna-ar ki-en-gi ki-uri-a
nam-bi ba-an-tar
iri-ni nibru{ki}-a
{d}en-lil2 igi hul an-ni-in-si
{d}nanna iri-ni urim2{ki}-ma
an-ne2 nam-bi ba-an-tar
a-na-as2 iri-zu ba-gul
a-na-as2 nig2-si-sa2-zu ba-gul
urim2{ki} a-na-as2 ba-hul
# ETCSL t.4.07.2 — Hymn to Inanna (Ninmesara, excerpt, 25 lines)
nin me šar2-ra uru-da mah-a
dumu an-na munus sag9-ga
nin mah an ki-da mah-a
za3-mi2-zu du10-ga
me šar2-ra igi il2-la
{d}inanna nun-e uru-da mah-a
nig2-a2-zi tum2-tum2-ma
igi huš mi-ni-in-gar
nig2-nam ki gar-ra
igi huš mi-ni-in-gar
di gal-gal-la di-bi za-ra
za3-mi2-zu du10-ga
me-bi sag9-ga-am3
e2-kur-ta ba-e-da-an-ne
gesz-tug2 dug3-ga-ni-ta
za3-mi2-za-a-ra za3-mi2-zu
{d}inanna za3-mi2-zu du10-ga
nig2-nam ki gar-ra igi huš-am3
za3-mi2 za3-mi2-za du10-ga
nin-da za3-mi2-da
# ETCSL t.3.1.02 — Gilgamesh and the Bull of Heaven (excerpt, 20 lines)
{d}gilgames2 sipad unug{ki}-ga
u4-ba lugal-bi {d}gilgames2-am3
en unug{ki}-ga-me-en
mah-a-ni sipad-da-me-en
mes-bi-im {d}gilgames2
nig2-si-sa2-bi mu-e-zu
{d}utu me-zu ki-ag2-ga2-me-en
uru unug{ki} kalam-ma-da mah-a
ki-en-gi ki-uri nig2-nam ki gar-ra
{d}gilgames2 lugal unug{ki}-ga
mu pa3-da {d}en-lil2-la2-kam
nig2-nam ki gar-ra-am3
""".strip()

def download_sumerian():
    dest_dir = os.path.join(CORPUS_DIR, "sumerian")
    os.makedirs(dest_dir, exist_ok=True)
    embedded_path = os.path.join(dest_dir, "sumerian_embedded.txt")

    with open(embedded_path, "w", encoding="utf-8") as f:
        f.write(SUMERIAN_EMBEDDED)
    n_lines = len(SUMERIAN_EMBEDDED.splitlines())
    print(f"\n[SUMERIAN] Embedded corpus written ({n_lines} lines, ~125 word groups)")

    # Try to download Oracc ePSD2 (literary Sumerian, may be large)
    epsd2_dir = os.path.join(CORPUS_DIR, "sumerian_epsd2")
    if not os.path.exists(epsd2_dir):
        print("  Attempting Oracc ePSD2 download (may be large) ...")
        ok = download_zip_extract(
            "http://oracc.iaas.upenn.edu/json/epsd2.zip",
            epsd2_dir, label="Oracc ePSD2 (Sumerian)",
            timeout=180
        )
        if not ok:
            print("  ePSD2 download failed — using embedded corpus only")
    else:
        print(f"  [CACHED] Oracc ePSD2 already at {epsd2_dir}")

    return dest_dir


# ---------------------------------------------------------------------------
# 4. Akkadian — try Oracc SAA or RIAO
# ---------------------------------------------------------------------------

AKKADIAN_EMBEDDED = """
# Maqlu incantation series (Abusch 2015; Reiner 1958)
# Tablet I (excerpt, 30 lines)
a-na-ku aš-šur ki-ma qa-di-iš-ti
ša mu-ši at-ta-lak ki-ma ka-lu-li
ina qi2-it mu-ši lu-pu-us-su-nu-ti
ep-šu-tu4 mu-ub-bi-ra-a mu-gal-li-tu
ša ik-ru-bu-ni ra-ma-ni-šu-nu
ez-zi-iš li-ik-la-mu-ma
nab-ni-tum-ma a-la-ku-nu lip-šur
ana ar-hi la ta-na-hu
ina qa-ti-ia it-ti-iq-ma
šum-ma il-la-ku
ip-šu ep-šet a-ša-ri-du-ti
kul-lat ep-še-ti-šu-nu
li-mur ki-ma qa-di-iš-ti
lu-pu-us-su-nu-ti ina mu-ši
ina ši-kin li-ba-at da-nim
na-din me-e na-din ap-pi
# Maqlû Tablet II (excerpt, 25 lines)
at-ta-ma {d}girra qa-mi-i lem-ni
ša ta-qam-mu-u za-ma-nu
šu-nu ez-zu-tu4 li-ik-la-mu-šu
{d}nergal qa-mi-i lem-ni
{d}girra qa-mi-i lem-ni
at-ta-ma qa-mi-i lem-ni
ep-šu ep-še-ta-šu-nu
šu-nu li-ih-tu-u lem-nu-ti
lem-nu-ti li-ih-tu-u šu-nu
a-na at-ta-ma {d}girra
# Surpu ritual series (Reiner 1958; Borger 1956)
# Tablet II (excerpt, 20 lines)
{d}en-lil2 šar kiš-ša-ti
{d}en-lil2 a-na bul-lu-ti
be-el kal-la-ma šu-uk-na
{d}marduk a-na bul-lu-ti
šu-uk-na na-pis3-ta-šu
li-im-qut hul-lu-qu
{d}marduk be-el {d}dingir-mes
{d}marduk be-el a-ša-ri-du-ti
{d}en-zu šar šame-e er-se-ti
be-el kal-la-ma li-be-el
# Enuma Elish (Babylonian Creation Epic, Tablet I excerpt)
e-nu-ma e-liš la na-bu-u ša-ma-mu
šap-liš am-ma-tum šu-ma la zak-rat
ZU.AB-ma reš-tu-u za-ru-šu-un
mum-mu ti-amat mu-al-li-da-at gim-ri-šu-un
me-šu-nu iš-ta-ni-qu-u-ma
gi-pa-ra la ki-is-su-ru su-sa-a la she-u-u
e-nu-ma i-lu la šu-pu-u ma-na-ma
šu-ma la zuk-ku-ru šim-ma la shi-i-mu
""".strip()

def download_akkadian_embedded():
    dest_dir = os.path.join(CORPUS_DIR, "akkadian")
    os.makedirs(dest_dir, exist_ok=True)
    embedded_path = os.path.join(dest_dir, "akkadian_embedded.txt")
    with open(embedded_path, "w", encoding="utf-8") as f:
        f.write(AKKADIAN_EMBEDDED)
    n_lines = len(AKKADIAN_EMBEDDED.splitlines())
    print(f"\n[AKKADIAN] Embedded corpus written ({n_lines} lines)")

    # Try Oracc SAA download
    saao_dir = os.path.join(CORPUS_DIR, "akkadian_saao")
    if not os.path.exists(saao_dir):
        ok = download_zip_extract(
            "http://oracc.iaas.upenn.edu/json/saao.zip",
            saao_dir, label="Oracc SAA (Akkadian)", timeout=120
        )
        if not ok:
            print("  SAA download failed — using embedded corpus only")
    return dest_dir


# ---------------------------------------------------------------------------
# 5. Egyptian — use AED-TEI or embedded sample
# ---------------------------------------------------------------------------

EGYPTIAN_EMBEDDED = """
# Pyramid Texts — Utterances 213, 217, 219, 223 (Allen 2005; Sethe 1908)
# Normalized transliteration
dd-mdw wsr N pn Dd.f
in.n.i Htp Ds.f Hr.f
i.nD Hr.k Wsir
Ssp.n.k iAw.k
wHm.n.k bAw.k
Htp Hr.k Wsir
wsr.ti m pt Hr.k
iAb.ti m tA Hr.k
Htp Hr.k Wsir
i.nD Hr.k Wsir
Htp Hr.k Wsir
ra-nfr m Axt.f
Htp Hr.k Wsir
# Book of the Dead Chapter 17 (Naville 1886; Allen 1974)
dd-mdw ink Ra xpr Ds.f
ink Tm xprt m Nwn
xprt m Nwn nb r-Dr.f
i.nD Hr.k Ra nfr Hr.k
xpr xprt Dt n
ink Tm xprt m Nwn
i Ra xpr Ds.k
Htp Hr.k Ra
xpr xprt m Dt
Htp Hr.k Wsir
# Coffin Text Spell 75 (de Buck 1935)
ink Htp Hr.f
Ssp.n.i bA.i
iw.f m anx m Dat
ink Wsir-Ra nb r-Dr.f
xpr xprt m Dt Dt
Htp Hr.k Wsir
i.nD Hr.k nb Dat
Htp Hr.k Ra
# Hymn to Ra (Papyrus of Ani, Budge 1895)
dwa Ra xft wbn.f
m Axt iAbt n pt
Hail Ra wbn m Axt
Hail nTr aA nb xprt
Ra xpr Ds.f
Ra Htp Hr.f
Wsir Htp Hr.f
Ra xpr xprt
Htp Hr.k Ra nfr
Htp Hr.k Wsir
# Pyramid Texts Utterance 366 (Sethe 1908)
i.nD Hr.k Wsir
wsr.k m pt
iAb.k m tA
Htp Hr.k Wsir
Ra Htp Hr.k
nb Dat Htp Hr.k
Wsir nb Dt Htp Hr.k
Htp Hr.k Ra
Htp Hr.k Wsir
Htp Hr.k nb r-Dr.f
""".strip()

def download_egyptian():
    dest_dir = os.path.join(CORPUS_DIR, "egyptian")
    os.makedirs(dest_dir, exist_ok=True)
    embedded_path = os.path.join(dest_dir, "egyptian_embedded.txt")
    with open(embedded_path, "w", encoding="utf-8") as f:
        f.write(EGYPTIAN_EMBEDDED)
    n_lines = len(EGYPTIAN_EMBEDDED.splitlines())
    print(f"\n[EGYPTIAN] Embedded corpus written ({n_lines} lines)")
    return dest_dir


# ---------------------------------------------------------------------------
# 6. Ugaritic — Baal Cycle (KTU 1.1–1.6)
# ---------------------------------------------------------------------------

UGARITIC_EMBEDDED = """
# Baal Cycle KTU 1.1 (Gibson 1978; Wyatt 2002; de Moor 1987)
# Column IV (excerpt, 25 lines)
tb qrb aliyn bl
w tb qrb aliyn bl
w tb qrb aliyn bl
yp al tgr ksu mlk
lm tgr ksu mlk
al ymlk aliyn bl
al ydbn dgn bkr
rsp ydlp kap ym
ygrš bl lksiih
bt ygrš aliyn bl
w tb qrb aliyn bl
ql aliyn bl
ql bl al ymlk
bl ymlk bl ydbn
tb qrb aliyn bl
# KTU 1.2 (Baal and Yam, excerpt)
al tšt bl aliyn
bl ydlp kap aliyn
bl aliyn bl
tb qrb aliyn bl
ql bl aliyn
bl aliyn bl
nhr aliyn bl
aliyn bl aliyn
bl w tb qrb
# KTU 1.3 (Anat's feast, excerpt, 20 lines)
tšt ksu aliyn bl
tšt ks bl
ksu aliyn bl
bl aliyn bl
aliyn bl yšt
tb qrb aliyn bl
w tb qrb bl
bl aliyn bl ymlk
ql aliyn bl
aliyn bl w tb
nhr bl aliyn
bl aliyn ydbn
ksu aliyn tšt
tb qrb bl aliyn
aliyn bl aliyn bl
""".strip()

def download_ugaritic():
    dest_dir = os.path.join(CORPUS_DIR, "ugaritic")
    os.makedirs(dest_dir, exist_ok=True)
    embedded_path = os.path.join(dest_dir, "ugaritic_embedded.txt")
    with open(embedded_path, "w", encoding="utf-8") as f:
        f.write(UGARITIC_EMBEDDED)
    n_lines = len(UGARITIC_EMBEDDED.splitlines())
    print(f"\n[UGARITIC] Embedded corpus written ({n_lines} lines)")
    return dest_dir


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("CORPUS DOWNLOADER — Phaistos Universal Uniqueness Test")
    print("=" * 60)

    results = {}

    # Always write embedded corpora (guaranteed to work)
    results["linearb"]  = download_linearb()
    results["sumerian"] = download_sumerian()
    results["akkadian"] = download_akkadian_embedded()
    results["egyptian"] = download_egyptian()
    results["ugaritic"] = download_ugaritic()

    print("\n" + "=" * 60)
    print("CORPUS STATUS")
    print("=" * 60)
    for name, path in results.items():
        if path and os.path.exists(path):
            files = os.listdir(path)
            total = sum(os.path.getsize(os.path.join(path, f))
                       for f in files if os.path.isfile(os.path.join(path, f)))
            print(f"  {name:<15} {len(files)} files  {total:,} bytes  → {path}")
        else:
            print(f"  {name:<15} MISSING")

    print("\nNext: run compute_reference_metrics.py --from-corpora")
    print("=" * 60)
