#!/bin/bash
# Build script for Render.com deployment
# Installs Chromium via Playwright (works in read-only environments)

set -e

echo "🔧 Installing Chromium for headless browser automation..."

# Install Playwright browsers (Chromium is bundled)
echo "📦 Installing Playwright browsers..."
python -m playwright install chromium
python -m playwright install-deps chromium || echo "⚠️  Could not install system dependencies (may not be needed)"

echo "✅ Chromium installation complete via Playwright"
