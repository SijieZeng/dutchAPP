import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';

class LocalStorageService {
  late SharedPreferences _prefs;

  Future<void> init() async {
    _prefs = await SharedPreferences.getInstance();
  }

  // Auth
  bool get isLoggedIn => _prefs.getBool('isLoggedIn') ?? false;
  Future<void> setLoggedIn(bool value) => _prefs.setBool('isLoggedIn', value);

  String? get userName => _prefs.getString('userName');
  Future<void> setUserName(String name) => _prefs.setString('userName', name);

  String? get userEmail => _prefs.getString('userEmail');
  Future<void> setUserEmail(String email) =>
      _prefs.setString('userEmail', email);

  // Textbook
  String get currentTextbookId =>
      _prefs.getString('currentTextbookId') ?? 'nig';
  Future<void> setCurrentTextbookId(String id) =>
      _prefs.setString('currentTextbookId', id);

  // Check-in
  List<String> get checkInDates =>
      _prefs.getStringList('checkInDates') ?? [];
  Future<void> setCheckInDates(List<String> dates) =>
      _prefs.setStringList('checkInDates', dates);

  // Progress (JSON string)
  String? get progressJson => _prefs.getString('progressJson');
  Future<void> setProgressJson(String json) =>
      _prefs.setString('progressJson', json);

  // Bookmarked words
  List<String> get bookmarkedWordIds =>
      _prefs.getStringList('bookmarkedWordIds') ?? [];
  Future<void> setBookmarkedWordIds(List<String> ids) =>
      _prefs.setStringList('bookmarkedWordIds', ids);

  // Bookmarked sentences
  List<String> get bookmarkedSentences =>
      _prefs.getStringList('bookmarkedSentences') ?? [];
  Future<void> setBookmarkedSentences(List<String> sentences) =>
      _prefs.setStringList('bookmarkedSentences', sentences);

  // Learning stats
  Map<String, dynamic> get todayStats {
    final json = _prefs.getString('todayStats');
    if (json == null) return {};
    return jsonDecode(json) as Map<String, dynamic>;
  }

  Future<void> setTodayStats(Map<String, dynamic> stats) =>
      _prefs.setString('todayStats', jsonEncode(stats));

  // Selected tenses
  List<String> get selectedTenses =>
      _prefs.getStringList('selectedTenses') ?? ['tegenwoordige_tijd'];
  Future<void> setSelectedTenses(List<String> tenses) =>
      _prefs.setStringList('selectedTenses', tenses);

  // Clear all
  Future<void> clear() => _prefs.clear();
}
