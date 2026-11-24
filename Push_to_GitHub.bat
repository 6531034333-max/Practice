@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
title PharmaCU Practice -- Push to GitHub
cd /d "%~dp0"

echo ================================================================
echo   [PharmaCU Practice] Auto Deploy to GitHub (Practice Repo)
echo   Target Repo : https://github.com/6531034333-max/Practice.git
echo   User Email  : 6531034333@student.chula.ac.th
echo ================================================================
echo.

REM --- Check Git initialization ---
if not exist ".git" (
    echo [1/4] กำลังเริ่มต้น Git Repository...
    git init
    git branch -M main
    git remote add origin https://github.com/6531034333-max/Practice.git
) else (
    echo [1/4] ตรวจพบ Git Repository แล้ว
    git remote set-url origin https://github.com/6531034333-max/Practice.git
)

REM --- Set local git identity for this repo ---
git config user.name "6531034333-max"
git config user.email "6531034333@student.chula.ac.th"

REM --- Add files ---
echo.
echo [2/4] กำลังจัดเตรียมไฟล์สำหรับการ Commit...
git add -A

REM --- Check status ---
git status -s > tmp_status.txt 2>nul
set size=0
for %%A in (tmp_status.txt) do set size=%%~zA
del tmp_status.txt 2>nul

if "%size%"=="0" (
    echo [INFO] ไม่มีไฟล์ใหม่ที่เปลี่ยนแปลง กำลังตรวจสอบ Commit ที่ยังไม่ได้ Push...
    git push -u origin main
    goto FINISH
)

echo.
echo [3/4] กำลังสร้าง Commit...
set MYDATE=%date:~0,10%
set MYTIME=%time:~0,5%
git commit -m "Update PharmaCU Practice Hub: %MYDATE% %MYTIME%"

echo.
echo [4/4] กำลัง Push ขึ้น GitHub (main branch)...
git push -u origin main
if errorlevel 1 (
    echo.
    echo ================================================================
    echo  [WARNING] การ Push ขึ้น GitHub มีข้อขัดข้อง
    echo  หากระบบถาม Password ให้ใช้ GitHub Personal Access Token (PAT)
    echo  หรือตรวจสอบสิทธิ์การเข้าถึงคลังโค้ด 6531034333-max/Practice
    echo ================================================================
    echo.
    pause
    exit /b 1
)

:FINISH
echo.
echo ================================================================
echo  🎉 สำเร็จ! อัปเดตไฟล์ขึ้น GitHub เรียบร้อยแล้ว
echo  เว็บของคุณจะเปิดใช้งานได้ที่:
echo  https://6531034333-max.github.io/Practice/
echo ================================================================
echo.
pause
