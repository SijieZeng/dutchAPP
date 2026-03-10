import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../core/theme/app_colors.dart';
import '../../state/providers.dart';
import '../../data/models/textbook.dart';

class MijnInhoudScreen extends ConsumerWidget {
  const MijnInhoudScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final textbook = ref.watch(selectedTextbookProvider);
    final learnedCount = ref.watch(learnedWordIdsProvider).length;
    final bookmarkedCount = ref.watch(bookmarkedWordIdsProvider).length;

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text('Mijn inhoud'),
        backgroundColor: AppColors.surface,
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // Current textbook
          _SectionTile(
            icon: Icons.menu_book_rounded,
            title: textbook.name,
            subtitle: 'Niveau ${textbook.level}',
            trailing: TextButton(
              onPressed: () => _showTextbookPicker(context, ref),
              child: const Text('Wijzigen'),
            ),
          ),
          const SizedBox(height: 8),
          _SectionTile(
            icon: Icons.history_rounded,
            title: 'Recent geleerd',
            subtitle: 'Laatst bestudeerde woorden',
            onTap: () => context.push('/word-list/recent'),
          ),
          const SizedBox(height: 8),
          _SectionTile(
            icon: Icons.check_circle_outline_rounded,
            title: 'Alle geleerd',
            subtitle: '$learnedCount woorden',
            onTap: () => context.push('/word-list/all-learned'),
          ),
          const SizedBox(height: 8),
          _SectionTile(
            icon: Icons.bookmark_rounded,
            title: 'Woordenboek',
            subtitle: '$bookmarkedCount woorden opgeslagen',
            onTap: () => context.push('/word-list/bookmarked'),
          ),
          const SizedBox(height: 8),
          _SectionTile(
            icon: Icons.format_quote_rounded,
            title: 'Zinnenbank',
            subtitle: 'Opgeslagen zinnen',
            onTap: () => context.push('/word-list/sentences'),
          ),
        ],
      ),
    );
  }

  void _showTextbookPicker(BuildContext context, WidgetRef ref) {
    showModalBottomSheet(
      context: context,
      backgroundColor: AppColors.surface,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) => Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Kies je lesboek',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 16),
            ...Textbook.all.map(
              (book) => ListTile(
                title: Text(book.name),
                subtitle: Text('Niveau ${book.level}'),
                leading: const Icon(Icons.menu_book, color: AppColors.orange),
                selected: book.id ==
                    ref.read(selectedTextbookProvider).id,
                selectedColor: AppColors.orange,
                onTap: () {
                  ref.read(selectedTextbookProvider.notifier).state = book;
                  ref
                      .read(localStorageProvider)
                      .setCurrentTextbookId(book.id);
                  Navigator.pop(ctx);
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _SectionTile extends StatelessWidget {
  final IconData icon;
  final String title;
  final String subtitle;
  final VoidCallback? onTap;
  final Widget? trailing;

  const _SectionTile({
    required this.icon,
    required this.title,
    required this.subtitle,
    this.onTap,
    this.trailing,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      color: AppColors.surface,
      child: ListTile(
        leading: Icon(icon, color: AppColors.orange),
        title: Text(title),
        subtitle: Text(subtitle, style: const TextStyle(color: AppColors.textSecondary)),
        trailing:
            trailing ?? const Icon(Icons.chevron_right, color: AppColors.textHint),
        onTap: onTap,
      ),
    );
  }
}
