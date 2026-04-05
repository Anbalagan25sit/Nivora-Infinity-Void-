#!/bin/bash

# Nivora Extension Build Script
# ============================

echo "🔧 Building Nivora Browser Extension..."
echo "======================================"

# Navigate to extension directory
cd nivora-extension || { echo "❌ Extension directory not found"; exit 1; }

echo "📦 Installing dependencies..."
npm install

echo "🔨 Building extension..."
npm run build

echo ""
echo "✅ Extension built successfully!"
echo ""
echo "📋 Installation Instructions:"
echo "1. Open Chrome and go to chrome://extensions/"
echo "2. Enable 'Developer mode' (top right toggle)"
echo "3. Click 'Load unpacked'"
echo "4. Select the 'dist' folder in this directory:"
echo "   $(pwd)/dist"
echo ""
echo "🎯 Usage:"
echo "- Click the extension icon in the toolbar"
echo "- Or press Alt+N to open quickly"
echo "- Make sure the token server and agent are running!"