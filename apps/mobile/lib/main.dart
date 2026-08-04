import 'package:flutter/material.dart';

import 'src/app.dart';
import 'src/auth/auth_api.dart';
import 'src/auth/auth_controller.dart';
import 'src/auth/token_store.dart';
import 'src/config/app_config.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  final config = AppConfig.fromEnvironment();
  final tokenStore = SecureTokenStore();
  final authApi = AuthApi(baseUrl: config.apiBaseUrl, tokenStore: tokenStore);
  runApp(BeeThinkingApp(controller: AuthController(authApi)..restoreSession()));
}
