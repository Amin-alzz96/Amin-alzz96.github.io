"""
app.py: FastAPI app for Amin's chat agent with per-session memory and welcome message.
"""
from fastapi import FastAPI, Request
from pydantic import BaseModel
from main import get_agent
from fastapi.middleware.cors import CORSMiddleware
import uuid

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory store for agent instances per session
agent_store = {}

WELCOME_MESSAGE = "Welcome! I am Amin. How can I help you?"

class ChatRequest(BaseModel):
    session_id: str
    message: str

@app.post("/start_session")
def start_session():
    session_id = str(uuid.uuid4())
    return {"session_id": session_id, "welcome": WELCOME_MESSAGE}

@app.post("/chat")
async def chat_endpoint(req: ChatRequest):
    # Use a persistent agent per session_id for memory
    if req.session_id not in agent_store:
        agent_store[req.session_id] = get_agent()
    agent = agent_store[req.session_id]
    result = await agent.ainvoke({"input": req.message}, config={"configurable": {"session_id": req.session_id}})
    return {"response": result["output"]}

@app.post("/end_session")
async def end_session(request: Request):
    data = await request.json()
    session_id = data.get("session_id")
    if session_id and session_id in agent_store:
        del agent_store[session_id]
        return {"message": f"Session {session_id} ended and memory cleared."}
    return {"message": "Session not found."}

@app.get("/")
def root():
    return {"message": "Amin's chat agent is running!"}
