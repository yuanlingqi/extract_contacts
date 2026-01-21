#!/bin/bash
# 修复端口 5000 被 AirPlay Receiver 占用的问题

PORT=5000

echo "🔍 Checking port $PORT..."

# 检查端口占用
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "⚠️  Port $PORT is in use:"
    lsof -i :$PORT
    echo ""
    
    # 尝试杀死进程
    echo "🔄 Attempting to kill process..."
    PIDS=$(lsof -ti :$PORT)
    
    if [ -z "$PIDS" ]; then
        echo "❌ Could not find process ID"
        exit 1
    fi
    
    for PID in $PIDS; do
        echo "   Killing PID: $PID"
        kill -9 $PID 2>/dev/null || sudo kill -9 $PID 2>/dev/null
    done
    
    # 等待端口释放
    sleep 2
    
    # 再次检查
    if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        echo ""
        echo "❌ Port $PORT is still in use (process may have restarted)"
        echo ""
        echo "💡 This is likely AirPlay Receiver (ControlCenter) on macOS"
        echo "💡 Solutions:"
        echo "   1. Disable AirPlay Receiver:"
        echo "      System Settings > General > AirPlay & Handoff > Turn off AirPlay Receiver"
        echo ""
        echo "   2. Use a different port:"
        echo "      PORT=5001 python extract_contacts.py --server"
        exit 1
    else
        echo "✅ Port $PORT is now available"
    fi
else
    echo "✅ Port $PORT is available"
fi
