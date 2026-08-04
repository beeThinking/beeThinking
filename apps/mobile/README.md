# BeeThinking Mobile

iOS-first Flutter client for BeeThinking authentication and profile access.

## Run

Debug builds default to the iOS Simulator backend at `http://localhost:8000`:

```sh
flutter --directory apps/mobile run
```

Override the backend at build time:

```sh
flutter --directory apps/mobile run --dart-define=API_BASE_URL=https://api.example.com
```

Non-debug builds require `API_BASE_URL`. Release builds reject non-HTTPS URLs. The iOS debug configuration permits insecure HTTP only for `localhost`; release and profile configurations have no App Transport Security exception.
