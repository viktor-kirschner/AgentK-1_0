@echo off
setlocal enabledelayedexpansion

echo.
echo ?? Checking for Python...

where python >nul 2>&1
if errorlevel 1 (
    echo ? Python not found. Downloading installer...
    powershell -Command "Invoke-WebRequest -Uri https://www.python.org/ftp/python/3.12.3/python-3.12.3-amd64.exe -OutFile python_installer.exe"
    echo ??? Installing Python silently...
    start /wait python_installer.exe /quiet InstallAllUsers=0 PrependPath=1
    del python_installer.exe
) else (
    echo ? Python is already installed.
)

echo.
echo ?? Installing required Python packages...
python -m pip install --upgrade pip
python -m pip install openai httpx colorama

echo.
echo ?? Extracting AgentK files...

set "ZIP=AgentK-1_0.zip"
set "TARGET=%LOCALAPPDATA%\AgentK"

powershell -Command "Expand-Archive -Path '%ZIP%' -DestinationPath '%TARGET%' -Force"

if not exist "%TARGET%\dropk.bat" (
    echo ? Installation failed: dropk.bat not found.
    exit /b 1
)

echo.
echo ?? Adding DropK to user PATH...

:: Read existing user PATH
for /f "tokens=2*" %%A in ('reg query "HKCU\Environment" /v PATH 2^>nul') do set "userpath=%%B"

echo Current PATH: !userpath!

:: Check if already in PATH
echo !userpath! | find /I "%TARGET%" >nul
if errorlevel 1 (
    setx PATH "!userpath!;%TARGET%"
    echo ? Added %TARGET% to PATH.
) else (
    echo ?? Already in PATH - skipping.
)

echo.
echo ? DropK is ready! Open a new terminal and type:
echo.
echo     dropk
echo.
echo to spawn a new AgentK instance.
echo.

endlocal
pause