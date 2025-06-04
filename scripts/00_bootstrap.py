# scripts/00_bootstrap.py
"""
Bootstrap script to create/reuse assistant with file_search capability
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Check OpenAI version
try:
    import openai
    print(f"OpenAI version: {openai.__version__}")
except:
    pass

def create_or_get_assistant():
    """Create a new assistant or reuse existing one."""
    try:
        # Try to load existing assistant ID
        with open('.assistant_id', 'r') as f:
            assistant_id = f.read().strip()
            assistant = client.beta.assistants.retrieve(assistant_id)
            print(f"✅ Reusing existing assistant: {assistant.name} (ID: {assistant_id})")
            return assistant
    except FileNotFoundError:
        pass
    except Exception as e:
        print(f"⚠️ Error retrieving existing assistant: {e}")
    
    # Create new assistant
    assistant = client.beta.assistants.create(
        name="Study Q&A Assistant",
        instructions=(
            "You are a helpful tutor. "
            "Use the knowledge in the attached files to answer questions. "
            "Cite sources where possible."
        ),
        model="gpt-4o-mini",
        tools=[{"type": "file_search"}]
    )
    
    # Save assistant ID for reuse
    with open('.assistant_id', 'w') as f:
        f.write(assistant.id)
    
    print(f"✅ Created new assistant: {assistant.name} (ID: {assistant.id})")
    return assistant

def upload_pdf_to_assistant(assistant_id, pdf_path):
    """Upload PDF and attach to assistant."""
    if not os.path.exists(pdf_path):
        print(f"❌ File not found: {pdf_path}")
        return None
    
    try:
        # Upload file
        with open(pdf_path, "rb") as file:
            uploaded_file = client.files.create(
                purpose="assistants",
                file=file
            )
        
        print(f"✅ Uploaded file: {pdf_path} (ID: {uploaded_file.id})")
        
        # Create vector store
        vector_store = client.vector_stores.create(
            name="Study Materials"
        )
        
        # Add file to vector store
        client.vector_stores.files.create(
            vector_store_id=vector_store.id,
            file_id=uploaded_file.id
        )
        
        # Update assistant with vector store
        client.beta.assistants.update(
            assistant_id,
            tool_resources={
                "file_search": {
                    "vector_store_ids": [vector_store.id]
                }
            }
        )
        
        print(f"✅ File attached to assistant")
        return uploaded_file.id
        
    except Exception as e:
        print(f"❌ Error uploading file: {e}")
        return None

if __name__ == "__main__":
    # Create/get assistant
    assistant = create_or_get_assistant()
    
    # Upload PDF
    pdf_path = "data/calculus.pdf"
    if os.path.exists(pdf_path):
        upload_pdf_to_assistant(assistant.id, pdf_path)
    else:
        print(f"⚠️ PDF not found at {pdf_path}")
        print("Please place your PDF in the data/ folder")