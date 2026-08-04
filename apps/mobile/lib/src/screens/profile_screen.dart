import 'package:flutter/material.dart';

import '../auth/auth_models.dart';

class ProfileScreen extends StatelessWidget {
  const ProfileScreen({required this.profile, required this.onLogout, super.key});

  final UserProfile profile;
  final Future<void> Function() onLogout;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Profile'),
        actions: [
          IconButton(
            key: const Key('logout-button'),
            tooltip: 'Sign out',
            onPressed: onLogout,
            icon: const Icon(Icons.logout),
          ),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.all(24),
        children: [
          CircleAvatar(
            radius: 40,
            child: Text(profile.username.characters.first.toUpperCase()),
          ),
          const SizedBox(height: 24),
          Text(profile.username, style: Theme.of(context).textTheme.headlineSmall),
          const SizedBox(height: 8),
          Text(profile.email),
          const SizedBox(height: 24),
          ListTile(
            leading: const Icon(Icons.verified_user_outlined),
            title: const Text('Account status'),
            subtitle: Text(profile.isActive ? 'Active' : 'Inactive'),
          ),
          ListTile(
            leading: const Icon(Icons.verified_outlined),
            title: const Text('Email verification'),
            subtitle: Text(profile.isVerified ? 'Verified' : 'Not verified'),
          ),
        ],
      ),
    );
  }
}
