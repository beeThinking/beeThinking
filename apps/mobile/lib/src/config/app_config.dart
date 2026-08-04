import 'package:flutter/foundation.dart';

class AppConfig {
  const AppConfig({required this.apiBaseUrl});

  factory AppConfig.fromEnvironment() {
    const configured = String.fromEnvironment('API_BASE_URL');
    final apiBaseUrl = configured.isEmpty && kDebugMode
        ? 'http://localhost:8000'
        : configured;
    if (apiBaseUrl.isEmpty) {
      throw StateError('API_BASE_URL is required outside debug builds.');
    }
    if (kReleaseMode && Uri.parse(apiBaseUrl).scheme != 'https') {
      throw StateError('Release API_BASE_URL must use HTTPS.');
    }
    return AppConfig(apiBaseUrl: apiBaseUrl);
  }

  final String apiBaseUrl;
}
