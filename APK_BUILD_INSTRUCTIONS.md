# Building the APK for Structural Analysis App

This guide provides step-by-step instructions to build the Android APK from the provided source files.

## Prerequisites

- **Java Development Kit (JDK)** version 11 or higher
  - Download from: [AdoptOpenJDK](https://adoptopenjdk.net/) or [Oracle JDK](https://www.oracle.com/java/technologies/javase-downloads.html)
  - Set JAVA_HOME environment variable to point to your JDK installation

- **Android Studio** (if you want to use the GUI method)
  - Download from: [Android Studio](https://developer.android.com/studio)

## Option 1: Using the Provided Build Scripts (Recommended)

### For Windows Users

1. Open File Explorer and navigate to the root directory of the project
2. Double-click on `build_apk_windows.bat`
3. Wait for the build process to complete
4. If successful, the APK will be available at:
   ```
   android_app\app\build\outputs\apk\debug\app-debug.apk
   ```

### For Linux/macOS Users

1. Open Terminal
2. Navigate to the root directory of the project
3. Make the build script executable:
   ```
   chmod +x build_apk_linux.sh
   ```
4. Run the script:
   ```
   ./build_apk_linux.sh
   ```
5. If successful, the APK will be available at:
   ```
   android_app/app/build/outputs/apk/debug/app-debug.apk
   ```

## Option 2: Using Android Studio

1. Start Android Studio
2. Select "Open an Existing Project"
3. Navigate to and select the `android_app` folder
4. Wait for the project to sync and build
5. From the menu, select Build > Build Bundle(s) / APK(s) > Build APK(s)
6. When the build completes, click on the "locate" link in the popup notification
7. The APK will be in the `android_app/app/build/outputs/apk/debug/` directory

## Option 3: Using Command Line (Manual Method)

### For Windows:

1. Open Command Prompt
2. Navigate to the android_app directory:
   ```
   cd path\to\android_app
   ```
3. If the Gradle wrapper doesn't exist, create it:
   ```
   mkdir -p gradle\wrapper
   curl -o gradle\wrapper\gradle-wrapper.jar https://repo.maven.apache.org/maven2/org/gradle/gradle-wrapper/7.6.1/gradle-wrapper-7.6.1.jar
   ```
4. Build the APK:
   ```
   gradlew.bat assembleDebug
   ```
5. The APK will be located at:
   ```
   app\build\outputs\apk\debug\app-debug.apk
   ```

### For Linux/macOS:

1. Open Terminal
2. Navigate to the android_app directory:
   ```
   cd path/to/android_app
   ```
3. If the Gradle wrapper doesn't exist, create it:
   ```
   mkdir -p gradle/wrapper
   curl -o gradle/wrapper/gradle-wrapper.jar https://repo.maven.apache.org/maven2/org/gradle/gradle-wrapper/7.6.1/gradle-wrapper-7.6.1.jar
   ```
4. Make the gradlew script executable:
   ```
   chmod +x gradlew
   ```
5. Build the APK:
   ```
   ./gradlew assembleDebug
   ```
6. The APK will be located at:
   ```
   app/build/outputs/apk/debug/app-debug.apk
   ```

## Installing the APK on Your Device

1. Transfer the APK file to your Android device using:
   - USB cable
   - Email attachment
   - Cloud storage (Google Drive, Dropbox, etc.)
   
2. On your Android device:
   - Go to Settings > Security > Install Unknown Apps
   - Allow installations from the app you're using to open the APK
   
3. Navigate to the APK file on your device and tap on it to install

4. Open the installed "Structural Analysis" app

## Troubleshooting

### Common Issues:

1. **"JAVA_HOME is not set" error**
   - Set the JAVA_HOME environment variable to your JDK installation directory
   - Windows: `set JAVA_HOME=C:\Program Files\Java\jdk-11.0.12`
   - Linux/macOS: `export JAVA_HOME=/usr/lib/jvm/java-11-openjdk`

2. **Gradle build failures**
   - Make sure you have internet connectivity for downloading dependencies
   - Try adding `--stacktrace` to the gradlew command for more detailed error information
   - Example: `./gradlew assembleDebug --stacktrace`

3. **APK won't install on device**
   - Check if your device allows installation from unknown sources
   - Ensure your device has enough storage space
   - Verify the APK wasn't corrupted during transfer

4. **WebView not loading**
   - Before building, edit `android_app/app/src/main/java/com/example/structuralanalysisapp/MainActivity.java`
   - Replace the URL with your hosted Streamlit app URL
   - Example: `webView.loadUrl("https://my-structural-app.streamlit.app");`

## Next Steps

After successfully building and installing the APK, you need to:

1. Host your Streamlit app online (see deploy_instructions.md)
2. Update the WebView URL in MainActivity.java to point to your hosted app
3. Rebuild the APK with the updated URL 