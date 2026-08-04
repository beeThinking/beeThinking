class TokenPair {
  const TokenPair({required this.accessToken, required this.refreshToken});

  factory TokenPair.fromJson(Map<String, dynamic> json) {
    final accessToken = json['access_token'];
    final refreshToken = json['refresh_token'];
    if (accessToken is! String || refreshToken is! String) {
      throw const AuthException('Server returned invalid credentials.');
    }
    return TokenPair(accessToken: accessToken, refreshToken: refreshToken);
  }

  final String accessToken;
  final String refreshToken;
}

class UserProfile {
  const UserProfile({
    required this.id,
    required this.username,
    required this.email,
    required this.isActive,
    required this.isVerified,
    required this.isAdmin,
    required this.createdAt,
  });

  factory UserProfile.fromJson(Map<String, dynamic> json) {
    return UserProfile(
      id: json['id'] as int,
      username: json['username'] as String,
      email: json['email'] as String,
      isActive: json['is_active'] as bool,
      isVerified: json['is_verified'] as bool,
      isAdmin: json['is_admin'] as bool,
      createdAt: DateTime.parse(json['created_at'] as String),
    );
  }

  final int id;
  final String username;
  final String email;
  final bool isActive;
  final bool isVerified;
  final bool isAdmin;
  final DateTime createdAt;
}

enum AuthFailureKind { unauthorized, validation, rateLimited, offline, server }

class AuthException implements Exception {
  const AuthException(this.message, {this.kind = AuthFailureKind.server});

  final String message;
  final AuthFailureKind kind;

  @override
  String toString() => message;
}
