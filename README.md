# Context_Aware_Chatbot
This project is a context-aware conversational chatbot built as part of a technical interview task.  
It supports multi-turn conversations, short-term memory, model fallback, and response enrichment.

Features
- Context-aware multi-turn chat memory
- Primary LLM integration using **Google Gemini**
- Automatic fallback to **Ollama (local LLM)** when Gemini fails
- Simple caching via in-memory conversation history
- Fun animal jokes injected every 4 user messages
- Swagger UI for easy testing and API exploration

Architecture Overview
1. User sends a message via REST API
2. Conversation history is retrieved from memory
3. Prompt is constructed with recent context
4. **Gemini** is called as the primary model
5. If Gemini fails, **Ollama** is used as a fallback
6. Response is returned along with the model used

Tech Stack
- Python 3
- FastAPI
- Google Gemini API (google-genai SDK)
- Ollama (local LLM server)
- Swagger UI (FastAPI auto-generated)
- Uvicorn

How to Run Locally
1. Clone the repository
(git clone <your-github-repo-url>
cd context_chatbot)

2. Create virtual environment
python -m venv venv
venv\Scripts\activate   # Windows

3. Install dependencies
pip install -r requirements.txt

4. Set environment variable
$Env:GEMINI_API_KEY="YOUR_API_KEY"

5. Run the server
python -m uvicorn chatbot:app --reload

6. Open Swagger UI
Visit:
http://127.0.0.1:8000/docs

⚠️ Challenges & Solutions

Ollama Version Changes
Ollama 2 has been used as a fallback instead of Ollama3

Gemini API changes
Gemini APIs and model names have changed frequently
Solution: dynamically list available models and target supported aliases

Reliability
Primary model failures are handled gracefully
Automatic fallback ensures uninterrupted responses

Context management
Limited memory window is used to control prompt size and cost
