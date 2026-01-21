#!/bin/bash
# One-click script to start local API service + ngrok

echo "🚀 Starting local API service (for Google Sheets)"
echo ""

# Check if ngrok is installed
if ! command -v ngrok &> /dev/null; then
    echo "❌ ngrok is not installed"
    echo "💡 Installation:"
    echo "   brew install ngrok"
    echo "   Or visit: https://ngrok.com/download"
    exit 1
fi

# Check if port is already in use
if lsof -Pi :5001 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "⚠️  Port 5001 is already in use, cleaning up..."
    lsof -ti :5001 | xargs kill -9 2>/dev/null
    sleep 1
fi

# Start Chrome (background)
echo "1️⃣  Starting Chrome (remote debugging mode)..."
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 > /dev/null 2>&1 &
CHROME_PID=$!
echo "   ✅ Chrome started (PID: $CHROME_PID)"
sleep 2

# Start API server (background)
echo "2️⃣  Starting API server..."
cd "$(dirname "$0")"
python extract_contacts.py --server > /tmp/api_server.log 2>&1 &
API_PID=$!
echo "   ✅ API server started (PID: $API_PID)"
sleep 3

# Check if API server started successfully
if ! curl -s http://localhost:5001/health > /dev/null; then
    echo "   ⚠️  API server may not be fully started, waiting..."
    sleep 3
fi

# Start ngrok
echo "3️⃣  Starting ngrok (exposing local service to public internet)..."
ngrok http 5001 > /tmp/ngrok.log 2>&1 &
NGROK_PID=$!
echo "   ✅ ngrok started (PID: $NGROK_PID)"
sleep 3

# Get ngrok URL
echo ""
echo "⏳ Fetching ngrok URL..."
sleep 2

# Try to get URL from ngrok API
NGROK_URL=$(curl -s http://localhost:4040/api/tunnels 2>/dev/null | grep -o '"public_url":"https://[^"]*"' | head -1 | cut -d'"' -f4)

if [ -z "$NGROK_URL" ]; then
    echo ""
    echo "⚠️  Could not automatically fetch ngrok URL"
    echo ""
    echo "📋 Please manually visit the following URL to see ngrok URL:"
    echo "   http://localhost:4040"
    echo ""
    echo "💡 Or run the following command:"
    echo "   curl http://localhost:4040/api/tunnels | grep -o \"https://[^\"]*\" | head -1"
    echo ""
    NGROK_URL="Please visit http://localhost:4040 to view"
else
    echo "   ✅ Successfully fetched!"
fi

echo ""
printf "%.60s\n" "============================================================"
echo "✅ All services started!"
printf "%.60s\n" "============================================================"
echo ""
echo "📋 Service Information:"
echo "   Chrome:      PID $CHROME_PID"
echo "   API Server:  PID $API_PID (http://localhost:5001)"
echo "   ngrok:       PID $NGROK_PID"
echo ""
echo "🌐 ngrok Public URL:"
echo "   $NGROK_URL"
echo ""
echo "📝 Next Steps:"
echo "   1. Copy the ngrok URL above"
echo "   2. Open Google Sheets > Extensions > Apps Script"
echo "   3. Find apiBaseUrl in google_apps_script.js"
echo "   4. Update to: const apiBaseUrl = \\\"$NGROK_URL\\\";"
echo "   5. Save and run the script"
echo ""
echo "🔍 View ngrok request logs:"
echo "   http://localhost:4040"
echo ""
echo "🛑 Stop all services:"
echo "   kill $CHROME_PID $API_PID $NGROK_PID"
echo "   Or run: ./stop_services.sh"
echo ""
printf "%.60s\n" "============================================================"
