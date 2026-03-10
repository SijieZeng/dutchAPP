import 'package:flutter/material.dart';
import '../../../core/theme/app_colors.dart';
import '../../../data/models/verb_conjugation.dart';

class ConjugationExercise extends StatefulWidget {
  final VerbConjugation verb;
  final Set<String> selectedTenses;
  final VoidCallback onComplete;

  const ConjugationExercise({
    super.key,
    required this.verb,
    required this.selectedTenses,
    required this.onComplete,
  });

  @override
  State<ConjugationExercise> createState() => _ConjugationExerciseState();
}

class _ConjugationExerciseState extends State<ConjugationExercise> {
  // Controllers for each input field
  final Map<String, TextEditingController> _controllers = {};
  // Validation results: null = not checked, true = correct, false = wrong
  final Map<String, bool?> _results = {};
  bool _isChecked = false;
  bool _showAnswers = false;

  @override
  void initState() {
    super.initState();
    _initControllers();
  }

  @override
  void dispose() {
    for (final c in _controllers.values) {
      c.dispose();
    }
    super.dispose();
  }

  void _initControllers() {
    final tenses = widget.selectedTenses;

    if (tenses.contains('tegenwoordige_tijd')) {
      for (final person in VerbConjugation.personKeys) {
        final key = 'tt_$person';
        _controllers[key] = TextEditingController();
        _results[key] = null;
      }
    }
    if (tenses.contains('imperfectum')) {
      _controllers['imp_singular'] = TextEditingController();
      _controllers['imp_plural'] = TextEditingController();
      _results['imp_singular'] = null;
      _results['imp_plural'] = null;
    }
    if (tenses.contains('perfectum')) {
      _controllers['perf_auxiliary'] = TextEditingController();
      _controllers['perf_deelwoord'] = TextEditingController();
      _results['perf_auxiliary'] = null;
      _results['perf_deelwoord'] = null;
    }
    if (tenses.contains('toekomende_tijd')) {
      _controllers['toek_singular'] = TextEditingController();
      _controllers['toek_plural'] = TextEditingController();
      _results['toek_singular'] = null;
      _results['toek_plural'] = null;
    }
    if (tenses.contains('plusquamperfectum')) {
      _controllers['pqp_singular'] = TextEditingController();
      _controllers['pqp_plural'] = TextEditingController();
      _results['pqp_singular'] = null;
      _results['pqp_plural'] = null;
    }
    if (tenses.contains('conditionalis')) {
      _controllers['cond_singular'] = TextEditingController();
      _controllers['cond_plural'] = TextEditingController();
      _results['cond_singular'] = null;
      _results['cond_plural'] = null;
    }
  }

  Map<String, String> get _correctAnswers {
    final verb = widget.verb;
    final answers = <String, String>{};

    if (widget.selectedTenses.contains('tegenwoordige_tijd')) {
      for (final person in VerbConjugation.personKeys) {
        answers['tt_$person'] = verb.tegenwoordigeTijd[person]!;
      }
    }
    if (widget.selectedTenses.contains('imperfectum')) {
      answers['imp_singular'] = verb.imperfectumSingular;
      answers['imp_plural'] = verb.imperfectumPlural;
    }
    if (widget.selectedTenses.contains('perfectum')) {
      answers['perf_auxiliary'] = verb.auxiliaryVerb;
      answers['perf_deelwoord'] = verb.voltooidDeelwoord;
    }
    if (widget.selectedTenses.contains('toekomende_tijd')) {
      answers['toek_singular'] = 'zal ${verb.infinitive}';
      answers['toek_plural'] = 'zullen ${verb.infinitive}';
    }
    if (widget.selectedTenses.contains('plusquamperfectum')) {
      final pqp = verb.plusquamperfectum;
      answers['pqp_singular'] = pqp['singular']!;
      answers['pqp_plural'] = pqp['plural']!;
    }
    if (widget.selectedTenses.contains('conditionalis')) {
      final cond = verb.conditionalis;
      answers['cond_singular'] = cond['singular']!;
      answers['cond_plural'] = cond['plural']!;
    }

    return answers;
  }

  void _checkAnswers() {
    final answers = _correctAnswers;
    setState(() {
      _isChecked = true;
      for (final key in _controllers.keys) {
        final userAnswer = _controllers[key]!.text.trim().toLowerCase();
        final correct = answers[key]!.toLowerCase();
        _results[key] = userAnswer == correct;
      }
    });
  }

  void _showCorrectAnswers() {
    final answers = _correctAnswers;
    setState(() {
      _showAnswers = true;
      _isChecked = true;
      for (final key in _controllers.keys) {
        _controllers[key]!.text = answers[key]!;
        _results[key] = true;
      }
    });
  }

  bool get _allCorrect =>
      _isChecked && _results.values.every((r) => r == true);

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Verb header
          Center(
            child: Text(
              widget.verb.infinitive,
              style: Theme.of(context).textTheme.headlineLarge?.copyWith(
                    fontSize: 32,
                    fontWeight: FontWeight.bold,
                  ),
            ),
          ),
          const SizedBox(height: 8),
          // Irregular hint
          if (widget.verb.isIrregular && widget.verb.irregularHint != null)
            Center(
              child: Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
                decoration: BoxDecoration(
                  color: AppColors.orange.withValues(alpha: 0.15),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  widget.verb.irregularHint!,
                  style: const TextStyle(
                      color: AppColors.orange, fontSize: 13),
                ),
              ),
            ),
          const SizedBox(height: 24),

          // Tense sections
          if (widget.selectedTenses.contains('tegenwoordige_tijd')) ...[
            _sectionTitle('Tegenwoordige tijd'),
            ...VerbConjugation.personKeys.map(
              (person) => _inputRow(person, 'tt_$person'),
            ),
            const SizedBox(height: 20),
          ],
          if (widget.selectedTenses.contains('imperfectum')) ...[
            _sectionTitle('Verleden tijd - imperfectum'),
            _inputRow('Singular', 'imp_singular'),
            _inputRow('Plural', 'imp_plural'),
            const SizedBox(height: 20),
          ],
          if (widget.selectedTenses.contains('perfectum')) ...[
            _sectionTitle('Verleden tijd - perfectum'),
            _inputRow('Hulpwerkwoord (zijn/hebben)', 'perf_auxiliary'),
            _inputRow('Voltooid deelwoord', 'perf_deelwoord'),
            const SizedBox(height: 20),
          ],
          if (widget.selectedTenses.contains('toekomende_tijd')) ...[
            _sectionTitle('Toekomende tijd'),
            _inputRow('Singular (ik)', 'toek_singular'),
            _inputRow('Plural (wij)', 'toek_plural'),
            const SizedBox(height: 20),
          ],
          if (widget.selectedTenses.contains('plusquamperfectum')) ...[
            _sectionTitle('Plusquamperfectum'),
            _inputRow('Singular', 'pqp_singular'),
            _inputRow('Plural', 'pqp_plural'),
            const SizedBox(height: 20),
          ],
          if (widget.selectedTenses.contains('conditionalis')) ...[
            _sectionTitle('Conditionalis'),
            _inputRow('Singular', 'cond_singular'),
            _inputRow('Plural', 'cond_plural'),
            const SizedBox(height: 20),
          ],

          const SizedBox(height: 16),

          // Buttons
          if (_allCorrect) ...[
            SizedBox(
              width: double.infinity,
              height: 52,
              child: ElevatedButton(
                onPressed: widget.onComplete,
                child: const Text('Volgende', style: TextStyle(fontSize: 16)),
              ),
            ),
          ] else ...[
            Row(
              children: [
                Expanded(
                  child: SizedBox(
                    height: 52,
                    child: ElevatedButton(
                      onPressed: _checkAnswers,
                      child: Text(
                        _isChecked ? 'Opnieuw controleren' : 'Controleer',
                        style: const TextStyle(fontSize: 16),
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                SizedBox(
                  height: 52,
                  child: OutlinedButton(
                    onPressed: _showCorrectAnswers,
                    style: OutlinedButton.styleFrom(
                      foregroundColor: AppColors.textSecondary,
                      side: const BorderSide(color: AppColors.textHint),
                    ),
                    child: const Text('Antwoord'),
                  ),
                ),
              ],
            ),
          ],
          const SizedBox(height: 32),
        ],
      ),
    );
  }

  Widget _sectionTitle(String title) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Text(
        title,
        style: Theme.of(context).textTheme.titleMedium?.copyWith(
              color: AppColors.orange,
            ),
      ),
    );
  }

  Widget _inputRow(String label, String key) {
    final controller = _controllers[key]!;
    final result = _results[key];

    Color? borderColor;
    if (_isChecked && result != null) {
      borderColor = result ? AppColors.correct : AppColors.incorrect;
    }

    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        children: [
          SizedBox(
            width: 110,
            child: Text(
              label,
              style: const TextStyle(
                  color: AppColors.textSecondary, fontSize: 14),
            ),
          ),
          Expanded(
            child: TextField(
              controller: controller,
              enabled: !_showAnswers,
              style: TextStyle(
                color: _isChecked && result != null
                    ? (result ? AppColors.correct : AppColors.incorrect)
                    : AppColors.textPrimary,
              ),
              decoration: InputDecoration(
                isDense: true,
                contentPadding:
                    const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(10),
                  borderSide: BorderSide.none,
                ),
                enabledBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(10),
                  borderSide: borderColor != null
                      ? BorderSide(color: borderColor, width: 2)
                      : BorderSide.none,
                ),
                focusedBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(10),
                  borderSide: BorderSide(
                    color: borderColor ?? AppColors.orange,
                    width: 2,
                  ),
                ),
                filled: true,
                fillColor: AppColors.surfaceLight,
                suffixIcon: _isChecked && result != null
                    ? Icon(
                        result ? Icons.check_circle : Icons.cancel,
                        color: result ? AppColors.correct : AppColors.incorrect,
                        size: 20,
                      )
                    : null,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
