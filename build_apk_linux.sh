#!/bin/bash

echo "Building Android APK for Structural Analysis App..."

cd android_app

# Create gradle wrapper if it doesn't exist
if [ ! -f "gradle/wrapper/gradle-wrapper.jar" ]; then
    echo "Creating Gradle wrapper..."
    mkdir -p gradle/wrapper
    curl -o gradle/wrapper/gradle-wrapper.jar https://repo.maven.apache.org/maven2/org/gradle/gradle-wrapper/7.6.1/gradle-wrapper-7.6.1.jar
fi

# Make gradlew executable
chmod +x gradlew

# Build the APK
./gradlew assembleDebug

if [ $? -eq 0 ]; then
    echo
    echo "Build successful!"
    echo
    echo "APK location: android_app/app/build/outputs/apk/debug/app-debug.apk"
    echo
    echo "Install instructions:"
    echo "1. Transfer the APK to your Android device"
    echo "2. On your device, enable 'Install from Unknown Sources' in settings"
    echo "3. Open the APK file on your device to install"
else
    echo
    echo "Build failed. Please check the error messages above."
fi 