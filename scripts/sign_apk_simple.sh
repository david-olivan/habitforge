#!/bin/bash
# Simple APK signing using uber-apk-signer tool (pure Java, works anywhere)

if [ -z "$1" ]; then
    echo "Usage: ./scripts/sign_apk_simple.sh <path-to-unsigned-apk>"
    exit 1
fi

UNSIGNED_APK="$1"
SIGNED_APK="${UNSIGNED_APK%.apk}-signed.apk"
KEYSTORE=".android/debug.keystore"
SIGNER_JAR="scripts/uber-apk-signer.jar"

if [ ! -f "$UNSIGNED_APK" ]; then
    echo "Error: APK not found: $UNSIGNED_APK"
    exit 1
fi

if [ ! -f "$KEYSTORE" ]; then
    echo "Error: Keystore not found: $KEYSTORE"
    exit 1
fi

# Download uber-apk-signer if not present
if [ ! -f "$SIGNER_JAR" ]; then
    echo "Downloading uber-apk-signer..."
    curl -L -o "$SIGNER_JAR" "https://github.com/patrickfav/uber-apk-signer/releases/download/v1.3.0/uber-apk-signer-1.3.0.jar"
    if [ $? -ne 0 ]; then
        echo "Error: Failed to download uber-apk-signer"
        exit 1
    fi
fi

echo "Signing APK with APK Signature Scheme v2/v3..."
echo "  Input:  $UNSIGNED_APK"
echo "  Output: $SIGNED_APK"
echo ""

# Remove old signed version if exists
rm -f "$SIGNED_APK"

# Sign with uber-apk-signer (supports v1, v2, v3, v4 signatures)
java -jar "$SIGNER_JAR" \
  --apks "$UNSIGNED_APK" \
  --ks "$KEYSTORE" \
  --ksAlias androiddebugkey \
  --ksPass android \
  --ksKeyPass android \
  --allowResign \
  --overwrite

# Find the signed APK (uber-apk-signer adds -aligned-debugSigned suffix)
GENERATED_APK="${UNSIGNED_APK%.apk}-aligned-debugSigned.apk"

if [ -f "$GENERATED_APK" ]; then
    mv "$GENERATED_APK" "$SIGNED_APK"
    echo ""
    echo "✓ APK signed successfully!"
    echo ""
    echo "Ready to install: $SIGNED_APK"
    echo ""
    echo "To install:"
    echo "  adb install -r $SIGNED_APK"
else
    echo ""
    echo "✗ Signing failed! Generated APK not found."
    ls -la "${UNSIGNED_APK%.apk}"*.apk
    exit 1
fi