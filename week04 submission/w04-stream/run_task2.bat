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
echo Task 2 memory-limit measurement. Do NOT close this window.
echo (The exact set grows with the data; Flajolet-Martin stays flat.)
echo.

echo [1/2] sizes 100000,400000,1600000,6400000  (required set - 4 sizes) ...
echo [1/2] sizes 100000,400000,1600000,6400000 >> run_task2.log
%PY% task2_limits.py --sizes 100000,400000,1600000,6400000 >> run_task2.log 2>&1

echo    ^>^> 4 sizes done (minimum met). Next tries 25,000,000 to find the wall.
echo    ^>^> That one is slow and memory-heavy - close this window now if you don't want it.
echo [2/2] size 25000000  (optional - the memory wall) ...
echo [2/2] size 25000000 >> run_task2.log
%PY% task2_limits.py --sizes 25000000 >> run_task2.log 2>&1

echo DONE_ALL >> run_task2.log
echo.
echo =====================================
echo  Done. You can close this window.
echo  Tell Claude: done
echo =====================================
echo.
pause
exit /b 0

:nopy
echo Python not found > run_task2.log
echo.
echo Python not found. Please screenshot this and tell Claude.
echo.
pause
exit /b 1
