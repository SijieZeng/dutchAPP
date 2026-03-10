import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../core/theme/app_colors.dart';
import '../../state/providers.dart';

class ProfileScreen extends ConsumerWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final storage = ref.read(localStorageProvider);
    final userName = storage.userName ?? 'Student';
    final userEmail = storage.userEmail ?? 'student@gmail.com';

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text('Profiel'),
        backgroundColor: AppColors.surface,
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          const SizedBox(height: 20),
          // Avatar + info
          Center(
            child: Column(
              children: [
                const CircleAvatar(
                  radius: 48,
                  backgroundColor: AppColors.surfaceLight,
                  child: Icon(Icons.person, size: 48, color: AppColors.textSecondary),
                ),
                const SizedBox(height: 16),
                Text(userName, style: Theme.of(context).textTheme.titleLarge),
                const SizedBox(height: 4),
                Text(userEmail, style: Theme.of(context).textTheme.bodyMedium),
              ],
            ),
          ),
          const SizedBox(height: 32),

          // Sections
          Card(
            color: AppColors.surface,
            child: ListTile(
              leading: const Icon(Icons.star_rounded, color: AppColors.orange),
              title: const Text('Abonnement'),
              subtitle: const Text('Gratis plan'),
              trailing: const Icon(Icons.chevron_right, color: AppColors.textHint),
              onTap: () {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Binnenkort beschikbaar!')),
                );
              },
            ),
          ),
          const SizedBox(height: 8),
          Card(
            color: AppColors.surface,
            child: ListTile(
              leading: const Icon(Icons.settings_rounded, color: AppColors.orange),
              title: const Text('Leerinstellingen'),
              trailing: const Icon(Icons.chevron_right, color: AppColors.textHint),
              onTap: () {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Binnenkort beschikbaar!')),
                );
              },
            ),
          ),
          const SizedBox(height: 8),
          Card(
            color: AppColors.surface,
            child: ListTile(
              leading: const Icon(Icons.more_horiz_rounded, color: AppColors.orange),
              title: const Text('Meer instellingen'),
              trailing: const Icon(Icons.chevron_right, color: AppColors.textHint),
              onTap: () {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Binnenkort beschikbaar!')),
                );
              },
            ),
          ),
          const SizedBox(height: 32),

          // Sign out
          SizedBox(
            width: double.infinity,
            child: OutlinedButton.icon(
              onPressed: () {
                storage.setLoggedIn(false);
                ref.read(isLoggedInProvider.notifier).state = false;
                context.go('/login');
              },
              icon: const Icon(Icons.logout_rounded),
              label: const Text('Uitloggen'),
              style: OutlinedButton.styleFrom(
                foregroundColor: AppColors.incorrect,
                side: const BorderSide(color: AppColors.incorrect),
                padding: const EdgeInsets.symmetric(vertical: 14),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
