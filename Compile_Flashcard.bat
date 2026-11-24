@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ================================================================
echo   [PharmaCU Practice] Flashcard Database Compiler
echo   Target Sheet : 1yY5Gnjv0vvtj0036V0bB5wa6kfalPHVFcjFZg1uDXEY
echo   Output       : flashcard-data-offline.js
echo ================================================================
echo.

python compile_flashcard.py %*
if errorlevel 1 (
    echo.
    echo [ERROR] Flashcard Compilation failed!
    echo Please make sure your Google Sheet is shared with:
    echo   senior-projects@gemini-sheets-editor-497118.iam.gserviceaccount.com
    echo or set to 'Anyone with the link can view'.
    echo.
    pause
    exit /b 1
)

echo.
echo [SUCCESS] Flashcard database compiled successfully!
echo.
pause
