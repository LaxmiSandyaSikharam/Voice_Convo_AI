# Voice-Driven Real Estate Conversational AI

This project is an intelligent voice-enabled real estate assistant that enables users to interact naturally using speech to inquire about commercial property listings. The assistant processes user queries using speech recognition, retrieves relevant structured data, and responds via voice synthesis—creating a seamless and human-centric user experience.

---

## 🔍 Use Case

Designed for real estate professionals, brokers, and clients to:

- Quickly retrieve property information using natural voice commands.
- Dynamically filter listings by fields like rent, suite, floor, associates, or address.
- Handle both structured CSV inputs and natural language queries with RAG (Retrieval-Augmented Generation).

---

## Key Features

- **Voice-to-Text Input**: Converts spoken queries to text using OpenAI Whisper.
- **Data-Aware Chat**: Queries are parsed and matched against a structured dataset (CSV).
- **Text-to-Speech Output**: Converts the response back to voice using OpenAI TTS.
- **RAG Integration**: Retrieves supplemental context from unstructured knowledge base files.
- **Smart Query Parsing**: Handles filters such as:
  - Rent/SF/Year (highest/lowest)
  - Annual Rent
  - GCI on 3 Years
  - Floor, Suite
  - Associate names
  - Property Address (fuzzy matched)
- **FastAPI Backend**: RESTful API supporting conversation and document ingestion.
- **Front-end UI**: Simple HTML/JS interface to speak, receive voice response, and interact in real-time.

---

## Tech Stack

- **Backend**: Python, FastAPI
- **AI Services**: 
  - OpenAI Whisper (speech recognition)
  - GPT-4 with RAG (chat processing)
  - OpenAI TTS (speech synthesis)
- **Data Handling**: Pandas, Regex, FuzzyWuzzy for query filtering
- **Frontend**: HTML, JavaScript
- **File Ingestion**: CSV and PDF support for knowledge base

---

## File Structure

```
voice_convo_ai/
│
├── app/
│   ├── api/
│   │   └── routes.py
│   ├── services/
│   │   ├── stt.py         # Speech-to-text
│   │   ├── tts.py         # Text-to-speech
│   │   ├── rag.py         # RAG retrieval logic
│   │   ├── agent.py       # Core LLM logic
│   │   └── filters.py     # Query filtering logic
│   ├── utils/
│   │   └── csv_loader.py  # CSV parsing and indexing
│   └── main.py            # FastAPI app entry point
│
├── static/
│   ├── index.html
│   ├── script.js
│   └── audio/             # Saved voice outputs
│
├── backend_data/
│   └── HackathonInternalKnowledgeBase.csv
│
└── requirements.txt
```

---

## Setup Instructions

1. **Clone the Repository**

```bash
git clone https://github.com/your-username/voice-convo-ai.git
cd voice-convo-ai
```

2. **Create a virtual environment and install dependencies**

```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

3. **Add your OpenAI API Key**

Create a `.env` file in the root directory:

```
OPENAI_API_KEY=your-api-key-here
```

4. **Run the App**

```bash
uvicorn app.main:app --reload
```

5. **Visit**: `http://localhost:8000` in your browser.

---

## User Manual

### 1. Access the Web Interface
Navigate to `http://localhost:8000` after starting the FastAPI server. You’ll see a simple interface with a "Start Recording" button.

### 2. Using Voice Search
- Click **Start Recording** and speak your query clearly.
- Example Queries:
  - "Which suite has the highest annual rent?"
  - "Show me properties handled by Jack Sparrow."
  - "Find available suites in 9 Times Square."
  - "What’s the GCI on 3 years for floor E6?"

### 3. AI Processing & Response
- The query is parsed using intelligent filters.
- Data is pulled from both:
  - A structured CSV (HackathonInternalKnowledgeBase.csv)
  - An optional PDF knowledge base via RAG.
- The response is:
  - Displayed as text.
  - Played back as audio using text-to-speech.

### 4. File Uploads (Optional)
- You can enhance responses by uploading your own:
  - **CSV**: Structured listings
  - **PDF**: Internal documentation for RAG-based context

### 5. Troubleshooting
- **No Response?** Ensure your mic is working and your browser has permission.
- **Inaccurate Matches?** Try to be more specific in queries (e.g., add suite/floor).
- **Debug Info** is logged in the terminal for each request.

---

## Example Queries Supported

- "Which property has the maximum GCI on 3 years?"
- "Show all listings with Rent per SF greater than $100."
- "Get me all listings where Jon Snow is an associate."
- "Show me Suite 600 on Floor E6."
- "Lowest rent/sf/year available?"

---

## Future Enhancements

- Natural language date range support
- Location-based filtering with map integration
- User authentication and history
- Mobile-friendly responsive UI

---

## License

This project is open-source and available under the MIT License.
