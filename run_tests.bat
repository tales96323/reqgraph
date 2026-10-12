@echo off
chcp 65001 >nul 2>&1
echo.
echo ============================================================
echo   REQGRAPH - Suite de Testes com Projetos Reais do GitHub
echo ============================================================
echo.

cd /d "%~dp0"

if "%1"=="" (
    python run_tests.py
) else (
    python run_tests.py %*
)

echo.
pause
