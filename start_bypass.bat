@echo off
title Luna Music SSL hook launcher (foreground)
cd /d "%~dp0"

echo ============================================
echo   Luna Music SSL hook (foreground) launcher
echo ============================================
echo.

rem Check frida version
echo [1/3] Check frida version...
set FVER=
for /f "delims=" %%v in ('python -c "import frida;print(frida.__version__)" 2^>nul') do set FVER=%%v
echo         Current frida: %FVER%  (need 16.1.4)
if not "%FVER%"=="16.1.4" (
    echo [!] Version mismatch, switching frida to 16.1.4 ...
    pip install frida==16.1.4 --no-deps >nul 2>&1
)

rem Check hluda-server
echo [2/3] Check hluda-server...
adb devices >nul 2>&1
adb shell "su -c 'ps -A'" | findstr hluda >nul 2>&1
if errorlevel 1 (
    echo        hluda not running, starting...
    adb shell "su -c 'pkill hluda; sleep 1; nohup /data/local/tmp/hluda >/dev/null 2>&1 &'"
    timeout /t 3 >nul
) else (
    echo        hluda is running
)

rem Start hook (spawn) foreground
echo [3/3] Start hook (spawn)...
echo        Keep this window open. Ctrl-C to exit.
echo.
python "%~dp0start_bypass.py"

pause