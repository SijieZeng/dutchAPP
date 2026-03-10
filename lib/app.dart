import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'core/theme/app_theme.dart';
import 'features/splash/splash_screen.dart';
import 'features/auth/login_screen.dart';
import 'features/main_shell/main_shell.dart';
import 'features/home/home_screen.dart';
import 'features/mijn_inhoud/mijn_inhoud_screen.dart';
import 'features/mijn_inhoud/word_list_screen.dart';
import 'features/werkwoorden/werkwoorden_screen.dart';
import 'features/dashboard/dashboard_screen.dart';
import 'features/profile/profile_screen.dart';
import 'features/exercises/exercise_flow_screen.dart';
import 'features/exercises/verb_practice_screen.dart';

final _shellNavigatorKey = GlobalKey<NavigatorState>();
final _rootNavigatorKey = GlobalKey<NavigatorState>();

final routerProvider = Provider<GoRouter>((ref) {
  return GoRouter(
    navigatorKey: _rootNavigatorKey,
    initialLocation: '/splash',
    routes: [
      GoRoute(
        path: '/splash',
        builder: (context, state) => const SplashScreen(),
      ),
      GoRoute(
        path: '/login',
        builder: (context, state) => const LoginScreen(),
      ),
      ShellRoute(
        navigatorKey: _shellNavigatorKey,
        builder: (context, state, child) => MainShell(child: child),
        routes: [
          GoRoute(
            path: '/home',
            pageBuilder: (context, state) => const NoTransitionPage(
              child: HomeScreen(),
            ),
          ),
          GoRoute(
            path: '/mijn-inhoud',
            pageBuilder: (context, state) => const NoTransitionPage(
              child: MijnInhoudScreen(),
            ),
          ),
          GoRoute(
            path: '/werkwoorden',
            pageBuilder: (context, state) => const NoTransitionPage(
              child: WerkwoordenScreen(),
            ),
          ),
          GoRoute(
            path: '/dashboard',
            pageBuilder: (context, state) => const NoTransitionPage(
              child: DashboardScreen(),
            ),
          ),
        ],
      ),
      GoRoute(
        path: '/word-list/:category',
        parentNavigatorKey: _rootNavigatorKey,
        builder: (context, state) => WordListScreen(
          category: state.pathParameters['category']!,
        ),
      ),
      GoRoute(
        path: '/profile',
        parentNavigatorKey: _rootNavigatorKey,
        builder: (context, state) => const ProfileScreen(),
      ),
      GoRoute(
        path: '/exercise/:mode',
        parentNavigatorKey: _rootNavigatorKey,
        builder: (context, state) {
          if (state.pathParameters['mode'] == 'verb-only') {
            return const VerbPracticeScreen();
          }
          return ExerciseFlowScreen(
            isReviewMode: state.pathParameters['mode'] == 'review',
          );
        },
      ),
    ],
  );
});

class DutchApp extends ConsumerWidget {
  const DutchApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final router = ref.watch(routerProvider);

    return MaterialApp.router(
      title: 'DutchApp',
      theme: AppTheme.darkTheme,
      routerConfig: router,
      debugShowCheckedModeBanner: false,
    );
  }
}
