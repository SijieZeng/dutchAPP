import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../core/theme/app_colors.dart';
import '../../state/providers.dart';
import '../../data/models/textbook.dart';

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

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final textbook = ref.watch(selectedTextbookProvider);
    final selectedTenses = ref.watch(selectedTensesProvider);
    final practiceSource = ref.watch(verbPracticeSourceProvider);

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
                ref.read(verbPracticeSourceProvider.notifier).state = 'textbook';
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
              subtitle: const Text('80 meest voorkomende onregelmatige werkwoorden'),
              trailing: practiceSource == 'irregular'
                  ? const Icon(Icons.check_circle, color: AppColors.orange)
                  : null,
              onTap: () {
                ref.read(verbPracticeSourceProvider.notifier).state = 'irregular';
              },
            ),
          ),
          const SizedBox(height: 24),

          // Textbook selector (only for textbook mode)
          if (practiceSource == 'textbook') ...[
            Text(
              'Kies je lesboek',
              style: Theme.of(context).textTheme.titleMedium,
            ),
            const SizedBox(height: 12),
            ...Textbook.all.map((book) => Card(
                  color: book.id == textbook.id
                      ? AppColors.orange.withValues(alpha: 0.15)
                      : AppColors.surface,
                  child: ListTile(
                    leading: Icon(
                      Icons.menu_book,
                      color: book.id == textbook.id
                          ? AppColors.orange
                          : AppColors.textHint,
                    ),
                    title: Text(book.name),
                    subtitle: Text('Niveau ${book.level}'),
                    trailing: book.id == textbook.id
                        ? const Icon(Icons.check_circle,
                            color: AppColors.orange)
                        : null,
                    onTap: () {
                      ref.read(selectedTextbookProvider.notifier).state = book;
                    },
                  ),
                )),
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
                    final current = {...selectedTenses};
                    if (checked == true) {
                      current.add(entry.key);
                    } else {
                      current.remove(entry.key);
                    }
                    if (current.isNotEmpty) {
                      ref.read(selectedTensesProvider.notifier).state =
                          current;
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
