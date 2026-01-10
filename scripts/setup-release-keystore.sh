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

# Generate keystore with keytool
keytool -genkey -v \
  -keystore "$KEYSTORE_FILE" \
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