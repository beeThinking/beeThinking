import 'dart:convert';

import 'package:flutter_secure_storage/flutter_secure_storage.dart';

import 'auth_models.dart';

abstract interface class TokenStore {
  Future<TokenPair?> read();
  Future<void> write(TokenPair tokens);
  Future<void> clear();
}

class SecureTokenStore implements TokenStore {
  SecureTokenStore([FlutterSecureStorage? storage])
      : _storage = storage ?? const FlutterSecureStorage();

  static const _credentialsKey = 'auth_credentials';
  final FlutterSecureStorage _storage;

  @override
  Future<TokenPair?> read() async {
    final encoded = await _storage.read(key: _credentialsKey);
    if (encoded == null) return null;
    try {
      return TokenPair.fromJson(jsonDecode(encoded) as Map<String, dynamic>);
    } on Object {
      await clear();
      return null;
    }
  }

  @override
  Future<void> write(TokenPair tokens) async {
    await _storage.write(
      key: _credentialsKey,
      value: jsonEncode({
        'access_token': tokens.accessToken,
        'refresh_token': tokens.refreshToken,
      }),
    );
  }

  @override
  Future<void> clear() => _storage.delete(key: _credentialsKey);
}
