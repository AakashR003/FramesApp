@echo off
echo Building Structural Analysis Application...

rem Create output directories if they don't exist
if not exist "dist" mkdir dist
if not exist "build" mkdir build

rem Run PyInstaller with a simpler configuration
pyinstaller ^
  --noconfirm ^
  --onedir ^
  --windowed ^
  --name "Structural Analysis App" ^
  --add-data "app.py;." ^
  --add-data "pages;pages" ^
  --add-data "StructuralElements.py;." ^
  --add-data "Loads.py;." ^
  --add-data "FirstOrderResponse.py;." ^
  --add-data "SecondOrderResponse.py;." ^
  --add-data "DynamicResponse.py;." ^
  --add-data "FiniteElementDivisor.py;." ^
  --add-data "Comparision.py;." ^
  --add-data "Functions.py;." ^
  --add-data "Model.py;." ^
  --add-data "config.py;." ^
  --add-data "Computer.py;." ^
  --add-data "data;data" ^
  --add-data ".streamlit;.streamlit" ^
  --hidden-import streamlit ^
  --hidden-import pydeck ^
  --hidden-import altair ^
  --hidden-import plotly ^
  --hidden-import numpy ^
  --hidden-import pandas ^
  --hidden-import matplotlib ^
  --hidden-import scipy ^
  --collect-all streamlit ^
  run_app_simple.py

echo.
echo Build completed!
echo.
echo You can find the executable at:
echo %CD%\dist\Structural Analysis App\Structural Analysis App.exe
echo.
pause 