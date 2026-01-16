# 🤖 Pinecone Assistant Setup Guide

Advanced setup guide for using Pinecone's built-in Assistant feature for enhanced AI capabilities.

---

## 📋 What is Pinecone Assistant?

Pinecone Assistant is a powerful feature that allows you to:
- Create custom assistants with specific instructions
- Perform retrieval-augmented generation (RAG) with built-in tools
- Manage conversation context automatically
- Use serverless compute for AI tasks

---

## 🚀 Quick Setup

### Step 1: Install Pinecone SDK

```bash
cd backend
pip install --upgrade pinecone
```

### Step 2: Create Assistant

Add this to your Python script or `main.py`:

```python
from pinecone import Pinecone

# Initialize Pinecone with your API key
pc = Pinecone(api_key="YOUR_API_KEY")

# Create an assistant
assistant = pc.assistant.create_assistant(
    assistant_name="example-assistant", 
    instructions="Answer in polite, short sentences. Use American English spelling and vocabulary.", 
    timeout=30  # Wait 30 seconds for assistant operation to complete
)

print(f"Assistant created: {assistant.name}")
```

---

## 🔧 Configuration Options

### Create Assistant with Full Options

```python
assistant = pc.assistant.create_assistant(
    assistant_name="novachat-assistant",
    instructions="""You are a helpful, polite AI assistant. 
    - Answer in short, clear sentences
    - Use American English
    - Be concise and accurate
    - Ask clarifying questions if needed""",
    model="gpt-4",  # Optional: specify model
    timeout=30,
    metadata={
        "version": "1.0",
        "purpose": "chat",
        "language": "en"
    }
)
```

---

## 💬 Using the Assistant

### Send a Message

```python
# Send message to assistant
response = pc.assistant.chat(
    assistant_id="example-assistant",
    messages=[
        {"role": "user", "content": "What is artificial intelligence?"}
    ]
)

print(response.message)
```

### Multi-turn Conversation

```python
conversation_history = []

# User message 1
user_message_1 = "Hello, what can you do?"
conversation_history.append({"role": "user", "content": user_message_1})

response_1 = pc.assistant.chat(
    assistant_id="example-assistant",
    messages=conversation_history
)
print(response_1.message)

# Add assistant response to history
conversation_history.append({"role": "assistant", "content": response_1.message})

# User message 2
user_message_2 = "Can you help with Python?"
conversation_history.append({"role": "user", "content": user_message_2})

response_2 = pc.assistant.chat(
    assistant_id="example-assistant",
    messages=conversation_history
)
print(response_2.message)
```

---

## 📚 Use with RAG (Retrieval Augmented Generation)

### Add Documents to Assistant

```python
# Upload documents for context
assistant.upsert_files(
    files=[
        ("document1.txt", open("document1.txt", "rb")),
        ("document2.pdf", open("document2.pdf", "rb"))
    ]
)
```

### Query with Context

```python
# Ask question with document context
response = pc.assistant.chat(
    assistant_id="example-assistant",
    messages=[
        {"role": "user", "content": "Based on the documents, what is...?"}
    ],
    file_ids=["document1.txt", "document2.pdf"]
)

print(response.message)
```

---

## 🔌 Integration with FastAPI Backend

### Example: `backend/main.py`

```python
from fastapi import FastAPI
from pinecone import Pinecone
import os

app = FastAPI()

# Initialize Pinecone
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

@app.post("/chat")
async def chat(message: str, language: str = "English"):
    """Chat endpoint using Pinecone Assistant"""
    
    try:
        # Use Pinecone Assistant
        response = pc.assistant.chat(
            assistant_id="example-assistant",
            messages=[
                {"role": "user", "content": message}
            ]
        )
        
        return {
            "reply": response.message,
            "language": language
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/health")
async def health():
    return {"status": "healthy", "message": "NovaChat AI API is running"}
```

---

## 📊 Assistant Methods

### Create Assistant
```python
assistant = pc.assistant.create_assistant(
    assistant_name="name",
    instructions="instructions",
    model="gpt-4",
    timeout=30
)
```

### Get Assistant
```python
assistant = pc.assistant.describe_assistant(assistant_id="assistant-name")
```

### List Assistants
```python
assistants = pc.assistant.list_assistants()
for asst in assistants:
    print(asst.name)
```

### Delete Assistant
```python
pc.assistant.delete_assistant(assistant_id="assistant-name")
```

### Update Assistant
```python
pc.assistant.update_assistant(
    assistant_id="assistant-name",
    instructions="new instructions"
)
```

### Chat
```python
response = pc.assistant.chat(
    assistant_id="assistant-name",
    messages=[{"role": "user", "content": "message"}]
)
```

---

## 🛠️ Error Handling

```python
from pinecone import Pinecone
from pinecone.core.client.exceptions import PineconeException

pc = Pinecone(api_key="YOUR_API_KEY")

try:
    assistant = pc.assistant.create_assistant(
        assistant_name="my-assistant",
        instructions="Be helpful and concise",
        timeout=30
    )
except PineconeException as e:
    print(f"Pinecone error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

---

## 🔐 Best Practices

1. **Never hardcode API keys** - Use environment variables
2. **Set appropriate timeout** - Balance between response time and reliability
3. **Handle errors gracefully** - Wrap calls in try-except blocks
4. **Monitor assistant usage** - Track API calls and costs
5. **Use meaningful instructions** - Clear instructions lead to better responses
6. **Test before production** - Verify assistant behavior thoroughly
7. **Keep instructions updated** - Refine based on user feedback

---

## 📝 Environment Setup

Add to `backend/.env`:

```env
OPENAI_API_KEY=sk-your_key_here
PINECONE_API_KEY=pcsk_your_key_here
PINECONE_INDEX=chatbot-index
PINECONE_ENVIRONMENT=us-east-1
PINECONE_ASSISTANT_ID=your-assistant-name
```

Load in Python:

```python
import os
from dotenv import load_dotenv

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
ASSISTANT_ID = os.getenv("PINECONE_ASSISTANT_ID", "example-assistant")
```

---

## 🚀 Complete Example

```python
from fastapi import FastAPI
from pinecone import Pinecone
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
ASSISTANT_ID = os.getenv("PINECONE_ASSISTANT_ID", "novachat-assistant")

# Create assistant on startup (optional)
@app.on_event("startup")
async def startup():
    try:
        # Try to get existing assistant
        assistant = pc.assistant.describe_assistant(assistant_id=ASSISTANT_ID)
        print(f"Using existing assistant: {ASSISTANT_ID}")
    except:
        # Create new assistant if doesn't exist
        assistant = pc.assistant.create_assistant(
            assistant_name=ASSISTANT_ID,
            instructions="""You are a helpful AI assistant for the NovaChat application.
            - Provide clear, concise answers
            - Use professional tone
            - Be accurate and helpful
            - Ask clarifying questions when needed""",
            timeout=30
        )
        print(f"Created new assistant: {ASSISTANT_ID}")

@app.post("/chat")
async def chat(message: str, language: str = "English", conversation_history: list = None):
    """Chat with Pinecone Assistant"""
    
    try:
        # Prepare messages
        if conversation_history is None:
            conversation_history = []
        
        conversation_history.append({"role": "user", "content": message})
        
        # Get response from assistant
        response = pc.assistant.chat(
            assistant_id=ASSISTANT_ID,
            messages=conversation_history
        )
        
        return {
            "reply": response.message,
            "language": language
        }
    except Exception as e:
        return {"error": f"Chat failed: {str(e)}", "reply": ""}

@app.get("/health")
async def health():
    return {"status": "healthy", "message": "NovaChat AI API is running"}
```

---

## 📚 Resources

- [Pinecone Assistant Documentation](https://docs.pinecone.io/guides/assistant)
- [Pinecone Python SDK](https://docs.pinecone.io/reference/python/)
- [Pinecone RAG Guide](https://docs.pinecone.io/guides/retrieval-augmented-generation)

---

## 🆘 Troubleshooting

### "Assistant not found"
```
Solution: Ensure assistant_id matches the assistant you created
```

### "API key invalid"
```
Solution: Check PINECONE_API_KEY in .env file
```

### "Timeout error"
```
Solution: Increase timeout value or check network connection
```

### "Permission denied"
```
Solution: Verify API key has assistant permissions
```

---

## 🎯 Next Steps

1. Create your Pinecone assistant
2. Test with simple messages
3. Integrate with FastAPI backend
4. Add to frontend chat interface
5. Deploy to production

Happy assisting! 🚀
