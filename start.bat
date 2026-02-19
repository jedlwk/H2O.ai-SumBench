@echo off
:: H2O SumBench — one-command start (Windows)
:: Finds Python 3.10+, sets up .venv if needed, and launches the app.

cd /d "%~dp0"

:: ── Find Python 3.10+ ───────────────────────────────────────────────
set "PYTHON="

:: Try py launcher first (most reliable on Windows)
for %%V in (3.13 3.12 3.11 3.10) do (
    if not defined PYTHON (
        py -%%V --version >nul 2>&1 && set "PYTHON=py -%%V"
    )
)

:: Fallback: bare python
if not defined PYTHON (
    python --version >nul 2>&1 && (
        for /f "tokens=2 delims= " %%A in ('python --version 2^>^&1') do (
            for /f "tokens=1,2 delims=." %%X in ("%%A") do (
                if %%X GEQ 3 if %%Y GEQ 10 set "PYTHON=python"
            )
        )
    )
)

if not defined PYTHON (
    echo ERROR: Python 3.10+ not found.
    echo   Install it from https://www.python.org/downloads/
    exit /b 1
)

for /f "delims=" %%V in ('%PYTHON% --version 2^>^&1') do echo Found %PYTHON% ^(%%V^)

:: ── Set up venv if needed ────────────────────────────────────────────
set "VENV_PY=.venv\Scripts\python.exe"

if not exist "%VENV_PY%" goto :setup

%VENV_PY% -c "import streamlit" >nul 2>&1
if errorlevel 1 goto :setup
goto :launch

:setup
echo.
echo Virtual environment missing or incomplete — running setup...
%PYTHON% setup.py
if errorlevel 1 exit /b 1

:: ── Launch ───────────────────────────────────────────────────────────
:launch
echo.
echo Starting H2O SumBench...
%VENV_PY% -m streamlit run ui/app.py
