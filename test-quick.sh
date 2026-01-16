#!/bin/bash
# Quick test script to verify ultra-fast setup

echo "=================================="
echo "🚀 Testing Ultra-Fast Bot"
echo "=================================="
echo ""

# Test Ollama
echo "📡 Testing Ollama connection..."
curl -s http://localhost:11434/api/tags | python -m json.tool > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Ollama is running"
else
    echo "❌ Ollama not responding - start with: ollama serve"
    exit 1
fi

# Test Backend
echo ""
echo "🔧 Testing Backend..."
curl -s http://localhost:8000/health | python -m json.tool > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Backend is running"
else
    echo "❌ Backend not responding - start with: python main.py"
    exit 1
fi

echo ""
echo "=================================="
echo "✅ All systems ready!"
echo "🎯 Open http://localhost:5173 in browser"
echo "⚡ Type a message - responses appear instantly!"
echo "=================================="
