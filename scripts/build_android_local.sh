#!/bin/bash
# Build Android APK locally with custom debug keystore for consistent signing

echo "Building HabitForge APK with custom debug keystore..."
echo ""

# Check if debug keystore exists
if [ ! -f ".android/debug.keystore" ]; then
    echo "Error: Debug keystore not found!"
    echo "Please run: ./scripts/setup-debug-keystore.ps1"
    echo ""
    echo "Or create it manually with:"
    echo 'keytool -genkeypair -v -keystore .android/debug.keystore \\'
    echo '  -alias androiddebugkey -keyalg RSA -keysize 2048 -validity 10000 \\'
    echo '  -storepass android -keypass android \\'
    echo '  -dname "CN=HabitForge Debug,O=Davs,C=US"'
    exit 1
fi

echo "✓ Found debug keystore: .android/debug.keystore"
echo ""

# Export debug keystore path for buildozer
export P4A_RELEASE_KEYSTORE="$PWD/.android/debug.keystore"
export P4A_RELEASE_KEYSTORE_PASSWD="android"
export P4A_RELEASE_KEYALIAS="androiddebugkey"
export P4A_RELEASE_KEYALIAS_PASSWD="android"

echo "Building with Docker (this may take 30-60 minutes on first build)..."
echo ""

# Run buildozer with custom keystore mounted
docker run --rm \
  -v "$(pwd):/home/user/hostcwd" \
  -v "$HOME/.buildozer:/home/user/.buildozer" \
  -v "$(pwd)/.android:/home/user/.android" \
  -e P4A_RELEASE_KEYSTORE="/home/user/.android/debug.keystore" \
  -e P4A_RELEASE_KEYSTORE_PASSWD="android" \
  -e P4A_RELEASE_KEYALIAS="androiddebugkey" \
  -e P4A_RELEASE_KEYALIAS_PASSWD="android" \
  kivy/buildozer \
  --verbose android debug

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Build complete! APK location:"
    echo "  bin/habitforge-*-arm64-v8a-debug.apk"
    echo ""
    echo "This APK is signed with your custom debug keystore."
    echo "You can update the installed app without uninstalling."
else
    echo ""
    echo "✗ Build failed! Check the log above for errors."
    exit 1
fi
