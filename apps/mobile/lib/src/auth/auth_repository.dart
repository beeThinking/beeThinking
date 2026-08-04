import 'auth_models.dart';

abstract interface class AuthRepository {
  Future<bool> hasCredentials();
  Future<UserProfile> login(String username, String password);
  Future<UserProfile> getProfile();
  Future<void> logout();
}
