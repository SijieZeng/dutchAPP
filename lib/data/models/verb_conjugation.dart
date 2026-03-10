class VerbConjugation {
  final String id;
  final String infinitive;
  final bool isIrregular;
  final bool usesZijn; // perfectum auxiliary
  final String voltooidDeelwoord;

  // Tegenwoordige tijd
  final Map<String, String> tegenwoordigeTijd;

  // Imperfectum
  final String imperfectumSingular;
  final String imperfectumPlural;

  // Derived tenses are computed
  final String? irregularHint;

  const VerbConjugation({
    required this.id,
    required this.infinitive,
    required this.isIrregular,
    required this.usesZijn,
    required this.voltooidDeelwoord,
    required this.tegenwoordigeTijd,
    required this.imperfectumSingular,
    required this.imperfectumPlural,
    this.irregularHint,
  });

  String get auxiliaryVerb => usesZijn ? 'zijn' : 'hebben';

  // Perfectum: heb/heeft/hebben + voltooid deelwoord
  // or: ben/bent/is/zijn + voltooid deelwoord
  String get perfectumDisplay =>
      '${usesZijn ? "zijn" : "hebben"} + $voltooidDeelwoord';

  // Toekomende tijd: zal/zullen + infinitive
  Map<String, String> get toekomendeTijd => {
        'ik': 'zal $infinitive',
        'jij': 'zal $infinitive',
        'hij/zij/het': 'zal $infinitive',
        'wij': 'zullen $infinitive',
        'jullie': 'zullen $infinitive',
        'zij (pl)': 'zullen $infinitive',
      };

  // Plusquamperfectum: had/hadden + voltooid deelwoord
  // or: was/waren + voltooid deelwoord
  Map<String, String> get plusquamperfectum => usesZijn
      ? {'singular': 'was $voltooidDeelwoord', 'plural': 'waren $voltooidDeelwoord'}
      : {'singular': 'had $voltooidDeelwoord', 'plural': 'hadden $voltooidDeelwoord'};

  // Conditionalis: zou/zouden + infinitive
  Map<String, String> get conditionalis => {
        'singular': 'zou $infinitive',
        'plural': 'zouden $infinitive',
      };

  static const personKeys = [
    'ik',
    'jij',
    'hij/zij/het',
    'wij',
    'jullie',
    'zij (pl)',
  ];
}
