@echo off
echo ==========================================
echo  AIEAT - AI Engine Setup
echo ==========================================
echo.
echo Step 1: Install Ollama (Local AI Engine)
echo Step 2: Download Typhoon 2.5 Model
echo.

:: Check if Ollama is already installed
where ollama >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo [OK] Ollama is already installed!
    goto :pull_model
)

:: Download Ollama
echo Downloading Ollama installer...
powershell -Command "Invoke-WebRequest -Uri 'https://ollama.com/download/OllamaSetup.exe' -OutFile '%TEMP%\OllamaSetup.exe'"

if not exist "%TEMP%\OllamaSetup.exe" (
    echo [ERROR] Download failed.
    echo Please install manually: https://ollama.com/download
    pause
    exit /b 1
)

echo Installing Ollama...
start /wait "" "%TEMP%\OllamaSetup.exe"

:: Refresh PATH so we can find ollama
set "PATH=%LOCALAPPDATA%\Programs\Ollama;%PATH%"

:: Verify installation
where ollama >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo.
    echo [!] Ollama installed but not found in PATH.
    echo     Please RESTART your computer, then run this script again.
    pause
    exit /b 1
)

:pull_model
echo.
echo Downloading Typhoon 2.5 model (this may take a few minutes)...
ollama pull typhoon2.5:4b

if %ERRORLEVEL% equ 0 (
    echo.
    echo ==========================================
    echo  [DONE] AI Engine is ready!
    echo  You can now use AIEAT for AI scoring
    echo  and Thai translation.
    echo ==========================================
) else (
    echo.
    echo [!] Model download failed.
    echo     Make sure Ollama is running, then try:
    echo     ollama pull typhoon2.5:4b
)

echo.
pause
