#!/bin/bash
# Stop all services

echo "🛑 Stopping all services..."

# Stop Chrome
pkill -f "Chrome.*remote-debugging-port=9222" 2>/dev/null
echo "✅ Chrome stopped"

# Stop API server
pkill -f "extract_contacts.py --server" 2>/dev/null
lsof -ti :5001 | xargs kill -9 2>/dev/null
echo "✅ API server stopped"

# Stop ngrok
pkill -f "ngrok http 5001" 2>/dev/null
pkill ngrok 2>/dev/null
echo "✅ ngrok stopped"

echo ""
echo "✅ All services stopped"
