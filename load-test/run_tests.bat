@echo off
chcp 65001 >nul
REM ══════════════════════════════════════════════════════════════
REM  اختبار حمل منصة Smart Real Estate Agent
REM  smartsapp.net — Windows Version
REM ══════════════════════════════════════════════════════════════

setlocal enabledelayedexpansion

set TARGET_URL=https://smartsapp.net
set RESULTS_DIR=results
set TIMESTAMP=%date:~-4%%date:~-7,2%%date:~-10,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set TIMESTAMP=%TIMESTAMP: =0%

echo ══════════════════════════════════════════════════════════════
echo   Load Test — Smart Real Estate Agent
echo   Target: %TARGET_URL%
echo ══════════════════════════════════════════════════════════════

if not exist "%RESULTS_DIR%" mkdir "%RESULTS_DIR%"

REM التحقق من المتطلبات
echo.
echo [1/5] Checking requirements...
python --version >nul 2>&1 || (
    echo ERROR: Python is not installed
    exit /b 1
)

python -c "import locust" 2>nul || (
    echo Installing dependencies...
    pip install locust faker requests
)

REM فحص الاتصال
echo.
echo [2/5] Checking server connection...
curl -s -o nul -w "%%{http_code}" "%TARGET_URL%/api/health" > temp_code.txt 2>nul
set /p HTTP_CODE=<temp_code.txt
del temp_code.txt
echo Server responded: HTTP %HTTP_CODE%

REM المرحلة 1: إحماء
echo.
echo [3/5] Phase 1: Warmup (50 users — 60s)
locust -f locustfile_realestate.py --headless ^
    --host %TARGET_URL% ^
    --users 50 --spawn-rate 5 --run-time 60s ^
    --csv %RESULTS_DIR%\%TIMESTAMP%_phase1_warmup ^
    --csv-full-history ^
    --html %RESULTS_DIR%\%TIMESTAMP%_phase1_report.html ^
    --only-summary

echo Phase 1 completed

REM المرحلة 2: حمل متوسط
echo.
echo [4/5] Phase 2: Medium Load (200 users — 180s)
locust -f locustfile_realestate.py --headless ^
    --host %TARGET_URL% ^
    --users 200 --spawn-rate 20 --run-time 180s ^
    --csv %RESULTS_DIR%\%TIMESTAMP%_phase2_medium ^
    --csv-full-history ^
    --html %RESULTS_DIR%\%TIMESTAMP%_phase2_report.html ^
    --only-summary

echo Phase 2 completed

REM المرحلة 3: حمل عالي
echo.
echo [5/5] Phase 3: Heavy Load (500 users — 180s)
locust -f locustfile_realestate.py --headless ^
    --host %TARGET_URL% ^
    --users 500 --spawn-rate 50 --run-time 180s ^
    --csv %RESULTS_DIR%\%TIMESTAMP%_phase3_heavy ^
    --csv-full-history ^
    --html %RESULTS_DIR%\%TIMESTAMP%_phase3_report.html ^
    --only-summary

echo Phase 3 completed

echo.
echo ══════════════════════════════════════════════════════════════
echo   Load test completed!
echo   Results in: %RESULTS_DIR%\
echo.
echo   To run with Web UI:
echo   locust -f locustfile_realestate.py --host %TARGET_URL%
echo   Then open: http://localhost:8089
echo ══════════════════════════════════════════════════════════════

pause
