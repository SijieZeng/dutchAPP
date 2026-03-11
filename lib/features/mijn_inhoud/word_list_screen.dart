import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/theme/app_colors.dart';
import '../../state/providers.dart';
import '../../data/mock/mock_words.dart';

class WordListScreen extends ConsumerWidget {
  final String category;
  const WordListScreen({super.key, required this.category});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final learnedIds = ref.watch(learnedWordIdsProvider);
    final bookmarkedIds = ref.watch(bookmarkedWordIdsProvider);
    final textbook = ref.watch(selectedTextbookProvider);

    List<Word> words;
    String title;

    switch (category) {
      case 'recent':
        title = 'Recent geleerd';
        words = mockWords
            .where((w) => w.textbookId == textbook.id && learnedIds.contains(w.id))
            .toList()
            .reversed
            .take(20)
            .toList();
        break;
      case 'all-learned':
        title = 'Alle geleerd';
        words = mockWords
            .where((w) => w.textbookId == textbook.id && learnedIds.contains(w.id))
            .toList();
        break;
      case 'bookmarked':
        title = 'Woordenboek';
        words = mockWords.where((w) => bookmarkedIds.contains(w.id)).toList();
        break;
      case 'sentences':
        title = 'Zinnenbank';
        words = []; // Placeholder
        break;
      default:
        title = 'Woorden';
        words = [];
    }

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: Text(title),
        backgroundColor: AppColors.surface,
      ),
      body: words.isEmpty
          ? Center(
              child: Text(
                category == 'sentences'
                    ? 'Nog geen zinnen opgeslagen'
                    : 'Nog geen woorden',
                style: const TextStyle(color: AppColors.textSecondary),
              ),
            )
          : ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: words.length,
              itemBuilder: (context, index) {
                final word = words[index];
                return Card(
                  color: AppColors.surface,
                  child: ListTile(
                    title: Text(
                      word.dutch,
                      style: const TextStyle(fontWeight: FontWeight.w600),
                    ),
                    subtitle: Text(
                      '${word.chinese} · ${word.english}',
                      style: const TextStyle(color: AppColors.textSecondary),
                    ),
                    trailing: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Container(
                          padding: const EdgeInsets.symmetric(
                              horizontal: 8, vertical: 4),
                          decoration: BoxDecoration(
                            color: AppColors.surfaceLight,
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: Text(
                            word.partOfSpeechLabel,
                            style: const TextStyle(
                              fontSize: 11,
                              color: AppColors.textSecondary,
                            ),
                          ),
                        ),
                        const SizedBox(width: 8),
                        GestureDetector(
                          onTap: () {
                            final current =
                                ref.read(bookmarkedWordIdsProvider);
                            if (current.contains(word.id)) {
                              ref
                                  .read(bookmarkedWordIdsProvider.notifier)
                                  .set(<String>{...current}..remove(word.id));
                            } else {
                              ref
                                  .read(bookmarkedWordIdsProvider.notifier)
                                  .set({...current, word.id});
                            }
                          },
                          child: Icon(
                            bookmarkedIds.contains(word.id)
                                ? Icons.bookmark_rounded
                                : Icons.bookmark_border_rounded,
                            color: bookmarkedIds.contains(word.id)
                                ? AppColors.orange
                                : AppColors.textHint,
                          ),
                        ),
                      ],
                    ),
                  ),
                );
              },
            ),
    );
  }
}
