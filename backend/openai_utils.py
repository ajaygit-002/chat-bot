import os
import requests
import json
import hashlib
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# Ollama API Configuration (runs locally, no API key needed!)
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "tinyllama")  # Ultra-fast model

# Get current date for context
CURRENT_DATE = datetime.now().strftime("%A, %B %d, %Y")

# Timeouts optimized for local Ollama
EMBEDDING_TIMEOUT = 120
CHAT_TIMEOUT = 300

# Simple in-memory embedding cache to reduce redundant API calls
_embedding_cache = {}

def get_embedding(text):
    """Generate embedding for text using Ollama (free local AI) - with caching"""
    try:
        # Check cache first
        cache_key = hashlib.md5(text.encode()).hexdigest()
        if cache_key in _embedding_cache:
            return _embedding_cache[cache_key]
        
        # Ollama embeddings endpoint
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/embeddings",
            json={
                "model": OLLAMA_MODEL,
                "prompt": text
            },
            timeout=EMBEDDING_TIMEOUT
        )
        response.raise_for_status()
        data = response.json()
        embedding = data.get("embedding", [0] * 768)  # Default 768-dim embedding
        
        # Cache the result
        _embedding_cache[cache_key] = embedding
        
        # Keep cache size reasonable (max 1000 entries)
        if len(_embedding_cache) > 1000:
            _embedding_cache.clear()
        
        return embedding
    except requests.exceptions.Timeout:
        print(f"Timeout generating embedding - Ollama may be busy or model is slow")
        # Return a dummy embedding for now (Pinecone is optional)
        return [0.1] * 768
    except requests.exceptions.ConnectionError:
        print(f"ConnectionError: Ollama is not running at {OLLAMA_BASE_URL}")
        return [0.1] * 768
    except Exception as e:
        print(f"Error generating embedding: {e}")
        # Return a dummy embedding for now (Pinecone is optional)
        return [0.1] * 768

def get_chat_response(messages, context=""):
    """Get response from local Ollama AI (free, no API key needed!) - optimized"""
    try:
        # Prepare system message with current date and context
        system_message = f"You are a helpful AI assistant. Today is {CURRENT_DATE}. Provide clear, concise, and accurate responses."
        
        if context:
            system_message += f"\n\nContext from previous conversations:\n{context}"
        
        # Convert messages to Ollama format
        prompt = system_message + "\n\n"
        for msg in messages:
            role = "User" if msg["role"] == "user" else "Assistant"
            prompt += f"{role}: {msg['content']}\n"
        prompt += "Assistant: "
        
        print(f"[DEBUG] Sending request to Ollama at {OLLAMA_BASE_URL}")
        print(f"[DEBUG] Using model: {OLLAMA_MODEL}")
        print(f"[DEBUG] Timeout: {CHAT_TIMEOUT} seconds")
        
        # Call Ollama chat completion - ULTRA FAST SETTINGS
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.2,
                    "num_predict": 80,
                    "top_k": 10,
                    "top_p": 0.7,
                    "repeat_penalty": 1.2,
                    "num_thread": 4
                }
            },
            timeout=CHAT_TIMEOUT
        )
        response.raise_for_status()
        data = response.json()
        return data.get("response", "I'm processing your request...")
    except requests.exceptions.Timeout:
        print(f"Timeout error: Ollama request exceeded {CHAT_TIMEOUT} seconds. Model may be too slow or Ollama is overloaded.")
        return "⚠️ Response timeout - Ollama is taking too long. Try using a faster model or ensure Ollama has enough resources."
    except requests.exceptions.ConnectionError:
        return f"⚠️ Ollama is not running at {OLLAMA_BASE_URL}. Please start Ollama: Run 'ollama serve' in terminal or install from https://ollama.com"
    except Exception as e:
        print(f"Error getting chat response: {e}")
        return f"Error: {str(e)}"

def get_chat_response_stream(messages, context=""):
    """Get streaming response from local Ollama AI - tokens appear live like ChatGPT"""
    try:
        # Prepare system message with current date and context
        system_message = f"You are a helpful AI assistant. Today is {CURRENT_DATE}. Provide clear, concise, and accurate responses."
        
        if context:
            system_message += f"\n\nContext from previous conversations:\n{context}"
        
        # Convert messages to Ollama format
        prompt = system_message + "\n\n"
        for msg in messages:
            role = "User" if msg["role"] == "user" else "Assistant"
            prompt += f"{role}: {msg['content']}\n"
        prompt += "Assistant: "
        
        print(f"[DEBUG] Sending STREAMING request to Ollama")
        
        # Call Ollama with streaming enabled - ULTRA FAST SETTINGS
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": True,
                "options": {
                    "temperature": 0.2,
                    "num_predict": 80,
                    "top_k": 10,
                    "top_p": 0.7,
                    "repeat_penalty": 1.2,
                    "num_thread": 4
                }
            },
            timeout=CHAT_TIMEOUT,
            stream=True
        )
        response.raise_for_status()
        
        # Yield tokens as they arrive (live streaming)
        for line in response.iter_lines():
            if line:
                data = json.loads(line)
                token = data.get("response", "")
                if token:
                    yield token
        
    except requests.exceptions.Timeout:
        print(f"Timeout error during streaming")
        yield "⚠️ Response timeout"
    except requests.exceptions.ConnectionError:
        yield f"⚠️ Ollama not running"
    except Exception as e:
        print(f"Error in streaming: {e}")
        yield f"Error: {str(e)}"
    except requests.exceptions.Timeout:
        print(f"Timeout error: Ollama request exceeded {CHAT_TIMEOUT} seconds. Model may be too slow or Ollama is overloaded.")
        return "⚠️ Response timeout - Ollama is taking too long. Try using a faster model or ensure Ollama has enough resources."
    except requests.exceptions.ConnectionError:
        return f"⚠️ Ollama is not running at {OLLAMA_BASE_URL}. Please start Ollama: Run 'ollama serve' in terminal or install from https://ollama.com"
    except Exception as e:
        print(f"Error getting chat response: {e}")
        return f"Error: {str(e)}"

def translate_text(text, target_language):
    """Translate text to target language using Ollama - ULTRA FAST"""
    try:
        prompt = f"Translate to {target_language}:\n{text}\n\nTranslation:"
        
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "num_predict": 50,
                    "num_thread": 4
                }
            },
            timeout=CHAT_TIMEOUT
        )
        response.raise_for_status()
        data = response.json()
        return data.get("response", text).strip()
    except requests.exceptions.Timeout:
        print(f"Timeout during translation")
        return text
    except Exception as e:
        print(f"Error translating text: {e}")
        return text
