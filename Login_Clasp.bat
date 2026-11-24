@echo off
cd /d "%~dp0"
echo ================================================================
echo   [PharmaCU Practice] Login to Google Apps Script (CLASP)
echo ================================================================
echo.
echo Please log in with: 6531034333@student.chula.ac.th
echo.
call npx @google/clasp login
echo.
pause
