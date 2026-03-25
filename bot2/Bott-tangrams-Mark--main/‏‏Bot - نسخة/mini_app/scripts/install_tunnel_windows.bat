@echo off
chcp 65001 > nul
setlocal EnableDelayedExpansion

:: ======================================================================
:: Cloudflare Tunnel Installation Script - Windows
:: Mini App - Telegram Bot
:: ======================================================================

title Cloudflare Tunnel Installer - Mini App

echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║   ^|   Cloudflare Tunnel Installer for Windows        ║
echo ║   Mini App Server Setup                              ║
echo ╚════════════════════════════════════════════════════════╝
echo.

:: ======================================================================
:: STEP 1: Check Administrator Privileges
:: ======================================================================
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo [*] STEP 1: Checking Administrator Privileges
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] This script must run as Administrator
    echo.
    echo         Right-click the file and select "Run as administrator"
    echo.
    pause
    exit /b 1
)
echo [OK] Administrator privileges confirmed

:: ======================================================================
:: STEP 2: Download and Install Cloudflared
:: ======================================================================
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo [*] STEP 2: Downloading Cloudflared
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

set "CLOUDFLARED_PATH=C:\cloudflared"
set "CLOUDFLARED_EXE=%CLOUDFLARED_PATH%\cloudflared.exe"

if exist "%CLOUDFLARED_EXE%" (
    echo [INFO] Cloudflared already installed
    "%CLOUDFLARED_EXE%" --version
    echo.
    set /p REINSTALL="Reinstall? (y/n): "
    if /i not "!REINSTALL!"=="y" goto :skip_download
)

:: Create folder
if not exist "%CLOUDFLARED_PATH%" mkdir "%CLOUDFLARED_PATH%"

:: Detect system architecture
if "%PROCESSOR_ARCHITECTURE%"=="AMD64" (
    set "DOWNLOAD_URL=https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
    echo [INFO] System: 64-bit
) else (
    set "DOWNLOAD_URL=https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-386.exe"
    echo [INFO] System: 32-bit
)

:: Download file
echo [INFO] Downloading...
echo     %DOWNLOAD_URL%
echo.

:: Use PowerShell to download
powershell -Command "& {Invoke-WebRequest -Uri '%DOWNLOAD_URL%' -OutFile '%CLOUDFLARED_EXE%'}"

if exist "%CLOUDFLARED_EXE%" (
    echo [OK] Download successful
) else (
    echo [ERROR] Download failed!
    echo     Try manual download from:
    echo     https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/
    pause
    exit /b 1
)

:skip_download

:: Add to PATH
echo.
echo [INFO] Adding Cloudflared to PATH...
setx PATH "%PATH%;%CLOUDFLARED_PATH%" /M > nul 2>&1
set "PATH=%PATH%;%CLOUDFLARED_PATH%"
echo [OK] PATH updated

:: Verify installation
echo.
"%CLOUDFLARED_EXE%" --version
echo [OK] Installation verified

:: ======================================================================
:: STEP 3: Setup Configuration Directory
:: ======================================================================
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo [*] STEP 3: Setting up Configuration Directory
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

set "CONFIG_PATH=%USERPROFILE%\.cloudflared"
if not exist "%CONFIG_PATH%" mkdir "%CONFIG_PATH%"
echo [OK] Config directory: %CONFIG_PATH%

:: ======================================================================
:: STEP 4: Choose Tunnel Type
:: ======================================================================
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo [*] STEP 4: Choose Tunnel Type
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo Choose tunnel setup method:
echo.
echo   1) Quick Tunnel - Temporary URL (changes every time)
echo   2) Named Tunnel - Permanent URL with custom domain
echo.
set /p TUNNEL_TYPE="Enter choice (1 or 2): "

if "%TUNNEL_TYPE%"=="1" goto :quick_tunnel
if "%TUNNEL_TYPE%"=="2" goto :named_tunnel
goto :quick_tunnel

:: ======================================================================
:: OPTION 1: Quick Tunnel
:: ======================================================================
:quick_tunnel
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo [*] Quick Tunnel Setup
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

set /p PORT="Enter port number (default: 5000): "
if "%PORT%"=="" set PORT=5000

echo.
echo [INFO] Make sure Mini App is running on port %PORT%
echo [INFO] Creating tunnel...
echo.
echo ═══════════════════════════════════════════════════════
echo   Press Ctrl+C to stop the tunnel
echo ═══════════════════════════════════════════════════════
echo.

"%CLOUDFLARED_EXE%" tunnel --url http://localhost:%PORT%
goto :end

:: ======================================================================
:: OPTION 2: Named Tunnel (Permanent)
:: ======================================================================
:named_tunnel
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo [*] Permanent Named Tunnel Setup
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

:: Step 1: Login
echo.
echo [STEP 4.1] Login to Cloudflare Account
echo [INFO] Browser will open - sign in and select your domain
echo.
pause

"%CLOUDFLARED_EXE%" tunnel login
echo [OK] Login successful

:: Step 2: Create tunnel
echo.
echo [STEP 4.2] Create Tunnel
set /p TUNNEL_NAME="Enter tunnel name (example: miniapp-bot): "
if "%TUNNEL_NAME%"=="" set TUNNEL_NAME=miniapp-bot

"%CLOUDFLARED_EXE%" tunnel create %TUNNEL_NAME%
echo [OK] Tunnel created: %TUNNEL_NAME%

:: Step 3: Setup domain
echo.
echo [STEP 4.3] Configure Domain
set /p DOMAIN="Enter full subdomain (example: miniapp.yourdomain.com): "
set /p PORT="Enter port number (default: 5000): "
if "%PORT%"=="" set PORT=5000

:: Get tunnel ID
for /f "tokens=1" %%a in ('"%CLOUDFLARED_EXE%" tunnel list ^| findstr %TUNNEL_NAME%') do set TUNNEL_ID=%%a
echo [INFO] Tunnel ID: %TUNNEL_ID%

:: Step 4: Create config file
echo.
echo [STEP 4.4] Creating Configuration File

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

echo [OK] Config file created: %CONFIG_PATH%\config.yml

:: Step 5: Bind domain
echo.
echo [STEP 4.5] Binding Domain to DNS
"%CLOUDFLARED_EXE%" tunnel route dns %TUNNEL_NAME% %DOMAIN%
echo [OK] Domain bound: %DOMAIN%

:: Step 6: Create startup script
echo.
echo [STEP 4.6] Creating Startup Script

(
echo @echo off
echo title Cloudflare Tunnel - %TUNNEL_NAME%
echo echo Starting tunnel...
echo echo URL: https://%DOMAIN%
echo echo.
echo "%CLOUDFLARED_EXE%" tunnel run %TUNNEL_NAME%
echo pause
) > "%CLOUDFLARED_PATH%\start_tunnel.bat"

echo [OK] Startup script created: %CLOUDFLARED_PATH%\start_tunnel.bat

:: Optional: Install as Windows service
echo.
set /p INSTALL_SERVICE="Install as Windows service? (runs automatically) (y/n): "

if /i "%INSTALL_SERVICE%"=="y" (
    echo [INFO] Installing service...
    "%CLOUDFLARED_EXE%" service install
    echo [OK] Service installed
    
    net start cloudflared
    echo [OK] Service started
)

:: ======================================================================
:: Summary and Next Steps
:: ======================================================================
echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║             SETUP COMPLETED SUCCESSFULLY!             ║
echo ╚════════════════════════════════════════════════════════╝
echo.
echo [*] Configuration Summary:
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo   Tunnel Name:     %TUNNEL_NAME%
echo   Tunnel ID:       %TUNNEL_ID%
echo   URL:             https://%DOMAIN%
echo   Local Port:      %PORT%
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo [*] Running Methods:
echo   1. Script:  %CLOUDFLARED_PATH%\start_tunnel.bat
echo   2. Command: cloudflared tunnel run %TUNNEL_NAME%
if /i "%INSTALL_SERVICE%"=="y" (
echo   3. Service: net start cloudflared
)
echo.
echo [*] Next Steps:
echo   1. Start Mini App: python mini_app/app.py
echo   2. Add URL in BotFather: https://%DOMAIN%
echo.

:end
echo [OK] Script completed successfully!
echo.
pause
