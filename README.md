# Structural Analysis Application

A powerful Streamlit-based application for structural analysis of frame structures, similar to Sofistik.

## Features

- Create and visualize 3D structural models
- Input nodes with boundary conditions
- Input members with various cross-section types
- Apply different types of loads (nodal and member loads)
- Perform structural analysis
- View analysis results for members and nodes
- Interactive 3D visualization

## Requirements

- Python 3.8 or higher
- Dependencies listed in `requirements.txt`

## Installation

1. Clone this repository or download the source code
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Running the Application

Run the following command in the project directory:

```bash
streamlit run app.py
```

The application will start and open in your default web browser.

## Application Structure

The application is organized into the following sections:

1. **Introduction** - Overview of the application
2. **Model**
   - **Node Input** - Add and manage structural nodes
   - **Member Input** - Add and manage members connecting nodes
   - **Load Input** - Apply forces, moments, and displacements
3. **Analysis**
   - **Member Analysis** - View analysis results for members
   - **Node Analysis** - View analysis results for nodes

## Using the Application

1. Start by adding nodes in the "Node Input" page
2. Create members connecting these nodes in the "Member Input" page
3. Apply loads to your structure in the "Load Input" page
4. Perform analysis and view results in the "Analysis" section

## Data Persistence

All inputs (nodes, members, loads) are automatically saved to JSON files in the `data` directory. This allows you to close and reopen the application without losing your work.

## Converting to APK

To convert this application to an APK (Android application), you can use tools like:

1. **Streamlit-Appsmith-Builder** - For wrapping Streamlit apps as mobile applications
2. **Kivy** - For creating cross-platform applications with Python

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- This application uses Streamlit for the frontend
- Plotly is used for interactive 3D visualization
- Backend calculations are performed using custom Python code

# Converting the Structural Analysis App to an APK

This guide explains how to convert the Streamlit-based Structural Analysis application to an Android APK file.

## Option 1: Using Streamlit-in-WebView

### Prerequisites
- Android Studio installed
- Basic knowledge of Android development
- A hosted version of your Streamlit app (e.g., on Streamlit Cloud, Heroku, or any other hosting service)

### Steps

1. **Host your Streamlit application**
   - Deploy your Streamlit app to a hosting service like [Streamlit Cloud](https://streamlit.io/cloud)
   - Or use a service like Heroku, AWS, etc.
   - Make sure your app is accessible via a public URL

2. **Create an Android WebView Project**
   - Open Android Studio
   - Create a new project with an Empty Activity template
   - Replace the main activity XML layout with a WebView
   - In the MainActivity, load your hosted Streamlit app URL in the WebView

3. **Build the APK**
   - Configure the build.gradle file with appropriate settings
   - Build the project to generate a debug or release APK
   - Sign the release APK for distribution

## Option 2: Using Streamlit Native (Experimental)

For developing a more native-feeling mobile app with your Streamlit code:

1. Install the [Streamlit Native](https://github.com/whitphx/streamlit-webrtc) package (experimental)
2. Use the package to create a mobile-friendly interface
3. Package using React Native or similar frameworks

## Option 3: Using Appflow (Ionic)

[Ionic Appflow](https://ionic.io/appflow) can help convert web applications to mobile apps:

1. Package your Streamlit app as a Progressive Web App (PWA)
2. Use Ionic's Capacitor to wrap it as a native app
3. Build Android APK through Appflow

## Option 4: Using a Third-Party Service

Services like [BuildFire](https://buildfire.com/) or [AppMakr](https://www.appmakr.com/) provide platforms to convert web applications to mobile apps:

1. Create an account on the service
2. Input your deployed Streamlit app URL
3. Customize appearance and settings
4. Let the service build the APK for you

## Important Considerations

- **User Experience**: WebView-based apps may not provide the best mobile experience
- **Responsive Design**: Ensure your Streamlit app is mobile-responsive
- **Performance**: Complex calculations might be slower on mobile devices
- **Updates**: Consider how app updates will be handled

## Ready-made Example

For a quick option using Android Studio with a WebView:

```java
// MainActivity.java
package com.example.structuralanalysisapp;

import androidx.appcompat.app.AppCompatActivity;
import android.os.Bundle;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

public class MainActivity extends AppCompatActivity {
    private WebView webView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        webView = findViewById(R.id.webview);
        WebSettings webSettings = webView.getSettings();
        webSettings.setJavaScriptEnabled(true);
        webSettings.setDomStorageEnabled(true);
        webView.setWebViewClient(new WebViewClient());
        
        // Replace this URL with your hosted Streamlit app URL
        webView.loadUrl("https://your-streamlit-app-url.com");
    }
    
    @Override
    public void onBackPressed() {
        if (webView.canGoBack()) {
            webView.goBack();
        } else {
            super.onBackPressed();
        }
    }
}
```

```xml
<!-- activity_main.xml -->
<?xml version="1.0" encoding="utf-8"?>
<RelativeLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    tools:context=".MainActivity">

    <WebView
        android:id="@+id/webview"
        android:layout_width="match_parent"
        android:layout_height="match_parent" />

</RelativeLayout>
```

## Need Help?

Contact the development team for assistance in creating a customized APK that best meets your requirements. 