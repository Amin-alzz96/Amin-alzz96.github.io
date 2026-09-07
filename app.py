"""
app.py: FastAPI app for Amin's website chatbot, with session memory.
Also serves the static frontend from docs/ so the whole site runs locally
with a single `uvicorn app:app` command.
"""
import uuid
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from main import chat, end_session

FRONTEND_DIR = Path(__file__).parent / "docs"

app = FastAPI(title="Amin's CV chat API")

# TODO Phase 4: restrict origins to the deployed frontend domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    session_id: str
    message: str


class ChatResponse(BaseModel):
    response: str
    session_id: str


class SessionRequest(BaseModel):
    session_id: str


@app.post("/start_session", response_model=ChatResponse)
async def start_session():
    session_id = str(uuid.uuid4())
    return ChatResponse(
        response="Hi, I'm Amin — well, my AI twin. Ask me anything about my work, skills, or background!",
        session_id=session_id,
    )


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    reply = await chat(req.session_id, req.message)
    return ChatResponse(response=reply, session_id=req.session_id)


@app.post("/end_session")
async def end_session_endpoint(req: SessionRequest):
    end_session(req.session_id)
    return {"status": "Session ended", "session_id": req.session_id}


# Mounted last so the API routes above take precedence.
if FRONTEND_DIR.is_dir():
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
