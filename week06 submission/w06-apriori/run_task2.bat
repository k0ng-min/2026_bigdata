@echo off
cd /d "%~dp0"

set "PY="
py --version >nul 2>&1 && set "PY=py"
if not defined PY (python --version >nul 2>&1 && set "PY=python")
if not defined PY (python3 --version >nul 2>&1 && set "PY=python3")
if not defined PY goto nopy

echo using %PY% > run_task2.log
%PY% --version >> run_task2.log 2>&1

echo.
echo Task 2 explosion measurement.
echo.

echo [1/2] supports 400,200,100,50,25  (required set) ...
echo [1/2] supports 400,200,100,50,25 >> run_task2.log
%PY% task2_explosion.py --supports 400,200,100,50,25 >> run_task2.log 2>&1

echo    ^>^> 5 supports done (minimum met). Next lowers to 12,6 (heavier).
echo [2/2] supports 12,6 ...
echo [2/2] supports 12,6 >> run_task2.log
%PY% task2_explosion.py --supports 12,6 >> run_task2.log 2>&1

echo DONE_ALL >> run_task2.log
echo.
echo =====================================
echo  Done. Tell Claude: done
echo =====================================
echo.
pause
exit /b 0

:nopy
echo Python not found > run_task2.log
echo Python not found. Please screenshot this and tell Claude.
pause
exit /b 1
