@echo off
echo Building Android APK for Structural Analysis App...

cd android_app

if not exist gradle\wrapper\gradle-wrapper.jar (
    echo Creating Gradle wrapper...
    mkdir -p gradle\wrapper
    powershell -Command "(New-Object System.Net.WebClient).DownloadFile('https://repo.maven.apache.org/maven2/org/gradle/gradle-wrapper/7.6.1/gradle-wrapper-7.6.1.jar', 'gradle\wrapper\gradle-wrapper.jar')"
)

call gradlew.bat assembleDebug

echo.
if %ERRORLEVEL% EQU 0 (
    echo Build successful!
    echo.
    echo APK location: android_app\app\build\outputs\apk\debug\app-debug.apk
    echo.
    echo Install instructions:
    echo 1. Transfer the APK to your Android device
    echo 2. On your device, enable "Install from Unknown Sources" in settings
    echo 3. Open the APK file on your device to install
) else (
    echo Build failed. Please check the error messages above.
)

pause 