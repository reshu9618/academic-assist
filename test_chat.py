import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to sys.path
root_path = str(Path(__file__).parent)
if root_path not in sys.path:
    sys.path.append(root_path)

from app.agent.agent_graph import run_chat_agent

if __name__ == "__main__":
    print("Testing Chat Assistant...")
    messages = [{"role": "user", "content": "Hello"}]
    courses = []
    tasks = []
    schedule = {}
    try:
        response = run_chat_agent(messages, courses, tasks, schedule)
        print(f"Chat Assistant Response: {response}")
    except Exception as e:
        print(f"An error occurred: {e}")
