import 'dart:async';
import 'dart:convert';

import 'package:bee_thinking_mobile/src/auth/auth_api.dart';
import 'package:bee_thinking_mobile/src/auth/auth_models.dart';
import 'package:bee_thinking_mobile/src/auth/token_store.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';

void main() {
  const original = TokenPair(accessToken: 'old-access', refreshToken: 'old-refresh');
  const replacement = TokenPair(
    accessToken: 'new-access',
    refreshToken: 'new-refresh',
  );

  test('login sends form credentials and stores returned tokens', () async {
    final store = MemoryTokenStore();
    final client = MockClient((request) async {
      if (request.url.path == '/api/auth/login') {
        expect(request.headers['content-type'], contains('form-urlencoded'));
        expect(request.bodyFields, {'username': 'beekeeper', 'password': 'secret'});
        return http.Response(
          jsonEncode({
            'access_token': original.accessToken,
            'refresh_token': original.refreshToken,
            'token_type': 'bearer',
          }),
          200,
        );
      }
      expect(request.headers['authorization'], 'Bearer old-access');
      return profileResponse;
    });
    final api = AuthApi(
      baseUrl: 'http://localhost:8000',
      tokenStore: store,
      client: client,
    );

    final profile = await api.login('beekeeper', 'secret');

    expect(profile.username, 'beekeeper');
    expect((await store.read())?.refreshToken, original.refreshToken);
  });

  test('concurrent 401 responses use one refresh and persist before replay', () async {
    final store = MemoryTokenStore(original);
    var refreshCount = 0;
    final oldRequestsReady = Completer<void>();
    var oldRequestCount = 0;
    final client = MockClient((request) async {
      if (request.url.path == '/api/auth/refresh') {
        refreshCount++;
        expect(jsonDecode(request.body), {'refresh_token': 'old-refresh'});
        return http.Response(
          jsonEncode({
            'access_token': replacement.accessToken,
            'refresh_token': replacement.refreshToken,
          }),
          200,
        );
      }
      if (request.headers['authorization'] == 'Bearer old-access') {
        oldRequestCount++;
        if (oldRequestCount == 2) oldRequestsReady.complete();
        await oldRequestsReady.future;
        return http.Response('', 401);
      }
      expect((await store.read())?.accessToken, replacement.accessToken);
      expect(request.headers['authorization'], 'Bearer new-access');
      return profileResponse;
    });
    final api = AuthApi(
      baseUrl: 'http://localhost:8000',
      tokenStore: store,
      client: client,
    );

    await Future.wait([api.getProfile(), api.getProfile()]);

    expect(refreshCount, 1);
    expect((await store.read())?.refreshToken, replacement.refreshToken);
  });

  test('ambiguous refresh failure clears credentials without retrying', () async {
    final store = MemoryTokenStore(original);
    var refreshCount = 0;
    final client = MockClient((request) async {
      if (request.url.path == '/api/auth/refresh') {
        refreshCount++;
        throw http.ClientException('connection lost');
      }
      return http.Response('', 401);
    });
    final api = AuthApi(
      baseUrl: 'http://localhost:8000',
      tokenStore: store,
      client: client,
    );

    await expectLater(api.getProfile(), throwsA(isA<AuthException>()));

    expect(refreshCount, 1);
    expect(await store.read(), isNull);
  });

  test('logout clears credentials before revocation completes', () async {
    final store = MemoryTokenStore(original);
    final releaseResponse = Completer<http.Response>();
    final client = MockClient((request) async {
      expect(jsonDecode(request.body), {'refresh_token': 'old-refresh'});
      return releaseResponse.future;
    });
    final api = AuthApi(
      baseUrl: 'http://localhost:8000',
      tokenStore: store,
      client: client,
    );

    final logout = api.logout();
    await Future<void>.delayed(Duration.zero);
    expect(await store.read(), isNull);
    releaseResponse.complete(http.Response('', 204));
    await logout;
  });

  test('logout during refresh never restores rotated credentials', () async {
    final store = MemoryTokenStore(original);
    final refreshStarted = Completer<void>();
    final releaseRefresh = Completer<http.Response>();
    final client = MockClient((request) async {
      if (request.url.path == '/api/users/me') return http.Response('', 401);
      if (request.url.path == '/api/auth/logout') return http.Response('', 204);
      refreshStarted.complete();
      return releaseRefresh.future;
    });
    final api = AuthApi(
      baseUrl: 'http://localhost:8000',
      tokenStore: store,
      client: client,
    );

    final profile = api.getProfile();
    await refreshStarted.future;
    await api.logout();
    releaseRefresh.complete(
      http.Response(
        jsonEncode({
          'access_token': replacement.accessToken,
          'refresh_token': replacement.refreshToken,
        }),
        200,
      ),
    );

    await expectLater(profile, throwsA(isA<AuthException>()));
    expect(await store.read(), isNull);
  });
}

final profileResponse = http.Response(
  jsonEncode({
    'id': 1,
    'username': 'beekeeper',
    'email': 'bee@example.com',
    'is_active': true,
    'is_verified': true,
    'is_admin': false,
    'created_at': '2026-08-03T10:00:00Z',
  }),
  200,
);

class MemoryTokenStore implements TokenStore {
  MemoryTokenStore([this.tokens]);

  TokenPair? tokens;

  @override
  Future<void> clear() async => tokens = null;

  @override
  Future<TokenPair?> read() async => tokens;

  @override
  Future<void> write(TokenPair tokens) async => this.tokens = tokens;
}
