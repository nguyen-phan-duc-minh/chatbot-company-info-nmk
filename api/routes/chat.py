import logging

from core.schema import RetrievedDocument
from retrieval.retriever import retrieve
from llm.generator import generate_answer

logger = logging.getLogger("chat")

def chat(question: str) -> str:
    if not question or not question.strip():
        logger.warning("Empty question received")
        return "Vui lòng nhập câu hỏi."
    
    logger.info(f"Received question: {question}")
    
    documents = retrieve(question)
    if not documents:
        logger.warning("No documents retrieved for the question")
        context = "" 
        return "Tôi không tìm thấy thông tin phù hợp trong dữ liệu hiện có."
    else:   
        context = "\n\n".join(f"[{i+1}] {doc.text}\n(Nguồn: {doc.metadata})" for i, doc in enumerate(documents))
        logger.info(f"Retrieved {len(documents)} documents for the question")
        
    answer = generate_answer(context, question)
    logger.info("Generated answer successfully")
    return answer