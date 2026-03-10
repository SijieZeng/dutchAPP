"""
Generate Dart data file from parsed woordenlijst JSON.
"""
import json
import sys
import io
import re

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

INPUT_PATH = 'c:/Users/Sijie/dutchapp/tools/nig_parsed_with_sentences.json'
INPUT_PATH_FALLBACK = 'c:/Users/Sijie/dutchapp/tools/nig_parsed.json'
OUTPUT_PATH = 'c:/Users/Sijie/dutchapp/lib/data/textbooks/nig_data.dart'

def escape_dart(s):
    """Escape string for Dart single-quoted string."""
    return s.replace("'", "\\'").replace('$', r'\$')

def determine_pos(entry):
    """Determine part of speech."""
    if entry['is_verb']:
        return 'PartOfSpeech.verb'
    if entry['gender'] == 'de':
        return 'PartOfSpeech.noun'
    if entry['gender'] == 'het':
        return 'PartOfSpeech.noun'

    english = entry['english'].lower()
    # Common adjective endings
    if any(english.endswith(x) for x in ['ful', 'ous', 'ive', 'ble', 'tic', 'ish', 'ant', 'ent']):
        return 'PartOfSpeech.adjective'

    return 'PartOfSpeech.other'

def determine_gender(entry):
    if entry['gender'] == 'de':
        return 'Gender.de'
    if entry['gender'] == 'het':
        return 'Gender.het'
    return 'Gender.none'

def make_id(textbook_id, chapter, index):
    return f'{textbook_id}_h{chapter}_{index:03d}'

def make_verb_id(dutch):
    """Create a verb ID from the Dutch infinitive."""
    clean = dutch.lower().strip()
    clean = re.sub(r'[^a-z]', '_', clean)
    return f'verb_{clean}'

def main():
    import os
    path = INPUT_PATH if os.path.exists(INPUT_PATH) else INPUT_PATH_FALLBACK
    print(f"Reading from: {path}")
    with open(path, 'r', encoding='utf-8') as f:
        entries = json.load(f)

    # Filter: only chapters 1-18, skip garbage entries
    valid = []
    for e in entries:
        ch = e['primary_chapter']
        if ch < 1 or ch > 18:
            continue
        # Skip entries that are clearly not words
        dutch = e['dutch'].strip()
        if len(dutch) < 2:
            continue
        if dutch.startswith('©') or dutch.startswith('Uitgeverij') or dutch.startswith('ISBN'):
            continue
        if not e['english'] or len(e['english']) < 1:
            continue
        valid.append(e)

    # Organize by chapter
    by_chapter = {}
    for e in valid:
        ch = e['primary_chapter']
        if ch not in by_chapter:
            by_chapter[ch] = []
        by_chapter[ch].append(e)

    # Stats
    total = len(valid)
    print(f"Total valid entries: {total}")
    for ch in sorted(by_chapter.keys()):
        print(f"  H{ch}: {len(by_chapter[ch])} words")

    # Generate Dart code
    lines = []
    lines.append("import '../models/word.dart';")
    lines.append("import '../models/verb_conjugation.dart';")
    lines.append("")
    lines.append("// ============================================================")
    lines.append("// Nederlands in gang - Complete Woordenlijst")
    lines.append(f"// Total: {total} words across {len(by_chapter)} chapters")
    lines.append("// Generated from: nig-woordenlijst-nl-eng-totaal.pdf")
    lines.append("// Example sentences are auto-generated")
    lines.append("// ============================================================")
    lines.append("")

    all_verb_ids = set()

    for ch in sorted(by_chapter.keys()):
        words = by_chapter[ch]
        var_name = f'nigH{ch}Words'
        lines.append(f"// ------ Hoofdstuk {ch} ({len(words)} words) ------")
        lines.append(f"final List<Word> {var_name} = [")

        for idx, e in enumerate(words, 1):
            word_id = make_id('nig', ch, idx)
            dutch = escape_dart(e['dutch'])
            english = escape_dart(e['english'])
            pos = determine_pos(e)
            gender = determine_gender(e)

            verb_id_str = ''
            if e['is_verb']:
                vid = make_verb_id(e['dutch'])
                all_verb_ids.add(vid)
                verb_id_str = f", verbId: '{vid}'"

            gender_str = f', gender: {gender}' if gender != 'Gender.none' else ''

            # Use generated sentence if available, otherwise placeholder
            sentence = e.get('example_nl', f'{e["dutch"].capitalize()} is een belangrijk woord.')
            sent_trans = e.get('example_en', f'{e["english"].capitalize()} is an important word.')

            lines.append(f"  const Word(")
            lines.append(f"    id: '{word_id}', dutch: '{dutch}', english: '{english}', chinese: '',")
            lines.append(f"    exampleSentence: '{escape_dart(sentence)}',")
            lines.append(f"    exampleTranslation: '{escape_dart(sent_trans)}',")
            lines.append(f"    partOfSpeech: {pos}{gender_str}, textbookId: 'nig', chapter: {ch}{verb_id_str},")
            lines.append(f"  ),")

        lines.append("];")
        lines.append("")

    # Combined list
    lines.append("// === Combined data for all chapters ===")
    lines.append("final List<Word> nigAllWords = [")
    for ch in sorted(by_chapter.keys()):
        lines.append(f"  ...nigH{ch}Words,")
    lines.append("];")
    lines.append("")

    # Verb conjugations placeholder
    lines.append("// === Verb conjugations ===")
    lines.append("// NOTE: Only common verbs have full conjugation data.")
    lines.append("// The rest will be added incrementally.")
    lines.append("final List<VerbConjugation> nigAllVerbs = [")

    # Include conjugations for the most important/common verbs
    common_verbs = {
        'verb_zijn': ('zijn', True, True, 'geweest',
            {'ik': 'ben', 'jij': 'bent', 'hij/zij/het': 'is', 'wij': 'zijn', 'jullie': 'zijn', 'zij (pl)': 'zijn'},
            'was', 'waren', 'Zeer onregelmatig werkwoord!'),
        'verb_hebben': ('hebben', True, False, 'gehad',
            {'ik': 'heb', 'jij': 'hebt', 'hij/zij/het': 'heeft', 'wij': 'hebben', 'jullie': 'hebben', 'zij (pl)': 'hebben'},
            'had', 'hadden', 'Onregelmatig werkwoord!'),
        'verb_komen': ('komen', True, True, 'gekomen',
            {'ik': 'kom', 'jij': 'komt', 'hij/zij/het': 'komt', 'wij': 'komen', 'jullie': 'komen', 'zij (pl)': 'komen'},
            'kwam', 'kwamen', 'Sterk werkwoord! Imperfectum: kwam/kwamen'),
        'verb_gaan': ('gaan', True, True, 'gegaan',
            {'ik': 'ga', 'jij': 'gaat', 'hij/zij/het': 'gaat', 'wij': 'gaan', 'jullie': 'gaan', 'zij (pl)': 'gaan'},
            'ging', 'gingen', 'Sterk werkwoord! Imperfectum: ging/gingen'),
        'verb_doen': ('doen', True, False, 'gedaan',
            {'ik': 'doe', 'jij': 'doet', 'hij/zij/het': 'doet', 'wij': 'doen', 'jullie': 'doen', 'zij (pl)': 'doen'},
            'deed', 'deden', 'Sterk werkwoord! Imperfectum: deed/deden'),
        'verb_kunnen': ('kunnen', True, False, 'gekund',
            {'ik': 'kan', 'jij': 'kan/kunt', 'hij/zij/het': 'kan', 'wij': 'kunnen', 'jullie': 'kunnen', 'zij (pl)': 'kunnen'},
            'kon', 'konden', 'Modaal werkwoord!'),
        'verb_willen': ('willen', True, False, 'gewild',
            {'ik': 'wil', 'jij': 'wil/wilt', 'hij/zij/het': 'wil', 'wij': 'willen', 'jullie': 'willen', 'zij (pl)': 'willen'},
            'wilde/wou', 'wilden', 'Modaal werkwoord!'),
        'verb_moeten': ('moeten', True, False, 'gemoeten',
            {'ik': 'moet', 'jij': 'moet', 'hij/zij/het': 'moet', 'wij': 'moeten', 'jullie': 'moeten', 'zij (pl)': 'moeten'},
            'moest', 'moesten', 'Modaal werkwoord!'),
        'verb_mogen': ('mogen', True, False, 'gemogen',
            {'ik': 'mag', 'jij': 'mag', 'hij/zij/het': 'mag', 'wij': 'mogen', 'jullie': 'mogen', 'zij (pl)': 'mogen'},
            'mocht', 'mochten', 'Modaal werkwoord!'),
        'verb_zullen': ('zullen', True, False, '-',
            {'ik': 'zal', 'jij': 'zal/zult', 'hij/zij/het': 'zal', 'wij': 'zullen', 'jullie': 'zullen', 'zij (pl)': 'zullen'},
            'zou', 'zouden', 'Modaal werkwoord!'),
        'verb_wonen': ('wonen', False, False, 'gewoond',
            {'ik': 'woon', 'jij': 'woont', 'hij/zij/het': 'woont', 'wij': 'wonen', 'jullie': 'wonen', 'zij (pl)': 'wonen'},
            'woonde', 'woonden', None),
        'verb_werken': ('werken', False, False, 'gewerkt',
            {'ik': 'werk', 'jij': 'werkt', 'hij/zij/het': 'werkt', 'wij': 'werken', 'jullie': 'werken', 'zij (pl)': 'werken'},
            'werkte', 'werkten', None),
        'verb_heten': ('heten', False, False, 'geheten',
            {'ik': 'heet', 'jij': 'heet', 'hij/zij/het': 'heet', 'wij': 'heten', 'jullie': 'heten', 'zij (pl)': 'heten'},
            'heette', 'heetten', None),
        'verb_lezen': ('lezen', True, False, 'gelezen',
            {'ik': 'lees', 'jij': 'leest', 'hij/zij/het': 'leest', 'wij': 'lezen', 'jullie': 'lezen', 'zij (pl)': 'lezen'},
            'las', 'lazen', 'Sterk werkwoord! Imperfectum: las/lazen'),
        'verb_beginnen': ('beginnen', True, True, 'begonnen',
            {'ik': 'begin', 'jij': 'begint', 'hij/zij/het': 'begint', 'wij': 'beginnen', 'jullie': 'beginnen', 'zij (pl)': 'beginnen'},
            'begon', 'begonnen', 'Sterk werkwoord! Imperfectum: begon/begonnen'),
        'verb_eten': ('eten', True, False, 'gegeten',
            {'ik': 'eet', 'jij': 'eet', 'hij/zij/het': 'eet', 'wij': 'eten', 'jullie': 'eten', 'zij (pl)': 'eten'},
            'at', 'aten', 'Sterk werkwoord! Imperfectum: at/aten'),
        'verb_drinken': ('drinken', True, False, 'gedronken',
            {'ik': 'drink', 'jij': 'drinkt', 'hij/zij/het': 'drinkt', 'wij': 'drinken', 'jullie': 'drinken', 'zij (pl)': 'drinken'},
            'dronk', 'dronken', 'Sterk werkwoord! Imperfectum: dronk/dronken'),
        'verb_geven': ('geven', True, False, 'gegeven',
            {'ik': 'geef', 'jij': 'geeft', 'hij/zij/het': 'geeft', 'wij': 'geven', 'jullie': 'geven', 'zij (pl)': 'geven'},
            'gaf', 'gaven', 'Sterk werkwoord! Imperfectum: gaf/gaven'),
        'verb_nemen': ('nemen', True, False, 'genomen',
            {'ik': 'neem', 'jij': 'neemt', 'hij/zij/het': 'neemt', 'wij': 'nemen', 'jullie': 'nemen', 'zij (pl)': 'nemen'},
            'nam', 'namen', 'Sterk werkwoord! Imperfectum: nam/namen'),
        'verb_kopen': ('kopen', True, False, 'gekocht',
            {'ik': 'koop', 'jij': 'koopt', 'hij/zij/het': 'koopt', 'wij': 'kopen', 'jullie': 'kopen', 'zij (pl)': 'kopen'},
            'kocht', 'kochten', 'Sterk werkwoord! Imperfectum: kocht/kochten'),
        'verb_zeggen': ('zeggen', True, False, 'gezegd',
            {'ik': 'zeg', 'jij': 'zegt', 'hij/zij/het': 'zegt', 'wij': 'zeggen', 'jullie': 'zeggen', 'zij (pl)': 'zeggen'},
            'zei', 'zeiden', 'Sterk werkwoord! Imperfectum: zei/zeiden'),
        'verb_vinden': ('vinden', True, False, 'gevonden',
            {'ik': 'vind', 'jij': 'vindt', 'hij/zij/het': 'vindt', 'wij': 'vinden', 'jullie': 'vinden', 'zij (pl)': 'vinden'},
            'vond', 'vonden', 'Sterk werkwoord! Imperfectum: vond/vonden'),
        'verb_weten': ('weten', True, False, 'geweten',
            {'ik': 'weet', 'jij': 'weet', 'hij/zij/het': 'weet', 'wij': 'weten', 'jullie': 'weten', 'zij (pl)': 'weten'},
            'wist', 'wisten', 'Sterk werkwoord! Imperfectum: wist/wisten'),
        'verb_zien': ('zien', True, False, 'gezien',
            {'ik': 'zie', 'jij': 'ziet', 'hij/zij/het': 'ziet', 'wij': 'zien', 'jullie': 'zien', 'zij (pl)': 'zien'},
            'zag', 'zagen', 'Sterk werkwoord! Imperfectum: zag/zagen'),
        'verb_schrijven': ('schrijven', True, False, 'geschreven',
            {'ik': 'schrijf', 'jij': 'schrijft', 'hij/zij/het': 'schrijft', 'wij': 'schrijven', 'jullie': 'schrijven', 'zij (pl)': 'schrijven'},
            'schreef', 'schreven', 'Sterk werkwoord! Imperfectum: schreef/schreven'),
        'verb_spreken': ('spreken', True, False, 'gesproken',
            {'ik': 'spreek', 'jij': 'spreekt', 'hij/zij/het': 'spreekt', 'wij': 'spreken', 'jullie': 'spreken', 'zij (pl)': 'spreken'},
            'sprak', 'spraken', 'Sterk werkwoord! Imperfectum: sprak/spraken'),
        'verb_staan': ('staan', True, False, 'gestaan',
            {'ik': 'sta', 'jij': 'staat', 'hij/zij/het': 'staat', 'wij': 'staan', 'jullie': 'staan', 'zij (pl)': 'staan'},
            'stond', 'stonden', 'Sterk werkwoord! Imperfectum: stond/stonden'),
        'verb_zitten': ('zitten', True, False, 'gezeten',
            {'ik': 'zit', 'jij': 'zit', 'hij/zij/het': 'zit', 'wij': 'zitten', 'jullie': 'zitten', 'zij (pl)': 'zitten'},
            'zat', 'zaten', 'Sterk werkwoord! Imperfectum: zat/zaten'),
        'verb_liggen': ('liggen', True, False, 'gelegen',
            {'ik': 'lig', 'jij': 'ligt', 'hij/zij/het': 'ligt', 'wij': 'liggen', 'jullie': 'liggen', 'zij (pl)': 'liggen'},
            'lag', 'lagen', 'Sterk werkwoord! Imperfectum: lag/lagen'),
        'verb_rijden': ('rijden', True, False, 'gereden',
            {'ik': 'rijd', 'jij': 'rijdt', 'hij/zij/het': 'rijdt', 'wij': 'rijden', 'jullie': 'rijden', 'zij (pl)': 'rijden'},
            'reed', 'reden', 'Sterk werkwoord! Imperfectum: reed/reden'),
        'verb_brengen': ('brengen', True, False, 'gebracht',
            {'ik': 'breng', 'jij': 'brengt', 'hij/zij/het': 'brengt', 'wij': 'brengen', 'jullie': 'brengen', 'zij (pl)': 'brengen'},
            'bracht', 'brachten', 'Sterk werkwoord! Imperfectum: bracht/brachten'),
        'verb_denken': ('denken', True, False, 'gedacht',
            {'ik': 'denk', 'jij': 'denkt', 'hij/zij/het': 'denkt', 'wij': 'denken', 'jullie': 'denken', 'zij (pl)': 'denken'},
            'dacht', 'dachten', 'Sterk werkwoord! Imperfectum: dacht/dachten'),
    }

    for vid, data in common_verbs.items():
        inf, irreg, uses_zijn, vd, tt, imp_s, imp_p, hint = data
        lines.append(f"  const VerbConjugation(")
        lines.append(f"    id: '{vid}', infinitive: '{escape_dart(inf)}',")
        lines.append(f"    isIrregular: {str(irreg).lower()}, usesZijn: {str(uses_zijn).lower()},")
        lines.append(f"    voltooidDeelwoord: '{escape_dart(vd)}',")
        lines.append(f"    tegenwoordigeTijd: {{")
        for person, form in tt.items():
            lines.append(f"      '{person}': '{escape_dart(form)}',")
        lines.append(f"    }},")
        lines.append(f"    imperfectumSingular: '{escape_dart(imp_s)}',")
        lines.append(f"    imperfectumPlural: '{escape_dart(imp_p)}',")
        if hint:
            lines.append(f"    irregularHint: '{escape_dart(hint)}',")
        lines.append(f"  ),")

    lines.append("];")

    # Write output
    dart_code = '\n'.join(lines) + '\n'
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        f.write(dart_code)

    print(f"\nGenerated {OUTPUT_PATH}")
    print(f"Total words: {total}")
    print(f"Common verb conjugations: {len(common_verbs)}")

if __name__ == '__main__':
    main()
