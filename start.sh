#!/usr/bin/env bash
# H2O SumBench — one-command start (macOS / Linux)
# Finds Python 3.10+, sets up .venv if needed, and launches the app.
set -euo pipefail

cd "$(dirname "$0")"

# ── Find Python 3.10+ ───────────────────────────────────────────────
PYTHON=""
for ver in python3.13 python3.12 python3.11 python3.10 python3; do
    if command -v "$ver" &>/dev/null; then
        minor=$("$ver" -c "import sys; print(sys.version_info.minor)" 2>/dev/null || echo 0)
        major=$("$ver" -c "import sys; print(sys.version_info.major)" 2>/dev/null || echo 0)
        if [ "$major" -ge 3 ] && [ "$minor" -ge 10 ]; then
            PYTHON="$ver"
            break
        fi
    fi
done

if [ -z "$PYTHON" ]; then
    echo "ERROR: Python 3.10+ not found."
    echo "  Install it from https://www.python.org/downloads/"
    exit 1
fi

echo "Found $PYTHON ($($PYTHON --version 2>&1))"

# ── Set up venv if needed ────────────────────────────────────────────
VENV_PY=".venv/bin/python"

if [ ! -f "$VENV_PY" ] || ! "$VENV_PY" -c "import streamlit" 2>/dev/null; then
    echo ""
    echo "Virtual environment missing or incomplete — running setup..."
    "$PYTHON" setup.py
fi

# ── Launch ───────────────────────────────────────────────────────────
echo ""
echo "Starting H2O SumBench..."
"$VENV_PY" -m streamlit run ui/app.py
