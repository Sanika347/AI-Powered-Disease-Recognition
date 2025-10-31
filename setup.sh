#!/usr/bin/env bash
set -e

echo "📦 Updating system and installing Tesseract..."
apt-get update && apt-get install -y tesseract-ocr

echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Setup complete!"
