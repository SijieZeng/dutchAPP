enum WordStatus { unseen, learning, learned }

class UserProgress {
  final String wordId;
  WordStatus status;
  int correctCount;
  int incorrectCount;
  DateTime? lastPracticed;
  bool isBookmarked;
  bool sentenceBookmarked;
  bool inRepeatPool;

  UserProgress({
    required this.wordId,
    this.status = WordStatus.unseen,
    this.correctCount = 0,
    this.incorrectCount = 0,
    this.lastPracticed,
    this.isBookmarked = false,
    this.sentenceBookmarked = false,
    this.inRepeatPool = false,
  });

  Map<String, dynamic> toJson() => {
        'wordId': wordId,
        'status': status.index,
        'correctCount': correctCount,
        'incorrectCount': incorrectCount,
        'lastPracticed': lastPracticed?.toIso8601String(),
        'isBookmarked': isBookmarked,
        'sentenceBookmarked': sentenceBookmarked,
        'inRepeatPool': inRepeatPool,
      };

  factory UserProgress.fromJson(Map<String, dynamic> json) => UserProgress(
        wordId: json['wordId'] as String,
        status: WordStatus.values[json['status'] as int],
        correctCount: json['correctCount'] as int,
        incorrectCount: json['incorrectCount'] as int,
        lastPracticed: json['lastPracticed'] != null
            ? DateTime.parse(json['lastPracticed'] as String)
            : null,
        isBookmarked: json['isBookmarked'] as bool? ?? false,
        sentenceBookmarked: json['sentenceBookmarked'] as bool? ?? false,
        inRepeatPool: json['inRepeatPool'] as bool? ?? false,
      );
}
