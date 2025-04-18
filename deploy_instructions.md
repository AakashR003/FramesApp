# Deploying the Structural Analysis App (APK)

This guide provides detailed steps to deploy your Streamlit-based Structural Analysis application as an Android APK.

## Step 1: Deploy Your Streamlit App

First, you need to make your Streamlit app accessible from the internet.

### Option A: Deploy to Streamlit Cloud (Recommended)

1. Create an account at [Streamlit Cloud](https://streamlit.io/cloud)
2. Connect your GitHub repository to Streamlit Cloud
3. Follow the deployment instructions
4. Once deployed, you'll have a public URL (e.g., https://your-app-name.streamlit.app)

### Option B: Deploy to Heroku

1. Create a `Procfile` in your project root:
   ```
   web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
   ```
2. Create a `requirements.txt` file with all dependencies
3. Deploy to Heroku using their CLI or GitHub integration
4. Once deployed, you'll have a public URL (e.g., https://your-app-name.herokuapp.com)

## Step 2: Build the Android App

### Prerequisites

- [Android Studio](https://developer.android.com/studio) installed
- [JDK 11+](https://adoptopenjdk.net/) installed

### Steps

1. **Clone the Android project**
   - Extract the `android_app` folder from this project
   - Open it in Android Studio

2. **Update the WebView URL**
   - Open `app/src/main/java/com/example/structuralanalysisapp/MainActivity.java`
   - Find the line: `webView.loadUrl("https://your-streamlit-app-url.com");`
   - Replace with your actual Streamlit app URL (from Step 1)

3. **Build the APK**
   - From Android Studio's menu, select Build > Build Bundle(s) / APK(s) > Build APK(s)
   - Wait for the build to complete
   - The APK will be available in `app/build/outputs/apk/debug/app-debug.apk`

4. **For Release Version** (Optional)
   - In Android Studio, select Build > Generate Signed Bundle / APK
   - Follow the wizard to create a signing key
   - Build a signed APK with release configuration
   - The release APK will be available in `app/build/outputs/apk/release/app-release.apk`

## Step 3: Distribute the APK

### Test Distribution

1. Send the APK file directly to your device via email, cloud storage, or USB connection
2. On your Android device, open the APK file and install it (you may need to enable "Install from Unknown Sources")

### Google Play Store Distribution (Optional)

1. Create a [Google Play Developer account](https://play.google.com/console/signup) ($25 one-time fee)
2. Create a new app in the Google Play Console
3. Upload your signed APK
4. Complete the required metadata (app description, screenshots, etc.)
5. Submit for review

## Troubleshooting

**App shows white screen**
- Check if your Streamlit app is accessible from a mobile browser
- Ensure the URL in MainActivity.java is correct
- Add debugging code to see if there are WebView errors

**App doesn't connect to the internet**
- Check if the Internet permission is properly set in AndroidManifest.xml
- Ensure your device/emulator has internet connectivity

**APK doesn't install**
- Check the minimum Android version requirement (set to 21/Android 5.0 in build.gradle)
- If distributing manually, ensure "Install from Unknown Sources" is enabled

## Optimization Tips

1. Make your Streamlit UI mobile-friendly:
   - Use `st.set_page_config(layout="wide")` carefully on mobile
   - Test the UI on different screen sizes
   - Use responsive plots and elements

2. Reduce app size:
   - Enable minification in build.gradle (already set)
   - Remove unused resources
   - Consider using Android App Bundles for Play Store distribution 