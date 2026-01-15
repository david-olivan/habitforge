# Build Android APK locally with custom debug keystore for consistent signing

Write-Host "Building HabitForge APK with custom debug keystore..." -ForegroundColor Green
Write-Host ""

# Check if debug keystore exists
if (-not (Test-Path ".android/debug.keystore")) {
    Write-Host "Error: Debug keystore not found!" -ForegroundColor Red
    Write-Host "Please run: .\scripts\setup-debug-keystore.ps1" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

Write-Host "✓ Found debug keystore: .android/debug.keystore" -ForegroundColor Green
Write-Host ""

Write-Host "Building with Docker (this may take 30-60 minutes on first build)..." -ForegroundColor Cyan
Write-Host ""

# Get absolute path for mounting
$androidPath = (Resolve-Path ".android").Path
$buildozerPath = "$env:USERPROFILE\.buildozer"

# Run buildozer with custom keystore mounted
docker run --rm `
  -v "${PWD}:/home/user/hostcwd" `
  -v "$buildozerPath:/home/user/.buildozer" `
  -v "${androidPath}:/home/user/.android" `
  -e P4A_RELEASE_KEYSTORE="/home/user/.android/debug.keystore" `
  -e P4A_RELEASE_KEYSTORE_PASSWD="android" `
  -e P4A_RELEASE_KEYALIAS="androiddebugkey" `
  -e P4A_RELEASE_KEYALIAS_PASSWD="android" `
  kivy/buildozer `
  --verbose android debug

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✓ Build complete! APK location:" -ForegroundColor Green
    $apk = Get-ChildItem -Path "bin" -Filter "*-arm64-v8a-debug.apk" | Select-Object -First 1
    Write-Host "  $($apk.FullName)" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "This APK is signed with your custom debug keystore." -ForegroundColor Yellow
    Write-Host "You can update the installed app without uninstalling." -ForegroundColor Yellow
} else {
    Write-Host ""
    Write-Host "✗ Build failed! Check the log above for errors." -ForegroundColor Red
    exit 1
}
