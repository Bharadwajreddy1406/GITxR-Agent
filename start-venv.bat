@echo off
REM Change directory to the script location (root of the project)
cd /d "%~dp0"
echo Current directory: %CD%
REM Activate the virtual environment located in the virtual environment folder
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
    echo Virtual environment activated successfully
) else if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    echo Virtual environment activated successfully
) else (
    echo Error: Virtual environment not found in either .venv\Scripts\activate.bat or venv\Scripts\activate.bat
    echo Please make sure a virtual environment is created in either .venv or venv directory
    pause
)