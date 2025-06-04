# scripts/99_cleanup.py
"""
Cleanup script to remove assistant and associated resources
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def cleanup_assistant():
    """Delete the assistant and clean up files."""
    try:
        # Get assistant ID
        with open('.assistant_id', 'r') as f:
            assistant_id = f.read().strip()
        
        # Delete assistant
        client.beta.assistants.delete(assistant_id)
        print(f"✅ Deleted assistant: {assistant_id}")
        
        # Remove local files
        os.remove('.assistant_id')
        print("✅ Removed .assistant_id file")
        
    except FileNotFoundError:
        print("⚠️ No assistant found to cleanup")
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")

def cleanup_generated_files():
    """Remove generated files."""
    files_to_remove = [
        'exam_notes.json',
        '.assistant_id'
    ]
    
    for filename in files_to_remove:
        try:
            if os.path.exists(filename):
                os.remove(filename)
                print(f"✅ Removed {filename}")
        except Exception as e:
            print(f"❌ Error removing {filename}: {e}")

def list_all_assistants():
    """List all assistants (for debugging)."""
    try:
        assistants = client.beta.assistants.list()
        print("📋 All assistants:")
        for assistant in assistants.data:
            print(f"  - {assistant.name} (ID: {assistant.id})")
    except Exception as e:
        print(f"❌ Error listing assistants: {e}")

def main():
    """Main cleanup function."""
    print("🧹 Starting cleanup...")
    
    # Show current assistants
    list_all_assistants()
    
    # Ask for confirmation
    confirm = input("\nDo you want to delete the study assistant? (y/N): ").strip().lower()
    
    if confirm in ['y', 'yes']:
        cleanup_assistant()
        cleanup_generated_files()
        print("✅ Cleanup completed!")
    else:
        print("❌ Cleanup cancelled")

if __name__ == "__main__":
    main()