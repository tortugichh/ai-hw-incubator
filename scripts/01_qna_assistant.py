# scripts/01_qna_assistant.py
"""
Q&A Assistant that answers questions using uploaded PDFs
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_assistant_id():
    """Get assistant ID from file."""
    try:
        with open('.assistant_id', 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        print("❌ Assistant not found. Please run 00_bootstrap.py first.")
        return None

def create_thread():
    """Create a new conversation thread."""
    thread = client.beta.threads.create()
    print(f"✅ Created thread: {thread.id}")
    return thread

def ask_question(assistant_id, thread_id, question):
    """Ask a question and stream the response."""
    print(f"\n🤔 Question: {question}")
    print("🤖 Assistant: ", end="", flush=True)
    
    # Add message to thread
    client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=question
    )
    
    # Create and stream the run
    with client.beta.threads.runs.create_and_stream(
        thread_id=thread_id,
        assistant_id=assistant_id,
    ) as stream:
        for event in stream:
            if event.event == 'thread.message.delta':
                for content in event.data.delta.content:
                    if content.type == 'text':
                        print(content.text.value, end="", flush=True)
    
    print("\n")
    
    # Get citations
    messages = client.beta.threads.messages.list(thread_id=thread_id, limit=1)
    latest_message = messages.data[0]
    
    # Print citations if available
    if (hasattr(latest_message.content[0], 'text') and 
        latest_message.content[0].text.annotations):
        print("📚 Citations:")
        for annotation in latest_message.content[0].text.annotations:
            if hasattr(annotation, 'file_citation'):
                citation = annotation.file_citation
                print(f"  - File ID: {citation.file_id}")
                if hasattr(citation, 'quote'):
                    print(f"    Quote: {citation.quote[:100]}...")
    
    return latest_message

def main():
    """Main Q&A session."""
    # Get assistant
    assistant_id = get_assistant_id()
    if not assistant_id:
        return
    
    # Create thread
    thread = create_thread()
    
    # Test questions
    test_questions = [
        "Explain the difference between a definite and an indefinite integral in one paragraph.",
        "Give me the statement of the Mean Value Theorem.",
        "What is the fundamental theorem of calculus?"
    ]
    
    for question in test_questions:
        ask_question(assistant_id, thread.id, question)
        print("-" * 50)
    
    # Interactive mode
    print("\n🎓 Interactive Q&A Mode (type 'quit' to exit)")
    while True:
        user_question = input("\nYour question: ").strip()
        if user_question.lower() in ['quit', 'exit', 'q']:
            break
        if user_question:
            ask_question(assistant_id, thread.id, user_question)

if __name__ == "__main__":
    main()