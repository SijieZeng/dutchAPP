import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';
import '../../core/theme/app_colors.dart';
import '../../state/providers.dart';
import '../../widgets/frosted_card.dart';
import '../../data/mock/mock_words.dart';

class HomeScreen extends ConsumerWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final textbook = ref.watch(selectedTextbookProvider);
    final learnedIds = ref.watch(learnedWordIdsProvider);
    final repeatPool = ref.watch(repeatPoolProvider);

    final textbookWords =
        mockWords.where((w) => w.textbookId == textbook.id).toList();
    final unlearnedCount =
        textbookWords.where((w) => !learnedIds.contains(w.id)).length;
    final reviewCount = repeatPool.length;

    final today = DateFormat('MM/dd EEE').format(DateTime.now());
    final checkInDates = ref.watch(checkInDatesProvider);
    final todayStr = DateFormat('yyyy-MM-dd').format(DateTime.now());
    final isCheckedIn = checkInDates.contains(todayStr);

    return Scaffold(
      body: Stack(
        fit: StackFit.expand,
        children: [
          // Background gradient (Momentum-style)
          Container(
            decoration: const BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: [
                  Color(0xFF1A1A2E),
                  Color(0xFF16213E),
                  Color(0xFF0F3460),
                  Color(0xFF1A1A2E),
                ],
              ),
            ),
          ),
          // Decorative circles
          Positioned(
            top: -80,
            right: -60,
            child: Container(
              width: 250,
              height: 250,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                gradient: RadialGradient(
                  colors: [
                    AppColors.orange.withValues(alpha: 0.15),
                    Colors.transparent,
                  ],
                ),
              ),
            ),
          ),
          Positioned(
            bottom: 200,
            left: -100,
            child: Container(
              width: 300,
              height: 300,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                gradient: RadialGradient(
                  colors: [
                    AppColors.orange.withValues(alpha: 0.08),
                    Colors.transparent,
                  ],
                ),
              ),
            ),
          ),
          // Content
          SafeArea(
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const SizedBox(height: 8),
                  // Top bar: avatar
                  GestureDetector(
                    onTap: () => context.push('/profile'),
                    child: const CircleAvatar(
                      radius: 22,
                      backgroundColor: AppColors.surfaceLight,
                      child: Icon(Icons.person, color: AppColors.textSecondary),
                    ),
                  ),
                  const Spacer(flex: 2),
                  // Dutch motto
                  Center(
                    child: Column(
                      children: [
                        Text(
                          'Oefening baart kunst',
                          style: Theme.of(context)
                              .textTheme
                              .headlineMedium
                              ?.copyWith(
                                fontStyle: FontStyle.italic,
                                color: AppColors.textPrimary,
                              ),
                        ),
                        const SizedBox(height: 8),
                        Text(
                          'Practice makes perfect',
                          style: Theme.of(context)
                              .textTheme
                              .bodyMedium
                              ?.copyWith(color: AppColors.textSecondary),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 40),
                  // Check-in card
                  Center(
                    child: FrostedCard(
                      onTap: () {
                        if (!isCheckedIn) {
                          final updated = <String>[...checkInDates, todayStr];
                          ref.read(checkInDatesProvider.notifier).state =
                              updated;
                          ref
                              .read(localStorageProvider)
                              .setCheckInDates(updated);
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(
                              content: Text('Ingecheckt! Goed bezig! '),
                              backgroundColor: AppColors.correct,
                              duration: Duration(seconds: 1),
                            ),
                          );
                        }
                      },
                      padding: const EdgeInsets.symmetric(
                          horizontal: 32, vertical: 20),
                      child: Column(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Icon(
                            isCheckedIn
                                ? Icons.check_circle_rounded
                                : Icons.calendar_today_rounded,
                            size: 36,
                            color: isCheckedIn
                                ? AppColors.correct
                                : AppColors.textPrimary,
                          ),
                          const SizedBox(height: 8),
                          Text(
                            isCheckedIn ? 'Ingecheckt' : 'Inchecken',
                            style: Theme.of(context).textTheme.titleMedium,
                          ),
                          const SizedBox(height: 4),
                          Text(
                            today,
                            style: Theme.of(context).textTheme.bodyMedium,
                          ),
                        ],
                      ),
                    ),
                  ),
                  const Spacer(flex: 3),
                  // Learn and Review cards
                  Row(
                    children: [
                      Expanded(
                        child: FrostedCard(
                          onTap: () => context.push('/exercise/learn'),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                'Learn',
                                style:
                                    Theme.of(context).textTheme.titleLarge,
                              ),
                              const SizedBox(height: 4),
                              Text(
                                '$unlearnedCount',
                                style: Theme.of(context)
                                    .textTheme
                                    .headlineMedium
                                    ?.copyWith(color: AppColors.orange),
                              ),
                            ],
                          ),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: FrostedCard(
                          onTap: () => context.push('/exercise/review'),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                'Review',
                                style:
                                    Theme.of(context).textTheme.titleLarge,
                              ),
                              const SizedBox(height: 4),
                              Text(
                                '$reviewCount',
                                style: Theme.of(context)
                                    .textTheme
                                    .headlineMedium
                                    ?.copyWith(color: AppColors.orange),
                              ),
                            ],
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
