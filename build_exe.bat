@echo off
echo Building Structural Analysis Application Executable...

echo Building the executable using PyInstaller
pyinstaller --clean frames_app.spec

echo Creating data directories if they don't exist
if not exist "dist\Structural Analysis App\data" mkdir "dist\Structural Analysis App\data"
if not exist "dist\Structural Analysis App\.streamlit" mkdir "dist\Structural Analysis App\.streamlit"

echo Copying additional required files
if exist "data" xcopy /E /I /Y "data" "dist\Structural Analysis App\data"
if exist ".streamlit" xcopy /E /I /Y ".streamlit" "dist\Structural Analysis App\.streamlit"

echo Build completed! You can find the executable in the 'dist\Structural Analysis App' folder.
echo Run 'Structural Analysis App.exe' to start the application.
pause 