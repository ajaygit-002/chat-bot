from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv
import json

from openai_utils import get_embedding, get_chat_response, get_chat_response_stream, translate_text
from pinecone_db import store_message, retrieve_context

load_dotenv()

app = FastAPI(title="NovaChat AI API", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Models
class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    language: Optional[str] = "English"
    conversation_history: Optional[List[Message]] = []

class ChatResponse(BaseModel):
    reply: str
    language: Optional[str] = "English"

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "message": "NovaChat AI API is running"
    }

# Main chat endpoint
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # Validate input
        if not request.message or not request.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        user_message = request.message.strip()
        target_language = request.language or "English"
        
        # Step 1: Generate embedding for user message (only once)
        embedding = None
        try:
            embedding = get_embedding(user_message)
        except Exception as e:
            error_msg = str(e)
            print(f"Warning: Could not generate embedding: {error_msg}")
            # Continue without embedding - Pinecone is optional
        
        # Step 2: Retrieve context from Pinecone if embedding available (top_k reduced to 2 for speed)
        context = ""
        if embedding and embedding != [0.1] * 768:  # Only if we have a valid embedding
            try:
                context = retrieve_context(embedding, top_k=2)  # Reduced from 3 to 2 for speed
            except Exception as e:
                print(f"Warning: Could not retrieve context from Pinecone: {e}")
                context = ""
        
        # Step 3: Prepare conversation history for Ollama (last 5 messages for speed)
        messages = []
        
        # Add previous conversation history - REDUCED to last 5 for faster processing
        if request.conversation_history:
            for msg in request.conversation_history[-5:]:  # Keep last 5 messages only
                messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
        
        # Add current user message
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        # Step 4: Get response from Ollama with context
        try:
            reply = get_chat_response(messages, context)
        except Exception as e:
            error_msg = str(e)
            print(f"Chat response error: {error_msg}")
            raise HTTPException(status_code=500, detail=f"Error getting chat response: {error_msg}")
        
        # Step 5: Translate response if needed (for non-English)
        translated_reply = reply
        if target_language.lower() != "english":
            try:
                translated_reply = translate_text(reply, target_language)
            except Exception as e:
                print(f"Warning: Could not translate response: {e}")
                translated_reply = reply
        
        # Step 6: Store messages in Pinecone (async-friendly, non-blocking)
        if embedding and embedding != [0.1] * 768:
            try:
                store_message(embedding, user_message, metadata={"role": "user", "language": target_language})
            except Exception as e:
                print(f"Warning: Could not store user message in Pinecone: {e}")
            
            try:
                # Generate embedding for bot response only if needed for storage
                bot_embedding = get_embedding(translated_reply)
                store_message(bot_embedding, translated_reply, metadata={"role": "assistant", "language": target_language})
            except Exception as e:
                print(f"Warning: Could not store bot response in Pinecone: {e}")
        
        return ChatResponse(
            reply=translated_reply,
            language=target_language
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

# New streaming chat endpoint - for real-time responses like ChatGPT
@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """Streaming endpoint - sends tokens as they arrive for instant feedback"""
    try:
        # Validate input
        if not request.message or not request.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        user_message = request.message.strip()
        target_language = request.language or "English"
        
        # Step 1: Generate embedding for user message (only once)
        embedding = None
        try:
            embedding = get_embedding(user_message)
        except Exception as e:
            print(f"Warning: Could not generate embedding: {e}")
        
        # Step 2: Retrieve context from Pinecone if embedding available (top_k=2 for speed)
        context = ""
        if embedding and embedding != [0.1] * 768:
            try:
                context = retrieve_context(embedding, top_k=2)
            except Exception as e:
                print(f"Warning: Could not retrieve context: {e}")
        
        # Step 3: Prepare conversation history - REDUCED to last 5 for speed
        messages = []
        
        if request.conversation_history:
            for msg in request.conversation_history[-5:]:  # Last 5 messages only
                messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
        
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        # Step 4: Stream response from Ollama
        async def event_generator():
            try:
                full_response = ""
                for token in get_chat_response_stream(messages, context):
                    full_response += token
                    # Send token as Server-Sent Event
                    yield f"data: {json.dumps({'token': token})}\n\n"
                
                # Send completion signal with full response
                yield f"data: {json.dumps({'done': True, 'full_response': full_response})}\n\n"
                
                # Store messages in Pinecone (non-blocking)
                if embedding and embedding != [0.1] * 768:
                    try:
                        store_message(embedding, user_message, metadata={"role": "user", "language": target_language})
                        bot_embedding = get_embedding(full_response)
                        store_message(bot_embedding, full_response, metadata={"role": "assistant", "language": target_language})
                    except Exception as e:
                        print(f"Warning: Could not store in Pinecone: {e}")
                        
            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        return StreamingResponse(event_generator(), media_type="text/event-stream")
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Streaming error: {str(e)}")

# About endpoint
@app.get("/about")
async def about():
    return {
        "name": "NovaChat AI",
        "version": "1.0.0",
        "description": "A modern AI chatbot powered by OpenAI GPT and Pinecone embeddings",
        "features": [
            "Multi-language support",
            "Context-aware responses",
            "Message memory with Pinecone",
            "Real-time chat interface"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
