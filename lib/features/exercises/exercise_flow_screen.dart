import 'dart:math';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/theme/app_colors.dart';
import '../../state/providers.dart';
import '../../data/mock/mock_words.dart';
import '../../data/mock/mock_verbs.dart';
import 'betekenis/betekenis_screen.dart';
import 'conjugation/conjugation_screen.dart';

class ExerciseFlowScreen extends ConsumerStatefulWidget {
  final bool isReviewMode;
  const ExerciseFlowScreen({super.key, required this.isReviewMode});

  @override
  ConsumerState<ExerciseFlowScreen> createState() => _ExerciseFlowScreenState();
}

enum _ExerciseStep { betekenis, conjugation }

class _ExerciseFlowScreenState extends ConsumerState<ExerciseFlowScreen> {
  late List<Word> _wordQueue;
  int _currentIndex = 0;
  _ExerciseStep _currentStep = _ExerciseStep.betekenis;
  bool _isComplete = false;

  @override
  void initState() {
    super.initState();
    _buildWordQueue();
  }

  void _buildWordQueue() {
    final textbook = ref.read(selectedTextbookProvider);
    final learnedIds = ref.read(learnedWordIdsProvider);

    if (widget.isReviewMode) {
      // Review: words from repeat pool
      final repeatIds = ref.read(repeatPoolProvider);
      _wordQueue = mockWords.where((w) => repeatIds.contains(w.id)).toList();
    } else {
      // Learn: unlearned words from current textbook
      _wordQueue = mockWords
          .where(
              (w) => w.textbookId == textbook.id && !learnedIds.contains(w.id))
          .toList();
    }
    _wordQueue.shuffle(Random());
    // Limit to 10 words per session
    if (_wordQueue.length > 10) {
      _wordQueue = _wordQueue.sublist(0, 10);
    }

    if (_wordQueue.isEmpty) {
      _isComplete = true;
    }
  }

  void _onBetekenisComplete(bool wasCorrect) {
    final word = _wordQueue[_currentIndex];

    if (!wasCorrect) {
      // Add to repeat pool
      final pool = ref.read(repeatPoolProvider);
      if (!pool.contains(word.id)) {
        ref.read(repeatPoolProvider.notifier).state = [...pool, word.id];
      }
    }

    // If verb, go to conjugation; otherwise next word
    if (word.isVerb && word.verbId != null && getVerbById(word.verbId) != null) {
      setState(() {
        _currentStep = _ExerciseStep.conjugation;
      });
    } else {
      _goToNextWord(wasCorrect);
    }
  }

  void _onConjugationComplete() {
    _goToNextWord(true);
  }

  void _goToNextWord(bool wasCorrect) {
    final word = _wordQueue[_currentIndex];

    if (wasCorrect) {
      // Mark as learned
      final learned = ref.read(learnedWordIdsProvider);
      ref.read(learnedWordIdsProvider.notifier).state = {...learned, word.id};

      // Remove from repeat pool if present
      final pool = ref.read(repeatPoolProvider);
      ref.read(repeatPoolProvider.notifier).state =
          pool.where((id) => id != word.id).toList();

      // Update stats
      if (widget.isReviewMode) {
        ref.read(todayReviewedCountProvider.notifier).state++;
      } else {
        ref.read(todayLearnedCountProvider.notifier).state++;
      }
      ref.read(totalLearnedCountProvider.notifier).state =
          ref.read(learnedWordIdsProvider).length;
    }

    if (_currentIndex + 1 < _wordQueue.length) {
      setState(() {
        _currentIndex++;
        _currentStep = _ExerciseStep.betekenis;
      });
    } else {
      setState(() {
        _isComplete = true;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isComplete) {
      return _CompletionScreen(
        isReview: widget.isReviewMode,
        wordCount: _wordQueue.length,
      );
    }

    final word = _wordQueue[_currentIndex];
    final progress = _currentIndex + 1;
    final total = _wordQueue.length;

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        backgroundColor: AppColors.surface,
        title: Text('$progress / $total'),
        leading: IconButton(
          icon: const Icon(Icons.close),
          onPressed: () => Navigator.of(context).pop(),
        ),
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(4),
          child: LinearProgressIndicator(
            value: progress / total,
            backgroundColor: AppColors.surfaceLight,
            valueColor:
                const AlwaysStoppedAnimation<Color>(AppColors.orange),
          ),
        ),
      ),
      body: _currentStep == _ExerciseStep.betekenis
          ? BetekenisExercise(
              word: word,
              allWords: mockWords
                  .where((w) => w.textbookId == word.textbookId)
                  .toList(),
              onComplete: _onBetekenisComplete,
              onBookmark: () {
                final bookmarked = ref.read(bookmarkedWordIdsProvider);
                ref.read(bookmarkedWordIdsProvider.notifier).state = {
                  ...bookmarked,
                  word.id
                };
              },
            )
          : ConjugationExercise(
              verb: getVerbById(word.verbId)!,
              selectedTenses: ref.read(selectedTensesProvider),
              onComplete: _onConjugationComplete,
            ),
    );
  }
}

class _CompletionScreen extends StatelessWidget {
  final bool isReview;
  final int wordCount;
  const _CompletionScreen(
      {required this.isReview, required this.wordCount});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      body: SafeArea(
        child: Center(
          child: Padding(
            padding: const EdgeInsets.all(32),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Icon(Icons.celebration_rounded,
                    size: 80, color: AppColors.orange),
                const SizedBox(height: 24),
                Text(
                  wordCount == 0
                      ? (isReview
                          ? 'Geen woorden om te herhalen!'
                          : 'Alle woorden geleerd!')
                      : 'Goed gedaan!',
                  style: Theme.of(context).textTheme.headlineMedium,
                ),
                const SizedBox(height: 12),
                Text(
                  wordCount > 0
                      ? '$wordCount woorden ${isReview ? "herhaald" : "geleerd"}'
                      : 'Kies een nieuw hoofdstuk om verder te gaan.',
                  style: Theme.of(context).textTheme.bodyLarge,
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 40),
                ElevatedButton(
                  onPressed: () => Navigator.of(context).pop(),
                  child: const Text('Terug naar home'),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
