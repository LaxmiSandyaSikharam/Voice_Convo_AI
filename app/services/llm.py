import os
from openai import OpenAI
from app.memory.memory_store import get_conversation, add_message

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_response(user_message: str, rag_context: str = ""):
    """
    Generates a GPT-4 response using strictly the provided RAG context.
    If the answer isn't in the context, the assistant explicitly states that.
    """
    # Clear, strict system instruction
    system_prompt = {
        "role": "system",
        "content": (
            "You are a factual assistant that answers ONLY based on the [Context] below.\n"
            "You MUST extract answers only from this context and avoid any assumptions or general knowledge.\n"
            "ALWAYS read the entire context and find the precise numeric or textual values when asked.\n"
            "If the answer is not directly available, respond with:\n"
            "'I couldn't find that information in the knowledge base.'"
        )
    }

    # Structure user message with explicit context
    full_message = (
        f"User question: {user_message}\n\n"
        f"[Context]: {rag_context}"
    ) if rag_context else user_message

    # Compose the conversation with system + user message
    conversation = [system_prompt, {"role": "user", "content": full_message}]

    # Generate a response
    response = client.chat.completions.create(
        model="gpt-4",
        messages=conversation,
        temperature=0.0  # Enforce strict factual answers
    )

    assistant_reply = response.choices[0].message.content.strip()

    # Store in memory (user + assistant)
    add_message("user", user_message)
    add_message("assistant", assistant_reply)

    return assistant_reply
