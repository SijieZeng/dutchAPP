#!/usr/bin/env python3
"""
Generate contextual example sentences for all NIG and NIA words.
Outputs updated JSON files with sentences added.
"""

import json
import re
import sys
import io
import random

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

random.seed(42)  # Reproducible results

# ============================================================
# Sentence templates by part of speech
# Each template is (dutch_template, english_template)
# {word} = the Dutch word, {eng} = English translation
# ============================================================

NOUN_TEMPLATES = [
    ("Ik heb een goede {word} nodig.", "I need a good {eng}."),
    ("De {word} is erg belangrijk.", "The {eng} is very important."),
    ("Heb jij een {word} gezien?", "Have you seen a {eng}?"),
    ("We hebben een nieuwe {word}.", "We have a new {eng}."),
    ("Waar is de {word}?", "Where is the {eng}?"),
    ("Deze {word} is van mij.", "This {eng} is mine."),
    ("Ik zoek een {word}.", "I am looking for a {eng}."),
    ("De {word} ligt op tafel.", "The {eng} is on the table."),
    ("Hij heeft een mooie {word}.", "He has a beautiful {eng}."),
    ("Zij vertelde over de {word}.", "She talked about the {eng}."),
    ("De {word} was heel interessant.", "The {eng} was very interesting."),
    ("Kun je de {word} even pakken?", "Can you grab the {eng}?"),
    ("Ik wil graag een {word} kopen.", "I would like to buy a {eng}."),
    ("De {word} kost tien euro.", "The {eng} costs ten euros."),
    ("Er is een probleem met de {word}.", "There is a problem with the {eng}."),
]

VERB_TEMPLATES = [
    ("Ik moet vandaag {word}.", "I have to {eng} today."),
    ("Kun je mij helpen om te {word}?", "Can you help me to {eng}?"),
    ("Wij gaan morgen {word}.", "We are going to {eng} tomorrow."),
    ("Het is belangrijk om te {word}.", "It is important to {eng}."),
    ("Zij wil graag {word}.", "She would like to {eng}."),
    ("Je moet leren {word}.", "You have to learn to {eng}."),
    ("Ik probeer te {word}.", "I am trying to {eng}."),
    ("Hij kan goed {word}.", "He can {eng} well."),
    ("We moeten samen {word}.", "We have to {eng} together."),
    ("Wanneer ga je {word}?", "When are you going to {eng}?"),
    ("Ik vind het leuk om te {word}.", "I enjoy {eng_gerund}."),
    ("Het is moeilijk om te {word}.", "It is difficult to {eng}."),
    ("Ze heeft geleerd te {word}.", "She has learned to {eng}."),
    ("Ik wil {word}.", "I want to {eng}."),
    ("Hij begint te {word}.", "He starts to {eng}."),
]

VERB_CONJUGATED_TEMPLATES = [
    ("Ik {conj} elke dag.", "I {eng} every day."),
    ("Hij {conj} heel goed.", "He {eng_s} very well."),
    ("Wij {word} graag samen.", "We like to {eng} together."),
    ("Zij {conj} altijd vroeg.", "She always {eng_s} early."),
    ("Ik {conj} dat niet.", "I don't {eng} that."),
]

ADJ_TEMPLATES = [
    ("Dit is een {word} idee.", "This is a {eng} idea."),
    ("Het weer is {word} vandaag.", "The weather is {eng} today."),
    ("Zij is heel {word}.", "She is very {eng}."),
    ("Dat klinkt {word}.", "That sounds {eng}."),
    ("De stad is erg {word}.", "The city is very {eng}."),
    ("Het boek is {word}.", "The book is {eng}."),
    ("Ik voel me {word}.", "I feel {eng}."),
    ("De situatie is {word}.", "The situation is {eng}."),
    ("Hij vindt het {word}.", "He finds it {eng}."),
    ("Het is een {word} dag.", "It is a {eng} day."),
    ("Dat is heel {word}.", "That is very {eng}."),
    ("We hebben een {word} huis.", "We have a {eng} house."),
]

ADV_TEMPLATES = [
    ("{word_cap} ga ik naar huis.", "{eng_cap} I go home."),
    ("Ik doe het {word}.", "I do it {eng}."),
    ("Hij komt {word}.", "He comes {eng}."),
    ("We gaan {word} eten.", "We are {eng} going to eat."),
    ("{word_cap} is het klaar.", "{eng_cap} it is ready."),
    ("Zij werkt {word} hard.", "She works {eng} hard."),
    ("Ik heb het {word} gedaan.", "I have done it {eng}."),
]

PREP_TEMPLATES = [
    ("Het boek ligt {word} de tafel.", "The book is {eng} the table."),
    ("Ik loop {word} het park.", "I walk {eng} the park."),
    ("Hij staat {word} het gebouw.", "He stands {eng} the building."),
    ("We wonen {word} de stad.", "We live {eng} the city."),
]

CONJ_TEMPLATES = [
    ("Ik ga, {word} het regent.", "I go, {eng} it rains."),
    ("Hij werkt hard, {word} hij moe is.", "He works hard, {eng} he is tired."),
    ("Zij studeert, {word} ze wil slagen.", "She studies, {eng} she wants to pass."),
]

OTHER_TEMPLATES = [
    ("Ik gebruik '{word}' in een zin.", "I use '{eng}' in a sentence."),
    ("'{word_cap}' is een nuttig woord.", "'{eng_cap}' is a useful word."),
    ("Ken je het woord '{word}'?", "Do you know the word '{eng}'?"),
    ("Ik heb '{word}' geleerd.", "I learned '{eng}'."),
]


def clean_word_for_sentence(dutch: str) -> str:
    """Get the base form of a word for use in sentences."""
    word = dutch.strip()
    # Remove article for nouns
    for art in ['de ', 'het ', 'een ']:
        if word.lower().startswith(art):
            word = word[len(art):]
            break
    # Remove parenthetical variations like "(e)" or "(noun)"
    word = re.sub(r'\s*\([^)]*\)\s*', '', word).strip()
    # Remove "zich" for reflexive verbs in infinitive templates
    word = word.replace(' zich', '').strip()
    if word.startswith('zich '):
        word = word[5:]
    return word


def clean_english_for_sentence(english: str) -> str:
    """Clean English translation for use in sentence templates."""
    eng = english.strip()
    # Fix known broken translations
    fixes = {
        'to an(noun)ce': 'to announce',
        'to (adj)ust': 'to adjust',
        'finance(s)': 'finances',
        'cost(s)': 'costs',
    }
    for k, v in fixes.items():
        eng = eng.replace(k, v)
    # Take first meaning if multiple: "a) X b) Y" -> "X"
    m = re.match(r'^a\)\s*(.+?)\s*b\)', eng)
    if m:
        eng = m.group(1).strip()
    # Take first option if comma-separated with different meanings
    if ',' in eng:
        parts = eng.split(',')
        eng = parts[0].strip()
    return eng


def remove_article(eng: str) -> str:
    """Remove English articles 'a ', 'an ', 'the ' from the start."""
    lower = eng.lower()
    if lower.startswith('the '):
        return eng[4:]
    if lower.startswith('an '):
        return eng[3:]
    if lower.startswith('a '):
        return eng[2:]
    return eng


def get_verb_infinitive(dutch: str) -> str:
    """Get infinitive form for verb templates."""
    word = dutch.strip().lower()
    word = re.sub(r'\s*\([^)]*\)\s*', '', word).strip()
    # Remove "zich"
    word = word.replace(' zich', '').strip()
    if word.startswith('zich '):
        word = word[5:]
    return word


def get_eng_without_to(eng: str) -> str:
    """Remove 'to ' prefix from English verb."""
    eng = clean_english_for_sentence(eng)
    if eng.lower().startswith('to '):
        return eng[3:]
    return eng


def make_gerund(eng_verb: str) -> str:
    """Make simple gerund from English verb (rough)."""
    v = get_eng_without_to(eng_verb).strip()
    if v.endswith('e'):
        return v[:-1] + 'ing'
    if re.match(r'.*[^aeiou][aeiou][^aeiou]$', v) and len(v) <= 6:
        return v + v[-1] + 'ing'
    return v + 'ing'


def add_s(eng_verb: str) -> str:
    """Add third person -s to English verb."""
    v = get_eng_without_to(eng_verb).strip()
    if v.endswith(('s', 'sh', 'ch', 'x', 'z')):
        return v + 'es'
    if v.endswith('y') and v[-2] not in 'aeiou':
        return v[:-1] + 'ies'
    return v + 's'


def generate_sentence(dutch: str, english: str, pos: str, index: int):
    """Generate a contextual example sentence pair."""
    clean_nl = clean_word_for_sentence(dutch)
    clean_en = clean_english_for_sentence(english)

    # Use index as seed for deterministic but varied selection
    r = random.Random(hash(dutch) + index)

    if pos == 'verb':
        inf = get_verb_infinitive(dutch)
        eng_no_to = get_eng_without_to(clean_en)
        gerund = make_gerund(clean_en)
        eng_s = add_s(clean_en)

        templates = VERB_TEMPLATES
        t = r.choice(templates)
        nl_sent = t[0].format(word=inf)
        en_sent = t[1].format(
            eng=eng_no_to,
            eng_gerund=gerund,
            eng_s=eng_s,
        )
    elif pos == 'noun':
        templates = NOUN_TEMPLATES
        t = r.choice(templates)
        nl_sent = t[0].format(word=clean_nl)
        en_sent = t[1].format(eng=remove_article(clean_en.lower()))
    elif pos == 'adjective':
        templates = ADJ_TEMPLATES
        t = r.choice(templates)
        nl_sent = t[0].format(word=clean_nl)
        en_sent = t[1].format(eng=clean_en.lower())
    elif pos == 'adverb':
        templates = ADV_TEMPLATES
        t = r.choice(templates)
        nl_sent = t[0].format(
            word=clean_nl,
            word_cap=clean_nl.capitalize(),
        )
        en_sent = t[1].format(
            eng=clean_en.lower(),
            eng_cap=clean_en.capitalize(),
        )
    elif pos == 'preposition':
        templates = PREP_TEMPLATES
        t = r.choice(templates)
        nl_sent = t[0].format(word=clean_nl)
        en_sent = t[1].format(eng=clean_en.lower())
    elif pos == 'conjunction':
        templates = CONJ_TEMPLATES
        t = r.choice(templates)
        nl_sent = t[0].format(word=clean_nl)
        en_sent = t[1].format(eng=clean_en.lower())
    else:
        templates = OTHER_TEMPLATES
        t = r.choice(templates)
        nl_sent = t[0].format(word=clean_nl, word_cap=clean_nl.capitalize())
        en_sent = t[1].format(eng=clean_en, eng_cap=clean_en.capitalize())

    return nl_sent, en_sent


def process_nig():
    """Process NIG parsed data and add sentences."""
    with open('tools/nig_parsed.json', 'r', encoding='utf-8') as f:
        entries = json.load(f)

    for i, entry in enumerate(entries):
        pos = entry.get('pos', 'other')
        # Determine pos from entry data
        if entry.get('is_verb'):
            pos = 'verb'
        elif entry.get('gender') in ['de', 'het']:
            pos = 'noun'
        else:
            eng = entry.get('english', '').strip()
            if eng.startswith('to ') or re.match(r'^a\)\s*to\s', eng):
                pos = 'verb'
            else:
                pos = 'other'

        nl_sent, en_sent = generate_sentence(
            entry['dutch'], entry.get('english', ''), pos, i
        )
        entry['example_nl'] = nl_sent
        entry['example_en'] = en_sent

    with open('tools/nig_parsed_with_sentences.json', 'w', encoding='utf-8') as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)

    print(f"NIG: Added sentences to {len(entries)} entries")
    # Show samples
    for e in entries[:5]:
        print(f"  {e['dutch']:25s} -> {e['example_nl']}")
        print(f"  {'':25s}    {e['example_en']}")
    return entries


def process_nia():
    """Process NIA parsed data and add sentences."""
    with open('tools/nia_parsed.json', 'r', encoding='utf-8') as f:
        entries = json.load(f)

    for i, entry in enumerate(entries):
        dutch = entry['dutch']
        english = entry.get('english', '')

        # Classify
        if english.strip().startswith('to ') or re.match(r'^a\)\s*to\s', english.strip()):
            pos = 'verb'
        elif 'zich' in dutch:
            pos = 'verb'
        else:
            # Use same classification as generate_nia_data.py
            dutch_lower = dutch.lower().strip()
            adj_suffixes = ['lijk', 'ig', 'isch', 'baar', 'loos', 'vol', 'ief', 'eel', 'aal', 'eus']
            is_adj = any(dutch_lower.endswith(s) for s in adj_suffixes)
            if is_adj:
                pos = 'adjective'
            else:
                pos = 'noun'  # default for NIA

        nl_sent, en_sent = generate_sentence(dutch, english, pos, i)
        entry['example_nl'] = nl_sent
        entry['example_en'] = en_sent

    with open('tools/nia_parsed_with_sentences.json', 'w', encoding='utf-8') as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)

    print(f"NIA: Added sentences to {len(entries)} entries")
    for e in entries[:5]:
        print(f"  {e['dutch']:25s} -> {e['example_nl']}")
        print(f"  {'':25s}    {e['example_en']}")
    return entries


if __name__ == '__main__':
    process_nig()
    print()
    process_nia()
    print("\nDone! Now run generate_dart_data.py and generate_nia_data.py to rebuild Dart files.")
