import logging
import ollama
import time # Thêm thư viện time để đo thời gian thực thi va theo dõi hiệu suất
from llm.prompt import build_prompt
from core.settings_loader import load_settings

settings = load_settings()
logger = logging.getLogger("llm")
start = time.time()

LLM_CONFIG = settings["llm"]
MODEL_PROVIDER = LLM_CONFIG.get("provider", "openai")
MODEL_NAME = LLM_CONFIG.get("model_name", "gpt-3.5-turbo")
MODEL_TEMPERATURE = LLM_CONFIG.get("temperature", 0.2)
MODEL_MAX_TOKENS = LLM_CONFIG.get("max_tokens", 1024)

def generate_answer(context: str, question: str) -> str:
    if not context or not context.strip(): # Kiểm tra context rỗng
        logger.warning("Received empty context for answer generation.")
        return "Dữ liệu ngữ cảnh không được để trống."
    
    if not question or not question.strip(): # Kiểm tra câu hỏi rỗng
        logger.warning("Received empty question for answer generation.")
        return "Câu hỏi không được để trống."
    
    prompt = build_prompt(context, question) # Tạo prompt từ context và question
    
    logger.info(f"Generating answer using model: {MODEL_NAME}")
    
    try:
        if MODEL_PROVIDER == "ollama":
            response = ollama.chat(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": prompt},
                ],
                options={
                    "temperature": MODEL_TEMPERATURE,
                    "num_predict": MODEL_MAX_TOKENS
                }
            )
            answer = response['message']['content'].strip()
        else:
            logger.error(f"Unsupported model provider: {MODEL_PROVIDER}")
            return "Nhà cung cấp mô hình không được hỗ trợ."
        
        logger.info("Answer generation completed successfully.")
        logger.info(f"Time taken for generation: {time.time() - start} seconds")
        return answer
    except Exception as e:
        logger.error(f"Error during answer generation: {e}")
        return "Đã xảy ra lỗi trong quá trình tạo câu trả lời."