# Use Python base image
FROM python:3.11-slim

# Install system dependencies and Chromium
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
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
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements_api.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements_api.txt

# Copy application code
COPY api_server.py extract_contacts.py ./

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DISPLAY=:99
ENV CHROMIUM_FLAGS="--headless --no-sandbox --disable-dev-shm-usage --disable-gpu"

# Expose port (Render will set PORT env var)
EXPOSE 5000

# Run the application
CMD gunicorn api_server:app --bind 0.0.0.0:${PORT:-5000} --workers 1 --timeout 300 --worker-class sync
