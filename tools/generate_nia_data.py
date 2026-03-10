#!/usr/bin/env python3
"""
Generate lib/data/textbooks/nia_data.dart from parsed NIA word list.
Nederlands in actie - 765 words (no chapter divisions, alphabetical).
"""

import json
import re
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

INPUT_FILE = 'tools/nia_full_parsed_with_sentences.json'
INPUT_FILE_FALLBACK = 'tools/nia_full_parsed.json'
OUTPUT_FILE = 'lib/data/textbooks/nia_data.dart'

def clean_english(eng: str) -> str:
    """Clean up English translation quirks."""
    # Fix broken parenthetical insertions: "to an(noun)ce" -> "to announce"
    fixes = {
        'to an(noun)ce': 'to announce',
        'to (adj)ust': 'to adjust',
        'finance(s)': 'finances',
        'cost(s)': 'costs',
    }
    for k, v in fixes.items():
        eng = eng.replace(k, v)
    return eng.strip()

def classify_word(dutch: str, english: str):
    """Determine part of speech and gender from the word."""
    dutch_lower = dutch.lower().strip()
    english_clean = english.strip()

    # Reflexive verbs: "aanmelden zich"
    if 'zich' in dutch_lower:
        return 'verb', 'none'

    # Explicit (noun) marker
    if '(noun)' in dutch_lower or '(noun)' in english_clean.lower():
        return 'noun', 'none'

    # Check English for verb pattern
    if english_clean.startswith('to '):
        return 'verb', 'none'

    # a) to ... b) ... pattern (verb with multiple meanings)
    if re.match(r'^a\)\s*to\s', english_clean):
        return 'verb', 'none'

    # Common adjective/adverb suffixes in Dutch
    adj_suffixes = ['lijk', 'ig', 'isch', 'baar', 'loos', 'vol', 'ief', 'eel', 'aal', 'eus']
    adv_words = ['achteraf', 'aldus', 'amper', 'andersom', 'bovendien', 'daarom', 'daardoor',
                 'daarna', 'desnoods', 'dus', 'eigenlijk', 'eveneens', 'gauw', 'gelukkig',
                 'helaas', 'hierbij', 'hierdoor', 'hierover', 'hopelijk', 'inmiddels',
                 'intussen', 'kortom', 'langzaam', 'liefst', 'misschien', 'namelijk',
                 'nauwelijks', 'ooit', 'opeens', 'opnieuw', 'overigens', 'pas', 'precies',
                 'sindsdien', 'slechts', 'sowieso', 'steeds', 'telkens', 'tenminste',
                 'tenslotte', 'terwijl', 'toch', 'uiteindelijk', 'uiteraard', 'vanwege',
                 'vervolgens', 'vlak', 'voortaan', 'vooruit', 'waarschijnlijk', 'weliswaar',
                 'zeker', 'zelfs', 'zolang', 'zomaar', 'zowel']

    if dutch_lower in adv_words:
        return 'adverb', 'none'

    for suf in adj_suffixes:
        if dutch_lower.endswith(suf):
            return 'adjective', 'none'

    # Prepositions
    preps = ['behalve', 'binnen', 'buiten', 'langs', 'midden', 'naast', 'ondanks',
             'richting', 'rondom', 'tijdens', 'vanuit', 'vanwege', 'via', 'volgens',
             'voorbij']
    if dutch_lower in preps:
        return 'preposition', 'none'

    # Conjunctions
    conjs = ['alsof', 'doordat', 'hoewel', 'mits', 'noch', 'ofwel', 'opdat',
             'terwijl', 'tenzij', 'waardoor', 'zodat', 'zodra', 'zolang']
    if dutch_lower in conjs:
        return 'conjunction', 'none'

    # Default: noun (most remaining words are nouns without de/het)
    return 'noun', 'none'

def escape_dart(s: str) -> str:
    """Escape string for Dart single-quoted string."""
    return s.replace("\\", "\\\\").replace("'", "\\'")

def make_id(dutch: str, index: int) -> str:
    """Create a unique ID for a word."""
    # Clean dutch word for ID
    clean = re.sub(r'[^a-z]', '_', dutch.lower().strip())
    clean = re.sub(r'_+', '_', clean).strip('_')
    return f'nia_{index+1:04d}'

POS_MAP = {
    'noun': 'PartOfSpeech.noun',
    'verb': 'PartOfSpeech.verb',
    'adjective': 'PartOfSpeech.adjective',
    'adverb': 'PartOfSpeech.adverb',
    'preposition': 'PartOfSpeech.preposition',
    'conjunction': 'PartOfSpeech.conjunction',
    'other': 'PartOfSpeech.other',
}

GENDER_MAP = {
    'de': 'Gender.de',
    'het': 'Gender.het',
    'none': 'Gender.none',
}

# ============================================================
# Common NIA verb conjugations
# These are verbs that appear in NIA and have useful conjugation practice
# ============================================================
NIA_VERB_CONJUGATIONS = {
    'accepteren': {
        'irregular': False, 'uses_zijn': False, 'voltooid_deelwoord': 'geaccepteerd',
        'tt': {'ik': 'accepteer', 'jij': 'accepteert', 'hij/zij/het': 'accepteert',
               'wij': 'accepteren', 'jullie': 'accepteren', 'zij (pl)': 'accepteren'},
        'imp_sg': 'accepteerde', 'imp_pl': 'accepteerden',
    },
    'adviseren': {
        'irregular': False, 'uses_zijn': False, 'voltooid_deelwoord': 'geadviseerd',
        'tt': {'ik': 'adviseer', 'jij': 'adviseert', 'hij/zij/het': 'adviseert',
               'wij': 'adviseren', 'jullie': 'adviseren', 'zij (pl)': 'adviseren'},
        'imp_sg': 'adviseerde', 'imp_pl': 'adviseerden',
    },
    'bepalen': {
        'irregular': False, 'uses_zijn': False, 'voltooid_deelwoord': 'bepaald',
        'tt': {'ik': 'bepaal', 'jij': 'bepaalt', 'hij/zij/het': 'bepaalt',
               'wij': 'bepalen', 'jullie': 'bepalen', 'zij (pl)': 'bepalen'},
        'imp_sg': 'bepaalde', 'imp_pl': 'bepaalden',
    },
    'beschrijven': {
        'irregular': True, 'uses_zijn': False, 'voltooid_deelwoord': 'beschreven',
        'tt': {'ik': 'beschrijf', 'jij': 'beschrijft', 'hij/zij/het': 'beschrijft',
               'wij': 'beschrijven', 'jullie': 'beschrijven', 'zij (pl)': 'beschrijven'},
        'imp_sg': 'beschreef', 'imp_pl': 'beschreven',
    },
    'bestaan': {
        'irregular': True, 'uses_zijn': False, 'voltooid_deelwoord': 'bestaan',
        'tt': {'ik': 'besta', 'jij': 'bestaat', 'hij/zij/het': 'bestaat',
               'wij': 'bestaan', 'jullie': 'bestaan', 'zij (pl)': 'bestaan'},
        'imp_sg': 'bestond', 'imp_pl': 'bestonden',
    },
    'besteden': {
        'irregular': False, 'uses_zijn': False, 'voltooid_deelwoord': 'besteed',
        'tt': {'ik': 'besteed', 'jij': 'besteedt', 'hij/zij/het': 'besteedt',
               'wij': 'besteden', 'jullie': 'besteden', 'zij (pl)': 'besteden'},
        'imp_sg': 'besteedde', 'imp_pl': 'besteedden',
    },
    'bevatten': {
        'irregular': False, 'uses_zijn': False, 'voltooid_deelwoord': 'bevat',
        'tt': {'ik': 'bevat', 'jij': 'bevat', 'hij/zij/het': 'bevat',
               'wij': 'bevatten', 'jullie': 'bevatten', 'zij (pl)': 'bevatten'},
        'imp_sg': 'bevatte', 'imp_pl': 'bevatten',
    },
    'bevinden_zich': {
        'irregular': True, 'uses_zijn': False, 'voltooid_deelwoord': 'bevonden',
        'tt': {'ik': 'bevind', 'jij': 'bevindt', 'hij/zij/het': 'bevindt',
               'wij': 'bevinden', 'jullie': 'bevinden', 'zij (pl)': 'bevinden'},
        'imp_sg': 'bevond', 'imp_pl': 'bevonden',
    },
    'beweren': {
        'irregular': False, 'uses_zijn': False, 'voltooid_deelwoord': 'beweerd',
        'tt': {'ik': 'beweer', 'jij': 'beweert', 'hij/zij/het': 'beweert',
               'wij': 'beweren', 'jullie': 'beweren', 'zij (pl)': 'beweren'},
        'imp_sg': 'beweerde', 'imp_pl': 'beweerden',
    },
    'bezitten': {
        'irregular': True, 'uses_zijn': False, 'voltooid_deelwoord': 'bezeten',
        'tt': {'ik': 'bezit', 'jij': 'bezit', 'hij/zij/het': 'bezit',
               'wij': 'bezitten', 'jullie': 'bezitten', 'zij (pl)': 'bezitten'},
        'imp_sg': 'bezat', 'imp_pl': 'bezaten',
    },
    'bijdragen': {
        'irregular': True, 'uses_zijn': False, 'voltooid_deelwoord': 'bijgedragen',
        'tt': {'ik': 'draag bij', 'jij': 'draagt bij', 'hij/zij/het': 'draagt bij',
               'wij': 'dragen bij', 'jullie': 'dragen bij', 'zij (pl)': 'dragen bij'},
        'imp_sg': 'droeg bij', 'imp_pl': 'droegen bij',
    },
    'blijken': {
        'irregular': True, 'uses_zijn': True, 'voltooid_deelwoord': 'gebleken',
        'tt': {'ik': 'blijk', 'jij': 'blijkt', 'hij/zij/het': 'blijkt',
               'wij': 'blijken', 'jullie': 'blijken', 'zij (pl)': 'blijken'},
        'imp_sg': 'bleek', 'imp_pl': 'bleken',
    },
    'dreigen': {
        'irregular': False, 'uses_zijn': False, 'voltooid_deelwoord': 'gedreigd',
        'tt': {'ik': 'dreig', 'jij': 'dreigt', 'hij/zij/het': 'dreigt',
               'wij': 'dreigen', 'jullie': 'dreigen', 'zij (pl)': 'dreigen'},
        'imp_sg': 'dreigde', 'imp_pl': 'dreigden',
    },
    'dwingen': {
        'irregular': True, 'uses_zijn': False, 'voltooid_deelwoord': 'gedwongen',
        'tt': {'ik': 'dwing', 'jij': 'dwingt', 'hij/zij/het': 'dwingt',
               'wij': 'dwingen', 'jullie': 'dwingen', 'zij (pl)': 'dwingen'},
        'imp_sg': 'dwong', 'imp_pl': 'dwongen',
    },
    'ervaren': {
        'irregular': True, 'uses_zijn': False, 'voltooid_deelwoord': 'ervaren',
        'tt': {'ik': 'ervaar', 'jij': 'ervaart', 'hij/zij/het': 'ervaart',
               'wij': 'ervaren', 'jullie': 'ervaren', 'zij (pl)': 'ervaren'},
        'imp_sg': 'ervoer', 'imp_pl': 'ervoeren',
    },
    'functioneren': {
        'irregular': False, 'uses_zijn': False, 'voltooid_deelwoord': 'gefunctioneerd',
        'tt': {'ik': 'functioneer', 'jij': 'functioneert', 'hij/zij/het': 'functioneert',
               'wij': 'functioneren', 'jullie': 'functioneren', 'zij (pl)': 'functioneren'},
        'imp_sg': 'functioneerde', 'imp_pl': 'functioneerden',
    },
    'gelden': {
        'irregular': True, 'uses_zijn': False, 'voltooid_deelwoord': 'gegolden',
        'tt': {'ik': 'geld', 'jij': 'geldt', 'hij/zij/het': 'geldt',
               'wij': 'gelden', 'jullie': 'gelden', 'zij (pl)': 'gelden'},
        'imp_sg': 'gold', 'imp_pl': 'golden',
    },
    'groeien': {
        'irregular': False, 'uses_zijn': True, 'voltooid_deelwoord': 'gegroeid',
        'tt': {'ik': 'groei', 'jij': 'groeit', 'hij/zij/het': 'groeit',
               'wij': 'groeien', 'jullie': 'groeien', 'zij (pl)': 'groeien'},
        'imp_sg': 'groeide', 'imp_pl': 'groeiden',
    },
    'herinneren_zich': {
        'irregular': False, 'uses_zijn': False, 'voltooid_deelwoord': 'herinnerd',
        'tt': {'ik': 'herinner', 'jij': 'herinnert', 'hij/zij/het': 'herinnert',
               'wij': 'herinneren', 'jullie': 'herinneren', 'zij (pl)': 'herinneren'},
        'imp_sg': 'herinnerde', 'imp_pl': 'herinnerden',
    },
    'invoeren': {
        'irregular': False, 'uses_zijn': False, 'voltooid_deelwoord': 'ingevoerd',
        'tt': {'ik': 'voer in', 'jij': 'voert in', 'hij/zij/het': 'voert in',
               'wij': 'voeren in', 'jullie': 'voeren in', 'zij (pl)': 'voeren in'},
        'imp_sg': 'voerde in', 'imp_pl': 'voerden in',
    },
    'leveren': {
        'irregular': False, 'uses_zijn': False, 'voltooid_deelwoord': 'geleverd',
        'tt': {'ik': 'lever', 'jij': 'levert', 'hij/zij/het': 'levert',
               'wij': 'leveren', 'jullie': 'leveren', 'zij (pl)': 'leveren'},
        'imp_sg': 'leverde', 'imp_pl': 'leverden',
    },
    'lijden': {
        'irregular': True, 'uses_zijn': False, 'voltooid_deelwoord': 'geleden',
        'tt': {'ik': 'lijd', 'jij': 'lijdt', 'hij/zij/het': 'lijdt',
               'wij': 'lijden', 'jullie': 'lijden', 'zij (pl)': 'lijden'},
        'imp_sg': 'leed', 'imp_pl': 'leden',
    },
    'meedoen': {
        'irregular': True, 'uses_zijn': False, 'voltooid_deelwoord': 'meegedaan',
        'tt': {'ik': 'doe mee', 'jij': 'doet mee', 'hij/zij/het': 'doet mee',
               'wij': 'doen mee', 'jullie': 'doen mee', 'zij (pl)': 'doen mee'},
        'imp_sg': 'deed mee', 'imp_pl': 'deden mee',
    },
    'meenemen': {
        'irregular': True, 'uses_zijn': False, 'voltooid_deelwoord': 'meegenomen',
        'tt': {'ik': 'neem mee', 'jij': 'neemt mee', 'hij/zij/het': 'neemt mee',
               'wij': 'nemen mee', 'jullie': 'nemen mee', 'zij (pl)': 'nemen mee'},
        'imp_sg': 'nam mee', 'imp_pl': 'namen mee',
    },
    'merken': {
        'irregular': False, 'uses_zijn': False, 'voltooid_deelwoord': 'gemerkt',
        'tt': {'ik': 'merk', 'jij': 'merkt', 'hij/zij/het': 'merkt',
               'wij': 'merken', 'jullie': 'merken', 'zij (pl)': 'merken'},
        'imp_sg': 'merkte', 'imp_pl': 'merkten',
    },
    'omgaan': {
        'irregular': True, 'uses_zijn': False, 'voltooid_deelwoord': 'omgegaan',
        'tt': {'ik': 'ga om', 'jij': 'gaat om', 'hij/zij/het': 'gaat om',
               'wij': 'gaan om', 'jullie': 'gaan om', 'zij (pl)': 'gaan om'},
        'imp_sg': 'ging om', 'imp_pl': 'gingen om',
    },
    'ondernemen': {
        'irregular': True, 'uses_zijn': False, 'voltooid_deelwoord': 'ondernomen',
        'tt': {'ik': 'onderneem', 'jij': 'onderneemt', 'hij/zij/het': 'onderneemt',
               'wij': 'ondernemen', 'jullie': 'ondernemen', 'zij (pl)': 'ondernemen'},
        'imp_sg': 'ondernam', 'imp_pl': 'ondernamen',
    },
    'onderzoeken': {
        'irregular': True, 'uses_zijn': False, 'voltooid_deelwoord': 'onderzocht',
        'tt': {'ik': 'onderzoek', 'jij': 'onderzoekt', 'hij/zij/het': 'onderzoekt',
               'wij': 'onderzoeken', 'jullie': 'onderzoeken', 'zij (pl)': 'onderzoeken'},
        'imp_sg': 'onderzocht', 'imp_pl': 'onderzochten',
    },
    'ontwikkelen': {
        'irregular': False, 'uses_zijn': False, 'voltooid_deelwoord': 'ontwikkeld',
        'tt': {'ik': 'ontwikkel', 'jij': 'ontwikkelt', 'hij/zij/het': 'ontwikkelt',
               'wij': 'ontwikkelen', 'jullie': 'ontwikkelen', 'zij (pl)': 'ontwikkelen'},
        'imp_sg': 'ontwikkelde', 'imp_pl': 'ontwikkelden',
    },
    'opgroeien': {
        'irregular': False, 'uses_zijn': True, 'voltooid_deelwoord': 'opgegroeid',
        'tt': {'ik': 'groei op', 'jij': 'groeit op', 'hij/zij/het': 'groeit op',
               'wij': 'groeien op', 'jullie': 'groeien op', 'zij (pl)': 'groeien op'},
        'imp_sg': 'groeide op', 'imp_pl': 'groeiden op',
    },
    'oplossen': {
        'irregular': False, 'uses_zijn': False, 'voltooid_deelwoord': 'opgelost',
        'tt': {'ik': 'los op', 'jij': 'lost op', 'hij/zij/het': 'lost op',
               'wij': 'lossen op', 'jullie': 'lossen op', 'zij (pl)': 'lossen op'},
        'imp_sg': 'loste op', 'imp_pl': 'losten op',
    },
    'opvallen': {
        'irregular': True, 'uses_zijn': True, 'voltooid_deelwoord': 'opgevallen',
        'tt': {'ik': 'val op', 'jij': 'valt op', 'hij/zij/het': 'valt op',
               'wij': 'vallen op', 'jullie': 'vallen op', 'zij (pl)': 'vallen op'},
        'imp_sg': 'viel op', 'imp_pl': 'vielen op',
    },
    'overleggen': {
        'irregular': False, 'uses_zijn': False, 'voltooid_deelwoord': 'overlegd',
        'tt': {'ik': 'overleg', 'jij': 'overlegt', 'hij/zij/het': 'overlegt',
               'wij': 'overleggen', 'jullie': 'overleggen', 'zij (pl)': 'overleggen'},
        'imp_sg': 'overlegde', 'imp_pl': 'overlegden',
    },
    'plaatsvinden': {
        'irregular': True, 'uses_zijn': False, 'voltooid_deelwoord': 'plaatsgevonden',
        'tt': {'ik': 'vind plaats', 'jij': 'vindt plaats', 'hij/zij/het': 'vindt plaats',
               'wij': 'vinden plaats', 'jullie': 'vinden plaats', 'zij (pl)': 'vinden plaats'},
        'imp_sg': 'vond plaats', 'imp_pl': 'vonden plaats',
    },
    'scheiden': {
        'irregular': True, 'uses_zijn': False, 'voltooid_deelwoord': 'gescheiden',
        'tt': {'ik': 'scheid', 'jij': 'scheidt', 'hij/zij/het': 'scheidt',
               'wij': 'scheiden', 'jullie': 'scheiden', 'zij (pl)': 'scheiden'},
        'imp_sg': 'scheidde', 'imp_pl': 'scheidden',
    },
    'slagen': {
        'irregular': False, 'uses_zijn': True, 'voltooid_deelwoord': 'geslaagd',
        'tt': {'ik': 'slaag', 'jij': 'slaagt', 'hij/zij/het': 'slaagt',
               'wij': 'slagen', 'jullie': 'slagen', 'zij (pl)': 'slagen'},
        'imp_sg': 'slaagde', 'imp_pl': 'slaagden',
    },
    'steunen': {
        'irregular': False, 'uses_zijn': False, 'voltooid_deelwoord': 'gesteund',
        'tt': {'ik': 'steun', 'jij': 'steunt', 'hij/zij/het': 'steunt',
               'wij': 'steunen', 'jullie': 'steunen', 'zij (pl)': 'steunen'},
        'imp_sg': 'steunde', 'imp_pl': 'steunden',
    },
    'stichten': {
        'irregular': False, 'uses_zijn': False, 'voltooid_deelwoord': 'gesticht',
        'tt': {'ik': 'sticht', 'jij': 'sticht', 'hij/zij/het': 'sticht',
               'wij': 'stichten', 'jullie': 'stichten', 'zij (pl)': 'stichten'},
        'imp_sg': 'stichtte', 'imp_pl': 'stichtten',
    },
    'toenemen': {
        'irregular': True, 'uses_zijn': True, 'voltooid_deelwoord': 'toegenomen',
        'tt': {'ik': 'neem toe', 'jij': 'neemt toe', 'hij/zij/het': 'neemt toe',
               'wij': 'nemen toe', 'jullie': 'nemen toe', 'zij (pl)': 'nemen toe'},
        'imp_sg': 'nam toe', 'imp_pl': 'namen toe',
    },
    'toepassen': {
        'irregular': False, 'uses_zijn': False, 'voltooid_deelwoord': 'toegepast',
        'tt': {'ik': 'pas toe', 'jij': 'past toe', 'hij/zij/het': 'past toe',
               'wij': 'passen toe', 'jullie': 'passen toe', 'zij (pl)': 'passen toe'},
        'imp_sg': 'paste toe', 'imp_pl': 'pasten toe',
    },
    'uitvoeren': {
        'irregular': False, 'uses_zijn': False, 'voltooid_deelwoord': 'uitgevoerd',
        'tt': {'ik': 'voer uit', 'jij': 'voert uit', 'hij/zij/het': 'voert uit',
               'wij': 'voeren uit', 'jullie': 'voeren uit', 'zij (pl)': 'voeren uit'},
        'imp_sg': 'voerde uit', 'imp_pl': 'voerden uit',
    },
    'verbieden': {
        'irregular': True, 'uses_zijn': False, 'voltooid_deelwoord': 'verboden',
        'tt': {'ik': 'verbied', 'jij': 'verbiedt', 'hij/zij/het': 'verbiedt',
               'wij': 'verbieden', 'jullie': 'verbieden', 'zij (pl)': 'verbieden'},
        'imp_sg': 'verbood', 'imp_pl': 'verboden',
    },
    'verdwijnen': {
        'irregular': True, 'uses_zijn': True, 'voltooid_deelwoord': 'verdwenen',
        'tt': {'ik': 'verdwijn', 'jij': 'verdwijnt', 'hij/zij/het': 'verdwijnt',
               'wij': 'verdwijnen', 'jullie': 'verdwijnen', 'zij (pl)': 'verdwijnen'},
        'imp_sg': 'verdween', 'imp_pl': 'verdwenen',
    },
    'vergelijken': {
        'irregular': True, 'uses_zijn': False, 'voltooid_deelwoord': 'vergeleken',
        'tt': {'ik': 'vergelijk', 'jij': 'vergelijkt', 'hij/zij/het': 'vergelijkt',
               'wij': 'vergelijken', 'jullie': 'vergelijken', 'zij (pl)': 'vergelijken'},
        'imp_sg': 'vergeleek', 'imp_pl': 'vergeleken',
    },
    'verlangen': {
        'irregular': False, 'uses_zijn': False, 'voltooid_deelwoord': 'verlangd',
        'tt': {'ik': 'verlang', 'jij': 'verlangt', 'hij/zij/het': 'verlangt',
               'wij': 'verlangen', 'jullie': 'verlangen', 'zij (pl)': 'verlangen'},
        'imp_sg': 'verlangde', 'imp_pl': 'verlangden',
    },
    'vermijden': {
        'irregular': True, 'uses_zijn': False, 'voltooid_deelwoord': 'vermeden',
        'tt': {'ik': 'vermijd', 'jij': 'vermijdt', 'hij/zij/het': 'vermijdt',
               'wij': 'vermijden', 'jullie': 'vermijden', 'zij (pl)': 'vermijden'},
        'imp_sg': 'vermeed', 'imp_pl': 'vermeden',
    },
    'verschijnen': {
        'irregular': True, 'uses_zijn': True, 'voltooid_deelwoord': 'verschenen',
        'tt': {'ik': 'verschijn', 'jij': 'verschijnt', 'hij/zij/het': 'verschijnt',
               'wij': 'verschijnen', 'jullie': 'verschijnen', 'zij (pl)': 'verschijnen'},
        'imp_sg': 'verscheen', 'imp_pl': 'verschenen',
    },
    'vertrouwen': {
        'irregular': False, 'uses_zijn': False, 'voltooid_deelwoord': 'vertrouwd',
        'tt': {'ik': 'vertrouw', 'jij': 'vertrouwt', 'hij/zij/het': 'vertrouwt',
               'wij': 'vertrouwen', 'jullie': 'vertrouwen', 'zij (pl)': 'vertrouwen'},
        'imp_sg': 'vertrouwde', 'imp_pl': 'vertrouwden',
    },
    'verwachten': {
        'irregular': False, 'uses_zijn': False, 'voltooid_deelwoord': 'verwacht',
        'tt': {'ik': 'verwacht', 'jij': 'verwacht', 'hij/zij/het': 'verwacht',
               'wij': 'verwachten', 'jullie': 'verwachten', 'zij (pl)': 'verwachten'},
        'imp_sg': 'verwachtte', 'imp_pl': 'verwachtten',
    },
    'voorkomen': {
        'irregular': True, 'uses_zijn': False, 'voltooid_deelwoord': 'voorkomen',
        'tt': {'ik': 'voorkom', 'jij': 'voorkomt', 'hij/zij/het': 'voorkomt',
               'wij': 'voorkomen', 'jullie': 'voorkomen', 'zij (pl)': 'voorkomen'},
        'imp_sg': 'voorkwam', 'imp_pl': 'voorkwamen',
    },
    'voorstellen': {
        'irregular': False, 'uses_zijn': False, 'voltooid_deelwoord': 'voorgesteld',
        'tt': {'ik': 'stel voor', 'jij': 'stelt voor', 'hij/zij/het': 'stelt voor',
               'wij': 'stellen voor', 'jullie': 'stellen voor', 'zij (pl)': 'stellen voor'},
        'imp_sg': 'stelde voor', 'imp_pl': 'stelden voor',
    },
    'wijzen': {
        'irregular': True, 'uses_zijn': False, 'voltooid_deelwoord': 'gewezen',
        'tt': {'ik': 'wijs', 'jij': 'wijst', 'hij/zij/het': 'wijst',
               'wij': 'wijzen', 'jullie': 'wijzen', 'zij (pl)': 'wijzen'},
        'imp_sg': 'wees', 'imp_pl': 'wezen',
    },
}


def get_verb_id(dutch: str) -> str:
    """Get verb_id if this verb has conjugation data."""
    # Normalize: "aanmelden zich" -> "aanmelden_zich"
    clean = dutch.lower().strip()
    # Handle "X zich" -> "X_zich"
    if ' zich' in clean:
        clean = clean.replace(' zich', '_zich')
    # Remove "zich " prefix
    if clean.startswith('zich '):
        clean = clean[5:] + '_zich'

    if clean in NIA_VERB_CONJUGATIONS:
        return f'verb_nia_{clean}'
    return None


def main():
    import os
    path = INPUT_FILE if os.path.exists(INPUT_FILE) else INPUT_FILE_FALLBACK
    print(f"Reading from: {path}")
    with open(path, 'r', encoding='utf-8') as f:
        entries = json.load(f)

    lines = []
    lines.append("import '../models/word.dart';")
    lines.append("import '../models/verb_conjugation.dart';")
    lines.append("")
    lines.append("// ============================================================")
    lines.append("// Nederlands in actie - Frequente woorden")
    lines.append(f"// Total: {len(entries)} words (De 5000 frequentste woorden)")
    lines.append("// Generated from: Bijlage-8-Frequente woorden.xlsx")
    lines.append("// Includes: NIA words, NIG words, and other frequent Dutch words")
    lines.append("// Example sentences are auto-generated")
    lines.append("// ============================================================")
    lines.append("")

    # Generate word list
    lines.append(f"final List<Word> niaAllWords = [")

    pos_counts = {}
    verb_count = 0

    for i, entry in enumerate(entries):
        dutch = entry['dutch'].strip()
        english = clean_english(entry['english'])
        pos, gender = classify_word(dutch, english)

        pos_counts[pos] = pos_counts.get(pos, 0) + 1

        word_id = f'nia_{i+1:04d}'

        # Check for verb conjugation
        verb_id = None
        if pos == 'verb':
            verb_id = get_verb_id(dutch)
            if verb_id:
                verb_count += 1

        # Build word entry
        esc_dutch = escape_dart(dutch)
        esc_english = escape_dart(english)
        # Use generated sentence if available
        sentence = entry.get('example_nl', f'{dutch.split(",")[0].split("(")[0].strip()} is een belangrijk woord.')
        sent_trans = entry.get('example_en', f'{english.split(",")[0].split("(")[0].strip()} is an important word.')

        line = f"  const Word("
        line += f"\n    id: '{word_id}', dutch: '{esc_dutch}', english: '{esc_english}', chinese: '',"
        line += f"\n    exampleSentence: '{escape_dart(sentence)}',"
        line += f"\n    exampleTranslation: '{escape_dart(sent_trans)}',"
        line += f"\n    partOfSpeech: {POS_MAP[pos]},"
        if gender != 'none':
            line += f" gender: {GENDER_MAP[gender]},"
        line += f" textbookId: 'nia', chapter: 0,"
        if verb_id:
            line += f" verbId: '{verb_id}',"
        line += f"\n  ),"
        lines.append(line)

    lines.append("];")
    lines.append("")

    # Generate verb conjugation list
    lines.append(f"final List<VerbConjugation> niaAllVerbs = [")

    for verb_name, data in NIA_VERB_CONJUGATIONS.items():
        verb_id = f'verb_nia_{verb_name}'
        infinitive = verb_name.replace('_zich', ' zich').replace('_', ' ')

        lines.append(f"  const VerbConjugation(")
        lines.append(f"    id: '{verb_id}', infinitive: '{escape_dart(infinitive)}',")
        lines.append(f"    isIrregular: {str(data['irregular']).lower()}, usesZijn: {str(data['uses_zijn']).lower()},")
        lines.append(f"    voltooidDeelwoord: '{escape_dart(data['voltooid_deelwoord'])}',")

        # Tegenwoordige tijd
        tt = data['tt']
        lines.append(f"    tegenwoordigeTijd: {{")
        for person in ['ik', 'jij', 'hij/zij/het', 'wij', 'jullie', 'zij (pl)']:
            lines.append(f"      '{person}': '{escape_dart(tt[person])}',")
        lines.append(f"    }},")

        # Imperfectum
        lines.append(f"    imperfectumSingular: '{escape_dart(data['imp_sg'])}',")
        lines.append(f"    imperfectumPlural: '{escape_dart(data['imp_pl'])}',")

        lines.append(f"  ),")

    lines.append("];")
    lines.append("")

    # Write output
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    print(f"Generated {OUTPUT_FILE}")
    print(f"Total words: {len(entries)}")
    print(f"Part of speech distribution: {pos_counts}")
    print(f"Verbs with conjugation data: {verb_count}")
    print(f"Total verb conjugation tables: {len(NIA_VERB_CONJUGATIONS)}")


if __name__ == '__main__':
    main()
