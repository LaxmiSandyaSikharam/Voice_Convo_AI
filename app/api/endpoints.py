from fastapi import APIRouter, UploadFile, File
from app.services.stt import transcribe_audio
from app.services.llm import generate_response
from app.services.tts import speak_text
from app.services.rag import ingest_and_index_doc, query_rag_context
import openai

router = APIRouter()

@router.post("/converse")
async def converse(audio: UploadFile = File(...)):
    try:
        # Step 1: Transcribe
        text = await transcribe_audio(audio)
        print("📝 Transcribed Text:", text)

        # Step 2: Retrieve RAG context
        rag_context = query_rag_context(text)
        print("📚 Retrieved RAG context:", rag_context)

        # Step 3: Handle empty RAG
        if not rag_context.strip():
            response = "I couldn't find relevant information in the knowledge base."
        else:
            # Step 4: Truncate RAG to avoid token limit
            MAX_RAG_CHARS = 3000
            rag_context = rag_context[:MAX_RAG_CHARS]

            try:
                response = generate_response(text, rag_context)
            except openai.error.RateLimitError as rate_err:
                print("❌ GPT Rate Limit Error:", rate_err)
                return {
                    "text": "⚠️ Sorry, rate limit exceeded. Please wait and try again.",
                    "audio": None
                }

        print("💬 Agent Response:", response)

        # Step 5: Generate TTS
        try:
            audio_output = speak_text(response)
        except Exception as tts_err:
            print("❌ TTS generation failed:", tts_err)
            return {
                "text": response,
                "audio": None
            }

        return {"text": response, "audio": audio_output}

    except Exception as e:
        print("❌ Error in /converse:", e)
        return {"error": str(e)}

@router.post("/upload_rag_docs")
async def upload_docs(file: UploadFile = File(...)):
    try:
        success = ingest_and_index_doc(file)
        return {"status": "success" if success else "failed"}
    except Exception as e:
        print("❌ Error in /upload_rag_docs:", e)
        return {"status": "failed", "error": str(e)}

@router.post("/reset")
async def reset_context():
    try:
        print("🔁 Context reset endpoint called")
        return {"status": "reset successful"}
    except Exception as e:
        print("❌ Error in /reset:", e)
        return {"status": "failed", "error": str(e)}