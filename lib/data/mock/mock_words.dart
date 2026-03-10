import '../textbooks/nig_data.dart';
import '../textbooks/nia_data.dart';
import '../models/word.dart';

// Central word list - combines all textbook data
// ignore: unused_import
export '../models/word.dart';

final List<Word> mockWords = [
  ...nigAllWords,
  ...niaAllWords,
  // ...nonAllWords,  // TODO: add when Nederlands op niveau data is ready
];
