@echo off
setlocal enabledelayedexpansion
title PharmaCU Practice -- Push to GitHub
cd /d "%~dp0"

echo ================================================================
echo   [PharmaCU Practice] Auto Deploy to GitHub
echo   Target Repo : https://github.com/6531034333-max/Practice.git
echo   User Email  : 6531034333@student.chula.ac.th
echo ================================================================
echo.

echo [1/3] Setting Git config...
git config user.name "6531034333-max"
git config user.email "6531034333@student.chula.ac.th"
git remote set-url origin https://github.com/6531034333-max/Practice.git

echo.
echo [2/3] Adding files and checking status...
git add -A

git status -s > tmp_status.txt 2>nul
set size=0
for %%A in (tmp_status.txt) do set size=%%~zA
del tmp_status.txt 2>nul

if not "%size%"=="0" (
    echo Creating commit...
    git commit -m "Update PharmaCU Practice Hub: %date% %time%"
) else (
    echo Working tree clean. Checking unpushed commits...
)

echo.
echo [3/3] Pushing to GitHub (origin main)...
git push -u origin main
if errorlevel 1 (
    echo.
    echo ================================================================
    echo  [ERROR] Git push failed!
    echo  If prompted for credentials, please sign in with GitHub
    echo  or use your GitHub Personal Access Token (PAT).
    echo ================================================================
    echo.
    pause
    exit /b 1
)

echo.
echo ================================================================
echo  SUCCESS! Pushed to GitHub successfully!
echo  Your website will be live at:
echo  https://6531034333-max.github.io/Practice/
echo ================================================================
echo.
pause
