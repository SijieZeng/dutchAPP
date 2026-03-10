import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../core/storage/local_storage_service.dart';
import '../data/models/textbook.dart';

// Local storage
final localStorageProvider = Provider<LocalStorageService>((ref) {
  return LocalStorageService();
});

// Selected textbook
final selectedTextbookProvider = StateProvider<Textbook>((ref) {
  return Textbook.nederlandsInGang;
});

// Auth state
final isLoggedInProvider = StateProvider<bool>((ref) {
  return false;
});

// Check-in dates
final checkInDatesProvider = StateProvider<List<String>>((ref) {
  return [];
});

// Selected tenses for werkwoorden practice
final selectedTensesProvider = StateProvider<Set<String>>((ref) {
  return {'tegenwoordige_tijd'};
});

// Verb practice source: 'textbook' or 'irregular'
final verbPracticeSourceProvider = StateProvider<String>((ref) {
  return 'textbook';
});

// Bookmarked word IDs
final bookmarkedWordIdsProvider = StateProvider<Set<String>>((ref) {
  return {};
});

// Learned word IDs
final learnedWordIdsProvider = StateProvider<Set<String>>((ref) {
  return {};
});

// Repeat pool word IDs
final repeatPoolProvider = StateProvider<List<String>>((ref) {
  return [];
});

// Stats
final todayLearnedCountProvider = StateProvider<int>((ref) => 0);
final todayReviewedCountProvider = StateProvider<int>((ref) => 0);
final totalLearnedCountProvider = StateProvider<int>((ref) => 0);
final todayDurationProvider = StateProvider<Duration>((ref) => Duration.zero);
final totalDurationProvider = StateProvider<Duration>((ref) => Duration.zero);
