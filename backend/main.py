"""
main.py — Entry point. Route definitions only; all logic lives in core/.
"""
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from config.prompts import BUSINESS
from core.llm import call_llm, is_lead_intent
from core.leads import save_lead, get_leads

app = FastAPI(title="Chatbot & Lead Capture API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten to the real frontend origin in production
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)
    history: List[ChatMessage] = []


class ChatResponse(BaseModel):
    reply: str
    is_lead_intent: bool


class LeadRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    contact: str = Field(..., min_length=3, max_length=200)
    interest: Optional[str] = "General inquiry"


@app.get("/")
def root():
    return {"status": "ok", "service": "chatbot-lead-capture", "business": BUSINESS["name"]}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    if not req.message.strip():
        raise HTTPException(status_code=422, detail="Message cannot be empty.")
    history = [m.model_dump() for m in req.history]
    reply = call_llm(req.message, history)
    return ChatResponse(reply=reply, is_lead_intent=is_lead_intent(req.message))


@app.post("/lead")
def capture_lead(req: LeadRequest):
    lead = save_lead(req.name, req.contact, req.interest)
    return {"ok": True, "lead": lead}


@app.get("/leads")
def list_leads():
    leads = get_leads()
    return {"count": len(leads), "leads": leads}
