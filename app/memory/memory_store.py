# app/memory/memory_store.py

conversation_memory = []

def add_message(role: str, content: str):
    conversation_memory.append({"role": role, "content": content})

def get_conversation():
    return conversation_memory.copy()

def reset_memory():
    conversation_memory.clear()

