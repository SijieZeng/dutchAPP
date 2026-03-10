#!/usr/bin/env python3
"""
Generate example sentences for all NIA words (full 5163 word list).
"""
import json
import re
import sys
import io
import random

# Import sentence generation logic from generate_sentences.py
# Must import before setting stdout to avoid double-wrap
sys.path.insert(0, 'tools')
from generate_sentences import generate_sentence, clean_english_for_sentence

# Ensure stdout is utf-8 (generate_sentences.py may have already set it)
if not isinstance(sys.stdout, io.TextIOWrapper) or sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

random.seed(42)

INPUT = 'tools/nia_full_parsed.json'
OUTPUT = 'tools/nia_full_parsed_with_sentences.json'

def classify_pos(dutch: str, english: str) -> str:
    """Classify part of speech."""
    dutch_lower = dutch.lower().strip()
    eng = english.strip()

    if 'zich' in dutch_lower:
        return 'verb'
    if eng.startswith('to ') or re.match(r'^a\)\s*to\s', eng):
        return 'verb'

    adj_suffixes = ['lijk', 'ig', 'isch', 'baar', 'loos', 'vol', 'ief', 'eel', 'aal', 'eus']
    for suf in adj_suffixes:
        if dutch_lower.endswith(suf):
            return 'adjective'

    adv_words = ['achteraf', 'aldus', 'amper', 'andersom', 'bovendien', 'daarom', 'daardoor',
                 'daarna', 'desnoods', 'dus', 'eigenlijk', 'eveneens', 'gauw', 'gelukkig',
                 'helaas', 'hierbij', 'hierdoor', 'hierover', 'hopelijk', 'inmiddels',
                 'intussen', 'kortom', 'langzaam', 'liefst', 'misschien', 'namelijk',
                 'nauwelijks', 'ooit', 'opeens', 'opnieuw', 'overigens', 'pas', 'precies',
                 'sindsdien', 'slechts', 'sowieso', 'steeds', 'telkens', 'tenminste',
                 'tenslotte', 'terwijl', 'toch', 'uiteindelijk', 'uiteraard', 'vanwege',
                 'vervolgens', 'vlak', 'voortaan', 'vooruit', 'waarschijnlijk', 'weliswaar',
                 'zeker', 'zelfs', 'zolang', 'zomaar', 'zowel', 'absoluut', 'af en toe',
                 'alsmaar', 'altijd', 'binnenkort', 'daar', 'doorgaans', 'echt', 'eerder',
                 'eindelijk', 'enigszins', 'ergens', 'eventueel', 'gewoon', 'graag',
                 'haast', 'heel', 'hier', 'hoewel', 'immers', 'inderdaad', 'intussen',
                 'juist', 'kennelijk', 'kort', 'letterlijk', 'meteen', 'mogelijk', 'naar',
                 'nergens', 'nooit', 'nu', 'vaak', 'alleen', 'alweer', 'anders', 'bijna',
                 'boven', 'buiten', 'dadelijk', 'enorm', 'erg', 'ernstig', 'vooral',
                 'verder', 'vroeg', 'wanneer', 'wellicht', 'werkelijk', 'zo', 'blijkbaar',
                 'nogal', 'reeds', 'tamelijk', 'trouwens', 'vrijwel', 'wederom']
    if dutch_lower in adv_words:
        return 'adverb'

    return 'noun'


def main():
    with open(INPUT, 'r', encoding='utf-8') as f:
        entries = json.load(f)

    for i, entry in enumerate(entries):
        pos = classify_pos(entry['dutch'], entry.get('english', ''))
        nl_sent, en_sent = generate_sentence(
            entry['dutch'], entry.get('english', ''), pos, i
        )
        entry['example_nl'] = nl_sent
        entry['example_en'] = en_sent
        entry['pos'] = pos

    with open(OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)

    pos_counts = {}
    for e in entries:
        p = e['pos']
        pos_counts[p] = pos_counts.get(p, 0) + 1

    print(f'Generated sentences for {len(entries)} words')
    print(f'POS distribution: {pos_counts}')

    # Show samples
    for e in entries[:5]:
        print(f"  {e['dutch']:25s} -> {e['example_nl']}")
        print(f"  {'':25s}    {e['example_en']}")


if __name__ == '__main__':
    main()
