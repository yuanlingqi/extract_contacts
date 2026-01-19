# How to Run the API Server Locally

## Step-by-Step Guide

### Step 1: Install Dependencies

Make sure you have Python 3.8+ installed, then install the required packages:

```bash
cd /Users/chenjianping/Desktop/facebook_scraper
pip install -r requirements_api.txt
```

Or if you're using a virtual environment:

```bash
# Activate your virtual environment first
source venv/bin/activate

# Then install dependencies
pip install -r requirements_api.txt
```

### Step 2: Start Chrome with Remote Debugging

**On macOS:**
```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222
```

**On Linux:**
```bash
google-chrome --remote-debugging-port=9222
```

**On Windows:**
```bash
chrome.exe --remote-debugging-port=9222
```

**Note:** Keep this Chrome window open while the API server is running.

### Step 3: Run the API Server

```bash
python api_server.py
```

Or if using Python 3 explicitly:
```bash
python3 api_server.py
```

You should see output like:
```
============================================================
🚀 Contact Extractor API Server
============================================================

📡 API Endpoints:
  GET  /health - Health check
  GET  /extract?url=<URL> - Extract contacts from a single URL
  POST /extract/batch - Extract contacts from multiple URLs

💡 Example:
  http://localhost:5000/extract?url=https://www.facebook.com/FidelidadeSeguros.Portugal

⚠️  Note: Make sure Chrome is running with:
  chrome --remote-debugging-port=9222
============================================================

 * Running on http://0.0.0.0:5000
```

### Step 4: Test the API

#### Test Health Check:
```bash
curl http://localhost:5000/health
```

#### Test Single URL Extraction:
```bash
curl "http://localhost:5000/extract?url=https://www.facebook.com/FidelidadeSeguros.Portugal"
```

Or open in your browser:
```
http://localhost:5000/extract?url=https://www.facebook.com/FidelidadeSeguros.Portugal
```

#### Test Batch Extraction:
```bash
curl -X POST http://localhost:5000/extract/batch \
  -H "Content-Type: application/json" \
  -d '{"urls": ["https://www.facebook.com/FidelidadeSeguros.Portugal"]}'
```

## Troubleshooting

### Issue: "Error connecting to browser"
**Solution:** Make sure Chrome is running with `--remote-debugging-port=9222`. Close Chrome completely and restart it with the command above.

### Issue: "Port 5000 already in use"
**Solution:** Either:
1. Stop the other service using port 5000
2. Or modify `api_server.py` to use a different port (change `port=5000` to another port like `port=5001`)

### Issue: "Module not found"
**Solution:** Make sure all dependencies are installed:
```bash
pip install Flask flask-cors DrissionPage gunicorn
```

### Issue: Chrome doesn't start
**Solution:** 
- On macOS, make sure you use the full path: `/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome`
- Check if Chrome is already running and close it first
- Try using `chromium` instead of `google-chrome` on Linux

## Quick Start Script

You can create a simple script to start everything:

**start_server.sh** (macOS/Linux):
```bash
#!/bin/bash
# Start Chrome with remote debugging
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 &
sleep 2
# Start API server
python api_server.py
```

Make it executable:
```bash
chmod +x start_server.sh
./start_server.sh
```

## Using the API

Once the server is running, you can use it from:

1. **Browser:** Open `http://localhost:5000/extract?url=YOUR_URL`
2. **cURL:** Use the commands above
3. **Python:**
```python
import requests
response = requests.get('http://localhost:5000/extract', params={'url': 'https://www.facebook.com/FidelidadeSeguros.Portugal'})
print(response.json())
```

4. **JavaScript:**
```javascript
fetch('http://localhost:5000/extract?url=https://www.facebook.com/FidelidadeSeguros.Portugal')
  .then(response => response.json())
  .then(data => console.log(data));
```
