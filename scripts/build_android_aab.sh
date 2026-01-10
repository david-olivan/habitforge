#!/bin/bash
# Build Android AAB (release mode) using Docker with signing
# Output: bin/habitforge-0.2.0-release.aab (signed)

echo -e "\033[0;32mBuilding HabitForge AAB for Google Play Store...\033[0m"
echo ""

# Check if release keystore exists
KEYSTORE_FILE=".android/release.keystore"
if [ ! -f "$KEYSTORE_FILE" ]; then
    echo -e "\033[0;31m❌ ERROR: Release keystore not found!\033[0m"
    echo ""
    echo "You need to create a release keystore first."
    echo "Run: ./scripts/setup-release-keystore.sh"
    echo ""
    exit 1
fi

echo -e "\033[0;32m✓ Found release keystore\033[0m"
echo ""

# Prompt for keystore passwords
echo "Enter keystore password:"
read -s KEYSTORE_PASSWD
echo ""
echo "Enter key password (press Enter if same as keystore password):"
read -s KEY_PASSWD
if [ -z "$KEY_PASSWD" ]; then
    KEY_PASSWD="$KEYSTORE_PASSWD"
fi
echo ""

echo "Build configuration:"
echo "  - First build: 30-60 minutes (downloads SDK/NDK)"
echo "  - Subsequent builds: 5-10 minutes"
echo "  - Keystore: $KEYSTORE_FILE"
echo "  - Alias: habitforge-upload-key"
echo ""

# Clean previous AAB/APK outputs to avoid confusion
echo -e "\033[0;33mCleaning previous builds...\033[0m"
rm -f bin/*.aab
echo "Removed old AAB files"
echo ""

# Run buildozer in release mode with signing
echo -e "\033[0;36mBuilding signed AAB...\033[0m"
echo ""

docker run --rm \
  -v "$(pwd):/home/user/hostcwd" \
  -v "$HOME/.buildozer:/home/user/.buildozer" \
  -v "$(pwd)/.android:/home/user/.android" \
  -e P4A_RELEASE_KEYSTORE="/home/user/.android/release.keystore" \
  -e P4A_RELEASE_KEYSTORE_PASSWD="$KEYSTORE_PASSWD" \
  -e P4A_RELEASE_KEYALIAS="habitforge-upload-key" \
  -e P4A_RELEASE_KEYALIAS_PASSWD="$KEY_PASSWD" \
  kivy/buildozer \
  --verbose android release

if [ $? -eq 0 ]; then
    echo ""
    echo -e "\033[0;32m========================================\033[0m"
    echo -e "\033[0;32mAAB BUILD SUCCESSFUL!\033[0m"
    echo -e "\033[0;32m========================================\033[0m"
    echo ""
    echo -e "\033[0;36mOutput location:\033[0m"
    for aab in bin/*.aab; do
        if [ -f "$aab" ]; then
            echo -e "  \033[1;37m$aab\033[0m"
            size=$(du -h "$aab" | cut -f1)
            echo -e "  Size: $size"
        fi
    done
    echo ""
    echo -e "\033[0;33mNext steps:\033[0m"
    echo "1. Go to Google Play Console: https://play.google.com/console"
    echo "2. Select HabitForge app (or create new app)"
    echo "3. Navigate to: Release > Testing > Internal testing"
    echo "4. Create new release and upload this AAB"
    echo "5. Add release notes (see release-notes-*.txt files)"
    echo "6. Review and publish to internal testing track"
    echo ""
else
    echo ""
    echo -e "\033[0;31mBuild failed! Check the log above for errors.\033[0m"
    exit 1
fi
