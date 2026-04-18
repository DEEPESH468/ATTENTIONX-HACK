#!/usr/bin/env bash
set -e
PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
source "$PROJECT_ROOT/.venv/bin/activate"
streamlit run "$PROJECT_ROOT/app.py"
