@echo off
setlocal

set APP_NAME=schach.breburda.at
set VENV_DIR=.venv
set ENV_FILE=.env

echo Installing %APP_NAME%...

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found.
    exit /b 1
)

echo Python found:
python --version

REM Create virtual environment
if not exist "%VENV_DIR%" (
    echo Creating virtual environment...
    python -m venv %VENV_DIR%
) else (
    echo Virtual environment already exists.
)

REM Upgrade pip
echo Updating pip...
%VENV_DIR%\Scripts\python.exe -m pip install --upgrade pip

REM Install requirements
if exist requirements.txt (
    echo Installing requirements...
    %VENV_DIR%\Scripts\pip.exe install -r requirements.txt
) else (
    echo Warning: requirements.txt not found.
)

REM Create .env
if not exist "%ENV_FILE%" (
    echo Creating .env...

    (
        echo SECRET_KEY=CHANGE_ME_TO_A_RANDOM_SECRET
    ) > %ENV_FILE%

) else (
    echo .env already exists.
)

echo.
echo Windows installation complete.
echo.
echo No system service created.
echo.

pause