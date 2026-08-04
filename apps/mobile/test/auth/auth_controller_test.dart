import 'package:bee_thinking_mobile/src/auth/auth_controller.dart';
import 'package:bee_thinking_mobile/src/auth/auth_models.dart';
import 'package:bee_thinking_mobile/src/auth/auth_repository.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('restore reports offline profile failure as retryable error', () async {
    final repository = FakeAuthRepository()
      ..credentials = true
      ..failure = const AuthException(
        'You appear to be offline.',
        kind: AuthFailureKind.offline,
      );
    final controller = AuthController(repository);

    await controller.restoreSession();

    expect(controller.status, AuthStatus.error);
    expect(controller.failure?.kind, AuthFailureKind.offline);
  });

  test('unauthorized restore returns to signed-out state', () async {
    final repository = FakeAuthRepository()
      ..credentials = true
      ..failure = const AuthException(
        'Session expired.',
        kind: AuthFailureKind.unauthorized,
      );
    final controller = AuthController(repository);

    await controller.restoreSession();

    expect(controller.status, AuthStatus.signedOut);
  });
}

class FakeAuthRepository implements AuthRepository {
  bool credentials = false;
  AuthException? failure;

  @override
  Future<UserProfile> getProfile() async => throw failure!;

  @override
  Future<bool> hasCredentials() async => credentials;

  @override
  Future<UserProfile> login(String username, String password) => getProfile();

  @override
  Future<void> logout() async {}
}
