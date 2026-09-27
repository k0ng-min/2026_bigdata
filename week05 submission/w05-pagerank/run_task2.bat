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
echo Task 2 convergence measurement. This is fast (a few seconds).
echo.

echo [1/3] betas 0.5,0.7,0.85,0.95,0.99  (default graph, tol 1e-10) ...
echo [1/3] betas 0.5,0.7,0.85,0.95,0.99 >> run_task2.log
%PY% task2_convergence.py --betas 0.5,0.7,0.85,0.95,0.99 >> run_task2.log 2>&1

echo [2/3] bigger graph: nodes 6000, betas 0.85,0.95 ...
echo [2/3] nodes 6000 betas 0.85,0.95 >> run_task2.log
%PY% task2_convergence.py --nodes 6000 --betas 0.85,0.95 >> run_task2.log 2>&1

echo [3/3] looser tolerance: tol 1e-6, beta 0.85 ...
echo [3/3] tol 1e-6 beta 0.85 >> run_task2.log
%PY% task2_convergence.py --tol 1e-6 --betas 0.85 >> run_task2.log 2>&1

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
