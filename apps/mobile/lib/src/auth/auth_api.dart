import 'dart:async';
import 'dart:convert';
import 'dart:io';

import 'package:http/http.dart' as http;

import 'auth_models.dart';
import 'auth_repository.dart';
import 'token_store.dart';

class AuthApi implements AuthRepository {
  AuthApi({
    required String baseUrl,
    required TokenStore tokenStore,
    http.Client? client,
    this.timeout = const Duration(seconds: 15),
  })  : _baseUrl = baseUrl.replaceFirst(RegExp(r'/$'), ''),
        _tokenStore = tokenStore,
        _client = client ?? http.Client();

  final String _baseUrl;
  final TokenStore _tokenStore;
  final http.Client _client;
  final Duration timeout;
  Future<TokenPair>? _refreshInFlight;
  int _credentialGeneration = 0;

  Uri _uri(String path) => Uri.parse('$_baseUrl/api$path');

  @override
  Future<bool> hasCredentials() async => await _tokenStore.read() != null;

  @override
  Future<UserProfile> login(String username, String password) async {
    _credentialGeneration++;
    final response = await _network(
      () => _client
          .post(
            _uri('/auth/login'),
            headers: const {
              'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: {'username': username, 'password': password},
          )
          .timeout(timeout),
    );
    if (response.statusCode != 200) throw _responseFailure(response);
    final tokens = TokenPair.fromJson(_json(response));
    await _tokenStore.write(tokens);
    try {
      return await getProfile();
    } catch (_) {
      await _tokenStore.clear();
      rethrow;
    }
  }

  @override
  Future<UserProfile> getProfile() async {
    final response = await _protectedGet('/users/me');
    if (response.statusCode != 200) throw _responseFailure(response);
    try {
      return UserProfile.fromJson(_json(response));
    } on Object {
      throw const AuthException('Server returned an invalid profile.');
    }
  }

  Future<http.Response> _protectedGet(String path) async {
    var tokens = await _tokenStore.read();
    if (tokens == null) {
      throw const AuthException(
        'Please sign in again.',
        kind: AuthFailureKind.unauthorized,
      );
    }
    var response = await _authorizedGet(path, tokens.accessToken);
    if (response.statusCode != 401) return response;

    final latest = await _tokenStore.read();
    if (latest == null) {
      throw const AuthException(
        'Please sign in again.',
        kind: AuthFailureKind.unauthorized,
      );
    }
    tokens = latest.accessToken == tokens.accessToken
        ? await _refreshSingleFlight()
        : latest;
    response = await _authorizedGet(path, tokens.accessToken);
    if (response.statusCode == 401) {
      await _tokenStore.clear();
      throw const AuthException(
        'Your session expired. Please sign in again.',
        kind: AuthFailureKind.unauthorized,
      );
    }
    return response;
  }

  Future<http.Response> _authorizedGet(String path, String accessToken) {
    return _network(
      () => _client.get(
        _uri(path),
        headers: {'Authorization': 'Bearer $accessToken'},
      ).timeout(timeout),
    );
  }

  Future<TokenPair> _refreshSingleFlight() {
    return _refreshInFlight ??= _refresh().whenComplete(() {
      _refreshInFlight = null;
    });
  }

  Future<TokenPair> _refresh() async {
    final generation = _credentialGeneration;
    final current = await _tokenStore.read();
    if (current == null) {
      throw const AuthException(
        'Please sign in again.',
        kind: AuthFailureKind.unauthorized,
      );
    }
    try {
      final response = await _client
          .post(
            _uri('/auth/refresh'),
            headers: const {'Content-Type': 'application/json'},
            body: jsonEncode({'refresh_token': current.refreshToken}),
          )
          .timeout(timeout);
      if (response.statusCode != 200) {
        throw _responseFailure(response);
      }
      final replacement = TokenPair.fromJson(_json(response));
      if (generation != _credentialGeneration) {
        throw const AuthException(
          'Please sign in again.',
          kind: AuthFailureKind.unauthorized,
        );
      }
      await _tokenStore.write(replacement);
      if (generation != _credentialGeneration) {
        final stored = await _tokenStore.read();
        if (stored?.refreshToken == replacement.refreshToken) {
          await _tokenStore.clear();
        }
        throw const AuthException(
          'Please sign in again.',
          kind: AuthFailureKind.unauthorized,
        );
      }
      return replacement;
    } on AuthException {
      if (generation == _credentialGeneration) await _tokenStore.clear();
      rethrow;
    } on Object {
      if (generation == _credentialGeneration) await _tokenStore.clear();
      throw const AuthException(
        'Session refresh could not be confirmed. Please sign in again.',
        kind: AuthFailureKind.unauthorized,
      );
    }
  }

  @override
  Future<void> logout() async {
    final tokens = await _tokenStore.read();
    _credentialGeneration++;
    await _tokenStore.clear();
    if (tokens == null) return;
    try {
      await _client
          .post(
            _uri('/auth/logout'),
            headers: const {'Content-Type': 'application/json'},
            body: jsonEncode({'refresh_token': tokens.refreshToken}),
          )
          .timeout(timeout);
    } on Object {
      return;
    }
  }

  Future<http.Response> _network(
    Future<http.Response> Function() request,
  ) async {
    try {
      return await request();
    } on SocketException {
      throw const AuthException(
        'You appear to be offline.',
        kind: AuthFailureKind.offline,
      );
    } on http.ClientException {
      throw const AuthException(
        'You appear to be offline.',
        kind: AuthFailureKind.offline,
      );
    } on TimeoutException {
      throw const AuthException(
        'The request timed out. Try again.',
        kind: AuthFailureKind.offline,
      );
    }
  }

  Map<String, dynamic> _json(http.Response response) {
    final value = jsonDecode(response.body);
    if (value is! Map<String, dynamic>) {
      throw const AuthException('Server returned an invalid response.');
    }
    return value;
  }

  AuthException _responseFailure(http.Response response) {
    return switch (response.statusCode) {
      401 => const AuthException(
          'Incorrect username or password.',
          kind: AuthFailureKind.unauthorized,
        ),
      422 => const AuthException(
          'Check the entered username and password.',
          kind: AuthFailureKind.validation,
        ),
      429 => const AuthException(
          'Too many attempts. Try again later.',
          kind: AuthFailureKind.rateLimited,
        ),
      _ => const AuthException('BeeThinking is unavailable. Try again.'),
    };
  }
}
