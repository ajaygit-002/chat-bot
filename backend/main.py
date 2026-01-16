from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv

from openai_utils import get_embedding, get_chat_response, translate_text
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
        
        # Step 1: Generate embedding for user message
        try:
            embedding = get_embedding(user_message)
        except Exception as e:
            error_msg = str(e)
            # Check for quota exceeded error
            if "quota" in error_msg.lower() or "exceeded" in error_msg.lower():
                raise HTTPException(
                    status_code=429, 
                    detail=f"OpenAI API quota exceeded. Please check your billing at https://platform.openai.com/account/billing/overview"
                )
            elif "unauthorized" in error_msg.lower() or "invalid" in error_msg.lower():
                raise HTTPException(
                    status_code=401,
                    detail=f"OpenAI API authentication failed. Please check your API key in .env"
                )
            else:
                raise HTTPException(status_code=500, detail=f"Error generating embedding: {error_msg}")
        
        # Step 2: Store user message in Pinecone
        try:
            store_message(embedding, user_message, metadata={"role": "user", "language": target_language})
        except Exception as e:
            print(f"Warning: Could not store message in Pinecone: {e}")
            # Continue even if storage fails
        
        # Step 3: Retrieve context (top 3 similar messages)
        try:
            context = retrieve_context(embedding, top_k=3)
        except Exception as e:
            print(f"Warning: Could not retrieve context from Pinecone: {e}")
            context = ""
        
        # Step 4: Prepare conversation history for OpenAI
        messages = []
        
        # Add previous conversation history
        if request.conversation_history:
            for msg in request.conversation_history[-9:]:  # Keep last 9 messages to add current one
                messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
        
        # Add current user message
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        # Step 5: Get response from ChatGPT with context
        try:
            reply = get_chat_response(messages, context)
        except Exception as e:
            error_msg = str(e)
            # Check for quota exceeded error
            if "quota" in error_msg.lower() or "exceeded" in error_msg.lower():
                raise HTTPException(
                    status_code=429,
                    detail=f"OpenAI API quota exceeded. Please check your billing at https://platform.openai.com/account/billing/overview"
                )
            elif "unauthorized" in error_msg.lower() or "invalid" in error_msg.lower():
                raise HTTPException(
                    status_code=401,
                    detail=f"OpenAI API authentication failed. Please check your API key in .env"
                )
            else:
                raise HTTPException(status_code=500, detail=f"Error getting chat response: {error_msg}")
        
        # Step 6: Translate response if needed (for non-English)
        translated_reply = reply
        if target_language.lower() != "english":
            try:
                translated_reply = translate_text(reply, target_language)
            except Exception as e:
                print(f"Warning: Could not translate response: {e}")
                translated_reply = reply
        
        # Store bot response in Pinecone
        try:
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
