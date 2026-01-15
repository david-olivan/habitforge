#!/bin/bash
# Create release keystore for Google Play Store uploads
# This creates the UPLOAD KEY (not the app signing key - Google manages that)

KEYSTORE_DIR=".android"
KEYSTORE_FILE="$KEYSTORE_DIR/release.keystore"
ALIAS="habitforge-upload-key"

echo "=========================================="
echo "HabitForge Release Keystore Setup"
echo "=========================================="
echo ""
echo "This will create your UPLOAD KEY for Google Play Store."
echo "Google will manage the actual APP SIGNING KEY."
echo ""
echo "IMPORTANT: Keep this keystore file and passwords SECURE!"
echo "You'll need them for every app update."
echo ""

# Create directory if needed
mkdir -p "$KEYSTORE_DIR"

# Check if keystore already exists
if [ -f "$KEYSTORE_FILE" ]; then
    echo "⚠️  WARNING: Release keystore already exists!"
    echo "File: $KEYSTORE_FILE"
    echo ""
    read -p "Do you want to overwrite it? (yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        echo "Cancelled. Existing keystore preserved."
        exit 0
    fi
    rm -f "$KEYSTORE_FILE"
fi

echo ""
echo "Creating release keystore..."
echo "You will be prompted for:"
echo "1. Keystore password (choose a strong password!)"
echo "2. Key password (can be same as keystore password)"
echo "3. Your details (name, organization, etc.)"
echo ""

# Find keytool - check Windows Java installation first, then Linux
KEYTOOL=""
if [ -f "/c/Program Files/Microsoft/jdk-17.0.17.10-hotspot/bin/keytool.exe" ]; then
    KEYTOOL="/c/Program Files/Microsoft/jdk-17.0.17.10-hotspot/bin/keytool.exe"
elif command -v keytool &> /dev/null; then
    KEYTOOL="keytool"
else
    echo "❌ ERROR: keytool not found!"
    echo ""
    echo "Please install Java JDK:"
    echo "  - Windows: Download from https://adoptium.net/"
    echo "  - WSL: sudo apt-get install openjdk-17-jdk"
    exit 1
fi

echo "Using keytool: $KEYTOOL"
echo ""

# Convert Windows path to WSL path for keystore file
WIN_KEYSTORE_PATH=$(wslpath -w "$(pwd)/$KEYSTORE_FILE" 2>/dev/null || echo "$KEYSTORE_FILE")

# Generate keystore with keytool
"$KEYTOOL" -genkey -v \
  -keystore "$WIN_KEYSTORE_PATH" \
  -alias "$ALIAS" \
  -keyalg RSA \
  -keysize 2048 \
  -validity 10000

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ SUCCESS! Release keystore created:"
    echo "   Location: $KEYSTORE_FILE"
    echo "   Alias: $ALIAS"
    echo ""
    echo "CRITICAL: Store these securely:"
    echo "  1. Keystore file: $KEYSTORE_FILE"
    echo "  2. Keystore password (you just entered)"
    echo "  3. Key alias: $ALIAS"
    echo "  4. Key password (you just entered)"
    echo ""
    echo "Next steps:"
    echo "  1. Back up $KEYSTORE_FILE to a secure location"
    echo "  2. Create .android/keystore.properties with passwords"
    echo "  3. Run: ./scripts/build_android_aab.sh"
    echo ""
else
    echo ""
    echo "❌ ERROR: Failed to create keystore"
    exit 1
fi
