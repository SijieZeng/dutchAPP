#!/usr/bin/env python3
"""
Parse frequente_onregelmatige_werkwoorden.pdf and generate
lib/data/textbooks/irregular_verbs_data.dart

The PDF has 3 columns: hele werkwoord, verleden tijd (imperfectum), voltooide tijd (perfectum)
Example: beginnen    begon/ begonnen    begonnen
"""
import sys
import io
import re
import json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import pdfplumber

PDF_PATH = 'frequente_onregelmatige_werkwoorden.pdf'
OUTPUT_PATH = 'lib/data/textbooks/irregular_verbs_data.dart'

# Known zijn verbs (use 'zijn' as auxiliary in perfectum)
ZIJN_VERBS = {
    'beginnen', 'bewegen', 'blijken', 'blijven', 'gaan', 'komen', 'lopen',
    'rijden', 'vallen', 'verdwijnen', 'verschijnen', 'vliegen', 'worden',
    'zijn', 'sterven', 'stijgen', 'springen', 'toenemen', 'zwemmen',
    'slagen', 'groeien', 'opgroeien', 'varen',
}

# Verbs that already exist in NIG or NIA data (skip these)
EXISTING_VERB_INFINITIVES = {
    'zijn', 'hebben', 'komen', 'gaan', 'doen', 'kunnen', 'willen', 'moeten',
    'mogen', 'zullen', 'wonen', 'werken', 'heten', 'lezen', 'beginnen',
    'eten', 'drinken', 'geven', 'nemen', 'kopen', 'zeggen', 'vinden',
    'weten', 'zien', 'schrijven', 'spreken', 'staan', 'zitten', 'liggen',
    'rijden', 'brengen', 'denken',
    # NIA verbs
    'accepteren', 'adviseren', 'bepalen', 'beschrijven', 'bestaan', 'besteden',
    'bevatten', 'beweren', 'bezitten', 'bijdragen', 'blijken', 'dreigen',
    'dwingen', 'ervaren', 'functioneren', 'gelden', 'groeien',
    'invoeren', 'leveren', 'lijden', 'meedoen', 'meenemen', 'merken',
    'omgaan', 'ondernemen', 'onderzoeken', 'ontwikkelen', 'opgroeien',
    'oplossen', 'opvallen', 'overleggen', 'plaatsvinden', 'scheiden',
    'slagen', 'steunen', 'stichten', 'toenemen', 'toepassen', 'uitvoeren',
    'verbieden', 'verdwijnen', 'vergelijken', 'verlangen', 'vermijden',
    'verschijnen', 'vertrouwen', 'verwachten', 'voorkomen', 'voorstellen',
    'wijzen',
}


def get_stem(infinitive: str) -> str:
    """Get the verb stem for present tense conjugation."""
    inf = infinitive.lower().strip()

    # Handle separable verbs: opslaan -> sla ... op
    # For the stem, we work with the base verb
    particle = None
    separable_prefixes = ['aan', 'af', 'bij', 'in', 'mee', 'na', 'om', 'op', 'over',
                          'tegen', 'toe', 'uit', 'voor', 'weg']
    for prefix in sorted(separable_prefixes, key=len, reverse=True):
        if inf.startswith(prefix) and len(inf) > len(prefix) + 2:
            base = inf[len(prefix):]
            # Check if the base looks like a verb (common verb endings)
            if base.endswith('en') or base.endswith('n'):
                particle = prefix
                inf = base
                break

    # Remove -en ending to get stem
    if inf.endswith('ën'):
        stem = inf[:-2]
    elif inf.endswith('en'):
        stem = inf[:-2]
    elif inf.endswith('n'):
        stem = inf[:-1]
    else:
        stem = inf

    # Apply Dutch spelling rules
    # Double vowel in open syllable: lopen -> loop (not lop)
    # If stem ends in single consonant preceded by single vowel in pattern like CVC:
    # Check if we need to double the vowel
    vowels = 'aeiou'

    # Rule: if infinitive has double consonant, stem loses one: zitten -> zit
    # This is handled naturally by removing -en

    # Rule: if the verb has a long vowel in open syllable (like lo-pen),
    # the stem needs double vowel (loop)
    if len(stem) >= 2:
        # Check for pattern: single vowel + single consonant at end
        # where the infinitive suggests a long vowel (open syllable)
        if (stem[-1] not in vowels and
            len(stem) >= 2 and stem[-2] in vowels and
            (len(stem) < 3 or stem[-3] not in vowels)):
            # Check if it's truly an open syllable by looking at the infinitive
            # In Dutch: lo-pen -> stem = loop (double the vowel)
            # but: vin-den -> stem = vind (closed syllable, no doubling)
            # The key test: if after the stem vowel there's only one consonant
            # before -en, it's an open syllable
            after_vowel = inf[inf.index(stem[-2]) + 1:]
            consonants_before_en = 0
            for c in after_vowel:
                if c in vowels:
                    break
                consonants_before_en += 1

            if consonants_before_en == 1:
                # Open syllable -> double the vowel
                stem = stem[:-1] + stem[-2] + stem[-1]

    # Rule: stem cannot end in double consonant of same letter: rennen -> ren (not renn)
    if len(stem) >= 2 and stem[-1] == stem[-2]:
        stem = stem[:-1]

    # Rule: stem ending in 'v' becomes 'f': leven -> leef
    if stem.endswith('v'):
        stem = stem[:-1] + 'f'

    # Rule: stem ending in 'z' becomes 's': lezen -> lees
    if stem.endswith('z'):
        stem = stem[:-1] + 's'

    return stem, particle


def generate_present_tense(infinitive: str) -> dict:
    """Generate tegenwoordige_tijd from infinitive using Dutch rules."""
    stem, particle = get_stem(infinitive)

    suffix = f' {particle}' if particle else ''

    # jij/hij form: stem + t (unless stem already ends in t)
    if stem.endswith('t'):
        jij_form = stem
    else:
        jij_form = stem + 't'

    return {
        'ik': f'{stem}{suffix}',
        'jij': f'{jij_form}{suffix}',
        'hij/zij/het': f'{jij_form}{suffix}',
        'wij': f'{infinitive}{suffix}'.replace(f'{suffix}{suffix}', suffix) if not particle else f'{infinitive.replace(particle, "").strip()}{suffix}' if particle else infinitive,
        'jullie': f'{infinitive}{suffix}'.replace(f'{suffix}{suffix}', suffix) if not particle else f'{infinitive.replace(particle, "").strip()}{suffix}' if particle else infinitive,
        'zij (pl)': f'{infinitive}{suffix}'.replace(f'{suffix}{suffix}', suffix) if not particle else f'{infinitive.replace(particle, "").strip()}{suffix}' if particle else infinitive,
    }


def generate_present_tense_simple(infinitive: str) -> dict:
    """Simplified present tense generation."""
    stem, particle = get_stem(infinitive)
    p = f' {particle}' if particle else ''

    # Get base verb (without particle) for plural forms
    if particle:
        base_verb = infinitive[len(particle):]
    else:
        base_verb = infinitive

    jij_form = stem if stem.endswith('t') else stem + 't'

    return {
        'ik': f'{stem}{p}',
        'jij': f'{jij_form}{p}',
        'hij/zij/het': f'{jij_form}{p}',
        'wij': f'{base_verb}{p}',
        'jullie': f'{base_verb}{p}',
        'zij (pl)': f'{base_verb}{p}',
    }


def escape_dart(s: str) -> str:
    return s.replace("'", "\\'").replace('$', r'\$')


def parse_pdf():
    """Parse the irregular verbs PDF."""
    pdf = pdfplumber.open(PDF_PATH)
    verbs = []

    for page in pdf.pages:
        text = page.extract_text()
        if not text:
            continue

        for line in text.split('\n'):
            line = line.strip()
            if not line or 'Frequente' in line or 'hele werkwoord' in line or '(imperfectum)' in line or 'Schrijven' in line or '©' in line:
                continue

            # Pattern: infinitive imp_sg/ imp_pl voltooid_deelwoord
            # The '/' separates singular and plural imperfectum
            m = re.match(r'^(.+?)\s+(.+?)/\s*(.+?)\s+(\S+)$', line)
            if not m:
                continue

            infinitive = m.group(1).strip()
            imp_sg = m.group(2).strip()
            imp_pl = m.group(3).strip()
            vd = m.group(4).strip()

            verbs.append({
                'infinitive': infinitive,
                'imperfectum_sg': imp_sg,
                'imperfectum_pl': imp_pl,
                'voltooid_deelwoord': vd,
            })

    return verbs


def main():
    verbs = parse_pdf()
    print(f'Parsed {len(verbs)} irregular verbs from PDF')

    # Filter out verbs that already exist
    new_verbs = []
    skipped = []
    for v in verbs:
        inf = v['infinitive'].lower()
        if inf in EXISTING_VERB_INFINITIVES:
            skipped.append(inf)
        else:
            new_verbs.append(v)

    print(f'Skipped {len(skipped)} already-existing verbs: {", ".join(sorted(skipped))}')
    print(f'New verbs to add: {len(new_verbs)}')

    # Generate Dart file
    lines = []
    lines.append("import '../models/verb_conjugation.dart';")
    lines.append("")
    lines.append("// ============================================================")
    lines.append(f"// Frequente onregelmatige werkwoorden")
    lines.append(f"// Total: {len(new_verbs)} irregular verbs")
    lines.append("// Source: Schrijven op B1 (Uitgeverij Boom 2015)")
    lines.append("// Tegenwoordige tijd auto-generated from Dutch conjugation rules")
    lines.append("// ============================================================")
    lines.append("")
    lines.append(f"final List<VerbConjugation> irregularVerbsList = [")

    for v in new_verbs:
        inf = v['infinitive']
        inf_lower = inf.lower()
        verb_id = f"irreg_{re.sub(r'[^a-z]', '_', inf_lower)}"
        uses_zijn = inf_lower in ZIJN_VERBS
        vd = v['voltooid_deelwoord']

        # Generate present tense
        tt = generate_present_tense_simple(inf_lower)

        lines.append(f"  const VerbConjugation(")
        lines.append(f"    id: '{verb_id}', infinitive: '{escape_dart(inf_lower)}',")
        lines.append(f"    isIrregular: true, usesZijn: {str(uses_zijn).lower()},")
        lines.append(f"    voltooidDeelwoord: '{escape_dart(vd)}',")
        lines.append(f"    tegenwoordigeTijd: {{")
        for person in ['ik', 'jij', 'hij/zij/het', 'wij', 'jullie', 'zij (pl)']:
            lines.append(f"      '{person}': '{escape_dart(tt[person])}',")
        lines.append(f"    }},")
        lines.append(f"    imperfectumSingular: '{escape_dart(v['imperfectum_sg'])}',")
        lines.append(f"    imperfectumPlural: '{escape_dart(v['imperfectum_pl'])}',")
        lines.append(f"  ),")

    lines.append("];")
    lines.append("")

    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    print(f'\nGenerated {OUTPUT_PATH}')
    print(f'Total irregular verbs: {len(new_verbs)}')

    # Show sample
    for v in new_verbs[:5]:
        tt = generate_present_tense_simple(v['infinitive'].lower())
        print(f"  {v['infinitive']:20s} ik={tt['ik']:15s} imp={v['imperfectum_sg']:15s} vd={v['voltooid_deelwoord']}")


if __name__ == '__main__':
    main()
