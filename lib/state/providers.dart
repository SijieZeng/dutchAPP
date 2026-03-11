import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../core/storage/local_storage_service.dart';
import '../data/models/textbook.dart';

// Local storage
final localStorageProvider = Provider<LocalStorageService>((ref) {
  return LocalStorageService();
});

// Selected textbook
class SelectedTextbookNotifier extends Notifier<Textbook> {
  @override
  Textbook build() => Textbook.nederlandsInGang;
  void set(Textbook value) => state = value;
}

final selectedTextbookProvider =
    NotifierProvider<SelectedTextbookNotifier, Textbook>(
        SelectedTextbookNotifier.new);

// Auth state
class IsLoggedInNotifier extends Notifier<bool> {
  @override
  bool build() => false;
  void set(bool value) => state = value;
}

final isLoggedInProvider =
    NotifierProvider<IsLoggedInNotifier, bool>(IsLoggedInNotifier.new);

// Check-in dates
class CheckInDatesNotifier extends Notifier<List<String>> {
  @override
  List<String> build() => [];
  void set(List<String> value) => state = value;
}

final checkInDatesProvider =
    NotifierProvider<CheckInDatesNotifier, List<String>>(
        CheckInDatesNotifier.new);

// Selected tenses for werkwoorden practice
class SelectedTensesNotifier extends Notifier<Set<String>> {
  @override
  Set<String> build() => {'tegenwoordige_tijd'};
  void set(Set<String> value) => state = value;
}

final selectedTensesProvider =
    NotifierProvider<SelectedTensesNotifier, Set<String>>(
        SelectedTensesNotifier.new);

// Verb practice source: 'textbook' or 'irregular'
class VerbPracticeSourceNotifier extends Notifier<String> {
  @override
  String build() => 'textbook';
  void set(String value) => state = value;
}

final verbPracticeSourceProvider =
    NotifierProvider<VerbPracticeSourceNotifier, String>(
        VerbPracticeSourceNotifier.new);

// Bookmarked word IDs
class BookmarkedWordIdsNotifier extends Notifier<Set<String>> {
  @override
  Set<String> build() => <String>{};
  void set(Set<String> value) => state = value;
}

final bookmarkedWordIdsProvider =
    NotifierProvider<BookmarkedWordIdsNotifier, Set<String>>(
        BookmarkedWordIdsNotifier.new);

// Learned word IDs
class LearnedWordIdsNotifier extends Notifier<Set<String>> {
  @override
  Set<String> build() => <String>{};
  void set(Set<String> value) => state = value;
}

final learnedWordIdsProvider =
    NotifierProvider<LearnedWordIdsNotifier, Set<String>>(
        LearnedWordIdsNotifier.new);

// Repeat pool word IDs
class RepeatPoolNotifier extends Notifier<List<String>> {
  @override
  List<String> build() => [];
  void set(List<String> value) => state = value;
}

final repeatPoolProvider =
    NotifierProvider<RepeatPoolNotifier, List<String>>(
        RepeatPoolNotifier.new);

// Stats
class IntNotifier extends Notifier<int> {
  @override
  int build() => 0;
  void set(int value) => state = value;
  void increment() => state++;
}

class DurationNotifier extends Notifier<Duration> {
  @override
  Duration build() => Duration.zero;
  void set(Duration value) => state = value;
}

final todayLearnedCountProvider =
    NotifierProvider<IntNotifier, int>(IntNotifier.new);
final todayReviewedCountProvider =
    NotifierProvider<IntNotifier, int>(IntNotifier.new);
final totalLearnedCountProvider =
    NotifierProvider<IntNotifier, int>(IntNotifier.new);
final todayDurationProvider =
    NotifierProvider<DurationNotifier, Duration>(DurationNotifier.new);
final totalDurationProvider =
    NotifierProvider<DurationNotifier, Duration>(DurationNotifier.new);
