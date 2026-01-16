import os
from dotenv import load_dotenv

load_dotenv()

# Initialize Pinecone (OPTIONAL - chatbot works without it!)
api_key = os.getenv("PINECONE_API_KEY")
index_name = os.getenv("PINECONE_INDEX", "chatbot-index")

# Only try to use Pinecone if API key is provided
index = None
if api_key:
    try:
        from pinecone import Pinecone
        pc = Pinecone(api_key=api_key)
        index = pc.Index(index_name)
        print(f"✅ Pinecone connected: {index_name}")
    except Exception as e:
        print(f"⚠️ Pinecone not available: {e}")
        print("💡 Chatbot will work without context memory - this is fine!")
        index = None
else:
    print("💡 Pinecone API key not set - chatbot will work without context memory")

def store_message(embedding, text, metadata=None):
    """Store a message embedding in Pinecone with metadata (OPTIONAL)"""
    try:
        if index is None:
            # Silently skip if Pinecone not available
            return None
        
        if metadata is None:
            metadata = {}
        
        metadata["text"] = text
        
        # Create unique ID based on timestamp
        import time
        message_id = f"msg_{int(time.time() * 1000)}"
        
        # Upsert to Pinecone
        index.upsert(vectors=[(message_id, embedding, metadata)])
        return message_id
    except Exception as e:
        print(f"⚠️ Could not store message in Pinecone: {e}")
        return None

def retrieve_context(embedding, top_k=3):
    """Retrieve top K similar messages from Pinecone (OPTIONAL)"""
    try:
        if index is None:
            # Return empty context if Pinecone not available
            return ""
        
        results = index.query(vector=embedding, top_k=top_k, include_metadata=True)
        
        context_list = []
        for match in results.get("matches", []):
            if "metadata" in match and "text" in match["metadata"]:
                context_list.append(match["metadata"]["text"])
        
        # Join context with newlines
        context = "\n".join(context_list) if context_list else ""
        return context
    except Exception as e:
        print(f"⚠️ Could not retrieve context from Pinecone: {e}")
        return ""

def initialize_index():
    """
    Initialize Pinecone index (run this once)
    
    To create index manually in Pinecone dashboard:
    - Index name: chatbot-index
    - Dimension: 1536
    - Metric: cosine
    """
    try:
        from pinecone import Index, Serverless
        
        dimension = 1536
        metric = "cosine"
        
        # Check if index exists
        existing_indexes = pc.list_indexes()
        
        if index_name not in [idx.name for idx in existing_indexes]:
            print(f"Creating index: {index_name}")
            pc.create_index(
                name=index_name,
                dimension=dimension,
                metric=metric,
                spec=Serverless(cloud="aws", region="us-east-1")
            )
            print(f"Index {index_name} created successfully!")
        else:
            print(f"Index {index_name} already exists")
    except Exception as e:
        print(f"Error initializing index: {e}")
