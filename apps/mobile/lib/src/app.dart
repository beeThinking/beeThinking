import 'package:flutter/material.dart';

import 'auth/auth_controller.dart';
import 'screens/login_screen.dart';
import 'screens/profile_screen.dart';
import 'screens/status_screen.dart';

class BeeThinkingApp extends StatelessWidget {
  const BeeThinkingApp({required this.controller, super.key});

  final AuthController controller;

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'BeeThinking',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFFF2B705),
          brightness: Brightness.light,
        ),
        useMaterial3: true,
        inputDecorationTheme: const InputDecorationTheme(
          border: OutlineInputBorder(),
        ),
      ),
      home: ListenableBuilder(
        listenable: controller,
        builder: (context, _) => switch (controller.status) {
          AuthStatus.loading => const StatusScreen.loading(),
          AuthStatus.error => StatusScreen.error(
              message: controller.failure?.message ?? 'Something went wrong.',
              onRetry: controller.retry,
              onLogout: controller.logout,
            ),
          AuthStatus.signedIn => ProfileScreen(
              profile: controller.profile!,
              onLogout: controller.logout,
            ),
          AuthStatus.signedOut || AuthStatus.signingIn => LoginScreen(
              isLoading: controller.status == AuthStatus.signingIn,
              error: controller.failure?.message,
              onLogin: controller.login,
            ),
        },
      ),
    );
  }
}
