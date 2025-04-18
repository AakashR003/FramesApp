@echo off
echo Cleaning up project...

REM Remove temporary files
del /S /Q *.pyc
del /S /Q *.pyo
del /S /Q *.pyd
del /S /Q __pycache__\*.*

REM Remove build artifacts
rmdir /S /Q build 2>nul
rmdir /S /Q dist 2>nul
rmdir /S /Q __pycache__ 2>nul
rmdir /S /Q .pytest_cache 2>nul

REM Clear data files (optional, uncomment if you want to remove saved structures)
REM rmdir /S /Q data 2>nul

echo Cleanup complete! 