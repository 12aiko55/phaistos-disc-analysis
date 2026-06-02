#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build Egyptian transliteration corpus from AED-TEI (aed-tei-master.zip).
Extracts <w> element text from main XML files → frequency distribution.
Target: 50,000+ tokens for Phaistos disc Egyptian hypothesis testing.
"""

import zipfile
import xml.etree.ElementTree as ET
import re
import json
import sys
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')

ZIP_PATH = r"C:\Users\Manos\Downloads\aed_tei_master.zip"
OUT_CORPUS = r"C:\Users\Manos\Downloads\tla_corpus.json"

# Namespaces used in TEI XML
NS = {
    'tei': 'http://www.tei-c.org/ns/1.0',
    'xml': 'http://www.w3.org/XML/namespace'
}

def clean_token(s):
    """Strip Egyptological diacritics to base consonantal skeleton for comparison."""
    if not s:
        return ""
    # Keep transliteration text, strip whitespace
    s = s.strip()
    # Remove lacuna markers and editorial brackets
    s = re.sub(r'[\[\]⸮…\.]+', '', s)
    return s.lower() if s else ""

def extract_words_from_xml(xml_bytes):
    """Parse one TEI XML file and return list of transliterated word strings.

    Structure: <w xml:id="..."><fs feats="verb"/>ḏd-mdw</w>
    The transliteration is the TAIL of the <fs> child element.
    """
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError:
        return []

    words = []
    for w in root.iter():
        tag = w.tag
        if '}' in tag:
            tag = tag.split('}')[1]
        if tag == 'w':
            token = ''
            # Check direct text first
            if w.text and w.text.strip():
                token = clean_token(w.text)
            # The transliteration is the tail of the <fs> child element
            if not token:
                for child in w:
                    ctag = child.tag
                    if '}' in ctag:
                        ctag = ctag.split('}')[1]
                    if ctag == 'fs' and child.tail and child.tail.strip():
                        token = clean_token(child.tail)
                        break
            if token and len(token) >= 1:
                words.append(token)
    return words

def main():
    print("=" * 70)
    print("  AED-TEI CORPUS BUILDER  —  Phaistos Egyptian Hypothesis")
    print("=" * 70)

    with zipfile.ZipFile(ZIP_PATH, 'r') as z:
        # Get all main XML files (not hiero/st/wt variants)
        all_files = z.namelist()
        main_xml = [f for f in all_files
                    if f.endswith('.xml')
                    and '_hiero' not in f
                    and '_st' not in f
                    and '_wt' not in f
                    and '/files/' in f
                    and 'dictionary' not in f
                    and 'thesaurus' not in f]

        print(f"Total main text XML files: {len(main_xml)}")

        all_tokens = []
        texts_processed = 0
        texts_with_words = 0

        # Process ALL files for maximum corpus size
        for i, fname in enumerate(main_xml):
            if i % 1000 == 0 and i > 0:
                print(f"  [{i}/{len(main_xml)}] tokens so far: {len(all_tokens):,}")

            try:
                data = z.read(fname)
                words = extract_words_from_xml(data)
                if words:
                    all_tokens.extend(words)
                    texts_with_words += 1
            except Exception:
                pass
            texts_processed += 1

        print(f"\nTexts processed:     {texts_processed:,}")
        print(f"Texts with tokens:   {texts_with_words:,}")
        print(f"Total tokens:        {len(all_tokens):,}")

        # Frequency distribution
        freq = Counter(all_tokens)
        print(f"Unique token types:  {len(freq):,}")
        print(f"\nTop 50 most frequent tokens:")
        print(f"{'Token':<20} {'Count':>8}  {'%':>6}")
        print("-" * 40)
        for tok, cnt in freq.most_common(50):
            pct = 100 * cnt / len(all_tokens)
            print(f"  {tok:<18} {cnt:>8}  {pct:>5.2f}%")

        # Save corpus
        corpus_data = {
            "total_tokens": len(all_tokens),
            "unique_types": len(freq),
            "texts_processed": texts_processed,
            "texts_with_words": texts_with_words,
            "frequency": dict(freq.most_common(500)),  # top 500 for analysis
            "all_tokens_sample": all_tokens[:10000]   # first 10k for pattern analysis
        }

        with open(OUT_CORPUS, 'w', encoding='utf-8') as f:
            json.dump(corpus_data, f, ensure_ascii=False, indent=2)

        print(f"\nCorpus saved → {OUT_CORPUS}")

        # Key analysis: extract CV syllable bigrams for adjacency test
        print("\n" + "=" * 70)
        print("  BIGRAM ANALYSIS — adjacency frequencies")
        print("=" * 70)
        bigrams = Counter()
        for j in range(len(all_tokens) - 1):
            bigrams[(all_tokens[j], all_tokens[j+1])] += 1

        print(f"Total bigrams: {len(bigrams):,}")
        print("\nTop 20 most common bigrams:")
        for (a,b), cnt in bigrams.most_common(20):
            print(f"  {a} → {b}: {cnt}")

        # Check specific Phaistos-relevant sequences
        print("\n" + "=" * 70)
        print("  PHAISTOS KEY TOKENS — corpus frequencies")
        print("=" * 70)
        key_tokens = ['ra', 'sa', 'na', 'ta', 'ma', 'ka', 'da', 'ti', 'wa',
                      'sa-ra', 'ra-sa', 'asar', 'wsir', 'n', 'sA', 'rA',
                      'nTr', 'mj', 'pr', 'xr', 'jn', 'jr', 'nn', 'nfr',
                      'wsr', 'mAat', 'Htp', 'anx', 'Dd', 'nb', 'nbt',
                      'jrt', 'mwt', 'sn', 'snt', 'Ast', 'nbt', 'Nbt-Hwt']
        print(f"{'Token':<20} {'Count':>8}  {'per 1000':>10}")
        print("-" * 45)
        for kt in key_tokens:
            cnt = freq.get(kt, 0)
            rate = 1000 * cnt / len(all_tokens) if all_tokens else 0
            print(f"  {kt:<18} {cnt:>8}  {rate:>9.2f}")

        # Sign-to-token mapping test: Phaistos sign frequencies vs TLA
        print("\n" + "=" * 70)
        print("  FREQUENCY RANK COMPARISON")
        print("  (Phaistos top signs vs TLA top tokens)")
        print("=" * 70)
        print("Phaistos top 15 signs (by occurrence):")
        phaistos_freq_order = [2, 36, 11, 29, 22, 7, 12, 6, 45, 1, 24, 25, 33, 44, 3]
        phaistos_counts =    [29, 26, 23, 21, 19, 18, 16, 15, 14, 13, 12, 11, 10, 9,  8]
        for rank, (sign, cnt) in enumerate(zip(phaistos_freq_order, phaistos_counts), 1):
            print(f"  Rank {rank:2d}: Sign #{sign:2d} → {cnt} occurrences")

        print(f"\nTLA top 15 tokens (by frequency):")
        for rank, (tok, cnt) in enumerate(freq.most_common(15), 1):
            pct = 100 * cnt / len(all_tokens)
            print(f"  Rank {rank:2d}: '{tok}' → {cnt} ({pct:.2f}%)")

        print("\n✓ Done. Use tla_corpus.json for phaistos_egypt_v3.py analysis.")

if __name__ == "__main__":
    main()
