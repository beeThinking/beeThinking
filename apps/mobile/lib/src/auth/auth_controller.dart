import 'package:flutter/foundation.dart';

import 'auth_models.dart';
import 'auth_repository.dart';

enum AuthStatus { loading, signedOut, signingIn, signedIn, error }

class AuthController extends ChangeNotifier {
  AuthController(this._repository);

  final AuthRepository _repository;
  AuthStatus status = AuthStatus.loading;
  UserProfile? profile;
  AuthException? failure;

  Future<void> restoreSession() async {
    status = AuthStatus.loading;
    notifyListeners();
    try {
      if (!await _repository.hasCredentials()) {
        status = AuthStatus.signedOut;
        notifyListeners();
        return;
      }
      await _loadProfile();
    } on Object {
      failure = const AuthException('Secure credentials could not be read.');
      status = AuthStatus.error;
      notifyListeners();
    }
  }

  Future<void> login(String username, String password) async {
    status = AuthStatus.signingIn;
    failure = null;
    notifyListeners();
    try {
      profile = await _repository.login(username.trim(), password);
      status = AuthStatus.signedIn;
    } on AuthException catch (error) {
      failure = error;
      status = AuthStatus.signedOut;
    } on Object {
      failure = const AuthException('Sign in could not be completed.');
      status = AuthStatus.signedOut;
    }
    notifyListeners();
  }

  Future<void> retry() => _loadProfile();

  Future<void> _loadProfile() async {
    status = AuthStatus.loading;
    failure = null;
    notifyListeners();
    try {
      profile = await _repository.getProfile();
      status = AuthStatus.signedIn;
    } on AuthException catch (error) {
      failure = error;
      status = error.kind == AuthFailureKind.unauthorized
          ? AuthStatus.signedOut
          : AuthStatus.error;
    } on Object {
      failure = const AuthException('Profile could not be loaded.');
      status = AuthStatus.error;
    }
    notifyListeners();
  }

  Future<void> logout() async {
    profile = null;
    failure = null;
    status = AuthStatus.signedOut;
    notifyListeners();
    await _repository.logout();
  }
}
