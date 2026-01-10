#!/bin/bash
# Build Android AAB (release mode) using Docker
# Output: bin/habitforge-0.2.0-release.aab

echo -e "\033[0;32mBuilding HabitForge AAB for Google Play Store...\033[0m"
echo -e "\033[0;36mThis uses Google Play App Signing (no manual keystore required)\033[0m"
echo ""
echo "First build: 30-60 minutes (downloads SDK/NDK if needed)"
echo "Subsequent builds: 5-10 minutes"
echo ""

# Clean previous AAB/APK outputs to avoid confusion
echo -e "\033[0;33mCleaning previous builds...\033[0m"
rm -f bin/*.aab
echo "Removed old AAB files"
echo ""

# Run buildozer in release mode
docker run --rm \
  -v "$(pwd):/home/user/hostcwd" \
  -v "$HOME/.buildozer:/home/user/.buildozer" \
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
