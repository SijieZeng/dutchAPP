import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../core/theme/app_colors.dart';
import '../../state/providers.dart';
import '../../data/textbooks/irregular_verbs_data.dart';

class WerkwoordenScreen extends ConsumerWidget {
  const WerkwoordenScreen({super.key});

  static const _allTenses = {
    'tegenwoordige_tijd': 'Tegenwoordige tijd (present)',
    'imperfectum': 'Verleden tijd - imperfectum',
    'perfectum': 'Verleden tijd - perfectum',
    'toekomende_tijd': 'Toekomende tijd (future)',
    'plusquamperfectum': 'Plusquamperfectum',
    'conditionalis': 'Conditionalis',
  };

  static const _frequencyOptions = {
    'high': {
      'title': 'Meest frequente woorden',
      'subtitle': '0-2000 meest frequente woorden',
      'icon': Icons.star_rounded,
    },
    'medium': {
      'title': 'Woorden met frequentie 2000-5000',
      'subtitle': 'Woorden met een frequentie tussen 2000 en 5000',
      'icon': Icons.star_half_rounded,
    },
    'low': {
      'title': 'Woorden met frequentie boven 5000',
      'subtitle': 'Woorden met een frequentie boven 5000',
      'icon': Icons.star_border_rounded,
    },
  };

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final selectedTenses = ref.watch(selectedTensesProvider);
    final practiceSource = ref.watch(verbPracticeSourceProvider);
    final frequencyFilter = ref.watch(verbFrequencyFilterProvider);

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text('Werkwoorden'),
        backgroundColor: AppColors.surface,
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // Practice source selector
          Text(
            'Bron',
            style: Theme.of(context).textTheme.titleMedium,
          ),
          const SizedBox(height: 12),
          // Textbook option
          Card(
            color: practiceSource == 'textbook'
                ? AppColors.orange.withValues(alpha: 0.15)
                : AppColors.surface,
            child: ListTile(
              leading: Icon(
                Icons.menu_book,
                color: practiceSource == 'textbook'
                    ? AppColors.orange
                    : AppColors.textHint,
              ),
              title: const Text('Lesboek werkwoorden'),
              subtitle: const Text('Werkwoorden uit je lesboek'),
              trailing: practiceSource == 'textbook'
                  ? const Icon(Icons.check_circle, color: AppColors.orange)
                  : null,
              onTap: () {
                ref.read(verbPracticeSourceProvider.notifier).set('textbook');
              },
            ),
          ),
          // Irregular verbs option
          Card(
            color: practiceSource == 'irregular'
                ? AppColors.orange.withValues(alpha: 0.15)
                : AppColors.surface,
            child: ListTile(
              leading: Icon(
                Icons.warning_amber_rounded,
                color: practiceSource == 'irregular'
                    ? AppColors.orange
                    : AppColors.textHint,
              ),
              title: const Text('Onregelmatige werkwoorden'),
              subtitle: Text('${allIrregularVerbs.length} onregelmatige werkwoorden'),
              trailing: practiceSource == 'irregular'
                  ? const Icon(Icons.check_circle, color: AppColors.orange)
                  : null,
              onTap: () {
                ref.read(verbPracticeSourceProvider.notifier).set('irregular');
              },
            ),
          ),
          const SizedBox(height: 24),

          // Frequency selector (only for irregular mode)
          if (practiceSource == 'irregular') ...[
            Text(
              'Frequentie',
              style: Theme.of(context).textTheme.titleMedium,
            ),
            const SizedBox(height: 12),
            ..._frequencyOptions.entries.map((entry) {
              final key = entry.key;
              final info = entry.value;
              final freq = key == 'high'
                  ? VerbFrequency.high
                  : (key == 'medium' ? VerbFrequency.medium : VerbFrequency.low);
              final count = getVerbsByFrequency(freq).length;
              return Card(
                color: frequencyFilter == key
                    ? AppColors.orange.withValues(alpha: 0.15)
                    : AppColors.surface,
                child: ListTile(
                  leading: Icon(
                    info['icon'] as IconData,
                    color: frequencyFilter == key
                        ? AppColors.orange
                        : AppColors.textHint,
                  ),
                  title: Text(info['title'] as String),
                  subtitle: Text('${info['subtitle']} ($count werkwoorden)'),
                  trailing: frequencyFilter == key
                      ? const Icon(Icons.check_circle, color: AppColors.orange)
                      : null,
                  onTap: () {
                    ref.read(verbFrequencyFilterProvider.notifier).set(key);
                  },
                ),
              );
            }),
            const SizedBox(height: 24),
          ],

          // Tense checkboxes
          Text(
            'Kies de tijden om te oefenen',
            style: Theme.of(context).textTheme.titleMedium,
          ),
          const SizedBox(height: 12),
          ..._allTenses.entries.map((entry) => Card(
                color: AppColors.surface,
                child: CheckboxListTile(
                  title: Text(entry.value),
                  value: selectedTenses.contains(entry.key),
                  activeColor: AppColors.orange,
                  onChanged: (checked) {
                    final current = <String>{...selectedTenses};
                    if (checked == true) {
                      current.add(entry.key);
                    } else {
                      current.remove(entry.key);
                    }
                    if (current.isNotEmpty) {
                      ref.read(selectedTensesProvider.notifier).set(current);
                    }
                  },
                ),
              )),
          const SizedBox(height: 32),

          // Start button
          SizedBox(
            width: double.infinity,
            height: 56,
            child: ElevatedButton(
              onPressed: () {
                if (practiceSource == 'irregular') {
                  context.push('/exercise/verb-only');
                } else {
                  context.push('/exercise/learn');
                }
              },
              child: const Text(
                'Begin met oefenen',
                style: TextStyle(fontSize: 18),
              ),
            ),
          ),
          const SizedBox(height: 16),
        ],
      ),
    );
  }
}
