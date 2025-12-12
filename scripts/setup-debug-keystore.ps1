# Setup Debug Keystore for Consistent Signing
# This script generates a debug keystore that will be used for all builds

Write-Host "Setting up debug keystore for HabitForge..." -ForegroundColor Green
Write-Host ""

# Find keytool (should be in JAVA_HOME/bin or Android SDK)
$keytoolPaths = @(
    "$env:JAVA_HOME\bin\keytool.exe",
    "$env:ANDROID_HOME\openjdk\bin\keytool.exe",
    "C:\Program Files\Android\Android Studio\jbr\bin\keytool.exe",
    "C:\Program Files\Java\jdk*\bin\keytool.exe"
)

$keytool = $null
foreach ($path in $keytoolPaths) {
    if (Test-Path $path) {
        $keytool = $path
        break
    }
    # Try wildcard expansion for JDK
    $expanded = Get-ChildItem -Path (Split-Path $path) -Filter (Split-Path $path -Leaf) -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($expanded) {
        $keytool = $expanded.FullName
        break
    }
}

if (-not $keytool) {
    Write-Host "Error: keytool not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Java JDK or Android Studio, then run this script again." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Or manually run this command (adjust path to your keytool):" -ForegroundColor Cyan
    Write-Host 'keytool -genkeypair -v -keystore .android/debug.keystore -alias androiddebugkey -keyalg RSA -keysize 2048 -validity 10000 -storepass android -keypass android -dname "CN=HabitForge Debug,O=Davs,C=US"'
    exit 1
}

Write-Host "Found keytool: $keytool" -ForegroundColor Green

# Create .android directory
if (-not (Test-Path ".android")) {
    New-Item -ItemType Directory -Path ".android" | Out-Null
    Write-Host "Created .android directory" -ForegroundColor Green
}

# Check if keystore already exists
if (Test-Path ".android/debug.keystore") {
    Write-Host ""
    Write-Host "Warning: debug.keystore already exists!" -ForegroundColor Yellow
    $response = Read-Host "Do you want to overwrite it? (y/N)"
    if ($response -ne "y") {
        Write-Host "Keeping existing keystore. Exiting." -ForegroundColor Cyan
        exit 0
    }
    Remove-Item ".android/debug.keystore" -Force
}

# Generate keystore
Write-Host ""
Write-Host "Generating debug keystore..." -ForegroundColor Cyan
Write-Host ""

& $keytool -genkeypair -v `
    -keystore ".android/debug.keystore" `
    -alias androiddebugkey `
    -keyalg RSA `
    -keysize 2048 `
    -validity 10000 `
    -storepass android `
    -keypass android `
    -dname "CN=HabitForge Debug,O=Davs,C=US"

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✓ Debug keystore created successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Location: .android/debug.keystore" -ForegroundColor Cyan
    Write-Host "Password: android" -ForegroundColor Cyan
    Write-Host "Alias: androiddebugkey" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "IMPORTANT: This keystore is for DEBUG BUILDS ONLY!" -ForegroundColor Yellow
    Write-Host "It's excluded from git (.gitignore) for security." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "1. The keystore is ready for local builds"
    Write-Host "2. For CI builds, you need to add it as a GitHub secret"
    Write-Host "3. See docs/DEBUG_KEYSTORE_SETUP.md for instructions"
} else {
    Write-Host ""
    Write-Host "✗ Failed to create keystore!" -ForegroundColor Red
    exit 1
}