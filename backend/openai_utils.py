import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

# Ollama API Configuration (runs locally, no API key needed!)
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama2")  # Free local model

def get_embedding(text):
    """Generate embedding for text using Ollama (free local AI)"""
    try:
        # Ollama embeddings endpoint
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/embeddings",
            json={
                "model": OLLAMA_MODEL,
                "prompt": text
            },
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        return data.get("embedding", [0] * 768)  # Default 768-dim embedding
    except Exception as e:
        print(f"Error generating embedding: {e}")
        # Return a dummy embedding for now (Pinecone is optional)
        return [0.1] * 768

def get_chat_response(messages, context=""):
    """Get response from local Ollama AI (free, no API key needed!)"""
    try:
        # Prepare system message with context
        system_message = "You are a helpful AI assistant. Provide clear, concise, and accurate responses."
        
        if context:
            system_message += f"\n\nContext from previous conversations:\n{context}"
        
        # Convert messages to Ollama format
        prompt = system_message + "\n\n"
        for msg in messages:
            role = "User" if msg["role"] == "user" else "Assistant"
            prompt += f"{role}: {msg['content']}\n"
        prompt += "Assistant: "
        
        # Call Ollama chat completion
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 500
                }
            },
            timeout=60
        )
        response.raise_for_status()
        data = response.json()
        return data.get("response", "I'm processing your request...")
    except requests.exceptions.ConnectionError:
        return "⚠️ Ollama is not running. Please start Ollama: Run 'ollama serve' in terminal or install from https://ollama.com"
    except Exception as e:
        print(f"Error getting chat response: {e}")
        return f"Error: {str(e)}"

def translate_text(text, target_language):
    """Translate text to target language using Ollama"""
    try:
        prompt = f"Translate the following text to {target_language}. Only provide the translation, nothing else.\n\nText: {text}\n\nTranslation:"
        
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "num_predict": 500
                }
            },
            timeout=60
        )
        response.raise_for_status()
        data = response.json()
        return data.get("response", text).strip()
    except Exception as e:
        print(f"Error translating text: {e}")
        return text  # Return original if translation fails
