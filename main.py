import os
import sqlite3
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, TypedDict

# 🔹 Retriever & APIs
from ragcore import retrieve_docs
from ragcore import fetch_pubmed

# 🔹 LLM
from llm import generate_answer

# 🔹 Storage
import storage
from storage import (
    init_db,
    save_message,
    load_messages,
    save_pet_profile,
    load_pet_profile,
    create_session,
    get_all_sessions,
    delete_session,
)

# 🔹 LangGraph
from langgraph.graph import StateGraph, END


# ==================== STATE ====================
class PetCareState(TypedDict):
    user_id: str
    session_id: str
    question: str
    chat_history: list
    retrieved_docs: list
    context: str
    pet_profile: Optional[dict]
    answer: str


# ==================== CONTEXT + SOURCES ====================
def get_context(question: str):

    # 🔹 PDF/Docs
    try:
        docs = retrieve_docs(question, k=4)
    except:
        docs = []

    pdf_context = "\n\n---\n\n".join(docs)

    # 🔹 Sources list
    sources = []

    if docs:
        sources.append("PDF/Docs sources included")

    # 🔹 PubMed
    pubmed = ""

    if pubmed:
        sources.append("PubMed snippet included")

    # 🔹 Final context
    context_str = pdf_context + "\n\n" + pubmed

    return context_str, sources
# ==================== NODES ====================
def add_profile_context(state: PetCareState) -> PetCareState:
    profile = load_pet_profile(state["user_id"])
    context = state["context"]

    if profile:
        profile_text = f"""
🐾 PET PROFILE:
- Name: {profile.get('pet_name','N/A')}
- Species: {profile.get('species','N/A')}
- Breed: {profile.get('breed','N/A')}
- Age: {profile.get('age_months','N/A')} months
- Weight: {profile.get('weight_kg','N/A')} kg
- Gender: {profile.get('gender','N/A')}
"""
        context = profile_text + "\n\n" + context

    return {**state, "context": context, "pet_profile": profile}


def generate_llm_answer(state: PetCareState) -> PetCareState:
    answer = generate_answer(
        question=state["question"],
        context=state["context"],
        chat_history=state["chat_history"]
    )
    return {**state, "answer": answer}


# ==================== GRAPH ====================
workflow = StateGraph(PetCareState)
workflow.add_node("add_profile", add_profile_context)
workflow.add_node("generate_answer", generate_llm_answer)
workflow.add_edge("add_profile", "generate_answer")
workflow.add_edge("generate_answer", END)
workflow.set_entry_point("add_profile")
pet_graph = workflow.compile()


# ==================== FASTAPI ====================
app = FastAPI(title="PetCare AI Chatbot")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
init_db()


# ==================== MODELS ====================
class Query(BaseModel):
    user_id: str
    question: str
    session_id: Optional[str] = "default"

class PetProfile(BaseModel):
    user_id: str
    pet_name: Optional[str] = None
    species: Optional[str] = None
    age_months: Optional[int] = None
    breed: Optional[str] = None
    weight_kg: Optional[float] = None
    gender: Optional[str] = None

class SessionCreate(BaseModel):
    user_id: str
    session_id: str


# ==================== ROUTES ====================
@app.get("/")
def home():
    return {"status": "Running 🐾"}


@app.post("/ask")
def ask(q: Query):
    if not q.question.strip():
        return {"answer": "Please ask a question 🐾", "sources": []}

    save_message(q.user_id, "user", q.question, q.session_id)
    chat_history = load_messages(q.user_id, q.session_id, limit=20)
    context, sources = get_context(q.question)

    state = {
        "user_id": q.user_id,
        "session_id": q.session_id,
        "question": q.question,
        "chat_history": chat_history,
        "retrieved_docs": [],
        "context": context,
        "pet_profile": None,
        "answer": "",
    }

    result = pet_graph.invoke(state)
    save_message(q.user_id, "assistant", result["answer"], q.session_id)

    # Update session title if New Chat
    conn = sqlite3.connect("chat.db")
    c = conn.cursor()
    c.execute("SELECT title FROM chat_sessions WHERE session_id=?", (q.session_id,))
    row = c.fetchone()
    if row and row[0] == "New Chat":
        c.execute("UPDATE chat_sessions SET title=? WHERE session_id=?", (q.question[:30], q.session_id))
        conn.commit()
    conn.close()

    return {"answer": result["answer"], "sources": sources}


@app.get("/history")
def history(user_id: str, session_id: str = "default"):
    return load_messages(user_id, session_id)


@app.post("/profile/save")
def profile_save(p: PetProfile):
    save_pet_profile(p.user_id, p.model_dump())
    return {"ok": True}


@app.get("/profile/get")
def profile_get(user_id: str):
    return load_pet_profile(user_id) or {"message": "No profile"}


@app.post("/session/create")
def session_create(s: SessionCreate):
    create_session(s.user_id, s.session_id)
    return {"ok": True}


@app.get("/sessions")
def sessions_list(user_id: str):
    return get_all_sessions(user_id)


@app.delete("/session/{session_id}")
def session_delete(session_id: str):
    delete_session(session_id)
    return {"ok": True}


@app.post("/session/update_title")
def update_title(user_id: str, session_id: str, title: str):
    return storage.update_session_title(user_id, session_id, title)
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )    