#!/bin/bash
# Django development server startup script

echo "🚀 Starting Vstash Django Server..."
echo "📍 Working directory: $(pwd)"

# Activate virtual environment
source .venv/bin/activate

# Check if activation worked
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ Virtual environment activated: $VIRTUAL_ENV"
else
    echo "❌ Failed to activate virtual environment"
    exit 1
fi

# Run Django server
echo "🌐 Starting server at http://127.0.0.1:8000/"
python3 manage.py runserver
