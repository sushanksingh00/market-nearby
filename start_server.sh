#!/usr/bin/env bash
set -euo pipefail

echo "🚀 Starting Market Nearby Django Server..."

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "📍 Working directory: $(pwd)"

PORT="${1:-${PORT:-8000}}"
VENV_DIR=".venv"

pick_python() {
    if command -v python3.11 >/dev/null 2>&1; then
        echo "python3.11"
    else
        echo "python3"
    fi
}

if [[ ! -d "$VENV_DIR" ]]; then
    PYTHON_BIN="$(pick_python)"
    echo "🧰 Creating virtual environment ($VENV_DIR) using $PYTHON_BIN..."
    "$PYTHON_BIN" -m venv "$VENV_DIR"
fi

echo "✅ Activating virtual environment..."
source "$VENV_DIR/bin/activate"

echo "📦 Installing dependencies..."
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo "🗄️  Applying database migrations..."
python manage.py migrate --noinput

echo "🌐 Starting server at http://127.0.0.1:${PORT}/"
python manage.py runserver "$PORT"
