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
echo Task 2 curse-of-dimensionality measurement. This is fast.
echo.

echo [1/3] dims 2,5,10,20,50,100,200  (required set) ...
echo [1/3] dims 2,5,10,20,50,100,200 >> run_task2.log
%PY% task2_curse.py --dims 2,5,10,20,50,100,200 >> run_task2.log 2>&1

echo [2/3] dim 20, points 4000  (vary n) ...
echo [2/3] dim 20 points 4000 >> run_task2.log
%PY% task2_curse.py --dims 20 --points 4000 >> run_task2.log 2>&1

echo [3/3] dim 20, points 250  (vary n) ...
echo [3/3] dim 20 points 250 >> run_task2.log
%PY% task2_curse.py --dims 20 --points 250 >> run_task2.log 2>&1

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
