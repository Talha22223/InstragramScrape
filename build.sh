#!/bin/bash
set -e  # Exit on error

echo "🚀 Starting build process..."

# Install backend dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r "freelance prj/backend/requirements.txt"

# Install frontend dependencies and build
echo "📦 Installing Node.js dependencies..."
cd "freelance prj/frontend"

# Check if package.json exists
if [ ! -f "package.json" ]; then
    echo "❌ package.json not found in frontend directory"
    exit 1
fi

npm ci --production=false
echo "🏗️  Building React application..."
npm run build

# Verify build was successful
if [ ! -d "build" ]; then
    echo "❌ Build directory not found. Build may have failed."
    exit 1
fi

echo "✅ Build process completed successfully!"
echo "📁 Frontend build output:"
ls -la build/