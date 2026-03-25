@echo off
setlocal EnableDelayedExpansion

title Cloudflare Tunnel Installer - Mini App

echo.
echo ================================================
echo    Cloudflare Tunnel Installer for Windows
echo    Mini App Server Setup
echo ================================================
echo.

REM STEP 1: Check Administrator Privileges
echo.
echo [STEP 1] Checking Administrator Privileges...

net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] This script must run as Administrator!
    echo.
    echo Please right-click the file and select "Run as administrator"
    echo.
    pause
    exit /b 1
)
echo [OK] Administrator privileges confirmed!

REM STEP 2: Download and Install Cloudflared
echo.
echo [STEP 2] Downloading Cloudflared...

set "CLOUDFLARED_PATH=C:\cloudflared"
set "CLOUDFLARED_EXE=%CLOUDFLARED_PATH%\cloudflared.exe"

if exist "%CLOUDFLARED_EXE%" (
    echo [INFO] Cloudflared already installed
    "%CLOUDFLARED_EXE%" --version
    echo.
    set /p REINSTALL="Reinstall? (y/n): "
    if /i not "!REINSTALL!"=="y" goto :skip_download
)

if not exist "%CLOUDFLARED_PATH%" mkdir "%CLOUDFLARED_PATH%"

REM Detect system architecture
if "%PROCESSOR_ARCHITECTURE%"=="AMD64" (
    set "DOWNLOAD_URL=https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
    echo [INFO] System: 64-bit detected
) else (
    set "DOWNLOAD_URL=https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-386.exe"
    echo [INFO] System: 32-bit detected
)

echo [INFO] Downloading from:
echo         %DOWNLOAD_URL%
echo.

REM Download using PowerShell
powershell -Command "try { Invoke-WebRequest -Uri '%DOWNLOAD_URL%' -OutFile '%CLOUDFLARED_EXE%' -ErrorAction Stop; Write-Host 'Download successful' } catch { Write-Host 'Download failed'; exit 1 }"

if not exist "%CLOUDFLARED_EXE%" (
    echo [ERROR] Download failed!
    echo Try manual download from:
    echo https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/
    pause
    exit /b 1
)
echo [OK] Download successful!

:skip_download

REM Add to PATH
echo.
echo [INFO] Adding Cloudflared to system PATH...
setx PATH "%PATH%;%CLOUDFLARED_PATH%" /M > nul 2>&1
set "PATH=%PATH%;%CLOUDFLARED_PATH%"
echo [OK] PATH updated!

REM Verify installation
echo.
echo [INFO] Verifying installation...
"%CLOUDFLARED_EXE%" --version
if %errorLevel% equ 0 (
    echo [OK] Installation verified successfully!
) else (
    echo [ERROR] Verification failed!
    pause
    exit /b 1
)

REM STEP 3: Setup Configuration Directory
echo.
echo [STEP 3] Setting up Configuration Directory...

set "CONFIG_PATH=%USERPROFILE%\.cloudflared"
if not exist "%CONFIG_PATH%" mkdir "%CONFIG_PATH%"
echo [OK] Config directory: %CONFIG_PATH%

REM STEP 4: Choose Tunnel Type
echo.
echo [STEP 4] Choose Tunnel Setup Method
echo.
echo   1) Quick Tunnel - Temporary URL (changes every time)
echo   2) Named Tunnel - Permanent URL with custom domain
echo.
set /p TUNNEL_TYPE="Enter choice (1 or 2): "

if "%TUNNEL_TYPE%"=="1" goto :quick_tunnel
if "%TUNNEL_TYPE%"=="2" goto :named_tunnel
goto :quick_tunnel

REM OPTION 1: Quick Tunnel
:quick_tunnel
echo.
echo [QUICK TUNNEL MODE]
echo.

set /p PORT="Enter port number (default: 5000): "
if "%PORT%"=="" set PORT=5000

echo.
echo [INFO] Make sure Mini App is running on port %PORT%
echo [INFO] Starting tunnel... Press Ctrl+C to stop
echo.

"%CLOUDFLARED_EXE%" tunnel --url http://localhost:%PORT%
goto :end

REM OPTION 2: Named Tunnel
:named_tunnel
echo.
echo [NAMED TUNNEL MODE]
echo.

REM Step 1: Login
echo [STEP 4.1] Cloudflare Login
echo [INFO] Browser will open - sign in and select your domain
echo.
pause

"%CLOUDFLARED_EXE%" tunnel login
if %errorLevel% neq 0 (
    echo [ERROR] Login failed!
    pause
    exit /b 1
)
echo [OK] Login successful!

REM Step 2: Create tunnel
echo.
echo [STEP 4.2] Create Tunnel
set /p TUNNEL_NAME="Enter tunnel name (example: miniapp-bot): "
if "%TUNNEL_NAME%"=="" set TUNNEL_NAME=miniapp-bot

"%CLOUDFLARED_EXE%" tunnel create %TUNNEL_NAME%
if %errorLevel% neq 0 (
    echo [ERROR] Failed to create tunnel!
    pause
    exit /b 1
)
echo [OK] Tunnel created: %TUNNEL_NAME%

REM Step 3: Setup domain
echo.
echo [STEP 4.3] Configure Domain
set /p DOMAIN="Enter full subdomain (example: miniapp.yourdomain.com): "
set /p PORT="Enter port number (default: 5000): "
if "%PORT%"=="" set PORT=5000

REM Get tunnel ID
for /f "tokens=1" %%a in ('"%CLOUDFLARED_EXE%" tunnel list 2^>nul ^| findstr %TUNNEL_NAME%') do set TUNNEL_ID=%%a

if "%TUNNEL_ID%"=="" (
    echo [WARNING] Could not find tunnel ID
    set TUNNEL_ID=unknown
)
echo [INFO] Tunnel ID: %TUNNEL_ID%

REM Step 4: Create config file
echo.
echo [STEP 4.4] Creating Configuration File
echo.

(
echo # Cloudflare Tunnel Configuration
echo # Mini App Server
echo.
echo tunnel: %TUNNEL_ID%
echo credentials-file: %CONFIG_PATH%\%TUNNEL_ID%.json
echo.
echo ingress:
echo   - hostname: %DOMAIN%
echo     service: http://localhost:%PORT%
echo   - service: http_status:404
) > "%CONFIG_PATH%\config.yml"

if exist "%CONFIG_PATH%\config.yml" (
    echo [OK] Config file created: %CONFIG_PATH%\config.yml
) else (
    echo [ERROR] Failed to create config file!
    pause
    exit /b 1
)

REM Step 5: Bind domain
echo.
echo [STEP 4.5] Binding Domain to DNS
"%CLOUDFLARED_EXE%" tunnel route dns %TUNNEL_NAME% %DOMAIN%
if %errorLevel% equ 0 (
    echo [OK] Domain bound: %DOMAIN%
) else (
    echo [WARNING] DNS binding may need manual setup
)

REM Step 6: Create startup script
echo.
echo [STEP 4.6] Creating Startup Script
echo.

(
echo @echo off
echo title Cloudflare Tunnel - %TUNNEL_NAME%
echo echo Starting tunnel...
echo echo URL: https://%DOMAIN%
echo echo.
echo "%CLOUDFLARED_EXE%" tunnel run %TUNNEL_NAME%
echo pause
) > "%CLOUDFLARED_PATH%\start_tunnel.bat"

if exist "%CLOUDFLARED_PATH%\start_tunnel.bat" (
    echo [OK] Startup script created: %CLOUDFLARED_PATH%\start_tunnel.bat
) else (
    echo [WARNING] Could not create startup script
)

REM Optional: Install as service
echo.
set /p INSTALL_SERVICE="Install as Windows service? (y/n): "

if /i "%INSTALL_SERVICE%"=="y" (
    echo [INFO] Installing service...
    "%CLOUDFLARED_EXE%" service install
    if %errorLevel% equ 0 (
        echo [OK] Service installed!
        
        net start cloudflared
        if %errorLevel% equ 0 (
            echo [OK] Service started!
        ) else (
            echo [WARNING] Service installed but failed to start
        )
    ) else (
        echo [WARNING] Service installation failed
    )
)

REM Summary
:end
echo.
echo ================================================
echo    SETUP COMPLETED SUCCESSFULLY!
echo ================================================
echo.
if "%TUNNEL_NAME%"=="" (
    echo Configuration Summary:
    echo   Mode: Quick Tunnel
    echo   Port: %PORT%
    echo   Type: Temporary (changes each time)
) else (
    echo Configuration Summary:
    echo   Tunnel Name: %TUNNEL_NAME%
    echo   Tunnel ID: %TUNNEL_ID%
    echo   Domain: https://%DOMAIN%
    echo   Port: %PORT%
)
echo.
echo Running Methods:
if not "%TUNNEL_NAME%"=="" (
    echo   1. Script:  %CLOUDFLARED_PATH%\start_tunnel.bat
    echo   2. Command: cloudflared tunnel run %TUNNEL_NAME%
) else (
    echo   1. Use Quick Tunnel mode (shown above)
    echo   2. Command: cloudflared tunnel --url http://localhost:%PORT%
)
echo.
echo Next Steps:
echo   1. Start Mini App: python mini_app/app.py
if not "%DOMAIN%"=="" (
    echo   2. Add URL in BotFather: https://%DOMAIN%
)
echo.
echo [OK] Script completed!
echo.
pause
