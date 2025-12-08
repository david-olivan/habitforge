# Build Android APK using Docker

Write-Host "Building HabitForge APK with Docker..." -ForegroundColor Green
Write-Host "This will take 30-60 minutes on first build (downloads SDK/NDK)"
Write-Host "Subsequent builds: 5-10 minutes"
Write-Host ""

docker run --rm `
  -v "${PWD}:/home/user/hostcwd" `
  -v "$env:USERPROFILE\.buildozer:/home/user/.buildozer" `
  kivy/buildozer `
  android debug

Write-Host ""
Write-Host "Build complete! APK location:" -ForegroundColor Green
Write-Host "  bin/habitforge-0.1.0-arm64-v8a-debug.apk"