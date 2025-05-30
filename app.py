"""
app.py: FastAPI app for Amin's RAG-based chatbot with session memory.
"""
import uuid
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from main import get_agent, session_histories

app = FastAPI()

# Allow CORS for all origins (customize for production)
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

@app.post("/start_session", response_model=ChatResponse)
async def start_session():
    session_id = str(uuid.uuid4())
    # Optionally, initialize session memory here
    return ChatResponse(response="Welcome! I am Amin. How can I help you?", session_id=session_id)

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    agent = get_agent()
    result = await agent.ainvoke({"input": req.message}, config={"configurable": {"session_id": req.session_id}})
    return ChatResponse(response=result["output"], session_id=req.session_id)

@app.post("/end_session")
async def end_session(req: ChatRequest):
    # Remove session memory if exists
    session_histories.pop(req.session_id, None)
    return {"status": "Session ended", "session_id": req.session_id}
