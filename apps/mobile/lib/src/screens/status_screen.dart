import 'package:flutter/material.dart';

class StatusScreen extends StatelessWidget {
  const StatusScreen.loading({super.key})
      : message = null,
        onRetry = null,
        onLogout = null;

  const StatusScreen.error({
    required this.message,
    required this.onRetry,
    required this.onLogout,
    super.key,
  });

  final String? message;
  final Future<void> Function()? onRetry;
  final Future<void> Function()? onLogout;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Center(
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: message == null
                ? const CircularProgressIndicator()
                : Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const Icon(Icons.cloud_off_outlined, size: 56),
                      const SizedBox(height: 16),
                      Text(message!, textAlign: TextAlign.center),
                      const SizedBox(height: 24),
                      FilledButton(onPressed: onRetry, child: const Text('Retry')),
                      TextButton(
                        onPressed: onLogout,
                        child: const Text('Sign out'),
                      ),
                    ],
                  ),
          ),
        ),
      ),
    );
  }
}
