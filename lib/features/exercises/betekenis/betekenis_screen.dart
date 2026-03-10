import 'dart:math';
import 'package:flutter/material.dart';
import '../../../core/theme/app_colors.dart';
import '../../../data/models/word.dart';

class BetekenisExercise extends StatefulWidget {
  final Word word;
  final List<Word> allWords;
  final void Function(bool wasCorrect) onComplete;
  final VoidCallback onBookmark;

  const BetekenisExercise({
    super.key,
    required this.word,
    required this.allWords,
    required this.onComplete,
    required this.onBookmark,
  });

  @override
  State<BetekenisExercise> createState() => _BetekenisExerciseState();
}

class _BetekenisExerciseState extends State<BetekenisExercise> {
  late List<String> _choices;
  int? _selectedIndex;
  bool _showTip = false;
  bool _hasAnsweredWrong = false;
  bool _answered = false;

  @override
  void initState() {
    super.initState();
    _buildChoices();
  }

  @override
  void didUpdateWidget(BetekenisExercise oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.word.id != widget.word.id) {
      _buildChoices();
      _selectedIndex = null;
      _showTip = false;
      _hasAnsweredWrong = false;
      _answered = false;
    }
  }

  void _buildChoices() {
    final correctAnswer = widget.word.english;
    final distractors = widget.allWords
        .where((w) => w.id != widget.word.id)
        .map((w) => w.english)
        .toSet()
        .toList()
      ..shuffle(Random());

    final choices = [correctAnswer];
    for (final d in distractors) {
      if (choices.length >= 4) break;
      if (!choices.contains(d)) choices.add(d);
    }
    choices.shuffle(Random());
    _choices = choices;
  }

  void _onChoiceTap(int index) {
    if (_answered) return;

    setState(() {
      _selectedIndex = index;
    });

    final isCorrect = _choices[index] == widget.word.english;

    if (isCorrect) {
      setState(() => _answered = true);
      Future.delayed(const Duration(milliseconds: 800), () {
        if (mounted) widget.onComplete(!_hasAnsweredWrong);
      });
    } else {
      setState(() => _hasAnsweredWrong = true);
      // Flash red then reset
      Future.delayed(const Duration(milliseconds: 600), () {
        if (mounted) {
          setState(() => _selectedIndex = null);
        }
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(20),
      child: Column(
        children: [
          const Spacer(),
          // Word display
          Text(
            widget.word.dutch,
            style: Theme.of(context).textTheme.headlineLarge?.copyWith(
                  fontSize: 36,
                  fontWeight: FontWeight.bold,
                ),
          ),
          const SizedBox(height: 8),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
            decoration: BoxDecoration(
              color: AppColors.surfaceLight,
              borderRadius: BorderRadius.circular(8),
            ),
            child: Text(
              widget.word.partOfSpeechLabel,
              style: const TextStyle(
                  color: AppColors.textSecondary, fontSize: 13),
            ),
          ),
          const SizedBox(height: 32),

          // Tip section
          if (_showTip) ...[
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: AppColors.surfaceLight,
                borderRadius: BorderRadius.circular(12),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Tip:',
                    style: TextStyle(
                      color: AppColors.orange,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    widget.word.exampleSentence,
                    style: const TextStyle(
                      fontStyle: FontStyle.italic,
                      fontSize: 15,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    widget.word.exampleTranslation,
                    style: const TextStyle(
                      color: AppColors.textSecondary,
                      fontSize: 13,
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),
          ],

          // Choices
          ...List.generate(_choices.length, (index) {
            final isSelected = _selectedIndex == index;
            final isCorrectChoice = _choices[index] == widget.word.english;

            Color bgColor = AppColors.surface;
            Color borderColor = AppColors.surfaceLight;

            if (isSelected && _answered && isCorrectChoice) {
              bgColor = AppColors.correctLight;
              borderColor = AppColors.correct;
            } else if (isSelected && !_answered) {
              bgColor = AppColors.incorrectLight;
              borderColor = AppColors.incorrect;
            }

            return Padding(
              padding: const EdgeInsets.only(bottom: 12),
              child: SizedBox(
                width: double.infinity,
                child: GestureDetector(
                  onTap: () => _onChoiceTap(index),
                  child: AnimatedContainer(
                    duration: const Duration(milliseconds: 200),
                    padding: const EdgeInsets.symmetric(
                        horizontal: 20, vertical: 16),
                    decoration: BoxDecoration(
                      color: bgColor,
                      borderRadius: BorderRadius.circular(14),
                      border: Border.all(color: borderColor, width: 1.5),
                    ),
                    child: Text(
                      _choices[index],
                      style: const TextStyle(fontSize: 16),
                    ),
                  ),
                ),
              ),
            );
          }),
          const SizedBox(height: 16),

          // Bottom buttons
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              // Tips button
              TextButton.icon(
                onPressed: () => setState(() => _showTip = true),
                icon: const Icon(Icons.lightbulb_outline, size: 20),
                label: const Text('Tips'),
                style: TextButton.styleFrom(
                    foregroundColor: AppColors.textSecondary),
              ),
              const SizedBox(width: 24),
              // Bookmark button
              TextButton.icon(
                onPressed: widget.onBookmark,
                icon: const Icon(Icons.bookmark_border, size: 20),
                label: const Text('Opslaan'),
                style: TextButton.styleFrom(
                    foregroundColor: AppColors.textSecondary),
              ),
            ],
          ),
          const Spacer(),
        ],
      ),
    );
  }
}
