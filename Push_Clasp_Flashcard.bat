@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ================================================================
echo   [PharmaCU Practice] Push Code.gs to Flashcard Google Apps Script
echo   Script ID: 1QG2VNof-D8dv9gPSbVvGcZnY9RbEfPsRoewROAo3nFkhP8RehTf3Yfe0
echo ================================================================
echo.

if exist "google_apps_script\flashcard\.clasp.json" (
    pushd "google_apps_script\flashcard"
    call clasp push --force
    if errorlevel 1 (
        echo [ERROR] Clasp push failed.
    ) else (
        echo [SUCCESS] Flashcard Code.gs uploaded to Apps Script!
    )
    popd
) else (
    echo [ERROR] File google_apps_script\flashcard\.clasp.json not found!
)
echo.
pause
