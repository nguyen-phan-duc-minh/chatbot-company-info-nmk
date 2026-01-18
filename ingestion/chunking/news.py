import json
import logging
from pathlib import Path
from bs4 import BeautifulSoup

from core.settings_loader import load_settings

settings = load_settings()
logger = logging.getLogger("ingestion")

def html_to_text(html: str) -> str:  # Hàm nhận vào chuỗi HTML và trả về text thuần (không có tag)
    soup = BeautifulSoup(html, "html.parser")  # Parse chuỗi HTML bằng parser mặc định của Python
    return soup.get_text(separator=" ", strip=True)  
    # Lấy toàn bộ text trong HTML
    # separator=" " : chèn dấu cách giữa các đoạn text để tránh dính chữ
    # strip=True     : loại bỏ khoảng trắng dư ở đầu và cuối chuỗi

def chunk_news():
    file_path = Path(settings["data"]["processed_dir"]) / "news.json"
    
    if not file_path.exists():
        logger.error(f"File not found: {file_path}")
        return []
    
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            news = json.load(file)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON format {e}")
        return []
    except Exception as e:
        logger.error(f"Failed to load {e}")
        return []
    
    if isinstance(news, dict):
        news = [news]
        
    if not isinstance(news, list):
        logger.error("News categories data is not a list")
        return []
    
    if not news:
        logger.warning("No news found in the file")
        return []
    
    chunks = []
    
    for idx, news_item in enumerate(news):
        if not isinstance(news_item, dict):
            logger.warning(f"News item at index {idx} is not a dictionary")
            continue
        
        news_item_id = news_item.get("id")
        news_item_title = news_item.get("title", "")
        if not news_item_title or not isinstance(news_item_title, str):
            logger.warning(f"News item at index {idx} has an invalid or missing title")
            continue
        
        news_item_excerpt = news_item.get("excerpt", "")
        if not news_item_excerpt or not isinstance(news_item_excerpt, str):
            logger.warning(f"News item at index {idx} has an invalid or missing excerpt")
            continue
        
        news_item_content = news_item.get("content", "")
        if not news_item_content or not isinstance(news_item_content, str):
            logger.warning(f"News item at index {idx} has an invalid or missing content")
            continue
        news_item_content = html_to_text(news_item_content)
        
        news_item_author = news_item.get("author", "")
        news_published_at = news_item.get("publishedAt", "")
        news_item_view_count = news_item.get("viewCount")
        if not isinstance(news_item_view_count, int):
            news_item_view_count = 0
        
        text_parts = [
            f'Tựa đề tin tức: {news_item_title}',
            f'Tóm tắt tin tức: {news_item_excerpt}',
            f'Nội dung tin tức: {news_item_content}'
        ]
        
        if news_item_author and isinstance(news_item_author, str):
            text_parts.append(f'Tác giả tin tức: {news_item_author}')
            
        text = "\n".join(text_parts)
        
        chunks.append({
            "text": text,
            "metadata": {
                "type": "news_article",
                "news_article_id": news_item_id,
                "published_at": news_published_at,
                "view_count": news_item_view_count,
                "source": "news.json",
            }
        })
        
    if not chunks:
        logger.warning("No valid news items were processed")
        
    return chunks