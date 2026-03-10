"""
Parse the complete NIG woordenlijst PDF into structured Dart data.
"""
import pdfplumber
import re
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PDF_PATH = 'c:/Users/Sijie/dutchapp/nig-woordenlijst-nl-eng-totaal.pdf'

def extract_all_text(pdf_path):
    """Extract all text from PDF pages."""
    all_lines = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                for line in text.strip().split('\n'):
                    line = line.strip()
                    if line and line != 'Woordenlijst Nederlands in gang':
                        all_lines.append(line)
    return all_lines

def parse_entry(line):
    """
    Parse a single woordenlijst line.
    Format examples:
      'de cursus course 1'
      'het land country 1'
      'beginnen to begin / start 1'
      'aankomen to arrive 12'
      'als as 6, if 18'
    Returns dict or None if not a valid entry.
    """
    # Skip header lines
    if line.startswith('Nederlands') and 'Engels' in line:
        return None
    if line.startswith('De blauw') or line.startswith('Nederlands.'):
        return None
    if line.startswith('Woordenlijst') or line.startswith('groepen'):
        return None

    # Try to extract chapter numbers at the end
    # Pattern: word(s) | translation | chapter_number(s)
    # Chapter numbers can be: "1", "6, 18", "9, last few 9"

    # Find trailing numbers (chapter references)
    # Match one or more numbers at the end, possibly with commas
    chapter_match = re.search(r'(\d[\d,\s]*)\s*$', line)
    if not chapter_match:
        return None

    chapters_str = chapter_match.group(1).strip()
    # Extract all chapter numbers
    chapters = [int(x.strip()) for x in re.findall(r'\d+', chapters_str)]
    if not chapters:
        return None

    # Everything before the chapter numbers
    rest = line[:chapter_match.start()].strip()

    if not rest:
        return None

    # Determine gender and Dutch word
    gender = 'none'
    dutch = ''
    english = ''
    is_verb = False

    # Check for "to " in the line - indicates verb translation
    # Split: dutch part | english part
    # The tricky part is finding where Dutch ends and English begins

    # Strategy: look for known English patterns
    # If starts with 'de ' or 'het ', it's a noun
    if rest.startswith('de '):
        gender = 'de'
    elif rest.startswith('het '):
        gender = 'het'

    # Try to find the English part
    # English translations often start with: to, a, the, or common English words
    # For verbs: "to verb"
    # For nouns/adj: after the Dutch word

    # Use "to " as verb marker
    to_match = re.search(r'\b(to [\w\s/]+)', rest)
    if to_match:
        is_verb = True
        english = to_match.group(1).strip()
        dutch = rest[:to_match.start()].strip()
    else:
        # Try to split by finding where English starts
        # This is heuristic - look for common patterns
        # Many entries: "dutch_word english_word(s)"
        # We need to find the boundary

        # For "de/het" nouns: "de cursus course" -> dutch="de cursus", english="course"
        # For adjectives: "belangrijk important" -> dutch="belangrijk", english="important"

        # Simple approach: if starts with de/het, take first 2-3 words as Dutch
        if gender != 'none':
            # "de cursus course" or "het appartement apartment"
            parts = rest.split()
            # The Dutch part is "de/het + word(s)", English is the rest
            # Heuristic: de/het + 1 Dutch word, rest is English
            if len(parts) >= 3:
                # Check if second word could still be Dutch (compound: "de postcode", "het avondeten")
                dutch = ' '.join(parts[:2])
                english = ' '.join(parts[2:])

                # Handle cases like "de boon (het boontje) bean"
                paren_match = re.match(r'(de|het)\s+\S+\s*\([^)]+\)\s*(.*)', rest)
                if paren_match:
                    dutch = rest[:rest.index(')')+ 1].strip()
                    english = paren_match.group(2).strip()
            elif len(parts) == 2:
                dutch = rest
                english = ''
        else:
            # No article - could be verb, adjective, adverb, etc.
            parts = rest.split()
            if len(parts) >= 2:
                # Heuristic: first word is Dutch, rest is English
                # But some Dutch words are multi-word: "afscheid nemen", "boodschappen doen"
                # Check common multi-word patterns
                multi_word_patterns = [
                    r'^(\w+\s+doen)\s+(.+)',
                    r'^(\w+\s+nemen)\s+(.+)',
                    r'^(\w+\s+maken)\s+(.+)',
                    r'^(al\s+lang)\s+(.+)',
                ]
                found = False
                for pattern in multi_word_patterns:
                    m = re.match(pattern, rest)
                    if m:
                        dutch = m.group(1)
                        english = m.group(2)
                        found = True
                        break

                if not found:
                    dutch = parts[0]
                    english = ' '.join(parts[1:])
            else:
                dutch = rest
                english = ''

    if not dutch or not english:
        return None

    # Clean up
    dutch = dutch.strip().rstrip(',')
    english = english.strip().rstrip(',')

    # Remove trailing chapter-like numbers from english
    english = re.sub(r'\s+\d+\s*$', '', english).strip()

    return {
        'dutch': dutch,
        'english': english,
        'gender': gender,
        'is_verb': is_verb,
        'chapters': chapters,
        'primary_chapter': chapters[0],
    }

def main():
    lines = extract_all_text(PDF_PATH)
    print(f"Total lines extracted: {len(lines)}")

    entries = []
    skipped = []

    # Some lines are continuations of previous lines
    # Buffer for multi-line entries
    buffer = ''

    for line in lines:
        # Skip known non-entry lines
        if any(line.startswith(x) for x in [
            'Nederlands Engels', 'De blauw', 'groepen',
            'Methode NT2', 'Berna de Boer', 'Margaret van',
            'Birgit Lijmbach', 'Derde', 'bussum',
            'Nederlands in gang'
        ]):
            if buffer:
                entry = parse_entry(buffer)
                if entry:
                    entries.append(entry)
                buffer = ''
            continue

        # Check if this line has chapter numbers (complete entry)
        has_chapter = bool(re.search(r'\d+\s*$', line))

        if has_chapter:
            full_line = (buffer + ' ' + line).strip() if buffer else line
            entry = parse_entry(full_line)
            if entry:
                entries.append(entry)
            else:
                skipped.append(full_line)
            buffer = ''
        else:
            # Continuation line
            buffer = (buffer + ' ' + line).strip() if buffer else line

    # Process remaining buffer
    if buffer:
        entry = parse_entry(buffer)
        if entry:
            entries.append(entry)

    # Filter out pure function words
    function_words = {
        'de', 'het', 'een', 'en', 'of', 'maar', 'want', 'dat', 'die', 'dit',
        'er', 'in', 'op', 'aan', 'met', 'van', 'voor', 'naar', 'bij', 'uit',
        'om', 'over', 'na', 'tot', 'ik', 'jij', 'je', 'hij', 'zij', 'ze',
        'wij', 'we', 'jullie', 'u', 'mijn', 'jouw', 'zijn', 'haar', 'ons',
        'hun', 'wie', 'wat', 'waar', 'hoe', 'welk', 'nee', 'ja', 'niet',
        'geen', 'ook', 'al', 'nog', 'dan', 'toen', 'nu', 'hier', 'daar',
        'twee', 'drie', 'vier', 'vijf', 'zes', 'zeven', 'acht', 'negen',
        'tien', 'elf', 'twaalf', 'een', 'eerste', 'tweede',
    }

    # Don't filter verbs named 'zijn' - that's important!
    filtered = []
    for e in entries:
        dutch_base = e['dutch'].replace('de ', '').replace('het ', '').strip().lower()
        if dutch_base in function_words and not e['is_verb']:
            continue
        filtered.append(e)

    # Organize by chapter
    by_chapter = {}
    for e in filtered:
        ch = e['primary_chapter']
        if ch not in by_chapter:
            by_chapter[ch] = []
        by_chapter[ch].append(e)

    print(f"\nTotal entries parsed: {len(entries)}")
    print(f"After filtering function words: {len(filtered)}")
    print(f"Skipped lines: {len(skipped)}")
    print(f"\nChapters found: {sorted(by_chapter.keys())}")
    for ch in sorted(by_chapter.keys()):
        words = by_chapter[ch]
        nouns = len([w for w in words if w['gender'] != 'none'])
        verbs = len([w for w in words if w['is_verb']])
        other = len(words) - nouns - verbs
        print(f"  H{ch}: {len(words)} words ({nouns} nouns, {verbs} verbs, {other} other)")

    # Save as JSON for further processing
    output_path = 'c:/Users/Sijie/dutchapp/tools/nig_parsed.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(filtered, f, ensure_ascii=False, indent=2)
    print(f"\nSaved to {output_path}")

    # Print first 10 entries as sample
    print("\nSample entries:")
    for e in filtered[:10]:
        print(f"  {e['dutch']:25s} | {e['english']:25s} | H{e['primary_chapter']} | {'verb' if e['is_verb'] else e['gender']}")

if __name__ == '__main__':
    main()
