#!/bin/bash
# Build Android APK using Docker

echo "Building HabitForge APK with Docker..."
echo "This will take 30-60 minutes on first build (downloads SDK/NDK)"
echo "Subsequent builds: 5-10 minutes"
echo ""

# Run buildozer - the kivy/buildozer image runs as root by default
# We've already set warn_on_root=0 in buildozer.spec
docker run --rm \
  -v "$(pwd):/home/user/hostcwd" \
  -v "$HOME/.buildozer:/home/user/.buildozer" \
  kivy/buildozer \
  --verbose android debug

if [ $? -eq 0 ]; then
    echo ""
    echo "Build complete! APK location:"
    echo "  bin/habitforge-0.1.0-arm64-v8a-debug.apk"
else
    echo ""
    echo "Build failed! Check the log above for errors."
    exit 1
fi