@echo off
cd /d "%~dp0"

REM --- find python launcher: py -> python -> python3 ---
set "PY="
py --version >nul 2>&1 && set "PY=py"
if not defined PY (python --version >nul 2>&1 && set "PY=python")
if not defined PY (python3 --version >nul 2>&1 && set "PY=python3")
if not defined PY goto nopy

echo using %PY% > run_task2.log
%PY% --version >> run_task2.log 2>&1

echo.
echo Task 2 crossover measurement started. Do NOT close this window.
echo (Brute force is quadratic, so later sizes take longer.)
echo.

echo [1/3] sizes 250,500,1000,2000 ...
echo [1/3] sizes 250,500,1000,2000 >> run_task2.log
%PY% task2_crossover.py --sizes 250,500,1000,2000 >> run_task2.log 2>&1

echo [2/3] size 4000 ...
echo [2/3] size 4000 >> run_task2.log
%PY% task2_crossover.py --sizes 4000 >> run_task2.log 2>&1

echo    ^>^> 5 sizes done (minimum met). Size 8000 is the slowest.
echo    ^>^> If it takes too long you may close this window now.
echo [3/3] size 8000 ...
echo [3/3] size 8000 >> run_task2.log
%PY% task2_crossover.py --sizes 8000 >> run_task2.log 2>&1

echo DONE_ALL >> run_task2.log
echo.
echo =====================================
echo  DONE. You can close this window.
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
