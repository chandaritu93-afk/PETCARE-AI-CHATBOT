# backend/llm.py
import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from dotenv import load_dotenv
load_dotenv()
# ==================== GROQ LLM ====================
# Apna API key environment variable me set karo ya yahan likho
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "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")

llm = ChatGroq(
    model_name="llama-3.1-8b-instant",   # Fast inference model
    api_key=GROQ_API_KEY,
    temperature=0.0,                     # Low temperature for accuracy
    max_tokens=1024,                     # Enough length for detailed answers
)

# ==================== SYSTEM PROMPT ====================
SYSTEM_PROMPT = """You are PetCare AI 🐾 — a professional and context-aware pet healthcare assistant.

RULES:
1. You are ONLY a pet healthcare assistant. Politely decline non-pet-related topics.
2. Always assume the user is talking about their pet.
3. Use only the provided CONTEXT from the pet healthcare database to answer queries accurately.
4. Do NOT generate information outside the retrieved context.
5. If sufficient information is unavailable, politely state that the information is not available in the database.
6. If symptoms appear serious, strongly recommend consulting a veterinarian.
7. Personalize responses using available pet profile information.
8. Keep responses concise, structured, and easy to understand.
9. Use empathetic and professional language.
10. Treat each retrieved chunk as a separate evidence source.
11. Never generate unsupported medical claims.
12. If retrieved evidence is weak or missing, clearly state:
"Information not available in the trusted medical database."

FORMATTING:
- Use bullet points where appropriate
- Use **bold** for important information
- Keep responses clear and informative
"""

# ==================== PROMPT TEMPLATE ====================
prompt_template = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("system", "📚 CONTEXT FROM DATABASE:\n{context}"),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{question}"),
])

# ==================== GENERATE ANSWER ====================
def generate_answer(question: str, context: str, chat_history: list = None) -> str:
    """
    Generate answer using Groq LLM with context + history.
    
    Args:
        question: User's current question
        context: RAG retrieved context (FAISS docs + pet profile)
        chat_history: List of {"role": "user"/"assistant", "content": "..."}
    """
    if chat_history is None:
        chat_history = []

    # Convert chat history to LangChain message format
    lc_history = []
    for msg in chat_history[-10:]:  # Last 10 messages for context
        if msg["role"] == "user":
            lc_history.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            lc_history.append(AIMessage(content=msg["content"]))

    # Build the chain
    chain = prompt_template | llm

    try:
        response = chain.invoke({
            "context": "\n\n--- DOCUMENT SEPARATOR ---\n\n".join(context) if isinstance(context, list) else context,
            "chat_history": lc_history,
            "question": question,
        })
        return response.content
    except Exception as e:
        print(f"❌ LLM Error: {e}")
        return "I'm sorry, I'm having trouble responding right now. Please try again! 🐾"
