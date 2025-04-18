# Building the Structural Analysis Application Executable

This document provides instructions for building and running the Structural Analysis Application as a standalone executable file.

## Prerequisites

- Windows operating system
- Python 3.9 or newer
- Administrator access (may be required for some installations)

## Building the Executable

1. **Run the build script**

   Simply run the `build_exe.bat` file by double-clicking it or running it from the command prompt.
   
   This script will:
   - Install required packages (including PyInstaller if not already installed)
   - Build the executable using the specification file
   - Copy necessary additional files

2. **Wait for the build to complete**

   The build process may take several minutes. When complete, you'll see a success message.
   
   The executable will be located in the `dist\Structural Analysis App` folder.

## Running the Application

There are two ways to run the application:

1. **Run directly from the build folder**

   Navigate to the `dist\Structural Analysis App` folder and run `Structural Analysis App.exe`

2. **Use the provided run script**

   Run the `run_packaged_app.bat` file by double-clicking it or running it from the command prompt.

## Troubleshooting

If you encounter any issues:

1. **Missing dependencies**

   Make sure all dependencies are installed:
   ```
   pip install -r requirements.txt
   pip install pyinstaller
   ```

2. **Antivirus interference**

   Some antivirus software may flag PyInstaller-created applications. You may need to add an exclusion.

3. **Windows Defender SmartScreen**

   Windows may display a warning when running the executable for the first time. Click "More info" and then "Run anyway".

4. **Data files not found**

   If the application can't find data files, make sure the `data` folder is correctly copied to the executable directory.

## Distribution

To distribute the application:

1. Copy the entire `dist\Structural Analysis App` folder
2. Share it with users who can run the application directly from the `Structural Analysis App.exe` file

Note that users don't need to have Python installed to run the executable. 