@echo off
REM Quick setup for ultra-fast chatbot

echo ====================================
echo 🚀 Ultra-Fast Chatbot Setup
echo ====================================

REM Pull tinyllama if not already available
echo.
echo 📥 Pulling tinyllama (1.1GB - ultra-fast model)...
ollama pull tinyllama

echo.
echo ✅ Setup complete!
echo.
echo 🎯 Next steps:
echo 1. Start Ollama: ollama serve
echo 2. In another terminal, go to backend folder
echo 3. Run: python main.py
echo 4. In another terminal, go to frontend folder  
echo 5. Run: npm run dev
echo.
echo ⚡ tinyllama is 10x faster than mistral!
echo.
pause
