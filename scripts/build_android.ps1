# Build Android APK using Docker

Write-Host "Building HabitForge APK with Docker..." -ForegroundColor Green
Write-Host "This will take 30-60 minutes on first build (downloads SDK/NDK)"
Write-Host "Subsequent builds: 5-10 minutes"
Write-Host ""

# Run buildozer - the kivy/buildozer image runs as root by default
# We've already set warn_on_root=0 in buildozer.spec
docker run --rm `
  -v "${PWD}:/home/user/hostcwd" `
  -v "$env:USERPROFILE\.buildozer:/home/user/.buildozer" `
  kivy/buildozer `
  --verbose android debug

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "Build complete! APK location:" -ForegroundColor Green
    Write-Host "  bin/habitforge-*-arm64-v8a-debug.apk"
} else {
    Write-Host ""
    Write-Host "Build failed! Check the log above for errors." -ForegroundColor Red
    exit 1
}
