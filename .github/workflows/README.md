# GitHub Workflows

Available Workflows:

1. build-android.yml - Builds Android Debug APK
   Trigger: push, pull_request, workflow_dispatch
   Output: APK artifact uploaded

2. run-tests.yml - Runs unit tests
   Trigger: push, pull_request, workflow_dispatch
   Output: Test results artifact uploaded

How to use:
- Push to main branch to trigger automatically
- Or manually trigger from Actions tab

Artifacts:
- Android APK: bin/*.apk (retention: 30 days)
- Test results: test-results/ (retention: 7 days)

Requirements:
- Android build: ~30-60 minutes, 5GB storage
- Tests: Python 3.10, pytest

Notes:
- Android builds take time due to SDK download
- First build may take longer
- APK supports arm64-v8a and armeabi-v7a
- Minimum API: 21, Target API: 30
