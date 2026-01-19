#!/bin/bash
# Build script for Render.com deployment
# Installs Chromium and sets up the environment

set -e

echo "🔧 Installing Chromium for headless browser automation..."

# Install Chromium and dependencies
if command -v apt-get &> /dev/null; then
    # Debian/Ubuntu
    apt-get update
    apt-get install -y chromium-browser chromium-chromedriver
elif command -v yum &> /dev/null; then
    # CentOS/RHEL
    yum install -y chromium chromium-headless
elif command -v apk &> /dev/null; then
    # Alpine
    apk add --no-cache chromium chromium-chromedriver
else
    echo "⚠️  Package manager not found. Trying to install Chromium manually..."
    # Fallback: Download Chromium
    mkdir -p /tmp/chromium
    cd /tmp/chromium
    wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb || true
    if [ -f google-chrome-stable_current_amd64.deb ]; then
        apt-get update
        apt-get install -y ./google-chrome-stable_current_amd64.deb || true
    fi
fi

# Install Chrome/Chromium dependencies
apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libc6 \
    libcairo2 \
    libcups2 \
    libdbus-1-3 \
    libexpat1 \
    libfontconfig1 \
    libgbm1 \
    libgcc1 \
    libglib2.0-0 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libstdc++6 \
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    libxrandr2 \
    libxrender1 \
    libxss1 \
    libxtst6 \
    lsb-release \
    xdg-utils || true

echo "✅ Chromium installation complete"

# Start Chromium in headless mode with remote debugging
echo "🚀 Starting Chromium in headless mode..."
chromium-browser --headless --remote-debugging-port=9222 --no-sandbox --disable-dev-shm-usage &
# Or try: google-chrome --headless --remote-debugging-port=9222 --no-sandbox --disable-dev-shm-usage &

echo "✅ Build script completed"
