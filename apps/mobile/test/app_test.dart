import 'package:bee_thinking_mobile/src/app.dart';
import 'package:bee_thinking_mobile/src/auth/auth_controller.dart';
import 'package:bee_thinking_mobile/src/auth/auth_models.dart';
import 'package:bee_thinking_mobile/src/auth/auth_repository.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('login displays profile and logout returns immediately', (tester) async {
    final repository = WidgetAuthRepository();
    final controller = AuthController(repository)..status = AuthStatus.signedOut;
    await tester.pumpWidget(BeeThinkingApp(controller: controller));

    await tester.enterText(find.byKey(const Key('username')), 'beekeeper');
    await tester.enterText(find.byKey(const Key('password')), 'secret');
    await tester.tap(find.byKey(const Key('login-button')));
    await tester.pumpAndSettle();

    expect(find.text('bee@example.com'), findsOneWidget);
    expect(repository.loginUsername, 'beekeeper');

    await tester.tap(find.byKey(const Key('logout-button')));
    await tester.pump();
    expect(find.text('Sign in'), findsOneWidget);
  });

  testWidgets('login error remains on login screen', (tester) async {
    final repository = WidgetAuthRepository()
      ..failure = const AuthException(
        'Incorrect username or password.',
        kind: AuthFailureKind.unauthorized,
      );
    final controller = AuthController(repository)..status = AuthStatus.signedOut;
    await tester.pumpWidget(BeeThinkingApp(controller: controller));

    await tester.enterText(find.byKey(const Key('username')), 'wrong');
    await tester.enterText(find.byKey(const Key('password')), 'wrong');
    await tester.tap(find.byKey(const Key('login-button')));
    await tester.pumpAndSettle();

    expect(find.byKey(const Key('login-error')), findsOneWidget);
    expect(find.text('Incorrect username or password.'), findsOneWidget);
  });
}

class WidgetAuthRepository implements AuthRepository {
  String? loginUsername;
  AuthException? failure;

  static final profile = UserProfile(
    id: 1,
    username: 'beekeeper',
    email: 'bee@example.com',
    isActive: true,
    isVerified: true,
    isAdmin: false,
    createdAt: DateTime.utc(2026, 8, 3),
  );

  @override
  Future<UserProfile> login(String username, String password) async {
    loginUsername = username;
    if (failure case final failure?) throw failure;
    return profile;
  }

  @override
  Future<UserProfile> getProfile() async => profile;

  @override
  Future<bool> hasCredentials() async => false;

  @override
  Future<void> logout() async {}
}
