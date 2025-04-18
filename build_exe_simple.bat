@echo off
echo Building Structural Analysis Application Executable (Simple Method)...

echo Building with basic PyInstaller configuration
pyinstaller --onedir ^
  --add-data "app.py;." ^
  --add-data "pages;pages" ^
  --add-data "StructuralElements.py;." ^
  --add-data "Loads.py;." ^
  --add-data "FirstOrderResponse.py;." ^
  --add-data "SecondOrderResponse.py;." ^
  --add-data "FiniteElementDivisor.py;." ^
  --add-data "config.py;." ^
  --add-data "data;data" ^
  --hidden-import streamlit ^
  --hidden-import plotly ^
  --hidden-import numpy ^
  --hidden-import pandas ^
  --hidden-import matplotlib ^
  --hidden-import scipy ^
  --name "Structural Analysis App" ^
  run_app.py

echo Creating .streamlit directory if it doesn't exist
if not exist "dist\Structural Analysis App\.streamlit" mkdir "dist\Structural Analysis App\.streamlit"

echo Copying additional required files
if exist ".streamlit" xcopy /E /I /Y ".streamlit" "dist\Structural Analysis App\.streamlit"

echo Build completed! You can find the executable in the 'dist\Structural Analysis App' folder.
echo Run 'Structural Analysis App.exe' to start the application.
pause 