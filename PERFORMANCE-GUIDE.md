# Performance Optimization & Timeout Fix Guide

## Issue Summary
- **Slow response time**: Multiple redundant Ollama API calls
- **Timeout Error**: `HTTPConnectionPool(host='localhost', port=11434): Read timed out. (read timeout=60)`

## Solutions Implemented

### 1. **Increased Timeouts** (openai_utils.py)
```python
EMBEDDING_TIMEOUT = 120      # Was 30, now 2 minutes
CHAT_TIMEOUT = 300           # Was 60, now 5 minutes
```

**Why**: Large language models need more time, especially on slower hardware.

### 2. **Added Embedding Cache** (openai_utils.py)
- Caches embeddings to avoid redundant API calls
- Reduces repeated embedding generation for similar queries
- Automatically clears cache when it exceeds 1000 entries

### 3. **Optimized API Call Flow** (main.py)
- **Before**: 3 Ollama calls per message (embedding, chat, bot embedding)
- **After**: 2 Ollama calls (chat response is fastest, embeddings are optional)
- Made Pinecone integration optional to prevent blocking

### 4. **Better Error Handling**
- Gracefully handles timeouts instead of crashing
- Returns meaningful error messages
- Continues operation if Pinecone fails

## Quick Fixes to Try

### ✅ Step 1: Ensure Ollama is Running
```bash
# Start Ollama in a new terminal
ollama serve
```

### ✅ Step 2: Use a Faster Model
Edit your `.env` file in the `backend` folder:
```
OLLAMA_MODEL=mistral
```

Available fast models:
- `mistral` - Very fast, high quality (recommended)
- `neural-chat` - Fast, conversational
- `orca-mini` - Very fast, lightweight
- `tinyllama` - Ultra-fast, good for low-end devices
- `llama2` - Default, slower but accurate

To pull a new model:
```bash
ollama pull mistral
```

### ✅ Step 3: Check Ollama Status
```bash
# In a terminal, verify Ollama is responsive
curl http://localhost:11434/api/tags
```

## Performance Tuning

### For Slower Hardware
```python
# In openai_utils.py, reduce num_predict in options:
"num_predict": 256  # Instead of 500 (shorter responses)
```

### For Faster Responses
```python
# Reduce temperature for faster convergence:
"temperature": 0.5  # Instead of 0.7
"top_k": 20         # More restrictive sampling
```

## Debugging

### Enable Debug Logging
The code now prints debug info:
- Shows Ollama URL being used
- Shows model name
- Shows timeout values
- Prints detailed error messages

### Check Backend Logs
```bash
# In backend folder with running uvicorn
# You'll see [DEBUG] messages in the terminal
```

## Expected Response Times

| Model | First Response | Subsequent |
|-------|---|---|
| mistral | 5-10s | 3-5s |
| neural-chat | 8-15s | 5-8s |
| llama2 | 15-30s | 10-20s |
| tinyllama | 2-5s | 1-3s |

*Times vary based on hardware*

## If Issues Persist

1. **Check if Ollama is actually running**
   ```bash
   # Windows: Check Task Manager for "ollama" process
   # Terminal: ollama serve should show "Listening on 127.0.0.1:11434"
   ```

2. **Monitor Ollama performance**
   ```bash
   # While running a query, check system resources
   # Ollama needs: 4GB+ RAM for llama2, 2GB+ for mistral
   ```

3. **Increase timeouts further if needed**
   - Edit `openai_utils.py`
   - Increase `CHAT_TIMEOUT = 600` (10 minutes) if using large models

4. **Check your .env file**
   ```bash
   # Verify OLLAMA_BASE_URL is correct
   OLLAMA_BASE_URL=http://localhost:11434
   ```

## Performance Checklist

- [ ] Ollama is running (`ollama serve`)
- [ ] Using a fast model (mistral, neural-chat, or orca-mini)
- [ ] Backend timeout is at least 120s for embedding, 300s for chat
- [ ] `.env` file is configured correctly
- [ ] System has 2GB+ free RAM
- [ ] No other heavy processes running during testing
