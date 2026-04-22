#!/bin/bash

# Build script for TSQL2012 FastAPI application

set -e

echo "🔧 TSQL2012 FastAPI Build Script"
echo "================================="

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Setup database
echo "🗄️ Setting up database..."
python setup_db.py

# Run migrations (if any)
echo "✅ Database setup complete"

# Run tests
echo "🧪 Running tests..."
pytest test_crud.py -v || echo "⚠️ Some tests failed, but continuing..."

# Start application
echo "🚀 Starting FastAPI application..."
uvicorn main:app --host 0.0.0.0 --port 8000

