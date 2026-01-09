from fastapi import FastAPI
from pydantic import BaseModel
import os
import requests
import random
from google import genai
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="Context-Aware Chatbot")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all origins (safe for local dev)
    allow_credentials=True,
    allow_methods=["*"],  # allow POST, OPTIONS, etc.
    allow_headers=["*"],
)


# ---------------------------
# Config
# ---------------------------

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
gemini_client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama2"

gemini_client = None
if GEMINI_API_KEY:
    gemini_client = genai.Client(api_key=GEMINI_API_KEY)

# ---------------------------
# Models
# ---------------------------

class ChatRequest(BaseModel):
    user_id: str
    message: str

class ChatResponse(BaseModel):
    response: str
    model_used: str

# ---------------------------
# Memory
# ---------------------------

conversation_memory: dict[str, list[str]] = {}
message_counter: dict[str, int] = {}

# ---------------------------
# Fun
# ---------------------------

ANIMAL_JOKES = [
    "Why don’t elephants use computers? Because they’re afraid of the mouse 🐭",
    "Why did the cow become an astronaut? To see the moooon 🐮",
    "Why don’t cats play poker in the jungle? Too many cheetahs 🐆",
    "What do you call a sleeping bull? A bulldozer 🐂"
]

def maybe_add_animal_joke(user_id: str):
    count = message_counter.get(user_id, 0)
    if count > 0 and count % 4 == 0:
        return random.choice(ANIMAL_JOKES)
    return None

# ---------------------------
# Model Calls
# ---------------------------

def call_gemini(prompt: str) -> str:
    if not gemini_client:
        raise RuntimeError("Gemini not configured")

    response = gemini_client.models.generate_content(
        model="models/gemini-flash-latest",
        contents=prompt
    )
    return response.text

def call_ollama(prompt: str) -> str:
    r = requests.post(
        OLLAMA_URL,
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False
        },
        timeout=60
    )
    r.raise_for_status()
    return r.json()["response"]

# ---------------------------
# Endpoint
# ---------------------------

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    user_id = req.user_id
    user_message = req.message

    history = conversation_memory.setdefault(user_id, [])
    message_counter[user_id] = message_counter.get(user_id, 0) + 1

    history.append(f"User: {user_message}")
    context = "\n".join(history[-8:])

    prompt = f"""
You are a helpful, friendly chatbot.

Conversation so far:
{context}

Assistant:
"""

    try:
        reply = call_gemini(prompt)
        model_used = "gemini"
    except Exception as e:
        print("Gemini failed:", e)
        reply = call_ollama(prompt)
        model_used = "ollama"

    joke = maybe_add_animal_joke(user_id)
    if joke:
        reply += f"\n\n🐾 Fun animal joke:\n{joke}"

    history.append(f"Assistant: {reply}")

    return ChatResponse(response=reply, model_used=model_used)
