@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ================================================================
echo   [PharmaCU Practice] Push Code.gs to Quiz Google Apps Script
echo   Script ID: 1nJwbleNGtDtRVfxEL8s8QlmG5bkCOog13L-B_U98sCXYrbTXa0Xe72tA
echo ================================================================
echo.

if exist "google_apps_script\quiz\.clasp.json" (
    pushd "google_apps_script\quiz"
    call clasp push --force
    if errorlevel 1 (
        echo [ERROR] Clasp push failed.
    ) else (
        echo [SUCCESS] Quiz Code.gs uploaded to Apps Script!
    )
    popd
) else (
    echo [ERROR] File google_apps_script\quiz\.clasp.json not found!
)
echo.
pause
