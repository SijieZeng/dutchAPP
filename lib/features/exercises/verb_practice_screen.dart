import 'dart:math';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/theme/app_colors.dart';
import '../../state/providers.dart';
import '../../data/models/verb_conjugation.dart';
import '../../data/mock/mock_verbs.dart';
import '../../data/textbooks/irregular_verbs_data.dart';
import 'conjugation/conjugation_screen.dart';

/// Verb-only practice mode: skips betekenis, just does conjugation exercises.
class VerbPracticeScreen extends ConsumerStatefulWidget {
  const VerbPracticeScreen({super.key});

  @override
  ConsumerState<VerbPracticeScreen> createState() => _VerbPracticeScreenState();
}

class _VerbPracticeScreenState extends ConsumerState<VerbPracticeScreen> {
  late List<VerbConjugation> _verbQueue;
  int _currentIndex = 0;
  bool _isComplete = false;

  @override
  void initState() {
    super.initState();
    _buildVerbQueue();
  }

  void _buildVerbQueue() {
    // Use all irregular verbs + verbs from NIG/NIA
    final allVerbs = [...irregularVerbsList, ...mockVerbs];

    // Deduplicate by infinitive (keep first occurrence)
    final seen = <String>{};
    final unique = <VerbConjugation>[];
    for (final v in allVerbs) {
      if (seen.add(v.infinitive)) {
        unique.add(v);
      }
    }

    _verbQueue = unique..shuffle(Random());
    // Limit to 10 per session
    if (_verbQueue.length > 10) {
      _verbQueue = _verbQueue.sublist(0, 10);
    }

    if (_verbQueue.isEmpty) {
      _isComplete = true;
    }
  }

  void _onComplete() {
    if (_currentIndex + 1 < _verbQueue.length) {
      setState(() {
        _currentIndex++;
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
                    _verbQueue.isEmpty
                        ? 'Geen werkwoorden beschikbaar!'
                        : 'Goed gedaan!',
                    style: Theme.of(context).textTheme.headlineMedium,
                  ),
                  const SizedBox(height: 12),
                  Text(
                    _verbQueue.isNotEmpty
                        ? '${_verbQueue.length} werkwoorden geoefend'
                        : '',
                    style: Theme.of(context).textTheme.bodyLarge,
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 40),
                  ElevatedButton(
                    onPressed: () => Navigator.of(context).pop(),
                    child: const Text('Terug'),
                  ),
                ],
              ),
            ),
          ),
        ),
      );
    }

    final verb = _verbQueue[_currentIndex];
    final progress = _currentIndex + 1;
    final total = _verbQueue.length;
    final selectedTenses = ref.read(selectedTensesProvider);

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
      body: ConjugationExercise(
        verb: verb,
        selectedTenses: selectedTenses,
        onComplete: _onComplete,
      ),
    );
  }
}
