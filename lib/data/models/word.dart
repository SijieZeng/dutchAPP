enum PartOfSpeech { noun, verb, adjective, adverb, preposition, conjunction, other }

enum Gender { de, het, none }

class Word {
  final String id;
  final String dutch;
  final String english;
  final String chinese;
  final String exampleSentence;
  final String exampleTranslation;
  final PartOfSpeech partOfSpeech;
  final Gender gender;
  final String textbookId;
  final int chapter;
  final String? verbId;

  const Word({
    required this.id,
    required this.dutch,
    required this.english,
    required this.chinese,
    required this.exampleSentence,
    required this.exampleTranslation,
    required this.partOfSpeech,
    this.gender = Gender.none,
    required this.textbookId,
    required this.chapter,
    this.verbId,
  });

  bool get isVerb => partOfSpeech == PartOfSpeech.verb;

  String get partOfSpeechLabel {
    switch (partOfSpeech) {
      case PartOfSpeech.noun:
        return gender == Gender.de ? 'de (noun)' : 'het (noun)';
      case PartOfSpeech.verb:
        return 'werkwoord';
      case PartOfSpeech.adjective:
        return 'bijvoeglijk naamwoord';
      case PartOfSpeech.adverb:
        return 'bijwoord';
      case PartOfSpeech.preposition:
        return 'voorzetsel';
      case PartOfSpeech.conjunction:
        return 'voegwoord';
      case PartOfSpeech.other:
        return '';
    }
  }
}
