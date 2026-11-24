@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ================================================================
echo   [PharmaCU Practice] Quiz Database Compiler
echo   Target Sheet : 1EEkYzLVM7yxVyXG1H3AZJgGw9v91tGFRH3bhtmnPVVY
echo   Output       : quiz-data-offline.js
echo ================================================================
echo.

python compile_quiz.py %*
if errorlevel 1 (
    echo.
    echo [ERROR] Quiz Compilation failed!
    echo Please make sure your Google Sheet is shared with:
    echo   senior-projects@gemini-sheets-editor-497118.iam.gserviceaccount.com
    echo or set to 'Anyone with the link can view'.
    echo.
    pause
    exit /b 1
)

echo.
echo [SUCCESS] Quiz database compiled successfully!
echo.
pause
