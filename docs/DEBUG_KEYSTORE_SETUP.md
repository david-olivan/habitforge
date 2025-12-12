# Debug Keystore Setup Guide

## Overview

To avoid signature conflicts when updating the app on your device, both local builds and CI builds must use the **same debug keystore**. This guide shows you how to set it up.

## Why This Matters

**Problem:** When you build an APK, Android signs it with a keystore. If different builds use different keystores, Android sees them as different apps and refuses to update:

```
INSTALL_FAILED_UPDATE_INCOMPATIBLE: Existing package signatures do not match
```

**Solution:** Use a consistent debug keystore for all builds.

---

## Part 1: Local Setup

### Step 1: Generate Debug Keystore

Run the setup script:

```powershell
# Windows PowerShell
.\scripts\setup-debug-keystore.ps1
```

```bash
# Linux/macOS
./scripts/setup-debug-keystore.sh
```

This creates `.android/debug.keystore` with these credentials:
- **Password:** `android`
- **Alias:** `androiddebugkey`
- **Validity:** 10,000 days (~27 years)

### Step 2: Verify Keystore

Check that it was created:

```powershell
# Windows
dir .android\

# Linux/macOS
ls -la .android/
```

You should see `debug.keystore` (~2KB file).

### Step 3: Build with Custom Keystore

Use the new build scripts:

```powershell
# Windows
.\scripts\build_android_local.ps1

# Linux/macOS
./scripts/build_android_local.sh
```

These scripts automatically use your custom keystore.

### Step 4: Test on Device

```bash
adb install -r bin/habitforge-*-arm64-v8a-debug.apk
```

**Result:** The app updates without uninstalling! ✅

---

## Part 2: CI Setup (GitHub Actions)

To make CI builds use the same keystore, you need to upload it as a GitHub secret.

### Step 1: Encode Keystore to Base64

```powershell
# Windows PowerShell
$bytes = [System.IO.File]::ReadAllBytes(".android\debug.keystore")
$base64 = [Convert]::ToBase64String($bytes)
$base64 | Set-Clipboard
Write-Host "✓ Keystore copied to clipboard!" -ForegroundColor Green
```

```bash
# Linux/macOS
base64 -i .android/debug.keystore | pbcopy  # macOS
base64 -i .android/debug.keystore | xclip   # Linux
echo "✓ Keystore copied to clipboard!"
```

The encoded keystore is now in your clipboard.

### Step 2: Add to GitHub Secrets

1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Create a secret:
   - **Name:** `DEBUG_KEYSTORE_BASE64`
   - **Value:** Paste from clipboard (Ctrl+V)
5. Click **Add secret**

### Step 3: Verify CI Configuration

The workflow `.github/workflows/release.yml` is already configured to:

1. Decode the base64 secret
2. Save it to `.android/debug.keystore`
3. Mount it into the Docker container
4. Pass keystore credentials to buildozer

**No changes needed** - it's ready to use!

---

## Security Notes

### ⚠️ Important: Debug Keystore Only!

**This keystore is for DEBUG BUILDS ONLY.** Never use it for production releases!

| Build Type | Keystore | Public? | Purpose |
|------------|----------|---------|---------|
| **Debug** | `.android/debug.keystore` | Can be shared in team | Development & testing |
| **Release** | `habitforge-release.keystore` | **KEEP PRIVATE!** | Production (Google Play) |

### What's Protected

✅ `.android/` is in `.gitignore` - won't be committed
✅ Keystore is base64-encoded in GitHub Secrets - encrypted at rest
✅ GitHub Actions logs never show secret values

### If Keystore is Compromised

Since this is a **debug** keystore (not production):

1. Delete `.android/debug.keystore`
2. Run `.\scripts\setup-debug-keystore.ps1` again
3. Update GitHub secret `DEBUG_KEYSTORE_BASE64`
4. Uninstall app from all test devices
5. Rebuild and reinstall

**No serious security impact** - it's only used for development.

---

## Troubleshooting

### Error: "Debug keystore not found!"

**Cause:** Script can't find `.android/debug.keystore`

**Solution:**
```powershell
# Run the setup script
.\scripts\setup-debug-keystore.ps1
```

### Error: "keytool not found"

**Cause:** Java JDK not installed or not in PATH

**Solution:**
1. Install Java JDK or Android Studio
2. Manually run:
   ```bash
   keytool -genkeypair -v -keystore .android/debug.keystore \
     -alias androiddebugkey -keyalg RSA -keysize 2048 -validity 10000 \
     -storepass android -keypass android \
     -dname "CN=HabitForge Debug,O=Davs,C=US"
   ```

### Error: "Context access might be invalid: DEBUG_KEYSTORE_BASE64"

**Cause:** IDE warning about GitHub secret (false positive)

**Solution:** Ignore it - the secret exists in GitHub, not in local code.

### Still Getting Signature Mismatch?

1. **Check local keystore:**
   ```bash
   keytool -list -v -keystore .android/debug.keystore -storepass android
   ```

2. **Check CI secret:**
   - Go to GitHub → Settings → Secrets
   - Verify `DEBUG_KEYSTORE_BASE64` exists

3. **Rebuild both:**
   - Delete old APK: `rm bin/*.apk`
   - Build locally: `.\scripts\build_android_local.ps1`
   - Build in CI: Push a tag

4. **Last resort:**
   ```bash
   # Uninstall app
   adb uninstall com.davs.habitforge

   # Install fresh
   adb install bin/habitforge-*-debug.apk
   ```

---

## Advanced: Migrating Existing Installations

If you already have the app installed with a different keystore:

### Option 1: Backup Data First (Recommended)

```bash
# Backup app data
adb backup -f habitforge_backup.ab com.davs.habitforge

# Uninstall old version
adb uninstall com.davs.habitforge

# Install new version
adb install bin/habitforge-*-debug.apk

# Restore data
adb restore habitforge_backup.ab
```

### Option 2: Fresh Install (Simpler)

```bash
# Uninstall (loses data)
adb uninstall com.davs.habitforge

# Install with new keystore
adb install bin/habitforge-*-debug.apk
```

Going forward, all updates will work without uninstalling!

---

## Team Collaboration

If you're working with a team:

1. **Share the keystore** (it's just for debug):
   - Send `.android/debug.keystore` to team members via secure channel
   - Or have them use the same setup script with **same password**

2. **Everyone uses same keystore**:
   - All team members can install each other's builds
   - All CI builds are compatible

3. **For production releases**:
   - Use a separate, **private** release keystore
   - Never share the production keystore!

---

## Next Steps

After setting up the debug keystore:

1. ✅ Build locally: `.\scripts\build_android_local.ps1`
2. ✅ Push tag to trigger CI: `git tag v0.1.2 && git push origin v0.1.2`
3. ✅ Install from either build - both work!
4. ✅ Update anytime without data loss

---

## Quick Reference

| Task | Command |
|------|---------|
| **Generate keystore** | `.\scripts\setup-debug-keystore.ps1` |
| **Build locally** | `.\scripts\build_android_local.ps1` |
| **Install APK** | `adb install -r bin/habitforge-*-debug.apk` |
| **Check keystore** | `keytool -list -v -keystore .android/debug.keystore -storepass android` |
| **Base64 encode** | See "Part 2: CI Setup" above |

---

**Questions?** Check the main [README.md](../README.md) or open an issue.