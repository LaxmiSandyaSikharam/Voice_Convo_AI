from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi import UploadFile
from app.api.endpoints import router as api_router
from app.services.rag import ingest_and_index_doc  # ✅ needed to load CSV
from io import BytesIO
import os

app = FastAPI(title="Voice Conversational Agentic AI")

# Serve static files (CSS, JS, audio, etc.)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def read_index():
    index_path = os.path.join("static", "index.html")
    if not os.path.exists(index_path):
        return {"error": "index.html not found in static folder"}
    return FileResponse(index_path)

@app.get("/ping")
def ping():
    return {"message": "pong"}

# ✅ Load CSV at startup
@app.on_event("startup")
def load_csv_on_startup():
    csv_path = "backend_data/HackathonInternalKnowledgeBase.csv"
    if os.path.exists(csv_path):
        with open(csv_path, "rb") as f:
            file = UploadFile(filename=os.path.basename(csv_path), file=BytesIO(f.read()))
            success = ingest_and_index_doc(file)
            if success:
                print("✅ CSV loaded on startup.")
            else:
                print("❌ Failed to load CSV on startup.")
    else:
        print("⚠️ CSV file not found at startup:", csv_path)

# Register routes
app.include_router(api_router)