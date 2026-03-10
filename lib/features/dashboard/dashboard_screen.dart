import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import '../../core/theme/app_colors.dart';
import '../../state/providers.dart';

class DashboardScreen extends ConsumerWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final checkInDates = ref.watch(checkInDatesProvider);
    final todayLearned = ref.watch(todayLearnedCountProvider);
    final todayReviewed = ref.watch(todayReviewedCountProvider);
    final totalLearned = ref.watch(totalLearnedCountProvider);
    final todayDuration = ref.watch(todayDurationProvider);
    final totalDuration = ref.watch(totalDurationProvider);

    // Calculate streak
    int streak = 0;
    final now = DateTime.now();
    for (int i = 0; i < 365; i++) {
      final date = now.subtract(Duration(days: i));
      final dateStr = DateFormat('yyyy-MM-dd').format(date);
      if (checkInDates.contains(dateStr)) {
        streak++;
      } else {
        break;
      }
    }

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text('Dashboard'),
        backgroundColor: AppColors.surface,
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // Streak
          Card(
            color: AppColors.surface,
            child: Padding(
              padding: const EdgeInsets.all(20),
              child: Row(
                children: [
                  const Icon(Icons.local_fire_department_rounded,
                      color: AppColors.orange, size: 40),
                  const SizedBox(width: 16),
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        '$streak dagen op rij!',
                        style: Theme.of(context).textTheme.titleLarge,
                      ),
                      Text(
                        'Ga zo door!',
                        style: Theme.of(context).textTheme.bodyMedium,
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),

          // Calendar
          Text(
            'Incheck kalender',
            style: Theme.of(context).textTheme.titleMedium,
          ),
          const SizedBox(height: 12),
          _CheckInCalendar(checkInDates: checkInDates),
          const SizedBox(height: 24),

          // Stats grid
          Text(
            'Overzicht',
            style: Theme.of(context).textTheme.titleMedium,
          ),
          const SizedBox(height: 12),
          GridView.count(
            crossAxisCount: 2,
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            mainAxisSpacing: 12,
            crossAxisSpacing: 12,
            childAspectRatio: 1.8,
            children: [
              _StatCard(
                label: 'Vandaag geleerd',
                value: '$todayLearned',
                icon: Icons.school_rounded,
              ),
              _StatCard(
                label: 'Vandaag herhaald',
                value: '$todayReviewed',
                icon: Icons.replay_rounded,
              ),
              _StatCard(
                label: 'Totaal geleerd',
                value: '$totalLearned',
                icon: Icons.check_circle_rounded,
              ),
              _StatCard(
                label: 'Vandaag tijd',
                value: '${todayDuration.inMinutes} min',
                icon: Icons.timer_rounded,
              ),
              _StatCard(
                label: 'Totale tijd',
                value: '${totalDuration.inHours}u ${totalDuration.inMinutes % 60}m',
                icon: Icons.access_time_rounded,
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _CheckInCalendar extends StatelessWidget {
  final List<String> checkInDates;
  const _CheckInCalendar({required this.checkInDates});

  @override
  Widget build(BuildContext context) {
    final now = DateTime.now();
    final firstOfMonth = DateTime(now.year, now.month, 1);
    final daysInMonth = DateTime(now.year, now.month + 1, 0).day;
    final startWeekday = firstOfMonth.weekday; // 1=Monday

    return Card(
      color: AppColors.surface,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
          // Month header
          Text(
            DateFormat('MMMM yyyy').format(now),
            style: Theme.of(context).textTheme.titleMedium,
          ),
          const SizedBox(height: 12),
          // Day headers
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: ['Ma', 'Di', 'Wo', 'Do', 'Vr', 'Za', 'Zo']
                .map((d) => SizedBox(
                      width: 36,
                      child: Center(
                        child: Text(d,
                            style: const TextStyle(
                                color: AppColors.textHint, fontSize: 12)),
                      ),
                    ))
                .toList(),
          ),
          const SizedBox(height: 8),
          // Day grid
          GridView.builder(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
              crossAxisCount: 7,
            ),
            itemCount: daysInMonth + startWeekday - 1,
            itemBuilder: (context, index) {
              if (index < startWeekday - 1) {
                return const SizedBox.shrink();
              }
              final day = index - startWeekday + 2;
              final dateStr = DateFormat('yyyy-MM-dd')
                  .format(DateTime(now.year, now.month, day));
              final isChecked = checkInDates.contains(dateStr);
              final isToday = day == now.day;

              return Center(
                child: Container(
                  width: 32,
                  height: 32,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: isChecked
                        ? AppColors.orange
                        : isToday
                            ? AppColors.surfaceLight
                            : Colors.transparent,
                  ),
                  child: Center(
                    child: Text(
                      '$day',
                      style: TextStyle(
                        fontSize: 13,
                        color: isChecked
                            ? Colors.white
                            : AppColors.textSecondary,
                        fontWeight:
                            isToday ? FontWeight.bold : FontWeight.normal,
                      ),
                    ),
                  ),
                ),
              );
            },
          ),
        ],
        ),
      ),
    );
  }
}

class _StatCard extends StatelessWidget {
  final String label;
  final String value;
  final IconData icon;

  const _StatCard({
    required this.label,
    required this.value,
    required this.icon,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      color: AppColors.surface,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Row(
              children: [
                Icon(icon, color: AppColors.orange, size: 20),
                const SizedBox(width: 8),
                Flexible(
                  child: Text(
                    label,
                    style: const TextStyle(
                        color: AppColors.textSecondary, fontSize: 12),
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              value,
              style: Theme.of(context)
                  .textTheme
                  .titleLarge
                  ?.copyWith(color: AppColors.textPrimary),
            ),
          ],
        ),
      ),
    );
  }
}
