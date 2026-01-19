#!/bin/bash
# Build script for Render.com deployment
# Installs Chromium via Playwright (works in read-only environments)

set -e

echo "🔧 Installing Chromium for headless browser automation..."

# Install Playwright browsers (Chromium is bundled)
echo "📦 Installing Playwright browsers..."
python -m playwright install chromium

# Verify installation
echo "🔍 Verifying Chromium installation..."
python -c "
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium
    path = browser.executable_path
    import os
    if path and os.path.exists(path):
        print(f'✅ Chromium found at: {path}')
    else:
        print(f'⚠️  Chromium path reported as: {path}')
        print('   But file does not exist')
"

# Try to install system dependencies (may fail in read-only environments)
python -m playwright install-deps chromium || echo "⚠️  Could not install system dependencies (may not be needed)"

# Show where browsers are installed
echo "📂 Browser cache location:"
python -c "
import os
cache_dirs = [
    os.path.expanduser('~/.cache/ms-playwright'),
    '/opt/render/.cache/ms-playwright',
    '/root/.cache/ms-playwright',
]
for cache_dir in cache_dirs:
    if os.path.exists(cache_dir):
        print(f'  {cache_dir}: exists')
        import subprocess
        result = subprocess.run(['ls', '-la', cache_dir], capture_output=True, text=True)
        if result.returncode == 0:
            print(result.stdout)
    else:
        print(f'  {cache_dir}: not found')
"

echo "✅ Chromium installation complete via Playwright"
