import '../models/verb_conjugation.dart';
import '../textbooks/nig_data.dart';
import '../textbooks/nia_data.dart';
import '../textbooks/irregular_verbs_data.dart';

// Central verb list - combines all textbook data
final List<VerbConjugation> mockVerbs = [
  ...nigAllVerbs,
  ...niaAllVerbs,
  ...irregularVerbsList,
  // ...nonAllVerbs,  // TODO: add when Nederlands op niveau data is ready
];

VerbConjugation? getVerbById(String? id) {
  if (id == null) return null;
  try {
    return mockVerbs.firstWhere((v) => v.id == id);
  } catch (_) {
    return null;
  }
}
