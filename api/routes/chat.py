import logging
import os
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import uuid

from core.schema import RetrievedDocument
from retrieval.retriever import retrieve
from llm.generator import generate_answer

logger = logging.getLogger("chat")
router = APIRouter()

MAX_QUERY_LENGTH = int(os.getenv("MAX_QUERY_LENGTH", "500"))

sessions = {}

class ChatRequest(BaseModel):
    """Chat request model"""
    query: str = Field(..., min_length=1, max_length=MAX_QUERY_LENGTH, description="User's question")
    session_id: Optional[str] = Field(None, description="Session ID for conversation tracking")

class ChatResponse(BaseModel):
    """Chat response model"""
    answer: str = Field(..., description="Bot's answer")
    sources: list = Field(default_factory=list, description="Source documents")
    session_id: str = Field(..., description="Session ID")


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    question = request.query.strip()
    
    if not question:
        raise HTTPException(status_code=400, detail="Vui lòng nhập câu hỏi.")
    
    session_id = request.session_id or str(uuid.uuid4())
    
    logger.info(f"Session {session_id}: Received question: {question}")
    
    try:
        documents = retrieve(question)
        
        if not documents:
            logger.warning(f"Session {session_id}: No documents retrieved")
            return ChatResponse(
                answer="Tôi không tìm thấy thông tin phù hợp trong dữ liệu hiện có.",
                sources=[],
                session_id=session_id
            )
        
        context = "\n\n".join(
            f"[{i+1}] {doc.text}\n(Nguồn: {doc.metadata})" 
            for i, doc in enumerate(documents)
        )
        logger.info(f"Session {session_id}: Retrieved {len(documents)} documents")
        
        answer = generate_answer(context, question)
        logger.info(f"Session {session_id}: Generated answer successfully")
        
        sources = [
            {
                "text": doc.text[:200] + "..." if len(doc.text) > 200 else doc.text,
                "metadata": doc.metadata,
                "score": doc.score
            }
            for doc in documents
        ]
        
        if session_id not in sessions:
            sessions[session_id] = []
        sessions[session_id].append({
            "question": question,
            "answer": answer,
            "sources": sources
        })
        
        return ChatResponse(
            answer=answer,
            sources=sources,
            session_id=session_id
        )
    
    except Exception as e:
        logger.error(f"Session {session_id}: Error in chat: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Xin lỗi, đã xảy ra lỗi khi xử lý câu hỏi của bạn. Vui lòng thử lại sau."
        )


def chat(question: str) -> str:
    """Legacy CLI chat function"""
    if not question or not question.strip():
        logger.warning("Empty question received")
        return "Vui lòng nhập câu hỏi."
    
    if len(question) > MAX_QUERY_LENGTH:
        logger.warning(f"Query too long: {len(question)} characters")
        return f"Câu hỏi quá dài. Vui lòng giới hạn dưới {MAX_QUERY_LENGTH} ký tự."
    
    logger.info(f"Received question: {question}")
    
    try:
        documents = retrieve(question)
        if not documents:
            logger.warning("No documents retrieved for the question")
            return "Tôi không tìm thấy thông tin phù hợp trong dữ liệu hiện có."
        
        context = "\n\n".join(f"[{i+1}] {doc.text}\n(Nguồn: {doc.metadata})" for i, doc in enumerate(documents))
        logger.info(f"Retrieved {len(documents)} documents for the question")
            
        answer = generate_answer(context, question)
        logger.info("Generated answer successfully")
        return answer
    
    except Exception as e:
        logger.error(f"Error in chat function: {e}", exc_info=True)
        return "Xin lỗi, đã xảy ra lỗi khi xử lý câu hỏi của bạn. Vui lòng thử lại sau."