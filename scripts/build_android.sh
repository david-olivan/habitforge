#!/bin/bash
# Build Android APK using Docker

echo "Building HabitForge APK with Docker..."
echo "This will take 30-60 minutes on first build (downloads SDK/NDK)"
echo "Subsequent builds: 5-10 minutes"
echo ""

docker run --rm \
  -v "$(pwd):/home/user/hostcwd" \
  -v "$HOME/.buildozer:/home/user/.buildozer" \
  kivy/buildozer \
  android debug

echo ""
echo "Build complete! APK location:"
echo "  bin/habitforge-0.1.0-arm64-v8a-debug.apk"